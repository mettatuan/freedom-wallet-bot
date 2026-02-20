"""
Database Models for Bot
Phase 2: Context Memory + Referral System
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config.settings import settings
import hashlib
import secrets

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
# Configure session to not expire objects after commit
# This allows objects to be used after session.close() without DetachedInstanceError
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    """
    Get database session
    Usage:
        db = next(get_db())
        try:
            # Use db
            db.commit()
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    """User model - Store Telegram user info"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)  # Telegram user ID
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    language_code = Column(String(10), default="vi")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_blocked = Column(Boolean, default=False)
    
    # Referral fields
    referral_code = Column(String(20), unique=True, index=True)  # Unique referral code
    referred_by = Column(Integer, nullable=True)  # Who referred this user
    referral_count = Column(Integer, default=0)  # How many people this user referred (GROWTH METRIC ONLY)
    
    # VIP Identity Tier (10/50/100 refs)
    vip_tier = Column(String(20), nullable=True)  # RISING_STAR, SUPER_VIP, LEGEND
    vip_unlocked_at = Column(DateTime, nullable=True)  # When VIP tier was unlocked
    vip_benefits = Column(Text, default='[]')  # JSON list of benefits
    
    # Subscription
    subscription_tier = Column(String(20), default="TRIAL")  # TRIAL, FREE, PREMIUM
    subscription_expires = Column(DateTime, nullable=True)
    
    # Week 1 Sprint: Usage tracking columns
    bot_chat_count = Column(Integer, default=0)  # Daily message counter
    bot_chat_limit_date = Column(DateTime, nullable=True)  # Last reset date
    premium_started_at = Column(DateTime, nullable=True)  # When premium/trial started
    premium_expires_at = Column(DateTime, nullable=True)  # When premium expires
    trial_ends_at = Column(DateTime, nullable=True)  # When trial ends
    premium_features_used = Column(Text, default='{}')  # JSON track feature usage
    
    # Week 1 Sprint: Fraud tracking (for future use)
    ip_address = Column(String(45), nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    last_referral_at = Column(DateTime, nullable=True)
    referral_velocity = Column(Integer, default=0)
    
    # Registration info (collected via bot)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    full_name = Column(String(255), nullable=True)
    is_registered = Column(Boolean, default=False)  # Completed registration form
    
    # STATE MACHINE (Foundation Phase - Week 1)
    user_state = Column(String(20), default="LEGACY")  # LEGACY, VISITOR, REGISTERED, VIP, SUPER_VIP, ADVOCATE, CHURNED
    current_program = Column(String(50), nullable=True)  # NURTURE_7_DAY, ONBOARDING_7_DAY, ADVANCED_WORKSHOP, etc.
    program_day = Column(Integer, default=0)  # Current day in program (0-based)
    program_started_at = Column(DateTime, nullable=True)  # When enrolled in current program
    program_completed_at = Column(DateTime, nullable=True)  # When completed current program
    
    # SUPER VIP DECAY TRACKING (Week 3)
    super_vip_last_active = Column(DateTime, nullable=True)  # Last interaction date
    super_vip_decay_warned = Column(Boolean, default=False)  # Warned at day 10
    show_on_leaderboard = Column(Boolean, default=True)  # Spotlight status
    
    # TRANSACTION TRACKING & STREAKS (Daily Reminder System)
    last_transaction_date = Column(DateTime, nullable=True)  # Last transaction date
    streak_count = Column(Integer, default=0)  # Current streak (consecutive days)
    longest_streak = Column(Integer, default=0)  # Longest streak achieved
    total_transactions = Column(Integer, default=0)  # Total transactions recorded
    milestone_7day_achieved = Column(Boolean, default=False)  # 7-day milestone
    
    # GOOGLE SHEETS INTEGRATION (Premium Features)
    spreadsheet_id = Column(String(100), nullable=True)  # User's Google Sheets ID (44 chars)
    sheets_connected_at = Column(DateTime, nullable=True)  # When sheets connected
    sheets_last_sync = Column(DateTime, nullable=True)  # Last data sync timestamp
    webhook_url = Column(String(500), nullable=True)  # Apps Script webhook URL for Quick Record
    web_app_url = Column(String(500), nullable=True)  # Freedom Wallet Web App URL for manual entry
    milestone_30day_achieved = Column(Boolean, default=False)  # 30-day milestone
    milestone_90day_achieved = Column(Boolean, default=False)  # 90-day milestone
    last_reminder_sent = Column(DateTime, nullable=True)  # Last reminder timestamp
    reminder_enabled = Column(Boolean, default=True)  # User preference for reminders
    
    # ACTIVATION & RETENTION TRACKING (Phase 1 - Retention-First Model)
    first_transaction_at = Column(DateTime, nullable=True)  # When user logged first transaction (ACTIVATION)
    activated_at = Column(DateTime, nullable=True)  # Activation timestamp (same as first_transaction_at)
    last_checkin = Column(DateTime, nullable=True)  # Last check-in message sent
    last_insight_sent = Column(DateTime, nullable=True)  # Last weekly insight sent (Phase 2 - Reflection Engine)
    
    def __repr__(self):
        return f"<User {self.id} ({self.username}) state={self.user_state} streak={self.streak_count}>"


class Transaction(Base):
    """Transaction model - Store financial transactions"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)  # Telegram user ID
    amount = Column(Integer)  # Amount in VND (negative for expenses, positive for income)
    category = Column(String(50))  # Category (Ăn uống, Di chuyển, Lương, etc.)
    description = Column(String(255))  # Transaction description (e.g., "Cà phê")
    transaction_type = Column(String(20))  # "income" or "expense"
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # Transaction date
    synced_to_sheets = Column(Boolean, default=False)  # Whether synced to Google Sheets
    synced_at = Column(DateTime, nullable=True)  # When synced
    
    def __repr__(self):
        return f"<Transaction {self.id} user={self.user_id} amount={self.amount} category={self.category}>"


