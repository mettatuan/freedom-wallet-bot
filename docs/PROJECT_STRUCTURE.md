# 📁 Project Structure Explained

```
Freedom Wallet Bot/
│
├── 📋 README.md                    # Project overview & quick start
├── 📖 BOT_MASTER_PROMPT.md         # Complete bot specification (15k lines)
├── 🚀 GETTING_STARTED.md           # 5-minute quick setup guide
├── 📘 IMPLEMENTATION_GUIDE.md       # Step-by-step build instructions
├── 📝 QUICK_REFERENCE.md           # Command cheat sheet
├── 📄 requirements.txt             # Python dependencies
├── 🚦 main.py                      # Bot entry point (run this!)
│
├── config/                         # Configuration files
│   ├── __init__.py
│   ├── settings.py                 # Settings with Pydantic + .env
│   └── .env.example                # Environment variables template
│
├── bot/                            # Main bot package
│   ├── __init__.py
│   │
│   ├── handlers/                   # Command & message handlers
│   │   ├── __init__.py
│   │   ├── start.py                # /start and /help commands
│   │   ├── message.py              # Text message processing (FAQ)
│   │   ├── support.py              # /support command (Google Sheets)
│   │   └── callback.py             # Inline button callbacks
│   │
│   ├── ai/                         # AI integration (Phase 2)
│   │   ├── __init__.py
│   │   └── gpt_client.py           # OpenAI GPT-4 client
│   │
│   ├── knowledge/                  # Knowledge base
│   │   ├── __init__.py
│   │   └── faq.json                # FAQ database (100+ Q&A)
│   │
│   └── utils/                      # Utility modules
│       ├── __init__.py
│       └── database.py             # SQLAlchemy models (Phase 2)
│
├── data/                           # Data storage
│   ├── logs/                       # Bot logs
│   │   └── bot.log                 # Daily rotating logs
│   └── bot.db                      # SQLite database (Phase 2)
│
├── media/                          # Media files
│   ├── screenshots/                # Tutorial screenshots
│   └── gifs/                       # Tutorial GIFs
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   └── test_basic.py               # Basic FAQ tests
│
├── 🐍 .gitignore                   # Git ignore rules
├── ⚙️ pytest.ini                   # Pytest configuration
├── 🚀 Procfile                     # Railway/Heroku deployment
└── 📦 railway.json                 # Railway configuration

```

---

## 📚 File Descriptions

### Core Files

**main.py** (Entry Point)
- Initializes bot application
- Registers all handlers
- Starts polling or webhook
- Run with: `python main.py`

**requirements.txt** (Dependencies)
- python-telegram-bot: Bot framework
- openai: GPT-4 API client
- gspread: Google Sheets integration
- sqlalchemy: Database ORM
- loguru: Logging
- chromadb: Vector database (Phase 3)

### Configuration

**config/settings.py** (Settings Manager)
- Loads from `.env` file using Pydantic
- Environment-specific configs
- Feature flags (ENABLE_AI, ENABLE_ADMIN)

**config/.env.example** (Template)
- Copy to `.env` and fill in:
  - TELEGRAM_BOT_TOKEN
  - OPENAI_API_KEY (Phase 2)
  - GOOGLE_SHEETS_CREDENTIALS (Phase 1)
  - Database URLs
  - Rate limits

### Handlers (bot/handlers/)

**start.py** - Welcome & Help
- `/start`: Welcome message with inline keyboard
- `/help`: Command menu
- Shows 6 quick action buttons

**message.py** - Message Processing
- Phase 1: Keyword-based FAQ matching
- Phase 2: Upgrade to GPT-4 AI
- Searches `faq.json` for answers
- Returns structured responses with buttons

**support.py** - Support Tickets
- `/support`: Create support ticket
- ConversationHandler for multi-step flow
- Saves to Google Sheets (7 columns)
- Returns ticket ID to user

**callback.py** - Button Callbacks
- Handles all inline button clicks
- Routes to appropriate actions
- Updates message text dynamically

### AI (bot/ai/)

**gpt_client.py** - GPT-4 Integration (Phase 2)
- AsyncOpenAI client wrapper
- System prompt with bot personality
- Context memory (last 5 messages)
- Function calling support (Phase 3)

### Knowledge Base (bot/knowledge/)

**faq.json** - Structured FAQ (100+ Q&A)
- 7 categories:
  - Transactions (Giao dịch)
  - 6 Jars (6 Hũ tiền)
  - Investments (Đầu tư)
  - Assets (Tài sản)
  - Debts (Khoản nợ)
  - Reports (Báo cáo)
  - Troubleshooting (Khắc phục lỗi)
