# 🖥️ Setup Máy Mới - Complete Guide

## 📋 Checklist Trước Khi Chuyển

### Từ Máy Cũ - Xuất Configs
```powershell
# 1. Export SSH keys
xcopy "$env:USERPROFILE\.ssh\*" "D:\backup\ssh\" /E /I

# 2. Export Git config
git config --global --list > D:\backup\git-config.txt

# 3. Backup .env files
xcopy "D:\Proïects\FreedomWalletBot\.env" "D:\backup\"
xcopy "D:\Proïects\FreedomWalletBot\google_service_account.json" "D:\backup\"

# 4. Export VS Code settings
xcopy "$env:APPDATA\Code\User\settings.json" "D:\backup\vscode\"
xcopy "$env:APPDATA\Code\User\keybindings.json" "D:\backup\vscode\"

# 5. List installed VS Code extensions
code --list-extensions > D:\backup\vscode\extensions.txt
```

---

## 🚀 Setup Máy Mới - Bước 1: Cài Đặt Tools

### 1. **Git**
```
Download: https://git-scm.com/download/win
- ✅ Git Bash
- ✅ Git Credential Manager
- ✅ Add to PATH
```

### 2. **Python 3.11+**
```
Download: https://www.python.org/downloads/
- ✅ Add Python to PATH
- ✅ Install pip
```

### 3. **Node.js** (for clasp - Google Apps Script)
```
Download: https://nodejs.org/
- ✅ LTS version
- ✅ npm included
```

### 4. **VS Code**
```
Download: https://code.visualstudio.com/
Extensions cần thiết:
- Python
- GitHub Copilot
- PowerShell
- GitLens
- Remote - SSH
```

### 5. **SSH Client**
Windows 11: Built-in OpenSSH
Windows 10: 
```powershell
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

---

## 📁 Setup Máy Mới - Bước 2: Clone Projects

### Option A: Clone từ GitHub (RECOMMENDED)
```powershell
# Tạo thư mục projects
mkdir D:\Proïects
cd D:\Proïects

# Clone bot repository
git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
cd FreedomWalletBot
git checkout cleanup/hard-refactor

# Setup Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Clone Google Apps Script project (nếu cần)
cd D:\Proïects
# Manual copy hoặc clasp clone
```

### Option B: Copy từ máy cũ
```powershell
# Nếu có USB hoặc network share
xcopy "\\OLD_PC\D$\Proïects\*" "D:\Proïects\" /E /I /H /Y
```

---

## 🔐 Setup Máy Mới - Bước 3: Configs & Credentials

### 1. **Git Config**
```powershell
git config --global user.name "Metta Tuan"
git config --global user.email "mettatuan@gmail.com"
git config --global core.autocrlf true
git config --global init.defaultBranch main
```

### 2. **SSH Keys** (để SSH vào VPS)
```powershell
# Copy SSH keys từ backup
xcopy "D:\backup\ssh\*" "$env:USERPROFILE\.ssh\" /E /I

# Hoặc tạo mới
ssh-keygen -t rsa -b 4096 -C "mettatuan@gmail.com"

# Test connection
ssh freedom-vps
```

### 3. **Environment Variables**
```powershell
cd D:\Proïects\FreedomWalletBot

# Copy .env từ backup
copy D:\backup\.env .env

# Copy Google credentials
copy D:\backup\google_service_account.json google_service_account.json
```

**File `.env` cần có:**
```env
TELEGRAM_BOT_TOKEN=7926077595:AAExXiCOT2R6cq15F6gmxPikkf54m96myZc
ADMIN_USER_ID=6588506476
ADMIN_TEST_USER_IDS=6588506476

# Database
DATABASE_URL=sqlite:///data/bot.db

# Google Sheets
GOOGLE_SHEET_ID=1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg
GOOGLE_SERVICE_ACCOUNT_FILE=google_service_account.json

# OpenAI (optional)
OPENAI_API_KEY=your_key_here

# SMTP Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### 4. **SSH Config** (để SSH nhanh vào VPS)
File: `C:\Users\[YourName]\.ssh\config`
```
Host freedom-vps
    HostName [VPS_IP_ADDRESS]
    User Administrator
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

---

## 🎯 Setup Máy Mới - Bước 4: Verify Setup

### Test Git
```powershell
cd D:\Proïects\FreedomWalletBot
git status
git log --oneline -5
```

### Test Python Environment
```powershell
cd D:\Proïects\FreedomWalletBot
.\.venv\Scripts\Activate.ps1
python --version  # Should show Python 3.11+
pip list  # Should show all packages
```

### Test Bot Locally (Optional)
```powershell
# Chỉ test nếu muốn run local
cd D:\Proïects\FreedomWalletBot
.\.venv\Scripts\Activate.ps1
python main.py
# Press Ctrl+C to stop
```

### Test SSH to VPS
```powershell
ssh freedom-vps
# Should connect without password
# Type: exit
```

### Test Git Push
```powershell
cd D:\Proïects\FreedomWalletBot
git pull origin cleanup/hard-refactor
# Should work without errors
```

---

## 📦 SCRIPT TỰ ĐỘNG - Setup Nhanh

Tôi tạo script tự động setup hết cho bạn:

### `setup_new_machine.ps1`
```powershell
# Run as Administrator
Write-Host "🚀 Setting up Development Environment..." -ForegroundColor Cyan

# Check Git
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git not found. Please install Git first!" -ForegroundColor Red
    exit 1
}

# Check Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.11+!" -ForegroundColor Red
    exit 1
}

