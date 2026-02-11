# 🚀 FREEDOM WALLET BOT - MVP 4-WEEK IMPLEMENTATION PLAN

**Target Launch**: Week 4 End (March 8, 2026)  
**Strategy**: Monetization-first MVP with viral mechanics  
**Tech Stack**: Pure Python (No VBA)

---

## 📊 SPRINT OVERVIEW

```
Week 1-2: FOUNDATION
├─ FREE/PREMIUM tier system
├─ Fraud detection (3 layers)
└─ Database migrations

Week 3-4: VIRAL MECHANICS
├─ Referral leaderboard
├─ Super VIP lite (Top 20)
└─ Launch campaign
```

---

## 🎯 WEEK 1: MONETIZATION FOUNDATION

### **Goal**: Tách FREE/PREMIUM, có thể bán ngay tuần 2

### Day 1-2: Database Schema

**Files to create/modify:**

1. **migrations/add_premium_tier.py**
```python
# Add to User table:
subscription_tier: Enum['FREE', 'PREMIUM', 'TRIAL']  # Changed from subscription_tier text
premium_started_at: DateTime
premium_expires_at: DateTime
trial_ends_at: DateTime
premium_features_used: JSON  # Track usage for upsell
bot_chat_count: Integer DEFAULT 0  # Daily counter
bot_chat_limit_date: Date  # Reset daily
```

2. **migrations/add_fraud_tracking.py**
```python
# Add to User table:
ip_address: String
device_fingerprint: String  # Telegram user_agent + language
last_referral_at: DateTime
referral_velocity: Integer  # refs in last 24h

# New table: fraud_events
- user_id
- event_type: Enum['velocity', 'duplicate_device', 'suspicious_timing']
- severity: Integer (1-100)
- details: JSON
- created_at
```

**Commands:**
```powershell
cd D:\Projects\FreedomWalletBot
python migrations/add_premium_tier.py
python migrations/add_fraud_tracking.py
```

**Verify:**
```python
python -c "from bot.utils.database import User, SessionLocal; db = SessionLocal(); u = db.query(User).first(); print([c.name for c in u.__table__.columns])"
```

---

### Day 3-4: Tier System Core

**Files to create:**

