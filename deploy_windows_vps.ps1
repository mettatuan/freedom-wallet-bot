# ============================================================
# DEPLOY TO WINDOWS VPS
# Script chạy từ máy local để deploy lên Windows VPS
# ============================================================

param(
    [string]$VPS_HOST = "103.69.190.75",
    [string]$VPS_USER = "administrator",
    [string]$VPS_PATH = "C:\FreedomWalletBot",
    [string]$BRANCH = "cleanup/hard-refactor",
    [switch]$SetupFirstTime = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY TO WINDOWS VPS" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "VPS: $VPS_USER@$VPS_HOST" -ForegroundColor White
Write-Host "Path: $VPS_PATH" -ForegroundColor White
Write-Host "Branch: $BRANCH`n" -ForegroundColor White

# ============================================================
# FIRST TIME SETUP
# ============================================================
if ($SetupFirstTime) {
    Write-Host "🔧 FIRST TIME SETUP MODE" -ForegroundColor Yellow
    Write-Host "This will clone the repo and setup the bot on Windows VPS`n" -ForegroundColor Yellow
    
    $setupScript = @"
# Setup script for Windows VPS
Write-Host '📥 Cloning repository...' -ForegroundColor Yellow

# Remove old directory if exists
if (Test-Path '$VPS_PATH') {
    Write-Host '⚠️  Directory exists, removing...' -ForegroundColor Yellow
    Remove-Item -Path '$VPS_PATH' -Recurse -Force
}

# Clone from GitHub
git clone https://github.com/mettatuan/freedom-wallet-bot.git '$VPS_PATH'

Set-Location '$VPS_PATH'

# Checkout branch
Write-Host '🔀 Checking out branch: $BRANCH...' -ForegroundColor Yellow
git checkout $BRANCH

# Setup Python virtual environment
Write-Host '🐍 Setting up Python environment...' -ForegroundColor Yellow
python -m venv .venv

# Activate venv and install packages
Write-Host '📦 Installing dependencies...' -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
Write-Host '📝 Creating .env file...' -ForegroundColor Yellow
@'
TELEGRAM_BOT_TOKEN=REPLACE_WITH_YOUR_TOKEN
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
'@ | Out-File -FilePath '.env' -Encoding utf8

# Create data directory
New-Item -ItemType Directory -Force -Path 'data\backups' | Out-Null
New-Item -ItemType Directory -Force -Path 'logs' | Out-Null

# Run migration
Write-Host '🔄 Running database migration...' -ForegroundColor Yellow
python migrate_database.py

Write-Host ''
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '✅ SETUP COMPLETE!' -ForegroundColor Green
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Next steps:' -ForegroundColor Yellow
Write-Host '1. Edit .env file with your bot token' -ForegroundColor Gray
Write-Host '2. Start the bot (see DEPLOY_WINDOWS_VPS.md)' -ForegroundColor Gray
"@
    
    Write-Host "Running setup on Windows VPS via PowerShell remoting..." -ForegroundColor Gray
    Write-Host "(You may need to enter VPS password)`n" -ForegroundColor Gray
    
    # Use SSH to run PowerShell commands
    $setupScript | ssh "$VPS_USER@$VPS_HOST" "powershell -Command -"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ First time setup complete!" -ForegroundColor Green
        Write-Host "`n⚠️  IMPORTANT: Edit .env file with your bot token:" -ForegroundColor Yellow
        Write-Host "ssh $VPS_USER@$VPS_HOST `"notepad $VPS_PATH\.env`"" -ForegroundColor Gray
    } else {
        Write-Host "`n❌ Setup failed!" -ForegroundColor Red
        exit 1
    }
    
    exit 0
}

# ============================================================
# UPDATE EXISTING INSTALLATION
# ============================================================
Write-Host "🔄 Updating bot from GitHub..." -ForegroundColor Yellow

