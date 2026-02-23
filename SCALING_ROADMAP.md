# SCALING ROADMAP — FreedomWallet Bot
**Cập nhật:** 2026-02-23  
**Stack hiện tại:** python-telegram-bot v20 · PostgreSQL (sync ORM + asyncio.to_thread) · VPS duy nhất · Polling · concurrent_updates=32 · Google Sheets per-user

---

## Tổng quan kiến trúc hiện tại

```
User
 └─► Telegram Server ──polling──► Bot Process (PTB v20)
                                      │
                          ┌───────────┼───────────────┐
                          ▼           ▼               ▼
                     PostgreSQL   asyncio.to_thread  SheetsAPIClient
                    (sync ORM)     (run_sync)        (REST/HTTP)
```

---

## GIAI ĐOẠN 1 — 0–200 User

### Trạng thái: LAUNCH NOW — Không nên thay đổi gì

**Dấu hiệu kỹ thuật CẦN nâng cấp (chưa xuất hiện ở giai đoạn này):**
- CPU VPS dưới 20% sustained
- Response time < 500ms cho mọi lệnh
- Không có Sheets 429 quota error
- Không có DB connection timeout

**Việc cần làm:**
| Hạng mục | Hành động |
|---|---|
| Monitoring cơ bản | Bật loguru + ghi log ra file, theo dõi response time bằng mắt |
| Error alerting | Telegram alert khi exception không catch được |
| DB pool | `pool_size=5, max_overflow=5` (đã đủ) |
| Sheets quota | Mỗi user ghi ~1–5 lần/ngày → hoàn toàn trong quota miễn phí |

**Việc KHÔNG nên làm:**
- ❌ Không dựng Redis
- ❌ Không viết batch worker
- ❌ Không chuyển sang webhook (polling ổn hoàn toàn ở quy mô này)
- ❌ Không tách service
- ❌ Không dựng queue/broker

**Rủi ro nếu nâng cấp quá sớm:**
- Tốn 2–4 tuần developer time vào infra chưa cần thiết
- Tăng độ phức tạp vận hành (Redis crash → bot ngừng hoạt động)
- Chi phí VPS tăng mà chưa có revenue tương xứng

**Kiến trúc sau giai đoạn 1 (giữ nguyên):**
```
PTB v20 (polling)
  └─► run_sync(db_call) ──► PostgreSQL (pool_size=5)
  └─► SheetsAPIClient ──────► Google Sheets REST API
```

---

## GIAI ĐOẠN 2 — 200–1.000 User

### Trạng thái: OPTIMIZE ON SINGLE VPS

**Dấu hiệu kỹ thuật cần nâng cấp:**
- Sheets 429 quota error bắt đầu xuất hiện (> 100 write/min)
- Response time tăng lên 800ms–1.5s trong giờ cao điểm
- DB connections `pool_size=5` chạm giới hạn (log: `QueuePool limit overflow`)
- CPU spike lên 60–80% trong 10–15 phút/ngày

**Việc cần làm:**

**1. Sheets: Thêm retry + exponential backoff**
```python
# Trong SheetsAPIClient — thêm decorator retry
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def add_transaction(self, ...):
    ...
```

**2. DB pool mở rộng**
```python
# database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,       # tăng từ 5
    max_overflow=20,    # tăng từ 5
    pool_timeout=20,
    pool_recycle=300,
)
```

**3. Chuyển sang Webhook (thay polling)**
```
Lý do: Polling gửi request liên tục đến Telegram server.
Webhook nhận event khi có, tiết kiệm CPU và giảm latency.

Nginx (SSL termination)
  └─► uvicorn / gunicorn
        └─► PTB v20 webhook mode
```

**4. Thêm simple in-memory rate limiter per user**
```python
# Tránh 1 user spam gây block event loop
from collections import defaultdict
import time

_last_call: dict[int, float] = defaultdict(float)

async def rate_limit_check(user_id: int, min_interval: float = 0.5) -> bool:
    now = time.monotonic()
    if now - _last_call[user_id] < min_interval:
        return False
    _last_call[user_id] = now
    return True
```

