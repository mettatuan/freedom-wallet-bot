# 🎯 DEPLOY LÊN WINDOWS VPS - KHÔNG CẦN SSH

**Tình huống:** Máy local và VPS đều Windows, không có SSH

**VPS:** 103.69.190.75 (Windows Server 2016)  
**User:** administrator

---

## 🚀 CÁCH ĐƠN GIẢN NHẤT: RDP VÀO VPS

### Bước 1: Kết nối RDP

```
1. Nhấn Windows Key + R
2. Gõ: mstsc
3. Computer: 103.69.190.75
4. User name: administrator
5. Click "Connect"
6. Nhập password
```

### Bước 2: Trên VPS, mở PowerShell

```powershell
# Kiểm tra Git và Python
git --version
python --version

# Nếu chưa có, cài:
# Git: https://git-scm.com/download/win
# Python: https://www.python.org/downloads/
```

### Bước 3: Clone repo từ GitHub

```powershell
# Mở PowerShell
cd C:\

# Clone repo
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot

# Di chuyển vào thư mục
cd FreedomWalletBot

# Checkout branch đúng
git checkout cleanup/hard-refactor

# Xem files
dir
```

### Bước 4: Setup Python environment

```powershell
# Tạo virtual environment
python -m venv .venv

# Activate
& .\.venv\Scripts\Activate.ps1

# Nếu gặp lỗi "cannot be loaded", chạy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate lại
& .\.venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Cài dependencies
pip install -r requirements.txt
```

### Bước 5: Tạo file .env

```powershell
# Mở Notepad
notepad .env
```

**Gõ vào Notepad:**
```
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
```

**Lưu:** `Ctrl+S` → Đóng Notepad

### Bước 6: Tạo folders và run migration

```powershell
# Tạo thư mục
New-Item -ItemType Directory -Force -Path data\backups
New-Item -ItemType Directory -Force -Path logs

# Run migration
python migrate_database.py

# Kết quả:
# ✅ Migration complete!
# - 8 tables created
# - Users: 56 columns
# - Transactions: 9 columns
```

### Bước 7: Start bot

```powershell
# Start bot
python main.py

# Kết quả:
# 2026-02-20 10:30:45 | INFO | Application started
# 2026-02-20 10:30:46 | INFO | Bot polling started
```

**Bot đang chạy!** ✅

### Bước 8: Test trên Telegram

1. Mở Telegram, tìm bot của bạn
2. Gửi `/start` → Thấy keyboard 8 nút ✅
3. Gửi `35k ăn sáng` → Lưu giao dịch ✅
4. Click **📊 Tổng quan** → Thấy số dư ✅

---

## 🔄 CHẠY BOT TRONG BACKGROUND

Bot hiện đang chạy trong cửa sổ PowerShell. Nếu đóng cửa sổ, bot sẽ dừng.

### Cách 1: Start-Process (Đơn giản)

```powershell
# Nhấn Ctrl+C để dừng bot hiện tại

# Start bot ẩn
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\FreedomWalletBot; & .\.venv\Scripts\Activate.ps1; python main.py *> logs\bot.log" -WindowStyle Hidden

# Kiểm tra bot đã chạy
Get-Process python

# Xem logs
Get-Content logs\bot.log -Tail 50 -Wait
```

### Cách 2: Windows Task Scheduler (Tự động khởi động)

```powershell
# Tạo script start
@'
Set-Location C:\FreedomWalletBot
& .\.venv\Scripts\Activate.ps1
python main.py *> logs\bot.log
'@ | Out-File -FilePath C:\FreedomWalletBot\start_bot.ps1 -Encoding utf8

# Tạo scheduled task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\FreedomWalletBot\start_bot.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "administrator" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "FreedomWalletBot" -Action $action -Trigger $trigger -Principal $principal -Settings $settings

# Start task ngay
Start-ScheduledTask -TaskName "FreedomWalletBot"

# Kiểm tra status
Get-ScheduledTask -TaskName "FreedomWalletBot"
```

**Giờ bot sẽ tự chạy khi VPS khởi động!** ✅

---

## 📊 MONITORING & MANAGEMENT

### Xem logs

```powershell
# Xem 50 dòng cuối
Get-Content C:\FreedomWalletBot\logs\bot.log -Tail 50

# Xem real-time
Get-Content C:\FreedomWalletBot\logs\bot.log -Tail 20 -Wait
# Nhấn Ctrl+C để thoát
```

