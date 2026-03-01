# FreedomWallet Bot - Windows Service Setup
# Run as Administrator

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  FreedomWallet Bot - Service Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$ServiceName = "FreedomWalletBot"
$BotPath = "C:\FreedomWalletBot"
$PythonExe = "$BotPath\.venv\Scripts\python.exe"
$MainScript = "$BotPath\main.py"
$NSSMPath = "C:\nssm"
$LogDir = "$BotPath\logs"

# Step 1: Stop Python processes
Write-Host "Step 1: Stopping Python processes..." -ForegroundColor Yellow
$procs = Get-Process python -ErrorAction SilentlyContinue
if ($procs) {
    Stop-Process -Name python -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  Stopped $($procs.Count) process(es)" -ForegroundColor Green
} else {
    Write-Host "  No processes to stop" -ForegroundColor Green
}
Write-Host ""

# Step 2: Install NSSM
Write-Host "Step 2: Installing NSSM..." -ForegroundColor Yellow
if (Test-Path "$NSSMPath\nssm.exe") {
    Write-Host "  Already installed" -ForegroundColor Green
} else {
    Write-Host "  Downloading..." -ForegroundColor Yellow
    
    # Enable TLS 1.2 for older Windows Server
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    
    try {
        $nssmZip = "$env:TEMP\nssm.zip"
        Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile $nssmZip -UseBasicParsing
        Expand-Archive -Path $nssmZip -DestinationPath $env:TEMP -Force
        New-Item -ItemType Directory -Path $NSSMPath -Force | Out-Null
        Copy-Item "$env:TEMP\nssm-2.24\win64\nssm.exe" -Destination "$NSSMPath\nssm.exe" -Force
        Remove-Item $nssmZip -Force -ErrorAction SilentlyContinue
        Write-Host "  Installed" -ForegroundColor Green
    } catch {
        Write-Host "  ERROR: Download failed" -ForegroundColor Red
        Write-Host "  Please download manually from: https://nssm.cc/download" -ForegroundColor Yellow
        Write-Host "  Extract nssm.exe to: $NSSMPath\nssm.exe" -ForegroundColor Yellow
        Write-Host "  Then run this script again." -ForegroundColor Yellow
        exit 1
    }
}
Write-Host ""

# Step 3: Create log directory
Write-Host "Step 3: Creating logs..." -ForegroundColor Yellow
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
Write-Host "  Done" -ForegroundColor Green
Write-Host ""

# Step 4: Remove existing service
Write-Host "Step 4: Removing old service..." -ForegroundColor Yellow
$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existing) {
    & "$NSSMPath\nssm.exe" stop $ServiceName 2>$null
    Start-Sleep -Seconds 2
    & "$NSSMPath\nssm.exe" remove $ServiceName confirm
    Start-Sleep -Seconds 2
    Write-Host "  Removed" -ForegroundColor Green
} else {
    Write-Host "  No old service" -ForegroundColor Green
}
Write-Host ""

# Step 5: Verify files
Write-Host "Step 5: Verifying files..." -ForegroundColor Yellow
if (!(Test-Path $PythonExe)) {
    Write-Host "  ERROR: Python not found at $PythonExe" -ForegroundColor Red
    exit 1
}
if (!(Test-Path $MainScript)) {
    Write-Host "  ERROR: main.py not found at $MainScript" -ForegroundColor Red
    exit 1
}
Write-Host "  Files OK" -ForegroundColor Green
Write-Host ""

# Step 6: Install service
Write-Host "Step 6: Installing service..." -ForegroundColor Yellow
& "$NSSMPath\nssm.exe" install $ServiceName $PythonExe $MainScript
& "$NSSMPath\nssm.exe" set $ServiceName AppDirectory $BotPath
& "$NSSMPath\nssm.exe" set $ServiceName DisplayName "Freedom Wallet Bot"
& "$NSSMPath\nssm.exe" set $ServiceName Description "Telegram bot for Freedom Wallet"
& "$NSSMPath\nssm.exe" set $ServiceName Start SERVICE_AUTO_START
& "$NSSMPath\nssm.exe" set $ServiceName AppEnvironmentExtra "PYTHONPATH=$BotPath"
& "$NSSMPath\nssm.exe" set $ServiceName AppStdout "$LogDir\service_stdout.log"
& "$NSSMPath\nssm.exe" set $ServiceName AppStderr "$LogDir\service_stderr.log"
& "$NSSMPath\nssm.exe" set $ServiceName AppExit Default Restart
& "$NSSMPath\nssm.exe" set $ServiceName AppRestartDelay 5000
& "$NSSMPath\nssm.exe" set $ServiceName AppRotateFiles 1
& "$NSSMPath\nssm.exe" set $ServiceName AppRotateOnline 1
& "$NSSMPath\nssm.exe" set $ServiceName AppRotateSeconds 86400
Write-Host "  Installed" -ForegroundColor Green
Write-Host ""

# Step 7: Start service
Write-Host "Step 7: Starting service..." -ForegroundColor Yellow
& "$NSSMPath\nssm.exe" start $ServiceName
Start-Sleep -Seconds 5
$service = Get-Service -Name $ServiceName
Write-Host "  Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") {"Green"} else {"Red"})
Write-Host ""

# Step 8: Verify
Write-Host "Step 8: Verifying..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
$procs = Get-Process python -ErrorAction SilentlyContinue
if ($procs) {
    Write-Host "  Bot is running!" -ForegroundColor Green
    $procs | Select-Object Id,SessionId,StartTime | Format-Table
    $session0 = $procs | Where-Object {$_.SessionId -eq 0}
    if ($session0) {
        Write-Host "  Running in Session 0 (System Service)" -ForegroundColor Green
    } else {
        Write-Host "  WARNING: Not in Session 0" -ForegroundColor Yellow
    }
} else {
    Write-Host "  WARNING: No Python process found" -ForegroundColor Yellow
    Write-Host "  Check logs: $LogDir\service_stderr.log" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service: $ServiceName" -ForegroundColor White
Write-Host "Status: $($service.Status)" -ForegroundColor Green
Write-Host ""
Write-Host "Commands:" -ForegroundColor Yellow
Write-Host "  Check:   Get-Service $ServiceName" -ForegroundColor White
Write-Host "  Stop:    C:\nssm\nssm.exe stop $ServiceName" -ForegroundColor White
Write-Host "  Start:   C:\nssm\nssm.exe start $ServiceName" -ForegroundColor White
Write-Host "  Restart: C:\nssm\nssm.exe restart $ServiceName" -ForegroundColor White
Write-Host "  Logs:    Get-Content $LogDir\service_stderr.log -Tail 50" -ForegroundColor White
Write-Host ""
