# ============================================================
# FREEDOM WALLET BOT - VPS DEPLOYMENT SCRIPT
# Phase 2-3 Complete Version
# ============================================================

param(
    [string]$VPS_HOST = "your_vps_ip",
    [string]$VPS_USER = "your_username",
    [string]$VPS_PATH = "/home/your_username/FreedomWalletBot",
    [switch]$SkipTests = $false,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🚀 FREEDOM WALLET BOT - VPS DEPLOYMENT" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# ============================================================
# STEP 1: Pre-deployment checks
# ============================================================
Write-Host "STEP 1: Pre-deployment checks..." -ForegroundColor Yellow

# Check if local changes are tested
if (-not $SkipTests) {
    Write-Host "  → Running Phase 3 tests..." -ForegroundColor Gray
    
    $testResult = python test_phase3.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Tests failed! Fix errors before deploying." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  ✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Skipping tests (use -SkipTests carefully!)" -ForegroundColor Yellow
}

# Check SSH connection
Write-Host "`n  → Testing SSH connection to VPS..." -ForegroundColor Gray

if ($DryRun) {
    Write-Host "  [DRY RUN] Would test: ssh $VPS_USER@$VPS_HOST" -ForegroundColor Magenta
} else {
    $sshTest = ssh -o ConnectTimeout=10 "$VPS_USER@$VPS_HOST" "echo 'SSH OK'" 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Cannot connect to VPS. Check SSH config." -ForegroundColor Red
        Write-Host "     Error: $sshTest" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  ✅ SSH connection successful!" -ForegroundColor Green
}

# ============================================================
# STEP 2: Backup VPS database
# ============================================================
Write-Host "`nSTEP 2: Backing up VPS database..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "vps_backup_$timestamp.db"

if ($DryRun) {
    Write-Host "  [DRY RUN] Would backup: $VPS_PATH/data/bot.db" -ForegroundColor Magenta
} else {
    ssh "$VPS_USER@$VPS_HOST" @"
mkdir -p $VPS_PATH/data/backups
if [ -f $VPS_PATH/data/bot.db ]; then
    cp $VPS_PATH/data/bot.db $VPS_PATH/data/backups/$backupName
    echo 'Backup created: $backupName'
else
    echo 'No existing database to backup'
fi
"@
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Database backed up: $backupName" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Backup failed (may not exist yet)" -ForegroundColor Yellow
    }
}

# ============================================================
# STEP 3: Stop bot on VPS
# ============================================================
Write-Host "`nSTEP 3: Stopping bot on VPS..." -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "  [DRY RUN] Would stop bot process" -ForegroundColor Magenta
} else {
    ssh "$VPS_USER@$VPS_HOST" @"
# Find and kill Python bot process
pkill -f 'python.*main.py' || echo 'No bot process found'
sleep 2
"@
    
    Write-Host "  ✅ Bot stopped" -ForegroundColor Green
}

# ============================================================
# STEP 4: Upload files to VPS
# ============================================================
Write-Host "`nSTEP 4: Uploading files to VPS..." -ForegroundColor Yellow

# Files/folders to exclude
$excludeList = @(
    ".git",
    ".venv",
    "__pycache__",
    "*.pyc",
    "data/bot.db",
    "data/backups",
    "logs/*.log",
    ".env",
    "*.backup",
    "node_modules",
    ".vscode"
)

$rsyncExcludes = $excludeList | ForEach-Object { "--exclude='$_'" }

