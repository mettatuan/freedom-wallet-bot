# 🚀 HƯỚNG DẪN DEPLOY LÊN VPS

## 📋 Tóm tắt nhanh

```bash
# 1. Cấu hình thông tin VPS
# Edit file deploy_config.txt với IP, user, path của VPS

# 2. Chạy script deploy
# Windows PowerShell:
.\deploy_to_vps.ps1 -VPS_HOST "your_ip" -VPS_USER "root" -VPS_PATH "/root/FreedomWalletBot"

# Linux/Mac:
./deploy_to_vps.sh

# 3. Xem logs sau khi deploy
ssh your_user@your_vps_ip "tail -f /path/to/bot/logs/bot.log"
```

---

## ✅ CHUẨN BỊ TRƯỚC KHI DEPLOY

### 1. **Chuẩn bị VPS**

VPS cần có:
- **Python 3.10+** (`python3 --version`)
- **pip** (`pip --version`)
- **SSH access** (có thể SSH vào VPS)
- **Disk space**: Tối thiểu 500MB
- **RAM**: Tối thiểu 512MB

**Kiểm tra kết nối VPS:**
```bash
ssh your_user@your_vps_ip
```

Nếu chưa setup SSH key, chạy:
```bash
# Tạo SSH key
ssh-keygen -t rsa -b 4096

# Copy key lên VPS (nhập password 1 lần cuối)
ssh-copy-id your_user@your_vps_ip

# Test login không cần password
ssh your_user@your_vps_ip
```

### 2. **Tạo file .env trên VPS**

File `.env` chứa token bot (KHÔNG upload lên Git!):

```bash
# SSH vào VPS
ssh your_user@your_vps_ip

# Tạo thư mục bot
mkdir -p /root/FreedomWalletBot
cd /root/FreedomWalletBot

# Tạo file .env
nano .env
```

Nội dung file `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
```

Bấm `Ctrl+X`, `Y`, `Enter` để lưu.

### 3. **Test local trước khi deploy**

```bash
# Chạy test suite
python test_phase3.py

# Nếu tất cả 6 tests PASS → OK để deploy
```

---

## 🚀 CÁCH 1: DEPLOY TỰ ĐỘNG (Khuyến nghị)

### **Windows (PowerShell)**

```powershell
# Mở PowerShell tại thư mục FreedomWalletBot
cd D:\Projects\FreedomWalletBot

# Chạy deploy script
.\deploy_to_vps.ps1 `
    -VPS_HOST "123.45.67.89" `
    -VPS_USER "root" `
    -VPS_PATH "/root/FreedomWalletBot"

# Xem logs sau khi deploy
ssh root@123.45.67.89 "tail -f /root/FreedomWalletBot/logs/bot.log"
```

**Options:**
```powershell
# Dry run (chỉ xem sẽ làm gì, không thực thi)
.\deploy_to_vps.ps1 -DryRun -VPS_HOST "..." -VPS_USER "..." -VPS_PATH "..."

# Skip tests (không test, deploy luôn - cẩn thận!)
.\deploy_to_vps.ps1 -SkipTests -VPS_HOST "..." -VPS_USER "..." -VPS_PATH "..."
```

### **Linux/Mac (Bash)**

```bash
# Cho phép execute script
chmod +x deploy_to_vps.sh

# Chạy deploy
VPS_HOST="123.45.67.89" \
VPS_USER="root" \
VPS_PATH="/root/FreedomWalletBot" \
./deploy_to_vps.sh

# Hoặc edit biến trong script rồi chạy:
./deploy_to_vps.sh
```

---

## 📦 CÁCH 2: DEPLOY THỦ CÔNG

Nếu script tự động không chạy được:

### **Bước 1: Backup database cũ trên VPS**

```bash
ssh your_user@your_vps_ip

cd /root/FreedomWalletBot
mkdir -p data/backups

# Backup database hiện tại (nếu có)
if [ -f data/bot.db ]; then
    cp data/bot.db data/backups/backup_$(date +%Y%m%d_%H%M%S).db
    echo "✅ Database backed up"
fi
```

### **Bước 2: Stop bot**

```bash
# Trên VPS
pkill -f 'python.*main.py'
sleep 2

# Kiểm tra đã stop chưa
pgrep -fa python
```

### **Bước 3: Upload code lên VPS**

**Option A: rsync (nhanh nhất)**
```bash
# Từ máy local
rsync -avz --progress \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='data/bot.db' \
    --exclude='logs/*.log' \
    ./ your_user@your_vps_ip:/root/FreedomWalletBot/
```

**Option B: Git (nếu dùng Git)**
```bash
# Push code lên Git repo
git add .
git commit -m "Phase 2-3 complete"
git push

