# 🚀 PRODUCTION DEPLOYMENT GUIDE

## 📋 KIẾN TRÚC ĐỀ XUẤT

```
┌─────────────────────────────────────────────────────────┐
│                   LOCAL DEVELOPMENT                     │
│                                                         │
│  • SQLite database                                      │
│  • Development bot token                               │
│  • .env.local configuration                            │
│                                                         │
│         git push origin main                           │
│                ↓                                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   GITHUB REPOSITORY                     │
│                                                         │
│  • Private repository                                   │
│  • .env files ignored                                  │
│  • Secrets protected                                   │
│                                                         │
│         git pull (on VPS)                              │
│                ↓                                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│              WINDOWS SERVER 2016 VPS                    │
│                                                         │
│  ┌─────────────────────────────────────────┐           │
│  │  PostgreSQL Database                    │           │
│  │  • freedomwalletdb                      │           │
│  │  • Daily backups (2 AM)                 │           │
│  └─────────────────────────────────────────┘           │
│                        ↓                                │
│  ┌─────────────────────────────────────────┐           │
│  │  FreedomWalletBot Service (NSSM)        │           │
│  │  • Auto-start on boot                   │           │
│  │  • Auto-restart on crash                │           │
│  │  • Log rotation                         │           │
│  └─────────────────────────────────────────┘           │
│                        ↓                                │
│  ┌─────────────────────────────────────────┐           │
│  │  Monitoring & Alerts                    │           │
│  │  • Health check (every 5 mins)          │           │
│  │  • Error tracking                       │           │
│  │  • Performance metrics                  │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 PHASE 1: INITIAL SETUP (One-time)

### 📦 Prerequisites

#### On Local Machine:
- ✅ Git installed
- ✅ Python 3.10+
- ✅ Code editor (VS Code recommended)

#### On VPS (Windows Server 2016):
- ✅ Administrator access
- ✅ Internet connection
- ✅ At least 20GB free disk space
- ✅ Git for Windows
- ✅ Python 3.10+
- ✅ PostgreSQL 15+ (will install)

---

### STEP 1: Setup GitHub Repository (Local)

```powershell
# Navigate to project directory
cd D:\Projects\FreedomWalletBot

# Initialize Git (if not already done)
git init

# Create GitHub repository (private)
# Go to: https://github.com/new
# Name: FreedomWalletBot
# Private: YES
# Don't initialize with README

# Add remote
git remote add origin https://github.com/mettatuan/FreedomWalletBot.git

# Add all files (except those in .gitignore)
git add .

# First commit
git commit -m "Initial commit: Production-ready setup"

# Push to GitHub
git push -u origin main
```

**✅ Verification:**
```powershell
git remote -v
# Should show: origin https://github.com/mettatuan/FreedomWalletBot.git
```

---

### STEP 2: Setup VPS Environment

**On VPS, run PowerShell as Administrator:**

```powershell
# Download Git for Windows (if not installed)
# https://git-scm.com/download/win

# Download Python 3.10+ (if not installed)
# https://www.python.org/downloads/

# Clone repository
cd D:\
git clone https://github.com/mettatuan/FreedomWalletBot.git

# Navigate to project
cd FreedomWalletBot

# Run VPS setup script
.\scripts\setup_vps.ps1
```

This script will:
- ✅ Check prerequisites
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Create required directories
- ✅ Setup .env file from template
- ✅ Configure scheduled backups

**⏱️ Time: ~15 minutes**

---

### STEP 3: Install PostgreSQL on VPS

```powershell
# Download PostgreSQL installer
# https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
# Version: 15.x or 16.x for Windows x86-64

# Install with these settings:
# - Port: 5432 (default)
# - Password: [CHOOSE STRONG PASSWORD]
# - Locale: English, United States
# - Components: PostgreSQL Server, pgAdmin 4, Command Line Tools

# After installation, create database
psql -U postgres

# In PostgreSQL prompt:
CREATE DATABASE freedomwalletdb;
CREATE USER freedomwallet WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE freedomwalletdb TO freedomwallet;
\q
```

**⏱️ Time: ~10 minutes**

---

### STEP 4: Configure Environment Variables (VPS)

Edit `D:\FreedomWalletBot\.env`:

```env
# REQUIRED - Get from @BotFather
TELEGRAM_BOT_TOKEN=7123456789:AAHdqTcvbXUXXXXXXXXXXXXXXXXXXXX

