# 🚀 DEPLOYMENT - PHASE 1.5

## ✅ Pre-deployment Checklist

Trước khi deploy, verify:

```bash
cd D:\Projects\FreedomWalletBot
python test_api_url.py
python test_getbalance.py
```

**Expected:**
- ✅ API URL working
- ✅ getBalance returns data
- ✅ Cache hit rate 100%

---

## 📋 BƯỚC 1: APPS SCRIPT (5 phút)

### Option A: Deploy via Google Apps Script Editor (RECOMMENDED)

1. **Mở Apps Script project:**
   - Vào: https://script.google.com/home
   - Tìm project: **"Freedom Wallet"** hoặc tương tự

2. **Verify code mới nhất:**
   - File `bot-api-handler-vietnamese.gs` phải có:
     ```javascript
     // Line ~150
     const rateLimitKey = `rateLimit_${apiKey}_${spreadsheetId}`;
     ```
   - Nếu chưa có, copy code từ `D:\Projects\FreedomWallet\bot-api-handler-vietnamese.gs`

3. **Deploy Web App:**
   - Click **Deploy** → **Manage deployments**
   - Nếu có deployment active → Copy URL
   - Nếu chưa có:
     - **New deployment**
     - Type: **Web app**
     - Execute as: **Me**
     - Who has access: **Anyone**
     - Click **Deploy**

4. **Copy Web App URL:**
   ```
   https://script.google.com/macros/s/AKfycb.../exec
   ```

5. **Update .env:**
   ```bash
   # Edit D:\Projects\FreedomWalletBot\.env
   FREEDOM_WALLET_API_URL=<your_web_app_url>
   ```

---

### Option B: Deploy via clasp (Advanced)

**Only if clasp already setup:**

```bash
cd D:\Projects\FreedomWallet

# Login (if not logged in)
clasp login

# Push code
clasp push

# Deploy
clasp deploy --description "Phase 1.5 - Rate limiting + Cache"
```

---

## 📋 BƯỚC 2: ENABLE AUTO SYNC (2 phút)

**In Apps Script Editor:**

1. Open file: `AutoSyncTriggers.gs`

2. Run function: `enableAutoSync()`
   - Click dropdown → Select `enableAutoSync`
   - Click **Run** (▶️)
   - Authorize if needed

3. **Verify triggers created:**
   - Click **Triggers** (clock icon) trong menu bên trái
   - Should see 2 triggers:
     - ✅ `onSheetChange` - On change event
     - ✅ `autoSyncByTime` - Time-based (5 min)

---

## 📋 BƯỚC 3: TEST CONNECTION (2 phút)

```bash
cd D:\Projects\FreedomWalletBot

# Test API connectivity
python test_api_url.py

# Test getBalance
python test_getbalance.py

# Test cache performance
python test_cache_performance.py
```

**Expected results:**
```
✅ API URL working
✅ getBalance: 50,297,000đ
✅ Cache hit rate: 100%
```

---

## 📋 BƯỚC 4: START BOT (1 phút)

### Method 1: Quick Start (Windows)

```bash
cd D:\Projects\FreedomWalletBot
start.bat
```

### Method 2: Quick Start (Linux/Mac)

```bash
cd /path/to/FreedomWalletBot
chmod +x start.sh
./start.sh
```

### Method 3: Manual Start

```bash
cd D:\Projects\FreedomWalletBot
python main.py
```

**Expected output:**
```
========================================
  FREEDOM WALLET BOT - STARTING
========================================

[1/3] Checking dependencies... ✅
[2/3] Running connectivity test... ✅
[3/3] Starting bot...

========================================
  BOT IS RUNNING
  Press Ctrl+C to stop
========================================

2026-02-09 14:30:52 | INFO | Bot started successfully
2026-02-09 14:30:52 | INFO | Listening for messages...
```

---

## 🧪 BƯỚC 5: TEST BOT (5 phút)

### Test 1: Basic Commands

Open Telegram → Find your bot → Send:

```
/start
```

**Expected:** Welcome message với menu buttons

---

### Test 2: Register (if needed)

```
/register
```

Follow wizard để kết nối Google Sheet

---

### Test 3: Quick Transaction

```
chi 50k cafe
```

**Expected:**
```
✅ Đã ghi nhận chi tiêu 50,000đ
⏳ Balance sẽ tự động cập nhật sau 10-15 giây
```

---

### Test 4: Check Balance (with Cache!)

```
/balance
```

**Expected:**
- First time: 2-3s (API call)
- Second time: **Instant!** (<1s - cache hit)

---

### Test 5: Manual Sync

```
/sync
```

**Expected:**
```
🔄 Đang đồng bộ...
✅ Đã đồng bộ! Balance đã được cập nhật.
```

---

## 📊 MONITORING (Week 1)

### Check Apps Script Execution