**5. Monitoring nâng cấp**
- Dùng `prometheus_client` + Grafana Cloud miễn phí
- Alert khi: response_time > 2s, error_rate > 1%, sheets_429_count > 10/hour

**Việc KHÔNG nên làm:**
- ❌ Không dựng pending_writes table + batch worker (chưa cần, Sheets quota còn rộng)
- ❌ Không dùng Redis (overhead không xứng với lợi ích)
- ❌ Không tách bot process ra microservice riêng
- ❌ Không rewrite sang async ORM (SQLAlchemy async + asyncio.to_thread đang ổn)

**Rủi ro nếu nâng cấp quá sớm (Redis, batch worker):**
- Batch worker cần thêm process quản lý, crash handling, retry logic
- Redis thêm 1 điểm failure duy nhất trên VPS
- Complexity tăng mà Sheets quota chưa thật sự bị chạm

**Kiến trúc sau giai đoạn 2:**
```
Nginx (SSL) ──webhook──► PTB v20 process
                              │
                 ┌────────────┼─────────────────┐
                 ▼            ▼                 ▼
           PostgreSQL    run_sync wrapper    SheetsAPIClient
          (pool=10/20)   (asyncio.to_thread)  (+ retry/backoff)
                 │
           Prometheus ──► Grafana Cloud
```

---

## GIAI ĐOẠN 3 — 1.000–3.000 User

### Trạng thái: INTRODUCE WRITE QUEUE FOR SHEETS

**Dấu hiệu kỹ thuật cần nâng cấp:**
- Sheets 429 xảy ra thường xuyên dù đã có retry (> 200 writes/min peak)
- User phàn nàn "bot chậm" khi ghi dữ liệu (phải chờ Sheets response)
- DB write latency tăng do nhiều concurrent run_sync chờ thread pool
- CPU sustained > 60% trong giờ cao điểm (7h–9h và 18h–22h)
- asyncio thread pool (`ThreadPoolExecutor`) queue backlog xuất hiện trong log

**Việc cần làm:**

**1. Tách Sheets write ra khỏi request path — dùng PostgreSQL pending table**
```sql
-- Thêm vào migration
CREATE TABLE sheets_write_queue (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    payload     JSONB NOT NULL,
    status      VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, DONE, FAILED
    retry_count INTEGER DEFAULT 0,
    created_at  TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
CREATE INDEX idx_swq_status ON sheets_write_queue(status, created_at);
```

**2. Handler chỉ ghi vào queue, không gọi Sheets trực tiếp**
```python
# quick_record_direct.py
async def handle_quick_record(...):
    # Ghi vào PostgreSQL (fast, < 5ms)
    await run_sync(_enqueue_write_sync, user_id, payload)
    await update.message.reply_text("✅ Đã ghi! (đồng bộ Sheets trong vài giây)")
    
def _enqueue_write_sync(user_id: int, payload: dict):
    db = SessionLocal()
    try:
        db.execute(insert(SheetsWriteQueue).values(
            user_id=user_id,
            payload=payload,
            status="PENDING"
        ))
        db.commit()
    finally:
        db.close()
```

**3. Background worker (asyncio task, CÙNG process)**
```python
# Chạy trong cùng PTB process, không cần process riêng
import asyncio

async def sheets_flush_worker():
    """Chạy mỗi 5 giây, flush PENDING items lên Sheets"""
    while True:
        await asyncio.sleep(5)
        pending = await run_sync(_get_pending_writes_sync, limit=50)
        for item in pending:
            try:
                client = SheetsAPIClient(item['spreadsheet_id'], item['web_app_url'])
                result = await client.add_transaction(**item['payload'])
                if result.get('success'):
                    await run_sync(_mark_done_sync, item['id'])
                else:
                    await run_sync(_increment_retry_sync, item['id'])
            except Exception as e:
                logger.error(f"Flush error {item['id']}: {e}")
                await run_sync(_increment_retry_sync, item['id'])

# Đăng ký trong main.py khi app start
application.job_queue.run_repeating(sheets_flush_worker_job, interval=5)
```

