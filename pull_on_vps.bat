@echo off
REM ================================================
REM VPS: Pull Latest Code from Git
REM ================================================

cd /d C:\Projects\FreedomWalletBot

echo [INFO] Stopping bot if running...
taskkill /F /IM python.exe 2>nul

echo.
echo [1/3] Fetching latest changes...
git fetch origin main

echo.
echo [2/3] Pulling code...
git pull origin main

echo.
echo [3/3] Installing dependencies...
call .venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo.
echo [DONE] Code updated!
echo.
echo [START BOT] Run: python main.py
pause
