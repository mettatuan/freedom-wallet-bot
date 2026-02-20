#!/bin/bash

# ============================================================
# FREEDOM WALLET BOT - VPS DEPLOYMENT SCRIPT (Linux/Mac)
# Phase 2-3 Complete Version
# ============================================================

set -e  # Exit on error

# Configuration (edit these)
VPS_HOST="${VPS_HOST:-your_vps_ip}"
VPS_USER="${VPS_USER:-your_username}"
VPS_PATH="${VPS_PATH:-/home/your_username/FreedomWalletBot}"
SKIP_TESTS="${SKIP_TESTS:-false}"
DRY_RUN="${DRY_RUN:-false}"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "\n${CYAN}============================================================${NC}"
echo -e "${CYAN}🚀 FREEDOM WALLET BOT - VPS DEPLOYMENT${NC}"
echo -e "${CYAN}============================================================${NC}\n"

# ============================================================
# STEP 1: Pre-deployment checks
# ============================================================
echo -e "${YELLOW}STEP 1: Pre-deployment checks...${NC}"

if [ "$SKIP_TESTS" != "true" ]; then
    echo -e "${GRAY}  → Running Phase 3 tests...${NC}"
    
    if ! python test_phase3.py; then
        echo -e "${RED}  ❌ Tests failed! Fix errors before deploying.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}  ✅ All tests passed!${NC}"
else
    echo -e "${YELLOW}  ⚠️ Skipping tests!${NC}"
fi

# Check SSH connection
echo -e "\n${GRAY}  → Testing SSH connection to VPS...${NC}"

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${GRAY}  [DRY RUN] Would test: ssh $VPS_USER@$VPS_HOST${NC}"
else
    if ! ssh -o ConnectTimeout=10 "$VPS_USER@$VPS_HOST" "echo 'SSH OK'" > /dev/null 2>&1; then
        echo -e "${RED}  ❌ Cannot connect to VPS. Check SSH config.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}  ✅ SSH connection successful!${NC}"
fi

# ============================================================
# STEP 2: Backup VPS database
# ============================================================
echo -e "\n${YELLOW}STEP 2: Backing up VPS database...${NC}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="vps_backup_$TIMESTAMP.db"

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${GRAY}  [DRY RUN] Would backup: $VPS_PATH/data/bot.db${NC}"
else
    ssh "$VPS_USER@$VPS_HOST" << EOF
mkdir -p $VPS_PATH/data/backups
if [ -f $VPS_PATH/data/bot.db ]; then
    cp $VPS_PATH/data/bot.db $VPS_PATH/data/backups/$BACKUP_NAME
    echo 'Backup created: $BACKUP_NAME'
else
    echo 'No existing database to backup'
fi
EOF
    
    echo -e "${GREEN}  ✅ Database backed up: $BACKUP_NAME${NC}"
fi

# ============================================================
# STEP 3: Stop bot on VPS
# ============================================================
echo -e "\n${YELLOW}STEP 3: Stopping bot on VPS...${NC}"

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${GRAY}  [DRY RUN] Would stop bot process${NC}"
else
    ssh "$VPS_USER@$VPS_HOST" << 'EOF'
pkill -f 'python.*main.py' || echo 'No bot process found'
sleep 2
EOF
    
    echo -e "${GREEN}  ✅ Bot stopped${NC}"
fi

