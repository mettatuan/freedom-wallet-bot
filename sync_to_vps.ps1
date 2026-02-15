# ================================================
# Sync FreedomWalletBot to VPS Windows
# ================================================

param(
    [string]$VpsIp = "103.69.190.75",
    [string]$VpsUser = "Administrator",
    [string]$VpsPath = "C:\Projects\FreedomWalletBot",
    [string]$LocalPath = "D:\Projects\FreedomWalletBot",
    [switch]$DryRun,
    [switch]$SkipBackup
)

$ErrorActionPreference = "Stop"

Write-Host "`n[SYNC] FreedomWalletBot Local to VPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor DarkGray

# Configuration
$VpsNetPath = '\\' + $VpsIp + '\C$\Projects\FreedomWalletBot'
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Excluded directories
$ExcludeDirs = @(
    ".venv",
    "__pycache__",
    ".git",
    "database",
    "logs",
    "backup",
    "_archive",
    ".pytest_cache",
    "node_modules"
)

# Excluded files
$ExcludeFiles = @(
    "*.log",
    "*.db",
    "*.db-journal",
    "*.pyc",
    "google_service_account.json",
    ".env",
    "sync_to_vps.bat",
    "sync_to_vps.ps1"
)

Write-Host "`n[CONFIG]" -ForegroundColor Yellow
Write-Host "  Local:  $LocalPath" -ForegroundColor Gray
Write-Host "  VPS:    $VpsIp -> $VpsPath" -ForegroundColor Gray
Write-Host "  User:   $VpsUser" -ForegroundColor Gray

# Step 1: Test connectivity
Write-Host "`n[1/4] Testing VPS connectivity..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $VpsIp -Count 1 -Quiet -ErrorAction SilentlyContinue

if (-not $pingResult) {
    Write-Host "  [X] Cannot reach VPS at $VpsIp" -ForegroundColor Red
    Write-Host "  [!] Check:" -ForegroundColor Yellow
    Write-Host "     - VPS is running" -ForegroundColor Gray
    Write-Host "     - Firewall allows ICMP" -ForegroundColor Gray
    Write-Host "     - Network connection is active" -ForegroundColor Gray
    exit 1
}

Write-Host "  [OK] VPS is reachable" -ForegroundColor Green

# Step 2: Map network drive with credentials
Write-Host "`n[2/4] Mapping network drive..." -ForegroundColor Yellow

Write-Host "  [!] Establishing connection to VPS..." -ForegroundColor Yellow
Write-Host "      If prompted, enter VPS Administrator password" -ForegroundColor Gray

try {
    # Try to map the network drive
    $netResult = net use "\\$VpsIp\C`$" /user:$VpsUser 2>&1
    
    if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 2) {
        Write-Host "  [OK] Network drive mapped successfully" -ForegroundColor Green
    } else {
        Write-Host "  [!] Network drive may already be mapped" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [!] Warning: " -NoNewline -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Gray
}

# Step 3: Test file sharing access
Write-Host "`n[3/4] Testing file share access..." -ForegroundColor Yellow

try {
    # Try to access the UNC path
    $testPath = Test-Path $VpsNetPath -ErrorAction Stop
    
    if (-not $testPath) {
        Write-Host "  [!] Path does not exist: $VpsNetPath" -ForegroundColor Yellow
        Write-Host "  [*] Creating remote directory..." -ForegroundColor Yellow
        New-Item -Path $VpsNetPath -ItemType Directory -Force | Out-Null
    }
    
    Write-Host "  [OK] File share accessible" -ForegroundColor Green
} catch {
    Write-Host "  [X] Cannot access file share" -ForegroundColor Red
    Write-Host "  [!] Possible fixes:" -ForegroundColor Yellow
    Write-Host "     1. Enable Admin`$ share on VPS:" -ForegroundColor Gray
    Write-Host "        reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f" -ForegroundColor DarkGray
    Write-Host "     2. Or use credential:" -ForegroundColor Gray
    $credMsg = '        net use \\' + $VpsIp + '\C$ /user:' + $VpsUser + ' [password]'
    Write-Host $credMsg -ForegroundColor DarkGray
    Write-Host ("`n  Error: " + $_.Exception.Message) -ForegroundColor Red
    exit 1
}