**4. Tăng concurrent_updates**
```python
# main.py
application = Application.builder()
    .token(TOKEN)
    .concurrent_updates(64)  # tăng từ 32
    .build()
```

**5. DB: Tách read replica (optional, nếu read query chiếm > 40% load)**
```
Nếu cần: Dùng PostgreSQL streaming replication
Primary: writes
Replica: reads (overview, stats, leaderboard)
```

**Việc KHÔNG nên làm:**
- ❌ Không dùng Redis cho queue (PostgreSQL pending table là đủ, đã có sẵn)
- ❌ Không tách worker ra process riêng (asyncio task trong cùng process là đủ)
- ❌ Không dùng Kafka/RabbitMQ (hoàn toàn over-engineer)
- ❌ Không tách microservice

**Rủi ro nếu không nâng cấp (vẫn giữ direct Sheets write):**
- Sheets 429 → user nhận error message → churn
- Event loop bị block bởi Sheets HTTP timeout (5–10s) → toàn bộ bot chậm
- Không có cách retry khi Sheets API down tạm thời

**Rủi ro nếu nâng cấp quá phức tạp (Redis + separate worker process):**
- Separate process phải handle graceful shutdown, zombie process risk
- Redis down → mất queue → mất dữ liệu nếu không thiết kế đúng

**Kiến trúc sau giai đoạn 3:**
```
Telegram ──webhook──► Nginx ──► PTB v20 process
                                    │
                        ┌───────────┼──────────────────┐
                        ▼           ▼                  ▼
                  Handler logic  asyncio.to_thread  Job Queue (PTB)
                        │                              │
                        ▼                              ▼ (every 5s)
                  sheets_write_queue          SheetsAPIClient
                  (PostgreSQL table)           (rate-limited)
                        │
                  PostgreSQL primary
                  (pool=15/30)
```

---

## GIAI ĐOẠN 4 — 3.000–7.000 User

### Trạng thái: VERTICAL SCALE + PROCESS SEPARATION

**Dấu hiệu kỹ thuật cần nâng cấp:**
- CPU sustained > 80% → VPS cần nâng cấp (4 vCPU → 8 vCPU)
- asyncio thread pool backlog thường xuyên (> 100 pending run_sync tasks)
- GIL contention: 1 Python process không tận dụng được multi-core
- Database connection pool liên tục đầy dù đã tăng size
- Memory bot process > 1GB
- Sheets flush worker không kịp xử lý batch (> 1000 pending items)

**Việc cần làm:**

**1. Nâng cấp VPS**
```
Current: 2 vCPU / 4GB RAM
Target:  8 vCPU / 16GB RAM (không cần multi-VPS)
Cost:    ~$40–60/month (DigitalOcean/Hetzner)
```

**2. Tách Sheets worker ra process riêng (lần đầu tách process)**
```
Process 1: Bot PTB (webhook handler) — 2 vCPU
Process 2: Sheets flush worker — 1 vCPU
Process 3: PostgreSQL — 2 vCPU (nếu trên cùng VPS)

Quản lý bằng: supervisord hoặc systemd
```

**3. Tối ưu DB queries**
```python
# Thêm index cho các query thường dùng
CREATE INDEX idx_transactions_user_date ON transactions(user_id, created_at DESC);
CREATE INDEX idx_users_referral ON users(referral_code) WHERE referral_code IS NOT NULL;

# Bật pg_stat_statements để profile slow queries
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
```

**4. Sheets: Batch ghi theo user (group by user_id trước khi flush)**
```python
async def sheets_flush_worker():
    # Nhóm pending items theo user để tránh multiple API calls/user/batch
    pending = await run_sync(_get_pending_writes_sync, limit=200)
    by_user = group_by_user(pending)
    
    tasks = [flush_for_user(user_id, items) for user_id, items in by_user.items()]
    await asyncio.gather(*tasks, return_exceptions=True)
```