$updateScript = @"
`$ErrorActionPreference = 'Stop'

Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '🔄 UPDATING FREEDOM WALLET BOT' -ForegroundColor Cyan
Write-Host '============================================================' -ForegroundColor Cyan

Set-Location '$VPS_PATH'

# Backup database
Write-Host ''
Write-Host 'STEP 1: Backing up database...' -ForegroundColor Yellow
`$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
if (Test-Path 'data\bot.db') {
    Copy-Item 'data\bot.db' -Destination "data\backups\backup_`$timestamp.db"
    Write-Host '  ✅ Database backed up' -ForegroundColor Green
} else {
    Write-Host '  ℹ️  No database to backup (first deploy)' -ForegroundColor Gray
}

# Stop bot if running
Write-Host ''
Write-Host 'STEP 2: Stopping bot...' -ForegroundColor Yellow
Get-CimInstance Win32_Process -Filter "Name='python.exe' AND CommandLine LIKE '%main.py%'" | ForEach-Object {
    Stop-Process -Id `$_.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host "  ⛔ Killed old bot process (PID: `$(`$_.ProcessId))" -ForegroundColor Yellow
}
Start-Sleep -Seconds 3
Write-Host '  ✅ Bot stopped' -ForegroundColor Green

# Pull latest code
Write-Host ''
Write-Host 'STEP 3: Pulling latest code from GitHub...' -ForegroundColor Yellow
git fetch origin
git pull origin $BRANCH
Write-Host '  ✅ Code updated' -ForegroundColor Green

# Update dependencies
Write-Host ''
Write-Host 'STEP 4: Updating dependencies...' -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Host '  ✅ Dependencies updated' -ForegroundColor Green

# Run migration
Write-Host ''
Write-Host 'STEP 5: Running database migration...' -ForegroundColor Yellow
python migrate_database.py
Write-Host '  ✅ Migration complete' -ForegroundColor Green

# Start bot
Write-Host ''
Write-Host 'STEP 6: Starting bot...' -ForegroundColor Yellow
Start-Process -FilePath 'python' -ArgumentList 'main.py' -NoNewWindow -RedirectStandardOutput 'logs\bot.log' -RedirectStandardError 'logs\bot_error.log'
Start-Sleep -Seconds 3

# Verify
`$botProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { `$_.CommandLine -like '*main.py*' }
if (`$botProcess) {
    Write-Host '  ✅ Bot started (PID: ' -NoNewline -ForegroundColor Green
    Write-Host `$botProcess.Id -NoNewline -ForegroundColor White
    Write-Host ')' -ForegroundColor Green
} else {
    Write-Host '  ❌ Bot failed to start!' -ForegroundColor Red
    Write-Host '  Check logs: cat logs\bot.log' -ForegroundColor Yellow
    exit 1
}

# Show recent logs
Write-Host ''
Write-Host 'STEP 7: Recent logs:' -ForegroundColor Yellow
Get-Content 'logs\bot.log' -Tail 10

Write-Host ''
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host '✅ UPDATE COMPLETE!' -ForegroundColor Green
Write-Host '============================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Useful commands:' -ForegroundColor Yellow
Write-Host '  View logs:    Get-Content logs\bot.log -Tail 50 -Wait' -ForegroundColor Gray
Write-Host '  Check status: Get-Process python' -ForegroundColor Gray
Write-Host '  Stop bot:     Stop-Process -Name python -Force' -ForegroundColor Gray
"@

Write-Host "Running update script on Windows VPS...`n" -ForegroundColor Gray

$updateScript | ssh "$VPS_USER@$VPS_HOST" "powershell -Command -"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment successful!" -ForegroundColor Green
    Write-Host "`nView logs:" -ForegroundColor Yellow
    Write-Host "ssh $VPS_USER@$VPS_HOST `"powershell Get-Content $VPS_PATH\logs\bot.log -Tail 50 -Wait`"" -ForegroundColor Gray
} else {
    Write-Host "`n❌ Deployment failed!" -ForegroundColor Red
    exit 1
}
