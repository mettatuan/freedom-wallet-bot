"""Subscription entity - represents a user's tier subscription."""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field

from ..value_objects.user_tier import UserTier


@dataclass
class Subscription:
    """
    Subscription entity representing a user's tier subscription.
    
    Business Rules:
    - FREE tier never expires
    - UNLOCK tier expires after 30 days if not renewed
    - PREMIUM tier requires active payment subscription
    - Grace period: 3 days after expiry before downgrade
    """
    
    user_id: int
    tier: UserTier
    started_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    auto_renew: bool = False
    last_payment_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    UNLOCK_DURATION_DAYS = 30
    GRACE_PERIOD_DAYS = 3
    
    @classmethod
    def create_free_subscription(cls, user_id: int) -> 'Subscription':
        """
        Create a FREE tier subscription (never expires).
        
        Args:
            user_id: User ID
            
        Returns:
            Subscription instance for FREE tier
        """
        return cls(
            user_id=user_id,
            tier=UserTier.FREE,
            expires_at=None,  # FREE never expires
            auto_renew=False
        )
    
    @classmethod
    def create_unlock_subscription(cls, user_id: int) -> 'Subscription':
        """
        Create an UNLOCK tier subscription (30 days expiry).
        
        Args:
            user_id: User ID
            
        Returns:
            Subscription instance for UNLOCK tier
        """
        started_at = datetime.utcnow()
        expires_at = started_at + timedelta(days=cls.UNLOCK_DURATION_DAYS)
        
        return cls(
            user_id=user_id,
            tier=UserTier.UNLOCK,
            started_at=started_at,
            expires_at=expires_at,
            auto_renew=False
        )
    
    @classmethod
    def create_premium_subscription(cls, user_id: int, expires_at: datetime) -> 'Subscription':
        """
        Create a PREMIUM tier subscription.
        
        Args:
            user_id: User ID
            expires_at: Expiry datetime (based on payment period)
            
        Returns:
            Subscription instance for PREMIUM tier
        """
        return cls(
            user_id=user_id,
            tier=UserTier.PREMIUM,
            started_at=datetime.utcnow(),
            expires_at=expires_at,
            auto_renew=True,
            last_payment_at=datetime.utcnow()
        )
    
    def is_active(self) -> bool:
        """
        Check if subscription is currently active.
        
        Returns:
            True if active, False otherwise
        """
        # FREE tier is always active
        if self.tier == UserTier.FREE:
            return True
        
        # Check expiry
        if self.expires_at is None:
            return True
        
        return datetime.utcnow() < self.expires_at
    
    def is_in_grace_period(self) -> bool:
        """
        Check if subscription is in grace period (3 days after expiry).
        
        Returns:
            True if in grace period, False otherwise
        """
        if self.tier == UserTier.FREE or self.expires_at is None:
            return False
        
        now = datetime.utcnow()
        grace_end = self.expires_at + timedelta(days=self.GRACE_PERIOD_DAYS)
        
        return self.expires_at <= now < grace_end
    
    def is_expired(self) -> bool:
        """
        Check if subscription has expired (past grace period).
        
        Returns:
            True if expired, False otherwise
        """
        if self.tier == UserTier.FREE or self.expires_at is None:
            return False
        
        return not self.is_active() and not self.is_in_grace_period()
    
    def days_until_expiry(self) -> Optional[int]:
        """
        Calculate days until subscription expires.
        
        Returns:
            Number of days until expiry, None if never expires
        """
        if self.tier == UserTier.FREE or self.expires_at is None:
            return None
        
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    def can_renew(self) -> bool:
        """
        Check if subscription can be renewed.
        
        Returns:
            True if can be renewed, False otherwise
        """
        # FREE tier doesn't need renewal
        if self.tier == UserTier.FREE:
            return False
        
        # Can renew if expired or about to expire (within 7 days)
        days_left = self.days_until_expiry()
        return days_left is not None and days_left <= 7
    
    def renew(self, duration_days: int = UNLOCK_DURATION_DAYS) -> None:
        """
        Renew subscription for specified duration.
        
        Args:
            duration_days: Number of days to extend subscription
            
        Raises:
            ValueError: If FREE tier or invalid duration
        """
        if self.tier == UserTier.FREE:
            raise ValueError("FREE tier subscription cannot be renewed.")
        
        if duration_days <= 0:
            raise ValueError("Duration must be positive.")
        
        now = datetime.utcnow()
        
        # If expired, start from now; otherwise extend current expiry
        if self.expires_at and self.expires_at > now:
            self.expires_at = self.expires_at + timedelta(days=duration_days)
        else:
            self.expires_at = now + timedelta(days=duration_days)
        
        self.last_payment_at = now
        self.updated_at = now
    
    def expire(self) -> None:
        """
        Manually expire the subscription immediately.
        
        Raises:
            ValueError: If FREE tier
        """
        if self.tier == UserTier.FREE:
            raise ValueError("Cannot expire FREE tier subscription.")
        
        self.expires_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        """String representation of subscription."""
        status = "active" if self.is_active() else "expired"
        return f"Subscription(user_id={self.user_id}, tier={self.tier}, status={status})"
    
    def __repr__(self) -> str:
        """Debug representation of subscription."""
        days = self.days_until_expiry()
        days_str = f"{days} days" if days is not None else "never"
        return (f"Subscription(user_id={self.user_id}, tier={self.tier}, "
                f"active={self.is_active()}, expires_in={days_str})")
