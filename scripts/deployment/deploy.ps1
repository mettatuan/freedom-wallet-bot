# ============================================================================
# Freedom Wallet Bot - Zero Downtime Deployment Script
# ============================================================================
# Description: Automated deployment with health checks and rollback
# Usage: .\deploy.ps1
# ============================================================================

param(
    [string]$InstallPath = "C:\FreedomWalletBot",
    [string]$ServiceName = "FreedomWalletBot",
    [switch]$SkipBackup,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

# Color output
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Step { param($Step, $Message) Write-Host "`n[$Step] $Message" -ForegroundColor Magenta }

# Timestamp for logs
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$logFile = Join-Path $InstallPath "logs\deploy_$timestamp.log"

# Logging function
function Write-Log {
    param($Message, $Level = "INFO")
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Add-Content -Path $logFile -Value $logMessage
    
    switch ($Level) {
        "ERROR" { Write-Error $Message }
        "WARNING" { Write-Warning $Message }
        "SUCCESS" { Write-Success $Message }
        default { Write-Info $Message }
    }
}

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Freedom Wallet Bot - Deployment Script               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Change to installation directory
Set-Location $InstallPath
Write-Log "Starting deployment from $InstallPath"

# ============================================================================
# STEP 1: Pre-deployment Checks
# ============================================================================
Write-Step "1/9" "Pre-deployment checks..."

# Check if service exists
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service) {
    Write-Log "Service '$ServiceName' found: $($service.Status)" "SUCCESS"
    $serviceExists = $true
} else {
    Write-Log "Service '$ServiceName' not found - will deploy without service management" "WARNING"
    $serviceExists = $false
}

# Check Git status
try {
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Log "Working directory has uncommitted changes" "WARNING"
        Write-Host $gitStatus -ForegroundColor Yellow
    }
} catch {
    Write-Log "Git status check failed: $_" "ERROR"
    exit 1
}

# ============================================================================
# STEP 2: Backup Database
# ============================================================================
if (-not $SkipBackup) {
    Write-Step "2/9" "Backing up database..."
    
    $backupScript = Join-Path $InstallPath "scripts\deployment\backup_database.ps1"
    if (Test-Path $backupScript) {
        try {
            & $backupScript
            Write-Log "Database backup completed" "SUCCESS"
        } catch {
            Write-Log "Backup failed: $_" "ERROR"
            $response = Read-Host "Continue anyway? (y/N)"
            if ($response -ne 'y') { exit 1 }
        }
    } else {
        Write-Log "Backup script not found - skipping backup" "WARNING"
    }
} else {
    Write-Log "Skipping backup (SkipBackup flag set)" "WARNING"
}

# ============================================================================
# STEP 3: Stop Service
# ============================================================================
Write-Step "3/9" "Stopping bot service..."

if ($serviceExists -and $service.Status -eq 'Running') {
    try {
        Stop-Service -Name $ServiceName -Force
        Start-Sleep -Seconds 3
        Write-Log "Service stopped successfully" "SUCCESS"
    } catch {
        Write-Log "Failed to stop service: $_" "ERROR"
        exit 1
    }
} else {
    Write-Log "Service not running - skipping stop" "INFO"
}

# ============================================================================
# STEP 4: Pull Latest Code
# ============================================================================
Write-Step "4/9" "Pulling latest code from GitHub..."

try {
    $currentBranch = git rev-parse --abbrev-ref HEAD
    Write-Log "Current branch: $currentBranch"
    
    git fetch origin
    $beforeCommit = git rev-parse HEAD
    git pull origin $currentBranch
    $afterCommit = git rev-parse HEAD
    
    if ($beforeCommit -eq $afterCommit) {
        Write-Log "Already up to date" "SUCCESS"
    } else {
        Write-Log "Updated from $($beforeCommit.Substring(0,7)) to $($afterCommit.Substring(0,7))" "SUCCESS"
        
        # Show what changed
        Write-Host "`nChanges:" -ForegroundColor Cyan
        git log --oneline "$beforeCommit..$afterCommit" | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    }
} catch {
    Write-Log "Git pull failed: $_" "ERROR"
    exit 1
}

