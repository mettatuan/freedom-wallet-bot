#!/bin/bash

# ============================================================
# VPS PREREQUISITES CHECKER
# Run this to check if VPS is ready for deployment
# ============================================================

echo "🔍 Checking VPS prerequisites..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# ============================================================
# 1. Check Python version
# ============================================================
echo -n "Checking Python version... "
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
    echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python $PYTHON_VERSION (need 3.10+)${NC}"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================
# 2. Check pip
# ============================================================
echo -n "Checking pip... "
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version | grep -oP '\d+\.\d+')
    echo -e "${GREEN}✅ pip $PIP_VERSION${NC}"
else
    echo -e "${RED}❌ pip not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================
# 3. Check virtualenv
# ============================================================
echo -n "Checking venv module... "
if python3 -m venv --help &> /dev/null; then
    echo -e "${GREEN}✅ venv available${NC}"
else
    echo -e "${RED}❌ venv module not found${NC}"
    echo -e "${YELLOW}   Install: apt install python3-venv${NC}"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================
# 4. Check disk space
# ============================================================
echo -n "Checking disk space... "
AVAILABLE=$(df -BM . | tail -1 | awk '{print $4}' | sed 's/M//')
if [ "$AVAILABLE" -gt 500 ]; then
    echo -e "${GREEN}✅ ${AVAILABLE}MB available${NC}"
else
    echo -e "${RED}❌ Only ${AVAILABLE}MB available (need 500MB+)${NC}"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================
# 5. Check RAM
# ============================================================
echo -n "Checking RAM... "
TOTAL_RAM=$(free -m | grep Mem | awk '{print $2}')
if [ "$TOTAL_RAM" -gt 512 ]; then
    echo -e "${GREEN}✅ ${TOTAL_RAM}MB RAM${NC}"
else
    echo -e "${YELLOW}⚠️  Only ${TOTAL_RAM}MB RAM (512MB+ recommended)${NC}"
fi

# ============================================================
# 6. Check internet connection
# ============================================================
echo -n "Checking internet... "
if curl -s --max-time 5 https://api.telegram.org > /dev/null; then
    echo -e "${GREEN}✅ Can reach Telegram API${NC}"
else
    echo -e "${RED}❌ Cannot reach Telegram API${NC}"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================
# 7. Check if bot directory exists
# ============================================================
echo -n "Checking bot directory... "
BOT_DIR="/root/FreedomWalletBot"
if [ -d "$BOT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory exists: $BOT_DIR${NC}"
    echo -e "${YELLOW}   Deployment will overwrite files${NC}"
else
    echo -e "${GREEN}✅ Directory ready to create${NC}"
fi

# ============================================================
# 8. Check .env file
# ============================================================
echo -n "Checking .env file... "
if [ -f "$BOT_DIR/.env" ]; then
    if grep -q "TELEGRAM_BOT_TOKEN=" "$BOT_DIR/.env"; then
        echo -e "${GREEN}✅ .env exists with token${NC}"
    else
        echo -e "${YELLOW}⚠️  .env exists but no token found${NC}"
    fi
else
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}   Create .env with: TELEGRAM_BOT_TOKEN=your_token${NC}"
    ERRORS=$((ERRORS + 1))
fi

# ============================================================
# 9. Check if old bot is running
# ============================================================
echo -n "Checking for running bot... "
if pgrep -f 'python.*main.py' > /dev/null; then
    PID=$(pgrep -f 'python.*main.py')
    echo -e "${YELLOW}⚠️  Bot is running (PID: $PID)${NC}"
    echo -e "${YELLOW}   Deployment will stop and restart it${NC}"
else
    echo -e "${GREEN}✅ No bot running${NC}"
fi

# ============================================================
# 10. Check systemd (optional)
# ============================================================
echo -n "Checking systemd... "
if command -v systemctl &> /dev/null; then
    echo -e "${GREEN}✅ systemd available${NC}"
    echo -e "${YELLOW}   Recommended: Setup auto-restart service${NC}"
else
    echo -e "${YELLOW}⚠️  systemd not available (not critical)${NC}"
fi

# ============================================================
# Summary
# ============================================================
echo ""
echo "============================================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ VPS is ready for deployment!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Create .env file with TELEGRAM_BOT_TOKEN (if not exists)"
    echo "2. Run deploy script from local machine"
    echo ""
    echo "Windows:"
    echo "  .\deploy_to_vps.ps1 -VPS_HOST \"your_ip\" -VPS_USER \"root\" -VPS_PATH \"$BOT_DIR\""
    echo ""
    echo "Linux/Mac:"
    echo "  ./deploy_to_vps.sh"
else
    echo -e "${RED}❌ Found $ERRORS critical issue(s)${NC}"
    echo ""
    echo "Fix required issues before deploying."
fi
echo "============================================================"

exit $ERRORS