class ConversationContext(Base):
    """Store conversation context for AI"""
    __tablename__ = "conversation_contexts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)  # Telegram user ID
    role = Column(String(20))  # "user" or "assistant"
    content = Column(Text)  # Message content
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Context {self.id} user={self.user_id} role={self.role}>"


class SupportTicket(Base):
    """Store support tickets (backup to Google Sheets)"""
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String(100))
    message = Column(Text)
    status = Column(String(20), default="Open")  # Open, In Progress, Resolved, Closed
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Ticket {self.ticket_id} status={self.status}>"


class MessageLog(Base):
    """Log all messages for analytics"""
    __tablename__ = "message_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    message_type = Column(String(50))  # text, photo, voice, command
    message_content = Column(Text)
    response_type = Column(String(50))  # faq, ai, error
    response_time_ms = Column(Integer)  # Response time in milliseconds
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Log {self.id} user={self.user_id} type={self.message_type}>"


class Referral(Base):
    """Track referral relationships"""
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    referrer_id = Column(Integer, index=True)  # Who shared the link
    referred_id = Column(Integer, index=True)  # Who joined via link
    referral_code = Column(String(20), index=True)  # Code used
    status = Column(String(20), default="PENDING")  # PENDING, VERIFIED, REWARDED
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)  # When referred user verified
    
    # FRAUD DETECTION (Week 1)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(255), nullable=True)  # Browser/device info
    device_fingerprint = Column(String(64), nullable=True)  # Hashed device ID
    velocity_score = Column(Integer, default=0)  # Fraud detection score (0-100)
    review_status = Column(String(20), default="AUTO_APPROVED")  # AUTO_APPROVED, PENDING_REVIEW, REJECTED
    reviewed_by = Column(Integer, nullable=True)  # Admin user_id
    reviewed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Referral {self.referrer_id} -> {self.referred_id} ({self.status}/{self.review_status})>"


