# 🐛 TROUBLESHOOTING GUIDE

## 🚨 COMMON ISSUES & SOLUTIONS

---

### 1. ❌ "ImportError: cannot import name..."

**Symptoms:**
```
ImportError: cannot import name 'register_setup_guide_handlers'
```

**Cause:** Function name mismatch between import and actual function name.

**Solution:**
```powershell
# Check actual function name in the file
Get-Content app\handlers\support\setup_guide.py | Select-String "def register"

# Update import in main.py to match
```

**Prevention:** Use IDE with auto-complete (VS Code + Python extension).

---

### 2. ❌ "Service failed to start"

**Symptoms:**
- Service status shows "Stopped"
- Bot not responding in Telegram
- No recent activity in logs

**Diagnosis:**
```powershell
# Check service logs
Get-Content D:\FreedomWalletBot\data\logs\service.log -Tail 50

# Try manual start to see error
cd D:\FreedomWalletBot
& .venv\Scripts\Activate.ps1
python main.py
```

**Common Causes & Solutions:**

#### a) `.env` file missing or invalid
```powershell
# Verify .env exists
Test-Path D:\FreedomWalletBot\.env

# Check required variables
Get-Content .env | Select-String "TELEGRAM_BOT_TOKEN|DATABASE_URL"
```

**Fix:** Copy `.env.production` to `.env` and fill in values.

#### b) Database connection failed
```powershell
# Test PostgreSQL
psql -U freedomwallet -d freedomwalletdb

# If fails, check PostgreSQL service
Get-Service postgresql*
Start-Service postgresql-x64-15  # Adjust version
```

#### c) Port already in use
```powershell
# Check if another Python process is running
Get-Process python

# Kill old process
Stop-Process -Name python -Force
```

---

### 3. ❌ "Database migration failed"

**Symptoms:**
```
alembic.util.exc.CommandError: Can't locate revision identified by...
```

**Solution:**

```powershell
# Option 1: Reset migrations (CAUTION: Development only)
Remove-Item migrations\versions\*.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Option 2: Skip migrations (if database up-to-date)
# Edit deploy.ps1 and comment out migration step
```

---

### 4. ❌ "Git pull conflicts"

**Symptoms:**
```
error: Your local changes to the following files would be overwritten by merge
```

**Solution:**

```powershell
# Option 1: Stash changes (keep them)
git stash
git pull origin main
git stash pop  # Restore changes

# Option 2: Discard local changes (careful!)
git reset --hard HEAD
git pull origin main

# Option 3: Commit local changes first
git add .
git commit -m "Local changes"
git pull origin main
# Resolve any conflicts manually
```

---

### 5. ❌ "ModuleNotFoundError: No module named 'X'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'openai'
```

**Cause:** Missing dependencies or wrong virtual environment.

**Solution:**

```powershell
# Verify you're in virtual environment
& .venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt

# If still fails, recreate venv
Remove-Item .venv -Recurse -Force
python -m venv .venv
& .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### 6. ❌ "Database locked" (SQLite only)

**Symptoms:**
```
sqlite3.OperationalError: database is locked
```

