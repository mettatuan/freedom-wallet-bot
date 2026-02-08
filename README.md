# 🤖 Freedom Wallet Bot

AI-powered Telegram customer support bot for Freedom Wallet app.

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
cp config/.env.example config/.env

# Edit .env with your tokens
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
```

### 3. Run Bot
```bash
# Development mode
python main.py

# Production mode
python main.py --prod
```

## 📁 Project Structure

```
freedom-wallet-bot/
├── bot/
│   ├── handlers/       # Command handlers
│   ├── ai/            # AI/GPT integration
│   ├── knowledge/     # FAQ & docs
│   └── utils/         # Helpers
├── data/              # Database & storage
├── media/             # Tutorial assets
├── config/            # Configuration
├── tests/             # Unit tests
└── main.py           # Entry point
```

## 🎯 Features

- ✅ 24/7 Vietnamese customer support
- 🤖 GPT-4 powered conversations
- 📚 Freedom Wallet knowledge base
- 🎓 Interactive tutorials
- 🔧 Troubleshooting assistance
- 💡 Financial tips (6 Jars method)
- 🆘 Support ticket system

## 📖 Documentation

See [BOT_MASTER_PROMPT.md](BOT_MASTER_PROMPT.md) for full specifications.

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Test specific handler
python -m pytest tests/test_handlers.py
```

## 🚢 Deployment

### Railway
```bash
railway login
railway init
railway up
```

### Google Cloud Run
```bash
gcloud run deploy freedom-wallet-bot \
  --source . \
  --platform managed \
  --region asia-southeast1
```

## 📊 Monitoring

- Bot stats: `/admin stats`
- Logs: Check `data/logs/bot.log`
- Analytics: Google Sheets dashboard

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📝 License

MIT License - See LICENSE file

## 🆘 Support

- Bot issues: Open GitHub issue
- App support: Use @FreedomWalletBot
- Email: support@freedomwallet.com

---

**Made with ❤️ for Freedom Wallet users**
