# register_bot_task.ps1
# Creates a Windows Scheduled Task that runs the bot as SYSTEM
# with the correct working directory, surviving RDP disconnects

$TaskName = "FreedomWalletBot"
$BotDir   = "C:\FreedomWalletBot"
$Python   = "C:\FreedomWalletBot\.venv\Scripts\python.exe"
$Script   = "main.py"

Write-Host "Unregistering old task (if any)..."
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Write-Host "Creating stdout/stderr wrapper..."
$WrapperPath = "$BotDir\run_bot_log.bat"
@"
@echo off
cd /d $BotDir
:: Kill any stale python bot processes before starting
taskkill /F /IM python.exe >nul 2>&1
:: Remove stale PID lock if present
if exist "$BotDir\bot.pid" del /f "$BotDir\bot.pid"
:: Start bot with all output captured
"$Python" $Script > "$BotDir\boot_stdout.log" 2>&1
"@ | Set-Content -Path $WrapperPath -Encoding ASCII

Write-Host "Creating scheduled task action..."
$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$WrapperPath`"" `
    -WorkingDirectory $BotDir

Write-Host "Creating trigger (at system startup)..."
$Trigger = New-ScheduledTaskTrigger -AtStartup

Write-Host "Setting principal (SYSTEM, highest privilege)..."
$Principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -RunLevel Highest

Write-Host "Registering task..."
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Principal $Principal `
    -Description "Freedom Wallet Telegram Bot - auto-start as SYSTEM" `
    -Force

Write-Host "Starting task now..."
Start-ScheduledTask -TaskName $TaskName

Write-Host "Waiting 8 seconds for bot to start..."
Start-Sleep 8

Write-Host "Process check:"
$procs = Get-Process python -ErrorAction SilentlyContinue
if ($procs) {
    $procs | Format-Table Id, SessionId, WorkingSet -AutoSize
    Write-Host "SUCCESS: Bot is running (Session 0 = Services = persistent)" -ForegroundColor Green
} else {
    Write-Host "WARNING: python.exe not found in process list" -ForegroundColor Yellow
    Write-Host "Checking bot log for errors..."
    if (Test-Path "$BotDir\data\logs\bot.log") {
        Get-Content "$BotDir\data\logs\bot.log" -Tail 20
    } else {
        Write-Host "No bot.log found. Bot likely crashed before logging."
    }
    if (Test-Path "$BotDir\boot_stdout.log") {
        Write-Host "boot_stdout.log content:"
        Get-Content "$BotDir\boot_stdout.log" -Tail 30
    }
}
