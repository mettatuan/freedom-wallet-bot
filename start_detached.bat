@echo off
REM Starts bot as a truly detached process using Task Scheduler
schtasks /delete /tn "FreedomWalletBot" /f 2>nul
schtasks /create /f /tn "FreedomWalletBot" /tr "\"C:\FreedomWalletBot\.venv\Scripts\python.exe\" \"C:\FreedomWalletBot\main.py\"" /sc ONCE /st 00:00 /sd 01/01/2099 /rl HIGHEST
schtasks /run /tn "FreedomWalletBot"
timeout /t 3 /nobreak > nul
tasklist /FI "IMAGENAME eq python.exe"
