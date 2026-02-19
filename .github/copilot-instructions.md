# Freedom Wallet Bot - AI Development Guide

## Architecture Overview

**Freedom Wallet Bot** is a Telegram bot built with **python-telegram-bot** (v20+) providing customer support for the Freedom Wallet app. Uses Vietnamese language for all user-facing messages.

### Core Components

1. **Main Entry** (`main.py`): Application setup, handler registration, and routing orchestration
2. **Handlers** (`app/handlers/`): 7 domain-separated modules with 40+ handlers
   - `user/` - Registration, commands, FREE tier flows
   - `premium/` - VIP tiers, unlock flows, premium features
   - `engagement/` - Referrals, daily reminders, streaks
   - `admin/` - Fraud review, payment approval, metrics
   - `sheets/` - Google Sheets integration, setup wizards
   - `core/` - Callbacks, messages, main menu routing (2800+ lines)
   - `support/` - Support tickets, setup guides
3. **Database** (`app/utils/database.py`): SQLAlchemy models with SQLite, session management via `get_db()`
4. **Services** (`app/services/`): Business logic layer (analytics, payments, sheets I/O, recommendations)
5. **Messages** (`app/messages/`): Centralized Vietnamese message templates (nurture, onboarding, reminders)
6. **Keyboards** (`app/keyboards/`): Inline and reply keyboard factories (premium_keyboards.py, user_keyboards.py)

## Critical Architectural Decisions

### Legacy Architecture (Active)

**Clean Architecture experiment was rolled back** (see [ARCHITECTURE_DECISION.md](ARCHITECTURE_DECISION.md)). The production system uses legacy architecture with:
- Handlers directly calling database via `get_db()` (53+ instances documented in [HANDLER_AUDIT_REPORT.md](HANDLER_AUDIT_REPORT.md))
- Handler-to-handler calls (26+ instances across 15+ handlers)
- Services used selectively for complex business logic (payment verification, metrics calculation)

**DO NOT** import or reference `src/` or `_archive/clean_architecture_experiment/` - archived code only.

### Database Column Mapping Pattern

The `User` model uses intentional column mapping (NOT a hack):
```python
# Model attribute: id (app code uses this)
# Database column: user_id (actual SQLite column)
id = Column("user_id", Integer, primary_key=True, autoincrement=False)

# Model attribute: username
# Database column: telegram_username  
username = Column("telegram_username", String(100), nullable=True)
```

**Rationale**: Preserves 100+ code references across 50+ files, avoids high-risk refactor. See [ARCHITECTURE_DECISION.md](ARCHITECTURE_DECISION.md) for details.

## Handler Registration Pattern

**Critical Order**: Handlers are registered in `main.py` with explicit priority groups to prevent conflicts:

1. **Commands** (group 0, highest priority): `/start`, `/help`, `/balance`, etc.
2. **ConversationHandlers** (default group): Registration, support tickets, sheets setup
3. **CallbackQueryHandlers** (default group): Inline button clicks, pattern-based routing
4. **MessageHandler** (group 100, lowest priority): Catch-all for AI conversations

### Registration Example
```python
# Domain-specific handlers use register_* functions
from app.handlers.premium.vip import register_vip_handlers
register_vip_handlers(application)

# Which internally adds handlers:
def register_vip_handlers(application):
    application.add_handler(CommandHandler("vip", vip_status_command))
    application.add_handler(CallbackQueryHandler(handle_vip_benefits, pattern="^vip_benefits_"))
```

### ConversationHandler Pattern
Multi-step flows (registration, sheets setup) use `ConversationHandler` with state constants:
```python
AWAITING_EMAIL = "awaiting_email"
AWAITING_PHONE = "awaiting_phone"

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("register", start_registration)],
    states={
        AWAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
        AWAITING_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
    },
    fallbacks=[CommandHandler("cancel", cancel_registration)],
    per_message=False,  # CRITICAL for callbacks starting conversations
    per_chat=True,
    per_user=True
)
```

## Development Workflows

### Running the Bot

**Local development**:
```bash
# Using start.bat (recommended - auto-creates .venv)
start.bat

# Or manually with venv
.venv\Scripts\python.exe main.py
```

**Configuration**: Requires `.env` in project root (see `.env.example`):
- `TELEGRAM_BOT_TOKEN` - Bot API token
- `OPENAI_API_KEY` - For AI conversations
- `FREEDOM_WALLET_API_URL` - Google Apps Script Web App URL
- `ADMIN_USER_ID` - Admin Telegram ID for fraud/payment review

### Testing