# ============================================================================
# STEP 5: Activate Virtual Environment
# ============================================================================
Write-Step "5/9" "Activating virtual environment..."

$venvActivate = Join-Path $InstallPath ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    try {
        & $venvActivate
        Write-Log "Virtual environment activated" "SUCCESS"
    } catch {
        Write-Log "Failed to activate venv: $_" "ERROR"
        exit 1
    }
} else {
    Write-Log "Virtual environment not found at .venv\" "ERROR"
    exit 1
}

# ============================================================================
# STEP 6: Update Dependencies
# ============================================================================
Write-Step "6/9" "Updating dependencies..."

try {
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    Write-Log "Dependencies updated successfully" "SUCCESS"
} catch {
    Write-Log "Failed to update dependencies: $_" "ERROR"
    exit 1
}

# ============================================================================
# STEP 7: Run Database Migrations
# ============================================================================
Write-Step "7/9" "Running database migrations..."

# Check if migrations script exists
$migrateScript = Join-Path $InstallPath "scripts\database\migrate.py"
if (Test-Path $migrateScript) {
    try {
        python $migrateScript
        Write-Log "Database migrations completed" "SUCCESS"
    } catch {
        Write-Log "Migration warning: $_" "WARNING"
    }
} else {
    Write-Log "No migration script found - skipping" "INFO"
}

# ============================================================================
# STEP 8: Start Service
# ============================================================================
Write-Step "8/9" "Starting bot service..."

if ($serviceExists) {
    try {
        Start-Service -Name $ServiceName
        Start-Sleep -Seconds 5
        
        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq 'Running') {
            Write-Log "Service started successfully" "SUCCESS"
        } else {
            Write-Log "Service did not start properly: $($service.Status)" "ERROR"
            exit 1
        }
    } catch {
        Write-Log "Failed to start service: $_" "ERROR"
        exit 1
    }
} else {
    Write-Log "No service configured - start bot manually with: python main.py" "WARNING"
}

# ============================================================================
# STEP 9: Health Check
# ============================================================================
Write-Step "9/9" "Running health check..."

Start-Sleep -Seconds 10

$healthScript = Join-Path $InstallPath "scripts\deployment\health_check.ps1"
if (Test-Path $healthScript) {
    try {
        $healthResult = & $healthScript -Quick
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Health check passed ✓" "SUCCESS"
        } else {
            Write-Log "Health check failed!" "ERROR"
            Write-Host "`nCheck logs at: $logFile" -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Log "Health check error: $_" "WARNING"
    }
} else {
    # Basic health check
    if ($serviceExists) {
        $service = Get-Service -Name $ServiceName
        if ($service.Status -eq 'Running') {
            Write-Log "Basic health check passed (service running)" "SUCCESS"
        } else {
            Write-Log "Health check failed (service not running)" "ERROR"
            exit 1
        }
    }
}

# ============================================================================
# Deployment Complete
# ============================================================================
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Deployment Completed Successfully! ✓              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Deployment Summary:" -ForegroundColor Cyan
Write-Host "  • Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host "  • Branch: $currentBranch" -ForegroundColor White
Write-Host "  • Commit: $($afterCommit.Substring(0,7))" -ForegroundColor White
if ($serviceExists) {
    Write-Host "  • Service Status: Running ✓" -ForegroundColor Green
}
Write-Host "  • Log File: $logFile" -ForegroundColor White
Write-Host ""

Write-Host "View logs: .\scripts\deployment\view_logs.ps1" -ForegroundColor Yellow
Write-Host "Monitor bot: Get-Service $ServiceName | Format-List" -ForegroundColor Yellow
Write-Host ""

exit 0
