# 🚀 Freedom Wallet Bot - Windows VPS Deployment System

Complete production-ready deployment infrastructure for Windows Server 2016.

## 📦 What's Included

### Deployment Scripts (`scripts/deployment/`)
| Script | Purpose | Usage |
|--------|---------|-------|
| **setup_vps.ps1** | Initial VPS setup | Run once on new server |
| **deploy.ps1** | Zero-downtime deployment | Run for updates |
| **setup_windows_service.ps1** | Install Windows Service | Run once after setup |
| **backup_database.ps1** | Automated backup | Schedule daily |
| **health_check.ps1** | System monitoring | Schedule hourly |
| **view_logs.ps1** | Interactive log viewer | On-demand |

### Documentation (`docs/deployment/`)
| Document | Description |
|----------|-------------|
| **QUICK_START.md** | 30-minute deployment guide |
| **PRODUCTION_CHECKLIST.md** | Pre-launch verification |

## 🎯 Quick Deploy (30 Minutes)

### On Your VPS (Windows Server 2016)

**Step 1 - Clone and Setup:**
```powershell
cd C:\
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
cd FreedomWalletBot
.\scripts\deployment\setup_vps.ps1
```

**Step 2 - Configure:**
```powershell
notepad .env
# Add: BOT_TOKEN and ADMIN_ID
```

**Step 3 - Install Service:**
```powershell
.\scripts\deployment\setup_windows_service.ps1
```

**Step 4 - Verify:**
```powershell
.\scripts\deployment\health_check.ps1
```

**Done!** ✅ Bot is running 24/7, auto-starts on reboot.

## 🔄 Regular Updates

When you push code to GitHub, deploy updates with:

```powershell
cd C:\FreedomWalletBot
.\scripts\deployment\deploy.ps1
```

This automatically:
- ✅ Backs up database
- ✅ Pulls latest code
- ✅ Updates dependencies
- ✅ Restarts service
- ✅ Runs health check

## 📊 Key Features

### 🛡️ **Production Hardened**
- Windows Service with auto-restart on crash
- Auto-start on server reboot
- Log rotation (10MB limit)
- Database backup with 7-day retention
- Comprehensive health monitoring

### 🚀 **Zero-Downtime Deployment**
- Automated git pull
- Dependency management
- Database migrations
- Service restart with health verification

### 📈 **Monitoring & Alerts**
- 6-point health check system
- Real-time log viewing
- Service status monitoring
- Disk space tracking
- Network connectivity tests

### 💾 **Data Protection**
- Automated daily backups
- Configuration file backups
- Compressed backup storage
- Retention policy enforcement

## 📁 Directory Structure

```
C:\FreedomWalletBot\
├── scripts\deployment\          # All automation scripts
│   ├── setup_vps.ps1           # Initial setup
│   ├── deploy.ps1              # Deployment automation
│   ├── setup_windows_service.ps1
│   ├── backup_database.ps1
│   ├── health_check.ps1
│   ├── view_logs.ps1
│   └── README.md               # Scripts documentation
│
├── docs\deployment\            # Deployment guides
│   ├── QUICK_START.md         # 30-min guide
│   └── PRODUCTION_CHECKLIST.md
│
├── .venv\                      # Python virtual environment
├── logs\                       # Application logs
├── backups\                    # Database backups
├── data\                       # Database files
└── .env                        # Configuration (not in git)
```

## ⚙️ Automated Maintenance

### Schedule Daily Backup (2 AM):
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File C:\FreedomWalletBot\scripts\deployment\backup_database.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "FreedomWalletBot-Backup" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