1. Apps Script Editor → **Executions** (left menu)
2. Verify:
   - ✅ `onSheetChange` running after sheet edits
   - ✅ `autoSyncByTime` running every 5 minutes
   - ✅ No errors

---

### Check Rate Limiting

**In Apps Script Editor:**

```javascript
function checkRateLimitStatus() {
  const props = PropertiesService.getScriptProperties().getProperties();
  
  for (const key in props) {
    if (key.startsWith('rateLimit_')) {
      Logger.log(`${key}: ${props[key]}`);
    }
  }
}
```

Run → Check logs:
```
rateLimit_fwb_bot_testing_2026_1er6t9JQ...: {"count":45,"resetTime":1707487200000}
```

**Analysis:**
- Count: 45 requests used
- Should be <100 per hour per user
- Multiple sheets = multiple counters ✅

---

### Check Bot Logs

```bash
cd D:\Projects\FreedomWalletBot
cat data/logs/bot.log
```

Look for:
```
📦 Cache hit: balance     ← Good! Fast response
📡 API call: getBalance  ← Cache miss, normal
🗑️ Cache invalidated      ← After writes
```

**Target metrics:**
- Cache hit rate: >70%
- Average response time: <500ms
- API calls per user: <50/day

---

## 🐛 TROUBLESHOOTING

### Issue 1: Bot not starting

**Error:** `ModuleNotFoundError: No module named 'telegram'`

**Fix:**
```bash
pip install -r requirements.txt
```

---

### Issue 2: API connection failed

**Error:** `HTTP 404` or `Unauthorized`

**Fix:**
1. Check `.env` file:
   ```bash
   FREEDOM_WALLET_API_URL=<correct_url>
   FREEDOM_WALLET_API_KEY=fwb_bot_testing_2026
   ```
2. Verify deployment active in Apps Script
3. Run `python test_api_url.py` để debug

---

### Issue 3: Cache not working

**Symptom:** All balance queries take 2-3s

**Debug:**
```bash
python test_cache_performance.py
```

**Expected:** Cache hit rate >80%

**If failing:**
- Check `sheets_api_client.py` has cache code
- Verify `.env` loaded before import
- Check logs for "📦 Cache hit" messages

---

### Issue 4: Auto sync trigger not firing

**Symptom:** Balance không update sau 10-15s

**Check:**
1. Apps Script → **Triggers**
2. Verify `onSheetChange` exists
3. Try manual trigger:
   ```javascript
   testAutoSync()  // Run this function
   ```

**If failing:**
- Re-run `enableAutoSync()`
- Check execution logs for errors
- Verify sheet name = "Giao dịch" (Vietnamese)

---

### Issue 5: Rate limit hit too early

**Symptom:** `Rate limit exceeded` after <100 requests

**Check:**
```javascript
// In Apps Script
function checkRateLimit() {
  const rateLimitKey = `rateLimit_fwb_bot_testing_2026_1er6t9JQ...`;
  const data = PropertiesService.getScriptProperties().getProperty(rateLimitKey);
  Logger.log(data);
}
```

**Fix:**
- Use `fwb_bot_testing_2026` key (1000 req/hour)
- Or increase production limit to 200

---

## ✅ SUCCESS CRITERIA

**Bot is production-ready when:**

```
□ Apps Script deployed with latest code
□ Auto sync triggers active (2 triggers)
□ API connectivity test passes
□ Cache hit rate >70%
□ Bot responds to /start
□ Transaction recording works
□ Balance query <500ms (cached)
□ Manual /sync works (3-7s)
□ No errors in execution logs
□ Rate limiting working per user
```

---

## 🎯 NEXT STEPS (Week 2+)

**Optional optimizations:**

1. **Monitor metrics** (Week 1)
   - Cache hit rate
   - Response times
   - API call volume
   - Rate limit hits

2. **Optimize if needed** (Week 2)
   - If cache <70% → Upgrade to SQLite
   - If >100 users → Add monitoring dashboard
   - If rate limit hit → Increase limits

3. **Scale** (Week 3+)
   - See INTEGRATION_ASSESSMENT.md Option 2
   - Add persistent cache
   - Implement batch operations

---

## 📞 SUPPORT

**If stuck:**
1. Check logs: `data/logs/bot.log`
2. Run tests: `python test_api_url.py`
3. Check Apps Script executions
4. See troubleshooting section above

**Files for reference:**
- [PHASE_1.5_DEPLOYMENT.md](PHASE_1.5_DEPLOYMENT.md) - Detailed guide
- [SYNC_STRATEGY.md](../FreedomWallet/SYNC_STRATEGY.md) - Strategy overview
- [fix_api_url.md](fix_api_url.md) - API URL troubleshooting
- [BOT_PYTHON_CODE_UPDATES.md](../FreedomWallet/docs/BOT_PYTHON_CODE_UPDATES.md) - Code changes