# REQUIRED - Your Telegram user ID
ADMIN_USER_ID=123456789

# REQUIRED - PostgreSQL connection
DATABASE_URL=postgresql://freedomwallet:your-secure-password@localhost:5432/freedomwalletdb

# REQUIRED - Google service account
GOOGLE_SHEETS_CREDENTIALS=D:/FreedomWalletBot/google_service_account.json
TEMPLATE_SHEET_ID=your-sheet-id-here

# Optional but recommended
OPENAI_API_KEY=sk-your-api-key-here
```

**⏱️ Time: ~5 minutes**

---

### STEP 5: Migrate Database (if you have existing data)

**On local machine, export data:**

```powershell
# Activate virtual environment
& .venv\Scripts\Activate.ps1

# Export SQLite data
python scripts\migrate_db.py export --output=data\db_export.json

# Transfer db_export.json to VPS (via FTP, RDP, or cloud)
```

**On VPS, import data:**

```powershell
cd D:\FreedomWalletBot
& .venv\Scripts\Activate.ps1

# Import data to PostgreSQL
python scripts\migrate_db.py import --input=data\db_export.json

# Verify migration
python scripts\migrate_db.py verify
```

**⏱️ Time: ~10 minutes**

See: [DATABASE_MIGRATION.md](DATABASE_MIGRATION.md) for details.

---

### STEP 6: Test Bot Manually (VPS)

```powershell
cd D:\FreedomWalletBot
& .venv\Scripts\Activate.ps1

# Run bot manually
python main.py

# In Telegram, send /start to your bot
# Verify it responds correctly

# Press Ctrl+C to stop
```

**✅ If bot works → Proceed to Step 7**  
**❌ If errors → Check logs in `data\logs\bot.log`**

**⏱️ Time: ~5 minutes**

---

### STEP 7: Setup Windows Service (VPS)

```powershell
# Run as Administrator
.\scripts\setup_windows_service.ps1
```

This will:
- ✅ Download NSSM (service wrapper)
- ✅ Install bot as Windows Service
- ✅ Configure auto-start on boot
- ✅ Configure auto-restart on crash
- ✅ Setup log rotation
- ✅ Start the service

**⏱️ Time: ~5 minutes**

**Verify service:**

```powershell
# Check service status
Get-Service FreedomWalletBot

# Should show: Status: Running, StartType: Automatic
```

---

### STEP 8: Setup Monitoring & Backups (VPS)

#### Health Check (Every 5 minutes)

```powershell
# Create scheduled task
$TaskName = "FreedomWalletBot-HealthCheck"
$TaskAction = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"D:\FreedomWalletBot\scripts\health_check.ps1`""
$TaskTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
$TaskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $TaskAction -Trigger $TaskTrigger -Settings $TaskSettings -RunLevel Highest
```

#### Daily Backup (2:00 AM)

Already configured by `setup_vps.ps1`, but you can verify:

```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "*Backup*" }
```

**⏱️ Time: ~5 minutes**

---

## 🎯 PHASE 2: DAILY WORKFLOW

### Local Development → VPS Deployment

#### On Local Machine:

```powershell
# 1. Make your changes
# 2. Test locally

# 3. Commit and push
git add .
git commit -m "Your commit message"
git push origin main
```

#### On VPS:

```powershell
# Just run deploy script!
D:\FreedomWalletBot\deploy.bat
```

**Or use PowerShell:**

```powershell
cd D:\FreedomWalletBot
.\scripts\deploy.ps1
```

**What happens automatically:**
1. ✅ Database backup
2. ✅ Pull latest code from GitHub
3. ✅ Install/update dependencies
4. ✅ Run database migrations
5. ✅ Run tests
6. ✅ Restart bot service (zero downtime)
7. ✅ Health check

**⏱️ Time: ~2 minutes** 🎉

---

## 🔧 COMMON OPERATIONS

### View Logs

```powershell
# Last 50 lines
.\scripts\view_logs.ps1

# Follow logs (real-time)
.\scripts\view_logs.ps1 -Follow

# Show only errors
.\scripts\view_logs.ps1 -ErrorsOnly

# Filter by keyword
.\scripts\view_logs.ps1 -Filter "telegram"
```

### Service Management

```powershell
# Check status
Get-Service FreedomWalletBot

# Start service
Start-Service FreedomWalletBot

# Stop service
Stop-Service FreedomWalletBot

