# ============================================
# GITHUB SETUP - AUTOMATED SCRIPT (PowerShell)
# ============================================
# Push code to GitHub repository (first time)
# ============================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  GITHUB SETUP - FREEDOMWALLETBOT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location "D:\Projects\FreedomWalletBot"

# Check if Git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Git is not installed!" -ForegroundColor Red
    Write-Host "Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Step 1: Check Git status
Write-Host "[1/5] Checking Git status..." -ForegroundColor Yellow

try {
    git status | Out-Null
    Write-Host "   ✅ Git repository initialized" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Git not initialized. Initializing..." -ForegroundColor Yellow
    git init
    Write-Host "   ✅ Git initialized" -ForegroundColor Green
}

# Step 2: Check remote
Write-Host ""
Write-Host "[2/5] Checking remote..." -ForegroundColor Yellow

try {
    $currentRemote = git remote get-url origin 2>$null
    if ($currentRemote) {
        Write-Host "   ⚠️  Remote already exists: $currentRemote" -ForegroundColor Yellow
        Write-Host "   Updating to: https://github.com/mettatuan/FreedomWalletBot.git" -ForegroundColor Yellow
        git remote set-url origin https://github.com/mettatuan/FreedomWalletBot.git
    }
} catch {
    Write-Host "   Adding remote: https://github.com/mettatuan/FreedomWalletBot.git" -ForegroundColor Yellow
    git remote add origin https://github.com/mettatuan/FreedomWalletBot.git
}

Write-Host "   ✅ Remote configured" -ForegroundColor Green

# Step 3: Verify remote
Write-Host ""
Write-Host "[3/5] Verifying remote..." -ForegroundColor Yellow
git remote -v
Write-Host ""

# Step 4: Check branch
Write-Host "[4/5] Checking branch..." -ForegroundColor Yellow

try {
    $currentBranch = git branch --show-current
    
    if (-not $currentBranch) {
        Write-Host "   ⚠️  No branch detected. Will create 'main' on first commit." -ForegroundColor Yellow
    } elseif ($currentBranch -ne "main") {
        Write-Host "   Current branch: $currentBranch" -ForegroundColor Yellow
        Write-Host "   Renaming branch to 'main'..." -ForegroundColor Yellow
        git branch -M main
        Write-Host "   ✅ Branch renamed to 'main'" -ForegroundColor Green
    } else {
        Write-Host "   ✅ Branch: main" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  Could not determine branch" -ForegroundColor Yellow
}

# Step 5: Ready to push
Write-Host ""
Write-Host "[5/5] Ready to push!" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Make sure you created repository on GitHub:" -ForegroundColor White
Write-Host "   https://github.com/new" -ForegroundColor Yellow
Write-Host "   Repository name: FreedomWalletBot" -ForegroundColor Yellow
Write-Host "   Private: YES" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. This script will commit and push for you!" -ForegroundColor White
Write-Host ""

$proceed = Read-Host "Do you want to commit and push now? (yes/no)"

if ($proceed -eq "yes") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  COMMITTING FILES" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    # Add all files
    Write-Host ""
    Write-Host "Adding all files..." -ForegroundColor Yellow
    git add .
    
    # Get commit message
    $commitMsg = Read-Host "Enter commit message (or press Enter for default)"
    if (-not $commitMsg) {
        $commitMsg = "Initial commit: Production deployment system"
    }
    
    # Commit
    Write-Host ""
    Write-Host "Committing: $commitMsg" -ForegroundColor Yellow
    git commit -m $commitMsg
    
    # Push to GitHub
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  PUSHING TO GITHUB" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NOTE: You may need to authenticate with GitHub." -ForegroundColor Yellow
    Write-Host "      Use GitHub CLI (gh auth login) or Personal Access Token." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        git push -u origin main
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "View your repository:" -ForegroundColor White
        Write-Host "https://github.com/mettatuan/FreedomWalletBot" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor White
        Write-Host "  • Clone on VPS: git clone https://github.com/mettatuan/FreedomWalletBot.git" -ForegroundColor Yellow
        Write-Host "  • Follow QUICK_START.md to deploy" -ForegroundColor Yellow
        Write-Host ""
        
    } catch {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host "  AUTHENTICATION REQUIRED" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Option 1: Use GitHub CLI (Easiest)" -ForegroundColor White
        Write-Host "   winget install --id GitHub.cli" -ForegroundColor Cyan
        Write-Host "   gh auth login" -ForegroundColor Cyan
        Write-Host "   git push -u origin main" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Option 2: Use Personal Access Token" -ForegroundColor White
        Write-Host "   1. Create token: https://github.com/settings/tokens" -ForegroundColor Cyan
        Write-Host "   2. Run: git push -u origin main" -ForegroundColor Cyan
        Write-Host "   3. Username: mettatuan" -ForegroundColor Cyan
        Write-Host "   4. Password: [PASTE YOUR TOKEN]" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "See GITHUB_SETUP_GUIDE.md for detailed instructions." -ForegroundColor Yellow
        Write-Host ""
    }
    
} else {
    Write-Host ""
    Write-Host "Setup completed. Run these commands manually:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   git add ." -ForegroundColor Cyan
    Write-Host "   git commit -m `"Initial commit`"" -ForegroundColor Cyan
    Write-Host "   git push -u origin main" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
