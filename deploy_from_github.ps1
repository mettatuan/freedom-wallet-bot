# ============================================================
# DEPLOY FROM GITHUB TO VPS
# Chạy script này từ máy Windows để deploy code lên VPS
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$VPS_HOST,
    
    [Parameter(Mandatory=$true)]
    [string]$VPS_USER = "root",
    
    [string]$VPS_PATH = "/root/FreedomWalletBot",
    [string]$BRANCH = "cleanup/hard-refactor",
    [switch]$SetupFirstTime = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY FROM GITHUB TO VPS" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "VPS: $VPS_USER@$VPS_HOST" -ForegroundColor White
Write-Host "Path: $VPS_PATH" -ForegroundColor White
Write-Host "Branch: $BRANCH`n" -ForegroundColor White

# ============================================================
# FIRST TIME SETUP
# ============================================================
if ($SetupFirstTime) {
    Write-Host "🔧 FIRST TIME SETUP MODE" -ForegroundColor Yellow
    Write-Host "This will clone the repo and setup the bot on VPS`n" -ForegroundColor Yellow
    
    $setupScript = @'
#!/bin/bash
set -e

echo "📥 Cloning repository..."
cd /root
if [ -d "FreedomWalletBot" ]; then
    echo "⚠️  Directory exists, removing..."
    rm -rf FreedomWalletBot
fi

git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
cd FreedomWalletBot

echo "🔀 Checking out branch: {BRANCH}..."
git checkout {BRANCH}

echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "📝 Creating .env file..."
cat > .env << 'ENVEOF'
TELEGRAM_BOT_TOKEN=REPLACE_WITH_YOUR_TOKEN
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
ENVEOF

chmod 600 .env

echo "🔄 Running database migration..."
python migrate_database.py

echo "📋 Making update script executable..."
chmod +x update_from_github.sh

echo ""
echo "============================================================"
echo "✅ SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your bot token:"
echo "   nano /root/FreedomWalletBot/.env"
echo ""
echo "2. Start the bot:"
echo "   cd /root/FreedomWalletBot"
echo "   source .venv/bin/activate"
echo "   nohup python main.py > logs/bot.log 2>&1 &"
echo ""
echo "3. Or setup systemd service (recommended)"
echo ""
'@ -replace '{BRANCH}', $BRANCH
    
    Write-Host "Uploading and running setup script..." -ForegroundColor Gray
    
    $setupScript | ssh "$VPS_USER@$VPS_HOST" "bash -s"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ First time setup complete!" -ForegroundColor Green
        Write-Host "`n⚠️  IMPORTANT: Edit .env file with your bot token:" -ForegroundColor Yellow
        Write-Host "ssh $VPS_USER@$VPS_HOST 'nano $VPS_PATH/.env'" -ForegroundColor Gray
    } else {
        Write-Host "`n❌ Setup failed!" -ForegroundColor Red
        exit 1
    }
    
    exit 0
}

# ============================================================
# UPDATE EXISTING INSTALLATION
# ============================================================
Write-Host "🔄 Updating bot from GitHub..." -ForegroundColor Yellow

# Upload update script if not exists
Write-Host "`n→ Checking update script..." -ForegroundColor Gray
$scriptExists = ssh "$VPS_USER@$VPS_HOST" "test -f $VPS_PATH/update_from_github.sh && echo 'exists'"

if ($scriptExists -ne "exists") {
    Write-Host "  → Uploading update_from_github.sh..." -ForegroundColor Gray
    scp update_from_github.sh "$VPS_USER@${VPS_HOST}:$VPS_PATH/"
    ssh "$VPS_USER@$VPS_HOST" "chmod +x $VPS_PATH/update_from_github.sh"
    Write-Host "  ✅ Script uploaded" -ForegroundColor Green
} else {
    Write-Host "  ✅ Script exists" -ForegroundColor Green
}

# Run update script
Write-Host "`n→ Running update script on VPS..." -ForegroundColor Gray
Write-Host "============================================================`n" -ForegroundColor Cyan

ssh "$VPS_USER@$VPS_HOST" "cd $VPS_PATH && BRANCH=$BRANCH BOT_DIR=$VPS_PATH ./update_from_github.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "============================================================`n" -ForegroundColor Cyan
    
    Write-Host "View logs with:" -ForegroundColor Yellow
    Write-Host "ssh $VPS_USER@$VPS_HOST 'tail -f $VPS_PATH/logs/bot.log'" -ForegroundColor Gray
} else {
    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "❌ DEPLOYMENT FAILED!" -ForegroundColor Red
    Write-Host "============================================================`n" -ForegroundColor Cyan
    
    Write-Host "Check logs with:" -ForegroundColor Yellow
    Write-Host "ssh $VPS_USER@$VPS_HOST 'tail -50 $VPS_PATH/logs/bot.log'" -ForegroundColor Gray
    
    exit 1
}
