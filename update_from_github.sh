#!/bin/bash

# ============================================================
# VPS UPDATE SCRIPT
# Chạy script này trên VPS để pull code mới từ GitHub
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
BOT_DIR="${BOT_DIR:-/root/FreedomWalletBot}"
BRANCH="${BRANCH:-cleanup/hard-refactor}"

echo -e "\n${CYAN}============================================================${NC}"
echo -e "${CYAN}🔄 UPDATING FREEDOM WALLET BOT${NC}"
echo -e "${CYAN}============================================================${NC}\n"

# ============================================================
# STEP 1: Check current directory
# ============================================================
echo -e "${YELLOW}STEP 1: Checking environment...${NC}"

if [ ! -d "$BOT_DIR" ]; then
    echo -e "${RED}  ❌ Bot directory not found: $BOT_DIR${NC}"
    echo -e "${YELLOW}  Run initial setup first (see docs/git-deployment.md)${NC}"
    exit 1
fi

cd "$BOT_DIR"
echo -e "${GREEN}  ✅ Working directory: $BOT_DIR${NC}"

# ============================================================
# STEP 2: Backup database
# ============================================================
echo -e "\n${YELLOW}STEP 2: Backing up database...${NC}"

mkdir -p data/backups

if [ -f data/bot.db ]; then
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).db"
    cp data/bot.db "data/backups/$BACKUP_NAME"
    echo -e "${GREEN}  ✅ Database backed up: $BACKUP_NAME${NC}"
else
    echo -e "${GRAY}  ℹ️  No database to backup (first deploy)${NC}"
fi

# ============================================================
# STEP 3: Check Git status
# ============================================================
echo -e "\n${YELLOW}STEP 3: Checking Git status...${NC}"

# Show current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${GRAY}  Current branch: $CURRENT_BRANCH${NC}"

# Show current commit
CURRENT_COMMIT=$(git log -1 --oneline)
echo -e "${GRAY}  Current commit: $CURRENT_COMMIT${NC}"

# Check for local changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}  ⚠️  Local changes detected:${NC}"
    git status --short
    
    echo -e "\n${YELLOW}  Stashing local changes...${NC}"
    git stash
    echo -e "${GREEN}  ✅ Changes stashed${NC}"
fi

# ============================================================
# STEP 4: Pull latest code
# ============================================================
echo -e "\n${YELLOW}STEP 4: Pulling latest code from GitHub...${NC}"

# Fetch latest
git fetch origin

# Pull
echo -e "${GRAY}  → Pulling branch: $BRANCH${NC}"
git pull origin "$BRANCH"

# Show new commit
NEW_COMMIT=$(git log -1 --oneline)
echo -e "${GREEN}  ✅ Updated to: $NEW_COMMIT${NC}"

# Count changes
CHANGED_FILES=$(git diff --name-only HEAD@{1} HEAD 2>/dev/null | wc -l)
if [ "$CHANGED_FILES" -gt 0 ]; then
    echo -e "${GRAY}  Changed files: $CHANGED_FILES${NC}"
else
    echo -e "${GRAY}  No changes (already up to date)${NC}"
fi

# ============================================================
# STEP 5: Update dependencies
# ============================================================
echo -e "\n${YELLOW}STEP 5: Updating dependencies...${NC}"

# Activate virtual environment
if [ ! -d .venv ]; then
    echo -e "${YELLOW}  Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

# Install/update dependencies
echo -e "${GRAY}  → Installing requirements...${NC}"
pip install -r requirements.txt --quiet

echo -e "${GREEN}  ✅ Dependencies updated${NC}"

# ============================================================
# STEP 6: Run database migration
# ============================================================
echo -e "\n${YELLOW}STEP 6: Running database migration...${NC}"

if [ -f migrate_database.py ]; then
    python migrate_database.py
    echo -e "${GREEN}  ✅ Migration complete${NC}"
else
    echo -e "${GRAY}  ℹ️  No migration script found (skipping)${NC}"
fi

# ============================================================
# STEP 7: Restart bot
# ============================================================
echo -e "\n${YELLOW}STEP 7: Restarting bot...${NC}"

# Check if systemd service exists
if command -v systemctl &> /dev/null && systemctl list-units --full -all | grep -q freedom-wallet-bot; then
    echo -e "${GRAY}  → Restarting via systemd...${NC}"
    sudo systemctl restart freedom-wallet-bot
    
    sleep 2
    
    if sudo systemctl is-active --quiet freedom-wallet-bot; then
        echo -e "${GREEN}  ✅ Bot restarted via systemd${NC}"
    else
        echo -e "${RED}  ❌ Systemd restart failed!${NC}"
        echo -e "${YELLOW}  Check status: sudo systemctl status freedom-wallet-bot${NC}"
        exit 1
    fi
else
    # Fallback to manual restart
    echo -e "${GRAY}  → Restarting manually...${NC}"
    
    # Kill old process
    pkill -f "python.*main.py" || echo "  No old process found"
    sleep 2
    
    # Start new process
    mkdir -p logs
    nohup python main.py > logs/bot.log 2>&1 &
    
    sleep 3
    
    # Verify
    if pgrep -f "python.*main.py" > /dev/null; then
        PID=$(pgrep -f "python.*main.py")
        echo -e "${GREEN}  ✅ Bot restarted (PID: $PID)${NC}"
    else
        echo -e "${RED}  ❌ Bot failed to start!${NC}"
        echo -e "${YELLOW}  Check logs: tail -50 logs/bot.log${NC}"
        exit 1
    fi
fi

# ============================================================
# STEP 8: Verify deployment
# ============================================================
echo -e "\n${YELLOW}STEP 8: Verifying deployment...${NC}"

sleep 2

# Check process
if pgrep -f "python.*main.py" > /dev/null; then
    PID=$(pgrep -f "python.*main.py")
    echo -e "${GREEN}  ✅ Bot is running (PID: $PID)${NC}"
else
    echo -e "${RED}  ❌ Bot is not running!${NC}"
    exit 1
fi

# Show recent logs
echo -e "\n${GRAY}Recent logs:${NC}"
tail -10 logs/bot.log

# ============================================================
# SUMMARY
# ============================================================
echo -e "\n${CYAN}============================================================${NC}"
echo -e "${GREEN}✅ UPDATE COMPLETE!${NC}"
echo -e "${CYAN}============================================================${NC}"

echo -e "\nCurrent version:"
echo -e "  Commit: $(git log -1 --oneline)"
echo -e "  Branch: $(git branch --show-current)"
echo -e "  Updated: $(date '+%Y-%m-%d %H:%M:%S')"

if [ -d data/backups ]; then
    BACKUP_COUNT=$(ls -1 data/backups/ | wc -l)
    echo -e "\nBackups: $BACKUP_COUNT backups in data/backups/"
fi

echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "${GRAY}  View logs:    tail -f logs/bot.log${NC}"
echo -e "${GRAY}  Check status: pgrep -fa python${NC}"
echo -e "${GRAY}  Restart bot:  sudo systemctl restart freedom-wallet-bot${NC}"
echo -e "${GRAY}  Rollback:     git reset --hard HEAD~1${NC}"

echo -e "\n${GREEN}🎉 Bot is now running latest version!${NC}\n"
