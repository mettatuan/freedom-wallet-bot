# 🚀 Quick Start - 30 Minutes to Production

Deploy Freedom Wallet Bot to Windows Server 2016 in 30 minutes.

## Prerequisites

Before you begin, ensure you have:

- ✅ Windows Server 2016 (or newer) VPS
- ✅ Administrator access
- ✅ Python 3.10+ installed
- ✅ Git installed
- ✅ Internet connection
- ✅ Telegram Bot Token (from @BotFather)
- ✅ Your Telegram User ID

## Step-by-Step Guide

### 1️⃣ Connect to VPS (5 minutes)

**Via Remote Desktop:**
```
Windows Key + R → mstsc
Computer: your_vps_ip
Username: Administrator
Password: your_password
```

### 2️⃣ Clone Repository (3 minutes)

Open PowerShell as Administrator:

```powershell
cd C:\
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
cd FreedomWalletBot
```

### 3️⃣ Initial Setup (5 minutes)

Run the setup script:

```powershell
.\scripts\deployment\setup_vps.ps1
```

This will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies
- ✅ Create `.env` configuration file
- ✅ Set up directory structure

**Expected output:**
```
╔════════════════════════════════════════════════════════════════╗
║     Freedom Wallet Bot - VPS Setup (Windows Server 2016)      ║
╚════════════════════════════════════════════════════════════════╝

✓ Git is installed: git version 2.x.x
✓ Python is installed: Python 3.10.x
✓ Repository cloned successfully
✓ Virtual environment created
✓ Dependencies installed successfully
✓ Created .env from .env.example

╔════════════════════════════════════════════════════════════════╗
║                    Setup Complete! ✓                           ║
╚════════════════════════════════════════════════════════════════╝
```

### 4️⃣ Configure Bot (7 minutes)

Edit the `.env` file:

```powershell
notepad C:\FreedomWalletBot\.env
```

**Minimum required configuration:**

```ini
# Telegram Bot Configuration
BOT_TOKEN=7654321098:AAHdEz9ghIjKLmNoPqRsTuVwXyZ1234567890
ADMIN_ID=1234567890

# Database (SQLite - default)
DATABASE_URL=sqlite:///./data/bot.db

# Environment
ENVIRONMENT=production
DEBUG=False
```

**How to get your Telegram User ID:**
1. Open Telegram
2. Search for `@userinfobot`
3. Send `/start`
4. Copy your ID

**Save and close** the file (Ctrl+S, Alt+F4).

### 5️⃣ Test Bot Manually (3 minutes)

Before installing as a service, test manually:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run bot
python main.py
```

**Expected output:**
```
2026-02-19 14:30:00 - INFO - Starting Freedom Wallet Bot...
2026-02-19 14:30:01 - INFO - Bot started successfully
2026-02-19 14:30:01 - INFO - Listening for messages...
```

**Test in Telegram:**
1. Open Telegram
2. Search for your bot (@YourBotUsername)
3. Send `/start`
4. You should receive a welcome message

**Stop the bot:** Press `Ctrl+C` in PowerShell

If working correctly, proceed to next step. If not, see [Troubleshooting](#troubleshooting).

### 6️⃣ Install as Windows Service (5 minutes)

Install the bot as a Windows Service (auto-start on boot):

```powershell
.\scripts\deployment\setup_windows_service.ps1
```

This will:
- ✅ Download NSSM (Non-Sucking Service Manager)
- ✅ Create Windows Service
- ✅ Configure auto-start on boot
- ✅ Configure automatic restart on crash
- ✅ Set up log rotation
- ✅ Start the service

**Expected output:**
```
╔════════════════════════════════════════════════════════════════╗
║        Freedom Wallet Bot - Windows Service Setup              ║
╚════════════════════════════════════════════════════════════════╝

✓ NSSM installed to C:\nssm\nssm.exe
✓ Service installed successfully
✓ Service started successfully!

╔════════════════════════════════════════════════════════════════╗
║            Windows Service Setup Complete! ✓                   ║
╚════════════════════════════════════════════════════════════════╝

Service Information:
  • Service Name: FreedomWalletBot
  • Display Name: Freedom Wallet Telegram Bot
  • Status: Running
  • Startup Type: Automatic
```

### 7️⃣ Verify Deployment (2 minutes)

Run health check:

```powershell
.\scripts\deployment\health_check.ps1
```

**Expected output:**
```
╔════════════════════════════════════════════════════════════════╗
║              Freedom Wallet Bot - Health Check                 ║
╚════════════════════════════════════════════════════════════════╝

