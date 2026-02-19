"""
🎯 UNIFIED STATE & TIER SYSTEM
================================

Clean architecture for FREE → UNLOCK → PREMIUM flow
Replaces legacy referral_count logic with proper state machine

Author: Freedom Wallet Team
Version: 2.0 (Unified Architecture)
Date: 2026-02-17
"""

from enum import Enum
from typing import Set, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


# ============================================================================
# SUBSCRIPTION TIERS (What User Pays For)
# ============================================================================

class SubscriptionTier(str, Enum):
    """
    Subscription tiers - What the user has access to
    
    Flow: FREE → UNLOCK → PREMIUM
    """
    
    FREE = "FREE"
    # - New users (not yet setup)
    # - Limited features
    # - 5 messages/day with AI
    
    UNLOCK = "UNLOCK"
    # - Completed Google Sheets setup
    # - Can log transactions
    # - Full access to basic features
    
    PREMIUM = "PREMIUM"
    # - Paid subscription (999k/year)
    # - Unlimited AI messages
    # - Advanced features
    # - Priority support
    
    @property
    def display_name(self) -> str:
        """Human-readable tier name (Vietnamese)"""
        return {
            SubscriptionTier.FREE: "Miễn phí",
            SubscriptionTier.UNLOCK: "Đã mở khóa",
            SubscriptionTier.PREMIUM: "Premium"
        }[self]
    
    @property
    def ai_message_limit(self) -> Optional[int]:
        """Daily AI message limit (None = unlimited)"""
        return {
            SubscriptionTier.FREE: 5,
            SubscriptionTier.UNLOCK: 20,
            SubscriptionTier.PREMIUM: None  # Unlimited
        }[self]
    
    @property
    def can_setup_sheets(self) -> bool:
        """Can user setup Google Sheets integration"""
        return self in [SubscriptionTier.UNLOCK, SubscriptionTier.PREMIUM]
    
    @property
    def has_ai_insights(self) -> bool:
        """Has advanced AI financial insights"""
        return self == SubscriptionTier.PREMIUM


# ============================================================================
# USER STATES (User Journey Stage)
# ============================================================================

class UserState(str, Enum):
    """
    User state - Where they are in the journey
    
    Different from tier: State = journey stage, Tier = access level
    """
    
    VISITOR = "VISITOR"
    # - Just clicked bot link
    # - Not registered yet
    # - Seeing welcome message
    
    REGISTERED = "REGISTERED"
    # - Completed registration
    # - Has account
    # - Tier = FREE
    
    ONBOARDING = "ONBOARDING"
    # - Setting up Google Sheets
    # - In tutorial flow
    # - Transitioning to UNLOCK
    
    ACTIVE = "ACTIVE"
    # - Using the bot regularly
    # - Tier = UNLOCK or PREMIUM
    # - Daily logging
    
    VIP = "VIP"
    # - 2+ successful referrals
    # - Unlock rewards
    # - Special perks
    
    SUPER_VIP = "SUPER_VIP"
    # - 50+ referrals
    # - Top contributor
    # - Premium benefits
    
    ADVOCATE = "ADVOCATE"
    # - 100+ referrals
    # - Community leader
    # - Lifetime benefits
    
    CHURNED = "CHURNED"
    # - Inactive 90+ days
    # - No engagement
    # - Re-activation needed
    
    BLOCKED = "BLOCKED"
    # - Violated terms
    # - Fraud detected
    # - Permanently banned


# ============================================================================
# STATE TRANSITIONS
# ============================================================================

class StateTransitions:
    """
    Valid state transitions with business rules
    """
    
    VALID_TRANSITIONS: Dict[UserState, Set[UserState]] = {
        UserState.VISITOR: {
            UserState.REGISTERED,
            UserState.BLOCKED
        },
        UserState.REGISTERED: {
            UserState.ONBOARDING,
            UserState.VIP,
            UserState.CHURNED,
            UserState.BLOCKED
        },
        UserState.ONBOARDING: {
            UserState.ACTIVE,
            UserState.CHURNED,
            UserState.BLOCKED
        },
        UserState.ACTIVE: {
            UserState.VIP,
            UserState.CHURNED,
            UserState.BLOCKED
        },
        UserState.VIP: {
            UserState.SUPER_VIP,
            UserState.ACTIVE,  # Decay if inactive
            UserState.CHURNED,
            UserState.BLOCKED
        },
        UserState.SUPER_VIP: {
            UserState.ADVOCATE,
            UserState.VIP,  # Decay if below 50 refs
            UserState.CHURNED,
            UserState.BLOCKED
        },
        UserState.ADVOCATE: {
            UserState.SUPER_VIP,  # Decay if below 100 refs
            UserState.CHURNED,
            UserState.BLOCKED
        },
        UserState.CHURNED: {
            UserState.ACTIVE,  # Re-activation successful
            UserState.BLOCKED
        },
        UserState.BLOCKED: set()  # No way out
    }
    
    @classmethod
    def can_transition(cls, from_state: UserState, to_state: UserState) -> bool:
        """Check if transition is valid"""
        return to_state in cls.VALID_TRANSITIONS.get(from_state, set())
    
    @classmethod
    def get_valid_next_states(cls, current_state: UserState) -> Set[UserState]:
        """Get all valid next states from current state"""
        return cls.VALID_TRANSITIONS.get(current_state, set())