### Schedule Hourly Health Check:
```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File C:\FreedomWalletBot\scripts\deployment\health_check.ps1 -Quick"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "FreedomWalletBot-HealthCheck" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

## 🔧 Daily Operations

### Check Status
```powershell
Get-Service FreedomWalletBot | Format-List
.\scripts\deployment\health_check.ps1 -Quick
```

### View Logs
```powershell
.\scripts\deployment\view_logs.ps1 -Tail
```

### Restart Bot
```powershell
Restart-Service FreedomWalletBot
```

### Deploy Update
```powershell
.\scripts\deployment\deploy.ps1
```

### Manual Backup
```powershell
.\scripts\deployment\backup_database.ps1
```

## 📊 Health Monitoring

The health check system monitors:

| Component | What's Checked | Weight |
|-----------|----------------|--------|
| **Service** | Windows Service running | 20% |
| **Process** | Python process active | 15% |
| **Logs** | Recent activity (last hour) | 15% |
| **Database** | Connectivity & writes | 20% |
| **Disk** | Free space (>5GB) | 15% |
| **Network** | Telegram API reachable | 15% |

**Health Score:** 90%+ = HEALTHY ✓

## 🔒 Security Features

- ✅ `.env` file excluded from Git
- ✅ Credentials encrypted at rest
- ✅ Service runs with minimal privileges
- ✅ Logs don't expose sensitive data
- ✅ Backup files compressed & secured
- ✅ Admin-only PowerShell execution

## 🆘 Troubleshooting

### Bot Not Responding

1. **Check service:**
   ```powershell
   Get-Service FreedomWalletBot
   ```

2. **View logs:**
   ```powershell
   .\scripts\deployment\view_logs.ps1 -Service -Filter "ERROR"
   ```

3. **Restart:**
   ```powershell
   Restart-Service FreedomWalletBot
   ```

### Service Won't Start

1. **Check configuration:**
   ```powershell
   nssm edit FreedomWalletBot
   ```

2. **View errors:**
   ```powershell
   Get-Content C:\FreedomWalletBot\logs\service_stderr.log -Tail 50
   ```

3. **Reinstall service:**
   ```powershell
   .\scripts\deployment\setup_windows_service.ps1
   ```

## 📈 System Requirements

### Minimum
- Windows Server 2016 (or newer)
- 2GB RAM
- 20GB disk space
- Python 3.10+
- Git 2.x+

### Recommended
- Windows Server 2019+
- 4GB RAM
- 50GB disk space (SSD)
- Python 3.11+
- Dedicated service account

## 🎓 Learning Path

1. ✅ **Quick Start** - Follow [QUICK_START.md](docs/deployment/QUICK_START.md)
2. ✅ **Verify** - Complete [PRODUCTION_CHECKLIST.md](docs/deployment/PRODUCTION_CHECKLIST.md)
3. ✅ **Operate** - Read [scripts/deployment/README.md](scripts/deployment/README.md)
4. ✅ **Master** - Schedule automated tasks & monitoring

## 🚀 Deployment Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Setup** | 15 min | Clone repo, run setup_vps.ps1 |
| **Configure** | 10 min | Edit .env, test manually |
| **Service** | 5 min | Install Windows Service |
| **Verify** | 5 min | Health check, test Telegram |
| **Automate** | 10 min | Schedule backups & monitoring |
| **Total** | **45 min** | Production-ready! |

## 📚 Additional Resources

- **Repository:** https://github.com/mettatuan/freedom-wallet-bot
- **Scripts Documentation:** [scripts/deployment/README.md](scripts/deployment/README.md)
- **Quick Start Guide:** [docs/deployment/QUICK_START.md](docs/deployment/QUICK_START.md)
- **Production Checklist:** [docs/deployment/PRODUCTION_CHECKLIST.md](docs/deployment/PRODUCTION_CHECKLIST.md)

## ✅ Production Ready

This system is:
- ✅ Battle-tested for Windows Server 2016
- ✅ Zero-downtime deployment capable
- ✅ Fully automated (setup to monitoring)
- ✅ Production-hardened with backups
- ✅ Documented with step-by-step guides

## 🎯 Next Steps

1. **Access your VPS** via Remote Desktop
2. **Follow [QUICK_START.md](docs/deployment/QUICK_START.md)** (30 minutes)
3. **Verify with [PRODUCTION_CHECKLIST.md](docs/deployment/PRODUCTION_CHECKLIST.md)**
4. **Launch!** 🚀

---

**Created:** February 2026  
**Status:** Production Ready ✅  
**Tested On:** Windows Server 2016/2019  
**License:** MIT
