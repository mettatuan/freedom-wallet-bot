# 🚀 Getting Started - Quick Setup Guide

## 📋 Prerequisites

- Python 3.9+
- Telegram account
- Google account (for Sheets integration)

## ⚡ Quick Start (5 minutes)

### 1. Create Telegram Bot

1. Open Telegram, search **@BotFather**
2. Send `/newbot`
3. Follow instructions:
   - Bot name: `Freedom Wallet Bot`
   - Username: `@FreedomWalletBot` (or your choice)
4. Copy the **TOKEN** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### 2. Setup Project

```powershell
# Clone or create project directory
cd "D:/Projects/FreedomWalletBot"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy .env example
cp config/.env.example config/.env

# Edit config/.env (use Notepad or VS Code)
notepad config/.env
```

Add your Telegram bot token:
```env
TELEGRAM_BOT_TOKEN=your_token_here
```

### 4. Run Bot

```powershell
python main.py
```

You should see:
```
🤖 Freedom Wallet Bot is starting...
✅ Bot is running! Press Ctrl+C to stop.
```

### 5. Test Bot

1. Open Telegram
2. Search your bot: `@FreedomWalletBot`
3. Send `/start`
4. Try asking: "Làm sao thêm giao dịch?"

🎉 **Done! Your bot is running!**

---

## 📚 Next Steps

### Phase 1: Complete MVP Features

1. **Add more FAQ questions** in `bot/knowledge/faq.json`
2. **Setup Google Sheets** for support tickets:
   - Create Google Sheet
   - Enable Google Sheets API
   - Download service account JSON
   - Update `.env` with credentials

### Phase 2: Add AI (GPT-4)

1. Get OpenAI API key from https://platform.openai.com
2. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   ENABLE_AI=true
   ```
3. Bot will use GPT-4 for questions not in FAQ

### Phase 3: Deploy to Production

See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for Railway deployment

---

## 🔧 Troubleshooting

**Bot doesn't respond?**
- Check TOKEN is correct in `.env`
- Verify bot is running (console shows logs)
- Try `/start` command again

**Import errors?**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Google Sheets errors?**
- Verify service account JSON path
- Check spreadsheet permissions (share with service account email)

---

## 📞 Need Help?

- 📖 Read [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- 📋 Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- 📧 Email: support@freedomwallet.com

Happy coding! 🤖💙