**bot/core/subscription.py** (NEW - 250 lines)
```python
from enum import Enum
from datetime import datetime, timedelta
from bot.utils.database import User, SessionLocal

class SubscriptionTier(Enum):
    FREE = "free"
    TRIAL = "trial"
    PREMIUM = "premium"

class SubscriptionManager:
    """Manage user subscription tiers and limits"""
    
    # FREE tier limits
    FREE_LIMITS = {
        'bot_chat_daily': 5,
        'ai_analysis': False,
        'real_time_balance': False,
        'smart_reminders': False,
        'budget_alerts': False,
        'add_transaction_via_bot': False,
        'reports_via_bot': False
    }
    
    # PREMIUM features (unlimited)
    PREMIUM_FEATURES = {
        'bot_chat_daily': 999999,
        'ai_analysis': True,
        'real_time_balance': True,
        'smart_reminders': True,
        'budget_alerts': True,
        'add_transaction_via_bot': True,
        'reports_via_bot': True,
        'priority_support': True,
        'managed_setup': True,
        'auto_backup': True
    }
    
    @staticmethod
    def get_user_tier(user: User) -> SubscriptionTier:
        """Get current active tier (handles trial expiry)"""
        if user.subscription_tier == 'PREMIUM':
            if user.premium_expires_at and user.premium_expires_at > datetime.utcnow():
                return SubscriptionTier.PREMIUM
            # Expired premium → downgrade to FREE
            return SubscriptionTier.FREE
        
        if user.subscription_tier == 'TRIAL':
            if user.trial_ends_at and user.trial_ends_at > datetime.utcnow():
                return SubscriptionTier.TRIAL
            # Expired trial → FREE
            return SubscriptionTier.FREE
        
        return SubscriptionTier.FREE
    
    @staticmethod
    def can_use_feature(user: User, feature: str) -> tuple[bool, str]:
        """Check if user can use feature. Returns (allowed, message)"""
        tier = SubscriptionManager.get_user_tier(user)
        
        if tier == SubscriptionTier.PREMIUM or tier == SubscriptionTier.TRIAL:
            return True, ""
        
        # FREE user checks
        if feature == 'bot_chat':
            # Reset daily counter
            today = datetime.utcnow().date()
            if user.bot_chat_limit_date != today:
                user.bot_chat_count = 0
                user.bot_chat_limit_date = today
            
            if user.bot_chat_count < SubscriptionManager.FREE_LIMITS['bot_chat_daily']:
                user.bot_chat_count += 1
                remaining = SubscriptionManager.FREE_LIMITS['bot_chat_daily'] - user.bot_chat_count
                return True, f"✅ Còn {remaining}/5 tin nhắn hôm nay (FREE tier)"
            else:
                return False, (
                    "⚠️ Bạn đã hết 5 tin nhắn miễn phí hôm nay.\n\n"
                    "💎 Nâng cấp PREMIUM (999k/năm) để chat không giới hạn:\n"
                    "• Chat unlimited với bot\n"
                    "• Xem số dư real-time\n"
                    "• Thêm giao dịch qua chat\n"
                    "• AI phân tích chi tiêu\n"
                    "• Báo cáo tức thì\n\n"
                    "👉 /upgrade để nâng cấp"
                )
        
        # Other features blocked for FREE
        if feature in ['ai_analysis', 'real_time_balance', 'add_transaction', 'reports']:
            return False, (
                "🔒 Tính năng Premium\n\n"
                f"'{feature}' chỉ dành cho Premium users.\n"
                "Nâng cấp ngay với 999k/năm → /upgrade"
            )
        
        return True, ""
    
    @staticmethod
    def start_trial(user: User, days: int = 7):
        """Start FREE trial for new users"""
        user.subscription_tier = 'TRIAL'
        user.trial_ends_at = datetime.utcnow() + timedelta(days=days)
        user.premium_started_at = datetime.utcnow()
        
        return {
            'success': True,
            'message': f"🎉 Kích hoạt thử nghiệm PREMIUM {days} ngày!\n\nBạn có full quyền truy cập đến {user.trial_ends_at.strftime('%d/%m/%Y')}"
        }
    
    @staticmethod
    def upgrade_to_premium(user: User, duration_days: int = 365):
        """Upgrade user to PREMIUM"""
        user.subscription_tier = 'PREMIUM'
        user.premium_started_at = datetime.utcnow()
        user.premium_expires_at = datetime.utcnow() + timedelta(days=duration_days)
        
        return {
            'success': True,
            'message': f"💎 Chào mừng đến PREMIUM!\n\nGói của bạn có hiệu lực đến {user.premium_expires_at.strftime('%d/%m/%Y')}"
        }
    
    @staticmethod
    def get_tier_status_message(user: User) -> str:
        """Get formatted tier status for user"""
        tier = SubscriptionManager.get_user_tier(user)
        
        if tier == SubscriptionTier.PREMIUM:
            days_left = (user.premium_expires_at - datetime.utcnow()).days
            return f"💎 Premium ({days_left} ngày còn lại)"
        
        if tier == SubscriptionTier.TRIAL:
            days_left = (user.trial_ends_at - datetime.utcnow()).days
            return f"🎁 Trial Premium ({days_left} ngày còn lại)"
        
        return "🆓 FREE (5 tin nhắn/ngày)"
```

**Test command:**
```python
# Test tier check
python -c "
from bot.core.subscription import SubscriptionManager, SubscriptionTier
from bot.utils.database import SessionLocal, User
db = SessionLocal()
user = db.query(User).first()
tier = SubscriptionManager.get_user_tier(user)
print(f'User tier: {tier}')
allowed, msg = SubscriptionManager.can_use_feature(user, 'bot_chat')
print(f'Can chat: {allowed}, Message: {msg}')
"
```

---

### Day 5-7: Tier Integration + Commands

**Files to modify:**

**bot/handlers/user_commands.py** (EXTEND)

Add 3 new commands:

