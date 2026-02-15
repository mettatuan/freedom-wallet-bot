@echo off
REM ================================================
REM Quick Git Push Script
REM ================================================

cd /d D:\Projects\FreedomWalletBot

echo [1/3] Checking Git status...
git status

echo.
echo [2/3] Adding all changes...
git add .

echo.
echo [3/3] Committing and pushing...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update: Sync to VPS

git commit -m "%commit_msg%"
git push origin main

echo.
echo [DONE] Code pushed to Git!
echo.
echo [NEXT] On VPS, run: git pull origin main
pause