**5. Caching kết quả query đọc nhiều**
```python
# Dùng in-memory dict với TTL — KHÔNG cần Redis
import cachetools

_cache = cachetools.TTLCache(maxsize=500, ttl=60)  # 60s TTL

def _get_user_settings_cached(user_id: int) -> dict:
    if user_id in _cache:
        return _cache[user_id]
    result = _actual_db_query(user_id)
    _cache[user_id] = result
    return result
```

**6. Tăng PostgreSQL max_connections**
```
# postgresql.conf
max_connections = 200
shared_buffers = 4GB
work_mem = 64MB
effective_cache_size = 12GB
```

**Việc KHÔNG nên làm:**
- ❌ Không dựng Kafka/RabbitMQ
- ❌ Không tách microservices (user-service, sheets-service, etc.)
- ❌ Không rewrite async ORM
- ❌ Không multi-VPS load balancer (PTB stateful → cần sticky session phức tạp)
- ❌ Không Kubernetes

**Rủi ro:**
- Tách process quá sớm: overhead IPC, phức tạp hơn debug
- Chưa profile DB trước khi scale up → thêm hardware nhưng vẫn slow

**Kiến trúc sau giai đoạn 4:**
```
Internet ──► Nginx (SSL)
                │
                ▼
          PTB Process (2 vCPU)          Sheets Worker Process (1 vCPU)
          webhook handlers               - Poll sheets_write_queue
          run_sync(db)                   - Batch by user_id
                │                        - SheetsAPIClient calls
                │                              │
                └──────────┬───────────────────┘
                           ▼
                  PostgreSQL (2 vCPU)
                  (pool=20/50, indices tuned)
                           │
                  cachetools TTLCache (in-process)
                           │
                  Prometheus ──► Grafana
```

---

## GIAI ĐOẠN 5 — 7.000–10.000+ User

### Trạng thái: MULTI-PROCESS + OPTIONAL SECOND VPS

**Dấu hiệu kỹ thuật cần nâng cấp:**
- 1 PTB process không đủ (> 500 concurrent messages/giây)
- PostgreSQL IOPS chạm giới hạn VPS disk
- Sheets API quota chạm ceiling dù batch (> 2000 writes/min tổng)
- Memory leak sau vài ngày uptime (PTB state accumulation)
- Deployment downtime > 0 (zero-downtime cần multi-instance)

**Việc cần làm:**

**1. Tách PostgreSQL sang VPS riêng (managed DB)**
```
Option A: Managed PostgreSQL (Neon.tech, Supabase, RDS) — $25–50/month
Option B: Dedicated DB VPS (2 vCPU / 8GB RAM) — $20/month
Lý do: IOPS bottleneck, backup management, connection pooling (PgBouncer)
```

**2. PgBouncer — connection pooler**
```
Hiện tại: mỗi Python thread mở 1 DB connection
PgBouncer: pool 1000 app connections → 50 PostgreSQL connections
Config: transaction pooling mode
```

**3. PTB multi-worker với Redis (lần đầu Redis thật sự cần thiết)**
```
Tại sao Redis bây giờ mới cần:
- PTB v20 dùng in-memory để track conversation state
- Nếu chạy multiple workers, state phải shared
- Redis làm shared state store cho PTB persistence

architecture:
  worker 1 ──┐
  worker 2 ──┼──► Redis (conversation state) ──► PostgreSQL (data)
  worker 3 ──┘
```

**4. Quota Sheets: Cân nhắc Google Workspace (business)**
```
Free tier:  60 req/min per project
Workspace:  3000 req/min per project
Cost:       $6/user/month — chỉ cần 1 service account
```

**5. Optional: Tách bot thành microservices CHỈ nếu có team**
```
Chỉ tách khi:
- Team > 3 developer
- Cần độc lập deploy từng service
- Sheets service cần scale riêng

Các service có thể tách:
- sheets-writer-service (Python, async)
- notification-service (daily reminders)
- bot-core (PTB handlers)

KHÔNG tách nếu vẫn 1 developer: overhead quản lý quá lớn
```

