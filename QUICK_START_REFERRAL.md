# 🚀 Quick Start: Test Referral System

## Prerequisites

1. **Telegram Bot Token**
   - Message [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Follow instructions
   - Copy token: `123456789:ABCdefGHIjklMNOpqrSTUvwxyz`

2. **Python Environment**
   - Python 3.9+
   - Virtual environment activated

---

## Setup Steps

### 1. Configure Environment

Create `.env` file in project root:

```bash
# d:\Projects\FreedomWalletBot\.env

# Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
BOT_USERNAME=YourBotUsername

# Database
DATABASE_URL=sqlite:///data/bot.db

# Environment
ENV=development
LOG_LEVEL=INFO

# OpenAI (for AI assistant - optional for now)
OPENAI_API_KEY=your_openai_key_here
```

### 2. Install Dependencies

```powershell
cd "d:\Projects\FreedomWalletBot"
python -m pip install -r requirements.txt
```

### 3. Initialize Database

```powershell
python -c "from bot.utils.database import Base, engine; Base.metadata.create_all(engine); print('✅ Database created!')"
```

### 4. Start Bot

```powershell
python main.py
```

You should see:
```
2026-02-07 10:30:00 - __main__ - INFO - 🤖 Freedom Wallet Bot is starting...
2026-02-07 10:30:01 - __main__ - INFO - ✅ Bot started in development mode
```

---

## Test Referral System

### Test Case 1: Generate Referral Link

1. **Open Telegram**
2. **Search for your bot** (use username from `.env`)
3. **Send:** `/start`
4. **Expected:** Welcome message with tier badge "🎯 TRIAL (0/2 refs)"
5. **Click button:** "🎁 Giới thiệu bạn bè"
6. **Expected:** Referral menu showing:
   - Your referral code (8 chars)
   - Link: `https://t.me/YourBot?start=ABC123`
   - Status: 🔒 Đang khóa
   - 0 người đã giới thiệu

### Test Case 2: Use Referral Link

**Option A: Test with Another Telegram Account (Recommended)**

1. **Copy your referral link** from Test Case 1
2. **Open another Telegram account** (phone/desktop/web)
3. **Paste and open the link**
4. **Send:** `/start` (should auto-detect referral)
5. **Expected (Account B):**
   ```
   🎉 Chào mừng!
   Bạn được giới thiệu bởi [Your Name].
   ...
   ```
6. **Check Account A:**
   - Should receive notification: "🎊 Tin vui! Bạn vừa giới thiệu thành công..."
   - Run `/referral` → See "Đã giới thiệu: 1 người"
   - Status: "🎯 Còn 1 người nữa để mở khóa FREE!"

**Option B: Simulate with Database (Quick Test)**

```powershell
# Add test referral via Python console
python

>>> from bot.utils.database import *
>>> import asyncio
>>> 
>>> async def test():
...     # Simulate 2 referrals for user 123456789
...     await create_referral(123456789, 111111111, "ABC123")
...     await create_referral(123456789, 222222222, "ABC123")
...     print("✅ Added 2 referrals")
>>> 
>>> asyncio.run(test())
```

### Test Case 3: AUTO-UNLOCK FREE

1. **Complete 2 referrals** (from Test Case 2)
2. **Expected:** After 2nd referral, Account A receives:
   ```
   🎉🎉🎉 CHÚC MỪNG! 🎉🎉🎉
   Bạn vừa mở khóa FREE FOREVER!
   ...
   ```
3. **Verify:**
   - Run `/start` → Badge shows "✅ FREE FOREVER"
   - Run `/referral` → Status: "✅ FREE Unlocked"

### Test Case 4: Edge Cases

**A. Self-Referral (Should Fail)**
1. Copy your own referral link
2. Click it in same account
3. **Expected:** "😅 Bạn không thể tự giới thiệu chính mình!"

**B. Already Referred (Should Fail)**
1. User B already referred by A
2. User C sends referral link to B
3. B clicks C's link
4. **Expected:** "Bạn đã được giới thiệu bởi người khác rồi!"

---

## Check Database

**SQLite Browser:**
```powershell
# Install DB Browser for SQLite
# Open: d:\Projects\FreedomWalletBot\data\bot.db
```

**Python Console:**
```powershell
python

>>> from bot.utils.database import *
>>> session = SessionLocal()
>>> 
>>> # Check users
>>> users = session.query(User).all()
>>> for u in users:
...     print(f"User {u.id}: {u.first_name} | Refs: {u.referral_count} | Unlocked: {u.is_free_unlocked}")
>>> 
>>> # Check referrals
>>> refs = session.query(Referral).all()
>>> for r in refs:
...     print(f"Ref {r.id}: {r.referrer_id} -> {r.referred_id} ({r.status})")
>>> 
>>> session.close()
```

---

## Troubleshooting

### Bot doesn't start

**Error:** `telegram.error.InvalidToken`
- ✅ Check `.env` has correct `TELEGRAM_BOT_TOKEN`
- ✅ No spaces around `=` in `.env`

**Error:** `ImportError: No module named 'telegram'`
- ✅ Run: `pip install python-telegram-bot==22.6`

### Referral code not showing

**Issue:** `/referral` shows error
- ✅ Check database has `User` record
- ✅ Run `/start` first to create user
- ✅ Check `referral_code` field is populated

### Deep link not working

**Issue:** Click link → normal start (no referral detected)
- ✅ Verify link format: `t.me/BotUsername?start=CODE` (not `/start CODE`)
- ✅ Check `context.args` in logs
- ✅ Test with clean account (not already in bot)

### Notification not sent

**Issue:** Referrer doesn't receive "Tin vui!" message
- ✅ Check referrer hasn't blocked bot
- ✅ Look for try/except errors in logs
- ✅ Verify `context.bot.send_message()` calls

---

## Next Steps

After testing referral system:

### Phase 1: Landing Page Integration
- [ ] Add referral signup form to landing page
- [ ] Pre-fill Telegram deep link on "Đăng ký FREE" button

### Phase 2: Analytics Dashboard
- [ ] Create `/stats` admin command
- [ ] Show: Total users, referrals, conversion rate
- [ ] Export CSV for analysis

### Phase 3: Payment Integration
- [ ] Implement VNPay/MoMo for PREMIUM tier
- [ ] Auto-upgrade subscription after payment
- [ ] Email receipts + invoices

### Phase 4: Google Sheets Sync
- [ ] Sync user data to Google Sheets
- [ ] Real-time referral leaderboard
- [ ] Auto-send welcome email with template link

---

## Command Reference

| Command | Description |
|---------|-------------|
| `/start` | Welcome + Menu |
| `/help` | Command list |
| `/referral` | Referral stats + link |
| `/support` | Contact support |

---

## Directory Structure

```
Freedom Wallet Bot/
├── main.py                 # Entry point
├── config/
│   └── settings.py        # Config loader
├── bot/
│   ├── handlers/
│   │   ├── start.py       # /start command
│   │   ├── referral.py    # /referral command + deep link
│   │   ├── callback.py    # Button clicks
│   │   └── ...
│   └── utils/
│       └── database.py    # Models + referral functions
├── data/
│   ├── bot.db            # SQLite database
│   └── logs/
│       └── bot.log       # Log file
├── .env                   # Environment variables
└── requirements.txt       # Dependencies
```

---

**Ready to test!** 🚀

Questions? Check [REFERRAL_SYSTEM.md](REFERRAL_SYSTEM.md) for detailed documentation.
