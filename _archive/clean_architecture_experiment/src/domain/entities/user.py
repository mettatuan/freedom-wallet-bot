"""User entity - represents a Freedom Wallet user."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field

from ..value_objects.user_tier import UserTier


@dataclass
class User:
    """
    User entity representing a Freedom Wallet user.
    
    Business Rules:
    - FREE is the default tier for new users
    - FREE → UNLOCK requires Google Sheets setup
    - UNLOCK → PREMIUM requires payment
    - Cannot downgrade from PREMIUM to FREE directly (must go through UNLOCK)
    """
    
    user_id: int
    telegram_username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tier: UserTier = field(default=UserTier.FREE)
    sheet_url: Optional[str] = None
    webapp_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def upgrade_to_unlock(self, sheet_url: str, webapp_url: str) -> None:
        """
        Upgrade user from FREE to UNLOCK tier.
        
        Args:
            sheet_url: Google Sheets URL
            webapp_url: Web App deployment URL
            
        Raises:
            ValueError: If user is not FREE tier or URLs are missing
        """
        if self.tier != UserTier.FREE:
            raise ValueError(f"Cannot upgrade to UNLOCK from {self.tier}. Must be FREE tier.")
        
        if not sheet_url or not webapp_url:
            raise ValueError("Sheet URL and Web App URL are required for UNLOCK tier.")
        
        self.tier = UserTier.UNLOCK
        self.sheet_url = sheet_url
        self.webapp_url = webapp_url
        self.updated_at = datetime.utcnow()
    
    def upgrade_to_premium(self) -> None:
        """
        Upgrade user from UNLOCK to PREMIUM tier.
        
        Raises:
            ValueError: If user is not UNLOCK tier
        """
        if self.tier != UserTier.UNLOCK:
            raise ValueError(f"Cannot upgrade to PREMIUM from {self.tier}. Must be UNLOCK tier.")
        
        self.tier = UserTier.PREMIUM
        self.updated_at = datetime.utcnow()
    
    def downgrade_to_unlock(self) -> None:
        """
        Downgrade user from PREMIUM to UNLOCK tier.
        
        Raises:
            ValueError: If user is not PREMIUM tier or sheet not set up
        """
        if self.tier != UserTier.PREMIUM:
            raise ValueError(f"Cannot downgrade to UNLOCK from {self.tier}. Must be PREMIUM tier.")
        
        if not self.sheet_url or not self.webapp_url:
            raise ValueError("Cannot downgrade: Sheet setup is required for UNLOCK tier.")
        
        self.tier = UserTier.UNLOCK
        self.updated_at = datetime.utcnow()
    
    def downgrade_to_free(self) -> None:
        """
        Downgrade user from UNLOCK to FREE tier.
        
        Raises:
            ValueError: If user is not UNLOCK tier
        """
        if self.tier != UserTier.UNLOCK:
            raise ValueError(f"Cannot downgrade to FREE from {self.tier}. Must be UNLOCK tier.")
        
        self.tier = UserTier.FREE
        self.sheet_url = None
        self.webapp_url = None
        self.updated_at = datetime.utcnow()
    
    def is_free(self) -> bool:
        """Check if user is on FREE tier."""
        return self.tier == UserTier.FREE
    
    def is_unlock(self) -> bool:
        """Check if user is on UNLOCK tier."""
        return self.tier == UserTier.UNLOCK
    
    def is_premium(self) -> bool:
        """Check if user is on PREMIUM tier."""
        return self.tier == UserTier.PREMIUM
    
    def can_use_quick_record(self) -> bool:
        """Check if user can use Quick Record feature."""
        return self.tier.has_quick_record
    
    def has_sheet_setup(self) -> bool:
        """Check if user has Google Sheets set up."""
        return bool(self.sheet_url and self.webapp_url)
    
    def can_upgrade_to_unlock(self) -> bool:
        """Check if user can upgrade to UNLOCK tier."""
        return self.tier == UserTier.FREE
    
    def can_upgrade_to_premium(self) -> bool:
        """Check if user can upgrade to PREMIUM tier."""
        return self.tier == UserTier.UNLOCK and self.has_sheet_setup()
    
    def __str__(self) -> str:
        """String representation of user."""
        return f"User(id={self.user_id}, username={self.telegram_username}, tier={self.tier})"
    
    def __repr__(self) -> str:
        """Debug representation of user."""
        return (f"User(user_id={self.user_id}, telegram_username={self.telegram_username}, "
                f"tier={self.tier}, has_sheet={self.has_sheet_setup()})")
