# 🪟 DEPLOY LÊN WINDOWS VPS

**VPS của bạn:** Windows Server 2016  
**IP:** 103.69.190.75  
**User:** administrator

---

## 📋 YÊU CẦU TRƯỚC KHI BẮT ĐẦU

### 1. Cài đặt trên Windows VPS

Cần cài sẵn trên VPS:

#### **Git for Windows**
```powershell
# RDP vào VPS, mở PowerShell (Run as Administrator)
# Download Git: https://git-scm.com/download/win
# Hoặc dùng Chocolatey:
choco install git -y
```

#### **Python 3.10+**
```powershell
# Download Python: https://www.python.org/downloads/
# Hoặc dùng Chocolatey:
choco install python --version=3.10.11 -y

# Verify
python --version
# Output: Python 3.10.x
```

### 2. Enable SSH trên Windows VPS (nếu chưa có)

```powershell
# Trên VPS (PowerShell as Admin)
Add-WindowsCapability -Online -Name OpenSSH.Server
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
```

### 3. Test SSH từ máy local

```powershell
# Từ máy Windows local
ssh administrator@103.69.190.75

# Nhập password khi được hỏi
# Nếu kết nối OK → Gõ 'exit' để thoát
```

---

## 🚀 DEPLOY TỰ ĐỘNG

### Lần đầu tiên (First Time Setup)

```powershell
# Từ máy local (PowerShell)
cd D:\Projects\FreedomWalletBot

.\deploy_windows_vps.ps1 -SetupFirstTime
```

**Script sẽ:**
1. SSH vào VPS
2. Clone repo từ GitHub
3. Checkout branch `cleanup/hard-refactor`
4. Setup Python virtual environment
5. Cài dependencies
6. Tạo file `.env` template
7. Run database migration

**Sau đó edit bot token:**

```powershell
# Cách 1: RDP vào VPS, mở Notepad
# C:\FreedomWalletBot\.env

# Cách 2: SSH và dùng notepad
ssh administrator@103.69.190.75
notepad C:\FreedomWalletBot\.env

# Thay REPLACE_WITH_YOUR_TOKEN bằng token thật
# Save và đóng notepad
```

**Start bot lần đầu:**

```powershell
ssh administrator@103.69.190.75 "powershell -Command 'cd C:\FreedomWalletBot; & .\.venv\Scripts\Activate.ps1; python main.py'"
```

### Lần sau (Update Code)

```powershell
# Mỗi khi có code mới
.\deploy_windows_vps.ps1
```

---

## 📋 DEPLOY THỦ CÔNG (Từng bước)

### Lần đầu tiên:

```powershell
# Bước 1: RDP vào VPS hoặc SSH
ssh administrator@103.69.190.75

# Bước 2: Mở PowerShell và clone repo
powershell
cd C:\
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
cd FreedomWalletBot

# Bước 3: Checkout branch
git checkout cleanup/hard-refactor

# Bước 4: Setup Python environment
python -m venv .venv
& .\.venv\Scripts\Activate.ps1

# Bước 5: Cài dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Bước 6: Tạo .env file
@'
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=sqlite:///data/bot.db
LOG_LEVEL=INFO
ENV=production
'@ | Out-File -FilePath '.env' -Encoding utf8

# Bước 7: Tạo thư mục data & logs
New-Item -ItemType Directory -Force -Path 'data\backups'
New-Item -ItemType Directory -Force -Path 'logs'

# Bước 8: Run migration
python migrate_database.py

# Bước 9: Start bot
python main.py
# Bot đang chạy! Ctrl+C để dừng
```

### Chạy bot trong background (Windows Service)

Tạo file `start_bot.ps1`:

```powershell
# Trên VPS
cd C:\FreedomWalletBot

@'
Set-Location C:\FreedomWalletBot
& .\.venv\Scripts\Activate.ps1
python main.py *> logs\bot.log
'@ | Out-File -FilePath 'start_bot.ps1' -Encoding utf8
```

Chạy bot:

```powershell
# Start bot trong background
Start-Process powershell -ArgumentList "-File C:\FreedomWalletBot\start_bot.ps1" -WindowStyle Hidden
```

Hoặc tạo **Windows Scheduled Task** (khuyến nghị):

```powershell
# Tạo task tự chạy bot khi VPS khởi động
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\FreedomWalletBot\start_bot.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "administrator" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "FreedomWalletBot" -Action $action -Trigger $trigger -Principal $principal

# Start task ngay
Start-ScheduledTask -TaskName "FreedomWalletBot"
```