```bash
# Run all tests
pytest

# Specific test file
pytest tests/integration/test_registration_flow.py

# Test with output
pytest -v -s tests/
```

**Common test patterns**: See `test_full_flow.py` and `test_button_flow.py` for handler testing examples.

### Adding New Features

1. **Define messages** in appropriate `app/messages/*.py` file (Vietnamese, HTML parse mode)
2. **Create keyboards** in `app/keyboards/premium_keyboards.py` or `user_keyboards.py`
3. **Implement handler** in domain-specific directory (`app/handlers/{domain}/`)
4. **Register handler** in `main.py` via domain's `register_*_handlers()` function
5. **Update database** if needed (models in `app/utils/database.py`, migrations in `migrations/`)

## Project-Specific Conventions

### Callback Data Naming
- **Format**: `{feature}_{action}` (e.g., `free_step3_copy_template`, `vip_benefits_RISING_STAR`)
- **Prefix separation**: Use prefixes to route to correct handler module:
  - `free_*` → `app/handlers/user/free_flow.py`
  - `vip_*` → `app/handlers/premium/vip.py`
  - `sheets_*` → `app/handlers/sheets/` (multiple files)
  - `qr_*` → Quick record handlers

### Message Format Standards
- **Language**: 100% Vietnamese for user-facing text
- **Parse mode**: Always use `parse_mode="Markdown"` (legacy uses HTML in some places, but Markdown is standard)
- **Emoji usage**: Consistent across features (🎯 goals, 💰 money, ✅ success, ❌ errors)
- **Tone**: Friendly, supportive, educational (not salesy)

### Database Access Pattern
```python
# Standard pattern in handlers:
from app.utils.database import get_db, User

db = next(get_db())
try:
    user = db.query(User).filter(User.id == user_id).first()
    # ... operations
    db.commit()
except Exception as e:
    db.rollback()
    logger.error(f"Error: {e}")
finally:
    db.close()
```

**Note**: 53+ handlers currently use direct DB access. Service layer refactor is aspirational, not current practice.

## Integration Points

### Google Apps Script API
- **Purpose**: Read/write transactions to user's Google Sheets
- **Client**: `app/services/sheets_api_client.py` (uses `FREEDOM_WALLET_API_URL` from `.env`)
- **Pattern**: All API calls go through Apps Script Web App, not direct Sheets API
- **Setup flow**: Users copy template sheet, deploy script, connect via `/connectsheets`

### Referral System
- **Tiers**: FREE (2+ refs), VIP tiers (10/50/100 refs)
- **Tracking**: `User.referral_code`, `User.referred_by`, `User.referral_count`
- **Unlock flow**: See `app/handlers/premium/unlock_calm_flow.py` (417 lines, step-by-step onboarding)

### Admin Features
- **Fraud review**: `/fraud_queue`, `/fraud_approve`, `/fraud_reject` (requires `ADMIN_USER_ID`)
- **Payment approval**: `/payment_pending`, `/payment_approve`, `/payment_reject`
- **Metrics**: Admin dashboard in `app/handlers/admin/admin_metrics.py`

## Common Pitfalls

1. **Don't skip `await query.answer()`** on callbacks - causes button loading hangs
2. **Don't hardcode messages in handlers** - use `app/messages/*.py` for maintainability
3. **Don't use group 0 for new handlers** unless critical priority needed (reserved for core commands)
4. **Don't forget `per_message=False`** when ConversationHandler starts from CallbackQuery
5. **Callbacks prefixed with `sheets_`, `free_`, `qr_`** are handled by specific modules - check routing in `app/handlers/core/callback.py` (skips these patterns)
6. **Multiple PowerShell terminals**: Check `Get-Process python` before running - kill duplicates to avoid conflicts
7. **UTF-8 encoding**: All logging uses UTF-8 with `errors='replace'` to prevent crashes on Vietnamese text

## Key Files to Reference

- [main.py](main.py) - Handler registration orchestration (447 lines)
- [app/handlers/core/main_menu.py](app/handlers/core/main_menu.py) - Main menu routing (2853 lines, 60+ callback handlers)
- [app/handlers/core/callback.py](app/handlers/core/callback.py) - Callback dispatcher with routing logic (1790 lines)
- [app/utils/database.py](app/utils/database.py) - All database models (527 lines, 56-column User schema)
- [ARCHITECTURE_DECISION.md](ARCHITECTURE_DECISION.md) - Why Clean Architecture was rolled back
- [HANDLER_AUDIT_REPORT.md](HANDLER_AUDIT_REPORT.md) - Current violations and refactor opportunities
- [DEPLOY.md](DEPLOY.md) - Production deployment steps for Google Apps Script + Railway
