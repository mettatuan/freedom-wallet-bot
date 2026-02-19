# 📜 SCRIPTS DIRECTORY

All production deployment and maintenance scripts for FreedomWalletBot.

---

## 🚀 DEPLOYMENT SCRIPTS

### `setup_vps.ps1` - Initial VPS Setup
**Purpose:** First-time setup on new VPS  
**Run once:** Yes  
**Requires Admin:** Yes  

**Usage:**
```powershell
.\scripts\setup_vps.ps1
```

**What it does:**
- Clones repository (or uses existing)
- Creates virtual environment
- Installs dependencies
- Creates required directories
- Sets up .env file
- Configures scheduled backups

**Time:** ~15 minutes

---

### `deploy.ps1` - Zero-Downtime Deployment
**Purpose:** Deploy updates from Git to production  
**Run once:** No (run after every `git push`)  
**Requires Admin:** No (but recommended)  

**Usage:**
```powershell
# Full deployment
.\scripts\deploy.ps1

# Skip backup
.\scripts\deploy.ps1 -SkipBackup

# Skip tests
.\scripts\deploy.ps1 -SkipTests
```

**What it does:**
1. Creates database backup
2. Pulls latest code from Git
3. Installs/updates dependencies
4. Runs database migrations
5. Runs tests
6. Restarts bot service
7. Performs health check

**Time:** ~2 minutes

---

### `setup_windows_service.ps1` - Windows Service Configuration
**Purpose:** Install bot as Windows Service (auto-start, auto-restart)  
**Run once:** Yes  
**Requires Admin:** YES (mandatory)  

**Usage:**
```powershell
# Install service
.\scripts\setup_windows_service.ps1

# Uninstall service
.\scripts\setup_windows_service.ps1 -Uninstall
```

**What it does:**
- Downloads NSSM (if needed)
- Installs bot as Windows Service
- Configures auto-start on boot
- Configures auto-restart on crash
- Sets up log rotation
- Starts the service

**Time:** ~5 minutes

---

## 💾 BACKUP & DATABASE SCRIPTS

### `backup_database.ps1` - PostgreSQL Backup
**Purpose:** Create database backup  
**Run once:** No (automated daily at 2 AM)  
**Requires Admin:** No  

**Usage:**
```powershell
# Default (7 days retention)
.\scripts\backup_database.ps1

# Custom retention (14 days)
.\scripts\backup_database.ps1 -RetentionDays 14

# Custom backup directory
.\scripts\backup_database.ps1 -BackupDir "E:\Backups"
```

**What it does:**
- Creates SQL dump of PostgreSQL database
- Compresses backup (if 7-Zip available)
- Deletes old backups (retention policy)
- Logs backup status

**Output:** `backups\database\freedomwallet_YYYYMMDD_HHMMSS.sql`

**Time:** ~1 minute

---

### `migrate_db.py` - Database Migration Tool
**Purpose:** Migrate data from SQLite to PostgreSQL  
**Run once:** Yes (during initial migration)  
**Requires Admin:** No  

**Usage:**
```powershell
# Export from SQLite
python scripts\migrate_db.py export --output=data\db_export.json

# Import to PostgreSQL
python scripts\migrate_db.py import --input=data\db_export.json

# Verify migration
python scripts\migrate_db.py verify
```

**What it does:**
- Exports all tables from SQLite to JSON
- Imports JSON data to PostgreSQL
- Verifies row counts match

**See:** [DATABASE_MIGRATION.md](../docs/DATABASE_MIGRATION.md)

---

## 🏥 MONITORING SCRIPTS

### `health_check.ps1` - System Health Monitor
**Purpose:** Check bot health and auto-recover  
**Run once:** No (automated every 5 minutes)  
**Requires Admin:** No  

**Usage:**
```powershell
# Basic health check
.\scripts\health_check.ps1

# With email alerts (configure SMTP first)
.\scripts\health_check.ps1 -SendAlert -AlertEmail "admin@example.com"
```

**What it checks:**
1. Windows Service status
2. Bot process running
3. Recent log activity
4. Database connection
5. Disk space
6. Network connectivity

**Auto-recovery:**
- Attempts to start service if stopped
- Logs all issues

**Exit codes:**
- `0` = All healthy
- `1` = Issues detected

**Time:** ~30 seconds

---

### `view_logs.ps1` - Log Viewer
**Purpose:** View and filter bot logs  
**Run once:** No (use anytime)  
**Requires Admin:** No  

**Usage:**
```powershell
# Last 50 lines
.\scripts\view_logs.ps1

# Follow logs (real-time)
.\scripts\view_logs.ps1 -Follow

# Show only errors
.\scripts\view_logs.ps1 -ErrorsOnly

# Show 100 lines
.\scripts\view_logs.ps1 -Lines 100

# Filter by keyword
.\scripts\view_logs.ps1 -Filter "telegram"

# Combine options
.\scripts\view_logs.ps1 -Follow -ErrorsOnly
```

