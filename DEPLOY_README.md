# 🚀 Quick Deploy to VPS

Đã hoàn thành Phase 2-3, giờ deploy lên VPS!

## ⚡ TL;DR - Deploy ngay

```bash
# 1. Tạo .env trên VPS với bot token
# 2. Chạy deploy script

# Windows PowerShell:
.\deploy_to_vps.ps1 -VPS_HOST "your_vps_ip" -VPS_USER "root" -VPS_PATH "/root/FreedomWalletBot"

# Linux/Mac:
chmod +x deploy_to_vps.sh
./deploy_to_vps.sh
```

## 📚 Hướng dẫn chi tiết

Xem file: **[VPS_DEPLOYMENT_GUIDE.md](VPS_DEPLOYMENT_GUIDE.md)**

## ✅ Phase 2-3 đã hoàn thành

**Phase 2 - Financial Assistant Core:**
- ✅ Transaction Engine (NLP parser, category detection)
- ✅ Awareness Engine (balance, streak, anomalies)
- ✅ Behavioral Engine (7 spending personas)
- ✅ Reflection Engine (weekly insights, 4 tones)
- ✅ Main Keyboard (4x2 layout, 8 buttons)
- ✅ Transaction handlers wired up

**Phase 3 - Testing & Refinement:**
- ✅ Database migration (backup system)
- ✅ Test suite (6/6 tests PASSED)
- ✅ Google Sheets auto-sync
- ✅ Error handling & logging
- ✅ Production ready!

## 📦 Files created (19 files total)

**New modules:**
- `bot/core/categories.py` - Category detection (9 expense + 5 income)
- `bot/core/nlp.py` - Vietnamese NLP parser (35k, 2.5tr formats)
- `bot/core/keyboard.py` - Main keyboard (8 buttons)
- `bot/core/awareness.py` - Real-time metrics
- `bot/core/behavioral.py` - Spending patterns & personas
- `bot/core/reflection.py` - Weekly insights generation
- `bot/core/sheets_sync.py` - Auto-sync to Google Sheets
- `bot/handlers/transaction.py` - Transaction handlers
- `bot/utils/database.py` - Transaction model added
- `main.py` - Handler registration
- `bot/handlers/start.py` - Main keyboard integration

**Deployment tools:**
- `deploy_to_vps.ps1` - PowerShell deploy script (Windows)
- `deploy_to_vps.sh` - Bash deploy script (Linux/Mac)
- `deploy_config.txt` - Configuration guide
- `VPS_DEPLOYMENT_GUIDE.md` - Complete deployment docs

**Testing/Migration:**
- `test_phase3.py` - Test suite (6 tests)
- `migrate_database.py` - Database migration with backup

**Documentation:**
- `PHASE2_IMPLEMENTATION_PROGRESS.md`
- `PHASE3_IMPLEMENTATION_SUMMARY.md`

## 🎯 What the script does

1. ✅ Run tests locally (6/6 must pass)
2. 🔌 Test SSH connection to VPS
3. 💾 Backup VPS database
4. 🛑 Stop bot
5. 📤 Upload 19 files (rsync)
6. 📦 Install dependencies
7. 🔄 Run database migration
8. ▶️ Start bot
9. ✅ Verify deployment

## 🔍 Verify deployment

```bash
# Check bot running
ssh your_user@your_vps "pgrep -fa python"

# View logs
ssh your_user@your_vps "tail -f /root/FreedomWalletBot/logs/bot.log"

# Test on Telegram
# 1. /start → See 8-button keyboard
# 2. Click "📊 Tổng quan" → See balance, streak
# 3. Send "35k ăn sáng" → Transaction saved
# 4. Click "📊 Tổng quan" → Balance updated!
```

## 🛟 Rollback if needed

If deployment fails, bot automatically uses backup:

```bash
ssh your_user@your_vps

cd /root/FreedomWalletBot

# List backups
ls -lh data/backups/

# Restore backup
cp data/backups/vps_backup_20240101_120000.db data/bot.db

# Restart bot
pkill -f python
nohup python main.py > logs/bot.log 2>&1 &
```

## 🎉 That's it!

Bot giờ chạy 24/7 trên VPS với full Phase 2-3 features!

**Test checklist:**
- [ ] `/start` shows 8-button keyboard
- [ ] `35k ăn sáng` logs transaction
- [ ] `📊 Tổng quan` shows balance/streak
- [ ] `💡 Insight` generates weekly reflection
- [ ] `📈 Báo cáo tuần` shows spending patterns
- [ ] Google Sheets auto-syncs (if configured)

---

**Need help?** See [VPS_DEPLOYMENT_GUIDE.md](VPS_DEPLOYMENT_GUIDE.md) for detailed troubleshooting.
