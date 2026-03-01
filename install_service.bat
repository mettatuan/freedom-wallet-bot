@echo off
REM Register FreedomWalletBot as a scheduled task running as SYSTEM
REM This ensures bot survives RDP disconnects

REM Create wrapper script that sets working directory
echo @echo off > C:\FreedomWalletBot\run_bot.bat
echo cd /d C:\FreedomWalletBot >> C:\FreedomWalletBot\run_bot.bat
echo C:\FreedomWalletBot\.venv\Scripts\python.exe main.py >> C:\FreedomWalletBot\run_bot.bat

schtasks /delete /tn "FreedomWalletBot" /f 2>nul
echo Creating task...

schtasks /create ^
    /tn "FreedomWalletBot" ^
    /tr "C:\FreedomWalletBot\run_bot.bat" ^
    /sc ONSTART ^
    /ru SYSTEM ^
    /delay 0001:00 ^
    /f

echo Task created. Running now...
schtasks /run /tn "FreedomWalletBot"

echo Waiting 6 seconds...
timeout /t 6 /nobreak > nul

echo Process check:
tasklist /FI "IMAGENAME eq python.exe"

echo Session check:
tasklist /FI "IMAGENAME eq python.exe" /FO LIST
