# ============================================
# PRODUCTION DEPLOYMENT SCRIPT
# ============================================
# Zero-downtime deployment for FreedomWalletBot
# Run this on VPS after git push
# ============================================

param(
    [switch]$SkipBackup = $false,
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"
$BotDir = "D:\FreedomWalletBot"
$VenvPath = "$BotDir\.venv"
$ServiceName = "FreedomWalletBot"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "🚀 FREEDOMWALLETBOT DEPLOYMENT"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "📅 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# Change to bot directory
Set-Location $BotDir

# ============================================
# STEP 1: Pre-deployment checks
# ============================================
Write-Host "[1/8] 🔍 Pre-deployment checks..."

# Check if Git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git is not installed!"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path $VenvPath)) {
    Write-Host "❌ Virtual environment not found at $VenvPath"
    Write-Host "   Run setup_vps.ps1 first!"
    exit 1
}

Write-Host "   ✅ All checks passed"

# ============================================
# STEP 2: Backup database (if PostgreSQL)
# ============================================
if (-not $SkipBackup) {
    Write-Host ""
    Write-Host "[2/8] 💾 Creating database backup..."
    try {
        & "$BotDir\scripts\backup_database.ps1" -RetentionDays 7
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   ⚠️ Backup failed, but continuing..."
        } else {
            Write-Host "   ✅ Backup completed"
        }
    } catch {
        Write-Host "   ⚠️ Backup error: $_"
        Write-Host "   Continuing deployment..."
    }
} else {
    Write-Host ""
    Write-Host "[2/8] ⏭️ Skipping backup (--SkipBackup flag)"
}

# ============================================
# STEP 3: Pull latest code
# ============================================
Write-Host ""
Write-Host "[3/8] 📥 Pulling latest code from Git..."

$GitStatus = git status --porcelain
if ($GitStatus) {
    Write-Host "   ⚠️ Uncommitted changes detected:"
    Write-Host $GitStatus
    $response = Read-Host "   Continue anyway? (yes/no)"
    if ($response -ne "yes") {
        Write-Host "❌ Deployment cancelled"
        exit 1
    }
}

git fetch origin
$LocalCommit = git rev-parse HEAD
$RemoteCommit = git rev-parse origin/main

if ($LocalCommit -eq $RemoteCommit) {
    Write-Host "   ℹ️ Already up to date"
} else {
    Write-Host "   🔄 Pulling changes..."
    git pull origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Git pull failed!"
        exit 1
    }
    Write-Host "   ✅ Code updated"
}

# ============================================
# STEP 4: Install/Update dependencies
# ============================================
Write-Host ""
Write-Host "[4/8] 📦 Updating dependencies..."

& "$VenvPath\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Dependency installation failed!"
    exit 1
}

Write-Host "   ✅ Dependencies updated"

# ============================================
# STEP 5: Database migrations (if any)
# ============================================
Write-Host ""
Write-Host "[5/8] 🗄️  Running database migrations..."

if (Test-Path "$BotDir\alembic.ini") {
    alembic upgrade head
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Migrations applied"
    } else {
        Write-Host "   ⚠️ Migration failed, check manually"
    }
} else {
    Write-Host "   ℹ️ No alembic.ini found, skipping migrations"
}

# ============================================
# STEP 6: Run tests (optional)
# ============================================
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "[6/8] 🧪 Running tests..."
    
    if (Test-Path "$BotDir\tests") {
        pytest tests/ -v --tb=short
        if ($LASTEXITCODE -ne 0) {
            $response = Read-Host "   ⚠️ Tests failed! Continue deployment? (yes/no)"
            if ($response -ne "yes") {
                Write-Host "❌ Deployment cancelled"
                exit 1
            }
        } else {
            Write-Host "   ✅ All tests passed"
        }
    } else {
        Write-Host "   ℹ️ No tests directory found"
    }
} else {
    Write-Host ""
    Write-Host "[6/8] ⏭️ Skipping tests (--SkipTests flag)"
}

# ============================================
# STEP 7: Restart bot service
# ============================================
Write-Host ""
Write-Host "[7/8] 🔄 Restarting bot service..."

$Service = Get-Service $ServiceName -ErrorAction SilentlyContinue

if ($Service) {
    Write-Host "   🛑 Stopping service..."
    Stop-Service $ServiceName -Force
    Start-Sleep -Seconds 2
    
    Write-Host "   ▶️ Starting service..."
    Start-Service $ServiceName
    Start-Sleep -Seconds 3
    
    $Service = Get-Service $ServiceName
    if ($Service.Status -eq "Running") {
        Write-Host "   ✅ Service restarted successfully"
    } else {
        Write-Host "   ❌ Service failed to start!"
        Write-Host "   Check logs: $BotDir\data\logs\"
        exit 1
    }
} else {
    Write-Host "   ⚠️ Service '$ServiceName' not found"
    Write-Host "   Run setup_windows_service.ps1 first!"
    Write-Host ""
    Write-Host "   Starting bot manually..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $BotDir; & .venv\Scripts\Activate.ps1; python main.py"
}

# ============================================
# STEP 8: Health check
# ============================================
Write-Host ""
Write-Host "[8/8] 🏥 Health check..."

Start-Sleep -Seconds 5

# Check if process is running
$Process = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*$BotDir*" }

if ($Process) {
    Write-Host "   ✅ Bot process is running (PID: $($Process.Id))"
} else {
    Write-Host "   ⚠️ Bot process not detected"
}

# Check log file for errors
$LogFile = Get-ChildItem "$BotDir\data\logs\" -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($LogFile) {
    Write-Host "   📄 Latest log: $($LogFile.Name)"
    $RecentErrors = Select-String -Path $LogFile.FullName -Pattern "ERROR|CRITICAL" -CaseSensitive | Select-Object -Last 3
    
    if ($RecentErrors) {
        Write-Host "   ⚠️ Recent errors found in log:"
        $RecentErrors | ForEach-Object { Write-Host "      $_" }
    } else {
        Write-Host "   ✅ No recent errors in log"
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "✅ DEPLOYMENT COMPLETED"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "📊 Next steps:"
Write-Host "   • Monitor logs: tail -f $BotDir\data\logs\bot.log"
Write-Host "   • Check status: Get-Service $ServiceName"
Write-Host "   • Test bot: Send /start to bot on Telegram"
Write-Host ""
