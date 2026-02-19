# 🚀 GITHUB SETUP - CHỈ 5 PHÚT!

## ✅ Bạn chỉ cần làm 3 bước đơn giản này:

---

## 📋 BƯỚC 1: Tạo Repository Trên GitHub (2 phút)

### Cách 1: Qua Web (Đơn giản nhất)

1. **Truy cập:** https://github.com/new

2. **Điền thông tin:**
   ```
   Repository name: FreedomWalletBot
   Description: Telegram Bot for Freedom Wallet - 24/7 Customer Support
   Private: ✅ CHẾ ĐỘ RIÊNG TƯ (để bảo vệ code)
   
   KHÔNG CHỌN:
   ❌ Add a README file
   ❌ Add .gitignore
   ❌ Choose a license
   ```

3. **Click:** "Create repository" (nút màu xanh)

4. **SAU KHI TẠO XONG:** GitHub sẽ hiển thị màn hình hướng dẫn
   - ⚠️ ĐỪNG LÀM GÌ CẢ - chỉ cần để đó
   - Chuyển sang Bước 2 bên dưới

---

## 🔑 BƯỚC 2: Push Code Lần Đầu (3 phút)

**Mở PowerShell trong thư mục FreedomWalletBot:**

### 2.1. Khởi tạo Git (nếu chưa có)

```powershell
# Navigate to project
cd D:\Projects\FreedomWalletBot

# Check if git already initialized
git status
```

**Nếu báo lỗi "not a git repository":**
```powershell
git init
```

**Nếu có sẵn git (hiển thị status):** Bỏ qua lệnh trên, chuyển sang 2.2

---

### 2.2. Kết nối với GitHub

```powershell
# Thêm remote repository
git remote add origin https://github.com/mettatuan/FreedomWalletBot.git

# Kiểm tra remote đã đúng chưa
git remote -v
```

**Phải hiển thị:**
```
origin  https://github.com/mettatuan/FreedomWalletBot.git (fetch)
origin  https://github.com/mettatuan/FreedomWalletBot.git (push)
```

---

### 2.3. Push Code Lên GitHub

**QUAN TRỌNG: Đảm bảo bạn đã commit code trước đó!**

```powershell
# Kiểm tra branch hiện tại
git branch

# Nếu đang ở branch "master", đổi thành "main"
git branch -M main

# Push lên GitHub
git push -u origin main
```

**Khi chạy `git push`:**
- GitHub sẽ yêu cầu đăng nhập
- Chọn phương thức xác thực (Browser, Token, SSH...)
- Làm theo hướng dẫn trên màn hình

---

### 🎯 Nếu Gặp Lỗi Xác Thực (Authentication)

**Cách 1: Dùng GitHub CLI (Đơn giản nhất)**

```powershell
# Cài GitHub CLI nếu chưa có
winget install --id GitHub.cli

# Đăng nhập
gh auth login

# Làm theo hướng dẫn trên màn hình:
# - Login with a web browser (khuyến nghị)
# - Chọn "GitHub.com"
# - Protocol: HTTPS
# - Authenticate: Yes
```

**Sau khi đăng nhập xong, chạy lại:**
```powershell
git push -u origin main
```

---

**Cách 2: Dùng Personal Access Token (PAT)**

1. Tạo token tại: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Note: `FreedomWalletBot Deploy`
   - Expiration: 90 days (hoặc No expiration)
   - Scopes: ✅ **repo** (đầy đủ quyền repository)
   - Click "Generate token"
   - **COPY TOKEN NGAY** (chỉ hiện 1 lần!)

2. Sử dụng token khi push:
   ```powershell
   git push -u origin main
   
   # Username: mettatuan
   # Password: [PASTE TOKEN VỪA COPY]
   ```

3. Lưu credentials (không phải nhập lại):
   ```powershell
   git config --global credential.helper wincred
   ```

---

**Cách 3: Dùng SSH Key (Advanced)**

```powershell
# Tạo SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"
# Nhấn Enter 3 lần (không cần passphrase)

# Copy public key
Get-Content ~/.ssh/id_ed25519.pub | clip

# Thêm vào GitHub:
# 1. Vào https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Title: "VPS - FreedomWalletBot"
# 4. Key: Paste (Ctrl+V)
# 5. Click "Add SSH key"

# Đổi remote sang SSH
git remote set-url origin git@github.com:mettatuan/FreedomWalletBot.git

# Push
git push -u origin main
```

---

## ✅ BƯỚC 3: Verify (30 giây)

```powershell
# Kiểm tra trạng thái Git
git status

# Kiểm tra remote
git remote -v

# Xem commit history
git log --oneline
```

**Truy cập repository trên web:**
https://github.com/mettatuan/FreedomWalletBot

