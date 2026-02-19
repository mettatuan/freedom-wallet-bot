# ============================================
# VPS INITIAL SETUP SCRIPT
# ============================================
# First-time setup on Windows Server 2016 VPS
# Run this ONCE after cloning the repository
# ============================================

param(
    [string]$GitRepo = "https://github.com/mettatuan/FreedomWalletBot.git",
    [string]$InstallDir = "D:\FreedomWalletBot"
)

$ErrorActionPreference = "Stop"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "🚀 FREEDOMWALLETBOT VPS SETUP"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "📅 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!"
    exit 1
}

# ============================================
# STEP 1: Check prerequisites
# ============================================
Write-Host "[1/9] 🔍 Checking prerequisites..."

# Check Python
$Python = Get-Command python -ErrorAction SilentlyContinue

if (-not $Python) {
    Write-Host "❌ Python 3.10+ is required!"
    Write-Host "   Download from: https://www.python.org/downloads/"
    exit 1
}

$PythonVersion = python --version
Write-Host "   ✅ Python found: $PythonVersion"

# Check Git
$Git = Get-Command git -ErrorAction SilentlyContinue

if (-not $Git) {
    Write-Host "❌ Git is required!"
    Write-Host "   Download from: https://git-scm.com/download/win"
    exit 1
}

Write-Host "   ✅ Git found: $(git --version)"

# ============================================
# STEP 2: Clone repository (if not exists)
# ============================================
Write-Host ""
Write-Host "[2/9] 📥 Setting up repository..."

if (Test-Path $InstallDir) {
    Write-Host "   ⚠️ Directory already exists: $InstallDir"
    $response = Read-Host "   Delete and re-clone? (yes/no)"
    if ($response -eq "yes") {
        Remove-Item $InstallDir -Recurse -Force
        git clone $GitRepo $InstallDir
    } else {
        Write-Host "   ℹ️ Using existing directory"
    }
} else {
    Write-Host "   🔄 Cloning repository..."
    git clone $GitRepo $InstallDir
}

Set-Location $InstallDir
Write-Host "   ✅ Repository ready"

# ============================================
# STEP 3: Create virtual environment
# ============================================
Write-Host ""
Write-Host "[3/9] 🐍 Creating virtual environment..."

$VenvPath = "$InstallDir\.venv"

if (Test-Path $VenvPath) {
    Write-Host "   ℹ️ Virtual environment already exists"
} else {
    python -m venv .venv
    Write-Host "   ✅ Virtual environment created"
}

# Activate venv
& "$VenvPath\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "   🔄 Upgrading pip..."
python -m pip install --upgrade pip --quiet

# ============================================
# STEP 4: Install dependencies
# ============================================
Write-Host ""
Write-Host "[4/9] 📦 Installing dependencies..."

pip install -r requirements.txt
Write-Host "   ✅ Dependencies installed"

# ============================================
# STEP 5: Create required directories
# ============================================
Write-Host ""
Write-Host "[5/9] 📁 Creating directories..."

$Directories = @(
    "$InstallDir\data",
    "$InstallDir\data\logs",
    "$InstallDir\backups",
    "$InstallDir\backups\database"
)

foreach ($dir in $Directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "   ✅ Created: $dir"
    }
}

# ============================================
# STEP 6: Setup environment file
# ============================================
Write-Host ""
Write-Host "[6/9] ⚙️  Setting up environment configuration..."

$EnvFile = "$InstallDir\.env"

if (Test-Path $EnvFile) {
    Write-Host "   ⚠️ .env file already exists"
    $response = Read-Host "   Overwrite with production template? (yes/no)"
    if ($response -ne "yes") {
        Write-Host "   ℹ️ Keeping existing .env file"
    } else {
        Copy-Item "$InstallDir\.env.production" -Destination $EnvFile
        Write-Host "   ✅ Copied .env.production to .env"
    }
} else {
    Copy-Item "$InstallDir\.env.production" -Destination $EnvFile
    Write-Host "   ✅ Created .env from template"
}