```python
async def upgrade_command(update, context):
    """Show upgrade pricing + payment link"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    tier = SubscriptionManager.get_user_tier(user)
    status = SubscriptionManager.get_tier_status_message(user)
    
    message = f"""
💎 NÂNG CẤP PREMIUM

📊 Trạng thái hiện tại: {status}

🆓 FREE → 💎 PREMIUM
Giá: 999,000 VNĐ/năm (~83k/tháng)

🌟 Bạn nhận được:
✅ Chat không giới hạn với bot
✅ Xem số dư real-time bất cứ lúc nào
✅ Thêm giao dịch qua chat: "Chi 50k ăn sáng"
✅ AI phân tích chi tiêu & tư vấn
✅ Báo cáo tức thì
✅ Nhắc nhở thông minh hàng ngày
✅ Cảnh báo vượt budget
✅ Priority support (<1h response)
✅ Setup service (5 phút)

💳 Thanh toán:
• Chuyển khoản: MB Bank - 0123456789 - LE VAN A
• Nội dung: PREMIUM_{user_id}

Sau khi chuyển khoản, gửi ảnh bill cho @Admin để kích hoạt ngay!

🎁 Hoặc thử TRIAL 7 ngày miễn phí → /trial
"""
    
    await update.message.reply_text(message)

async def trial_command(update, context):
    """Start 7-day FREE trial (once per user)"""
    user_id = update.effective_user.id
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    # Check if already used trial
    if user.trial_ends_at or user.premium_started_at:
        await update.message.reply_text(
            "⚠️ Bạn đã sử dụng trial rồi!\n\n"
            "Để tiếp tục dùng Premium → /upgrade"
        )
        return
    
    # Start trial
    result = SubscriptionManager.start_trial(user)
    db.commit()
    
    await update.message.reply_text(result['message'])

async def mystatus_command(update, context):
    """Show detailed subscription status"""
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    tier = SubscriptionManager.get_user_tier(user)
    status_line = SubscriptionManager.get_tier_status_message(user)
    
    if tier == SubscriptionTier.FREE:
        chat_used = user.bot_chat_count or 0
        chat_limit = SubscriptionManager.FREE_LIMITS['bot_chat_daily']
        
        message = f"""
📊 TRẠNG THÁI TÀI KHOẢN

Gói: {status_line}
Chat hôm nay: {chat_used}/{chat_limit} tin nhắn

🔒 Tính năng Premium (chưa có):
❌ Chat không giới hạn
❌ Xem số dư real-time
❌ Thêm giao dịch qua bot
❌ AI phân tích
❌ Báo cáo tức thì
❌ Priority support

💡 Nâng cấp ngay → /upgrade
🎁 Hoặc dùng thử 7 ngày → /trial
"""
    else:
        message = f"""
📊 TRẠNG THÁI TÀI KHOẢN

Gói: {status_line}

✅ Tính năng đang dùng:
✅ Chat không giới hạn
✅ Xem số dư real-time
✅ Thêm giao dịch qua bot
✅ AI phân tích
✅ Báo cáo tức thì
✅ Priority support

💎 Bạn đang tận hưởng Premium!
"""
    
    await update.message.reply_text(message)

# Register commands
app.add_handler(CommandHandler("upgrade", upgrade_command))
app.add_handler(CommandHandler("trial", trial_command))
app.add_handler(CommandHandler("mystatus", mystatus_command))
```

**Wrap all bot interactions:**

**bot/handlers/ai_assistant_handler.py** (MODIFY)
```python
async def handle_ai_query(update, context):
    user = get_user(update.effective_user.id)
    
    # Check tier access
    allowed, message = SubscriptionManager.can_use_feature(user, 'bot_chat')
    if not allowed:
        await update.message.reply_text(message)
        return
    
    # Existing AI handler logic...
```

**Repeat for:**
- `/balance` command → check 'real_time_balance'
- `/record` command → check 'add_transaction'
- `/report` command → check 'reports'

---

## 🛡️ WEEK 2: FRAUD DETECTION

### **Goal**: Prevent referral abuse trước khi mở leaderboard

### Day 8-10: Fraud Detection Core

**Files to create:**

**bot/core/fraud_detection.py** (NEW - 300 lines)

