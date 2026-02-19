# 🚀 QUICK START: Integration Guide
## Thêm Trust Economy vào FreedomWallet Bot hiện tại

---

## 📋 TÓM TẮT

Hướng dẫn này giúp bạn tích hợp **Trust Economy & Donation Model** vào bot Telegram hiện tại của bạn.

**Timeline:** 2-3 tuần (part-time)

---

## 🎯 PHASE 1: DATABASE SETUP (Week 1, Days 1-2)

### Bước 1: Tạo bảng mới

```sql
-- Chạy script SQL từ TRUST_ECONOMY_BLUEPRINT.md
-- Section V.1 - Database Schema

-- Hoặc sử dụng migration:
psql -U your_user -d freedomwallet < migrations/001_trust_economy.sql
```

### Bước 2: Update database module

Thêm vào `db.py`:

```python
# Import functions mới
from database.donations import (
    create_pending_donation,
    confirm_donation,
    get_donation_stats,
    get_community_stats
)

from database.milestones import (
    check_milestones,
    add_milestone,
    get_user_milestones
)

from database.referrals import (
    track_referral,
    get_referral_stats,
    increment_activated_referrals
)
```

### Bước 3: Seed initial data

```python
# Run once
python scripts/seed_milestones.py
```

---

## 🎯 PHASE 2: MILESTONE SYSTEM (Week 1, Days 3-5)

### Bước 1: Copy handler

```bash
# Copy donation_handler.py vào project
cp donation_handler.py app/handlers/
```

### Bước 2: Integrate vào bot.py

```python
# Trong bot.py
from handlers.donation_handler import DonationHandler

# Initialize
donation_handler = DonationHandler(db)

# Thêm sau khi user log transaction
async def log_transaction_handler(update, context):
    # ... existing code to log transaction ...
    
    # NEW: Check milestones
    await donation_handler.check_and_celebrate_milestones(update, context)

# Register callback handler
application.add_handler(CallbackQueryHandler(
    donation_handler.handle_donation_callback,
    pattern="^donate_|^pay_|^verify_|^fame_"
))
```

### Bước 3: Test milestone detection

```python
# Test script
python tests/test_milestone_detection.py
```

**Expected:** Khi user đạt streak 3 days, bot gửi celebration message.

---

## 🎯 PHASE 3: PAYMENT INTEGRATION (Week 1, Days 6-7 + Week 2, Days 1-3)

### Option A: Momo Integration

#### Bước 1: Đăng ký Momo Business

1. Truy cập: https://business.momo.vn/
2. Đăng ký tài khoản doanh nghiệp
3. Lấy:
   - Partner Code
   - Access Key
   - Secret Key

#### Bước 2: Configure

```python
# config.py
MOMO_PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE")
MOMO_ACCESS_KEY = os.getenv("MOMO_ACCESS_KEY")
MOMO_SECRET_KEY = os.getenv("MOMO_SECRET_KEY")
MOMO_IPN_URL = "https://yourdomain.com/webhook/momo"
MOMO_REDIRECT_URL = "https://t.me/FreedomWalletBot"
```

#### Bước 3: Webhook endpoint

```python
# webhook.py
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhook/momo', methods=['POST'])
def momo_webhook():
    data = request.json
    
    # Verify signature
    signature = data.get('signature')
    if not verify_momo_signature(data, signature):
        return {'error': 'Invalid signature'}, 403
    
    # Process payment
    if data['resultCode'] == 0:  # Success
        donation_code = data['orderId']
        db.confirm_donation_by_code(donation_code, data['transId'])
        
        # Send thank you to user
        user_id = db.get_user_by_donation_code(donation_code)
        await send_thank_you(user_id)
    
    return {'success': True}, 200

def verify_momo_signature(data, signature):
    # Implement signature verification
    pass
```

#### Bước 4: Deploy webhook

```bash
# Using ngrok for testing
ngrok http 5000

# Production: Deploy to your server
```

#### Bước 5: Test payment flow

```python
python tests/test_momo_payment.py
```

---

### Option B: Bank Transfer (Simpler, Manual)

#### Bước 1: Setup bank account info

```python
# config.py
BANK_ACCOUNT = {
    "bank_name": "Techcombank",
    "account_number": "19036653824018",
    "account_name": "FREEDOM WALLET"
}
```

#### Bước 2: Manual verification flow

```python
# Admin panel - verify pending donations
async def admin_verify_donation(update, context):
    # Show pending donations
    pending = db.get_pending_donations()
    
    for donation in pending:
        keyboard = [
            [InlineKeyboardButton("✅ Confirm", 
                callback_data=f"admin_confirm:{donation['id']}")],
            [InlineKeyboardButton("❌ Reject", 
                callback_data=f"admin_reject:{donation['id']}")]
        ]
        # Send to admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Donation: {donation['amount']} VNĐ\nCode: {donation['code']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
```

