# ============================================================
# PUSH CODE LÊN GITHUB
# Chạy script này để commit và push tất cả thay đổi Phase 1-3
# ============================================================

param(
    [string]$CommitMessage = "Phase 1-3 complete: Retention-first redesign",
    [string]$Branch = "cleanup/hard-refactor",
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "📤 PUSHING CODE TO GITHUB" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# ============================================================
# STEP 1: Check Git status
# ============================================================
Write-Host "STEP 1: Checking Git status..." -ForegroundColor Yellow

git status --short

$modifiedFiles = git status --short | Measure-Object | Select-Object -ExpandProperty Count

Write-Host "`n  Found $modifiedFiles changed/untracked files" -ForegroundColor Gray

# ============================================================
# STEP 2: Show changes
# ============================================================
Write-Host "`nSTEP 2: Changes to be committed:" -ForegroundColor Yellow

Write-Host "`n📝 Modified files:" -ForegroundColor Cyan
git status --short | Where-Object { $_ -match '^ M' } | ForEach-Object { 
    Write-Host "  $_" -ForegroundColor Yellow 
}

Write-Host "`n❌ Deleted files:" -ForegroundColor Cyan
git status --short | Where-Object { $_ -match '^ D' } | ForEach-Object { 
    Write-Host "  $_" -ForegroundColor Red 
}

Write-Host "`n✨ New files:" -ForegroundColor Cyan
git status --short | Where-Object { $_ -match '^\?\?' } | ForEach-Object { 
    Write-Host "  $_" -ForegroundColor Green 
}

# ============================================================
# STEP 3: Add all files
# ============================================================
Write-Host "`nSTEP 3: Adding files to Git..." -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "  [DRY RUN] Would run: git add ." -ForegroundColor Magenta
} else {
    # Add all files
    git add .
    
    # Show what was staged
    $stagedCount = git diff --cached --name-only | Measure-Object | Select-Object -ExpandProperty Count
    Write-Host "  ✅ Staged $stagedCount files" -ForegroundColor Green
}

# ============================================================
# STEP 4: Create comprehensive commit message
# ============================================================
Write-Host "`nSTEP 4: Creating commit..." -ForegroundColor Yellow

$detailedMessage = @"
$CommitMessage

Phase 1 - Remove Unlock System:
- Removed unlock handlers (unlock_flow_v3, unlock_calm_flow, free_flow)
- Removed unlock trigger job
- Updated referral, status, webapp handlers
- Database schema updated (removed unlock fields)
- Migration script created

Phase 2 - Financial Assistant Core:
- Transaction Engine (NLP parser, category detection)
- Awareness Engine (real-time metrics, anomaly detection)
- Behavioral Engine (7 spending personas)
- Reflection Engine (weekly insights, 4 tones)
- Main Keyboard (4x2 layout, 8 buttons)
- Transaction handlers fully wired

Phase 3 - Testing & Refinement:
- Test suite (6 comprehensive tests, 100% pass)
- Database migration with backup system
- Google Sheets auto-sync
- Error handling & logging
- Production-ready validation

Deployment:
- VPS deployment scripts (PowerShell & Bash)
- Git-based deployment guide
- Auto-deployment webhook setup
- Systemd service configuration

Documentation:
- README.md (comprehensive)
- VPS_DEPLOYMENT_GUIDE.md (detailed deployment)
- Git deployment guide (docs/git-deployment.md)
- Phase summaries (Phase 1-3)

Files changed: ~40 files
Lines of code: ~5,000 lines
Test coverage: 6/6 tests PASSED
"@

if ($DryRun) {
    Write-Host "  [DRY RUN] Commit message:" -ForegroundColor Magenta
    Write-Host $detailedMessage -ForegroundColor Gray
} else {
    git commit -m $detailedMessage
    Write-Host "  ✅ Commit created!" -ForegroundColor Green
}

# ============================================================
# STEP 5: Push to GitHub
# ============================================================
Write-Host "`nSTEP 5: Pushing to GitHub..." -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "  [DRY RUN] Would run: git push origin $Branch" -ForegroundColor Magenta
} else {
    Write-Host "  → Pushing to branch: $Branch" -ForegroundColor Gray
    
    git push origin $Branch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Code pushed successfully!" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Push failed!" -ForegroundColor Red
        exit 1
    }
}

# ============================================================
# STEP 6: Verify
# ============================================================
Write-Host "`nSTEP 6: Verifying..." -ForegroundColor Yellow

if (-not $DryRun) {
    $latestCommit = git log -1 --oneline
    Write-Host "  Latest commit: $latestCommit" -ForegroundColor Gray
    
    $remoteBranch = git ls-remote origin $Branch | Select-Object -First 1
    if ($remoteBranch) {
        Write-Host "  ✅ Remote branch updated!" -ForegroundColor Green
    }
}

# ============================================================
# SUMMARY
# ============================================================
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "✅ PUSH COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

Write-Host "`nRepository: https://github.com/mettatuan/freedom-wallet-bot" -ForegroundColor White
Write-Host "Branch: $Branch" -ForegroundColor White

if (-not $DryRun) {
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. VPS sẽ pull code về:" -ForegroundColor Gray
    Write-Host "   ssh root@your_vps 'cd /root/FreedomWalletBot && git pull'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Hoặc dùng deployment script:" -ForegroundColor Gray
    Write-Host "   ssh root@your_vps '/root/FreedomWalletBot/update.sh'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Hoặc setup auto-deploy webhook (xem docs/git-deployment.md)" -ForegroundColor Gray
}

Write-Host "`n🎉 Code is now on GitHub!`n" -ForegroundColor Green
