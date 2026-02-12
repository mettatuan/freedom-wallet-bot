"""
Registration Service - Handle user registration business logic

Extracted from: app/handlers/user/registration.py (150+ line function)
Purpose: Remove DB access and business logic from handlers
"""

from datetime import datetime
from typing import Optional
from loguru import logger

from app.utils.database import SessionLocal, User, Referral
from app.core.state_machine import StateManager, UserState


class RegistrationResult:
    """Plain data class for registration result (no Pydantic, no dataclass complexity)"""
    
    def __init__(
        self,
        success: bool,
        user_id: int,
        referral_verified: bool = False,
        referrer_id: Optional[int] = None,
        referrer_count: int = 0,
        referral_remaining: int = 2,
        review_status: Optional[str] = None,
        fraud_flags: Optional[list] = None,
    ):
        self.success = success
        self.user_id = user_id
        self.referral_verified = referral_verified
        self.referrer_id = referrer_id
        self.referrer_count = referrer_count
        self.referral_remaining = referral_remaining
        self.review_status = review_status
        self.fraud_flags = fraud_flags or []


class RegistrationService:
    """
    Registration business logic service.
    
    Plain Python class - no abstractions, no DI, no repository pattern.
    Handlers call this, this calls SQLAlchemy models directly.
    """
    
    def complete_registration(
        self,
        telegram_user_id: int,
        telegram_username: Optional[str],
        email: str,
        phone: Optional[str],
        full_name: str,
    ) -> RegistrationResult:
        """
        Complete user registration and handle referral verification.
        
        Args:
            telegram_user_id: Telegram user ID
            telegram_username: Telegram username (can be None)
            email: User email
            phone: User phone (optional)
            full_name: User full name
            
        Returns:
            RegistrationResult with transaction outcome
            
        Raises:
            ValueError: If user not found
            Exception: On database error (rolled back automatically)
        """
        session = SessionLocal()
        
        try:
            # Step 1: Update user basic info
            user = session.query(User).filter(User.id == telegram_user_id).first()
            
            if not user:
                raise ValueError(f"User {telegram_user_id} not found in database")
            
            # Update user fields
            user.email = email
            user.phone = phone
            user.full_name = full_name
            user.is_registered = True
            
            logger.info(f"✅ Updated user {telegram_user_id} registration info")
            
            # Step 2: Transition user state to REGISTERED
            with StateManager() as state_mgr:
                current_state, is_legacy = state_mgr.get_user_state(telegram_user_id)
                if is_legacy or current_state == UserState.VISITOR:
                    state_mgr.transition_user(
                        telegram_user_id,
                        UserState.REGISTERED,
                        "Completed registration"
                    )
                    logger.info(f"🎯 User {telegram_user_id} → REGISTERED state")
            
            # Step 3: Check for pending referral (will be expanded incrementally)
            referral = session.query(Referral).filter(
                Referral.referred_id == telegram_user_id,
                Referral.status == "PENDING"
            ).first()
            
            referral_verified = False
            referrer_id = None
            referrer_count = 0
            referral_remaining = 2
            review_status = None
            fraud_flags = []
            
            if referral:
                # TODO (Week 1): Extract referral verification logic to separate method
                # For now, just log that referral exists
                logger.info(f"📊 User {telegram_user_id} has pending referral: {referral.id}")
                referrer_id = referral.referrer_id
                
                # Placeholder: Will extract full fraud detection + verification logic
                # in incremental steps after basic extraction works
            
            # Commit transaction
            session.commit()
            
            logger.info(
                f"✅ Registration completed: user={telegram_user_id}, "
                f"email={email}, referral_exists={referral is not None}"
            )
            
            return RegistrationResult(
                success=True,
                user_id=telegram_user_id,
                referral_verified=referral_verified,
                referrer_id=referrer_id,
                referrer_count=referrer_count,
                referral_remaining=referral_remaining,
                review_status=review_status,
                fraud_flags=fraud_flags,
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Registration failed for user {telegram_user_id}: {e}")
            raise
            
        finally:
            session.close()
    
    # TODO (Week 1 - Day 2): Extract these methods after basic service works
    # def _verify_referral_with_fraud_check(self, referral, session):
    #     """Verify referral with fraud detection"""
    #     pass
    #
    # def _update_referrer_count(self, referrer, session):
    #     """Update referrer count and check for VIP unlock"""
    #     pass
    #
    # def _check_vip_unlock(self, referrer, session):
    #     """Check if referrer hit 2+ refs for FREE unlock"""
    #     pass


# Singleton instance (plain Python, no DI container)
registration_service = RegistrationService()