# Restart service
Restart-Service FreedomWalletBot
```

### Manual Backup

```powershell
.\scripts\backup_database.ps1
```

### Health Check

```powershell
.\scripts\health_check.ps1
```

---

## 🚨 TROUBLESHOOTING

### Bot Not Starting

```powershell
# Check service logs
.\scripts\view_logs.ps1 -ErrorsOnly

# Check service status
Get-Service FreedomWalletBot

# Try manual start
cd D:\FreedomWalletBot
& .venv\Scripts\Activate.ps1
python main.py
```

### Database Connection Error

```powershell
# Test PostgreSQL
psql -U freedomwallet -d freedomwalletdb

# Check PostgreSQL service
Get-Service postgresql*

# Restart PostgreSQL
Restart-Service postgresql-x64-15  # Adjust version
```

### Git Pull Conflicts

```powershell
# Stash local changes
git stash

# Pull latest
git pull origin main

# Apply stashed changes (optional)
git stash pop
```

### Service Won't Start

```powershell
# View NSSM logs
Get-Content D:\FreedomWalletBot\data\logs\service.log -Tail 50

# Reconfigure service
.\scripts\setup_windows_service.ps1

# Check Python path
where.exe python
# Should show: D:\FreedomWalletBot\.venv\Scripts\python.exe
```

---

## 📊 MONITORING & ALERTS

### Daily Tasks (Automated)

- ✅ **02:00 AM** - Database backup
- ✅ **Every 5 min** - Health check
- ✅ **On crash** - Auto-restart

### Manual Checks (Weekly)

```powershell
# Check service uptime
Get-Service FreedomWalletBot | Select-Object Status, StartType

# Check disk space
Get-PSDrive D

# Check backup folder
Get-ChildItem D:\FreedomWalletBot\backups\database | Measure-Object

# Check log size
Get-ChildItem D:\FreedomWalletBot\data\logs | Measure-Object -Property Length -Sum
```

### Optional: Setup Email Alerts

Edit `scripts\health_check.ps1` and configure SMTP settings for email alerts on failures.

---

## 🔒 SECURITY CHECKLIST

- [x] `.env` file not committed to Git
- [x] Strong PostgreSQL password
- [x] Windows Firewall enabled
- [x] Bot token kept secret
- [x] Google service account JSON protected
- [x] Administrator access restricted
- [x] Regular backups enabled
- [x] Auto-updates disabled (manual control)

---

## 📈 PERFORMANCE OPTIMIZATION

### PostgreSQL Tuning (Optional)

Edit `C:\Program Files\PostgreSQL\15\data\postgresql.conf`:

```conf
# Optimize for small-medium bot
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
max_connections = 20
```

Restart PostgreSQL after changes.

---

## 🎓 ADVANCED: CI/CD (Optional)

For automated deployment on git push, see: [CI_CD_GUIDE.md](CI_CD_GUIDE.md) (future enhancement)

---

## 📞 SUPPORT

**Error in deployment?**
1. Check logs: `.\scripts\view_logs.ps1 -ErrorsOnly`
2. Verify .env configuration
3. Test database connection
4. Check service status

**Still stuck?**
- Review this guide carefully
- Check individual script files for detailed comments
- Test each component manually

---

## ✅ DEPLOYMENT CHECKLIST

### Initial Setup (Once)
- [ ] GitHub repository created (private)
- [ ] VPS accessible via RDP
- [ ] Git installed on VPS
- [ ] Python 3.10+ installed on VPS
- [ ] PostgreSQL installed on VPS
- [ ] `setup_vps.ps1` completed successfully
- [ ] `.env` file configured correctly
- [ ] Database migrated (if applicable)
- [ ] Bot tested manually
- [ ] Windows Service created
- [ ] Service starts on boot
- [ ] Scheduled backups configured
- [ ] Health check scheduled

### Before Each Deployment
- [ ] Code tested locally
- [ ] Committed to Git
- [ ] Pushed to GitHub
- [ ] Ready to deploy

### Deploy Process
- [ ] Run `deploy.bat` on VPS
- [ ] Verify no errors
- [ ] Test bot in Telegram
- [ ] Check service status
- [ ] Monitor logs for 5 minutes

### Weekly Maintenance
- [ ] Check health check logs
- [ ] Verify backups are running
- [ ] Check disk space
- [ ] Review error logs
- [ ] Update dependencies (if needed)

---

**🎉 Congratulations! Your bot is now production-ready!**
