# Deployment Scripts

Complete automation tools for deploying Freedom Wallet Bot to Windows Server 2016.

## 📋 Scripts Overview

### 1. Initial Setup
**`setup_vps.ps1`** - One-time VPS setup
```powershell
.\setup_vps.ps1 -GitRepo "https://github.com/mettatuan/freedom-wallet-bot.git"
```
- Clones repository
- Creates Python virtual environment
- Installs dependencies
- Creates .env configuration
- Sets up directory structure

### 2. Windows Service
**`setup_windows_service.ps1`** - Install bot as Windows Service
```powershell
.\setup_windows_service.ps1
```
- Downloads and installs NSSM (Non-Sucking Service Manager)
- Registers bot as Windows Service
- Configures auto-start on boot
- Sets up automatic restart on failure
- Configures log rotation (10MB limit)

### 3. Deployment
**`deploy.ps1`** - Zero-downtime deployment
```powershell
.\deploy.ps1
```
- Backs up database
- Stops service
- Pulls latest code from GitHub
- Updates dependencies
- Runs database migrations
- Starts service
- Performs health check

### 4. Database Backup
**`backup_database.ps1`** - Automated backup
```powershell
.\backup_database.ps1 -RetentionDays 7
```
- Backs up SQLite database
- Backs up PostgreSQL (if configured)
- Backs up configuration files (.env, credentials)
- Compresses backups
- Removes old backups (retention policy)

### 5. Health Monitoring
**`health_check.ps1`** - System health check
```powershell
.\health_check.ps1          # Full check
.\health_check.ps1 -Quick   # Quick check
.\health_check.ps1 -Detailed # Detailed report
```
Checks:
- Windows Service status
- Python process running
- Log activity (last hour)
- Database connectivity
- Disk space availability
- Network connectivity (Telegram API)

### 6. Log Viewer
**`view_logs.ps1`** - Interactive log viewer
```powershell
.\view_logs.ps1             # Interactive selection
.\view_logs.ps1 -Tail       # Watch latest log
.\view_logs.ps1 -Filter "ERROR"  # Filter by keyword
.\view_logs.ps1 -Service    # Service logs only
.\view_logs.ps1 -Bot        # Bot logs only
.\view_logs.ps1 -Lines 100  # Show more lines
```

## 🚀 Quick Start

### First Time Setup (on VPS)

1. **Clone repository and setup:**
```powershell
cd C:\
.\FreedomWalletBot\scripts\deployment\setup_vps.ps1
```

2. **Configure bot:**
```powershell
notepad C:\FreedomWalletBot\.env
# Add your BOT_TOKEN and ADMIN_ID
```

3. **Install as Windows Service:**
```powershell
.\scripts\deployment\setup_windows_service.ps1
```

4. **Verify deployment:**
```powershell
.\scripts\deployment\health_check.ps1
```

### Regular Updates

```powershell
cd C:\FreedomWalletBot
.\scripts\deployment\deploy.ps1
```

## 📅 Automated Maintenance

### Setup Scheduled Tasks

**Daily Backup (2 AM):**
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File C:\FreedomWalletBot\scripts\deployment\backup_database.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "FreedomWalletBot-Backup" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

**Hourly Health Check:**
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File C:\FreedomWalletBot\scripts\deployment\health_check.ps1 -Quick"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "FreedomWalletBot-HealthCheck" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

## 🔧 Common Tasks

### Check Bot Status
```powershell
Get-Service FreedomWalletBot | Format-List
.\scripts\deployment\health_check.ps1 -Quick
```

### Restart Bot
```powershell
Restart-Service FreedomWalletBot
```

### View Logs
```powershell
.\scripts\deployment\view_logs.ps1 -Tail
```

### Manual Backup
```powershell
.\scripts\deployment\backup_database.ps1
```

### Update Bot
```powershell
.\scripts\deployment\deploy.ps1
```

## 📊 Exit Codes

All scripts use standard exit codes:
- **0** - Success
- **1** - Error/Failure

Use in CI/CD or monitoring:
```powershell
.\scripts\deployment\health_check.ps1
if ($LASTEXITCODE -ne 0) {
    # Send alert
}
```

## 🛡️ Security Notes

1. **Run as Administrator** - Most scripts require elevated privileges
2. **Credentials** - Never commit `.env` file (already in `.gitignore`)
3. **Backups** - Backup files contain sensitive data, store securely
4. **Service Account** - Consider using dedicated service account instead of Administrator

## 📁 Directory Structure

```
C:\FreedomWalletBot\
├── .venv\              # Python virtual environment
├── logs\               # Application logs
│   ├── bot.log
│   ├── service_stdout.log
│   ├── service_stderr.log
│   └── deploy_*.log
├── backups\            # Database backups
│   ├── bot_*.db.zip
│   ├── postgres_*.sql.zip
│   └── config_*.zip
├── data\               # Database files
│   └── bot.db
└── scripts\deployment\ # These deployment scripts
```

## 🆘 Troubleshooting

### Service won't start
```powershell
# Check service logs
.\scripts\deployment\view_logs.ps1 -Service

# View service configuration
nssm edit FreedomWalletBot

# Reinstall service
.\scripts\deployment\setup_windows_service.ps1
```

### Deployment fails
```powershell
# Check deploy logs
.\scripts\deployment\view_logs.ps1 -Deploy

# Manual rollback
git reset --hard HEAD~1
Restart-Service FreedomWalletBot
```

### Database issues
```powershell
# Restore from backup
cd C:\FreedomWalletBot\backups
# Find latest backup: ls *.zip | sort LastWriteTime -Descending
Expand-Archive bot_YYYY-MM-DD_HH-mm-ss.db.zip -DestinationPath ..\data\
```

## 📖 Further Reading

- [Quick Start Guide](../../docs/deployment/QUICK_START.md)
- [Deployment Guide](../../docs/deployment/DEPLOYMENT.md)
- [Troubleshooting Guide](../../docs/deployment/TROUBLESHOOTING.md)
- [Production Checklist](../../docs/deployment/PRODUCTION_CHECKLIST.md)

## 🤝 Support

For issues or questions:
1. Check logs: `.\view_logs.ps1`
2. Run health check: `.\health_check.ps1 -Detailed`
3. Review documentation in `docs/deployment/`
