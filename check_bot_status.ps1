#!/usr/bin/env pwsh
# Quick script to check FreedomWallet Bot service status

$ServiceName = "FreedomWalletBot"
$LogDir = "C:\FreedomWalletBot\logs"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  FreedomWallet Bot - Status Check" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check service
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service) {
    Write-Host "🔵 Service Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
    Write-Host ""
} else {
    Write-Host "❌ Service not installed!" -ForegroundColor Red
    Write-Host "Run: .\setup_windows_service.ps1" -ForegroundColor Yellow
    exit 1
}

# Check Python processes
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "✅ Bot Processes Running:" -ForegroundColor Green
    $pythonProcs | Select-Object Id,SessionId,StartTime,@{Name="Memory(MB)";Expression={[math]::Round($_.WorkingSet/1MB,2)}} | Format-Table
    
    $session0 = $pythonProcs | Where-Object { $_.SessionId -eq 0 }
    if ($session0) {
        Write-Host "✅ Running in Session 0 (System Service)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Not in Session 0!" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ No bot process found!" -ForegroundColor Red
}

Write-Host ""

# Show recent logs
if (Test-Path "$LogDir\service_stderr.log") {
    Write-Host "📋 Recent Logs (last 15 lines):" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────" -ForegroundColor Gray
    Get-Content "$LogDir\service_stderr.log" -Tail 15
} else {
    Write-Host "⚠️  No logs found at $LogDir\service_stderr.log" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "  Restart: C:\nssm\nssm.exe restart $ServiceName" -ForegroundColor White
Write-Host "  Stop:    C:\nssm\nssm.exe stop $ServiceName" -ForegroundColor White
Write-Host "  Logs:    Get-Content $LogDir\service_stderr.log -Tail 50 -Wait" -ForegroundColor White
Write-Host ""
