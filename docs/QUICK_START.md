# ⚡ QUICK START GUIDE

## 🎯 TL;DR - Production Deployment in 30 Minutes

**Goal:** Deploy FreedomWalletBot on Windows Server 2016 VPS với zero-downtime updates.

---

## 📋 PREREQUISITES (5 minutes)

### On VPS:
- ✅ Windows Server 2016
- ✅ Administrator access
- ✅ Internet connection
- ✅ Git installed ([Download](https://git-scm.com/download/win))
- ✅ Python 3.10+ installed ([Download](https://www.python.org/downloads/))
- ✅ At least 20GB free space

**Check versions:**
```powershell
git --version
python --version
```

---

## 🚀 STEP 1: Clone Repository (2 minutes)

**On VPS, PowerShell as Administrator:**

```powershell
# Clone repository
cd D:\
git clone https://github.com/mettatuan/FreedomWalletBot.git
cd FreedomWalletBot
```

---

## 🚀 STEP 2: Run VPS Setup (10 minutes)

```powershell
# Run automated setup
.\scripts\setup_vps.ps1
```

**What it does:**
- Creates virtual environment
- Installs dependencies
- Creates directories
- Sets up .env file (opens in Notepad for editing)

**⏸️ STOP HERE:** Edit `.env` file with your credentials!

---

## 🔑 STEP 3: Configure Credentials (5 minutes)

**Edit `D:\FreedomWalletBot\.env`:**

```env
# REQUIRED - Get from @BotFather
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# REQUIRED - Your Telegram ID
ADMIN_USER_ID=YOUR_TELEGRAM_USER_ID

# REQUIRED - Database (use SQLite for quick start)
DATABASE_URL=sqlite:///data/bot.db

# Or PostgreSQL (recommended for production)
# DATABASE_URL=postgresql://freedomwallet:PASSWORD@localhost:5432/freedomwalletdb
```

**Minimal quick start:** Only the first 3 variables are required!

---

## 🚀 STEP 4: Test Bot Manually (3 minutes)

```powershell
# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Run bot
python main.py
```

**✅ Test in Telegram:** Send `/start` to your bot

**If it works:** Press Ctrl+C and proceed to Step 5

**If errors:** Check logs and fix .env configuration

---

## 🚀 STEP 5: Setup Windows Service (5 minutes)

```powershell
# Install as Windows Service (run as Administrator)
.\scripts\setup_windows_service.ps1
```

**✅ Verify:**
```powershell
Get-Service FreedomWalletBot
# Should show: Status=Running, StartType=Automatic
```

**🎉 DONE! Your bot is now running 24/7!**

---

## 📦 OPTIONAL: Install PostgreSQL (10 minutes)

**For production, PostgreSQL is recommended over SQLite.**

### Install PostgreSQL:

1. Download: [PostgreSQL 15+](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. Install with defaults (Port 5432, remember password!)
3. Create database:

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE freedomwalletdb;
CREATE USER freedomwallet WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE freedomwalletdb TO freedomwallet;
\q
```

4. Update `.env`:
```env
DATABASE_URL=postgresql://freedomwallet:your-secure-password@localhost:5432/freedomwalletdb
```

5. Restart bot:
```powershell
Restart-Service FreedomWalletBot
```

**📚 Detailed guide:** [DATABASE_MIGRATION.md](docs/DATABASE_MIGRATION.md)

---

## 🔄 DAILY WORKFLOW

### On Local Machine:

```powershell
# 1. Make changes to code
# 2. Test locally
# 3. Commit and push

git add .
git commit -m "Your changes"
git push origin main
```

### On VPS:

```powershell
# Just run this!
D:\FreedomWalletBot\deploy.bat
```

**⏱️ Takes ~2 minutes**

**What happens:**
- ✅ Pulls latest code
- ✅ Updates dependencies
- ✅ Restarts bot
- ✅ Zero downtime!

---

## 🛠️ COMMON TASKS

### View Logs
```powershell
# Real-time logs
.\scripts\view_logs.ps1 -Follow

# Show errors only
.\scripts\view_logs.ps1 -ErrorsOnly
```

### Service Management
```powershell
# Check status
Get-Service FreedomWalletBot

# Restart
Restart-Service FreedomWalletBot

# Stop
Stop-Service FreedomWalletBot

# Start
Start-Service FreedomWalletBot
```

### Health Check
```powershell
.\scripts\health_check.ps1
```

### Manual Backup
```powershell
.\scripts\backup_database.ps1
```

---

## 🚨 TROUBLESHOOTING

### Bot not responding?

```powershell
# 1. Check service
Get-Service FreedomWalletBot

# 2. Check logs
.\scripts\view_logs.ps1 -ErrorsOnly

# 3. Restart
Restart-Service FreedomWalletBot

# 4. Health check
.\scripts\health_check.ps1
```

### Service won't start?

```powershell
# Test manually to see error
cd D:\FreedomWalletBot
& .venv\Scripts\Activate.ps1
python main.py
```

**Common issues:**
- ❌ `.env` file missing → Copy from `.env.production`
- ❌ Wrong bot token → Check @BotFather
- ❌ Database error → Check DATABASE_URL in `.env`

**📚 Full troubleshooting:** [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📚 DOCUMENTATION

**Complete guides:**
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Full deployment guide
- [DATABASE_MIGRATION.md](docs/DATABASE_MIGRATION.md) - SQLite → PostgreSQL
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [SECURITY.md](docs/SECURITY.md) - Security best practices
- [scripts/README.md](scripts/README.md) - All scripts documentation

---

## ✅ SUCCESS CHECKLIST

After setup, verify:

- [ ] Bot responds to `/start` in Telegram
- [ ] Service status is "Running": `Get-Service FreedomWalletBot`
- [ ] Logs are being written: `.\scripts\view_logs.ps1`
- [ ] Daily backup is scheduled: `Get-ScheduledTask | Where { $_.TaskName -like "*Backup*" }`
- [ ] Health check is scheduled: `Get-ScheduledTask | Where { $_.TaskName -like "*HealthCheck*" }`
- [ ] `.env` file has correct permissions (Admin only)
- [ ] `.gitignore` is protecting secrets

---

## 🎯 NEXT STEPS

### Production Hardening:
1. ✅ Move to PostgreSQL (if using SQLite)
2. ✅ Configure HTTPS webhook (optional)
3. ✅ Setup monitoring alerts
4. ✅ Configure offsite backups
5. ✅ Review [SECURITY.md](docs/SECURITY.md)

### Development:
1. ✅ Setup local development environment
2. ✅ Clone repository locally
3. ✅ Create `.env.local` with development bot
4. ✅ Test changes before pushing

---

## 💡 PRO TIPS

**Fastest deployment workflow:**
```powershell
# On Local
git add . ; git commit -m "Update" ; git push

# On VPS (one command!)
D:\FreedomWalletBot\deploy.bat
```

**Monitor bot 24/7:**
```powershell
# Follow logs in real-time
.\scripts\view_logs.ps1 -Follow
```

**Auto-restart on crash:**
Already configured! NSSM service manager automatically restarts bot if it crashes.

**Zero-downtime updates:**
`deploy.ps1` handles graceful restart - users won't notice!

---

## 📞 HELP & SUPPORT

**Got stuck?**
1. Check logs: `.\scripts\view_logs.ps1 -ErrorsOnly`
2. Run health check: `.\scripts\health_check.ps1`
3. Read [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
4. Check [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed guide

**Everything working?**
- 🎉 Your bot is production-ready!
- 🔄 Use `deploy.bat` for updates
- 📊 Check health weekly
- 💾 Backups run daily at 2 AM

---

**⏱️ Total setup time: ~30 minutes**  
**💪 Production-ready: YES**  
**🚀 Zero-downtime updates: YES**  
**🔒 Secure: YES**  
**📦 Automated backups: YES**

**🎉 Enjoy your production-ready Telegram bot!**