---

## 🔄 UPDATE CODE (Lần sau)

### Tự động (khuyến nghị):

```powershell
# Từ máy local
.\deploy_windows_vps.ps1
```

### Thủ công:

```powershell
# SSH vào VPS
ssh administrator@103.69.190.75

# Chạy trong PowerShell
powershell

# Update script
cd C:\FreedomWalletBot

# Stop bot
Get-Process python | Stop-Process -Force

# Backup database
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item data\bot.db -Destination "data\backups\backup_$timestamp.db"

# Pull code mới
git pull origin cleanup/hard-refactor

# Update dependencies
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run migration
python migrate_database.py

# Start bot
python main.py
```

---

## 📊 MONITORING

### Xem logs từ máy local:

```powershell
# Real-time logs
ssh administrator@103.69.190.75 "powershell Get-Content C:\FreedomWalletBot\logs\bot.log -Tail 50 -Wait"

# 50 dòng cuối
ssh administrator@103.69.190.75 "powershell Get-Content C:\FreedomWalletBot\logs\bot.log -Tail 50"
```

### Check bot status:

```powershell
# Check process
ssh administrator@103.69.190.75 "powershell Get-Process python"

# Stop bot
ssh administrator@103.69.190.75 "powershell Stop-Process -Name python -Force"

# Start bot
ssh administrator@103.69.190.75 "powershell -Command 'cd C:\FreedomWalletBot; & .\.venv\Scripts\Activate.ps1; python main.py'"
```

---

## 🎯 COMMANDS CHEAT SHEET

```powershell
# DEPLOY/UPDATE (từ máy local)
.\deploy_windows_vps.ps1

# XEM LOGS (từ máy local)
ssh administrator@103.69.190.75 "powershell Get-Content C:\FreedomWalletBot\logs\bot.log -Tail 50 -Wait"

# CHECK STATUS (từ máy local)
ssh administrator@103.69.190.75 "powershell Get-Process python"

# RESTART BOT (từ máy local)
ssh administrator@103.69.190.75 "powershell Stop-Process -Name python -Force; Start-Sleep 2; cd C:\FreedomWalletBot; & .\.venv\Scripts\Activate.ps1; python main.py"

# BACKUP DATABASE (trên VPS)
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item C:\FreedomWalletBot\data\bot.db -Destination "C:\FreedomWalletBot\data\backups\backup_$timestamp.db"

# GIT STATUS (trên VPS)
cd C:\FreedomWalletBot
git log -1 --oneline
git status
```

---

## 🔧 TROUBLESHOOTING

### ❌ Python not found

```powershell
# Cài Python trên VPS
choco install python --version=3.10.11 -y

# Hoặc download: https://www.python.org/downloads/
```

### ❌ Git not found

```powershell
# Cài Git trên VPS
choco install git -y

# Hoặc download: https://git-scm.com/download/win
```

### ❌ SSH connection refused

```powershell
# Trên VPS, enable OpenSSH Server
Add-WindowsCapability -Online -Name OpenSSH.Server
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'

# Mở firewall
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

### ❌ Bot không start

```powershell
# Xem logs chi tiết
Get-Content C:\FreedomWalletBot\logs\bot.log -Tail 100

# Kiểm tra .env
Get-Content C:\FreedomWalletBot\.env

# Kiểm tra Python packages
& C:\FreedomWalletBot\.venv\Scripts\Activate.ps1
pip list | Select-String telegram
```

---

## ✅ CHECKLIST

**Trên VPS (103.69.190.75):**
- [ ] Windows Server 2016
- [ ] Python 3.10+ installed
- [ ] Git for Windows installed
- [ ] OpenSSH Server enabled
- [ ] Firewall allows SSH (port 22)

**Deployment:**
- [ ] Clone repo từ GitHub
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file created with bot token
- [ ] Database migrated
- [ ] Bot started và running
- [ ] Test trên Telegram

---

## 🎉 TÓM TẮT

**Setup lần đầu:**
```powershell
.\deploy_windows_vps.ps1 -SetupFirstTime
```

**Update code:**
```powershell
.\deploy_windows_vps.ps1
```

**Xem logs:**
```powershell
ssh administrator@103.69.190.75 "powershell Get-Content C:\FreedomWalletBot\logs\bot.log -Tail 50 -Wait"
```

---

🎯 **Windows VPS deployment hoàn toàn khác Linux, nhưng script tự động sẽ lo tất cả!**
