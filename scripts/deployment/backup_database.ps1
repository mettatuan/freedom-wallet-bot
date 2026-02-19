# ============================================================================
# Freedom Wallet Bot - Database Backup Script
# ============================================================================
# Description: Backup database with rotation (keep last 7 days)
# Usage: .\backup_database.ps1
# ============================================================================

param(
    [string]$InstallPath = "C:\FreedomWalletBot",
    [int]$RetentionDays = 7
)

$ErrorActionPreference = "Stop"

# Color output
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }

Write-Host "`n═══ Database Backup Started ═══`n" -ForegroundColor Cyan

Set-Location $InstallPath

# Create backup directory
$backupDir = Join-Path $InstallPath "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Write-Info "Created backup directory: $backupDir"
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# ============================================================================
# Backup SQLite Database
# ============================================================================
$sqliteDb = Join-Path $InstallPath "data\bot.db"

if (Test-Path $sqliteDb) {
    Write-Info "Backing up SQLite database..."
    
    $backupFile = Join-Path $backupDir "bot_$timestamp.db"
    
    try {
        Copy-Item -Path $sqliteDb -Destination $backupFile -Force
        
        # Compress backup
        $zipFile = "$backupFile.zip"
        Compress-Archive -Path $backupFile -DestinationPath $zipFile -Force
        Remove-Item $backupFile -Force
        
        $fileSize = (Get-Item $zipFile).Length / 1KB
        Write-Success "Database backed up: $(Split-Path $zipFile -Leaf) ($([math]::Round($fileSize, 2)) KB)"
        
    } catch {
        Write-Warning "Backup failed: $_"
        exit 1
    }
} else {
    Write-Info "No SQLite database found at $sqliteDb"
}

# ============================================================================
# Backup PostgreSQL (if configured)
# ============================================================================
$envFile = Join-Path $InstallPath ".env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    
    if ($envContent -match "DATABASE_URL=postgresql://") {
        Write-Info "PostgreSQL detected - attempting backup..."
        
        # Extract connection details
        if ($envContent -match "postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(\S+)") {
            $pgUser = $matches[1]
            $pgPassword = $matches[2]
            $pgHost = $matches[3]
            $pgPort = $matches[4]
            $pgDatabase = $matches[5]
            
            $pgBackupFile = Join-Path $backupDir "postgres_$timestamp.sql"
            
            # Set password environment variable
            $env:PGPASSWORD = $pgPassword
            
            try {
                # Run pg_dump
                $pgDumpPath = "pg_dump"  # Assumes pg_dump is in PATH
                & $pgDumpPath -h $pgHost -p $pgPort -U $pgUser -d $pgDatabase -F c -f $pgBackupFile
                
                if (Test-Path $pgBackupFile) {
                    # Compress
                    $zipFile = "$pgBackupFile.zip"
                    Compress-Archive -Path $pgBackupFile -DestinationPath $zipFile -Force
                    Remove-Item $pgBackupFile -Force
                    
                    $fileSize = (Get-Item $zipFile).Length / 1KB
                    Write-Success "PostgreSQL backed up: $(Split-Path $zipFile -Leaf) ($([math]::Round($fileSize, 2)) KB)"
                }
            } catch {
                Write-Warning "PostgreSQL backup failed: $_"
                Write-Info "Make sure PostgreSQL tools (pg_dump) are installed and in PATH"
            } finally {
                # Clear password
                Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
            }
        }
    }
}

# ============================================================================
# Backup Configuration Files
# ============================================================================
Write-Info "Backing up configuration files..."

$configFiles = @(
    ".env",
    "google_service_account.json"
)

$configBackupDir = Join-Path $backupDir "config_$timestamp"
if (-not (Test-Path $configBackupDir)) {
    New-Item -ItemType Directory -Path $configBackupDir -Force | Out-Null
}

foreach ($file in $configFiles) {
    $sourcePath = Join-Path $InstallPath $file
    if (Test-Path $sourcePath) {
        $destPath = Join-Path $configBackupDir $file
        Copy-Item -Path $sourcePath -Destination $destPath -Force
        Write-Info "  • Backed up: $file"
    }
}

# Compress config backup
$configZip = Join-Path $backupDir "config_$timestamp.zip"
Compress-Archive -Path $configBackupDir -DestinationPath $configZip -Force
Remove-Item $configBackupDir -Recurse -Force

Write-Success "Configuration backed up: $(Split-Path $configZip -Leaf)"

# ============================================================================
# Cleanup Old Backups
# ============================================================================
Write-Info "`nCleaning up old backups (keeping last $RetentionDays days)..."

$cutoffDate = (Get-Date).AddDays(-$RetentionDays)
$oldBackups = Get-ChildItem -Path $backupDir -Filter "*.zip" | 
              Where-Object { $_.LastWriteTime -lt $cutoffDate }

if ($oldBackups) {
    foreach ($backup in $oldBackups) {
        Remove-Item $backup.FullName -Force
        Write-Info "  • Removed old backup: $($backup.Name)"
    }
    Write-Success "Cleaned up $($oldBackups.Count) old backup(s)"
} else {
    Write-Info "No old backups to remove"
}

# ============================================================================
# Backup Summary
# ============================================================================
Write-Host "`n═══ Backup Complete ═══`n" -ForegroundColor Green

$allBackups = Get-ChildItem -Path $backupDir -Filter "*.zip" | 
              Sort-Object LastWriteTime -Descending

Write-Host "Current Backups ($($allBackups.Count)):" -ForegroundColor Cyan
$allBackups | Select-Object -First 10 | ForEach-Object {
    $size = [math]::Round($_.Length / 1KB, 2)
    $age = [math]::Round(((Get-Date) - $_.LastWriteTime).TotalHours, 1)
    Write-Host "  • $($_.Name) - $size KB ($age hours ago)" -ForegroundColor White
}

Write-Host "`nBackup Location: $backupDir" -ForegroundColor Yellow
Write-Host ""

exit 0
