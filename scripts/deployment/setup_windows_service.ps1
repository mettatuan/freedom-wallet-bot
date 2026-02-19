# ============================================================================
# Freedom Wallet Bot - Windows Service Setup (NSSM)
# ============================================================================
# Description: Install bot as Windows Service using NSSM
# Usage: .\setup_windows_service.ps1
# ============================================================================

param(
    [string]$InstallPath = "C:\FreedomWalletBot",
    [string]$ServiceName = "FreedomWalletBot",
    [string]$ServiceDisplayName = "Freedom Wallet Telegram Bot",
    [string]$NssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
)

$ErrorActionPreference = "Stop"

# Color output
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        Freedom Wallet Bot - Windows Service Setup              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

# Change to installation directory
Set-Location $InstallPath

# ============================================================================
# 1. Check/Install NSSM
# ============================================================================
Write-Info "Step 1/5: Checking NSSM (Non-Sucking Service Manager)..."

$nssmPath = "C:\nssm\nssm.exe"
$nssmDir = "C:\nssm"

if (Test-Path $nssmPath) {
    Write-Success "NSSM already installed at $nssmPath"
} else {
    Write-Info "Downloading NSSM..."
    
    $tempZip = "$env:TEMP\nssm.zip"
    $tempExtract = "$env:TEMP\nssm_extract"
    
    try {
        # Download NSSM
        Invoke-WebRequest -Uri $NssmUrl -OutFile $tempZip -UseBasicParsing
        Write-Success "Downloaded NSSM"
        
        # Extract
        Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force
        
        # Copy appropriate version (64-bit)
        $sourceNssm = Get-ChildItem -Path $tempExtract -Filter "nssm.exe" -Recurse | 
                      Where-Object { $_.FullName -like "*win64*" } | 
                      Select-Object -First 1
        
        if ($sourceNssm) {
            New-Item -ItemType Directory -Path $nssmDir -Force | Out-Null
            Copy-Item -Path $sourceNssm.FullName -Destination $nssmPath -Force
            Write-Success "NSSM installed to $nssmPath"
        } else {
            Write-Error "Could not find NSSM executable in download"
            exit 1
        }
        
        # Cleanup
        Remove-Item $tempZip -Force -ErrorAction SilentlyContinue
        Remove-Item $tempExtract -Recurse -Force -ErrorAction SilentlyContinue
        
    } catch {
        Write-Error "Failed to download/install NSSM: $_"
        Write-Info "Please download manually from https://nssm.cc/download"
        exit 1
    }
}

# ============================================================================
# 2. Check if Service Already Exists
# ============================================================================
Write-Info "`nStep 2/5: Checking for existing service..."

$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue

if ($existingService) {
    Write-Warning "Service '$ServiceName' already exists"
    $response = Read-Host "Remove and recreate? (y/N)"
    
    if ($response -eq 'y') {
        # Stop service if running
        if ($existingService.Status -eq 'Running') {
            Write-Info "Stopping service..."
            Stop-Service -Name $ServiceName -Force
            Start-Sleep -Seconds 3
        }
        
        # Remove service
        Write-Info "Removing existing service..."
        & $nssmPath remove $ServiceName confirm
        Start-Sleep -Seconds 2
        Write-Success "Existing service removed"
    } else {
        Write-Info "Keeping existing service. Exiting..."
        exit 0
    }
}

# ============================================================================
# 3. Prepare Service Configuration
# ============================================================================
Write-Info "`nStep 3/5: Preparing service configuration..."

# Find Python executable in venv
$pythonExe = Join-Path $InstallPath ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Error "Python not found in virtual environment: $pythonExe"
    Write-Info "Run setup_vps.ps1 first to create virtual environment"
    exit 1
}

# Find main.py
$mainPy = Join-Path $InstallPath "main.py"
if (-not (Test-Path $mainPy)) {
    Write-Error "main.py not found: $mainPy"
    exit 1
}

Write-Success "Python: $pythonExe"
Write-Success "Script: $mainPy"

# ============================================================================
# 4. Install Service
# ============================================================================
Write-Info "`nStep 4/5: Installing Windows Service..."

try {
    # Install service
    & $nssmPath install $ServiceName $pythonExe $mainPy
    
    # Configure service
    & $nssmPath set $ServiceName DisplayName $ServiceDisplayName
    & $nssmPath set $ServiceName Description "Telegram bot for Freedom Wallet expense tracking"
    & $nssmPath set $ServiceName Start SERVICE_AUTO_START
    
    # Set working directory
    & $nssmPath set $ServiceName AppDirectory $InstallPath
    
    # Set up logging
    $logDir = Join-Path $InstallPath "logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    $stdoutLog = Join-Path $logDir "service_stdout.log"
    $stderrLog = Join-Path $logDir "service_stderr.log"
    
    & $nssmPath set $ServiceName AppStdout $stdoutLog
    & $nssmPath set $ServiceName AppStderr $stderrLog
    
    # Rotate logs (10MB limit)
    & $nssmPath set $ServiceName AppRotateFiles 1
    & $nssmPath set $ServiceName AppRotateBytes 10485760  # 10MB
    
    # Restart on failure
    & $nssmPath set $ServiceName AppExit Default Restart
    & $nssmPath set $ServiceName AppRestartDelay 10000  # 10 seconds
    
    Write-Success "Service installed successfully"
    
} catch {
    Write-Error "Failed to install service: $_"
    exit 1
}

# ============================================================================
# 5. Start Service
# ============================================================================
Write-Info "`nStep 5/5: Starting service..."

try {
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 5
    
    $service = Get-Service -Name $ServiceName
    
    if ($service.Status -eq 'Running') {
        Write-Success "Service started successfully!"
    } else {
        Write-Warning "Service status: $($service.Status)"
        Write-Info "Check logs at: $logDir"
    }
    
} catch {
    Write-Error "Failed to start service: $_"
    Write-Info "Check logs at: $logDir"
    exit 1
}

# ============================================================================
# Service Setup Complete
# ============================================================================
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║            Windows Service Setup Complete! ✓                   ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Service Information:" -ForegroundColor Cyan
Write-Host "  • Service Name: $ServiceName" -ForegroundColor White
Write-Host "  • Display Name: $ServiceDisplayName" -ForegroundColor White
Write-Host "  • Status: $($service.Status)" -ForegroundColor Green
Write-Host "  • Startup Type: Automatic" -ForegroundColor White
Write-Host "  • Log Files: $logDir" -ForegroundColor White
Write-Host ""

Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  • View status:  Get-Service $ServiceName | Format-List" -ForegroundColor Yellow
Write-Host "  • Stop service: Stop-Service $ServiceName" -ForegroundColor Yellow
Write-Host "  • Start service: Start-Service $ServiceName" -ForegroundColor Yellow
Write-Host "  • View logs:   .\\scripts\\deployment\\view_logs.ps1" -ForegroundColor Yellow
Write-Host "  • Restart bot: Restart-Service $ServiceName" -ForegroundColor Yellow
Write-Host ""

Write-Info "The bot will now start automatically when Windows boots!"
Write-Host ""

exit 0