### Check bot status

```powershell
# Xem process
Get-Process python

# Kết quả:
# Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
# -------  ------    -----      -----     ------     --  -- -----------
#     234      15    45678      67890       1.23   1234   1 python
```

### Stop bot

```powershell
# Stop process
Stop-Process -Name python -Force

# Hoặc stop task
Stop-ScheduledTask -TaskName "FreedomWalletBot"
```

### Restart bot

```powershell
# Restart task
Restart-ScheduledTask -TaskName "FreedomWalletBot"

# Hoặc manual
Stop-Process -Name python -Force
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\FreedomWalletBot; & .\.venv\Scripts\Activate.ps1; python main.py *> logs\bot.log" -WindowStyle Hidden
```

---

## 🔄 UPDATE CODE (Khi có code mới)

### Bước 1: RDP vào VPS

### Bước 2: Stop bot

```powershell
# Stop bot
Stop-Process -Name python -Force

# Hoặc
Stop-ScheduledTask -TaskName "FreedomWalletBot"
```

### Bước 3: Backup database

```powershell
cd C:\FreedomWalletBot

# Backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item data\bot.db -Destination "data\backups\backup_$timestamp.db"
```

### Bước 4: Pull code mới

```powershell
# Pull từ GitHub
git pull origin cleanup/hard-refactor
```

### Bước 5: Update dependencies

```powershell
# Activate venv
& .\.venv\Scripts\Activate.ps1

# Update packages
pip install -r requirements.txt
```

### Bước 6: Run migration

```powershell
python migrate_database.py
```

### Bước 7: Restart bot

```powershell
# Restart task
Start-ScheduledTask -TaskName "FreedomWalletBot"

# Hoặc manual
python main.py
```

---

## 🔧 TROUBLESHOOTING

### ❌ Git not found

```powershell
# Download Git for Windows
# https://git-scm.com/download/win

# Hoặc dùng Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install git -y
```

### ❌ Python not found

```powershell
# Download Python 3.10+
# https://www.python.org/downloads/

# Hoặc dùng Chocolatey
choco install python --version=3.10.11 -y

# Verify
python --version
```

### ❌ Cannot activate venv (ExecutionPolicy)

```powershell
# Cho phép run scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate lại
& .\.venv\Scripts\Activate.ps1
```

### ❌ Bot không start

```powershell
# Xem logs chi tiết
Get-Content logs\bot.log -Tail 100

# Kiểm tra .env
Get-Content .env

# Kiểm tra Python packages
& .\.venv\Scripts\Activate.ps1
pip list | Select-String telegram
```

### ❌ Port conflict

```powershell
# Kiểm tra port đang dùng
Get-NetTCPConnection | Where-Object {$_.State -eq "Listen"}

# Kill process trên port cụ thể (ví dụ 8080)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

---

## 📋 COMMAND CHEAT SHEET

```powershell
# ===== SETUP LẦN ĐẦU =====
cd C:\
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
cd FreedomWalletBot
git checkout cleanup/hard-refactor
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
notepad .env  # Thêm bot token
python migrate_database.py
python main.py

# ===== START BOT (BACKGROUND) =====
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\FreedomWalletBot; & .\.venv\Scripts\Activate.ps1; python main.py *> logs\bot.log" -WindowStyle Hidden

# ===== MONITORING =====
Get-Content C:\FreedomWalletBot\logs\bot.log -Tail 50 -Wait
Get-Process python

# ===== UPDATE CODE =====
cd C:\FreedomWalletBot
Stop-Process -Name python -Force
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item data\bot.db -Destination "data\backups\backup_$timestamp.db"
git pull origin cleanup/hard-refactor
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python migrate_database.py
python main.py
```

---

## ✅ CHECKLIST

- [ ] RDP vào VPS (103.69.190.75)
- [ ] Git đã cài (git --version)
- [ ] Python 3.10+ đã cài (python --version)
- [ ] Clone repo từ GitHub
- [ ] Checkout branch cleanup/hard-refactor
- [ ] Setup virtual environment (.venv)
- [ ] Cài dependencies (pip install -r requirements.txt)
- [ ] Tạo file .env với bot token
- [ ] Run migration (python migrate_database.py)
- [ ] Start bot (python main.py)
- [ ] Setup scheduled task (tự chạy khi khởi động)
- [ ] Test trên Telegram

---

🎉 **Xong! Bot giờ chạy 24/7 trên Windows VPS!**
