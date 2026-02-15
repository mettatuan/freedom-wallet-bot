@echo off
REM ================================================
REM Sync FreedomWalletBot local to VPS Windows
REM ================================================

echo [INFO] Starting sync to VPS...
echo.

REM VPS Configuration
set VPS_IP=103.69.190.75
set VPS_USER=Administrator
set VPS_PATH=\\%VPS_IP%\C$\Projects\FreedomWalletBot
set LOCAL_PATH=D:\Projects\FreedomWalletBot

REM Check network connectivity
echo [CHECK] Testing VPS connection...
ping -n 1 %VPS_IP% >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot reach VPS at %VPS_IP%
    echo [TIP] Check VPS is running and network is accessible
    pause
    exit /b 1
)

echo [OK] VPS is reachable
echo.

REM Map network drive (optional, helps with authentication)
echo [INFO] Mapping network drive...
net use Z: %VPS_PATH% /user:%VPS_USER% /persistent:no

REM Sync files using robocopy
echo [SYNC] Syncing files to VPS...
echo.

robocopy "%LOCAL_PATH%" "%VPS_PATH%" ^
    /MIR ^
    /XD ".venv" "__pycache__" ".git" "database" "logs" "backup" "_archive" ".pytest_cache" "media\images" ^
    /XF "*.log" "*.db" "*.db-journal" "*.pyc" "google_service_account.json" ".env" "sync_to_vps.bat" ^
    /R:2 ^
    /W:5 ^
    /NFL ^
    /NDL ^
    /NP ^
    /NS ^
    /NC

REM Cleanup
net use Z: /delete /y >nul 2>&1

echo.
echo [DONE] Sync completed!
echo.
echo [NEXT STEPS]
echo 1. RDP to VPS: mstsc /v:%VPS_IP%
echo 2. Navigate to: C:\Projects\FreedomWalletBot
echo 3. Activate venv: .venv\Scripts\activate
echo 4. Install deps: pip install -r requirements.txt
echo 5. Restart bot: python main.py
echo.

pause