# Step 4: Backup current VPS files (optional)
if (-not $SkipBackup) {
    Write-Host "`n[4/5] Backing up current VPS files..." -ForegroundColor Yellow
    
    $backupPath = "$VpsNetPath\backup\pre_sync_$Timestamp"
    
    try {
        if (Test-Path "$VpsNetPath\main.py") {
            New-Item -Path $backupPath -ItemType Directory -Force | Out-Null
            Copy-Item -Path "$VpsNetPath\*" -Destination $backupPath -Recurse -Exclude $ExcludeDirs -ErrorAction SilentlyContinue
            Write-Host "  [OK] Backup created: backup\pre_sync_$Timestamp" -ForegroundColor Green
        } else {
            Write-Host "  [i] No existing files to backup (first deployment)" -ForegroundColor Cyan
        }
    } catch {
        Write-Host ("  [!] Backup failed (continuing anyway): " + $_.Exception.Message) -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[4/5] Skipping backup..." -ForegroundColor Yellow
}

# Step 5: Sync files
Write-Host "`n[5/5] Syncing files to VPS..." -ForegroundColor Yellow

$robocopyArgs = @(
    $LocalPath,
    $VpsNetPath,
    "/MIR"  # Mirror (deletes files not in source)
)

# Add excluded directories
foreach ($dir in $ExcludeDirs) {
    $robocopyArgs += "/XD"
    $robocopyArgs += $dir
}

# Add excluded files
foreach ($file in $ExcludeFiles) {
    $robocopyArgs += "/XF"
    $robocopyArgs += $file
}

# Add robocopy options
$robocopyArgs += @(
    "/R:2",      # Retry 2 times
    "/W:5",      # Wait 5 seconds between retries
    "/NFL",      # No file list
    "/NDL",      # No directory list
    "/NP",       # No progress
    "/NS",       # No size
    "/NC"        # No class
)

if ($DryRun) {
    $robocopyArgs += "/L"  # List only (dry run)
    Write-Host "  [!] DRY RUN MODE - No files will be modified" -ForegroundColor Yellow
}

Write-Host "`n  Starting robocopy...`n" -ForegroundColor Gray

$result = & robocopy $robocopyArgs

$exitCode = $LASTEXITCODE

# Robocopy exit codes
# 0 = No files copied (no change)
# 1 = Files copied successfully
# 2 = Extra files/directories detected
# 4 = Mismatched files/directories
# 8+ = Failed

if ($exitCode -ge 8) {
    Write-Host "`n  [X] Sync failed with exit code: $exitCode" -ForegroundColor Red
    exit 1
} elseif ($exitCode -eq 0) {
    Write-Host "`n  [OK] No changes detected (already in sync)" -ForegroundColor Green
} else {
    Write-Host "`n  [OK] Successfully synced to VPS" -ForegroundColor Green
}

# Summary
Write-Host "`n========================================" -ForegroundColor DarkGray
Write-Host "[DONE] Deployment completed!" -ForegroundColor Green
Write-Host "`n[NEXT STEPS]" -ForegroundColor Cyan
Write-Host "  1. RDP to VPS:" -ForegroundColor Gray
Write-Host "     mstsc /v:$VpsIp`n" -ForegroundColor White

Write-Host "  2. On VPS, navigate to:" -ForegroundColor Gray
Write-Host "     cd C:\Projects\FreedomWalletBot`n" -ForegroundColor White

Write-Host "  3. Activate virtual environment:" -ForegroundColor Gray
Write-Host "     .\.venv\Scripts\activate`n" -ForegroundColor White

Write-Host "  4. Install/update dependencies:" -ForegroundColor Gray
Write-Host "     pip install -r requirements.txt`n" -ForegroundColor White

Write-Host "  5. Restart bot:" -ForegroundColor Gray
Write-Host "     Get-Process python | Stop-Process -Force" -ForegroundColor White
Write-Host "     python main.py`n" -ForegroundColor White

Write-Host "========================================`n" -ForegroundColor DarkGray