- Each Q: keywords array + formatted answer
- Default responses: greeting, thanks, goodbye

### Utils (bot/utils/)

**database.py** - Database Models (Phase 2)
- SQLAlchemy ORM models:
  - User: Telegram user info
  - ConversationContext: Chat history (5 messages)
  - SupportTicket: Ticket tracking
  - MessageLog: Analytics
- Helper functions:
  - save_user_to_db()
  - get_user_context()
  - save_message_to_context()

### Documentation

**BOT_MASTER_PROMPT.md** (15,000 lines)
- Complete specification document
- Bot personality, capabilities, architecture
- Conversation flow examples
- System prompts for GPT-4
- Implementation phases (4 phases)
- Testing checklist
- Security & privacy guidelines
- Success metrics

**IMPLEMENTATION_GUIDE.md**
- Phase 1 MVP: BotFather setup → Basic handlers → FAQ system → Google Sheets tickets
- Phase 2 AI: OpenAI integration → Context memory → Vector search
- Phase 3 Production: Railway deployment → Webhook → Monitoring
- Includes working code examples (copy-paste ready)

**GETTING_STARTED.md**
- 5-minute quick start
- Prerequisites checklist
- Step-by-step setup commands
- Troubleshooting tips

**QUICK_REFERENCE.md**
- Bot commands cheat sheet
- Example questions (Vietnamese + English)
- Inline buttons reference
- Admin commands (Phase 3)

---

## 🔄 Development Phases

### Phase 1: MVP (Current ✅)
**Status:** All files created, ready to implement
**Files needed:**
- ✅ main.py
- ✅ config/settings.py
- ✅ bot/handlers/start.py
- ✅ bot/handlers/message.py (FAQ only)
- ✅ bot/handlers/support.py
- ✅ bot/knowledge/faq.json

**Run MVP:**
```powershell
python main.py
```

### Phase 2: AI Enhancement
**Upgrade:** Add GPT-4 for intelligent conversations
**Files to activate:**
- ✅ bot/ai/gpt_client.py (already created)
- ✅ bot/utils/database.py (already created)
- Update bot/handlers/message.py (uncomment AI section)
- Enable `ENABLE_AI=true` in .env

**Prerequisites:**
- OpenAI API key
- SQLite database (or PostgreSQL)

### Phase 3: Production
**Deployment:** Railway or Google Cloud Run
**Files needed:**
- ✅ Procfile (already created)
- ✅ railway.json (already created)
- Configure webhook instead of polling
- Add monitoring (Sentry)
- Setup Redis cache
- Enable admin commands

---

## 🎯 Quick Start Workflow

1. **Setup (5 min)**
   ```powershell
   cd "D:/Projects/FreedomWalletBot"
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   cp config/.env.example config/.env
   # Edit .env with Telegram token
   ```

2. **Run MVP (Phase 1)**
   ```powershell
   python main.py
   ```

3. **Test in Telegram**
   - /start → Welcome message
   - "Làm sao thêm giao dịch?" → FAQ answer
   - /support → Create ticket

4. **Add AI (Phase 2)**
   - Get OpenAI API key
   - Add to .env: `OPENAI_API_KEY=sk-...`
   - Set `ENABLE_AI=true`
   - Restart bot

5. **Deploy (Phase 3)**
   - Push to GitHub
   - Connect Railway
   - Set environment variables
   - Deploy!

---

## 🔍 File Dependencies

```
main.py
├── config/settings.py (.env)
├── bot/handlers/start.py
├── bot/handlers/message.py
│   └── bot/knowledge/faq.json
├── bot/handlers/support.py
│   └── [Google Sheets API]
├── bot/handlers/callback.py
└── bot/ai/gpt_client.py [Phase 2]
    └── bot/utils/database.py
```

---

## 📊 Complexity Levels

**Beginner (Phase 1):**
- FAQ keyword matching
- Simple button menus
- Google Sheets integration

**Intermediate (Phase 2):**
- GPT-4 AI integration
- Context memory
- Database operations

**Advanced (Phase 3):**
- Production deployment
- Webhook + Redis
- API integration with Freedom Wallet
- Machine learning analytics

---

## 🆘 Where to Start?

1. **Just run MVP:** Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Understand architecture:** Read [BOT_MASTER_PROMPT.md](BOT_MASTER_PROMPT.md)
3. **Build step-by-step:** Follow [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
4. **Quick commands:** Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

**Happy coding! 🤖💙**
