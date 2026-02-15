"""
Subscription Management - FREE vs PREMIUM tier system
Core principle: "Give Knowledge (FREE), Sell Time (PREMIUM)"
"""
from enum import Enum
from datetime import datetime, timedelta, date
from typing import Tuple, Optional
from loguru import logger
from app.utils.database import get_user_by_id, SessionLocal


class SubscriptionTier(Enum):
    """Subscription tier levels"""
    FREE = "FREE"
    TRIAL = "TRIAL"
    PREMIUM = "PREMIUM"


class SubscriptionManager:
    """
    Manage user subscription tiers and feature access
    
    FREE limits:
    - 5 bot messages per day
    - Basic features only
    
    PREMIUM/TRIAL unlimited:
    - Unlimited bot messages
    - All advanced features
    """
    
    # FREE tier limits (UNLIMITED for 3-month market testing)
    FREE_DAILY_MESSAGES = 999  # Effectively unlimited for testing phase
    
    # Feature flags
    PREMIUM_FEATURES = {
        'bot_chat_unlimited',
        'financial_analysis',
        'quick_record',
        'smart_reminders',
        'export_reports',
        'priority_support',
        'managed_setup',
        'recommendation_engine',
        'roi_dashboard'
    }
    
    @staticmethod
    def get_user_tier(user) -> SubscriptionTier:
        """
        Get current active tier (handles expiry automatically)
        
        Returns:
            SubscriptionTier: Current active tier
        """
        if not user:
            return SubscriptionTier.FREE
        
        now = datetime.utcnow()
        
        # Check PREMIUM status
        if user.subscription_tier == 'PREMIUM':
            if user.premium_expires_at and user.premium_expires_at > now:
                return SubscriptionTier.PREMIUM
            else:
                # Expired premium → auto-downgrade to FREE
                logger.warning(f"User {user.id} Premium expired, downgrading to FREE")
                user.subscription_tier = 'FREE'
                db = SessionLocal()
                user = db.merge(user)
                db.commit()
                db.close()
                return SubscriptionTier.FREE
        
        # Check TRIAL status
        if user.subscription_tier == 'TRIAL':
            if user.trial_ends_at and user.trial_ends_at > now:
                return SubscriptionTier.TRIAL
            else:
                # Expired trial → auto-downgrade to FREE
                logger.warning(f"User {user.id} Trial expired, downgrading to FREE")
                user.subscription_tier = 'FREE'
                db = SessionLocal()
                user = db.merge(user)
                db.commit()
                db.close()
                return SubscriptionTier.FREE
        
        return SubscriptionTier.FREE
    
    @staticmethod
    def can_send_message(user) -> Tuple[bool, str]:
        """
        Check if user can send a message (usage limit check)
        
        Returns:
            Tuple[bool, str]: (allowed, error_message)
        """
        tier = SubscriptionManager.get_user_tier(user)
        
        # PREMIUM/TRIAL = unlimited
        if tier in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
            return True, ""
        
        # FREE = check daily limit
        today = date.today()
        
        # Reset counter if new day
        last_reset_date = user.bot_chat_limit_date.date() if user.bot_chat_limit_date else None
        if last_reset_date != today:
            user.bot_chat_count = 0
            user.bot_chat_limit_date = datetime.now()
            db = SessionLocal()
            user = db.merge(user)  # Merge user into session
            db.commit()
            db.close()
        
        # Check limit
        if user.bot_chat_count >= SubscriptionManager.FREE_DAILY_MESSAGES:
            remaining = SubscriptionManager.FREE_DAILY_MESSAGES - user.bot_chat_count
            return False, f"⚠️ Bạn đã hết {SubscriptionManager.FREE_DAILY_MESSAGES} tin nhắn hôm nay!\n\nCòn lại: {max(0, remaining)}/{SubscriptionManager.FREE_DAILY_MESSAGES}"
        
        return True, ""
    
    @staticmethod
    def increment_message_count(user):
        """Increment daily message counter for FREE users"""
        tier = SubscriptionManager.get_user_tier(user)
        
        if tier == SubscriptionTier.FREE:
            today = date.today()
            
            # Reset if new day
            last_reset_date = user.bot_chat_limit_date.date() if user.bot_chat_limit_date else None
            if last_reset_date != today:
                user.bot_chat_count = 1
                user.bot_chat_limit_date = datetime.now()
            else:
                user.bot_chat_count += 1
            
            # Save changes to database
            db = SessionLocal()
            user = db.merge(user)  # Merge detached object into this session
            db.commit()
            db.close()
            
            logger.info(f"User {user.id} message count: {user.bot_chat_count}/{SubscriptionManager.FREE_DAILY_MESSAGES}")
    
    @staticmethod
    def can_use_feature(user, feature: str) -> Tuple[bool, str]:
        """
        Check if user can use a premium feature
        
        Args:
            user: User object
            feature: Feature name (e.g., 'financial_analysis')
        
        Returns:
            Tuple[bool, str]: (allowed, error_message)
        """
        tier = SubscriptionManager.get_user_tier(user)
        
        # PREMIUM/TRIAL = all features
        if tier in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
            return True, ""
        
        # Check if feature is premium-only
        if feature in SubscriptionManager.PREMIUM_FEATURES:
            return False, f"🔒 Tính năng Premium\n\nNâng cấp để sử dụng '{feature}'"
        
        return True, ""
    
    @staticmethod
    def start_trial(user, days: int = 7, scheduler=None):
        """
        Start trial period for user
        
        Args:
            user: User object
            days: Trial duration in days (default 7)
            scheduler: APScheduler instance for scheduling jobs
        """
        now = datetime.utcnow()
        trial_end = now + timedelta(days=days)
        
        user.subscription_tier = 'TRIAL'
        user.trial_ends_at = trial_end
        user.premium_started_at = now  # Track when they first tried premium
        
        db = SessionLocal()
        user = db.merge(user)
        db.commit()
        db.close()
        
        logger.info(f"User {user.id} started {days}-day trial (ends {trial_end})")
        
        # Schedule jobs if scheduler provided
        if scheduler:
            # Schedule WOW moment (24h after trial start)
            from app.jobs.wow_moment import schedule_wow_moment_job
            schedule_wow_moment_job(user.id, scheduler)
            
            # Schedule Day-6 reminder (24h before trial ends)
            from app.jobs.trial_churn_prevention import schedule_trial_reminder_job
            schedule_trial_reminder_job(user.id, trial_end, scheduler)
    
    @staticmethod
    def upgrade_to_premium(user, months: int = 12):
        """
        Upgrade user to PREMIUM
        
        Args:
            user: User object
            months: Subscription duration in months (default 12)
        """
        now = datetime.utcnow()
        expires = now + timedelta(days=months * 30)  # Approximate
        
        user.subscription_tier = 'PREMIUM'
        user.premium_started_at = now
        user.premium_expires_at = expires
        user.trial_ends_at = None  # Clear trial date
        
        db = SessionLocal()
        user = db.merge(user)
        db.commit()
        db.close()
        
        logger.info(f"User {user.id} upgraded to PREMIUM (expires {expires})")
        
        # Schedule WOW moment if first time premium
        # Note: Commented out as schedule_wow_moment function needs scheduler parameter
        # if not user.premium_started_at or (now - user.premium_started_at).days < 1:
        #     from app.jobs.wow_moment import schedule_wow_moment_job
        #     schedule_wow_moment_job(user.id, scheduler)
    
    @staticmethod
    def get_remaining_messages(user) -> int:
        """Get remaining FREE messages for today"""
        tier = SubscriptionManager.get_user_tier(user)
        
        if tier in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
            return 999999  # Unlimited
        
        today = date.today()
        
        # Reset if new day
        if user.bot_chat_limit_date != today:
            return SubscriptionManager.FREE_DAILY_MESSAGES
        
        remaining = SubscriptionManager.FREE_DAILY_MESSAGES - user.bot_chat_count
        return max(0, remaining)
    
    @staticmethod
    def is_premium(user) -> bool:
        """Quick check if user is PREMIUM or TRIAL"""
        tier = SubscriptionManager.get_user_tier(user)
        return tier in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]


# Helper functions for quick access
def get_user_tier(user_id: int) -> SubscriptionTier:
    """Get user tier by ID"""
    user = get_user_by_id(user_id)
    return SubscriptionManager.get_user_tier(user)

def is_premium(user_id: int) -> bool:
    """Check if user is premium by ID"""
    user = get_user_by_id(user_id)
    return SubscriptionManager.is_premium(user)

def can_send_message(user_id: int) -> Tuple[bool, str]:
    """Check if user can send message by ID"""
    user = get_user_by_id(user_id)
    return SubscriptionManager.can_send_message(user)

