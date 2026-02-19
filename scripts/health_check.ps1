# ============================================
# HEALTH CHECK & MONITORING SCRIPT
# ============================================
# Monitor FreedomWalletBot status and send alerts
# Run this periodically (e.g., every 5 minutes via Task Scheduler)
# ============================================

param(
    [string]$AlertEmail = "",
    [switch]$SendAlert = $false
)

$ServiceName = "FreedomWalletBot"
$BotDir = "D:\FreedomWalletBot"
$LogFile = "$BotDir\data\logs\bot.log"
$HealthLogFile = "$BotDir\data\logs\health_check.log"

function Write-HealthLog {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - $Message" | Out-File -FilePath $HealthLogFile -Append
    Write-Host $Message
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "🏥 FREEDOMWALLETBOT HEALTH CHECK"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "📅 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

$AllHealthy = $true
$Issues = @()

# ============================================
# CHECK 1: Windows Service Status
# ============================================
Write-Host "[1/6] 🔍 Checking Windows Service..."

$Service = Get-Service $ServiceName -ErrorAction SilentlyContinue

if ($Service) {
    if ($Service.Status -eq "Running") {
        Write-Host "   ✅ Service is running"
        Write-HealthLog "✅ Service status: Running"
    } else {
        Write-Host "   ❌ Service is NOT running (Status: $($Service.Status))"
        Write-HealthLog "❌ Service status: $($Service.Status)"
        $AllHealthy = $false
        $Issues += "Service is not running"
        
        # Try to start service
        Write-Host "   🔄 Attempting to start service..."
        try {
            Start-Service $ServiceName
            Start-Sleep -Seconds 3
            $Service = Get-Service $ServiceName
            if ($Service.Status -eq "Running") {
                Write-Host "   ✅ Service started successfully"
                Write-HealthLog "✅ Service auto-started"
            } else {
                Write-Host "   ❌ Failed to start service"
                Write-HealthLog "❌ Failed to auto-start service"
            }
        } catch {
            Write-Host "   ❌ Error starting service: $_"
            Write-HealthLog "❌ Error starting service: $_"
        }
    }
} else {
    Write-Host "   ❌ Service not found!"
    Write-HealthLog "❌ Service not found"
    $AllHealthy = $false
    $Issues += "Service not installed"
}

# ============================================
# CHECK 2: Process Running
# ============================================
Write-Host ""
Write-Host "[2/6] 🔍 Checking bot process..."

$Process = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*$BotDir*" }

if ($Process) {
    $MemoryMB = [math]::Round($Process.WorkingSet64 / 1MB, 2)
    $Runtime = (Get-Date) - $Process.StartTime
    
    Write-Host "   ✅ Bot process is running"
    Write-Host "      PID: $($Process.Id)"
    Write-Host "      Memory: $MemoryMB MB"
    Write-Host "      Runtime: $($Runtime.Days)d $($Runtime.Hours)h $($Runtime.Minutes)m"
    
    Write-HealthLog "✅ Process running - PID: $($Process.Id), Memory: $MemoryMB MB"
    
    # Check for memory leak (warning if > 500MB)
    if ($MemoryMB -gt 500) {
        Write-Host "   ⚠️ High memory usage detected!"
        Write-HealthLog "⚠️ High memory usage: $MemoryMB MB"
        $Issues += "High memory usage: $MemoryMB MB"
    }
} else {
    Write-Host "   ❌ Bot process not found!"
    Write-HealthLog "❌ No bot process detected"
    $AllHealthy = $false
    $Issues += "Bot process not running"
}

# ============================================
# CHECK 3: Recent Log Activity
# ============================================
Write-Host ""
Write-Host "[3/6] 🔍 Checking log activity..."

if (Test-Path $LogFile) {
    $LogAge = (Get-Date) - (Get-Item $LogFile).LastWriteTime
    
    if ($LogAge.TotalMinutes -lt 10) {
        Write-Host "   ✅ Recent log activity ($(([math]::Round($LogAge.TotalMinutes, 1))) minutes ago)"
        Write-HealthLog "✅ Log activity: Active"
    } else {
        Write-Host "   ⚠️ No recent log activity ($([math]::Round($LogAge.TotalHours, 1)) hours ago)"
        Write-HealthLog "⚠️ No recent log activity: $([math]::Round($LogAge.TotalHours, 1)) hours"
        $Issues += "No recent log activity"
    }
    
    # Check for errors in last 100 lines
    $RecentErrors = Select-String -Path $LogFile -Pattern "ERROR|CRITICAL" -CaseSensitive | Select-Object -Last 5
    
    if ($RecentErrors) {
        Write-Host "   ⚠️ Recent errors found in log:"
        foreach ($error in $RecentErrors) {
            Write-Host "      $($error.Line.Substring(0, [Math]::Min(100, $error.Line.Length)))"
        }
        Write-HealthLog "⚠️ Recent errors detected in log"
    } else {
        Write-Host "   ✅ No recent errors in log"
    }
} else {
    Write-Host "   ❌ Log file not found!"
    Write-HealthLog "❌ Log file missing"
    $AllHealthy = $false
    $Issues += "Log file missing"
}

# ============================================
# CHECK 4: Database Connection
# ============================================
Write-Host ""
Write-Host "[4/6] 🔍 Checking database..."

try {
    $VenvPath = "$BotDir\.venv\Scripts\Activate.ps1"
    if (Test-Path $VenvPath) {
        & $VenvPath
        
        # Quick database check (you may need to customize this)
        $DbCheckScript = @"
import sys
sys.path.insert(0, '$BotDir')
from config.settings import settings
from sqlalchemy import create_engine
try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print('OK')
except Exception as e:
    print(f'ERROR: {e}')
"@
        
        $DbCheck = python -c $DbCheckScript
        
        if ($DbCheck -eq 'OK') {
            Write-Host "   ✅ Database connection successful"
            Write-HealthLog "✅ Database: Connected"
        } else {
            Write-Host "   ❌ Database connection failed: $DbCheck"
            Write-HealthLog "❌ Database connection failed"
            $AllHealthy = $false
            $Issues += "Database connection error"
        }
    }
} catch {
    Write-Host "   ⚠️ Could not verify database connection"
    Write-HealthLog "⚠️ Database check skipped"
}

# ============================================
# CHECK 5: Disk Space
# ============================================
Write-Host ""
Write-Host "[5/6] 🔍 Checking disk space..."

$Drive = Get-PSDrive -Name D -ErrorAction SilentlyContinue

if ($Drive) {
    $FreeGB = [math]::Round($Drive.Free / 1GB, 2)
    $UsedGB = [math]::Round($Drive.Used / 1GB, 2)
    $TotalGB = [math]::Round(($Drive.Free + $Drive.Used) / 1GB, 2)
    $FreePercent = [math]::Round(($Drive.Free / ($Drive.Free + $Drive.Used)) * 100, 1)
    
    Write-Host "   📊 Drive D: $FreeGB GB free / $TotalGB GB total ($FreePercent%)"
    
    if ($FreeGB -lt 5) {
        Write-Host "   ❌ Low disk space!"
        Write-HealthLog "❌ Low disk space: $FreeGB GB"
        $AllHealthy = $false
        $Issues += "Low disk space: $FreeGB GB"
    } elseif ($FreeGB -lt 20) {
        Write-Host "   ⚠️ Disk space getting low"
        Write-HealthLog "⚠️ Disk space: $FreeGB GB"
    } else {
        Write-Host "   ✅ Sufficient disk space"
    }
}

# ============================================
# CHECK 6: Network Connectivity
# ============================================
Write-Host ""
Write-Host "[6/6] 🔍 Checking network connectivity..."

try {
    $Ping = Test-Connection -ComputerName "api.telegram.org" -Count 1 -Quiet
    
    if ($Ping) {
        Write-Host "   ✅ Telegram API reachable"
        Write-HealthLog "✅ Network: Connected"
    } else {
        Write-Host "   ❌ Cannot reach Telegram API"
        Write-HealthLog "❌ Network: Telegram API unreachable"
        $AllHealthy = $false
        $Issues += "Network connectivity issue"
    }
} catch {
    Write-Host "   ⚠️ Network check failed"
    Write-HealthLog "⚠️ Network check error"
}

# ============================================
# SUMMARY & ALERTS
# ============================================
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ($AllHealthy) {
    Write-Host "✅ ALL SYSTEMS HEALTHY"
    Write-HealthLog "✅ Health check passed"
} else {
    Write-Host "❌ ISSUES DETECTED"
    Write-Host ""
    Write-Host "Issues found:"
    foreach ($issue in $Issues) {
        Write-Host "   • $issue"
    }
    
    Write-HealthLog "❌ Health check failed: $($Issues -join '; ')"
    
    # Send alert (if configured)
    if ($SendAlert -and $AlertEmail) {
        Write-Host ""
        Write-Host "📧 Sending alert email..."
        
        $Body = @"
FreedomWalletBot Health Check Alert

Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

Issues Detected:
$($Issues | ForEach-Object { "• $_" } | Out-String)

Please investigate immediately.
"@
        
        try {
            # Configure your SMTP settings here
            # Send-MailMessage -To $AlertEmail -Subject "⚠️ FreedomWalletBot Health Alert" -Body $Body -SmtpServer "smtp.gmail.com" -Port 587 -UseSsl -Credential (Get-Credential)
            Write-Host "   ℹ️ Email alert not configured yet"
        } catch {
            Write-Host "   ❌ Failed to send alert: $_"
        }
    }
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Return exit code (0 = healthy, 1 = issues)
exit ($AllHealthy ? 0 : 1)
