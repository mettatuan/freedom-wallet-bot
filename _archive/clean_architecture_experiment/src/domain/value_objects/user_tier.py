"""User tier enumeration for subscription levels."""

from enum import Enum

class UserTier(str, Enum):
    """User subscription tiers."""
    FREE = "FREE"
    UNLOCK = "UNLOCK"
    PREMIUM = "PREMIUM"
    
    def __str__(self):
        return self.value
    
    @property
    def display_name(self):
        """Human-readable tier name."""
        return {
            UserTier.FREE: "Miễn phí",
            UserTier.UNLOCK: "Mở khóa",
            UserTier.PREMIUM: "Premium"
        }[self]
    
    @property
    def has_quick_record(self):
        """Check if tier has Quick Record feature."""
        return self == UserTier.PREMIUM
    
    @property
    def has_sheet_setup(self):
        """Check if tier has Google Sheets setup."""
        return self in [UserTier.UNLOCK, UserTier.PREMIUM]