# Trên VPS pull code
ssh your_user@your_vps_ip
cd /root/FreedomWalletBot
git pull
```

**Option C: Manual upload (WinSCP, FileZilla)**
- Upload các file sau lên VPS:
  - Thư mục `bot/` (toàn bộ)
  - Thư mục `config/` (toàn bộ)
  - File `main.py`
  - File `requirements.txt`
  - File `migrate_database.py`
  - File `test_phase3.py`

### **Bước 4: Cài dependencies trên VPS**

```bash
# SSH vào VPS
ssh your_user@your_vps_ip
cd /root/FreedomWalletBot

# Tạo virtual environment (nếu chưa có)
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Cài packages
pip install --upgrade pip
pip install -r requirements.txt
```

### **Bước 5: Run migration**

```bash
# Trên VPS (vẫn trong .venv)
python migrate_database.py

# Nếu thành công sẽ thấy:
# ✅ Migration complete!
# - 8 tables created
# - Users table: 56 columns
# - Transactions table: 9 columns
```

### **Bước 6: Start bot**

```bash
# Start bot trong background
nohup python main.py > logs/bot.log 2>&1 &

# Đợi 3 giây
sleep 3

# Kiểm tra bot đã chạy chưa
pgrep -fa python

# Nếu thấy:
# 12345 python main.py
# → Bot đang chạy (PID 12345)
```

### **Bước 7: Xem logs**

```bash
# Xem logs real-time
tail -f logs/bot.log

# Hoặc từ máy local:
ssh your_user@your_vps_ip "tail -f /root/FreedomWalletBot/logs/bot.log"

# Xem 50 dòng cuối
tail -50 logs/bot.log
```

---

## 🔍 KIỂM TRA SAU KHI DEPLOY

### 1. **Bot có chạy không?**

```bash
ssh your_user@your_vps_ip "pgrep -fa python"

# Nếu thấy output:
# 12345 python main.py
# → ✅ Bot đang chạy
```

### 2. **Logs có lỗi không?**

```bash
ssh your_user@your_vps_ip "tail -50 /root/FreedomWalletBot/logs/bot.log"

# Tìm các dòng:
# ✅ "Application started"
# ✅ "Bot polling started"
# ❌ "ERROR", "Exception", "Failed"
```

### 3. **Test bot trên Telegram**

1. Mở Telegram, tìm bot của bạn
2. Gửi `/start` → Phải thấy keyboard 8 nút
3. Click **📊 Tổng quan** → Phải thấy số dư, streak
4. Gửi **35k ăn sáng** → Phải lưu giao dịch
5. Click **📊 Tổng quan** lại → Số dư phải giảm 35k

### 4. **Database có data không?**

```bash
ssh your_user@your_vps_ip

cd /root/FreedomWalletBot
source .venv/bin/activate

# Kiểm tra transactions
python << EOF
from bot.utils.database import SessionLocal, Transaction
from datetime import datetime, timedelta

session = SessionLocal()

# Đếm transactions 24h gần nhất
count = session.query(Transaction).filter(
    Transaction.created_at >= datetime.now() - timedelta(days=1)
).count()

print(f"Transactions trong 24h: {count}")
session.close()
EOF
```

---

## 🔧 TROUBLESHOOTING

### ❌ **Bot không start**

```bash
# Xem logs chi tiết
tail -100 logs/bot.log

# Kiểm tra lỗi phổ biến:

# 1. Thiếu .env file
ls -la .env
# Nếu không có → tạo file .env với TELEGRAM_BOT_TOKEN

# 2. Token sai
cat .env
# Kiểm tra token có đúng không

# 3. Port/network blocked
# Kiểm tra VPS có kết nối internet không
curl https://api.telegram.org

# 4. Dependencies thiếu
pip list | grep python-telegram-bot
# Nếu không thấy → pip install -r requirements.txt
```

### ❌ **SSH connection failed**

```bash
# Test kết nối
ssh -v your_user@your_vps_ip

# Nếu "Connection refused":
# - Kiểm tra IP VPS đúng chưa
# - Kiểm tra firewall VPS có cho phép port 22 không

# Nếu "Permission denied":
# - Kiểm tra username đúng chưa
# - Setup SSH key: ssh-copy-id your_user@your_vps_ip
```

### ❌ **rsync command not found (Windows)**

Windows không có rsync built-in. Có 3 cách:

**Cách 1: Dùng Git Bash**
```bash
# Mở Git Bash (đã cài Git for Windows)
rsync -avz ./ your_user@your_vps_ip:/path/to/bot/
```

**Cách 2: Dùng WSL**
```bash
# Cài WSL nếu chưa có
wsl --install

# Chạy rsync trong WSL
wsl rsync -avz ./ your_user@your_vps_ip:/path/to/bot/
```

**Cách 3: Dùng WinSCP/FileZilla**
- Download WinSCP: https://winscp.net/
- Upload thủ công các file lên VPS

### ❌ **Migration failed**

```bash
# Xem lỗi migration
python migrate_database.py

