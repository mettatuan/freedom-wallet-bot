# 🤖 Freedom Wallet Bot

AI-powered Telegram bot for personal finance management with Google Sheets integration.

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Python 3.9+
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup
```bash
# Create .env file
cp .env.example .env

# Edit .env with your tokens
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://...
GOOGLE_SHEETS_CREDENTIALS=path/to/google_service_account.json
```

### 3. Run Bot
```bash
# Local development
python main.py

# Or use batch script (Windows)
start_local.bat
```

## 📖 Documentation

**Comprehensive docs in `/docs` folder:**

- **[docs/MASTER_INDEX.md](docs/MASTER_INDEX.md)** - Complete documentation index
- **[docs/QUICK_START_v2.md](docs/QUICK_START_v2.md)** - Developer quick start guide
- **[docs/DEPLOY.md](docs/DEPLOY.md)** - Deployment guide (Railway/VPS)
- **[docs/FLOW_MAP.md](docs/FLOW_MAP.md)** - Architecture & user flows

## 📁 Project Structure

```
FreedomWalletBot/
├── app/
│   ├── handlers/           # Telegram command/callback handlers
│   │   ├── core/          # Core: start, menu, setup, keyboard
│   │   ├── features/      # Features: quick_record, reports, etc.
│   │   └── admin/         # Admin commands
│   ├── services/          # Business logic (roadmap, sheets, etc.)
│   ├── utils/             # Database, helpers
│   └── models/            # Data models
├── docs/                  # 📚 All documentation (70+ files)
├── tests/                 # Unit & integration tests
├── config/                # Configuration files
├── migrations/            # Database migrations
├── scripts/               # Utility scripts
├── main.py               # Entry point
├── version.py            # Version info (v2.0.0)
└── requirements.txt      # Python dependencies
```

## 🎯 Features

### **Core**
- ✅ Personal finance tracking via Telegram
- 📊 Google Sheets integration (private data)
- 🤖 AI-powered transaction parsing
- 📝 Quick record income/expenses
- 📈 Financial reports & analytics

### **Tiers**
- **FREE** - Basic tracking, manual setup
- **UNLOCK** - Advanced features via 2 referrals
- **PREMIUM** - Full automation + AI insights

### **Advanced**
- 💰 6 Jars budgeting system
- 🎯 Goal tracking
- 📊 Custom reports
- 🔔 Smart reminders
- 🤝 Referral system (gamification)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_state_machine_comprehensive.py

# Run with coverage
pytest --cov=app tests/
```

## 🚢 Deployment

See [docs/DEPLOY.md](docs/DEPLOY.md) and [docs/DEPLOYMENT_CHECKLIST_v2.md](docs/DEPLOYMENT_CHECKLIST_v2.md)

### Railway (Recommended)
```bash
railway login
railway link
railway up
```

### Manual VPS
```bash
# Sync to VPS
.\sync_to_vps.bat

# Or use PowerShell
.\sync_to_vps.ps1
```

## 📊 Version

**Current:** v2.0.0 - Unified Flow Architecture

See [CHANGELOG.md](CHANGELOG.md) and [docs/RELEASE_v2.0.0.md](docs/RELEASE_v2.0.0.md)

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing`)
5. Open Pull Request

**Before PR:** Run tests + check [docs/ARCHITECTURE_DECISION.md](docs/ARCHITECTURE_DECISION.md)

## 📝 License

MIT License - See LICENSE file

## 🆘 Support

- Bot issues: Open GitHub issue
- App support: Use @FreedomWalletBot
- Email: support@freedomwallet.com

---

**Made with ❤️ for Freedom Wallet users**
