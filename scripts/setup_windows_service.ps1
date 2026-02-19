# ============================================
# WINDOWS SERVICE SETUP SCRIPT
# ============================================
# Configure FreedomWalletBot as Windows Service using NSSM
# ============================================

param(
    [switch]$Uninstall = $false
)

$ErrorActionPreference = "Stop"
$ServiceName = "FreedomWalletBot"
$BotDir = "D:\FreedomWalletBot"
$VenvPath = "$BotDir\.venv"
$PythonExe = "$VenvPath\Scripts\python.exe"
$MainScript = "$BotDir\main.py"
$LogFile = "$BotDir\data\logs\service.log"
$NssmExe = "$BotDir\scripts\nssm.exe"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "⚙️  WINDOWS SERVICE CONFIGURATION"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# ============================================
# Check prerequisites
# ============================================
Write-Host "[1/5] 🔍 Checking prerequisites..."

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator!"
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'"
    exit 1
}

# Check if NSSM exists
if (-not (Test-Path $NssmExe)) {
    Write-Host "⚠️ NSSM not found. Downloading..."
    
    $NssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $TempZip = "$env:TEMP\nssm.zip"
    $TempDir = "$env:TEMP\nssm"
    
    try {
        # Download NSSM
        Invoke-WebRequest -Uri $NssmUrl -OutFile $TempZip
        
        # Extract
        Expand-Archive -Path $TempZip -DestinationPath $TempDir -Force
        
        # Copy appropriate version (64-bit)
        $NssmSource = "$TempDir\nssm-2.24\win64\nssm.exe"
        Copy-Item $NssmSource -Destination $NssmExe
        
        # Cleanup
        Remove-Item $TempZip, $TempDir -Recurse -Force
        
        Write-Host "   ✅ NSSM downloaded successfully"
    } catch {
        Write-Host "❌ Failed to download NSSM: $_"
        Write-Host "   Please download manually from: https://nssm.cc/download"
        Write-Host "   Extract nssm.exe to: $BotDir\scripts\"
        exit 1
    }
}

# Check Python and main.py
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Python not found at: $PythonExe"
    Write-Host "   Run setup_vps.ps1 first to create virtual environment"
    exit 1
}

if (-not (Test-Path $MainScript)) {
    Write-Host "❌ main.py not found at: $MainScript"
    exit 1
}

Write-Host "   ✅ All prerequisites met"

# ============================================
# Uninstall service (if requested)
# ============================================
if ($Uninstall) {
    Write-Host ""
    Write-Host "[2/5] 🗑️  Uninstalling service..."
    
    $ExistingService = Get-Service $ServiceName -ErrorAction SilentlyContinue
    
    if ($ExistingService) {
        # Stop service if running
        if ($ExistingService.Status -eq "Running") {
            Write-Host "   🛑 Stopping service..."
            Stop-Service $ServiceName -Force
        }
        
        # Remove service
        & $NssmExe remove $ServiceName confirm
        Write-Host "   ✅ Service uninstalled"
    } else {
        Write-Host "   ℹ️ Service not found"
    }
    
    exit 0
}

# ============================================
# Install/Update service
# ============================================
Write-Host ""
Write-Host "[2/5] 📦 Installing service..."

$ExistingService = Get-Service $ServiceName -ErrorAction SilentlyContinue

if ($ExistingService) {
    Write-Host "   ⚠️ Service already exists. Updating configuration..."
    
    # Stop service
    if ($ExistingService.Status -eq "Running") {
        Stop-Service $ServiceName -Force
        Start-Sleep -Seconds 2
    }
    
    # Remove old service
    & $NssmExe remove $ServiceName confirm
    Start-Sleep -Seconds 1
}

# Install service
& $NssmExe install $ServiceName $PythonExe $MainScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Service installation failed!"
    exit 1
}

Write-Host "   ✅ Service installed"

# ============================================
# Configure service
# ============================================
Write-Host ""
Write-Host "[3/5] ⚙️  Configuring service..."

# Set working directory
& $NssmExe set $ServiceName AppDirectory $BotDir

# Set service description
& $NssmExe set $ServiceName Description "Freedom Wallet Telegram Bot - 24/7 Customer Support"

# Set display name
& $NssmExe set $ServiceName DisplayName "Freedom Wallet Bot"

# Set startup type to automatic
& $NssmExe set $ServiceName Start SERVICE_AUTO_START

# Configure restart on failure
& $NssmExe set $ServiceName AppThrottle 1500  # Wait 1.5s before restart
& $NssmExe set $ServiceName AppRestartDelay 5000  # Wait 5s between restarts
& $NssmExe set $ServiceName AppExit Default Restart  # Restart on any exit

# Set environment variable for production
& $NssmExe set $ServiceName AppEnvironmentExtra ENV=production

# Configure logging
& $NssmExe set $ServiceName AppStdout $LogFile
& $NssmExe set $ServiceName AppStderr $LogFile

# Rotate logs (10MB max)
& $NssmExe set $ServiceName AppStdoutCreationDisposition 4
& $NssmExe set $ServiceName AppStderrCreationDisposition 4
& $NssmExe set $ServiceName AppRotateFiles 1
& $NssmExe set $ServiceName AppRotateOnline 1
& $NssmExe set $ServiceName AppRotateBytes 10485760  # 10MB

Write-Host "   ✅ Service configured"

# ============================================
# Start service
# ============================================
Write-Host ""
Write-Host "[4/5] ▶️  Starting service..."

Start-Service $ServiceName
Start-Sleep -Seconds 3

$Service = Get-Service $ServiceName

if ($Service.Status -eq "Running") {
    Write-Host "   ✅ Service started successfully"
} else {
    Write-Host "   ❌ Service failed to start!"
    Write-Host "   Status: $($Service.Status)"
    Write-Host "   Check logs: $LogFile"
    exit 1
}

# ============================================
# Verify installation
# ============================================
Write-Host ""
Write-Host "[5/5] 🔍 Verifying installation..."

# Check service status
$Service = Get-Service $ServiceName
Write-Host "   📊 Service Status: $($Service.Status)"
Write-Host "   📊 Startup Type: $($Service.StartType)"

# Check if process is running
Start-Sleep -Seconds 2
$Process = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $PythonExe }

if ($Process) {
    Write-Host "   ✅ Bot process is running (PID: $($Process.Id))"
    Write-Host "   📊 Memory: $([math]::Round($Process.WorkingSet64 / 1MB, 2)) MB"
} else {
    Write-Host "   ⚠️ Bot process not detected yet (may still be starting...)"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "✅ WINDOWS SERVICE SETUP COMPLETE"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "📋 Service Management Commands:"
Write-Host "   Start:   Start-Service $ServiceName"
Write-Host "   Stop:    Stop-Service $ServiceName"
Write-Host "   Restart: Restart-Service $ServiceName"
Write-Host "   Status:  Get-Service $ServiceName"
Write-Host "   Logs:    Get-Content $LogFile -Tail 50 -Wait"
Write-Host ""
Write-Host "🔧 Advanced Management:"
Write-Host "   Edit:    & '$NssmExe' edit $ServiceName"
Write-Host "   Remove:  & '$NssmExe' remove $ServiceName"
Write-Host ""
Write-Host "✅ The bot will now:"
Write-Host "   • Start automatically on server boot"
Write-Host "   • Restart automatically if it crashes"
Write-Host "   • Log to: $LogFile"
Write-Host ""
