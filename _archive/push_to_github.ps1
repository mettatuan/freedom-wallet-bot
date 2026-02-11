# ============================================
# Freedom Wallet Bot - Auto Push to GitHub
# ============================================
# Script tự động đẩy code lên GitHub
# Lọc file theo .gitignore, commit và push

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🚀 AUTO PUSH TO GITHUB" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Check if git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git is not installed!" -ForegroundColor Red
    Write-Host "   Download: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Check if git repo exists
if (-not (Test-Path .git)) {
    Write-Host "[INIT] Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "[OK] Git repository initialized`n" -ForegroundColor Green
}

# Check if .gitignore exists
if (-not (Test-Path .gitignore)) {
    Write-Host "[WARNING] .gitignore not found!" -ForegroundColor Yellow
    Write-Host "   Sensitive files may be pushed to GitHub!`n" -ForegroundColor Yellow
} else {
    Write-Host "[OK] .gitignore exists (sensitive files filtered)`n" -ForegroundColor Green
}

# Verify sensitive files are ignored
Write-Host "[CHECK] Verifying sensitive files..." -ForegroundColor Yellow
$sensitiveFiles = @(".env", "google_service_account.json", "data/bot.db")
$notIgnored = @()

foreach ($file in $sensitiveFiles) {
    if (Test-Path $file) {
        # Check if file is tracked by git
        $isTracked = git ls-files $file
        if ($isTracked) {
            $notIgnored += $file
        }
    }
}

if ($notIgnored.Count -gt 0) {
    Write-Host "[WARNING] Sensitive files are being tracked:" -ForegroundColor Red
    foreach ($file in $notIgnored) {
        Write-Host "   [X] $file" -ForegroundColor Red
    }
    Write-Host "`n[TIP] Run this command to remove from git:" -ForegroundColor Yellow
    foreach ($file in $notIgnored) {
        Write-Host "   git rm --cached $file" -ForegroundColor Cyan
    }
    Write-Host ""
    $continue = Read-Host "Continue to push? (y/n)"
    if ($continue -ne "y") {
        Write-Host "[CANCELLED] Push cancelled" -ForegroundColor Red
        exit 0
    }
}

# Show git status
Write-Host "[STATUS] File changes:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Check if there are changes
$changes = git status --porcelain
if (-not $changes) {
    Write-Host "[OK] No changes to commit" -ForegroundColor Green
    exit 0
}

# Ask for commit message
Write-Host "[INPUT] Enter commit message (or press Enter for default):" -ForegroundColor Yellow
$commitMsg = Read-Host "   Message"
if (-not $commitMsg) {
    $date = Get-Date -Format "yyyy-MM-dd HH:mm"
    $commitMsg = "Update: $date - Week 1-5 complete (fraud detection ready)"
}

# Add all files (respects .gitignore)
Write-Host "`n[ADD] Adding files..." -ForegroundColor Yellow
git add .

# Show what will be committed
Write-Host "`n[FILES] Files to be committed:" -ForegroundColor Yellow
git diff --cached --name-only
Write-Host ""

# Commit
Write-Host "[COMMIT] Committing changes..." -ForegroundColor Yellow
git commit -m "$commitMsg"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Commit failed!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Commit successful!`n" -ForegroundColor Green

# Check if remote exists
$remote = git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host "[WARNING] No remote repository configured!" -ForegroundColor Yellow
    Write-Host "`n[GUIDE] How to add remote:" -ForegroundColor Cyan
    Write-Host "   1. Create new repository on GitHub: https://github.com/new" -ForegroundColor White
    Write-Host "   2. Run these commands:" -ForegroundColor White
    Write-Host "      git remote add origin https://github.com/YOUR_USERNAME/freedom-wallet-bot.git" -ForegroundColor Cyan
    Write-Host "      git branch -M main" -ForegroundColor Cyan
    Write-Host "      git push -u origin main" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Or use GitHub CLI:" -ForegroundColor White
    Write-Host "      gh repo create freedom-wallet-bot --public --source=. --push" -ForegroundColor Cyan
    Write-Host ""
    exit 0
}

# Check current branch
$branch = git branch --show-current
if (-not $branch) {
    $branch = "main"
    Write-Host "[BRANCH] Renaming branch to main..." -ForegroundColor Yellow
    git branch -M main
}

# Push to GitHub
Write-Host "[PUSH] Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "   Remote: $remote" -ForegroundColor Gray
Write-Host "   Branch: $branch`n" -ForegroundColor Gray

git push -u origin $branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "[SUCCESS] PUSH SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "`n[REPO] Repository URL:" -ForegroundColor Cyan
    Write-Host "   $($remote -replace '\.git$', '')" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "`n[ERROR] Push failed!" -ForegroundColor Red
    Write-Host "[TIP] You may need to:" -ForegroundColor Yellow
    Write-Host "   - Login to GitHub Desktop" -ForegroundColor White
    Write-Host "   - Or use: gh auth login" -ForegroundColor White
    Write-Host "   - Or configure git credential manager" -ForegroundColor White
    exit 1
}
