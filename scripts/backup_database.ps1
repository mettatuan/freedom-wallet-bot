# ============================================
# PostgreSQL Automated Backup Script
# ============================================
# Daily backup with retention policy
# ============================================

param(
    [string]$BackupDir = "D:\FreedomWalletBot\backups\database",
    [int]$RetentionDays = 7
)

# Configuration
$DbName = "freedomwalletdb"
$DbUser = "freedomwallet"
$DbPassword = $env:DB_PASSWORD  # Load from environment
$PgDumpPath = "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe"

# Create backup directory if not exists
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "✅ Created backup directory: $BackupDir"
}

# Generate backup filename with timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDir "freedomwallet_$Timestamp.sql"
$BackupFileGz = "$BackupFile.gz"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "🔄 Starting PostgreSQL Backup"
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "📅 Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "💾 Database: $DbName"
Write-Host "📁 Backup file: $BackupFile"
Write-Host ""

# Set password as environment variable (pg_dump reads from PGPASSWORD)
$env:PGPASSWORD = $DbPassword

try {
    # Run pg_dump
    Write-Host "🔄 Creating database dump..."
    & $PgDumpPath -h localhost -U $DbUser -d $DbName -F p -f $BackupFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dump created successfully"
        
        # Compress backup (optional - requires 7-Zip or similar)
        if (Get-Command "7z" -ErrorAction SilentlyContinue) {
            Write-Host "🔄 Compressing backup..."
            & 7z a -tgzip $BackupFileGz $BackupFile -sdel | Out-Null
            $FinalFile = $BackupFileGz
        } else {
            $FinalFile = $BackupFile
        }
        
        $FileSize = (Get-Item $FinalFile).Length / 1MB
        Write-Host "✅ Backup completed: $FinalFile"
        Write-Host "📊 Size: $([math]::Round($FileSize, 2)) MB"
        
        # Clean old backups (retention policy)
        Write-Host ""
        Write-Host "🧹 Cleaning old backups (retention: $RetentionDays days)..."
        $CutoffDate = (Get-Date).AddDays(-$RetentionDays)
        $OldBackups = Get-ChildItem $BackupDir -Filter "freedomwallet_*.sql*" | Where-Object { $_.LastWriteTime -lt $CutoffDate }
        
        if ($OldBackups) {
            foreach ($file in $OldBackups) {
                Remove-Item $file.FullName -Force
                Write-Host "  🗑️ Deleted: $($file.Name)"
            }
            Write-Host "✅ Cleaned $($OldBackups.Count) old backup(s)"
        } else {
            Write-Host "ℹ️ No old backups to clean"
        }
        
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        Write-Host "✅ BACKUP COMPLETED SUCCESSFULLY"
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        exit 0
        
    } else {
        Write-Host "❌ Backup failed with exit code: $LASTEXITCODE"
        exit 1
    }
    
} catch {
    Write-Host "❌ Error during backup: $_"
    exit 1
} finally {
    # Clear password from environment
    $env:PGPASSWORD = $null
}