```python
from datetime import datetime, timedelta
from sqlalchemy import func
from bot.utils.database import User, SessionLocal
from loguru import logger

class FraudDetector:
    """3-layer fraud detection for referrals"""
    
    # Thresholds
    VELOCITY_THRESHOLD = {
        'suspicious': 5,   # refs in 1 hour
        'critical': 10,    # refs in 1 hour
        'daily_max': 30    # refs in 24 hours
    }
    
    DEVICE_THRESHOLD = {
        'max_accounts_per_device': 3  # same fingerprint
    }
    
    TIME_PATTERN_THRESHOLD = {
        'min_seconds_between': 60,     # minimum 1 minute between refs
        'same_minute_max': 2           # max refs in same minute
    }
    
    @staticmethod
    def check_referral_fraud(
        referrer_id: int,
        new_user_id: int,
        device_fingerprint: str,
        ip_address: str
    ) -> dict:
        """
        Multi-layer fraud check. Returns:
        {
            'allowed': bool,
            'severity': int (0-100),
            'reasons': list[str],
            'action': 'allow' | 'review' | 'block'
        }
        """
        db = SessionLocal()
        reasons = []
        severity = 0
        
        # Layer 1: Velocity Check
        velocity_score, velocity_reasons = FraudDetector._check_velocity(db, referrer_id)
        severity += velocity_score
        reasons.extend(velocity_reasons)
        
        # Layer 2: Device Fingerprint
        device_score, device_reasons = FraudDetector._check_device(db, device_fingerprint)
        severity += device_score
        reasons.extend(device_reasons)
        
        # Layer 3: Time Pattern
        time_score, time_reasons = FraudDetector._check_time_pattern(db, referrer_id)
        severity += time_score
        reasons.extend(time_reasons)
        
        # Determine action
        if severity >= 70:
            action = 'block'
        elif severity >= 40:
            action = 'review'
        else:
            action = 'allow'
        
        result = {
            'allowed': action == 'allow',
            'severity': severity,
            'reasons': reasons,
            'action': action
        }
        
        # Log fraud event
        if severity > 0:
            FraudDetector._log_fraud_event(
                db, referrer_id, new_user_id, 
                action, severity, reasons
            )
        
        db.close()
        return result
    
    @staticmethod
    def _check_velocity(db, referrer_id: int) -> tuple[int, list]:
        """Check referral velocity (refs/hour, refs/day)"""
        reasons = []
        score = 0
        
        referrer = db.query(User).filter(User.id == referrer_id).first()
        if not referrer:
            return 0, []
        
        now = datetime.utcnow()
        
        # Check last hour
        hour_ago = now - timedelta(hours=1)
        refs_last_hour = db.query(func.count(User.id)).filter(
            User.referred_by == referrer_id,
            User.created_at >= hour_ago
        ).scalar()
        
        if refs_last_hour >= FraudDetector.VELOCITY_THRESHOLD['critical']:
            score += 50
            reasons.append(f"⛔ Critical velocity: {refs_last_hour} refs in 1 hour")
        elif refs_last_hour >= FraudDetector.VELOCITY_THRESHOLD['suspicious']:
            score += 25
            reasons.append(f"⚠️ High velocity: {refs_last_hour} refs in 1 hour")
        
        # Check last 24 hours
        day_ago = now - timedelta(days=1)
        refs_last_day = db.query(func.count(User.id)).filter(
            User.referred_by == referrer_id,
            User.created_at >= day_ago
        ).scalar()
        
        if refs_last_day >= FraudDetector.VELOCITY_THRESHOLD['daily_max']:
            score += 30
            reasons.append(f"⚠️ Daily limit exceeded: {refs_last_day} refs in 24h")
        
        # Update user's velocity tracking
        referrer.referral_velocity = refs_last_hour
        referrer.last_referral_at = now
        db.commit()
        
        return score, reasons
    
    @staticmethod
    def _check_device(db, device_fingerprint: str) -> tuple[int, list]:
        """Check if device is reused across multiple accounts"""
        reasons = []
        score = 0
        
        if not device_fingerprint:
            return 0, []
        
        accounts_count = db.query(func.count(User.id)).filter(
            User.device_fingerprint == device_fingerprint
        ).scalar()
        
        max_allowed = FraudDetector.DEVICE_THRESHOLD['max_accounts_per_device']
        
        if accounts_count >= max_allowed:
            score += 40
            reasons.append(f"⚠️ Device reused: {accounts_count} accounts on same device")
        
        return score, reasons
    
    @staticmethod
    def _check_time_pattern(db, referrer_id: int) -> tuple[int, list]:
        """Check for suspicious timing patterns"""
        reasons = []
        score = 0
        
        # Get last 10 referrals
        recent_refs = db.query(User.created_at).filter(
            User.referred_by == referrer_id
        ).order_by(User.created_at.desc()).limit(10).all()
        
        if len(recent_refs) < 2:
            return 0, []
        
        # Check gaps between referrals
        timestamps = [r.created_at for r in recent_refs]
        
        suspicious_gaps = 0
        same_minute_count = 0
        
        for i in range(len(timestamps) - 1):
            gap_seconds = (timestamps[i] - timestamps[i+1]).total_seconds()
            
            # Too fast
            if gap_seconds < FraudDetector.TIME_PATTERN_THRESHOLD['min_seconds_between']:
                suspicious_gaps += 1
            
            # Same minute
            if timestamps[i].minute == timestamps[i+1].minute:
                same_minute_count += 1
        
        if suspicious_gaps >= 3:
            score += 20
            reasons.append(f"⚠️ Suspicious timing: {suspicious_gaps} refs < 1 min apart")
        
        if same_minute_count >= FraudDetector.TIME_PATTERN_THRESHOLD['same_minute_max']:
            score += 15
            reasons.append(f"⚠️ Time clustering: {same_minute_count} refs in same minute")
        
        return score, reasons
    
    @staticmethod
    def _log_fraud_event(db, referrer_id, new_user_id, action, severity, reasons):
        """Log fraud event to database for admin review"""
        from bot.utils.database import FraudEvent
        
        event = FraudEvent(
            user_id=referrer_id,
            related_user_id=new_user_id,
            event_type='referral_fraud',
            action=action,
            severity=severity,
            details={
                'reasons': reasons,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        db.add(event)
        db.commit()
        
        # Alert admin if critical
        if severity >= 70:
            logger.critical(
                f"🚨 FRAUD ALERT: User {referrer_id} blocked! "
                f"Severity: {severity}, Reasons: {reasons}"
            )
    
    @staticmethod
    def get_user_fraud_score(user_id: int) -> int:
        """Get cumulative fraud score for user"""
        db = SessionLocal()
        from bot.utils.database import FraudEvent
        
        total_score = db.query(func.sum(FraudEvent.severity)).filter(
            FraudEvent.user_id == user_id,
            FraudEvent.created_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
        
        db.close()
        return total_score
```

