# ============================================================================
# Freedom Wallet Bot - Health Check Script
# ============================================================================
# Description: Comprehensive system health monitoring
# Usage: .\health_check.ps1 [-Quick] [-Detailed]
# ============================================================================

param(
    [string]$InstallPath = "C:\FreedomWalletBot",
    [string]$ServiceName = "FreedomWalletBot",
    [switch]$Quick,
    [switch]$Detailed
)

$ErrorActionPreference = "Continue"

# Color output
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }

$healthScore = 0
$maxScore = 0
$issues = @()

if (-not $Quick) {
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              Freedom Wallet Bot - Health Check                 ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}

# ============================================================================
# 1. Service Status
# ============================================================================
if (-not $Quick) { Write-Host "`n[1] Checking Windows Service..." -ForegroundColor Magenta }

$maxScore += 20
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue

if ($service) {
    if ($service.Status -eq 'Running') {
        $healthScore += 20
        Write-Success "Service is running"
    } else {
        Write-Error "Service exists but not running: $($service.Status)"
        $issues += "Service not running"
    }
} else {
    Write-Warning "Service not installed (manual mode)"
    $healthScore += 10
}

# ============================================================================
# 2. Process Check
# ============================================================================
if (-not $Quick) { Write-Host "`n[2] Checking Python Process..." -ForegroundColor Magenta }

$maxScore += 15
$pythonProcess = Get-Process python -ErrorAction SilentlyContinue | 
                 Where-Object { $_.Path -like "*$InstallPath*" }

if ($pythonProcess) {
    $healthScore += 15
    $uptime = ((Get-Date) - $pythonProcess.StartTime).ToString("dd\.hh\:mm\:ss")
    Write-Success "Bot process running (PID: $($pythonProcess.Id), Uptime: $uptime)"
    
    if ($Detailed) {
        $memoryMB = [math]::Round($pythonProcess.WorkingSet64 / 1MB, 2)
        $cpuPercent = [math]::Round($pythonProcess.CPU, 2)
        Write-Info "  Memory: $memoryMB MB"
        Write-Info "  CPU Time: $cpuPercent seconds"
    }
} else {
    Write-Error "Python process not found"
    $issues += "Bot process not running"
}

# ============================================================================
# 3. Log Activity Check
# ============================================================================
if (-not $Quick) { Write-Host "`n[3] Checking Log Activity..." -ForegroundColor Magenta }

$maxScore += 15
$logDir = Join-Path $InstallPath "logs"

if (Test-Path $logDir) {
    $recentLogs = Get-ChildItem -Path $logDir -Filter "*.log" -ErrorAction SilentlyContinue | 
                  Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-1) }
    
    if ($recentLogs) {
        $healthScore += 15
        Write-Success "Recent log activity detected"
        
        if ($Detailed) {
            $recentLogs | ForEach-Object {
                $age = ((Get-Date) - $_.LastWriteTime).TotalMinutes
                Write-Info "  • $($_.Name) ($([ math]::Round($age, 1)) min ago)"
            }
        }
    } else {
        Write-Warning "No recent log activity (last hour)"
        $healthScore += 5
        $issues += "No recent log activity"
    }
} else {
    Write-Warning "Log directory not found"
    $healthScore += 5
}

# ============================================================================
# 4. Database Connectivity
# ============================================================================
if (-not $Quick) { Write-Host "`n[4] Checking Database..." -ForegroundColor Magenta }

$maxScore += 20
$sqliteDb = Join-Path $InstallPath "data\bot.db"

if (Test-Path $sqliteDb) {
    $dbInfo = Get-Item $sqliteDb
    $dbSizeMB = [math]::Round($dbInfo.Length / 1MB, 2)
    $dbAge = ((Get-Date) - $dbInfo.LastWriteTime).TotalMinutes
    
    if ($dbAge -lt 60) {
        $healthScore += 20
        Write-Success "Database active (last write: $([math]::Round($dbAge, 1)) min ago, size: $dbSizeMB MB)"
    } else {
        $healthScore += 10
        Write-Warning "Database not recently updated (last write: $([math]::Round($dbAge / 60, 1)) hours ago)"
        $issues += "Database not recently updated"
    }
} else {
    Write-Warning "SQLite database not found (might be using PostgreSQL)"
    $healthScore += 10
}

# ============================================================================
# 5. Disk Space
# ============================================================================
if (-not $Quick) { Write-Host "`n[5] Checking Disk Space..." -ForegroundColor Magenta }

$maxScore += 15
$drive = (Get-Item $InstallPath).PSDrive
$freeGB = [math]::Round($drive.Free / 1GB, 2)
$usedPercent = [math]::Round(($drive.Used / ($drive.Used + $drive.Free)) * 100, 1)

if ($freeGB -gt 5) {
    $healthScore += 15
    Write-Success "Sufficient disk space: $freeGB GB free ($usedPercent% used)"
} elseif ($freeGB -gt 1) {
    $healthScore += 10
    Write-Warning "Low disk space: $freeGB GB free ($usedPercent% used)"
    $issues += "Low disk space"
} else {
    Write-Error "Critical: Very low disk space: $freeGB GB free"
    $issues += "Critical low disk space"
}

# ============================================================================
# 6. Network Connectivity
# ============================================================================
if (-not $Quick) { Write-Host "`n[6] Checking Network..." -ForegroundColor Magenta }

$maxScore += 15

# Test Telegram API
$telegramTest = Test-NetConnection -ComputerName "api.telegram.org" -Port 443 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

if ($telegramTest.TcpTestSucceeded) {
    $healthScore += 15
    Write-Success "Telegram API reachable"
} else {
    Write-Error "Cannot reach Telegram API"
    $issues += "Network connectivity issue"
}

# ============================================================================
# Health Score Summary
# ============================================================================
$healthPercent = [math]::Round(($healthScore / $maxScore) * 100, 1)

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Health Check Summary                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Overall Health Score: $healthScore / $maxScore ($healthPercent%)" -ForegroundColor $(
    if ($healthPercent -ge 90) { 'Green' }
    elseif ($healthPercent -ge 70) { 'Yellow' }
    else { 'Red' }
)

if ($healthPercent -ge 90) {
    Write-Host "Status: HEALTHY ✓`n" -ForegroundColor Green
} elseif ($healthPercent -ge 70) {
    Write-Host "Status: DEGRADED ⚠`n" -ForegroundColor Yellow
} else {
    Write-Host "Status: CRITICAL ✗`n" -ForegroundColor Red
}

if ($issues.Count -gt 0) {
    Write-Host "Issues Detected:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  • $issue" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Additional recommendations
if (-not $Quick -and $healthPercent -lt 90) {
    Write-Host "Recommendations:" -ForegroundColor Cyan
    
    if ($issues -contains "Service not running") {
        Write-Host "  • Start the service: Start-Service $ServiceName" -ForegroundColor Yellow
    }
    if ($issues -contains "Bot process not running") {
        Write-Host "  • Check logs: .\scripts\deployment\view_logs.ps1" -ForegroundColor Yellow
        Write-Host "  • Restart service: Restart-Service $ServiceName" -ForegroundColor Yellow
    }
    if ($issues -like "*disk space*") {
        Write-Host "  • Clean up old logs and backups" -ForegroundColor Yellow
    }
    if ($issues -contains "Network connectivity issue") {
        Write-Host "  • Check firewall and internet connection" -ForegroundColor Yellow
        Write-Host "  • Verify VPS network configuration" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Set exit code based on health
if ($healthPercent -ge 70) {
    exit 0
} else {
    exit 1
}