**6. Zero-downtime deployment**
```bash
# Blue-green với Nginx upstream swap
# Hoặc đơn giản hơn: graceful restart với systemd
ExecStop=/bin/kill -SIGTERM $MAINPID
TimeoutStopSec=30
```

**Việc KHÔNG nên làm:**
- ❌ Kubernetes (over-kill, 1–2 VPS đủ cho 10k user)
- ❌ Kafka (PostgreSQL queue + asyncio đủ cho throughput này)
- ❌ Rewrite sang async ORM (ROI quá thấp, rủi ro regression cao)

**Kiến trúc sau giai đoạn 5:**
```
Internet
   │
Nginx/Cloudflare (SSL, DDoS protection)
   │
   ├──► PTB Worker 1 (2 vCPU)
   ├──► PTB Worker 2 (2 vCPU)     ◄── Redis (shared state)
   └──► PTB Worker 3 (2 vCPU)
              │
              ▼
         PgBouncer (connection pooler)
              │
              ▼
         PostgreSQL VPS
         (dedicated, 4 vCPU / 16GB)
              │
         sheets_write_queue
              │
              ▼
   Sheets Worker Process
   (batch, rate-limited)
              │
   Google Sheets API (Workspace tier)
```

---

## BẢNG TỔNG KẾT

| Mốc user | Hành động chính | Đừng làm | Chi phí VPS ước tính |
|---|---|---|---|
| 0–200 | Launch as-is, monitor log | Redis, queue, webhook | $10–20/tháng |
| 200–1.000 | Webhook + retry backoff + DB pool ×2 | Batch worker, Redis | $20–40/tháng |
| 1.000–3.000 | Sheets write queue (PG table) + asyncio flush worker | Redis, separate process | $30–50/tháng |
| 3.000–7.000 | Nâng VPS + tách Sheets worker process + cache TTL | Kafka, microservices | $60–100/tháng |
| 7.000–10.000+ | Managed DB + PgBouncer + Redis + multi-worker PTB | Kubernetes, full rewrite | $120–200/tháng |

---

## CHECKLIST TRƯỚC LAUNCH (0–200 user)

- [x] `run_sync` wrapper cho mọi DB call trong async handler
- [x] `concurrent_updates=32`
- [x] PostgreSQL pool_size=5 / max_overflow=5
- [x] SheetsAPIClient (async HTTP) thay SheetsWriter
- [ ] Telegram alert khi exception không catch
- [ ] Log rotation (loguru `rotation="100MB"`)
- [ ] Cron backup PostgreSQL daily
- [ ] Test Sheets 429 retry behavior

---

## GHI CHÚ KỸ THUẬT

### Tại sao KHÔNG rewrite async ORM?
SQLAlchemy async (với asyncpg) đòi hỏi refactor toàn bộ query code. Với `asyncio.to_thread` wrapper hiện tại, tất cả DB calls chạy trong thread pool — non-blocking với event loop. ROI quá thấp, rủi ro regression quá cao trước khi có user base ổn định.

### Tại sao KHÔNG Kafka?
Kafka yêu cầu: Zookeeper (hoặc KRaft), Kafka broker, consumer group management, schema registry. PostgreSQL `sheets_write_queue` table với `status=PENDING/DONE/FAILED` và 1 asyncio worker xử lý được > 10.000 writes/phút — thừa cho quy mô 10k user.

### Tại sao KHÔNG Redis sớm?
Redis thật sự cần khi: (a) cần shared state giữa multiple PTB workers, hoặc (b) cần pub/sub. 1 process PTB không cần Redis. Thêm Redis sớm = thêm 1 điểm failure, thêm complexity vận hành mà không có lợi ích cụ thể.

### Sheets quota thực tế
- Free: 60 read req/min, 60 write req/min per project
- 1k user active × 5 writes/ngày = 5.000 writes/ngày = ~3.5 writes/phút average
- Peak 10x = 35 writes/phút → vẫn dưới quota free tier
- Chỉ cần queue khi peak > 60 writes/phút (≈ 1.500+ daily active users)
