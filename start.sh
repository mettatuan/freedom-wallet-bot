#!/bin/bash
# FreedomWalletBot - Quick Start Script (Linux/Mac)

echo "========================================"
echo "  FREEDOM WALLET BOT - STARTING"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    echo "Please create .env file first"
    echo "See .env.example for template"
    exit 1
fi

# Check Python installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python not installed!"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "[1/3] Checking dependencies..."
if ! python3 -c "import telegram" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "[2/3] Running connectivity test..."
python3 test_api_url.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] API connectivity failed!"
    echo "Please check FREEDOM_WALLET_API_URL in .env"
    exit 1
fi

echo ""
echo "[3/3] Starting bot..."
echo ""
echo "========================================"
echo "  BOT IS RUNNING"
echo "  Press Ctrl+C to stop"
echo "========================================"
echo ""

python3 main.py