**Database migration:**

**migrations/add_fraud_events.py**
```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Enum
from bot.utils.database import Base, engine

class FraudEvent(Base):
    __tablename__ = 'fraud_events'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    related_user_id = Column(Integer, nullable=True)
    event_type = Column(String, nullable=False)  # 'referral_fraud', 'bot_abuse', etc
    action = Column(Enum('allow', 'review', 'block', name='fraud_action'), nullable=False)
    severity = Column(Integer, nullable=False)  # 0-100
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create table
Base.metadata.create_all(bind=engine, tables=[FraudEvent.__table__])
print("✅ fraud_events table created")
```

---

### Day 11-14: Fraud Integration

**Modify referral handler:**

**bot/handlers/start.py** (MODIFY start command)

```python
from bot.core.fraud_detection import FraudDetector

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    
    # Extract referral code
    referrer_id = None
    if context.args and context.args[0].startswith('ref'):
        try:
            referrer_id = int(context.args[0].replace('ref', ''))
        except:
            pass
    
    # Get or create user
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    # Get device fingerprint
    device_fingerprint = f"{update.effective_user.language_code}_{update.effective_chat.type}"
    ip_address = "telegram_cloud"  # Telegram doesn't expose IP
    
    if not user:
        # NEW USER - check fraud if has referrer
        if referrer_id:
            fraud_result = FraudDetector.check_referral_fraud(
                referrer_id=referrer_id,
                new_user_id=user_id,
                device_fingerprint=device_fingerprint,
                ip_address=ip_address
            )
            
            if fraud_result['action'] == 'block':
                await update.message.reply_text(
                    "⚠️ Không thể xử lý giới thiệu này.\n"
                    "Vui lòng đăng ký trực tiếp hoặc liên hệ @Support"
                )
                logger.warning(f"Blocked fraudulent referral: {fraud_result}")
                referrer_id = None  # Don't count this ref
            
            elif fraud_result['action'] == 'review':
                # Allow but flag for admin review
                logger.warning(f"Flagged referral for review: {fraud_result}")
        
        # Create user
        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            referred_by=referrer_id,
            device_fingerprint=device_fingerprint,
            subscription_tier='FREE',
            bot_chat_count=0
        )
        db.add(user)
        
        # Update referrer count
        if referrer_id:
            referrer = db.query(User).filter(User.id == referrer_id).first()
            if referrer:
                referrer.referral_count += 1
        
        db.commit()
    
    # Send welcome message
    tier_status = SubscriptionManager.get_tier_status_message(user)
    
    welcome_msg = f"""
🎉 Chào mừng {first_name} đến Freedom Wallet Bot!

📊 Trạng thái: {tier_status}

💡 Bạn có thể:
{"✅ Chat với bot (5 tin/ngày)" if user.subscription_tier == 'FREE' else "✅ Chat unlimited"}
✅ Xem hướng dẫn → /guide
✅ Theo dõi streak → /stats
{"✅ Giới thiệu bạn bè → /referral" if user.subscription_tier != 'FREE' else "🔒 Giới thiệu (Premium only)"}

💎 Muốn unlock full features? → /upgrade
🎁 Hoặc dùng thử 7 ngày FREE → /trial
"""
    
    await update.message.reply_text(welcome_msg)
    db.close()
```

**Admin fraud review command:**

```python
async def admin_fraud_review(update, context):
    """Admin only: Review flagged referrals"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    db = SessionLocal()
    from bot.utils.database import FraudEvent
    
    # Get 'review' cases
    flagged = db.query(FraudEvent).filter(
        FraudEvent.action == 'review',
        FraudEvent.created_at >= datetime.utcnow() - timedelta(days=7)
    ).order_by(FraudEvent.severity.desc()).limit(20).all()
    
    if not flagged:
        await update.message.reply_text("✅ No fraud cases to review")
        return
    
    messages = ["🔍 FRAUD REVIEW QUEUE\n"]
    
    for event in flagged:
        user = db.query(User).filter(User.id == event.user_id).first()
        messages.append(
            f"\n⚠️ User: @{user.username} ({user.id})\n"
            f"Severity: {event.severity}/100\n"
            f"Reasons: {', '.join(event.details.get('reasons', []))}\n"
            f"Time: {event.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Action: /approve_{event.id} | /block_{event.id}"
        )
    
    await update.message.reply_text('\n'.join(messages))
    db.close()
```

