# ============================================================
# Script chay tren VPS Windows - Pull code tu GitHub va chay bot
# 1. Ket noi RDP vao VPS
# 2. Mo PowerShell (Run as Administrator)
# 3. Dan va chay toan bo script nay
# ============================================================

$REPO_URL   = "https://github.com/mettatuan/freedom-wallet-bot.git"
$BRANCH     = "cleanup/hard-refactor"
$BOT_DIR    = "C:\FreedomWalletBot"
$PYTHON_CMD = "python"   # doi thanh "python3" neu can

Write-Host "`n===================================" -ForegroundColor Cyan
Write-Host "  FreedomWalletBot - VPS Setup" -ForegroundColor Cyan
Write-Host "===================================`n" -ForegroundColor Cyan

# --- 1. Kiem tra Git ---
Write-Host "[1/6] Kiem tra Git..." -ForegroundColor Yellow
$gitVer = git --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Git chua cai. Dang tai..." -ForegroundColor Red
    winget install --id Git.Git -e --source winget
    $env:PATH += ";C:\Program Files\Git\bin"
} else {
    Write-Host "  OK: $gitVer" -ForegroundColor Green
}

# --- 2. Kiem tra Python ---
Write-Host "`n[2/6] Kiem tra Python..." -ForegroundColor Yellow
$pyVer = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Python chua cai. Vui long cai tu https://python.org" -ForegroundColor Red
    Start-Process "https://www.python.org/downloads/"
    pause
} else {
    Write-Host "  OK: $pyVer" -ForegroundColor Green
}

# --- 3. Clone hoac pull repo ---
Write-Host "`n[3/6] Lay code tu GitHub..." -ForegroundColor Yellow
if (Test-Path "$BOT_DIR\.git") {
    Write-Host "  Repo da ton tai, dang pull..." -ForegroundColor Gray
    cd $BOT_DIR
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
    Write-Host "  OK: da cap nhat code moi nhat" -ForegroundColor Green
} else {
    Write-Host "  Clone repo moi..." -ForegroundColor Gray
    git clone -b $BRANCH $REPO_URL $BOT_DIR
    Write-Host "  OK: Clone thanh cong" -ForegroundColor Green
}

cd $BOT_DIR

# --- 4. Cai dependencies ---
Write-Host "`n[4/6] Cai thu vien Python..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Dependencies da cai" -ForegroundColor Green
} else {
    Write-Host "  Loi khi cai thu vien!" -ForegroundColor Red
}

# --- 5. Kiem tra .env ---
Write-Host "`n[5/6] Kiem tra file .env..." -ForegroundColor Yellow
if (Test-Path "$BOT_DIR\.env") {
    Write-Host "  OK: .env ton tai" -ForegroundColor Green
} else {
    Write-Host "  CANH BAO: Chua co file .env!" -ForegroundColor Red
    Write-Host "  Can copy file .env tu may local len VPS" -ForegroundColor Red
    Write-Host "  Su dung RDP clipboard de copy noi dung .env" -ForegroundColor Yellow
    
    # Tao file .env mau de dien
    @"
# Dien thong tin vao day
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_USER_ID=your_admin_id
ADMIN_SUPPORT_SHEET_ID=1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
PAYMENT_BANK_NAME=OCB
PAYMENT_ACCOUNT_NAME=PHAM THANH TUAN
PAYMENT_ACCOUNT_NUMBER=0937833239
"@ | Set-Content "$BOT_DIR\.env.example"
    Write-Host "  Da tao .env.example - copy va doi ten thanh .env" -ForegroundColor Yellow
    notepad "$BOT_DIR\.env.example"
    pause
    Rename-Item "$BOT_DIR\.env.example" ".env" -ErrorAction SilentlyContinue
}

# --- 6. Tao thu muc can thiet va chay bot ---
Write-Host "`n[6/6] Khoi dong bot..." -ForegroundColor Yellow

# Tao thu muc logs va data neu chua co
New-Item -ItemType Directory -Force -Path "$BOT_DIR\data\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$BOT_DIR\logs" | Out-Null

# Dung bot cu neu dang chay
$oldBot = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
if ($oldBot) {
    $oldBot | Stop-Process -Force
    Write-Host "  Da dung bot cu" -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

# Chay bot trong cua so moi
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$BOT_DIR'; python main.py`"" -WindowStyle Normal

Write-Host "  Bot dang khoi dong trong cua so moi!" -ForegroundColor Green

Write-Host "`n===================================" -ForegroundColor Cyan
Write-Host "  Hoan thanh! Bot dang chay." -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "`n  Xem log: Get-Content '$BOT_DIR\logs\bot_stdout.log' -Wait`n"
