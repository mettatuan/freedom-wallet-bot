@echo off
REM ============================================
REM Quick Deployment Script (Batch version)
REM ============================================
REM Simple wrapper for deploy.ps1
REM ============================================

cd /d D:\FreedomWalletBot

echo.
echo ████████████████████████████████████████
echo    FREEDOMWALLETBOT DEPLOYMENT
echo ████████████████████████████████████████
echo.

REM Run PowerShell deployment script
powershell.exe -ExecutionPolicy Bypass -File "scripts\deploy.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Deployment completed successfully!
) else (
    echo.
    echo ❌ Deployment failed!
    echo Check logs for details.
)

echo.
pause
