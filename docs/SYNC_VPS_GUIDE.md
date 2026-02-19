# 🚀 HƯỚNG DẪN ĐỒNG BỘ LOCAL → VPS WINDOWS

## 📋 Thông tin VPS
- **IP:** 103.69.190.75
- **Path:** C:\Projects\FreedomWalletBot
- **Local:** D:\Projects\FreedomWalletBot

---

## ✅ PHƯƠNG ÁN 1: PowerShell Script (Khuyến nghị)

### Cách 1A: Sync đơn giản
```powershell
.\sync_to_vps.ps1
```

### Cách 1B: Dry run (xem thử không sync thật)
```powershell
.\sync_to_vps.ps1 -DryRun
```

### Cách 1C: Bỏ qua backup
```powershell
.\sync_to_vps.ps1 -SkipBackup
```

### Cách 1D: Custom IP/User
```powershell
.\sync_to_vps.ps1 -VpsIp "103.69.190.75" -VpsUser "Administrator"
```

---

## ✅ PHƯƠNG ÁN 2: Robocopy (Batch File)

### Chạy script
```cmd
sync_to_vps.bat
```

### Hoặc manual command:
```cmd
robocopy "D:\Projects\FreedomWalletBot" "\\103.69.190.75\C$\Projects\FreedomWalletBot" ^
    /MIR ^
    /XD .venv __pycache__ .git database logs backup _archive ^
    /XF *.log *.db *.pyc google_service_account.json .env ^
    /R:2 /W:5
```

---

## ✅ PHƯƠNG ÁN 3: Git Push/Pull (Sạch nhất)

### 3.1. Setup trên VPS (chỉ làm 1 lần)
```powershell
# RDP vào VPS
cd C:\Projects\FreedomWalletBot
git init
git remote add origin <YOUR_GITHUB_REPO>
git fetch
git checkout main
```

### 3.2. Workflow sync
```powershell
# Local: Push code
git add .
git commit -m "Update: [mô tả thay đổi]"
git push origin main

# VPS: Pull code
cd C:\Projects\FreedomWalletBot
git pull origin main
```

---

## ✅ PHƯƠNG ÁN 4: WinSCP / FileZilla

### 4.1. Download WinSCP
https://winscp.net/

### 4.2. Kết nối
- Protocol: **SCP** hoặc **SFTP**
- Host: **103.69.190.75**
- User: **Administrator**
- Password: [nhập password VPS]

### 4.3. Sync
- Kéo thả folder từ Local → VPS
- Hoặc dùng tính năng **Synchronize**

---

## 🔧 TROUBLESHOOTING

### ❌ "Access denied" khi dùng robocopy

**Fix 1: Enable Admin$ share trên VPS**
```powershell
# Chạy trên VPS với quyền Admin
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f

# Restart Server service
Restart-Service LanmanServer
```

**Fix 2: Map network drive với credential**
```powershell
# Local: Kết nối với credential
net use \\103.69.190.75\C$ /user:Administrator [password]

# Sau đó chạy sync
.\sync_to_vps.ps1
```

### ❌ "Cannot reach VPS"

**Check firewall:**
```powershell
# Trên VPS: Allow File and Printer Sharing
New-NetFirewallRule -DisplayName "File and Printer Sharing (SMB-In)" -Direction Inbound -Protocol TCP -LocalPort 445 -Action Allow
```

**Check ping:**
```powershell
Test-Connection -ComputerName 103.69.190.75 -Count 4
```

### ❌ Bot không chạy sau sync

**Check dependencies:**
```powershell
# Trên VPS
cd C:\Projects\FreedomWalletBot
.\.venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

**Check config files:**
```powershell
# Kiểm tra .env có đầy đủ
Get-Content .env

# Kiểm tra google_service_account.json
Test-Path google_service_account.json
```

---

## 📝 FILES CẦN SYNC THỦ CÔNG

Những file này **KHÔNG** được sync tự động (phải copy riêng):

1. **`.env`** - Biến môi trường
2. **`google_service_account.json`** - Google API credentials
3. **`database/*.db`** - Database files (nếu cần migrate)
4. **`logs/*.log`** - Log files (thường không cần)

### Copy riêng:
```powershell
# Local
Copy-Item .env \\103.69.190.75\C$\Projects\FreedomWalletBot\.env
Copy-Item google_service_account.json \\103.69.190.75\C$\Projects\FreedomWalletBot\
```

---

## 🎯 WORKFLOW THỰC TẾ ĐỀ XUẤT

### Lần đầu deploy:
```powershell
# 1. Sync code (chọn 1 cách)
.\sync_to_vps.ps1

# 2. RDP vào VPS
mstsc /v:103.69.190.75

# 3. Trên VPS: Setup venv
cd C:\Projects\FreedomWalletBot
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 4. Copy config files thủ công
# (dùng RDP hoặc copy qua network)

# 5. Test chạy bot
python main.py
```

### Lần sau update code:
```powershell
# Local: Sync code
.\sync_to_vps.ps1

# VPS: Restart bot
Get-Process python | Stop-Process -Force
python main.py
```

---

## 🔒 BẢO MẬT

### Không sync những file này:
- ✅ `.env` (sensitive)
- ✅ `google_service_account.json` (sensitive)
- ✅ `*.db` (database)
- ✅ `*.log` (logs)
- ✅ `.venv` (virtual environment - tốn dung lượng)
- ✅ `__pycache__` (Python cache)

### Nên làm:
1. Dùng Git để version control
2. Encrypt credential files khi transfer
3. Dùng SSH/SCP thay vì SMB nếu có thể
4. Backup database trước khi sync qua

---

## 📞 HỖ TRỢ

Nếu gặp lỗi, check:
1. VPS có đang chạy không?
2. Firewall có block SMB (port 445)?
3. Admin$ share có enable?
4. Account có quyền admin?
5. Antivirus có block không?

Debug command:
```powershell
# Test SMB connection
Test-NetConnection -ComputerName 103.69.190.75 -Port 445

# Test admin access
Test-Path \\103.69.190.75\C$

# List shares
net view \\103.69.190.75
```