---

## 🏆 WEEK 3: VIRAL MECHANICS

### **Goal**: Referral leaderboard + Super VIP lite (Top 20)

### Day 15-17: Leaderboard System

**Files to create:**

**bot/services/leaderboard.py** (NEW - 200 lines)

```python
from bot.utils.database import User, SessionLocal
from datetime import datetime, timedelta

class LeaderboardService:
    """Manage referral leaderboards"""
    
    @staticmethod
    def get_top_referrers(limit: int = 20, period: str = 'all_time') -> list:
        """Get top referrers
        
        Args:
            limit: Number of users to return
            period: 'all_time', 'month', 'week'
        
        Returns:
            List of (user, referral_count, rank)
        """
        db = SessionLocal()
        
        query = db.query(User).filter(User.referral_count > 0)
        
        # Filter by period
        if period == 'month':
            month_ago = datetime.utcnow() - timedelta(days=30)
            # Count only refs created in last month
            # This needs subquery - simplified for MVP
            pass
        elif period == 'week':
            week_ago = datetime.utcnow() - timedelta(days=7)
            pass
        
        # Order by total ref count
        leaderboard = query.order_by(User.referral_count.desc()).limit(limit).all()
        
        # Add rank
        ranked = []
        for idx, user in enumerate(leaderboard, start=1):
            ranked.append({
                'rank': idx,
                'user': user,
                'ref_count': user.referral_count,
                'is_super_vip': idx <= 20  # Top 20 = Super VIP candidates
            })
        
        db.close()
        return ranked
    
    @staticmethod
    def get_user_rank(user_id: int) -> dict:
        """Get user's position in leaderboard"""
        db = SessionLocal()
        
        # Count users with more refs
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {'rank': None, 'ref_count': 0}
        
        higher_ranked = db.query(User).filter(
            User.referral_count > user.referral_count
        ).count()
        
        rank = higher_ranked + 1
        
        db.close()
        return {
            'rank': rank,
            'ref_count': user.referral_count,
            'is_top_20': rank <= 20
        }
    
    @staticmethod
    def format_leaderboard_message(leaderboard: list, viewer_id: int = None) -> str:
        """Format leaderboard for Telegram message"""
        
        message_lines = [
            "🏆 BẢNG XẾP HẠNG GIỚI THIỆU\n",
            "Top 20 = 🌟 Super VIP Candidate\n"
        ]
        
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        
        for entry in leaderboard:
            rank = entry['rank']
            user = entry['user']
            count = entry['ref_count']
            
            medal = medals.get(rank, f"{rank}.")
            star = "🌟" if rank <= 20 else ""
            highlight = "**" if user.id == viewer_id else ""
            
            name = user.first_name or user.username or f"User{user.id}"
            
            message_lines.append(
                f"{highlight}{medal} {name} - {count} refs {star}{highlight}"
            )
        
        # Add viewer's position if not in top 20
        if viewer_id:
            viewer_rank = LeaderboardService.get_user_rank(viewer_id)
            if viewer_rank['rank'] and viewer_rank['rank'] > 20:
                message_lines.append(
                    f"\n━━━━━━━━━━━━━━━━\n"
                    f"**{viewer_rank['rank']}. Bạn - {viewer_rank['ref_count']} refs**\n"
                    f"Cần thêm {leaderboard[-1]['ref_count'] - viewer_rank['ref_count'] + 1} refs để vào Top 20! 💪"
                )
        
        message_lines.append(
            "\n👉 Chia sẻ link của bạn: /referral"
        )
        
        return '\n'.join(message_lines)
```

**Command handler:**

```python
async def leaderboard_command(update, context):
    """Show referral leaderboard"""
    user_id = update.effective_user.id
    
    # Get tier (Premium feature in future)
    # For MVP: available to all
    
    leaderboard = LeaderboardService.get_top_referrers(limit=20)
    message = LeaderboardService.format_leaderboard_message(leaderboard, viewer_id=user_id)
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )

async def referral_command(update, context):
    """Show user's referral stats + link"""
    user_id = update.effective_user.id
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    
    # Generate referral link
    bot_username = context.bot.username
    ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
    
    # Get rank
    rank_info = LeaderboardService.get_user_rank(user_id)
    
    message = f"""
🎁 GIỚI THIỆU BẠN BÈ

📊 Thống kê của bạn:
• Đã giới thiệu: {user.referral_count} người
• Xếp hạng: #{rank_info['rank']}
{'🌟 Bạn ở Top 20! Super VIP Candidate!' if rank_info['is_top_20'] else ''}

🔗 Link giới thiệu của bạn:
{ref_link}

💎 Phần thưởng:
• 2 refs → Unlock FREE tier vĩnh viễn
• 5 refs → Badge "🔥 Influencer"
• 10 refs → Badge "💎 Diamond"
• Top 20 → 🌟 Super VIP (Spotlight mỗi tuần)

👉 Xem BXH đầy đủ: /leaderboard
"""
    
    await update.message.reply_text(message)
    db.close()
```