**Phải thấy:**
- ✅ Tất cả files đã được push
- ✅ Commit history có commit đầu tiên
- ✅ `.env` và `google_service_account.json` KHÔNG có (bị gitignore)

---

## 🎉 HOÀN THÀNH!

Bây giờ mỗi lần update code:

```powershell
# 1. Thay đổi code
# 2. Commit
git add .
git commit -m "Your commit message"

# 3. Push
git push
```

**Trên VPS chỉ cần:**
```powershell
git pull origin main
```

Hoặc dùng deployment script:
```powershell
D:\FreedomWalletBot\deploy.bat
```

---

## 🚨 TROUBLESHOOTING

### Lỗi: "fatal: not a git repository"
```powershell
git init
git remote add origin https://github.com/mettatuan/FreedomWalletBot.git
```

### Lỗi: "remote origin already exists"
```powershell
git remote set-url origin https://github.com/mettatuan/FreedomWalletBot.git
```

### Lỗi: "failed to push some refs"
```powershell
# Pull trước rồi push lại
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Lỗi: "Authentication failed"
- Dùng GitHub CLI: `gh auth login`
- Hoặc tạo Personal Access Token (xem Cách 2 ở trên)

### Lỗi: "Permission denied (publickey)"
- SSH key chưa được thêm vào GitHub
- Hoặc dùng HTTPS thay vì SSH:
  ```powershell
  git remote set-url origin https://github.com/mettatuan/FreedomWalletBot.git
  ```

---

## 📚 THAM KHẢO NHANH

### Git Commands Cơ Bản

```powershell
# Kiểm tra status
git status

# Thêm file
git add .                    # Tất cả files
git add file.py             # File cụ thể

# Commit
git commit -m "Message"

# Push
git push

# Pull
git pull

# Xem history
git log --oneline

# Xem remote
git remote -v

# Xem branch
git branch
```

---

## 💡 PRO TIPS

### Commit Messages Chuẩn

```powershell
git commit -m "feat: Add new deployment script"
git commit -m "fix: Resolve database connection issue"
git commit -m "docs: Update README with setup guide"
git commit -m "refactor: Improve health check logic"
```

### Git Aliases (Làm Việc Nhanh Hơn)

```powershell
# Thiết lập aliases
git config --global alias.st status
git config --global alias.co commit
git config --global alias.br branch
git config --global alias.ch checkout

# Sử dụng
git st      # thay vì git status
git co -m "message"  # thay vì git commit -m "message"
```

### Push Nhanh (One-liner)

```powershell
# Thêm function vào PowerShell profile
function GitPush {
    param([string]$message = "Update")
    git add .
    git commit -m $message
    git push
}

# Sử dụng
GitPush "Add new feature"
# Hoặc đơn giản:
GitPush
```

---

## 🔐 BẢO MẬT

### Kiểm Tra File Bị Gitignore

```powershell
# Kiểm tra .env có bị track không
git check-ignore .env
# Phải hiển thị: .env

# Xem files sẽ được commit
git status

# Nếu .env đang bị track (BAD!):
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

### Xóa File Secrets Đã Push Nhầm

**Nếu đã push `.env` nhầm lên GitHub:**

```powershell
# Xóa khỏi Git nhưng giữ file local
git rm --cached .env
git commit -m "Remove .env from repository"
git push

# QUAN TRỌNG: Đổi tất cả credentials trong .env
# Vì đã bị lộ trên GitHub!
```

**Hoặc xóa hoàn toàn khỏi history (nuclear option):**
```powershell
# Cài BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Xóa .env khỏi toàn bộ history
bfg --delete-files .env

# Force push
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

---

## 🎯 CHECKLIST HOÀN THÀNH

- [ ] Repository đã tạo trên GitHub
- [ ] Git remote đã kết nối đúng
- [ ] Code đã push lên GitHub thành công
- [ ] Vào https://github.com/mettatuan/FreedomWalletBot thấy code
- [ ] `.env` KHÔNG có trên GitHub (gitignore working)
- [ ] `google_service_account.json` KHÔNG có trên GitHub
- [ ] Git credentials đã được lưu (không cần nhập lại)

---

## 📞 CẦN TRỢ GIÚP?

**Lỗi Git:**
```powershell
# Xem chi tiết lỗi
git config --global core.verbose true

# Xem Git version
git --version

# Reset về trạng thái sạch (CẢNH BÁO: Mất thay đổi chưa commit)
git reset --hard HEAD
```

**GitHub Issues:**
- Authentication: https://docs.github.com/en/authentication
- SSH Keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- Personal Access Token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

---

**🎉 Xong! Repository đã sẵn sàng cho production deployment!**

**Next Step:** Đọc [QUICK_START.md](docs/QUICK_START.md) để deploy lên VPS!