# Nếu "Table already exists":
# → Database đã có schema, không cần migrate

# Nếu muốn migrate lại (XÓA DATA CŨ!):
rm data/bot.db
python migrate_database.py
```

### ❌ **Bot chạy nhưng không reply**

```bash
# Kiểm tra logs
tail -f logs/bot.log

# Nếu thấy "Application started" nhưng không thấy "Message received":
# → Telegram API blocked hoặc token sai

# Test token:
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Phải trả về thông tin bot, nếu không → token sai
```

---

## 🛡️ SETUP TỰ ĐỘNG RESTART (Khuyến nghị)

### **Systemd Service (Linux VPS)**

Tạo service để bot tự restart khi crash/reboot:

```bash
# SSH vào VPS
ssh your_user@your_vps_ip

# Tạo service file
sudo nano /etc/systemd/system/freedom-wallet-bot.service
```

Nội dung:
```ini
[Unit]
Description=Freedom Wallet Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/FreedomWalletBot
Environment="PATH=/root/FreedomWalletBot/.venv/bin"
ExecStart=/root/FreedomWalletBot/.venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/root/FreedomWalletBot/logs/bot.log
StandardError=append:/root/FreedomWalletBot/logs/bot.log

[Install]
WantedBy=multi-user.target
```

Kích hoạt service:
```bash
# Enable service (tự chạy khi reboot)
sudo systemctl enable freedom-wallet-bot

# Start service
sudo systemctl start freedom-wallet-bot

# Kiểm tra status
sudo systemctl status freedom-wallet-bot

# Xem logs
sudo journalctl -u freedom-wallet-bot -f

# Stop service
sudo systemctl stop freedom-wallet-bot

# Restart service
sudo systemctl restart freedom-wallet-bot
```

---

## 📊 MONITORING

### **Xem logs real-time từ máy local**

```bash
# Logs bot
ssh your_user@your_vps_ip "tail -f /root/FreedomWalletBot/logs/bot.log"

# Logs systemd (nếu dùng systemd)
ssh your_user@your_vps_ip "sudo journalctl -u freedom-wallet-bot -f"
```

### **Check bot status**

```bash
# Kiểm tra process
ssh your_user@your_vps_ip "pgrep -fa python"

# Kiểm tra uptime
ssh your_user@your_vps_ip "ps -eo pid,etime,cmd | grep python"
```

### **Check database size**

```bash
ssh your_user@your_vps_ip "du -sh /root/FreedomWalletBot/data/bot.db"
```

---

## 🔄 UPDATE BOT SAU NÀY

Khi có code mới cần deploy:

```bash
# Chạy lại deploy script
.\deploy_to_vps.ps1 -VPS_HOST "..." -VPS_USER "..." -VPS_PATH "..."

# Script sẽ:
# 1. Run tests local
# 2. Backup database VPS
# 3. Stop bot
# 4. Upload code mới
# 5. Run migration (nếu có)
# 6. Start bot
# 7. Verify

# Nếu có lỗi → Bot tự động rollback về backup
```

---

## 📝 CHECKLIST DEPLOY

- [ ] VPS đã cài Python 3.10+
- [ ] VPS đã setup SSH key (login không cần password)
- [ ] File `.env` đã tạo trên VPS với TELEGRAM_BOT_TOKEN
- [ ] Test suite đã PASS local (6/6 tests)
- [ ] Backup database cũ trên VPS (nếu có)
- [ ] Deploy script đã chạy thành công
- [ ] Bot process đang chạy trên VPS
- [ ] Logs không có ERROR
- [ ] Test bot trên Telegram (gửi /start, ghi giao dịch)
- [ ] Setup systemd service (optional nhưng khuyến nghị)

---

## 🎯 TÓM TẮT NHANH

**Deploy lần đầu:**
```bash
# 1. Tạo .env trên VPS
ssh root@your_vps "cat > /root/FreedomWalletBot/.env << EOF
TELEGRAM_BOT_TOKEN=your_token_here
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
EOF"

# 2. Chạy deploy
.\deploy_to_vps.ps1 -VPS_HOST "your_ip" -VPS_USER "root" -VPS_PATH "/root/FreedomWalletBot"

# 3. Xem logs
ssh root@your_vps "tail -f /root/FreedomWalletBot/logs/bot.log"
```

**Update sau này:**
```bash
# Chỉ cần chạy lại deploy script
.\deploy_to_vps.ps1 -VPS_HOST "your_ip" -VPS_USER "root" -VPS_PATH "/root/FreedomWalletBot"
```

**Khởi động lại bot:**
```bash
ssh root@your_vps "pkill -f python; cd /root/FreedomWalletBot && nohup python main.py > logs/bot.log 2>&1 &"
```

---

🎉 **Xong! Bot giờ đã chạy 24/7 trên VPS!**