if ($DryRun) {
    Write-Host "  [DRY RUN] Would upload with rsync:" -ForegroundColor Magenta
    Write-Host "    Source: ." -ForegroundColor Magenta
    Write-Host "    Destination: $VPS_USER@${VPS_HOST}:$VPS_PATH" -ForegroundColor Magenta
} else {
    # Use rsync for efficient upload (Windows: install via Git Bash or WSL)
    Write-Host "  → Syncing files..." -ForegroundColor Gray
    
    # Check if rsync is available
    $hasRsync = Get-Command rsync -ErrorAction SilentlyContinue
    
    if ($hasRsync) {
        # Use rsync (faster, incremental)
        $rsyncCmd = "rsync -avz --progress " + ($rsyncExcludes -join " ") + " ./ $VPS_USER@${VPS_HOST}:$VPS_PATH/"
        Invoke-Expression $rsyncCmd
    } else {
        # Fallback to scp (slower, full copy)
        Write-Host "  ⚠️ rsync not found, using scp (slower)..." -ForegroundColor Yellow
        
        scp -r `
            -o "LogLevel=ERROR" `
            bot config alembic *.py requirements.txt `
            "$VPS_USER@${VPS_HOST}:$VPS_PATH/"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Files uploaded successfully!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Upload failed!" -ForegroundColor Red
        exit 1
    }
}

# ============================================================
# STEP 5: Install dependencies on VPS
# ============================================================
Write-Host "`nSTEP 5: Installing dependencies on VPS..." -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "  [DRY RUN] Would install dependencies" -ForegroundColor Magenta
} else {
    ssh "$VPS_USER@$VPS_HOST" @"
cd $VPS_PATH

# Create virtual environment if not exists
if [ ! -d .venv ]; then
    echo 'Creating virtual environment...'
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo 'Dependencies installed!'
"@
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Dependencies installed!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Dependency installation failed!" -ForegroundColor Red
        exit 1
    }
}

# ============================================================
# STEP 6: Run database migration
# ============================================================
Write-Host "`nSTEP 6: Running database migration..." -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "  [DRY RUN] Would run: python migrate_database.py" -ForegroundColor Magenta
} else {
    ssh "$VPS_USER@$VPS_HOST" @"
cd $VPS_PATH
source .venv/bin/activate
python migrate_database.py
"@
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Database migration complete!" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Migration may have failed (check manually)" -ForegroundColor Yellow
    }
}

# ============================================================
# STEP 7: Start bot on VPS
# ============================================================
Write-Host "`nSTEP 7: Starting bot on VPS..." -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "  [DRY RUN] Would start bot with nohup" -ForegroundColor Magenta
} else {
    ssh "$VPS_USER@$VPS_HOST" @"
cd $VPS_PATH
source .venv/bin/activate

# Start bot in background with nohup
nohup python main.py > logs/bot.log 2>&1 &

# Wait a moment
sleep 3

# Check if bot started
if pgrep -f 'python.*main.py' > /dev/null; then
    echo 'Bot started successfully!'
    exit 0
else
    echo 'Bot failed to start! Check logs/bot.log'
    exit 1
fi
"@
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Bot started successfully!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Bot failed to start!" -ForegroundColor Red
        Write-Host "     Check logs with: ssh $VPS_USER@$VPS_HOST 'tail -50 $VPS_PATH/logs/bot.log'" -ForegroundColor Yellow
        exit 1
    }
}

# ============================================================
# STEP 8: Verify deployment
# ============================================================
Write-Host "`nSTEP 8: Verifying deployment..." -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "  [DRY RUN] Would verify bot status" -ForegroundColor Magenta
} else {
    Start-Sleep -Seconds 2
    
    $status = ssh "$VPS_USER@$VPS_HOST" @"
cd $VPS_PATH

# Check process
PID=\$(pgrep -f 'python.*main.py')
if [ -z "\$PID" ]; then
    echo 'ERROR: Bot not running!'
    exit 1
fi

echo "✅ Bot running (PID: \$PID)"

# Check recent logs
echo ""
echo "Recent logs:"
tail -10 logs/bot.log
"@
    
    Write-Host "`n  $status" -ForegroundColor Gray
}

# ============================================================
# DEPLOYMENT SUMMARY
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`nDeployed to: $VPS_USER@$VPS_HOST" -ForegroundColor White
Write-Host "Path: $VPS_PATH" -ForegroundColor White
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White

if (-not $DryRun) {
    Write-Host "`nUseful commands:" -ForegroundColor Yellow
    Write-Host "  View logs:    ssh $VPS_USER@$VPS_HOST 'tail -f $VPS_PATH/logs/bot.log'" -ForegroundColor Gray
    Write-Host "  Stop bot:     ssh $VPS_USER@$VPS_HOST 'pkill -f python.*main.py'" -ForegroundColor Gray
    Write-Host "  Restart bot:  ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && nohup python main.py > logs/bot.log 2>&1 &'" -ForegroundColor Gray
    Write-Host "  Check status: ssh $VPS_USER@$VPS_HOST 'pgrep -fa python.*main.py'" -ForegroundColor Gray
}

Write-Host "`n🎉 Bot is now live on VPS!`n" -ForegroundColor Green