# ============================================================
# STEP 4: Upload files to VPS
# ============================================================
echo -e "\n${YELLOW}STEP 4: Uploading files to VPS...${NC}"

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${GRAY}  [DRY RUN] Would upload with rsync${NC}"
else
    echo -e "${GRAY}  → Syncing files...${NC}"
    
    rsync -avz --progress \
        --exclude='.git' \
        --exclude='.venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='data/bot.db' \
        --exclude='data/backups' \
        --exclude='logs/*.log' \
        --exclude='.env' \
        --exclude='*.backup' \
        --exclude='node_modules' \
        --exclude='.vscode' \
        ./ "$VPS_USER@$VPS_HOST:$VPS_PATH/"
    
    echo -e "${GREEN}  ✅ Files uploaded successfully!${NC}"
fi

# ============================================================
# STEP 5: Install dependencies on VPS
# ============================================================
echo -e "\n${YELLOW}STEP 5: Installing dependencies on VPS...${NC}"

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${GRAY}  [DRY RUN] Would install dependencies${NC}"
else
    ssh "$VPS_USER@$VPS_HOST" << EOF
cd $VPS_PATH

# Create virtual environment if not exists
if [ ! -d .venv ]; then
    echo 'Creating virtual environment...'
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo 'Dependencies installed!'
EOF
    
    echo -e "${GREEN}  ✅ Dependencies installed!${NC}"
fi

# ============================================================
# STEP 6: Run database migration
# ============================================================
echo -e "\n${YELLOW}STEP 6: Running database migration...${NC}"

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${GRAY}  [DRY RUN] Would run: python migrate_database.py${NC}"
else
    ssh "$VPS_USER@$VPS_HOST" << EOF
cd $VPS_PATH
source .venv/bin/activate
python migrate_database.py
EOF
    
    echo -e "${GREEN}  ✅ Database migration complete!${NC}"
fi

# ============================================================
# STEP 7: Start bot on VPS
# ============================================================
echo -e "\n${YELLOW}STEP 7: Starting bot on VPS...${NC}"

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${GRAY}  [DRY RUN] Would start bot with nohup${NC}"
else
    ssh "$VPS_USER@$VPS_HOST" << EOF
cd $VPS_PATH
source .venv/bin/activate

# Create logs directory
mkdir -p logs

# Start bot in background with nohup
nohup python main.py > logs/bot.log 2>&1 &

# Wait a moment
sleep 3

# Check if bot started
if pgrep -f 'python.*main.py' > /dev/null; then
    echo 'Bot started successfully!'
    exit 0
else
    echo 'Bot failed to start! Check logs/bot.log'
    exit 1
fi
EOF
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ Bot started successfully!${NC}"
    else
        echo -e "${RED}  ❌ Bot failed to start!${NC}"
        echo -e "${YELLOW}     Check logs with: ssh $VPS_USER@$VPS_HOST 'tail -50 $VPS_PATH/logs/bot.log'${NC}"
        exit 1
    fi
fi

# ============================================================
# STEP 8: Verify deployment
# ============================================================
echo -e "\n${YELLOW}STEP 8: Verifying deployment...${NC}"

if [ "$DRY_RUN" = "true" ]; then
    echo -e "${GRAY}  [DRY RUN] Would verify bot status${NC}"
else
    sleep 2
    
    ssh "$VPS_USER@$VPS_HOST" << 'EOF'
cd $VPS_PATH

# Check process
PID=$(pgrep -f 'python.*main.py')
if [ -z "$PID" ]; then
    echo 'ERROR: Bot not running!'
    exit 1
fi

echo "✅ Bot running (PID: $PID)"

# Check recent logs
echo ""
echo "Recent logs:"
tail -10 logs/bot.log
EOF
fi

# ============================================================
# DEPLOYMENT SUMMARY
# ============================================================
echo -e "\n${CYAN}============================================================${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${CYAN}============================================================${NC}"

echo -e "\nDeployed to: $VPS_USER@$VPS_HOST"
echo -e "Path: $VPS_PATH"
echo -e "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"

if [ "$DRY_RUN" != "true" ]; then
    echo -e "\n${YELLOW}Useful commands:${NC}"
    echo -e "${GRAY}  View logs:    ssh $VPS_USER@$VPS_HOST 'tail -f $VPS_PATH/logs/bot.log'${NC}"
    echo -e "${GRAY}  Stop bot:     ssh $VPS_USER@$VPS_HOST 'pkill -f python.*main.py'${NC}"
    echo -e "${GRAY}  Restart bot:  ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && nohup python main.py > logs/bot.log 2>&1 &'${NC}"
    echo -e "${GRAY}  Check status: ssh $VPS_USER@$VPS_HOST 'pgrep -fa python.*main.py'${NC}"
fi

echo -e "\n${GREEN}🎉 Bot is now live on VPS!${NC}\n"