**Cause:** Multiple processes accessing SQLite (SQLite doesn't support concurrent writes).

**Solution:**

**Short-term:** Restart bot
```powershell
Restart-Service FreedomWalletBot
```

**Long-term:** **Migrate to PostgreSQL** (see [DATABASE_MIGRATION.md](DATABASE_MIGRATION.md))

---

### 7. ❌ "Telegram API timeout"

**Symptoms:**
```
telegram.error.TimedOut: Timed out
```

**Cause:** Network connectivity issues.

**Diagnosis:**

```powershell
# Test connectivity
Test-Connection api.telegram.org

# Check DNS
nslookup api.telegram.org

# Check firewall
Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*Python*" }
```

**Solution:**

```powershell
# Add firewall rule for Python
New-NetFirewallRule -DisplayName "Python (Bot)" -Direction Outbound -Program "D:\FreedomWalletBot\.venv\Scripts\python.exe" -Action Allow

# Restart bot
Restart-Service FreedomWalletBot
```

---

### 8. ❌ "Disk space error"

**Symptoms:**
```
OSError: [Errno 28] No space left on device
```

**Diagnosis:**

```powershell
# Check disk space
Get-PSDrive D

# Find large files
Get-ChildItem D:\FreedomWalletBot -Recurse | Sort-Object Length -Descending | Select-Object -First 20 Length, FullName
```

**Solution:**

```powershell
# Clean old logs
Remove-Item D:\FreedomWalletBot\data\logs\*.log.* -Force

# Clean old backups (keep last 7 days)
$Cutoff = (Get-Date).AddDays(-7)
Get-ChildItem D:\FreedomWalletBot\backups -Recurse | Where-Object { $_.LastWriteTime -lt $Cutoff } | Remove-Item -Force

# Clean Python cache
Get-ChildItem D:\FreedomWalletBot -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force
```

---

### 9. ❌ "Permission denied"

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Cause:** Script running without sufficient permissions.

**Solution:**

```powershell
# Run PowerShell as Administrator
# Right-click PowerShell -> "Run as Administrator"

# OR set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 10. ❌ "Bot responds slowly"

**Symptoms:**
- Bot takes 5-10 seconds to respond
- High memory usage
- CPU spikes

**Diagnosis:**

```powershell
# Check bot process
Get-Process python | Where-Object { $_.Path -like "*FreedomWallet*" } | Select-Object CPU, WorkingSet64, StartTime

# Check database performance
# Connect to PostgreSQL
psql -U freedomwallet -d freedomwalletdb
\timing
SELECT COUNT(*) FROM users;  # Should be < 100ms
```

**Solutions:**

#### a) Database needs indexing
```sql
-- In PostgreSQL
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_sheets_user_id ON user_sheets(user_id);
VACUUM ANALYZE;
```

#### b) Too many logs
```powershell
# Rotate logs
Rename-Item data\logs\bot.log data\logs\bot.log.old
Restart-Service FreedomWalletBot
```

#### c) Memory leak (restart needed)
```powershell
Restart-Service FreedomWalletBot
```

---

### 11. ❌ "Health check fails"

**Symptoms:**
- Health check script reports issues
- Service running but bot not responding

**Diagnosis:**

```powershell
# Run health check manually
.\scripts\health_check.ps1

# Check each component
Get-Service FreedomWalletBot  # Service status
Get-Process python            # Process running
Test-Connection api.telegram.org  # Network
psql -U freedomwallet -d freedomwalletdb -c "SELECT 1;"  # Database
```

**Solution:** Fix reported issues one by one.

---

### 12. ❌ "Backup fails"

**Symptoms:**
```
pg_dump: error: connection to database failed
```

**Diagnosis:**

```powershell
# Test pg_dump manually
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" --version

# Check environment variable
$env:PGPASSWORD = "your-password"
& "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -U freedomwallet -d freedomwalletdb -F p -f test.sql
```

**Solution:**

```powershell
# Set DB_PASSWORD environment variable (system-wide)
[System.Environment]::SetEnvironmentVariable("DB_PASSWORD", "your-password", [System.EnvironmentVariableTarget]::Machine)

# Or edit backup script to include password
# Edit: scripts\backup_database.ps1
```

---

## 🔍 DIAGNOSTIC COMMANDS

### Quick Health Check

```powershell
# Service status
Get-Service FreedomWalletBot

# Process info
Get-Process python | Where-Object { $_.Path -like "*FreedomWallet*" }

# Recent errors in log
Select-String -Path "data\logs\bot.log" -Pattern "ERROR|CRITICAL" -CaseSensitive | Select-Object -Last 5

# Disk space
Get-PSDrive D | Select-Object Used, Free

# Network
Test-Connection api.telegram.org -Count 1
```

### Detailed System Info

```powershell
# System info
Get-ComputerInfo | Select-Object WindowsVersion, OsArchitecture, TotalPhysicalMemory

# Python version
python --version

# PostgreSQL version
psql --version

# Git version
git --version

# Installed packages
pip list
```

---

## 📞 GETTING HELP

### 1. Check Logs First
```powershell
.\scripts\view_logs.ps1 -ErrorsOnly -Lines 100
```

### 2. Run Health Check
```powershell
.\scripts\health_check.ps1
```

### 3. Test Components Individually

**Test Bot:**
```powershell
cd D:\FreedomWalletBot
& .venv\Scripts\Activate.ps1
python main.py
# Press Ctrl+C after testing
```

**Test Database:**
```powershell
psql -U freedomwallet -d freedomwalletdb
\dt  # List tables
\q   # Quit
```

**Test Network:**
```powershell
Test-Connection api.telegram.org
```

### 4. Collect Debug Info

```powershell
# Create debug report
$Report = @"
=== DEBUG REPORT ===
Date: $(Get-Date)
Service Status: $(Get-Service FreedomWalletBot | Select-Object -ExpandProperty Status)
Process: $(Get-Process python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
Python Version: $(python --version)
Disk Space: $(Get-PSDrive D | Select-Object -ExpandProperty Free)
Recent Errors:
$(Select-String -Path "data\logs\bot.log" -Pattern "ERROR" -CaseSensitive | Select-Object -Last 5 | Out-String)
"@

$Report | Out-File debug_report.txt
Write-Host "Debug report saved to: debug_report.txt"
```

---

## 🛠️ MAINTENANCE TASKS

### Weekly

```powershell
# Check service health
.\scripts\health_check.ps1

# Review logs for errors
.\scripts\view_logs.ps1 -ErrorsOnly

# Check disk space
Get-PSDrive D

# Verify backups
Get-ChildItem backups\database | Sort-Object LastWriteTime -Descending | Select-Object -First 7
```

### Monthly

```powershell
# Update dependencies
& .venv\Scripts\Activate.ps1
pip install --upgrade pip
pip list --outdated

# Clean old logs
Remove-Item data\logs\*.log.* -Force

# Optimize database
psql -U freedomwallet -d freedomwalletdb -c "VACUUM ANALYZE;"

# Review scheduled tasks
Get-ScheduledTask | Where-Object { $_.TaskName -like "*FreedomWallet*" }
```

---

**✅ Most issues can be fixed by:**
1. Checking logs
2. Restarting the service
3. Verifying .env configuration
4. Testing database connection
5. Ensuring network connectivity