class Subscription(Base):
    """Track Premium subscriptions and payments"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True, unique=True)
    tier = Column(String(20), default="TRIAL")  # TRIAL, FREE, PREMIUM
    payment_method = Column(String(50), nullable=True)  # VNPay, MoMo, Transfer
    amount_paid = Column(Float, default=0)  # Amount in VND
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Subscription user={self.user_id} tier={self.tier}>"


class PaymentVerification(Base):
    """Track payment verification requests"""
    __tablename__ = "payment_verifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, index=True)  # User who made payment
    amount = Column(Float)  # Amount in VND
    transaction_info = Column(Text, nullable=True)  # Transaction details from user
    transfer_code = Column(String(50), nullable=True)  # FW{user_id}
    status = Column(String(20), default="PENDING")  # PENDING, APPROVED, REJECTED
    submitted_by = Column(Integer)  # User ID who submitted
    approved_by = Column(Integer, nullable=True)  # Admin who approved
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)  # Admin notes
    
    def __repr__(self):
        return f"<PaymentVerification user={self.user_id} status={self.status}>"


# Create tables
Base.metadata.create_all(engine)


# Helper functions
async def save_user_to_db(user):
    """Save or update user in database"""
    session = SessionLocal()
    try:
        db_user = session.query(User).filter(User.id == user.id).first()
        if db_user:
            # Update existing user
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            db_user.last_active = datetime.utcnow()
        else:
            # Create new user with unique referral code
            referral_code = generate_referral_code(user.id)
            db_user = User(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code or "vi",
                referral_code=referral_code,
                subscription_tier="TRIAL"
            )
            session.add(db_user)
        session.commit()
        session.refresh(db_user)  # Ensure all attributes are loaded
        # Don't expunge - causes DetachedInstanceError when accessing attributes
        # session.expunge(db_user)
        return db_user
    finally:
        session.close()


async def get_user_context(user_id: int, limit: int = 5):
    """Get last N messages from conversation context"""
    session = SessionLocal()
    try:
        contexts = session.query(ConversationContext)\
            .filter(ConversationContext.user_id == user_id)\
            .order_by(ConversationContext.timestamp.desc())\
            .limit(limit)\
            .all()
        
        # Convert to OpenAI message format
        messages = [
            {"role": context.role, "content": context.content}
            for context in reversed(contexts)
        ]
        return messages
    finally:
        session.close()


async def save_message_to_context(user_id: int, user_message: str, ai_response: str):
    """Save user message and AI response to context"""
    session = SessionLocal()
    try:
        # Save user message
        user_context = ConversationContext(
            user_id=user_id,
            role="user",
            content=user_message
        )
        session.add(user_context)
        
        # Save AI response
        ai_context = ConversationContext(
            user_id=user_id,
            role="assistant",
            content=ai_response
        )
        session.add(ai_context)
        
        session.commit()
    finally:
        session.close()


# ============= REFERRAL SYSTEM FUNCTIONS =============

def generate_referral_code(user_id: int) -> str:
    """Generate unique referral code for user"""
    # Create code from user_id + random salt
    salt = secrets.token_hex(4)
    raw = f"{user_id}_{salt}"
    code = hashlib.sha256(raw.encode()).hexdigest()[:8].upper()
    return code


async def get_user_by_id(user_id: int):
    """Get user from database"""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        # Don't expunge - keep user attached to avoid DetachedInstanceError
        # Session will be closed but object remains usable for basic attribute access
        return user
    finally:
        session.close()


async def get_user_by_referral_code(code: str):
    """Get user by their referral code"""
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.referral_code == code).first()
        # Don't expunge - keep user attached to avoid DetachedInstanceError
        return user
    finally:
        session.close()


async def create_referral(referrer_id: int, referred_id: int, code: str):
    """Create a referral relationship (PENDING until user registers)"""
    session = SessionLocal()
    try:
        # Check if referral already exists
        existing = session.query(Referral).filter(
            Referral.referred_id == referred_id
        ).first()
        
        if existing:
            return None, "Bạn đã được giới thiệu bởi người khác rồi!"
        
        # Create referral with PENDING status
        referral = Referral(
            referrer_id=referrer_id,
            referred_id=referred_id,
            referral_code=code,
            status="PENDING"  # Will be VERIFIED after registration
        )
        session.add(referral)
        
        # Update referred user
        referred_user = session.query(User).filter(User.id == referred_id).first()
        if referred_user:
            referred_user.referred_by = referrer_id
        
        # NOTE: referral_count will be updated after user completes registration
        
        session.commit()
        session.refresh(referral)
        session.expunge(referral)
        return referral, None
    except Exception as e:
        session.rollback()
        return None, str(e)
    finally:
        session.close()


async def get_user_referrals(user_id: int):
    """Get all users referred by this user"""
    session = SessionLocal()
    try:
        referrals = session.query(Referral).filter(
            Referral.referrer_id == user_id,
            Referral.status == "VERIFIED"
        ).all()
        
        # Get referred user details
        referred_users = []
        for ref in referrals:
            user = session.query(User).filter(User.id == ref.referred_id).first()
            if user:
                referred_users.append({
                    'id': user.id,
                    'name': user.first_name or user.username or 'Anonymous',
                    'date': ref.created_at
                })
        
        return referred_users
    finally:
        session.close()


async def create_subscription(user_id: int, tier: str, payment_method: str = None, amount: float = 0):
    """Create or update subscription"""
    session = SessionLocal()
    try:
        sub = session.query(Subscription).filter(Subscription.user_id == user_id).first()
        
        if sub:
            # Update existing
            sub.tier = tier
            sub.payment_method = payment_method
            sub.amount_paid += amount
            sub.is_active = True
        else:
            # Create new
            sub = Subscription(
                user_id=user_id,
                tier=tier,
                payment_method=payment_method,
                amount_paid=amount,
                is_active=True
            )
            session.add(sub)
        
        # Update user subscription
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.subscription_tier = tier
        
        session.commit()
        session.refresh(sub)
        session.expunge(sub)
        return sub
    finally:
        session.close()


async def update_user_registration(user_id: int, email: str, phone: str = None, full_name: str = None, source: str = 'BOT', referral_count: int = None):
    """
    Update user with registration information
    Used when syncing from web or completing in-bot registration
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        user.email = email
        user.phone = phone or user.phone
        user.full_name = full_name or user.full_name
        user.is_registered = True
        
        # Update referral count if provided (from Google Sheets sync)
        if referral_count is not None:
            user.referral_count = referral_count
            print(f"📊 Updated referral_count to {referral_count} for user {user_id}")
        
        session.commit()
        session.refresh(user)
        session.expunge(user)
        
        print(f"✅ Updated user {user_id} registration: {email} (source: {source})")
        return user
    except Exception as e:
        session.rollback()
        print(f"❌ Error updating user registration: {e}")
        return None
    finally:
        session.close()