---

### Day 18-21: Super VIP System (Lite)

**Files to create:**

**bot/services/super_vip.py** (NEW - 150 lines)

```python
from bot.utils.database import User, SessionLocal
from bot.services.leaderboard import LeaderboardService
from datetime import datetime, timedelta

class SuperVIPManager:
    """Manage Super VIP status and perks (Lite version for MVP)"""
    
    TOP_N = 20  # Top 20 = Super VIP
    DECAY_DAYS = 14  # Lose status after 14 days inactive
    
    @staticmethod
    def update_super_vip_statuses():
        """Daily job: Update Super VIP status based on leaderboard"""
        db = SessionLocal()
        
        # Get current top 20
        top_20 = LeaderboardService.get_top_referrers(limit=SuperVIPManager.TOP_N)
        top_20_ids = [entry['user']['id'] for entry in top_20]
        
        # Grant Super VIP to top 20
        granted = db.query(User).filter(
            User.id.in_(top_20_ids),
            User.subscription_tier != 'SUPER_VIP'
        ).update({'subscription_tier': 'SUPER_VIP'}, synchronize_session=False)
        
        # Revoke from others
        revoked = db.query(User).filter(
            User.subscription_tier == 'SUPER_VIP',
            User.id.not_in(top_20_ids)
        ).update({'subscription_tier': 'VIP'}, synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Super VIP update: {granted} granted, {revoked} revoked")
        
        db.close()
        return granted, revoked
    
    @staticmethod
    def check_decay():
        """Check for inactive Super VIPs (14+ days no login)"""
        db = SessionLocal()
        
        threshold = datetime.utcnow() - timedelta(days=SuperVIPManager.DECAY_DAYS)
        
        # Find inactive Super VIPs
        inactive = db.query(User).filter(
            User.subscription_tier == 'SUPER_VIP',
            User.last_active < threshold
        ).all()
        
        warned_users = []
        
        for user in inactive:
            # Warn if not warned yet
            if not user.super_vip_decay_warned:
                warned_users.append(user)
                user.super_vip_decay_warned = True
        
        db.commit()
        db.close()
        
        return warned_users
    
    @staticmethod
    async def send_spotlight_message(context, user_id: int):
        """Send weekly spotlight message to Super VIP"""
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.subscription_tier != 'SUPER_VIP':
            return
        
        rank_info = LeaderboardService.get_user_rank(user_id)
        
        message = f"""
🌟 SUPER VIP SPOTLIGHT 🌟

Chúc mừng {user.first_name}!
Bạn đang Top {rank_info['rank']} với {rank_info['ref_count']} giới thiệu!

💎 Đặc quyền Super VIP:
✅ Tên xuất hiện ở Leaderboard hàng đầu
✅ Badge 🌟 trong bot
✅ Priority support 24/7
✅ Early access cho tính năng mới
✅ Shoutout hàng tuần trong group

⚠️ Lưu ý: Cần active ít nhất 1 lần/14 ngày để giữ Super VIP!

Tiếp tục tạo impact! 🚀
"""
        
        await context.bot.send_message(
            chat_id=user_id,
            text=message
        )
        
        db.close()
```

**Daily jobs:**

**bot/jobs/daily_tasks.py** (ADD to existing scheduler)

```python
from bot.services.super_vip import SuperVIPManager

async def update_super_vip_job(context):
    """Run daily at 10 AM"""
    SuperVIPManager.update_super_vip_statuses()

async def check_super_vip_decay_job(context):
    """Run daily at 9 AM - warn inactive users"""
    warned_users = SuperVIPManager.check_decay()
    
    for user in warned_users:
        message = (
            "⚠️ CẢNH BÁO SUPER VIP\n\n"
            f"Bạn đã không hoạt động {SuperVIPManager.DECAY_DAYS} ngày!\n"
            "Nếu không login trong 3 ngày nữa, bạn sẽ mất Super VIP status.\n\n"
            "👉 Login ngay để giữ vị trí!"
        )
        await context.bot.send_message(chat_id=user.id, text=message)

# Register jobs
job_queue.run_daily(
    update_super_vip_job,
    time=datetime.time(hour=10, minute=0)
)
job_queue.run_daily(
    check_super_vip_decay_job,
    time=datetime.time(hour=9, minute=0)
)
```

