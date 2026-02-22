# ✅ ĐÃ PUSH CODE LÊN GITHUB!

**Repository:** https://github.com/mettatuan/freedom-wallet-bot  
**Branch:** `cleanup/hard-refactor`  
**Commit:** `3478096` - Phase 1-3 complete: Retention-first redesign

---

## 📦 Thay đổi đã push

### Files mới (26 files):
- ✅ **README.md** - Documentation đầy đủ
- ✅ **bot/core/** - 7 engine files (categories, NLP, keyboard, awareness, behavioral, reflection, sheets_sync)
- ✅ **bot/handlers/transaction.py** - Transaction handlers
- ✅ **migrate_database.py** - Database migration
- ✅ **test_phase3.py** - Test suite (6 tests)
- ✅ **VPS_DEPLOYMENT_GUIDE.md** - Hướng dẫn deploy VPS
- ✅ **docs/git-deployment.md** - Git-based deployment
- ✅ **update_from_github.sh** - VPS update script
- ✅ **push_to_github.ps1** - Push script (Windows)
- ✅ Phase 1-3 documentation files

### Files modified (7 files):
- ✅ main.py - Handler registration
- ✅ bot/handlers/start.py - Main keyboard
- ✅ bot/utils/database.py - Transaction model
- ✅ bot/handlers/referral.py - Remove unlock refs
- ✅ bot/handlers/status.py - Remove unlock refs
- ✅ bot/handlers/webapp_setup.py - Clean up

### Files deleted (11 files):
- ❌ Unlock system handlers (unlock_flow_v3, unlock_calm_flow, free_flow)
- ❌ Unlock trigger job
- ❌ Old documentation (ARCHITECTURE_RULES, CODE_AUDIT_REPORT, etc.)

**Total:** 43 files changed, **+7,409 insertions, -3,559 deletions**

---

## 🚀 DEPLOY LÊN VPS (3 cách)

### CÁCH 1: Script tự động (Khuyến nghị)

**Bước 1:** Upload script lên VPS (chỉ cần làm 1 lần)

```bash
# Từ máy local, upload script
scp update_from_github.sh root@your_vps_ip:/root/FreedomWalletBot/

# SSH vào VPS
ssh root@your_vps_ip

# Cho phép execute
chmod +x /root/FreedomWalletBot/update_from_github.sh
```

**Bước 2:** Chạy script update (mỗi lần deploy)

```bash
# Trên VPS, chỉ cần chạy:
/root/FreedomWalletBot/update_from_github.sh

# Script sẽ tự động:
# 1. Backup database
# 2. Pull code mới từ GitHub
# 3. Cài dependencies
# 4. Run migration
# 5. Restart bot
# 6. Verify deployment
```

**Xong!** Bot đã chạy version mới.

---

### CÁCH 2: Manual (từng bước)

```bash
# SSH vào VPS
ssh root@your_vps_ip

# 1. Backup database
cd /root/FreedomWalletBot
mkdir -p data/backups
cp data/bot.db data/backups/backup_$(date +%Y%m%d_%H%M%S).db

# 2. Pull code mới
git pull origin cleanup/hard-refactor

# 3. Activate venv & update dependencies
source .venv/bin/activate
pip install -r requirements.txt

# 4. Run migration
python migrate_database.py

# 5. Restart bot
# Nếu dùng systemd:
sudo systemctl restart freedom-wallet-bot

# Nếu dùng nohup:
pkill -f "python.*main.py"
nohup python main.py > logs/bot.log 2>&1 &

# 6. Xem logs
tail -f logs/bot.log
```

---

### CÁCH 3: Auto-deploy với GitHub Webhook

Setup 1 lần, sau đó mỗi lần `git push` sẽ tự động deploy!

**Xem hướng dẫn chi tiết:** [docs/git-deployment.md](docs/git-deployment.md#-auto-deployment-github-webhook)

---

## ✅ Kiểm tra sau khi deploy

### 1. Bot có chạy không?

```bash
ssh root@your_vps_ip "pgrep -fa python"

# Output mong đợi:
# 12345 python main.py
```

### 2. Xem logs

```bash
ssh root@your_vps_ip "tail -50 /root/FreedomWalletBot/logs/bot.log"

# Tìm:
# ✅ "Application started"
# ✅ "Bot polling started"
# ❌ KHÔNG có "ERROR" hoặc "Exception"
```

### 3. Test trên Telegram

1. Mở bot trên Telegram
2. Gửi `/start` → Thấy **keyboard 8 nút** ✅
3. Gửi `35k ăn sáng` → Lưu giao dịch ✅
4. Click **📊 Tổng quan** → Thấy số dư ✅
5. Click **💡 Insight** → Nhận insights ✅

---

## 🐛 Nếu có lỗi

### Bot không start

```bash
# Xem logs chi tiết
ssh root@your_vps_ip "tail -100 /root/FreedomWalletBot/logs/bot.log"

# Kiểm tra .env file
ssh root@your_vps_ip "cat /root/FreedomWalletBot/.env"

# Nếu thiếu .env, tạo:
ssh root@your_vps_ip "cat > /root/FreedomWalletBot/.env << 'EOF'
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
EOF"
```

### Git pull failed

```bash
# Reset về remote version
ssh root@your_vps_ip "cd /root/FreedomWalletBot && git reset --hard origin/cleanup/hard-refactor"
```

### Migration failed

```bash
# Xem lỗi
ssh root@your_vps_ip "cd /root/FreedomWalletBot && source .venv/bin/activate && python migrate_database.py"
```

---

## 📋 Commands cheat sheet

```bash
# UPDATE BOT (khuyến nghị)
ssh root@your_vps_ip "/root/FreedomWalletBot/update_from_github.sh"

# XEM LOGS
ssh root@your_vps_ip "tail -f /root/FreedomWalletBot/logs/bot.log"

# RESTART BOT
ssh root@your_vps_ip "sudo systemctl restart freedom-wallet-bot"

# CHECK STATUS
ssh root@your_vps_ip "pgrep -fa python"

# GIT STATUS
ssh root@your_vps_ip "cd /root/FreedomWalletBot && git log -1 --oneline"

# DATABASE BACKUPS
ssh root@your_vps_ip "ls -lh /root/FreedomWalletBot/data/backups/"

# ROLLBACK
ssh root@your_vps_ip "cd /root/FreedomWalletBot && git reset --hard HEAD~1 && sudo systemctl restart freedom-wallet-bot"
```

---

## 🎯 TÓM TẮT

**Code đã ở trên GitHub:** ✅  
**Để VPS chạy version mới:**

```bash
# Cách nhanh nhất:
ssh root@your_vps_ip "/root/FreedomWalletBot/update_from_github.sh"
```

**Hoặc từng bước:**

```bash
ssh root@your_vps_ip
cd /root/FreedomWalletBot
git pull origin cleanup/hard-refactor
source .venv/bin/activate
pip install -r requirements.txt
python migrate_database.py
sudo systemctl restart freedom-wallet-bot
```

---

## 📚 Tài liệu đầy đủ

- **Git deployment guide:** [docs/git-deployment.md](docs/git-deployment.md)
- **VPS deployment guide:** [VPS_DEPLOYMENT_GUIDE.md](VPS_DEPLOYMENT_GUIDE.md)
- **Quick start:** [DEPLOY_README.md](DEPLOY_README.md)

---

🎉 **Xong! Giờ bạn có thể deploy chỉ bằng `git push` + chạy script trên VPS!**