# ============================================================================
# TIER TRANSITIONS
# ============================================================================

class TierTransitions:
    """
    Valid tier upgrade/downgrade paths
    """
    
    VALID_UPGRADES: Dict[SubscriptionTier, Set[SubscriptionTier]] = {
        SubscriptionTier.FREE: {
            SubscriptionTier.UNLOCK,
            SubscriptionTier.PREMIUM  # Direct upgrade possible
        },
        SubscriptionTier.UNLOCK: {
            SubscriptionTier.PREMIUM
        },
        SubscriptionTier.PREMIUM: set()  # Cannot upgrade further
    }
    
    VALID_DOWNGRADES: Dict[SubscriptionTier, Set[SubscriptionTier]] = {
        SubscriptionTier.FREE: set(),  # Cannot downgrade
        SubscriptionTier.UNLOCK: {
            SubscriptionTier.FREE  # If sheets removed
        },
        SubscriptionTier.PREMIUM: {
            SubscriptionTier.UNLOCK  # If subscription expires
        }
    }
    
    @classmethod
    def can_upgrade(cls, from_tier: SubscriptionTier, to_tier: SubscriptionTier) -> bool:
        """Check if upgrade is valid"""
        return to_tier in cls.VALID_UPGRADES.get(from_tier, set())
    
    @classmethod
    def can_downgrade(cls, from_tier: SubscriptionTier, to_tier: SubscriptionTier) -> bool:
        """Check if downgrade is valid"""
        return to_tier in cls.VALID_DOWNGRADES.get(from_tier, set())


# ============================================================================
# UNIFIED USER MODEL
# ============================================================================

@dataclass
class UserProfile:
    """
    Unified user profile with state + tier
    
    Combines journey stage (state) with access level (tier)
    """
    
    user_id: int
    state: UserState
    tier: SubscriptionTier
    
    # Metadata
    created_at: datetime
    last_active: datetime
    
    # Referral tracking
    referral_count: int = 0
    referred_by: Optional[int] = None
    
    # Subscription tracking
    premium_expires_at: Optional[datetime] = None
    
    def can_transition_to(self, new_state: UserState) -> bool:
        """Check if can transition to new state"""
        return StateTransitions.can_transition(self.state, new_state)
    
    def can_upgrade_to(self, new_tier: SubscriptionTier) -> bool:
        """Check if can upgrade to new tier"""
        return TierTransitions.can_upgrade(self.tier, new_tier)
    
    def is_premium_active(self) -> bool:
        """Check if premium subscription is active"""
        if self.tier != SubscriptionTier.PREMIUM:
            return False
        if not self.premium_expires_at:
            return False
        return datetime.utcnow() < self.premium_expires_at
    
    def should_unlock(self) -> bool:
        """Check if user should auto-unlock (2+ referrals)"""
        return self.referral_count >= 2 and self.tier == SubscriptionTier.FREE


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("=== Unified State & Tier System ===\n")
    
    # Example 1: New user journey
    print("1. NEW USER FLOW:")
    print("   VISITOR → REGISTERED (tier=FREE)")
    print("   REGISTERED → ONBOARDING (setting up sheets)")
    print("   ONBOARDING → ACTIVE (tier=UNLOCK)")
    print("   ACTIVE → VIP (2+ referrals)")
    print()
    
    # Example 2: Premium upgrade
    print("2. PREMIUM UPGRADE:")
    print("   State: ACTIVE (unchanged)")
    print("   Tier: UNLOCK → PREMIUM (payment)")
    print()
    
    # Example 3: Check transitions
    print("3. VALID TRANSITIONS:")
    current = UserState.REGISTERED
    valid = StateTransitions.get_valid_next_states(current)
    print(f"   From {current}: {[s.value for s in valid]}")
