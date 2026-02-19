# ============================================================================
# Freedom Wallet Bot - VPS Initial Setup Script
# ============================================================================
# Description: One-time setup script for Windows Server 2016 VPS
# Usage: .\setup_vps.ps1 -GitRepo "https://github.com/mettatuan/freedom-wallet-bot.git"
# ============================================================================

param(
    [string]$GitRepo = "https://github.com/mettatuan/freedom-wallet-bot.git",
    [string]$InstallPath = "C:\FreedomWalletBot",
    [string]$PythonVersion = "3.10"
)

$ErrorActionPreference = "Stop"

function Write-Success { param($Message) Write-Host "[OK] $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Freedom Wallet Bot - VPS Setup (Windows Server 2016)      " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# 1. Check Prerequisites
# ============================================================================
Write-Info "Step 1/8: Checking prerequisites..."

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script must be run as Administrator. Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $pyVer = $matches[1]
        if ([double]$pyVer -ge [double]$PythonVersion) {
            Write-Success "Python is installed: $pythonVersion"
        } else {
            Write-Warning "Python $pyVer is installed, but $PythonVersion+ is recommended"
        }
    }
} catch {
    Write-Error "Python is not installed. Please install Python $PythonVersion+ from https://www.python.org/downloads/"
    exit 1
}

# ============================================================================
# 2. Check Installation Path
# ============================================================================
Write-Info ""
Write-Info "Step 2/8: Checking installation path..."

if (-not (Test-Path $InstallPath)) {
    Write-Error "Installation path not found: $InstallPath"
    Write-Info "This script should be run from the repository directory"
    exit 1
}

Set-Location $InstallPath
Write-Success "Using installation path: $InstallPath"

# ============================================================================
# 3. Create Virtual Environment
# ============================================================================
Write-Info ""
Write-Info "Step 3/8: Creating Python virtual environment..."

$venvPath = Join-Path $InstallPath ".venv"

if (Test-Path $venvPath) {
    Write-Warning "Virtual environment already exists"
} else {
    try {
        python -m venv .venv
        Write-Success "Virtual environment created"
    } catch {
        Write-Error "Failed to create virtual environment: $_"
        exit 1
    }
}

$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
try {
    & $activateScript
    Write-Success "Virtual environment activated"
} catch {
    Write-Error "Failed to activate virtual environment: $_"
    exit 1
}

# ============================================================================
# 4. Install Dependencies
# ============================================================================
Write-Info ""
Write-Info "Step 4/8: Installing Python dependencies..."

try {
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    Write-Success "Dependencies installed successfully"
} catch {
    Write-Error "Failed to install dependencies: $_"
    exit 1
}

# ============================================================================
# 5. Setup Environment Configuration
# ============================================================================
Write-Info ""
Write-Info "Step 5/8: Setting up environment configuration..."

$envFile = Join-Path $InstallPath ".env"

if (Test-Path $envFile) {
    Write-Warning ".env file already exists"
} else {
    $envExample = Join-Path $InstallPath ".env.example"
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Success "Created .env from .env.example"
    } else {
        $envContent = @"
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_user_id

# Database Configuration (SQLite by default)
DATABASE_URL=sqlite:///./data/bot.db

# Google Sheets (optional)
GOOGLE_CREDENTIALS_FILE=google_service_account.json

# Environment
ENVIRONMENT=production
DEBUG=False
"@
        Set-Content -Path $envFile -Value $envContent -Encoding UTF8
        Write-Success "Created default .env file"
    }
    
    Write-Warning "IMPORTANT: You must edit .env file with your actual credentials!"
    Write-Info "   Required: BOT_TOKEN, ADMIN_ID"
}

# ============================================================================
# 6. Create Required Directories
# ============================================================================
Write-Info ""
Write-Info "Step 6/8: Creating required directories..."

$directories = @("data", "logs", "media/uploads")

foreach ($dir in $directories) {
    $fullPath = Join-Path $InstallPath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Success "Created directory: $dir"
    }
}

# ============================================================================
# 7. Setup Database
# ============================================================================
Write-Info ""
Write-Info "Step 7/8: Setting up database..."

$dbPath = Join-Path $InstallPath "data\bot.db"
if (Test-Path $dbPath) {
    Write-Success "Database already exists"
} else {
    Write-Info "Database will be created on first run"
}

# ============================================================================
# 8. Test Bot Configuration
# ============================================================================
Write-Info ""
Write-Info "Step 8/8: Testing bot configuration..."

Write-Info "Running configuration check..."
try {
    $testCommand = "import sys; sys.path.insert(0, '.'); from config import config; print('OK')"
    $checkResult = python -c $testCommand 2>&1
    if ($checkResult -match "OK") {
        Write-Success "Configuration is valid"
    } else {
        Write-Warning "Configuration check returned: $checkResult"
    }
} catch {
    Write-Warning "Could not verify configuration: $_"
}

# ============================================================================
# Setup Complete
# ============================================================================
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "                    Setup Complete!                             " -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Edit .env file with your credentials:" -ForegroundColor White
Write-Host "     notepad $envFile" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Test the bot manually:" -ForegroundColor White
Write-Host "     cd $InstallPath" -ForegroundColor Yellow
Write-Host "     .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "     python main.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Setup Windows Service (auto-start on boot):" -ForegroundColor White
Write-Host "     .\scripts\deployment\setup_windows_service.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  4. For future updates, use the deployment script:" -ForegroundColor White
Write-Host "     .\scripts\deployment\deploy.ps1" -ForegroundColor Yellow
Write-Host ""

Write-Info "Installation Path: $InstallPath"
Write-Info "Virtual Environment: $venvPath"
Write-Info "Configuration File: $envFile"
Write-Host ""

exit 0