---

## 🎯 PHASE 4: REFERRAL SYSTEM (Week 2, Days 4-7)

### Bước 1: Copy growth handler

```bash
cp growth_handler.py app/handlers/
```

### Bước 2: Update /start command

```python
# bot.py
from handlers.growth_handler import GrowthHandler

growth_handler = GrowthHandler(db)

async def start_command(update, context):
    user_id = update.effective_user.id
    
    # Check if referral
    start_param = context.args[0] if context.args else None
    
    if start_param and start_param.startswith("freedom_"):
        await growth_handler.handle_new_user(update, context, start_param)
    
    # ... existing welcome flow ...
```

### Bước 3: Add /refer command

```python
async def referral_command(update, context):
    await growth_handler.referral.send_referral_link(update, context)

application.add_handler(CommandHandler("refer", referral_command))
```

### Bước 4: Track activation

```python
# When user completes 3 days
def check_user_activated(user_id):
    stats = db.get_user_stats(user_id)
    if stats['days_active'] >= 3:
        growth_handler.referral.mark_referral_activated(user_id)
        
        # Check if referrer gets badge
        referral = db.get_referral_by_referred(user_id)
        if referral:
            await growth_handler.referral.check_referral_milestones(
                update, context, referral['referrer_id']
            )
```

---

## 🎯 PHASE 5: COMMUNITY FEATURES (Week 3)

### Bước 1: Add /community command

```python
async def community_command(update, context):
    await growth_handler.community.send_community_stats(update, context)

application.add_handler(CommandHandler("community", community_command))
```

### Bước 2: Monthly summary (scheduled)

```python
from telegram.ext import JobQueue

def schedule_monthly_summaries(application):
    job_queue = application.job_queue
    
    # Run on 1st of every month at 10 AM
    job_queue.run_monthly(
        send_all_monthly_summaries,
        when=datetime.time(hour=10, minute=0),
        day=1
    )

async def send_all_monthly_summaries(context):
    active_users = db.get_all_active_users()
    for user in active_users:
        try:
            await growth_handler.monthly.send_monthly_summary(
                user['user_id'], context
            )
        except Exception as e:
            logger.error(f"Failed to send summary to {user['user_id']}: {e}")
```

### Bước 3: Create Contributor group

1. Tạo Telegram group: "FreedomWallet Contributors"
2. Lấy invite link
3. Update code:

```python
# config.py
CONTRIBUTORS_GROUP_LINK = "https://t.me/+YOUR_INVITE_LINK"
```

---

## 🎯 PHASE 6: TESTING & POLISH (Week 3)

### Test Cases

```python
# tests/test_donation_flow.py

async def test_milestone_triggers_donation():
    # Simulate user reaching 7 days
    user_id = 12345
    db.update_user_stats(user_id, days_active=7)
    
    # Check milestone
    milestones = milestone_detector.check_milestones(user_id)
    assert len(milestones) > 0
    assert milestones[0]['key'] == 'first_week'

async def test_donation_cooldown():
    user_id = 12345
    
    # First prompt
    assert timing.should_show_donation_prompt(user_id) == True
    
    # Log reminder
    db.log_donation_reminder(user_id, 'test')
    
    # Second prompt (should be blocked)
    assert timing.should_show_donation_prompt(user_id) == False

async def test_referral_tracking():
    referrer_id = 11111
    referred_id = 22222
    code = f"freedom_{referrer_id}"
    
    referral_system.track_referral(referrer_id, referred_id, code)
    
    stats = db.get_referral_stats(referrer_id)
    assert stats['total_referrals'] == 1
```

Run tests:
```bash
pytest tests/
```

---

## 🎯 PHASE 7: DEPLOYMENT

### Bước 1: Environment variables

```bash
# .env
DATABASE_URL=postgresql://user:pass@host:5432/freedomwallet
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id

# Momo (if using)
MOMO_PARTNER_CODE=xxx
MOMO_ACCESS_KEY=xxx
MOMO_SECRET_KEY=xxx

# Bank
BANK_ACCOUNT_NUMBER=xxx
BANK_NAME=Techcombank
BANK_ACCOUNT_NAME=FREEDOM WALLET

# Groups
CONTRIBUTORS_GROUP_LINK=https://t.me/+xxx
```

### Bước 2: Deploy

```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Restart bot
pm2 restart freedomwallet-bot

# Or systemd
sudo systemctl restart freedomwallet-bot
```

### Bước 3: Smoke test

