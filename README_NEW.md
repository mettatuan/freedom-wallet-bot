# 🤖 Freedom Wallet Bot

> **AI-powered Telegram Bot for 24/7 Vietnamese Customer Support**
>
> Hỗ trợ khách hàng tự động, tích hợp Google Sheets, theo dõi giao dịch, và gamification.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-blue)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Documentation](#-documentation)

---

## �️ Architecture High-Level

```
┌─────────────────────────────────────────────────────────┐
│                      TELEGRAM                           │
│              (Users/Admins Interaction)                 │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                   HANDLERS                              │
│         (Input → Service → Response)                    │
│   /user  /premium  /sheets  /admin  /engagement        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│                   SERVICES                              │
│         (Orchestrate Workflows)                         │
│   Payment • Analytics • User • Transaction • Sheets     │
└───────┬──────────────────────────────────────┬──────────┘
        ↓                                      ↓
┌──────────────────┐                  ┌──────────────────┐
│    CORE          │                  │   EXTERNAL APIs  │
│ (Domain Rules)   │                  │  Sheets • OpenAI │
│ Fraud • State    │                  └──────────────────┘
│ Payment Rules    │
└────────┬─────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│                   MODELS & DATABASE                     │
│         User • Transaction • Subscription               │
└─────────────────────────────────────────────────────────┘
```

**Key Principles:**
- **Handlers**: Input/Output only, NO business logic
- **Services**: Orchestrate workflows, coordinate Core & APIs
- **Core**: Pure domain rules (fraud detection, validations, state machine)
- **Models**: Data entities

---

## �🎯 Overview

**Freedom Wallet Bot** là Telegram bot hỗ trợ người dùng Freedom Wallet App:
- ✅ Hỗ trợ 24/7 bằng AI (GPT-4)
- ✅ Tích hợp Google Sheets để quản lý tài chính
- ✅ Quick record giao dịch (3 cách)
- ✅ Hệ thống Premium/VIP với unlock flow
- ✅ Gamification: streaks, referrals, daily nurture
- ✅ Admin dashboard & fraud detection

**Tech Stack:**
- Python 3.9+
- python-telegram-bot
- OpenAI GPT-4
- Google Sheets API
- SQLite / PostgreSQL
- Railway / Google Cloud Run

---

## ✨ Features

### 👤 User Features
- **Registration & Onboarding** - Đăng ký nhanh với email/phone
- **Quick Record** - 3 cách ghi giao dịch:
  1. Direct input (nhập trực tiếp)
  2. Template selection (chọn template)
  3. Webhook integration (tự động)
- **Status & Balance** - Xem số dư, giao dịch gần đây
- **Daily Reminders** - Nhắc nhở ghi chi tiêu hàng ngày
- **Streak Tracking** - Theo dõi chuỗi ngày ghi chép
- **Referral System** - Giới thiệu bạn bè, nhận rewards

### 💎 Premium Features
- **Premium Menu** - Truy cập tính năng nâng cao
- **Advanced Analytics** - Phân tích chi tiết chi tiêu
- **Custom Templates** - Template tùy chỉnh
- **Priority Support** - Hỗ trợ ưu tiên
- **Unlock Flow** - Mở khóa từng bước với guided tour

### 🛡️ Admin Features
- **Metrics Dashboard** - Thống kê người dùng, revenue
- **Fraud Detection** - Phát hiện hành vi bất thường
- **Payment Management** - Quản lý thanh toán, subscriptions
- **User Management** - Xem & quản lý users
- **Callback Handlers** - Xử lý admin actions

### 🧠 AI Features
- **GPT-4 Context** - Hiểu ngữ cảnh người dùng
- **FAQ Auto-response** - Trả lời tự động 100+ câu hỏi
- **Smart Prompts** - Gợi ý thông minh
- **Knowledge Base** - RAG với embeddings

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9 or higher
python --version

# Git
git --version
```

### Installation

```bash
# 1. Clone repository
git clone <repo-url>
cd FreedomWalletBot

# 2. Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup configuration
cp config/.env.example config/.env

# Edit config/.env with your tokens
```

### Configuration

```bash
# config/.env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///data/bot.db
GOOGLE_SHEETS_CREDENTIALS=config/credentials/google_service_account.json

# Optional
ENABLE_AI=true
ENABLE_ADMIN=true
LOG_LEVEL=INFO
```

### Run Bot

```bash
# Development mode
python main.py

# Production mode (with logging)
python main.py --prod
```

---

## 📁 Project Structure

```
FreedomWalletBot/
│
├── main.py                         # 🚀 Bot entry point
├── requirements.txt                # 📦 Dependencies
├── README.md                       # 📖 This file
├── REFACTORING_PLAN.md            # 🏗️ Restructure plan
│
├── config/                         # ⚙️ Configuration
│   ├── settings.py                 # Settings manager (Pydantic)
│   ├── .env.example                # Environment template
│   └── credentials/
│       └── google_service_account.json
│
├── app/                            # 🎯 Main application
│   ├── handlers/                   # Request handlers
│   │   ├── user/                   # User-facing handlers
│   │   ├── premium/                # Premium features
│   │   ├── sheets/                 # Google Sheets integration
│   │   ├── admin/                  # Admin functions
│   │   ├── engagement/             # Gamification
│   │   ├── support/                # Support & guides
│   │   └── core/                   # Core handlers
│   │
│   ├── services/                   # Business logic services
│   ├── keyboards/                  # Telegram keyboards
│   ├── ai/                         # AI/GPT integration
│   ├── core/                       # Core business logic
│   ├── knowledge/                  # Knowledge base & FAQ
│   ├── middleware/                 # Middleware
│   ├── jobs/                       # Background jobs
│   └── utils/                      # Utilities
│
├── models/                         # Database models
├── migrations/                     # DB migrations
├── tests/                          # Tests
├── scripts/                        # Utility scripts
├── data/                           # Runtime data
│   ├── logs/                       # Logs
│   └── bot.db                      # SQLite database
├── media/                          # Media assets
│
└── docs/                           # 📚 Documentation
    ├── README.md                   # Docs navigation
    ├── architecture/               # Architecture docs
    ├── guides/                     # User guides
    ├── flows/                      # Flow diagrams
    ├── specifications/             # Specs
    └── archive/                    # Old docs
```

### Key Directories Explained

**`/app/handlers`** - Request handlers grouped by feature:
- `user/` - User flows (registration, quick record, status)
- `premium/` - Premium features (unlock flow, premium menu)
- `sheets/` - Google Sheets integration
- `admin/` - Admin dashboard & management
- `engagement/` - Gamification (streaks, referrals, reminders)
- `support/` - Support & setup guides
- `core/` - Core handlers (message, callback, webapp)

**`/app/services`** - Business logic (separate from handlers):
- Payment processing
- Analytics & metrics
- Google Sheets API client
- ROI calculator
- Recommendations

**`/app/keyboards`** - All Telegram keyboards:
- `user_keyboards.py` - User flow keyboards
- `premium_keyboards.py` - Premium keyboards
- `admin_keyboards.py` - Admin keyboards
- `common_keyboards.py` - Shared keyboards

**`/app/ai`** - AI integration:
- GPT client
- Context management
- Prompts

**`/app/core`** - Core business logic:
- State machine
- Program manager
- Fraud detection
- Reminder scheduler
- Subscription management

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | ✅ Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | ✅ Yes | - |
| `DATABASE_URL` | Database connection string | No | `sqlite:///data/bot.db` |
| `GOOGLE_SHEETS_CREDENTIALS` | Path to service account JSON | ✅ Yes | - |
| `ENABLE_AI` | Enable AI features | No | `true` |
| `ENABLE_ADMIN` | Enable admin features | No | `true` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

### Google Sheets Setup

1. Create Google Cloud Project
2. Enable Google Sheets API
3. Create Service Account
4. Download credentials JSON
5. Place in `config/credentials/google_service_account.json`
6. Share your sheets with service account email

Full guide: [docs/guides/SHEETS_SETUP.md](docs/guides/SHEETS_SETUP.md)

---

## 💻 Development

### Adding a New Handler

```python
# app/handlers/user/my_feature.py

from telegram import Update
from telegram.ext import ContextTypes

async def my_feature_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my feature."""
    user_id = update.effective_user.id
    
    # Call service layer
    from app.services.my_service import process_feature
    result = await process_feature(user_id)
    
    # Use keyboard
    from app.keyboards.user_keyboards import my_feature_keyboard
    keyboard = my_feature_keyboard()
    
    await update.message.reply_text(
        result,
        reply_markup=keyboard
    )
```

### Register in main.py

```python
from app.handlers.user.my_feature import my_feature_handler

application.add_handler(CommandHandler("myfeature", my_feature_handler))
```

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions < 50 lines
- Separate business logic to services
- Don't hard-code keyboards in handlers

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feat/my-feature

# 2. Write code following structure
app/handlers/user/my_feature.py

# 3. Add tests
tests/test_my_feature.py

# 4. Run tests
python -m pytest tests/test_my_feature.py

# 5. Commit
git commit -m "feat: add my feature"

# 6. Push & create PR
git push origin feat/my-feature
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_registration.py

# Run with coverage
python -m pytest --cov=app tests/

# Run with verbose output
python -m pytest -v
```

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_services.py
│   ├── test_keyboards.py
│   └── test_utils.py
├── integration/            # Integration tests
│   ├── test_registration_flow.py
│   └── test_sheets_integration.py
└── fixtures/               # Test fixtures
    └── mock_data.py
```

---

## 🚢 Deployment

### Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Add environment variables
railway variables set TELEGRAM_BOT_TOKEN=xxx
railway variables set OPENAI_API_KEY=xxx

# 5. Deploy
railway up
```

### Google Cloud Run

```bash
# Deploy
gcloud run deploy freedom-wallet-bot \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated
```

### Environment Variables (Production)

Set in Railway/Cloud Run dashboard:
- `TELEGRAM_BOT_TOKEN`
- `OPENAI_API_KEY`
- `DATABASE_URL` (PostgreSQL recommended)
- `GOOGLE_SHEETS_CREDENTIALS` (base64 encoded JSON)

Full deployment guide: [docs/guides/DEPLOYMENT.md](docs/guides/DEPLOYMENT.md)

---

## 📚 Documentation

### Essential Docs

- **[REFACTORING_PLAN.md](REFACTORING_PLAN.md)** - Complete refactoring plan
- **[ARCHITECTURE_RULES.md](ARCHITECTURE_RULES.md)** - 🔒 **MUST READ** - 3 Laws & Enforcement
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Executive summary
- **[docs/architecture/OVERVIEW.md](docs/architecture/OVERVIEW.md)** - System architecture
- **[docs/guides/GETTING_STARTED.md](docs/guides/GETTING_STARTED.md)** - Getting started guide
- **[docs/guides/ADDING_FEATURES.md](docs/guides/ADDING_FEATURES.md)** - How to add features
- **[docs/flows/USER_FLOWS.md](docs/flows/USER_FLOWS.md)** - User flow diagrams

### Browse All Docs

See [docs/README.md](docs/README.md) for full documentation index.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feat/amazing-feature`)
3. Follow code style & structure guidelines
4. Write tests
5. Commit changes (`git commit -m 'feat: add amazing feature'`)
6. Push to branch (`git push origin feat/amazing-feature`)
7. Open Pull Request

