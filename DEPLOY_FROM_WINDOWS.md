# 🎯 HƯỚNG DẪN DEPLOY TỪ GITHUB LÊN VPS

Code đã ở trên GitHub: https://github.com/mettatuan/freedom-wallet-bot

Bây giờ cần pull code từ GitHub về VPS và chạy bot.

---

## ⚡ CÁCH NHANH NHẤT (Khuyến nghị)

### Lần đầu tiên (first time setup):

```powershell
# Từ máy Windows (PowerShell)
.\deploy_from_github.ps1 -VPS_HOST "your_vps_ip" -VPS_USER "root" -SetupFirstTime
```

Script sẽ tự động:
1. Clone repo từ GitHub
2. Checkout branch `cleanup/hard-refactor`
3. Setup Python virtual environment
4. Cài dependencies
5. Tạo file `.env` template
6. Run database migration
7. Setup update script

**Sau đó chỉ cần edit bot token:**

```powershell
# Edit .env file trên VPS
ssh root@your_vps_ip "nano /root/FreedomWalletBot/.env"

# Thay REPLACE_WITH_YOUR_TOKEN bằng token thật
# Nhấn Ctrl+X, Y, Enter để lưu
```

### Lần sau (update code):

```powershell
# Chỉ cần 1 lệnh
.\deploy_from_github.ps1 -VPS_HOST "your_vps_ip" -VPS_USER "root"
```

---

## 📋 CÁCH THỦ CÔNG (Từng bước)

### Lần đầu tiên:

```bash
# Bước 1: SSH vào VPS
ssh root@your_vps_ip

# Bước 2: Clone repo
cd /root
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
cd FreedomWalletBot

# Bước 3: Checkout branch
git checkout cleanup/hard-refactor

# Bước 4: Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Bước 5: Tạo .env file
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
EOF

# Bảo mật .env
chmod 600 .env

# Bước 6: Run migration
python migrate_database.py

# Bước 7: Cho phép execute update script
chmod +x update_from_github.sh

# Bước 8: Start bot
mkdir -p logs
nohup python main.py > logs/bot.log 2>&1 &

# Bước 9: Xem logs
tail -f logs/bot.log
```

### Lần sau (update):

```bash
# SSH vào VPS
ssh root@your_vps_ip

# Chạy update script
/root/FreedomWalletBot/update_from_github.sh
```

---

## 🔧 LỖI THƯỜNG GẶP

### ❌ Lỗi: `chmod: command not found` trên Windows

**Nguyên nhân:** Bạn đang chạy lệnh Linux trên Windows PowerShell

**Giải pháp:** Dùng script `deploy_from_github.ps1` đã tạo:

```powershell
.\deploy_from_github.ps1 -VPS_HOST "your_vps_ip" -VPS_USER "root"
```

### ❌ Lỗi: SSH connection refused

**Kiểm tra:**

```powershell
# Test SSH
ssh root@your_vps_ip "echo 'SSH OK'"

# Nếu không được, kiểm tra:
# 1. IP đúng chưa?
# 2. Firewall có block port 22 không?
# 3. SSH key đã setup chưa?
```

### ❌ Lỗi: Git clone failed

**Kiểm tra VPS có Git chưa:**

```bash
ssh root@your_vps_ip "git --version"

# Nếu chưa có, cài Git:
ssh root@your_vps_ip "apt update && apt install git -y"
```

### ❌ Lỗi: Bot không start

**Xem logs:**

```bash
ssh root@your_vps_ip "tail -50 /root/FreedomWalletBot/logs/bot.log"

# Kiểm tra .env:
ssh root@your_vps_ip "cat /root/FreedomWalletBot/.env"

# Nếu token sai, edit lại:
ssh root@your_vps_ip "nano /root/FreedomWalletBot/.env"
```

---

## 📊 WORKFLOW TÓM TẮT

```
┌─────────────────┐
│  Local Machine  │
│   (Windows)     │
└────────┬────────┘
         │
         │ 1. git push origin cleanup/hard-refactor
         ↓
┌─────────────────┐
│     GitHub      │
│  mettatuan/     │
│ freedom-wallet  │
└────────┬────────┘
         │
         │ 2. deploy_from_github.ps1
         │    (SSH + git pull)
         ↓
┌─────────────────┐
│      VPS        │
│    (Linux)      │
│                 │
│ /root/          │
│ FreedomWallet   │
│ Bot/            │
│  ├── .venv/     │
│  ├── bot/       │
│  ├── main.py    │
│  └── ...        │
└─────────────────┘
         │
         │ 3. python main.py
         ↓
┌─────────────────┐
│   Telegram      │
│   Bot API       │
└─────────────────┘
```

---

## ✅ CHECKLIST

**Setup lần đầu:**
- [ ] VPS đã cài Python 3.10+
- [ ] VPS đã cài Git
- [ ] SSH key đã setup (login không cần password)
- [ ] Đã có bot token từ BotFather
- [ ] Clone repo từ GitHub
- [ ] Tạo .env với bot token
- [ ] Run migration
- [ ] Start bot
- [ ] Test trên Telegram

**Update lần sau:**
- [ ] Push code mới lên GitHub
- [ ] Chạy `deploy_from_github.ps1` hoặc `update_from_github.sh`
- [ ] Kiểm tra logs
- [ ] Test trên Telegram

---

## 🎯 COMMANDS CHEAT SHEET

```powershell
# WINDOWS (từ máy local):

# Deploy lần đầu
.\deploy_from_github.ps1 -VPS_HOST "123.45.67.89" -VPS_USER "root" -SetupFirstTime

# Update code
.\deploy_from_github.ps1 -VPS_HOST "123.45.67.89" -VPS_USER "root"

# Xem logs
ssh root@123.45.67.89 "tail -f /root/FreedomWalletBot/logs/bot.log"

# Check status
ssh root@123.45.67.89 "pgrep -fa python"

# Restart bot
ssh root@123.45.67.89 "pkill -f python; cd /root/FreedomWalletBot && nohup python main.py > logs/bot.log 2>&1 &"
```

```bash
# VPS (trên Linux):

# Update từ GitHub
/root/FreedomWalletBot/update_from_github.sh

# Xem logs
tail -f /root/FreedomWalletBot/logs/bot.log

# Check bot chạy chưa
pgrep -fa python

# Restart bot
pkill -f python
cd /root/FreedomWalletBot
source .venv/bin/activate
nohup python main.py > logs/bot.log 2>&1 &
```

---

🎉 **Xong! Giờ bạn có thể deploy chỉ với 1 lệnh từ Windows!**
