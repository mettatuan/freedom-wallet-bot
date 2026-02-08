# 🚀 Hướng Dẫn Push Lên GitHub

## ⚡ CÁCH DỄ NHẤT - Click 2 Lần! (Windows)

### Lần đầu tiên (Setup):
1. **Double-click:** `setup_github.ps1`
2. Làm theo hướng dẫn:
   - Tạo repo trên GitHub: https://github.com/new (tên: `freedom-wallet-bot`)
   - Nhập GitHub username của bạn
3. ✅ Xong! Repository đã được tạo và code đã push

### Lần sau (Push Changes):
1. **Double-click:** `PUSH.bat` (hoặc `quick_push.ps1`)
2. ✅ Xong! Code tự động push lên GitHub

---

## Cách 1: Script Tự Động (PowerShell) ⚡

## Cách 1: Script Tự Động (PowerShell) ⚡

### A. Lần đầu tiên (Setup Git & GitHub):
```powershell
.\setup_github.ps1
```
- Tự động init git, commit, tạo/kết nối remote
- Wizard hướng dẫn từng bước
- Hỗ trợ cả manual và GitHub CLI

### B. Push thay đổi mới:
```powershell
# Push nhanh (dùng message mặc định)
.\quick_push.ps1

# Hoặc push với message tùy chỉnh
.\quick_push.ps1 "Add fraud detection system"
```

### C. Push có kiểm tra (interactive):
```powershell
.\push_to_github.ps1
```

Script này sẽ:
- ✅ Kiểm tra git đã cài chưa
- ✅ Init git repository (nếu chưa có)
- ✅ Kiểm tra file nhạy cảm đã được ignore
- ✅ Add tất cả files (theo .gitignore)
- ✅ Commit với message tùy chỉnh
- ✅ Push lên GitHub

---

## Cách 2: GitHub Desktop (Dễ Nhất) 🖱️

### Bước 1: Mở dự án trong GitHub Desktop
1. Mở **GitHub Desktop**
2. **File** → **Add Local Repository**
3. Chọn folder: `D:\Projects\FreedomWalletBot`
4. Nếu chưa có git repo → chọn **Create Repository**

### Bước 2: Publish lên GitHub
1. Click **Publish repository**
2. Đặt tên: `freedom-wallet-bot`
3. Chọn **Public** hoặc **Private**
4. ✅ Bỏ tick "Keep this code private" (nếu muốn public)
5. Click **Publish repository**

### Bước 3: Push thay đổi (lần sau)
1. GitHub Desktop tự động hiển thị files thay đổi
2. Nhập commit message ở bên trái
3. Click **Commit to main**
4. Click **Push origin**

✅ **Done!** File sẽ tự động được lọc theo `.gitignore`

---

## Cách 3: Command Line (Thủ Công) ⌨️

### Lần đầu setup:
```powershell
# 1. Init git repository
git init

# 2. Add tất cả files (theo .gitignore)
git add .

# 3. Commit lần đầu
git commit -m "Initial commit: Week 1-5 complete (fraud detection ready)"

# 4. Tạo repository trên GitHub
# Vào https://github.com/new
# Tên: freedom-wallet-bot

# 5. Thêm remote
git remote add origin https://github.com/YOUR_USERNAME/freedom-wallet-bot.git

# 6. Push lên GitHub
git branch -M main
git push -u origin main
```

### Lần sau (push thay đổi mới):
```powershell
# 1. Add files thay đổi
git add .

# 2. Commit
git commit -m "Your commit message here"

# 3. Push
git push
```

---

## 🔒 File Nào Được Push? (Theo .gitignore)

### ✅ Push lên GitHub:
- `*.py` - Code Python
- `requirements.txt` - Dependencies
- `.env.example` - Template environment (KHÔNG có secrets)
- `.gitignore` - Git ignore rules
- `README.md` - Documentation
- `bot/`, `config/`, `tests/` - Code folders
- Các file markdown (docs)

### ❌ KHÔNG push (đã lọc bởi .gitignore):
- `.env` - **Secrets (bot token, API keys)**
- `google_service_account.json` - **Google credentials**
- `data/*.db` - **Database với user data**
- `__pycache__/` - Python cache
- `*.log` - Log files
- `media/uploads/` - User uploads

---

## ⚡ Quick Commands

```powershell
# Xem trạng thái
git status

# Xem files sẽ được push
git ls-files

# Xem files bị ignore
git status --ignored

# Push nhanh (sau khi đã setup)
git add . ; git commit -m "Update" ; git push

# Xem remote URL
git remote -v

# Xem commit history
git log --oneline -10
```

---

## 🚨 Troubleshooting

### Lỗi: "fatal: not a git repository"
```powershell
git init
```

### Lỗi: "No remote configured"
```powershell
git remote add origin https://github.com/YOUR_USERNAME/freedom-wallet-bot.git
```

### Lỗi: "Authentication failed"
**Cách 1 (Dễ):** Dùng GitHub Desktop (tự động đăng nhập)

**Cách 2:** Dùng GitHub CLI
```powershell
# Install: winget install GitHub.cli
gh auth login
```

**Cách 3:** Dùng Personal Access Token
1. Tạo token: https://github.com/settings/tokens
2. Dùng token thay vì password khi git push

### File nhạy cảm đã bị push nhầm?
```powershell
# Xóa file khỏi git (giữ file local)
git rm --cached .env
git rm --cached google_service_account.json
git rm --cached data/bot.db

# Commit
git commit -m "Remove sensitive files"

# Push
git push

# Đổi secrets ngay lập tức!
# - Bot token: /revoke trên @BotFather → tạo mới
# - Google credentials: Revoke trên Google Cloud Console
```

---

## 📋 Pre-Push Checklist

Trước khi push, kiểm tra:
- [ ] `.env` có trong `.gitignore` ✅
- [ ] `google_service_account.json` có trong `.gitignore` ✅
- [ ] `data/*.db` có trong `.gitignore` ✅
- [ ] `.env.example` đã được tạo và KHÔNG chứa secrets ✅
- [ ] Các test đã pass (chạy `pytest`) ✅
- [ ] README.md đã update ✅

---

## 🎯 Next Steps After Push

1. **Setup Railway Deployment:**
   - Connect Railway to GitHub repo
   - Set environment variables (TELEGRAM_BOT_TOKEN, ADMIN_USER_ID)
   - Deploy on push

2. **Enable GitHub Actions (Optional):**
   - Auto-run tests on pull request
   - Auto-deploy to Railway on main branch

3. **Add Badge to README:**
   ```markdown
   ![Tests](https://github.com/YOUR_USERNAME/freedom-wallet-bot/workflows/tests/badge.svg)
   ```

---

## 📚 Resources

- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [GitHub Desktop](https://desktop.github.com/)
- [GitHub CLI](https://cli.github.com/)
- [Gitignore Generator](https://www.toptal.com/developers/gitignore)