✓ Service is running
✓ Bot process running (PID: 1234, Uptime: 00.00:05:00)
✓ Recent log activity detected
✓ Database active (last write: 0.5 min ago, size: 0.12 MB)
✓ Sufficient disk space: 25.5 GB free (20% used)
✓ Telegram API reachable

╔════════════════════════════════════════════════════════════════╗
║                    Health Check Summary                        ║
╚════════════════════════════════════════════════════════════════╝

Overall Health Score: 100 / 100 (100%)
Status: HEALTHY ✓
```

**If health score is 90%+, you're done!** 🎉

## ✅ Deployment Complete!

Your bot is now:
- ✅ Running 24/7
- ✅ Auto-starts on server reboot
- ✅ Auto-restarts on crash
- ✅ Logging everything

## Next Steps

### Setup Automated Backups

Schedule daily backups at 2 AM:

```powershell
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File C:\FreedomWalletBot\scripts\deployment\backup_database.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "FreedomWalletBot-Backup" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

### Daily Maintenance Commands

**Check status:**
```powershell
Get-Service FreedomWalletBot | Format-List
```

**View live logs:**
```powershell
.\scripts\deployment\view_logs.ps1 -Tail
```

**Deploy updates:**
```powershell
.\scripts\deployment\deploy.ps1
```

**Manual backup:**
```powershell
.\scripts\deployment\backup_database.ps1
```

## 🆘 Troubleshooting

### Bot not responding in Telegram

**Check service status:**
```powershell
Get-Service FreedomWalletBot
```

**Check logs:**
```powershell
.\scripts\deployment\view_logs.ps1 -Service
```

**Restart service:**
```powershell
Restart-Service FreedomWalletBot
```

### Invalid BOT_TOKEN error

1. Go to Telegram → Search `@BotFather`
2. Send `/token`
3. Select your bot
4. Copy new token
5. Update `.env` file
6. Restart service: `Restart-Service FreedomWalletBot`

### Permission errors

Make sure you're running PowerShell **as Administrator**.

### Python not found

Install Python 3.10+ from https://www.python.org/downloads/

During installation:
- ✅ Check "Add Python to PATH"
- ✅ Check "Install for all users"

### Git not found

Install Git from https://git-scm.com/downloads

### Service won't start

**Check detailed service config:**
```powershell
nssm edit FreedomWalletBot
```

**View service logs:**
```powershell
Get-Content C:\FreedomWalletBot\logs\service_stderr.log -Tail 50
```

## 📊 Monitoring Dashboard

Create a simple monitoring script:

```powershell
# Save as: monitor.ps1
while ($true) {
    Clear-Host
    Write-Host "Freedom Wallet Bot - Status Dashboard" -ForegroundColor Cyan
    Write-Host "══════════════════════════════════════" -ForegroundColor Cyan
    
    $service = Get-Service FreedomWalletBot
    Write-Host "`nService Status: $($service.Status)" -ForegroundColor Green
    
    $process = Get-Process python -ErrorAction SilentlyContinue | 
               Where-Object { $_.Path -like "*FreedomWalletBot*" }
    if ($process) {
        $uptime = ((Get-Date) - $process.StartTime).ToString("dd\.hh\:mm\:ss")
        $memMB = [math]::Round($process.WorkingSet64 / 1MB, 2)
        Write-Host "Uptime: $uptime" -ForegroundColor White
        Write-Host "Memory: $memMB MB" -ForegroundColor White
    }
    
    Write-Host "`nPress Ctrl+C to exit..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
}
```

Run it:
```powershell
.\monitor.ps1
```

## 📚 Further Reading

- [Full Deployment Guide](DEPLOYMENT.md) - Comprehensive documentation
- [Production Checklist](PRODUCTION_CHECKLIST.md) - Pre-launch verification
- [Troubleshooting Guide](TROUBLESHOOTING.md) - Common issues & solutions
- [Security Best Practices](SECURITY.md) - Hardening your deployment

## 🎯 Summary

**Total time:** ~30 minutes

| Step | Time | Status |
|------|------|--------|
| 1. Connect to VPS | 5 min | ✅ |
| 2. Clone repository | 3 min | ✅ |
| 3. Run setup script | 5 min | ✅ |
| 4. Configure .env | 7 min | ✅ |
| 5. Test manually | 3 min | ✅ |
| 6. Install service | 5 min | ✅ |
| 7. Verify deployment | 2 min | ✅ |

**Your bot is now production-ready!** 🚀