### Commit Convention

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Add tests
- `chore:` - Maintenance

---

## 📊 Monitoring

### Logs

```bash
# View logs
tail -f data/logs/bot.log

# Search for errors
grep ERROR data/logs/bot.log

# Last 100 lines
tail -100 data/logs/bot.log
```

### Admin Commands

```
/admin stats        - Bot statistics
/admin users        - User count
/admin metrics      - Key metrics
/admin fraud        - Fraud alerts
```

---

## 🐛 Troubleshooting

### Bot not starting

```bash
# Check Python version
python --version  # Must be 3.9+

# Check dependencies
pip install -r requirements.txt

# Check .env file
cat config/.env

# Check logs
tail -50 data/logs/bot.log
```

### Import errors after refactor

```bash
# Update imports following new structure
# Old: from bot.handlers.start import start
# New: from app.handlers.user.start import start
```

### Google Sheets not working

1. Check credentials file exists: `config/credentials/google_service_account.json`
2. Verify service account email has access to sheet
3. Check API is enabled in Google Cloud Console

---

## 📞 Support

- **Issues:** Create issue on GitHub
- **Discussions:** Use GitHub Discussions
- **Email:** [your-email@example.com]

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core bot functionality
- ✅ Registration & onboarding
- ✅ Quick record (3 methods)
- ✅ Google Sheets integration
- ✅ Premium unlock flow
- ✅ Admin dashboard

### Phase 2 (In Progress)
- 🟡 Code refactoring (see [REFACTORING_PLAN.md](REFACTORING_PLAN.md))
- 🟡 Test coverage > 80%
- 🟡 Performance optimization

### Phase 3 (Planned)
- ⏳ Mobile app integration
- ⏳ Advanced analytics
- ⏳ Multi-language support
- ⏳ Voice input for transactions

---

## 🙏 Acknowledgments

- python-telegram-bot team
- OpenAI for GPT-4 API
- Google Sheets API
- Railway for hosting

---

**Built with ❤️ for Freedom Wallet users**

*Last updated: 2026-02-12*
