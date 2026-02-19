# ============================================================================
# Freedom Wallet Bot - Log Viewer
# ============================================================================
# Description: Interactive log viewer with filtering and tail mode
# Usage: .\view_logs.ps1 [-Tail] [-Filter "keyword"] [-Lines 50]
# ============================================================================

param(
    [string]$InstallPath = "C:\FreedomWalletBot",
    [switch]$Tail,
    [string]$Filter = "",
    [int]$Lines = 50,
    [switch]$Service,
    [switch]$Bot,
    [switch]$Deploy
)

$ErrorActionPreference = "Continue"

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            Freedom Wallet Bot - Log Viewer                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$logDir = Join-Path $InstallPath "logs"

if (-not (Test-Path $logDir)) {
    Write-Host "✗ Log directory not found: $logDir" -ForegroundColor Red
    exit 1
}

# Get all log files
$logFiles = Get-ChildItem -Path $logDir -Filter "*.log" -ErrorAction SilentlyContinue

if (-not $logFiles) {
    Write-Host "✗ No log files found in $logDir" -ForegroundColor Red
    exit 1
}

# Filter by type
if ($Service) {
    $logFiles = $logFiles | Where-Object { $_.Name -like "service_*" }
    Write-Host "Showing: Service logs only`n" -ForegroundColor Yellow
}
elseif ($Bot) {
    $logFiles = $logFiles | Where-Object { $_.Name -like "bot_*" -or $_.Name -eq "bot.log" }
    Write-Host "Showing: Bot logs only`n" -ForegroundColor Yellow
}
elseif ($Deploy) {
    $logFiles = $logFiles | Where-Object { $_.Name -like "deploy_*" }
    Write-Host "Showing: Deployment logs only`n" -ForegroundColor Yellow
}

# Show available log files
Write-Host "Available Logs:" -ForegroundColor Cyan
$logFiles | Sort-Object LastWriteTime -Descending | ForEach-Object {
    $age = ((Get-Date) - $_.LastWriteTime).TotalHours
    $size = [math]::Round($_.Length / 1KB, 2)
    $ageStr = if ($age -lt 1) { "$([math]::Round($age * 60)) min ago" } 
              elseif ($age -lt 24) { "$([math]::Round($age, 1)) hrs ago" }
              else { "$([math]::Round($age / 24, 1)) days ago" }
    
    Write-Host "  • $($_.Name) - $size KB ($ageStr)" -ForegroundColor White
}

Write-Host ""

# Determine which log to view
$defaultLog = $logFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $Tail) {
    Write-Host "Select a log file (press Enter for latest: $($defaultLog.Name)):" -ForegroundColor Yellow
    Write-Host "Or type 'all' to merge all logs`n" -ForegroundColor Gray
    
    $selection = Read-Host "Selection"
    
    if ([string]::IsNullOrWhiteSpace($selection)) {
        $selectedLog = $defaultLog
    }
    elseif ($selection -eq 'all') {
        $selectedLog = $null
        $viewAll = $true
    }
    else {
        $selectedLog = $logFiles | Where-Object { $_.Name -like "*$selection*" } | Select-Object -First 1
        if (-not $selectedLog) {
            Write-Host "✗ Log file not found: $selection" -ForegroundColor Red
            exit 1
        }
    }
}
else {
    $selectedLog = $defaultLog
}

Write-Host ""

# View logs
if ($Tail) {
    Write-Host "Watching: $($selectedLog.Name) (Press Ctrl+C to stop)" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════════`n" -ForegroundColor Gray
    
    if ([string]::IsNullOrWhiteSpace($Filter)) {
        Get-Content -Path $selectedLog.FullName -Tail $Lines -Wait
    }
    else {
        Get-Content -Path $selectedLog.FullName -Tail 0 -Wait | Where-Object { $_ -like "*$Filter*" }
    }
}
elseif ($viewAll) {
    Write-Host "Merged Logs (latest $Lines lines):" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════════`n" -ForegroundColor Gray
    
    $allContent = $logFiles | ForEach-Object {
        Get-Content $_.FullName -ErrorAction SilentlyContinue | ForEach-Object {
            [PSCustomObject]@{
                Content = $_
                File = $_.Name
            }
        }
    }
    
    $filteredContent = if ([string]::IsNullOrWhiteSpace($Filter)) {
        $allContent
    } else {
        $allContent | Where-Object { $_.Content -like "*$Filter*" }
    }
    
    $filteredContent | Select-Object -Last $Lines | ForEach-Object {
        # Color code by log level
        $line = $_.Content
        if ($line -match "\[ERROR\]" -or $line -match "ERROR") {
            Write-Host $line -ForegroundColor Red
        }
        elseif ($line -match "\[WARNING\]" -or $line -match "WARNING") {
            Write-Host $line -ForegroundColor Yellow
        }
        elseif ($line -match "\[SUCCESS\]" -or $line -match "SUCCESS") {
            Write-Host $line -ForegroundColor Green
        }
        else {
            Write-Host $line
        }
    }
}
else {
    Write-Host "Viewing: $($selectedLog.Name) (latest $Lines lines)" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════════`n" -ForegroundColor Gray
    
    $content = Get-Content -Path $selectedLog.FullName -Tail $Lines -ErrorAction SilentlyContinue
    
    $filteredContent = if ([string]::IsNullOrWhiteSpace($Filter)) {
        $content
    } else {
        $content | Where-Object { $_ -like "*$Filter*" }
    }
    
    foreach ($line in $filteredContent) {
        # Color code by log level
        if ($line -match "\[ERROR\]" -or $line -match "ERROR" -or $line -match "✗") {
            Write-Host $line -ForegroundColor Red
        }
        elseif ($line -match "\[WARNING\]" -or $line -match "WARNING" -or $line -match "⚠") {
            Write-Host $line -ForegroundColor Yellow
        }
        elseif ($line -match "\[SUCCESS\]" -or $line -match "SUCCESS" -or $line -match "✓") {
            Write-Host $line -ForegroundColor Green
        }
        elseif ($line -match "\[INFO\]" -or $line -match "ℹ") {
            Write-Host $line -ForegroundColor Cyan
        }
        else {
            Write-Host $line
        }
    }
}

Write-Host "`n═══════════════════════════════════════════════════════════════════" -ForegroundColor Gray
Write-Host "`nLog Commands:" -ForegroundColor Cyan
Write-Host "  • Watch latest: .\view_logs.ps1 -Tail" -ForegroundColor Yellow
Write-Host "  • Filter logs:  .\view_logs.ps1 -Filter 'ERROR'" -ForegroundColor Yellow
Write-Host "  • More lines:   .\view_logs.ps1 -Lines 100" -ForegroundColor Yellow
Write-Host "  • Service logs: .\view_logs.ps1 -Service" -ForegroundColor Yellow
Write-Host "  • Bot logs:     .\view_logs.ps1 -Bot" -ForegroundColor Yellow
Write-Host ""

exit 0