```bash
# Send /start to bot
# Log a transaction
# Check if milestone triggers
# Try donation flow
# Test referral link
```

---

## 📊 MONITORING

### Daily Checks

```python
# scripts/daily_check.py

def daily_health_check():
    stats = {
        'total_users': db.count_total_users(),
        'active_users': db.count_active_users(days=1),
        'donations_today': db.sum_donations(days=1),
        'new_contributors': db.count_new_contributors(days=1),
        'errors_today': db.count_errors(days=1)
    }
    
    print(f"""
    📊 Daily Stats - {datetime.now().date()}
    
    👥 Users: {stats['total_users']} total, {stats['active_users']} active
    💰 Donations: {stats['donations_today']:,} VNĐ
    🌟 New contributors: {stats['new_contributors']}
    ⚠️ Errors: {stats['errors_today']}
    """)
    
    # Send to admin
    send_to_admin(format_report(stats))

# Cron job: Run daily at 9 AM
# 0 9 * * * /usr/bin/python3 /path/to/daily_check.py
```

---

## 🎓 TRAINING YOURSELF

### Understand the psychology

1. Đọc kỹ Section I trong `TRUST_ECONOMY_BLUEPRINT.md`
2. Nắm được 5 nguyên lý tâm lý:
   - Reciprocity
   - Identity Alignment
   - Social Proof
   - Autonomy
   - Progress Milestone

### Test user experience

1. Tạo test user
2. Trải nghiệm full flow:
   - Onboarding
   - Use features 7 days
   - Reach milestone
   - See donation prompt
   - Complete donation
   - Get badge
   - Share referral link

3. Note down:
   - Gì smooth?
   - Gì confusing?
   - Gì cần improve?

### Iterate

1. Collect feedback từ beta users
2. A/B test donation messages
3. Optimize timing
4. Improve conversion

---

## 🔧 TROUBLESHOOTING

### Issue: Milestone không trigger

**Debug:**
```python
# Check user stats
stats = db.get_user_stats(user_id)
print(stats)

# Check milestones reached
milestones = db.get_user_milestones(user_id)
print(milestones)

# Manually trigger
new_milestones = milestone_detector.check_milestones(user_id)
print(new_milestones)
```

### Issue: Payment không confirm

**Debug:**
```python
# Check pending donations
pending = db.get_pending_donations()
print(pending)

# Check webhook logs
tail -f logs/webhook.log

# Manually confirm (admin)
db.confirm_donation(donation_id, transaction_id="MANUAL")
```

### Issue: Referral không track

**Debug:**
```python
# Check deep link
print(context.args)  # Should have freedom_12345

# Check referral table
referrals = db.get_all_referrals(referrer_id)
print(referrals)
```

---

## 📚 NEXT STEPS AFTER LAUNCH

### Week 1-4: Stability
- Monitor errors
- Fix bugs
- Optimize performance
- Collect feedback

### Month 2: Optimization
- A/B test donation messages
- Improve conversion rate
- Add more milestones
- Polish UX

### Month 3: Growth
- Ambassador program
- Content marketing
- Community events
- Feature expansion

---

## 💡 PRO TIPS

1. **Start small**: Launch với basic flow, improve dần
2. **Monitor closely**: First month quan trọng nhất
3. **Listen to users**: Họ biết gì works, gì không
4. **Be transparent**: Luôn honest về tài chính
5. **Celebrate wins**: Share success stories
6. **Stay authentic**: Không fake social proof
7. **Trust the process**: Donation model cần thời gian build trust

---

## ✅ FINAL CHECKLIST BEFORE LAUNCH

- [ ] Database tables created
- [ ] Milestone system working
- [ ] Donation flow tested end-to-end
- [ ] Payment working (Momo or Bank)
- [ ] Referral tracking working
- [ ] All callbacks registered
- [ ] Error handling robust
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Documentation complete
- [ ] Beta tested with 10+ users
- [ ] Privacy policy published
- [ ] Contributors group created
- [ ] Launch announcement ready

---

## 🎉 YOU'RE READY TO LAUNCH!

**Remember:**
> Trust Economy không phải về tiền.  
> Nó về xây dựng cộng đồng tin tưởng nhau.  
> Nếu bạn give value first, trust sẽ theo.  
> Nếu trust đủ mạnh, donations sẽ đến.

**Chúc bạn thành công! 💚🚀**

---

## 📞 SUPPORT

Nếu cần support khi implement:

1. Review code examples trong `donation_handler.py` và `growth_handler.py`
2. Check `TRUST_ECONOMY_BLUEPRINT.md` cho strategy details
3. Refer to `PRODUCTION_CHECKLIST.md` cho deployment
4. Test thoroughly before going live

**Good luck building the Financial Freedom community! 💪**