---

## 🚀 WEEK 4: POLISH & LAUNCH

### **Goal**: Testing + Launch campaign

### Day 22-24: Testing & Fixes

**Test cases:**

1. **Tier System**
```python
# test_tiers.py
def test_free_chat_limit():
    # Simulate 6 messages in 1 day
    # Expected: first 5 succeed, 6th blocked
    pass

def test_trial_activation():
    # New user starts trial
    # Expected: 7 days premium, can use all features
    pass

def test_premium_expiry():
    # Premium expires
    # Expected: downgrade to FREE, limits apply
    pass
```

2. **Fraud Detection**
```python
# test_fraud.py
def test_velocity_block():
    # Simulate 11 refs in 1 hour
    # Expected: 11th blocked
    pass

def test_device_fingerprint():
    # 4 accounts same device
    # Expected: 4th flagged for review
    pass
```

3. **Leaderboard**
```python
# test_leaderboard.py
def test_top_20_calculation():
    # Create 30 users with refs
    # Expected: Top 20 get Super VIP
    pass

def test_rank_update():
    # User gets new ref, moves to #19
    # Expected: Gets Super VIP status
    pass
```

**Run tests:**
```powershell
cd D:\Projects\FreedomWalletBot
python -m pytest tests/ -v
```

---

### Day 25-28: Launch Campaign

**Pre-launch checklist:**

- [ ] Database migrations completed
- [ ] All commands working (/upgrade, /trial, /referral, /leaderboard)
- [ ] Fraud detection tested
- [ ] Payment instructions clear
- [ ] Admin fraud review working
- [ ] Super VIP jobs scheduled
- [ ] Bot deployed to production server

**Launch sequence:**

1. **Day 25**: Soft launch to 50 beta testers
   - Offer FREE trial extended (14 days)
   - Collect feedback
   
2. **Day 26**: Social media announcement
   - Post on Facebook groups
   - Create referral contest
   
3. **Day 27**: Content marketing
   - Tutorial videos
   - Success stories
   
4. **Day 28**: Full launch
   - Press release
   - Paid ads (if budget)

---

## 📊 SUCCESS METRICS (4-Week Goals)

```
Users:
✅ 100 total signups
✅ 50 active users (7-day retention)
✅ 20 users with 2+ refs (viral loop working)

Revenue:
✅ 10 Premium conversions = 9,990,000 VNĐ (~$400 USD)
✅ 5 trial → paid conversions

Engagement:
✅ 200+ total referrals
✅ Top 20 leaderboard filled
✅ 5+ Super VIP candidates active

Technical:
✅ <5% fraud rate
✅ 99% uptime
✅ <2s response time for bot commands
```

---

## 🛠️ TECH STACK SUMMARY

**Backend:**
- Python 3.11
- python-telegram-bot 20.7
- SQLAlchemy + SQLite (migrate to PostgreSQL at 1000+ users)
- APScheduler

**Features:**
- ✅ Tier system (FREE/TRIAL/PREMIUM)
- ✅ Fraud detection (3 layers)
- ✅ Referral leaderboard
- ✅ Super VIP (Top 20)
- ✅ Daily reminders + streak (already built)
- ✅ Milestones + images (already built)

**No VBA needed!** Pure Python.

---

## 📝 FILES TO CREATE/MODIFY SUMMARY

### Week 1-2:
```
NEW:
├── migrations/add_premium_tier.py
├── migrations/add_fraud_tracking.py
├── bot/core/subscription.py
└── bot/core/fraud_detection.py

MODIFY:
├── bot/utils/database.py (add FraudEvent model)
├── bot/handlers/user_commands.py (add /upgrade, /trial, /mystatus)
└── bot/handlers/ai_assistant_handler.py (add tier checks)
```

### Week 3-4:
```
NEW:
├── bot/services/leaderboard.py
├── bot/services/super_vip.py
└── tests/test_leaderboard.py

MODIFY:
├── bot/handlers/start.py (fraud check on referral)
├── bot/handlers/user_commands.py (add /referral, /leaderboard)
└── bot/jobs/daily_tasks.py (add Super VIP jobs)
```

**Total: ~12 files (8 new, 4 modified)**
**Total lines: ~2,000 lines of new code**

---

## 💡 NEXT STEPS

Bạn muốn:

1. **🚀 Bắt đầu Week 1 ngay** - Tôi tạo file đầu tiên?
2. **📋 Review plan trước** - Có điều chỉnh gì không?
3. **🛠️ Setup cơ sở hạ tầng trước** - Deploy server, domain, etc?

Nói cho tôi biết bạn muốn làm gì tiếp theo! 🎯