# Create projects folder
$ProjectsPath = "D:\Proïects"
if (!(Test-Path $ProjectsPath)) {
    New-Item -ItemType Directory -Path $ProjectsPath | Out-Null
    Write-Host "✅ Created $ProjectsPath" -ForegroundColor Green
}

# Clone repository
cd $ProjectsPath
if (!(Test-Path "$ProjectsPath\FreedomWalletBot")) {
    Write-Host "📥 Cloning repository..." -ForegroundColor Yellow
    git clone https://github.com/mettatuan/freedom-wallet-bot.git FreedomWalletBot
    cd FreedomWalletBot
    git checkout cleanup/hard-refactor
    Write-Host "✅ Repository cloned" -ForegroundColor Green
} else {
    Write-Host "✅ Repository already exists" -ForegroundColor Green
}

# Setup Python virtual environment
cd "$ProjectsPath\FreedomWalletBot"
if (!(Test-Path ".venv")) {
    Write-Host "🐍 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Install packages
Write-Host "📦 Installing Python packages..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✅ Packages installed" -ForegroundColor Green

# Check for .env
if (!(Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create .env file with your credentials" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file found" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Add .env file with credentials" -ForegroundColor White
Write-Host "2. Add google_service_account.json" -ForegroundColor White
Write-Host "3. Setup SSH keys for VPS access" -ForegroundColor White
Write-Host "4. Test: cd D:\Proïects\FreedomWalletBot; .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
```

---

## 🔧 VS Code Setup

### Install Extensions via Script
```powershell
# From backup
Get-Content D:\backup\vscode\extensions.txt | ForEach-Object { code --install-extension $_ }

# Or manually
code --install-extension ms-python.python
code --install-extension GitHub.copilot
code --install-extension ms-vscode.powershell
code --install-extension eamodio.gitlens
code --install-extension ms-vscode-remote.remote-ssh
```

### Import Settings
```powershell
copy D:\backup\vscode\settings.json "$env:APPDATA\Code\User\settings.json"
copy D:\backup\vscode\keybindings.json "$env:APPDATA\Code\User\keybindings.json"
```

---

## 📝 Checklist Hoàn Tất

### Core Setup
- [ ] ✅ Git installed
- [ ] ✅ Python 3.11+ installed
- [ ] ✅ Node.js installed
- [ ] ✅ VS Code installed
- [ ] ✅ SSH client enabled

### Project Setup
- [ ] ✅ Repository cloned
- [ ] ✅ Branch checkout: cleanup/hard-refactor
- [ ] ✅ Python venv created
- [ ] ✅ Packages installed
- [ ] ✅ .env file configured
- [ ] ✅ google_service_account.json added

### Access Setup
- [ ] ✅ Git config set
- [ ] ✅ SSH keys configured
- [ ] ✅ SSH to VPS works
- [ ] ✅ Git push works

### VS Code Setup
- [ ] ✅ Extensions installed
- [ ] ✅ Settings imported
- [ ] ✅ GitHub Copilot activated

---

## 🎯 Quick Start Commands (sau khi setup xong)

### Làm việc với Bot
```powershell
# Open project
cd D:\Proïects\FreedomWalletBot
code .

# Activate Python env
.\.venv\Scripts\Activate.ps1

# Pull latest code
git pull origin cleanup/hard-refactor

# Check bot status on VPS
ssh freedom-vps "Get-Service FreedomWalletBot"

# View bot logs on VPS
ssh freedom-vps "Get-Content C:\FreedomWalletBot\logs\service_stderr.log -Tail 50"

# Deploy changes to VPS
git push origin cleanup/hard-refactor
ssh freedom-vps "cd C:\FreedomWalletBot; git pull; C:\nssm\nssm.exe restart FreedomWalletBot"
```

### Làm việc với Google Apps Script
```powershell
cd D:\Proïects\FreedomWallet

# Push to Google
npx clasp push

# Pull from Google
npx clasp pull

# Open web app
npx clasp open --webapp
```

---

## 💡 Tips

### 1. **Sync Workspace Settings**
```powershell
# Export từ máy cũ
Export-Clixml -Path "D:\backup\workspace.xml" -InputObject @{
    Projects = "D:\Proïects"
    Git = (git config --global --list)
    Python = (python --version)
}
```

### 2. **Portable Git Credentials**
```powershell
# Use Git Credential Manager
git config --global credential.helper manager-core
```

### 3. **Quick Setup Script Location**
Save to: `D:\backup\setup_new_machine.ps1`
Run on new PC: 
```powershell
powershell -ExecutionPolicy Bypass -File D:\backup\setup_new_machine.ps1
```

---

## 🆘 Troubleshooting

### Git Push Authentication Failed
```powershell
# Re-authenticate
git config --global credential.helper manager-core
git push origin cleanup/hard-refactor
# Will prompt for GitHub credentials
```

### SSH Connection Refused
```powershell
# Check SSH service
Get-Service ssh-agent
Start-Service ssh-agent

# Check SSH key
ssh-add -l
ssh-add ~/.ssh/id_rsa
```

### Python Package Install Fails
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose
pip install -r requirements.txt -v
```

### VS Code Extensions Not Working
```powershell
# Reinstall all
code --list-extensions | ForEach-Object { code --uninstall-extension $_ }
Get-Content D:\backup\vscode\extensions.txt | ForEach-Object { code --install-extension $_ }
```

---

## 📞 Support

Nếu gặp vấn đề, check:
1. Git config: `git config --global --list`
2. Python version: `python --version`
3. SSH keys: `ssh-add -l`
4. Environment: `Get-Content .env`

---

**Last Updated:** March 3, 2026  
**Author:** GitHub Copilot + Mettatuan
