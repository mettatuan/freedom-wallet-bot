# 🔄 Git-Based VPS Deployment

Hướng dẫn deploy Freedom Wallet Bot lên VPS bằng Git (pull-based deployment).

---

## 🎯 Ưu điểm

✅ **Đơn giản:** Chỉ cần `git pull` để cập nhật  
✅ **Version control:** Track changes, rollback dễ dàng  
✅ **Tự động:** Setup webhook để auto-deploy  
✅ **Nhất quán:** Same code trên local và VPS  

---

## 📋 Prerequisites

### 1. VPS đã cài Git

```bash
# Kiểm tra Git
git --version

# Nếu chưa có, cài Git
# Ubuntu/Debian:
sudo apt update
sudo apt install git

# CentOS/RHEL:
sudo yum install git
```

### 2. GitHub repo đã có code

Repo: https://github.com/mettatuan/freedom-wallet-bot

---

## 🚀 SETUP LẦN ĐẦU

### Step 1: SSH vào VPS

```bash
ssh root@your_vps_ip
```

### Step 2: Clone repo

```bash
# Clone repo
cd /root
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot

# Vào thư mục
cd FreedomWalletBot

# Checkout branch (nếu không dùng main)
git checkout cleanup/hard-refactor
```

### Step 3: Setup Python environment

```bash
# Tạo virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Cài dependencies
pip install -r requirements.txt
```

### Step 4: Tạo .env file

```bash
# Tạo .env với bot token
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
EOF

# Set permissions (bảo mật)
chmod 600 .env
```

### Step 5: Database migration

```bash
# Chạy migration
python migrate_database.py

# Output:
# ✅ Migration complete!
# - 8 tables created
# - Users: 56 columns
# - Transactions: 9 columns
```

### Step 6: Test bot

```bash
# (Optional) Chạy tests
python test_phase3.py

# Nếu tất cả PASS → OK
```

### Step 7: Start bot

```bash
# Tạo thư mục logs
mkdir -p logs

# Start bot với nohup
nohup python main.py > logs/bot.log 2>&1 &

# Đợi 3 giây
sleep 3

# Kiểm tra bot đã chạy
pgrep -fa python

# Xem logs
tail -f logs/bot.log
```

### Step 8: Setup systemd (Recommended)

Để bot tự restart khi crash/reboot:

```bash
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

Kích hoạt:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable freedom-wallet-bot

# Start service
sudo systemctl start freedom-wallet-bot

# Kiểm tra status
sudo systemctl status freedom-wallet-bot

# Xem logs real-time
sudo journalctl -u freedom-wallet-bot -f
```

---

## 🔄 UPDATE CODE (Deploy mới)

Khi có code mới trên GitHub:

### Cách 1: Manual update

```bash
# SSH vào VPS
ssh root@your_vps_ip
cd /root/FreedomWalletBot

# Pull code mới
git pull origin main  # hoặc branch bạn đang dùng

# Cài dependencies mới (nếu có)
source .venv/bin/activate
pip install -r requirements.txt

# Chạy migration (nếu có schema changes)
python migrate_database.py

# Restart bot
# Nếu dùng systemd:
sudo systemctl restart freedom-wallet-bot

# Nếu dùng nohup:
pkill -f "python.*main.py"
nohup python main.py > logs/bot.log 2>&1 &

# Kiểm tra logs
tail -f logs/bot.log
```

### Cách 2: Dùng deployment script

Tạo script `update.sh` trên VPS:

```bash
cat > /root/FreedomWalletBot/update.sh << 'EOF'
#!/bin/bash

set -e

echo "🔄 Updating Freedom Wallet Bot..."

cd /root/FreedomWalletBot

# Backup database
echo "💾 Backing up database..."
mkdir -p data/backups
if [ -f data/bot.db ]; then
    cp data/bot.db data/backups/backup_$(date +%Y%m%d_%H%M%S).db
fi

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Update dependencies
echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run migration
echo "🔄 Running migration..."
python migrate_database.py

# Restart bot
echo "♻️ Restarting bot..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart freedom-wallet-bot
    echo "✅ Bot restarted via systemd"
else
    pkill -f "python.*main.py" || true
    sleep 2
    nohup python main.py > logs/bot.log 2>&1 &
    echo "✅ Bot restarted via nohup"
fi

# Verify
sleep 3
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ Bot is running!"
    echo "📋 View logs: tail -f logs/bot.log"
else
    echo "❌ Bot failed to start!"
    echo "Check logs: tail -50 logs/bot.log"
    exit 1
fi

echo "🎉 Update complete!"
EOF

# Cho phép execute
chmod +x /root/FreedomWalletBot/update.sh
```

**Sử dụng:**

```bash
# Chỉ cần chạy script này mỗi khi muốn update
/root/FreedomWalletBot/update.sh
```

---

## 🤖 AUTO-DEPLOYMENT (GitHub Webhook)

Setup để VPS tự động pull code khi bạn push lên GitHub.

### Step 1: Tạo webhook receiver trên VPS