**Time:** Instant

---

## 🛠️ UTILITY SCRIPTS

### `deploy.bat` - Batch Wrapper
**Purpose:** Simple wrapper for `deploy.ps1` (for convenience)  
**Usage:**
```cmd
deploy.bat
```

---

## 📋 SCHEDULED TASKS

**Automatically configured by `setup_vps.ps1`:**

| Task Name | Script | Schedule | Purpose |
|-----------|--------|----------|---------|
| FreedomWalletBot-DailyBackup | `backup_database.ps1` | Daily 2:00 AM | Database backup |
| FreedomWalletBot-HealthCheck | `health_check.ps1` | Every 5 minutes | Health monitoring |

**View scheduled tasks:**
```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "*FreedomWallet*" }
```

**Manually trigger:**
```powershell
Start-ScheduledTask -TaskName "FreedomWalletBot-DailyBackup"
```

---

## 🔧 SERVICE MANAGEMENT

**Windows Service Name:** `FreedomWalletBot`

### Common Commands

```powershell
# Check status
Get-Service FreedomWalletBot

# Start service
Start-Service FreedomWalletBot

# Stop service
Stop-Service FreedomWalletBot

# Restart service
Restart-Service FreedomWalletBot

# View service properties
Get-Service FreedomWalletBot | Select-Object *
```

### NSSM Commands

```powershell
# Edit service configuration
& "D:\FreedomWalletBot\scripts\nssm.exe" edit FreedomWalletBot

# View service parameters
& "D:\FreedomWalletBot\scripts\nssm.exe" get FreedomWalletBot *

# Remove service
& "D:\FreedomWalletBot\scripts\nssm.exe" remove FreedomWalletBot confirm
```

---

## 📊 TYPICAL WORKFLOW

### Initial Setup (Once)
```powershell
# 1. Setup VPS
.\scripts\setup_vps.ps1

# 2. Edit .env file
notepad .env

# 3. Test bot manually
& .venv\Scripts\Activate.ps1
python main.py
# (Ctrl+C to stop)

# 4. Setup as service
.\scripts\setup_windows_service.ps1
```

### Daily Development
```powershell
# On Local: Make changes, commit, push
git add .
git commit -m "Your changes"
git push origin main

# On VPS: Deploy
.\scripts\deploy.ps1
```

### Monitoring
```powershell
# Check health
.\scripts\health_check.ps1

# View logs
.\scripts\view_logs.ps1 -Follow

# Check backups
Get-ChildItem backups\database
```

---

## 🚨 EMERGENCY COMMANDS

### Bot Down - Quick Recovery
```powershell
# 1. Check service
Get-Service FreedomWalletBot

# 2. Restart
Restart-Service FreedomWalletBot

# 3. Check logs
.\scripts\view_logs.ps1 -ErrorsOnly -Lines 50

# 4. Health check
.\scripts\health_check.ps1
```

### Database Corruption
```powershell
# 1. Stop bot
Stop-Service FreedomWalletBot

# 2. Restore from latest backup
$LatestBackup = Get-ChildItem backups\database -Filter "*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
psql -U freedomwallet -d freedomwalletdb -f $LatestBackup.FullName

# 3. Start bot
Start-Service FreedomWalletBot
```

### Complete Reinstall
```powershell
# 1. Uninstall service
.\scripts\setup_windows_service.ps1 -Uninstall

# 2. Backup .env
Copy-Item .env .env.backup

# 3. Fresh clone
cd D:\
Remove-Item FreedomWalletBot -Recurse -Force
git clone https://github.com/mettatuan/FreedomWalletBot.git

# 4. Restore .env
Copy-Item .env.backup FreedomWalletBot\.env

# 5. Setup again
cd FreedomWalletBot
.\scripts\setup_vps.ps1
.\scripts\setup_windows_service.ps1
```

---

## 📚 DOCUMENTATION

- [DEPLOYMENT.md](../docs/DEPLOYMENT.md) - Full deployment guide
- [DATABASE_MIGRATION.md](../docs/DATABASE_MIGRATION.md) - Database migration instructions
- [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) - Common issues and solutions

---

## ⚠️ IMPORTANT NOTES

### Execution Policy
If scripts won't run, set execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Administrator Rights
Some scripts require Administrator:
- `setup_windows_service.ps1` - YES (mandatory)
- `setup_vps.ps1` - YES (recommended)
- `deploy.ps1` - NO (but recommended)
- Others - NO

### Virtual Environment
Always ensure virtual environment is activated when running Python scripts:
```powershell
& .venv\Scripts\Activate.ps1
```

### Logs
All scripts log to:
- Service logs: `data\logs\service.log`
- Bot logs: `data\logs\bot.log`
- Health check logs: `data\logs\health_check.log`
- Migration logs: `data\logs\migration_*.log`

---

**Questions? Check [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)**
