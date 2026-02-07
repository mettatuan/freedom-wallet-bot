# Freedom Wallet Bot 🤖💰

**⚠️ EXPERIMENTAL PROJECT - MARKET TEST PHASE ⚠️**

This is an early-access market test for a financial habit tracking bot. This project is experimental and designed to validate product-market fit. **No monetization is implemented in this phase.**

## 📋 Overview

Freedom Wallet Bot is a Telegram-based bot designed to help users build better financial habits through gamification, social proof, and community engagement. The bot implements a referral-based growth system with tiered membership levels and includes comprehensive activity tracking and fraud detection mechanisms.

**Current Status:** Market Testing & Validation  
**Purpose:** Understand user behavior, test engagement mechanics, gather feedback  
**Monetization:** None (Free to use)

## ✨ Features

### 🎯 Core Functionality
- **Financial Habit Tracking**: Monitor and encourage healthy financial behaviors
- **Activity Monitoring**: Track user engagement and participation
- **Decay System**: Activity scores naturally decay over time to encourage consistent engagement
- **Fraud Detection**: Automated systems to detect and prevent abuse

### 👥 Referral-Based Growth System
The bot implements a three-tier membership system based on referrals:

- **FREE Tier**: Available to all new users
- **VIP Tier**: Unlocked through successful referrals
- **SUPER VIP Tier**: Premium tier for highly engaged users with extensive networks

### 📊 Analytics & Monitoring
- User activity tracking
- Engagement metrics
- Referral chain analysis
- Fraud pattern detection

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Bot Framework**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: [Railway](https://railway.app)
- **Architecture**: Event-driven bot with webhook support

## 🚀 Local Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Telegram Bot Token (obtain from [@BotFather](https://t.me/botfather))
- PostgreSQL (for production-like environment) or SQLite will be used by default

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/mettatuan/freedom-wallet-bot.git
   cd freedom-wallet-bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration (see Environment Variables section below)

5. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

6. **Run the bot**
   ```bash
   python bot.py
   ```

## 🔐 Environment Variables

Create a `.env` file in the project root with the following variables:

### Required Variables

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here          # Get from @BotFather
TELEGRAM_BOT_USERNAME=YourBotUsername           # Your bot's username

# Database Configuration
DATABASE_URL=sqlite:///freedom_wallet.db         # SQLite for local dev
# DATABASE_URL=postgresql://user:pass@host:5432/dbname  # PostgreSQL for production

# Application Settings
ENVIRONMENT=development                          # development, staging, or production
LOG_LEVEL=INFO                                  # DEBUG, INFO, WARNING, ERROR
```

### Optional Variables

```bash
# Webhook Configuration (for production deployment)
WEBHOOK_URL=https://your-app.railway.app        # Your deployment URL
WEBHOOK_PORT=8443                               # Port for webhook server

# Feature Flags
ENABLE_FRAUD_DETECTION=true                     # Enable/disable fraud detection
ENABLE_DECAY_SYSTEM=true                        # Enable/disable activity decay

# Referral System Configuration
FREE_TIER_MAX_REFERRALS=10                      # Max referrals for free tier
VIP_TIER_THRESHOLD=5                            # Referrals needed for VIP
SUPER_VIP_TIER_THRESHOLD=25                     # Referrals needed for Super VIP

# Activity Decay Settings
ACTIVITY_DECAY_DAYS=7                           # Days before activity starts decaying
ACTIVITY_DECAY_RATE=0.1                         # Daily decay rate (10%)

# Rate Limiting
RATE_LIMIT_MESSAGES=30                          # Messages per minute per user
RATE_LIMIT_WINDOW=60                            # Time window in seconds

# Admin Configuration
ADMIN_USER_IDS=123456789,987654321             # Comma-separated admin Telegram user IDs
```

## 📦 Project Structure

```
freedom-wallet-bot/
├── bot.py                  # Main bot application
├── config.py              # Configuration management
├── database/              # Database models and migrations
├── handlers/              # Bot command and message handlers
├── services/              # Business logic services
│   ├── referral.py       # Referral system logic
│   ├── activity.py       # Activity tracking
│   ├── fraud.py          # Fraud detection
│   └── decay.py          # Activity decay system
├── utils/                 # Utility functions
├── scripts/               # Maintenance and setup scripts
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚢 Deployment

### Railway Deployment

This bot is designed to be deployed on [Railway](https://railway.app):

1. **Connect your GitHub repository** to Railway
2. **Add environment variables** in Railway dashboard
3. **Configure the start command**:
   ```bash
   python bot.py
   ```
4. **Deploy**: Railway will automatically deploy on push to main branch

### Database Setup

For production deployment with PostgreSQL:

1. Add a PostgreSQL database in Railway
2. Update `DATABASE_URL` environment variable with the provided connection string
3. Run migrations: `python scripts/migrate.py`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_referral.py
```

## 📈 Monitoring & Maintenance

- **Logs**: Check application logs for errors and user activity
- **Database**: Regular backups recommended for production
- **Fraud Detection**: Monitor fraud detection alerts and adjust thresholds
- **Activity Decay**: Review decay rates and adjust based on user feedback

## 🤝 Contributing

This is an experimental project in market test phase. Contributions, feedback, and suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Disclaimer

**This is an experimental market test project.** Features may change, be added, or removed based on user feedback and testing results. There is no monetization in this phase - the bot is completely free to use.

Data collected during this phase will be used solely for improving the product and understanding user needs. We are committed to user privacy and responsible data handling.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support & Contact

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/mettatuan/freedom-wallet-bot/issues)
- **Telegram**: Contact the bot admin through the bot itself
- **Repository**: [github.com/mettatuan/freedom-wallet-bot](https://github.com/mettatuan/freedom-wallet-bot)

## 🎯 Roadmap (Market Test Phase)

- ✅ Referral system implementation
- ✅ Activity tracking and decay
- ✅ Fraud detection basics
- 🔄 User feedback collection
- 🔄 Engagement metrics analysis
- 📋 Feature refinement based on testing
- 📋 Community building and growth
- 📋 Data-driven product decisions

---

**Remember**: This is a market test. Your feedback shapes the future of this project! 🚀
