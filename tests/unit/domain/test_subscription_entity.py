"""Unit tests for Subscription entity."""

import pytest
from datetime import datetime, timedelta

from src.domain.entities.subscription import Subscription
from src.domain.value_objects.user_tier import UserTier


class TestSubscriptionEntity:
    """Test suite for Subscription entity."""
    
    def test_create_free_subscription(self):
        """Test creating a FREE subscription."""
        sub = Subscription.create_free_subscription(user_id=123)
        
        assert sub.user_id == 123
        assert sub.tier == UserTier.FREE
        assert sub.expires_at is None
        assert sub.is_active()
        assert not sub.is_expired()
        assert sub.days_until_expiry() is None
    
    def test_create_unlock_subscription(self):
        """Test creating an UNLOCK subscription."""
        sub = Subscription.create_unlock_subscription(user_id=123)
        
        assert sub.user_id == 123
        assert sub.tier == UserTier.UNLOCK
        assert sub.expires_at is not None
        assert sub.is_active()
        assert not sub.is_expired()
        
        # Should expire in 30 days
        days_left = sub.days_until_expiry()
        assert days_left >= 29 and days_left <= 30
    
    def test_create_premium_subscription(self):
        """Test creating a PREMIUM subscription."""
        expires_at = datetime.utcnow() + timedelta(days=30)
        sub = Subscription.create_premium_subscription(user_id=123, expires_at=expires_at)
        
        assert sub.user_id == 123
        assert sub.tier == UserTier.PREMIUM
        assert sub.expires_at == expires_at
        assert sub.auto_renew is True
        assert sub.last_payment_at is not None
        assert sub.is_active()
    
    def test_free_subscription_never_expires(self):
        """Test that FREE subscription never expires."""
        sub = Subscription.create_free_subscription(user_id=123)
        
        assert sub.is_active()
        assert not sub.is_expired()
        assert not sub.is_in_grace_period()
        assert sub.days_until_expiry() is None
    
    def test_subscription_is_active(self):
        """Test is_active for various states."""
        # Active subscription
        active_sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() + timedelta(days=10)
        )
        assert active_sub.is_active()
        
        # Expired subscription
        expired_sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() - timedelta(days=10)
        )
        assert not expired_sub.is_active()
    
    def test_subscription_grace_period(self):
        """Test grace period (3 days after expiry)."""
        # Just expired (in grace period)
        in_grace = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        assert not in_grace.is_active()
        assert in_grace.is_in_grace_period()
        assert not in_grace.is_expired()
        
        # Past grace period
        past_grace = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() - timedelta(days=5)
        )
        assert not past_grace.is_active()
        assert not past_grace.is_in_grace_period()
        assert past_grace.is_expired()
    
    def test_days_until_expiry(self):
        """Test days_until_expiry calculation."""
        # 10 days left
        sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() + timedelta(days=10)
        )
        days_left = sub.days_until_expiry()
        # Allow 9 or 10 due to timing precision
        assert days_left in [9, 10]
        
        # Already expired
        expired_sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() - timedelta(days=5)
        )
        assert expired_sub.days_until_expiry() == 0
    
    def test_can_renew(self):
        """Test can_renew logic."""
        # Can renew if 7 days or less left
        can_renew_sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() + timedelta(days=5)
        )
        assert can_renew_sub.can_renew()
        
        # Cannot renew if more than 7 days left
        cannot_renew_sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() + timedelta(days=20)
        )
        assert not cannot_renew_sub.can_renew()
        
        # FREE tier cannot renew
        free_sub = Subscription.create_free_subscription(user_id=123)
        assert not free_sub.can_renew()
    
    def test_renew_subscription(self):
        """Test renewing a subscription."""
        # Create subscription expiring in 5 days
        sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() + timedelta(days=5)
        )
        
        original_expiry = sub.expires_at
        sub.renew(duration_days=30)
        
        # Should extend by 30 days from original expiry
        expected_expiry = original_expiry + timedelta(days=30)
        assert (sub.expires_at - expected_expiry).total_seconds() < 1
        assert sub.last_payment_at is not None
    
    def test_renew_expired_subscription(self):
        """Test renewing an expired subscription."""
        # Create expired subscription
        sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() - timedelta(days=10)
        )
        
        sub.renew(duration_days=30)
        
        # Should start from now
        expected_expiry = datetime.utcnow() + timedelta(days=30)
        assert (sub.expires_at - expected_expiry).total_seconds() < 1
    
    def test_cannot_renew_free_subscription(self):
        """Test that FREE subscription cannot be renewed."""
        sub = Subscription.create_free_subscription(user_id=123)
        
        with pytest.raises(ValueError, match="FREE tier subscription cannot be renewed"):
            sub.renew()
    
    def test_expire_subscription(self):
        """Test manually expiring a subscription."""
        sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        assert sub.is_active()
        
        sub.expire()
        
        assert not sub.is_active()
        assert (datetime.utcnow() - sub.expires_at).total_seconds() < 1
    
    def test_cannot_expire_free_subscription(self):
        """Test that FREE subscription cannot be expired."""
        sub = Subscription.create_free_subscription(user_id=123)
        
        with pytest.raises(ValueError, match="Cannot expire FREE tier subscription"):
            sub.expire()
    
    def test_subscription_string_representation(self):
        """Test __str__ and __repr__ methods."""
        sub = Subscription(
            user_id=123,
            tier=UserTier.UNLOCK,
            expires_at=datetime.utcnow() + timedelta(days=10)
        )
        
        str_repr = str(sub)
        assert "123" in str_repr
        assert "UNLOCK" in str_repr
        assert "active" in str_repr
