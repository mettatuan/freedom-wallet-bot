@echo off
REM FreedomWalletBot - Quick Start Script
REM Run this to start the bot

echo ========================================
echo   FREEDOM WALLET BOT - STARTING
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please create .env file first
    echo See .env.example for template
    pause
    exit /b 1
)

REM Check if local venv exists
if not exist .venv\Scripts\python.exe (
    echo [ERROR] Virtual environment not found!
    echo Creating virtual environment...
    python -m venv .venv
    echo Installing dependencies...
    .venv\Scripts\pip.exe install -r requirements.txt
)

echo [1/3] Checking dependencies...
.venv\Scripts\pip.exe show python-telegram-bot >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    .venv\Scripts\pip.exe install -r requirements.txt
)

echo.
echo [2/3] Starting bot...
echo.
echo ========================================
echo   BOT IS RUNNING (using local .venv)
echo   Press Ctrl+C to stop
echo ========================================
echo.

.venv\Scripts\python.exe main.py