```bash
# Cài Flask (web server nhẹ)
pip install flask

# Tạo webhook receiver
cat > /root/FreedomWalletBot/webhook_server.py << 'EOF'
from flask import Flask, request
import subprocess
import hmac
import hashlib
import os

app = Flask(__name__)

# Secret key (tạo random: openssl rand -hex 20)
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'your_secret_here')

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if signature:
        mac = hmac.new(
            WEBHOOK_SECRET.encode(),
            msg=request.data,
            digestmod=hashlib.sha256
        )
        expected_sig = 'sha256=' + mac.hexdigest()
        
        if not hmac.compare_digest(signature, expected_sig):
            return 'Invalid signature', 403
    
    # Run update script
    result = subprocess.run(
        ['/root/FreedomWalletBot/update.sh'],
        capture_output=True,
        text=True
    )
    
    return {
        'status': 'success' if result.returncode == 0 else 'failed',
        'output': result.stdout,
        'error': result.stderr
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
EOF
```

### Step 2: Start webhook server

```bash
# Tạo systemd service cho webhook
sudo nano /etc/systemd/system/github-webhook.service
```

Nội dung:

```ini
[Unit]
Description=GitHub Webhook Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/FreedomWalletBot
Environment="PATH=/root/FreedomWalletBot/.venv/bin"
Environment="WEBHOOK_SECRET=your_secret_here"
ExecStart=/root/FreedomWalletBot/.venv/bin/python webhook_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Kích hoạt:

```bash
sudo systemctl daemon-reload
sudo systemctl enable github-webhook
sudo systemctl start github-webhook

# Kiểm tra
sudo systemctl status github-webhook
```

### Step 3: Configure GitHub webhook

1. Vào repo: https://github.com/mettatuan/freedom-wallet-bot
2. Settings → Webhooks → Add webhook
3. Payload URL: `http://your_vps_ip:9000/webhook`
4. Content type: `application/json`
5. Secret: `your_secret_here` (same as WEBHOOK_SECRET)
6. Events: `Just the push event`
7. Active: ✅
8. Add webhook

### Step 4: Test

```bash
# Push code mới lên GitHub
git add .
git commit -m "Test auto-deploy"
git push

# VPS sẽ tự động:
# 1. Nhận webhook từ GitHub
# 2. Pull code mới
# 3. Update dependencies
# 4. Run migration
# 5. Restart bot

# Kiểm tra logs
sudo journalctl -u github-webhook -f
```

---

## 🔍 MONITORING

### Check bot status

```bash
# Process đang chạy?
pgrep -fa python

# Xem logs real-time
tail -f /root/FreedomWalletBot/logs/bot.log

# Systemd status (nếu dùng systemd)
sudo systemctl status freedom-wallet-bot

# Systemd logs
sudo journalctl -u freedom-wallet-bot -f
```

### Check Git status

```bash
cd /root/FreedomWalletBot

# Branch hiện tại
git branch

# Latest commit
git log -1 --oneline

# Check for updates
git fetch origin
git status
```

---

## 🛡️ ROLLBACK

Nếu deploy mới có lỗi, rollback về version cũ:

### Cách 1: Git reset

```bash
cd /root/FreedomWalletBot

# Xem lịch sử commits
git log --oneline -10

# Rollback về commit cũ
git reset --hard abc1234  # thay abc1234 bằng commit hash

# Restore database backup (nếu cần)
cp data/backups/backup_20240220_120000.db data/bot.db

# Restart bot
sudo systemctl restart freedom-wallet-bot
```

### Cách 2: Git revert

```bash
# Revert commit cuối (tạo commit mới)
git revert HEAD

# Push revert lên GitHub
git push origin main

# Restart bot
sudo systemctl restart freedom-wallet-bot
```

---

## 🔧 TROUBLESHOOTING

### ❌ Git pull failed: merge conflict

```bash
# Discard local changes (giữ remote version)
git reset --hard origin/main

# Hoặc stash local changes
git stash
git pull
git stash pop  # merge changes
```

### ❌ Permission denied

```bash
# Fix ownership
sudo chown -R root:root /root/FreedomWalletBot

# Fix permissions
chmod +x /root/FreedomWalletBot/update.sh
```

### ❌ Bot không restart

```bash
# Kill old process
pkill -9 -f "python.*main.py"

# Start manually
cd /root/FreedomWalletBot
source .venv/bin/activate
python main.py

# Xem logs để debug
tail -50 logs/bot.log
```

### ❌ Webhook không hoạt động

```bash
# Kiểm tra webhook server
sudo systemctl status github-webhook

# Kiểm tra port 9000 mở chưa
sudo netstat -tulpn | grep 9000

# Kiểm tra firewall
sudo ufw allow 9000/tcp

# Test webhook manually
curl -X POST http://your_vps_ip:9000/webhook
```

---

## 📊 Best Practices

1. ✅ **Always backup** database trước khi update
2. ✅ **Test locally** trước khi push lên GitHub
3. ✅ **Use systemd** để auto-restart bot
4. ✅ **Monitor logs** sau mỗi deployment
5. ✅ **Keep .env secure** (chmod 600, not in Git)
6. ✅ **Tag releases** on GitHub (git tag v1.0.0)
7. ✅ **Document changes** in CHANGELOG.md

---

## 🎯 TÓM TẮT COMMANDS

```bash
# SETUP LẦN ĐẦU
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
cd FreedomWalletBot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Tạo .env
python migrate_database.py
sudo systemctl start freedom-wallet-bot

# UPDATE CODE
cd /root/FreedomWalletBot
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python migrate_database.py
sudo systemctl restart freedom-wallet-bot

# MONITORING
sudo systemctl status freedom-wallet-bot
tail -f logs/bot.log
git log -1 --oneline

# ROLLBACK
git reset --hard abc1234
sudo systemctl restart freedom-wallet-bot
```

---

🎉 **Xong! Giờ bạn có thể deploy chỉ bằng `git push`!**
