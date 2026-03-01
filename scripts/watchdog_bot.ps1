# ====================================================================
# Bot Watchdog Service - Tự Động Restart Bot Khi Crash
# ====================================================================
# 
# Chức năng:
#   1. Kiểm tra bot có đang chạy không (mỗi 30s)
#   2. Nếu bot crash → tự động restart
#   3. Kiểm tra restart flag từ auto-fix (Event Loop closed)
#   4. Ghi log mỗi lần restart
#   5. Alert admin nếu restart > 3 lần/10 phút
#
# Cài đặt:
#   1. Run script này trong background terminal
#   2. Hoặc tạo Windows Scheduled Task chạy at startup
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File watchdog_bot.ps1
# ====================================================================

param(
    [int]$CheckIntervalSeconds = 30,
    [int]$MaxRestartsPerWindow = 3,
    [int]$RestartWindowMinutes = 10,
    [string]$BotPath = "C:\FreedomWalletBot",
    [string]$LogPath = "C:\FreedomWalletBot\data\logs\watchdog.log"
)

# ── Configuration ─────────────────────────────────────────────────
$BotProcessName = "python"
$BotMainScript = "main.py"
$RestartFlagFile = "$BotPath\data\.needs_restart"
$ScheduledTaskName = "FreedomWalletBot"

# Restart tracking
$RestartHistory = @()

# ── Functions ──────────────────────────────────────────────────────

function Write-WatchdogLog {
    param([string]$Message)
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    
    Write-Host $logEntry
    
    # Ensure log directory exists
    $logDir = Split-Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Add-Content -Path $LogPath -Value $logEntry
}

function Test-BotRunning {
    $processes = Get-Process -Name $BotProcessName -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -like "*$BotPath*" }
    
    return ($processes.Count -gt 0)
}

function Test-RestartFlagExists {
    return (Test-Path $RestartFlagFile)
}

function Get-RestartFlagReason {
    if (Test-Path $RestartFlagFile) {
        try {
            $content = Get-Content $RestartFlagFile -Raw
            return $content.Trim()
        } catch {
            return "Unknown reason"
        }
    }
    return $null
}

function Remove-RestartFlag {
    if (Test-Path $RestartFlagFile) {
        Remove-Item $RestartFlagFile -Force
        Write-WatchdogLog "🗑️  Removed restart flag"
    }
}

function Start-Bot {
    Write-WatchdogLog "🚀 Starting bot via scheduled task: $ScheduledTaskName"
    
    try {
        # Use scheduled task to start bot (cleaner than direct process start)
        schtasks /run /tn $ScheduledTaskName | Out-Null
        Start-Sleep -Seconds 3
        
        if (Test-BotRunning) {
            Write-WatchdogLog "✅ Bot started successfully"
            return $true
        } else {
            Write-WatchdogLog "⚠️  Bot process not detected after start attempt"
            return $false
        }
    } catch {
        Write-WatchdogLog "❌ Failed to start bot: $_"
        return $false
    }
}

function Stop-BotProcesses {
    Write-WatchdogLog "🛑 Stopping all bot processes..."
    
    $processes = Get-Process -Name $BotProcessName -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -like "*$BotPath*" }
    
    foreach ($proc in $processes) {
        try {
            Write-WatchdogLog "   Killing PID $($proc.Id)..."
            Stop-Process -Id $proc.Id -Force
        } catch {
            Write-WatchdogLog "   ⚠️  Could not kill PID $($proc.Id): $_"
        }
    }
    
    Start-Sleep -Seconds 2
}

function Test-ShouldThrottle {
    # Check if too many restarts in window
    $now = Get-Date
    $windowStart = $now.AddMinutes(-$RestartWindowMinutes)
    
    # Clean old entries
    $script:RestartHistory = $RestartHistory | Where-Object { $_ -gt $windowStart }
    
    $recentRestarts = $RestartHistory.Count
    
    if ($recentRestarts -ge $MaxRestartsPerWindow) {
        Write-WatchdogLog "⚠️  Restart throttle: $recentRestarts restarts in last $RestartWindowMinutes minutes"
        return $true
    }
    
    return $false
}

function Add-RestartToHistory {
    $script:RestartHistory += Get-Date
}

function Send-AdminAlert {
    param([string]$Message)
    
    # TODO: Integrate with Telegram bot to send alert
    Write-WatchdogLog "📢 ADMIN ALERT: $Message"
}

# ── Main Watchdog Loop ─────────────────────────────────────────────

Write-WatchdogLog "═══════════════════════════════════════════════════════"
Write-WatchdogLog "🐕 Watchdog Service Started"
Write-WatchdogLog "   Bot Path: $BotPath"
Write-WatchdogLog "   Check Interval: ${CheckIntervalSeconds}s"
Write-WatchdogLog "   Max Restarts: $MaxRestartsPerWindow in ${RestartWindowMinutes}min"
Write-WatchdogLog "═══════════════════════════════════════════════════════"

$iteration = 0

while ($true) {
    $iteration++
    
    # Check restart flag (from auto-fix Event Loop handler)
    if (Test-RestartFlagExists) {
        $reason = Get-RestartFlagReason
        Write-WatchdogLog "🚨 Restart flag detected!"
        Write-WatchdogLog "   Reason: $reason"
        
        if (Test-ShouldThrottle) {
            Write-WatchdogLog "⏸️  Restart throttled - too many recent restarts"
            Send-AdminAlert "Bot restart throttled - needs manual intervention"
            Start-Sleep -Seconds 60
            continue
        }
        
        Stop-BotProcesses
        Remove-RestartFlag
        
        if (Start-Bot) {
            Add-RestartToHistory
            Write-WatchdogLog "✅ Bot restarted due to restart flag"
        } else {
            Write-WatchdogLog "❌ Failed to restart bot"
            Send-AdminAlert "Bot restart failed - manual intervention required"
        }
        
        continue
    }
    
    # Regular health check
    $isRunning = Test-BotRunning
    
    if ($iteration % 10 -eq 0) {
        # Log status every 10 iterations (5 minutes if interval=30s)
        $status = if ($isRunning) { "✅ Running" } else { "❌ Not Running" }
        Write-WatchdogLog "Health check #${iteration}: $status"
    }
    
    if (-not $isRunning) {
        Write-WatchdogLog "🚨 Bot is NOT running - attempting restart..."
        
        if (Test-ShouldThrottle) {
            Write-WatchdogLog "⏸️  Restart throttled - too many recent restarts"
            Send-AdminAlert "Bot down but restart throttled - manual check needed"
            Start-Sleep -Seconds 60
            continue
        }
        
        if (Start-Bot) {
            Add-RestartToHistory
            Write-WatchdogLog "✅ Bot restarted successfully"
            
            $recentRestarts = $RestartHistory.Count
            if ($recentRestarts -ge 2) {
                Send-AdminAlert "Bot restarted $recentRestarts times recently - possible issue"
            }
        } else {
            Write-WatchdogLog "❌ Failed to restart bot - will retry next cycle"
            Send-AdminAlert "Bot restart failed - manual intervention may be needed"
        }
    }
    
    Start-Sleep -Seconds $CheckIntervalSeconds
}
