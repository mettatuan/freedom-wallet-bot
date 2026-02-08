# Setup GitHub Repository (First Time Only)
# This script helps you connect to GitHub

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "GITHUB SETUP WIZARD" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Check git installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git is not installed!" -ForegroundColor Red
    Write-Host "Download: https://git-scm.com/download/win`n" -ForegroundColor Yellow
    exit 1
}

# Init git
if (-not (Test-Path .git)) {
    Write-Host "[1/4] Initializing git repository..." -ForegroundColor Yellow
    git init
    git branch -M main
    Write-Host "[OK] Git initialized`n" -ForegroundColor Green
} else {
    Write-Host "[OK] Git already initialized`n" -ForegroundColor Green
}

# Add files
Write-Host "[2/4] Adding files..." -ForegroundColor Yellow
git add .
$filesCount = (git diff --cached --name-only | Measure-Object -Line).Lines
Write-Host "[OK] $filesCount files ready to commit`n" -ForegroundColor Green

# First commit
Write-Host "[3/4] Creating initial commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Freedom Wallet Bot - Week 1-5 complete"
Write-Host "[OK] Commit created`n" -ForegroundColor Green

# Check remote
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "[OK] Remote already configured: $remote`n" -ForegroundColor Green
} else {
    Write-Host "[4/4] Setting up GitHub remote..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Choose an option:" -ForegroundColor Cyan
    Write-Host "  1. I already created a repo on GitHub (manual)" -ForegroundColor White
    Write-Host "  2. Create new repo using GitHub CLI (auto)" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1 or 2)"
    
    if ($choice -eq "2") {
        # Check if gh CLI is installed
        if (Get-Command gh -ErrorAction SilentlyContinue) {
            Write-Host "`n[AUTO] Creating repository on GitHub..." -ForegroundColor Yellow
            gh repo create freedom-wallet-bot --public --source=. --remote=origin --description="Telegram Bot for Freedom Wallet referral system"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Repository created!`n" -ForegroundColor Green
                $remote = git remote get-url origin
            } else {
                Write-Host "[ERROR] Failed to create repo. Use option 1 instead.`n" -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "`n[ERROR] GitHub CLI not installed!" -ForegroundColor Red
            Write-Host "Install: winget install GitHub.cli" -ForegroundColor Yellow
            Write-Host "Then run: gh auth login`n" -ForegroundColor Yellow
            exit 1
        }
    } else {
        # Manual setup
        Write-Host "`n[MANUAL] Follow these steps:" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Go to: https://github.com/new" -ForegroundColor White
        Write-Host "2. Repository name: freedom-wallet-bot" -ForegroundColor White
        Write-Host "3. Set to Public or Private" -ForegroundColor White
        Write-Host "4. DON'T initialize with README" -ForegroundColor White
        Write-Host "5. Click 'Create repository'" -ForegroundColor White
        Write-Host ""
        Write-Host "When done, enter your GitHub username:" -ForegroundColor Yellow
        $username = Read-Host "Username"
        
        if ($username) {
            $repoUrl = "https://github.com/$username/freedom-wallet-bot.git"
            Write-Host "`n[ADD] Adding remote: $repoUrl" -ForegroundColor Yellow
            git remote add origin $repoUrl
            $remote = $repoUrl
            Write-Host "[OK] Remote added`n" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Username required!" -ForegroundColor Red
            exit 1
        }
    }
}

# Push
Write-Host "[PUSH] Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "Remote: $remote`n" -ForegroundColor Gray
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "[SUCCESS] SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository: $($remote -replace '\.git$', '')" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  - Push changes: .\quick_push.ps1" -ForegroundColor White
    Write-Host "  - Or use GitHub Desktop for GUI" -ForegroundColor White
    Write-Host "  - Deploy to Railway: https://railway.app" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "`n[ERROR] Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Authentication needed. Choose one:" -ForegroundColor Yellow
    Write-Host "  1. Use GitHub Desktop (easiest)" -ForegroundColor White
    Write-Host "  2. Use GitHub CLI: gh auth login" -ForegroundColor White
    Write-Host "  3. Use Personal Access Token" -ForegroundColor White
    Write-Host ""
    exit 1
}
