@echo off
REM ============================================
REM GITHUB SETUP - AUTOMATED SCRIPT
REM ============================================
REM Push code to GitHub repository (first time)
REM ============================================

echo.
echo ========================================
echo   GITHUB SETUP - FREEDOMWALLETBOT
echo ========================================
echo.

cd /d D:\Projects\FreedomWalletBot

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git is not installed!
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/5] Checking Git status...
git status >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo    Git not initialized. Initializing...
    git init
)

echo.
echo [2/5] Checking remote...
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo    Adding remote: https://github.com/mettatuan/FreedomWalletBot.git
    git remote add origin https://github.com/mettatuan/FreedomWalletBot.git
) else (
    echo    Remote already exists. Updating URL...
    git remote set-url origin https://github.com/mettatuan/FreedomWalletBot.git
)

echo.
echo [3/5] Verifying remote...
git remote -v
echo.

echo [4/5] Checking branch...
git branch --show-current >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo    No branch detected. Will create 'main' on first commit.
) else (
    for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
    echo    Current branch: %CURRENT_BRANCH%
    if NOT "%CURRENT_BRANCH%"=="main" (
        echo    Renaming branch to 'main'...
        git branch -M main
    )
)

echo.
echo [5/5] Ready to push!
echo.
echo ========================================
echo   NEXT STEPS:
echo ========================================
echo.
echo 1. Make sure you created repository on GitHub:
echo    https://github.com/new
echo    Repository name: FreedomWalletBot
echo    Private: YES
echo.
echo 2. Add and commit your files:
echo    git add .
echo    git commit -m "Initial commit: Production deployment system"
echo.
echo 3. Push to GitHub:
echo    git push -u origin main
echo.
echo ========================================
echo.

set /p proceed="Do you want to commit and push now? (yes/no): "
if /i "%proceed%"=="yes" (
    echo.
    echo Committing all files...
    git add .
    
    set /p commit_msg="Enter commit message (or press Enter for default): "
    if "%commit_msg%"=="" set commit_msg=Initial commit: Production deployment system
    
    git commit -m "%commit_msg%"
    
    echo.
    echo Pushing to GitHub...
    echo.
    echo NOTE: You may need to authenticate with GitHub.
    echo       Use GitHub CLI (gh auth login) or Personal Access Token.
    echo.
    
    git push -u origin main
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo   SUCCESS! Code pushed to GitHub!
        echo ========================================
        echo.
        echo View your repository:
        echo https://github.com/mettatuan/FreedomWalletBot
        echo.
    ) else (
        echo.
        echo ========================================
        echo   AUTHENTICATION REQUIRED
        echo ========================================
        echo.
        echo Option 1: Use GitHub CLI (Easiest)
        echo    winget install --id GitHub.cli
        echo    gh auth login
        echo    git push -u origin main
        echo.
        echo Option 2: Use Personal Access Token
        echo    1. Create token: https://github.com/settings/tokens
        echo    2. Run: git push -u origin main
        echo    3. Username: mettatuan
        echo    4. Password: [PASTE YOUR TOKEN]
        echo.
        echo See GITHUB_SETUP_GUIDE.md for detailed instructions.
        echo.
    )
) else (
    echo.
    echo Setup completed. Run these commands manually:
    echo.
    echo    git add .
    echo    git commit -m "Initial commit"
    echo    git push -u origin main
    echo.
)

pause
