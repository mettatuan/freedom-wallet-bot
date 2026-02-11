# Quick Push to GitHub (no prompts)
# Usage: .\quick_push.ps1 "Your commit message"

param(
    [string]$Message = "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "QUICK PUSH TO GITHUB" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Init git if needed
if (-not (Test-Path .git)) {
    Write-Host "[INIT] Initializing git..." -ForegroundColor Yellow
    git init
    git branch -M main
}

# Add all files
Write-Host "[ADD] Adding files..." -ForegroundColor Yellow
git add .

# Show status
Write-Host "`n[FILES] Changed files:" -ForegroundColor Cyan
git status --short

# Commit
Write-Host "`n[COMMIT] Committing: $Message" -ForegroundColor Yellow
git commit -m "$Message"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] No changes to commit" -ForegroundColor Gray
    exit 0
}

# Check remote
$remote = git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host "`n[WARNING] No remote configured!" -ForegroundColor Yellow
    Write-Host "Add remote first:`n" -ForegroundColor Cyan
    Write-Host "git remote add origin https://github.com/YOUR_USERNAME/freedom-wallet-bot.git" -ForegroundColor White
    exit 1
}

# Push
Write-Host "`n[PUSH] Pushing to GitHub..." -ForegroundColor Yellow
git push

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] Pushed successfully!" -ForegroundColor Green
    Write-Host "URL: $($remote -replace '\.git$', '')`n" -ForegroundColor Cyan
} else {
    Write-Host "`n[ERROR] Push failed!" -ForegroundColor Red
    Write-Host "Try: gh auth login" -ForegroundColor Yellow
    exit 1
}
