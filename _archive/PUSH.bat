@echo off
REM Quick Push - Windows Batch File
REM Double-click this file to push changes to GitHub

powershell -ExecutionPolicy Bypass -File "%~dp0quick_push.ps1" "Update: %date% %time%"
pause
