# ============================================
# LOG VIEWER SCRIPT
# ============================================
# View and filter bot logs in real-time
# ============================================

param(
    [switch]$Follow = $false,
    [int]$Lines = 50,
    [string]$Filter = "",
    [switch]$ErrorsOnly = $false
)

$BotDir = "D:\FreedomWalletBot"
$LogDir = "$BotDir\data\logs"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "📄 FREEDOMWALLETBOT LOG VIEWER"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

# Find latest log file
$LatestLog = Get-ChildItem $LogDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $LatestLog) {
    Write-Host "❌ No log files found in $LogDir"
    exit 1
}

Write-Host "📂 Log file: $($LatestLog.Name)"
Write-Host "📅 Modified: $($LatestLog.LastWriteTime)"
Write-Host "📊 Size: $([math]::Round($LatestLog.Length / 1KB, 2)) KB"
Write-Host ""

if ($Follow) {
    Write-Host "👁️  Following log (Ctrl+C to stop)..."
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""
    
    if ($ErrorsOnly) {
        Get-Content $LatestLog.FullName -Wait -Tail $Lines | Where-Object { $_ -match "ERROR|CRITICAL" }
    } elseif ($Filter) {
        Get-Content $LatestLog.FullName -Wait -Tail $Lines | Where-Object { $_ -match $Filter }
    } else {
        Get-Content $LatestLog.FullName -Wait -Tail $Lines
    }
} else {
    Write-Host "📜 Last $Lines lines:"
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host ""
    
    if ($ErrorsOnly) {
        Get-Content $LatestLog.FullName -Tail ($Lines * 3) | Where-Object { $_ -match "ERROR|CRITICAL" } | Select-Object -Last $Lines
    } elseif ($Filter) {
        Get-Content $LatestLog.FullName -Tail ($Lines * 3) | Where-Object { $_ -match $Filter } | Select-Object -Last $Lines
    } else {
        Get-Content $LatestLog.FullName -Tail $Lines
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""
Write-Host "💡 Tips:"
Write-Host "   • Follow logs:      .\scripts\view_logs.ps1 -Follow"
Write-Host "   • Show only errors: .\scripts\view_logs.ps1 -ErrorsOnly"
Write-Host "   • Filter by text:   .\scripts\view_logs.ps1 -Filter 'telegram'"
Write-Host "   • More lines:       .\scripts\view_logs.ps1 -Lines 100"
Write-Host ""
