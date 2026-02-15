"""
🎯 STATE MACHINE MANAGER
========================

Manages user state transitions with DUAL-RUN strategy for Week 2 soft-integration.

Strategy:
- LEGACY users: Use existing referral_count logic (backward compatible)
- NEW users: Use state machine with proper transitions
- Gradually migrate LEGACY → new states as they interact

Author: Freedom Wallet Team
Version: 2.0 (Week 2 - Soft Integration)
Date: 2026-02-08
"""

from enum import Enum
from typing import Optional, Tuple
from datetime import datetime
from app.utils.database import SessionLocal, User
import logging

logger = logging.getLogger(__name__)


class UserState(str, Enum):
    """User states - simplified for Week 2"""
    LEGACY = "LEGACY"  # Old users, not yet migrated
    VISITOR = "VISITOR"  # Just clicked link
    REGISTERED = "REGISTERED"  # Signed up, 0-1 refs
    VIP = "VIP"  # 2+ refs, unlocked FREE tier
    SUPER_VIP = "SUPER_VIP"  # 50+ refs (Week 3)
    ADVOCATE = "ADVOCATE"  # 100+ refs (Week 4)
    CHURNED = "CHURNED"  # Inactive 90+ days


class StateManager:
    """
    Central state management with fallback logic
    
    Usage:
        state_mgr = StateManager()
        state_mgr.get_user_state(user_id)  # Safe, handles LEGACY
        state_mgr.transition_user(user_id, UserState.VIP)
    """
    
    # Valid state transitions (Week 2: only core states)
    VALID_TRANSITIONS = {
        UserState.LEGACY: {UserState.VISITOR, UserState.REGISTERED, UserState.VIP},
        UserState.VISITOR: {UserState.REGISTERED, UserState.CHURNED},
        UserState.REGISTERED: {UserState.VIP, UserState.CHURNED},
        UserState.VIP: {UserState.SUPER_VIP, UserState.CHURNED},
        UserState.SUPER_VIP: {UserState.ADVOCATE, UserState.VIP, UserState.CHURNED},  # Week 4: Allow decay to VIP
        UserState.ADVOCATE: {UserState.CHURNED},
        UserState.CHURNED: {UserState.REGISTERED},  # Re-activation
    }
    
    def __init__(self):
        self.session = SessionLocal()
    
    def get_user_state(self, user_id: int) -> Tuple[UserState, bool]:
        """
        Get user state with LEGACY detection
        
        Returns:
            (state, is_legacy) - Tuple of state and whether it's from legacy logic
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return (UserState.VISITOR, False)
        
        # Check if user is LEGACY
        if user.user_state == "LEGACY":
            # Fallback to old logic
            legacy_state = self._infer_legacy_state(user)
            return (legacy_state, True)
        
        # Use new state machine
        try:
            return (UserState(user.user_state), False)
        except ValueError:
            logger.warning(f"Invalid state '{user.user_state}' for user {user_id}, falling back to LEGACY")
            return (self._infer_legacy_state(user), True)
    
    def _infer_legacy_state(self, user: User) -> UserState:
        """
        Infer state from old referral_count logic (backward compatible)
        
        Old logic:
        - referral_count >= 2 → VIP
        - referral_count < 2 → REGISTERED
        """
        if user.is_free_unlocked or user.referral_count >= 2:
            return UserState.VIP
        elif user.referral_count >= 1 or user.is_registered:
            return UserState.REGISTERED
        else:
            return UserState.VISITOR
    
    def transition_user(
        self, 
        user_id: int, 
        new_state: UserState,
        reason: Optional[str] = None,
        auto_migrate_legacy: bool = True
    ) -> Tuple[bool, str]:
        """
        Transition user to new state with validation
        
        Args:
            user_id: Telegram user ID
            new_state: Target state
            reason: Optional reason for transition (for logging)
            auto_migrate_legacy: If True, automatically migrate LEGACY users
        
        Returns:
            (success, message) - Tuple of success status and message
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return (False, "User not found")
        
        current_state, is_legacy = self.get_user_state(user_id)
        
        # Auto-migrate LEGACY users on first transition
        if is_legacy and auto_migrate_legacy:
            logger.info(f"Auto-migrating LEGACY user {user_id} from inferred {current_state} → {new_state}")
            user.user_state = new_state.value
            self.session.commit()
            return (True, f"Migrated from LEGACY → {new_state.value}")
        
        # Validate transition
        if new_state not in self.VALID_TRANSITIONS.get(current_state, set()):
            return (False, f"Invalid transition: {current_state.value} → {new_state.value}")
        
        # Perform transition
        old_state = current_state.value
        user.user_state = new_state.value
        self.session.commit()
        
        log_msg = f"State transition: {old_state} → {new_state.value}"
        if reason:
            log_msg += f" (reason: {reason})"
        logger.info(f"User {user_id}: {log_msg}")
        
        return (True, log_msg)
    
    def check_and_update_state_by_referrals(self, user_id: int) -> Optional[UserState]:
        """
        Auto-update state based on referral milestones (Week 2 compatible)
        
        This maintains backward compatibility with existing referral logic:
        - 2+ refs → VIP
        - 50+ refs → SUPER_VIP (Week 4)
        
        Returns:
            New state if changed, None if no change
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        current_state, _ = self.get_user_state(user_id)
        new_state = None
        
        # Referral-based state upgrades
        if user.referral_count >= 50 and current_state in [UserState.VIP, UserState.REGISTERED]:
            new_state = UserState.SUPER_VIP
            # Update activity timestamp when promoted to Super VIP
            user.super_vip_last_active = datetime.utcnow()
        elif user.referral_count >= 2 and current_state in [UserState.REGISTERED, UserState.VISITOR, UserState.LEGACY]:
            new_state = UserState.VIP
        
        if new_state:
            success, msg = self.transition_user(
                user_id, 
                new_state, 
                reason=f"Reached {user.referral_count} referrals"
            )
            if success:
                return new_state
        
        return None
    
    def update_super_vip_activity(self, user_id: int) -> bool:
        """
        Update last active timestamp for Super VIP users
        
        This is used for decay monitoring (Week 4):
        - Track activity to prevent auto-downgrade
        - Called on every significant user interaction
        
        Returns:
            True if updated successfully, False otherwise
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        current_state, _ = self.get_user_state(user_id)
        
        # Only track for Super VIP users
        if current_state == UserState.SUPER_VIP:
            user.super_vip_last_active = datetime.utcnow()
            user.super_vip_decay_warned = False  # Reset warning flag
            self.session.commit()
            logger.debug(f"Updated Super VIP activity for user {user_id}")
            return True
        
        return False
    
    def check_super_vip_decay(self, user_id: int) -> Optional[dict]:
        """
        Check if Super VIP user needs decay warning or downgrade
        
        Decay rules (Week 4):
        - 7 days inactive: Send warning (once)
        - 14 days inactive: Auto-downgrade to VIP
        
        Returns:
            dict with 'action' and 'days_inactive' if action needed, None otherwise
            action can be: 'warn' or 'downgrade'
        """
        user = self.session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        current_state, _ = self.get_user_state(user_id)
        
        # Only check Super VIP users
        if current_state != UserState.SUPER_VIP:
            return None
        
        # Check last active timestamp
        if not user.super_vip_last_active:
            # No timestamp yet, set it now
            user.super_vip_last_active = datetime.utcnow()
            self.session.commit()
            return None
        
        # Calculate days inactive
        now = datetime.utcnow()
        time_inactive = now - user.super_vip_last_active
        days_inactive = time_inactive.days
        
        # Check for downgrade (14+ days)
        if days_inactive >= 14:
            # Downgrade to VIP
            success, msg = self.transition_user(
                user_id,
                UserState.VIP,
                reason=f"Inactive for {days_inactive} days (Super VIP decay)"
            )
            
            if success:
                user.super_vip_decay_warned = False  # Reset flag
                self.session.commit()
                logger.info(f"🔻 Super VIP decay: User {user_id} downgraded to VIP ({days_inactive} days inactive)")
                return {'action': 'downgrade', 'days_inactive': days_inactive}
        
        # Check for warning (7+ days, not warned yet)
        elif days_inactive >= 7 and not user.super_vip_decay_warned:
            user.super_vip_decay_warned = True
            self.session.commit()
            logger.info(f"⚠️ Super VIP decay warning: User {user_id} ({days_inactive} days inactive)")
            return {'action': 'warn', 'days_inactive': days_inactive}
        
        return None
    
    def check_all_super_vip_decay(self) -> list:
        """
        Check all Super VIP users for decay
        
        Returns:
            List of dicts with user_id and decay action
            [{'user_id': 123, 'action': 'warn', 'days_inactive': 8}, ...]
        """
        # Get all Super VIP users
        super_vip_users = self.session.query(User).filter(
            User.user_state == UserState.SUPER_VIP.value
        ).all()
        
        results = []
        for user in super_vip_users:
            decay_info = self.check_super_vip_decay(user.id)
            if decay_info:
                results.append({
                    'user_id': user.id,
                    'username': user.username or user.full_name,
                    **decay_info
                })
        
        return results
    
    def get_state_display_name(self, state: UserState) -> str:
        """Get user-friendly state name (Vietnamese)"""
        display_names = {
            UserState.LEGACY: "🔄 Người dùng cũ",
            UserState.VISITOR: "👋 Khách",
            UserState.REGISTERED: "📝 Đã đăng ký",
            UserState.VIP: "⭐ VIP",
            UserState.SUPER_VIP: "🌟 Super VIP",
            UserState.ADVOCATE: "👑 Advocate",
            UserState.CHURNED: "😴 Không hoạt động",
        }
        return display_names.get(state, state.value)
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_state_safe(user_id: int) -> UserState:
    """
    Convenience function to get user state safely
    
    Usage:
        from app.core.state_machine import get_user_state_safe
        state = get_user_state_safe(user_id)
    """
    with StateManager() as mgr:
        state, _ = mgr.get_user_state(user_id)
        return state


def transition_user_safe(user_id: int, new_state: UserState, reason: str = None) -> bool:
    """
    Convenience function to transition user safely
    
    Usage:
        from app.core.state_machine import transition_user_safe, UserState
        success = transition_user_safe(user_id, UserState.VIP, "Unlocked 2 refs")
    """
    with StateManager() as mgr:
        success, msg = mgr.transition_user(user_id, new_state, reason)
        if not success:
            logger.warning(f"Failed to transition user {user_id}: {msg}")
        return success


def check_referral_milestone(user_id: int) -> Optional[UserState]:
    """
    Check if user reached referral milestone and auto-upgrade state
    
    Usage:
        from app.core.state_machine import check_referral_milestone
        new_state = check_referral_milestone(user_id)
        if new_state:
            # User upgraded to new_state
    """
    with StateManager() as mgr:
        return mgr.check_and_update_state_by_referrals(user_id)