Write-Host ""
Write-Host "   ⚠️ IMPORTANT: Edit .env file with your credentials!"
Write-Host "      Required: TELEGRAM_BOT_TOKEN, DATABASE_URL, etc."
notepad $EnvFile

# ============================================
# STEP 7: Setup PostgreSQL (optional)
# ============================================
Write-Host ""
Write-Host "[7/9] 🗄️  PostgreSQL setup..."

$response = Read-Host "   Install PostgreSQL now? (yes/no)"

if ($response -eq "yes") {
    Write-Host "   ℹ️ Please install PostgreSQL manually:"
    Write-Host "      1. Download: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads"
    Write-Host "      2. Install with default settings (Port 5432)"
    Write-Host "      3. Remember the password you set!"
    Write-Host ""
    Write-Host "   After installation, run:"
    Write-Host "      psql -U postgres"
    Write-Host "      CREATE DATABASE freedomwalletdb;"
    Write-Host "      CREATE USER freedomwallet WITH PASSWORD 'your-password';"
    Write-Host "      GRANT ALL PRIVILEGES ON DATABASE freedomwalletdb TO freedomwallet;"
    Write-Host ""
    Pause
} else {
    Write-Host "   ℹ️ Skipped PostgreSQL setup"
    Write-Host "      Using SQLite (not recommended for production)"
}

# ============================================
# STEP 8: Setup Windows Firewall (optional)
# ============================================
Write-Host ""
Write-Host "[8/9] 🔥 Firewall configuration..."

$response = Read-Host "   Configure Windows Firewall? (yes/no)"

if ($response -eq "yes") {
    # Allow PostgreSQL
    try {
        New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow -ErrorAction SilentlyContinue
        Write-Host "   ✅ PostgreSQL port (5432) allowed"
    } catch {
        Write-Host "   ℹ️ Firewall rule may already exist"
    }
    
    Write-Host "   ✅ Firewall configured"
} else {
    Write-Host "   ℹ️ Skipped firewall configuration"
}

# ============================================
# STEP 9: Setup scheduled tasks (backup)
# ============================================
Write-Host ""
Write-Host "[9/9] ⏰ Setting up scheduled backup..."

$response = Read-Host "   Create daily backup task? (yes/no)"

if ($response -eq "yes") {
    $TaskName = "FreedomWalletBot-DailyBackup"
    $TaskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$InstallDir\scripts\backup_database.ps1`""
    $TaskTrigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"
    $TaskPrincipal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    $TaskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    try {
        Register-ScheduledTask -TaskName $TaskName -Action $TaskAction -Trigger $TaskTrigger -Principal $TaskPrincipal -Settings $TaskSettings -Force | Out-Null
        Write-Host "   ✅ Daily backup scheduled for 2:00 AM"
    } catch {
        Write-Host "   ⚠️ Failed to create scheduled task: $_"
    }
} else {
    Write-Host "   ℹ️ Skipped backup task setup"
}

# ============================================
# COMPLETION
# ============================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "✅ VPS SETUP COMPLETED"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "📋 NEXT STEPS:"
Write-Host ""
Write-Host "1️⃣  Edit .env file with your credentials"
Write-Host "    File: $InstallDir\.env"
Write-Host ""
Write-Host "2️⃣  Test the bot manually:"
Write-Host "    cd $InstallDir"
Write-Host "    & .venv\Scripts\Activate.ps1"
Write-Host "    python main.py"
Write-Host ""
Write-Host "3️⃣  If bot works, setup as Windows Service:"
Write-Host "    .\scripts\setup_windows_service.ps1"
Write-Host ""
Write-Host "4️⃣  To deploy updates in future:"
Write-Host "    .\scripts\deploy.ps1"
Write-Host ""
Write-Host "📚 Documentation:"
Write-Host "    • Database migration: docs\DATABASE_MIGRATION.md"
Write-Host "    • Deployment guide: docs\DEPLOYMENT.md"
Write-Host ""
