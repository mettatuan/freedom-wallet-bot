"""
🧪 COMPREHENSIVE TEST SUITE - State Machine
============================================

Tests all state transitions, tier upgrades, and referral logic
for the unified state and tier system.

Author: Freedom Wallet Team
Version: 2.0
Date: 2026-02-17
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from app.core.state_machine import StateManager, UserState
from app.core.unified_states import (
    SubscriptionTier,
    StateTransitions,
    TierTransitions,
    UserProfile
)
from app.utils.database import SessionLocal, User


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def db_session():
    """Provide a clean database session for each test"""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_user(db_session):
    """Create a sample registered user"""
    user = User(
        id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone="0901234567",
        user_state="REGISTERED",
        subscription_tier="FREE",
        referral_count=0,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def vip_user(db_session):
    """Create a VIP user (2+ referrals)"""
    user = User(
        id=987654321,
        username="vipuser",
        first_name="VIP",
        last_name="User",
        email="vip@example.com",
        phone="0909876543",
        user_state="VIP",
        subscription_tier="UNLOCK",
        referral_count=3,
        is_free_unlocked=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def legacy_user(db_session):
    """Create a legacy user (no user_state set)"""
    user = User(
        id=111222333,
        username="legacyuser",
        first_name="Legacy",
        last_name="User",
        email="legacy@example.com",
        phone="0901112233",
        user_state="LEGACY",  # Or NULL in real DB
        subscription_tier="FREE",
        referral_count=5,
        is_free_unlocked=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    return user


# ============================================================================
# UNIT TESTS - State Transitions
# ============================================================================

class TestStateTransitions:
    """Test state transition validation and logic"""
    
    def test_visitor_to_registered_valid(self, db_session, sample_user):
        """Test: VISITOR can transition to REGISTERED"""
        # Setup: User in VISITOR state
        sample_user.user_state = "VISITOR"
        db_session.commit()
        
        # Execute
        mgr = StateManager()
        success, msg = mgr.transition_user(
            sample_user.id,
            UserState.REGISTERED,
            reason="Registration completed"
        )
        
        # Verify
        assert success is True
        assert "REGISTERED" in msg
        
        db_session.refresh(sample_user)
        assert sample_user.user_state == "REGISTERED"
    
    def test_visitor_to_vip_invalid(self, db_session, sample_user):
        """Test: VISITOR cannot skip to VIP directly"""
        sample_user.user_state = "VISITOR"
        db_session.commit()
        
        mgr = StateManager()
        success, msg = mgr.transition_user(
            sample_user.id,
            UserState.VIP
        )
        
        assert success is False
        assert "Invalid transition" in msg
    
    def test_registered_to_vip_valid(self, db_session, sample_user):
        """Test: REGISTERED can transition to VIP (via referrals)"""
        mgr = StateManager()
        success, msg = mgr.transition_user(
            sample_user.id,
            UserState.VIP,
            reason="2+ referrals completed"
        )
        
        assert success is True
        db_session.refresh(sample_user)
        assert sample_user.user_state == "VIP"
    
    def test_vip_to_super_vip_valid(self, db_session, vip_user):
        """Test: VIP can transition to SUPER_VIP (50+ refs)"""
        vip_user.referral_count = 50
        db_session.commit()
        
        mgr = StateManager()
        success, msg = mgr.transition_user(
            vip_user.id,
            UserState.SUPER_VIP,
            reason="50+ referrals milestone"
        )
        
        assert success is True
        db_session.refresh(vip_user)
        assert vip_user.user_state == "SUPER_VIP"
    
    def test_churned_to_active_reactivation(self, db_session, sample_user):
        """Test: CHURNED user can be re-activated"""
        sample_user.user_state = "CHURNED"
        db_session.commit()
        
        mgr = StateManager()
        success, msg = mgr.transition_user(
            sample_user.id,
            UserState.ACTIVE,
            reason="Re-engagement successful"
        )
        
        assert success is True
        db_session.refresh(sample_user)
        assert sample_user.user_state == "ACTIVE"
    
    def test_blocked_is_terminal(self, db_session, sample_user):
        """Test: BLOCKED state is terminal (no way out)"""
        sample_user.user_state = "BLOCKED"
        db_session.commit()
        
        mgr = StateManager()
        success, msg = mgr.transition_user(
            sample_user.id,
            UserState.REGISTERED
        )
        
        assert success is False
        assert "Invalid transition" in msg


# ============================================================================
# UNIT TESTS - Tier System
# ============================================================================

class TestTierSystem:
    """Test subscription tier logic"""
    
    def test_free_tier_properties(self):
        """Test: FREE tier has correct properties"""
        tier = SubscriptionTier.FREE
        
        assert tier.display_name == "Miễn phí"
        assert tier.ai_message_limit == 5
        assert tier.can_setup_sheets is False
        assert tier.has_ai_insights is False
    
    def test_unlock_tier_properties(self):
        """Test: UNLOCK tier has correct properties"""
        tier = SubscriptionTier.UNLOCK
        
        assert tier.display_name == "Đã mở khóa"
        assert tier.ai_message_limit == 20
        assert tier.can_setup_sheets is True
        assert tier.has_ai_insights is False
    
    def test_premium_tier_properties(self):
        """Test: PREMIUM tier has correct properties"""
        tier = SubscriptionTier.PREMIUM
        
        assert tier.display_name == "Premium"
        assert tier.ai_message_limit is None  # Unlimited
        assert tier.can_setup_sheets is True
        assert tier.has_ai_insights is True
    
    def test_free_to_unlock_upgrade_valid(self):
        """Test: FREE can upgrade to UNLOCK"""
        can_upgrade = TierTransitions.can_upgrade(
            SubscriptionTier.FREE,
            SubscriptionTier.UNLOCK
        )
        assert can_upgrade is True
    
    def test_free_to_premium_direct_upgrade_valid(self):
        """Test: FREE can upgrade directly to PREMIUM"""
        can_upgrade = TierTransitions.can_upgrade(
            SubscriptionTier.FREE,
            SubscriptionTier.PREMIUM
        )
        assert can_upgrade is True
    
    def test_premium_cannot_upgrade_further(self):
        """Test: PREMIUM is max tier"""
        can_upgrade = TierTransitions.can_upgrade(
            SubscriptionTier.PREMIUM,
            SubscriptionTier.PREMIUM
        )
        assert can_upgrade is False
    
    def test_premium_to_unlock_downgrade_valid(self):
        """Test: PREMIUM can downgrade to UNLOCK (subscription expired)"""
        can_downgrade = TierTransitions.can_downgrade(
            SubscriptionTier.PREMIUM,
            SubscriptionTier.UNLOCK
        )
        assert can_downgrade is True


# ============================================================================
# UNIT TESTS - Referral Logic
# ============================================================================

class TestReferralLogic:
    """Test referral counting and VIP unlock logic"""
    
    def test_auto_vip_unlock_at_2_refs(self, db_session, sample_user):
        """Test: User auto-unlocks VIP at 2 referrals"""
        # Setup: User with 1 referral
        sample_user.referral_count = 1
        db_session.commit()
        
        # Add 1 more referral
        sample_user.referral_count = 2
        db_session.commit()
        
        # Check auto-upgrade
        mgr = StateManager()
        new_state = mgr.check_and_update_state_by_referrals(sample_user.id)
        
        assert new_state == UserState.VIP
        
        db_session.refresh(sample_user)
        assert sample_user.user_state == "VIP"
    
    def test_no_upgrade_with_1_ref(self, db_session, sample_user):
        """Test: User stays REGISTERED with only 1 referral"""
        sample_user.referral_count = 1
        db_session.commit()
        
        mgr = StateManager()
        new_state = mgr.check_and_update_state_by_referrals(sample_user.id)
        
        # Should not upgrade yet
        assert new_state is None or new_state == UserState.REGISTERED
    
    def test_super_vip_unlock_at_50_refs(self, db_session, vip_user):
        """Test: VIP unlocks SUPER_VIP at 50 referrals"""
        vip_user.referral_count = 50
        db_session.commit()
        
        mgr = StateManager()
        new_state = mgr.check_and_update_state_by_referrals(vip_user.id)
        
        assert new_state == UserState.SUPER_VIP
        
        db_session.refresh(vip_user)
        assert vip_user.user_state == "SUPER_VIP"
    
    def test_advocate_unlock_at_100_refs(self, db_session, vip_user):
        """Test: SUPER_VIP unlocks ADVOCATE at 100 referrals"""
        vip_user.user_state = "SUPER_VIP"
        vip_user.referral_count = 100
        db_session.commit()
        
        mgr = StateManager()
        new_state = mgr.check_and_update_state_by_referrals(vip_user.id)
        
        assert new_state == UserState.ADVOCATE
        
        db_session.refresh(vip_user)
        assert vip_user.user_state == "ADVOCATE"


# ============================================================================
# UNIT TESTS - Legacy User Migration
# ============================================================================

class TestLegacyMigration:
    """Test automatic migration of legacy users"""
    
    def test_legacy_user_inferred_state(self, db_session, legacy_user):
        """Test: LEGACY user state is inferred from referral_count"""
        mgr = StateManager()
        state, is_legacy = mgr.get_user_state(legacy_user.id)
        
        assert is_legacy is True
        # Legacy user has 5 refs, should infer VIP
        assert state == UserState.VIP
    
    def test_legacy_user_auto_migration(self, db_session, legacy_user):
        """Test: LEGACY user auto-migrates on first transition"""
        mgr = StateManager()
        
        # Trigger any transition
        success, msg = mgr.transition_user(
            legacy_user.id,
            UserState.VIP,
            reason="Auto-migration"
        )
        
        assert success is True
        assert "Migrated from LEGACY" in msg
        
        # Verify no longer legacy
        state, is_legacy = mgr.get_user_state(legacy_user.id)
        assert is_legacy is False
        assert state == UserState.VIP
    
    def test_legacy_user_with_0_refs_infers_registered(self, db_session):
        """Test: LEGACY user with 0 refs → REGISTERED"""
        user = User(
            id=444555666,
            username="newlegacy",
            user_state="LEGACY",
            referral_count=0,
            is_free_unlocked=False
        )
        db_session.add(user)
        db_session.commit()
        
        mgr = StateManager()
        state, is_legacy = mgr.get_user_state(user.id)
        
        assert is_legacy is True
        assert state == UserState.REGISTERED


# ============================================================================
# UNIT TESTS - UserProfile Model
# ============================================================================

class TestUserProfile:
    """Test UserProfile dataclass logic"""
    
    def test_can_transition_to_valid(self):
        """Test: UserProfile.can_transition_to() validates correctly"""
        profile = UserProfile(
            user_id=123,
            state=UserState.REGISTERED,
            tier=SubscriptionTier.FREE,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        # Valid transition
        assert profile.can_transition_to(UserState.VIP) is True
        
        # Invalid transition
        assert profile.can_transition_to(UserState.ADVOCATE) is False
    
    def test_can_upgrade_to_valid(self):
        """Test: UserProfile.can_upgrade_to() validates correctly"""
        profile = UserProfile(
            user_id=123,
            state=UserState.ACTIVE,
            tier=SubscriptionTier.FREE,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        # Valid upgrade
        assert profile.can_upgrade_to(SubscriptionTier.UNLOCK) is True
        
        # Invalid upgrade (already at max)
        profile.tier = SubscriptionTier.PREMIUM
        assert profile.can_upgrade_to(SubscriptionTier.PREMIUM) is False
    
    def test_is_premium_active_with_valid_expiry(self):
        """Test: Premium is active if not expired"""
        profile = UserProfile(
            user_id=123,
            state=UserState.ACTIVE,
            tier=SubscriptionTier.PREMIUM,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            premium_expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        assert profile.is_premium_active() is True
    
    def test_is_premium_inactive_if_expired(self):
        """Test: Premium is inactive if expired"""
        profile = UserProfile(
            user_id=123,
            state=UserState.ACTIVE,
            tier=SubscriptionTier.PREMIUM,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            premium_expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
        )
        
        assert profile.is_premium_active() is False
    
    def test_should_unlock_with_2_refs(self):
        """Test: User should unlock with 2+ referrals"""
        profile = UserProfile(
            user_id=123,
            state=UserState.REGISTERED,
            tier=SubscriptionTier.FREE,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            referral_count=2
        )
        
        assert profile.should_unlock() is True


# ============================================================================
# INTEGRATION TEST - Complete Flow
# ============================================================================

class TestCompleteStateFlow:
    """Test complete user journey through states"""
    
    def test_visitor_to_advocate_flow(self, db_session):
        """
        Test complete flow:
        VISITOR → REGISTERED → ACTIVE → VIP → SUPER_VIP → ADVOCATE
        """
        # Create new user
        user = User(
            id=999888777,
            username="flowtest",
            user_state="VISITOR",
            subscription_tier="FREE",
            referral_count=0
        )
        db_session.add(user)
        db_session.commit()
        
        mgr = StateManager()
        
        # Step 1: VISITOR → REGISTERED
        success, _ = mgr.transition_user(user.id, UserState.REGISTERED)
        assert success is True
        
        # Step 2: Complete setup → ACTIVE
        user.subscription_tier = "UNLOCK"
        db_session.commit()
        success, _ = mgr.transition_user(user.id, UserState.ACTIVE)
        assert success is True
        
        # Step 3: Get 2 referrals → VIP
        user.referral_count = 2
        db_session.commit()
        new_state = mgr.check_and_update_state_by_referrals(user.id)
        assert new_state == UserState.VIP
        
        # Step 4: Get 50 referrals → SUPER_VIP
        user.referral_count = 50
        db_session.commit()
        new_state = mgr.check_and_update_state_by_referrals(user.id)
        assert new_state == UserState.SUPER_VIP
        
        # Step 5: Get 100 referrals → ADVOCATE
        user.referral_count = 100
        db_session.commit()
        new_state = mgr.check_and_update_state_by_referrals(user.id)
        assert new_state == UserState.ADVOCATE
        
        # Verify final state
        db_session.refresh(user)
        assert user.user_state == "ADVOCATE"
        assert user.referral_count == 100


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
