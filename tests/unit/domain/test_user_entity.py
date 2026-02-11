"""Unit tests for User entity."""

import pytest
from datetime import datetime

from src.domain.entities.user import User
from src.domain.value_objects.user_tier import UserTier


class TestUserEntity:
    """Test suite for User entity."""
    
    def test_create_free_user(self):
        """Test creating a FREE tier user."""
        user = User(user_id=123, telegram_username="testuser")
        
        assert user.user_id == 123
        assert user.telegram_username == "testuser"
        assert user.tier == UserTier.FREE
        assert user.is_free()
        assert not user.is_unlock()
        assert not user.is_premium()
    
    def test_upgrade_free_to_unlock(self):
        """Test upgrading from FREE to UNLOCK."""
        user = User(user_id=123)
        
        user.upgrade_to_unlock(
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        
        assert user.tier == UserTier.UNLOCK
        assert user.is_unlock()
        assert user.sheet_url == "https://docs.google.com/spreadsheets/d/abc123"
        assert user.webapp_url == "https://script.google.com/macros/s/xyz789/exec"
        assert user.has_sheet_setup()
    
    def test_upgrade_to_unlock_requires_urls(self):
        """Test that upgrade to UNLOCK requires both URLs."""
        user = User(user_id=123)
        
        with pytest.raises(ValueError, match="Sheet URL and Web App URL are required"):
            user.upgrade_to_unlock(sheet_url="", webapp_url="")
    
    def test_cannot_upgrade_to_unlock_from_premium(self):
        """Test that PREMIUM user cannot upgrade to UNLOCK."""
        user = User(user_id=123, tier=UserTier.PREMIUM)
        
        with pytest.raises(ValueError, match="Cannot upgrade to UNLOCK from PREMIUM"):
            user.upgrade_to_unlock(
                sheet_url="https://docs.google.com/spreadsheets/d/abc123",
                webapp_url="https://script.google.com/macros/s/xyz789/exec"
            )
    
    def test_upgrade_unlock_to_premium(self):
        """Test upgrading from UNLOCK to PREMIUM."""
        user = User(
            user_id=123,
            tier=UserTier.UNLOCK,
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        
        user.upgrade_to_premium()
        
        assert user.tier == UserTier.PREMIUM
        assert user.is_premium()
        assert user.can_use_quick_record()
    
    def test_cannot_upgrade_to_premium_from_free(self):
        """Test that FREE user cannot upgrade directly to PREMIUM."""
        user = User(user_id=123)
        
        with pytest.raises(ValueError, match="Cannot upgrade to PREMIUM from FREE"):
            user.upgrade_to_premium()
    
    def test_downgrade_premium_to_unlock(self):
        """Test downgrading from PREMIUM to UNLOCK."""
        user = User(
            user_id=123,
            tier=UserTier.PREMIUM,
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        
        user.downgrade_to_unlock()
        
        assert user.tier == UserTier.UNLOCK
        assert user.is_unlock()
        assert not user.can_use_quick_record()
    
    def test_cannot_downgrade_to_unlock_without_sheet(self):
        """Test that downgrade to UNLOCK requires sheet setup."""
        user = User(user_id=123, tier=UserTier.PREMIUM)
        
        with pytest.raises(ValueError, match="Cannot downgrade: Sheet setup is required"):
            user.downgrade_to_unlock()
    
    def test_downgrade_unlock_to_free(self):
        """Test downgrading from UNLOCK to FREE."""
        user = User(
            user_id=123,
            tier=UserTier.UNLOCK,
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        
        user.downgrade_to_free()
        
        assert user.tier == UserTier.FREE
        assert user.is_free()
        assert user.sheet_url is None
        assert user.webapp_url is None
        assert not user.has_sheet_setup()
    
    def test_cannot_downgrade_to_free_from_premium(self):
        """Test that PREMIUM user cannot downgrade directly to FREE."""
        user = User(user_id=123, tier=UserTier.PREMIUM)
        
        with pytest.raises(ValueError, match="Cannot downgrade to FREE from PREMIUM"):
            user.downgrade_to_free()
    
    def test_quick_record_only_for_premium(self):
        """Test that Quick Record is only available for PREMIUM."""
        free_user = User(user_id=1, tier=UserTier.FREE)
        unlock_user = User(user_id=2, tier=UserTier.UNLOCK)
        premium_user = User(user_id=3, tier=UserTier.PREMIUM)
        
        assert not free_user.can_use_quick_record()
        assert not unlock_user.can_use_quick_record()
        assert premium_user.can_use_quick_record()
    
    def test_can_upgrade_to_unlock(self):
        """Test can_upgrade_to_unlock logic."""
        free_user = User(user_id=1, tier=UserTier.FREE)
        unlock_user = User(user_id=2, tier=UserTier.UNLOCK)
        
        assert free_user.can_upgrade_to_unlock()
        assert not unlock_user.can_upgrade_to_unlock()
    
    def test_can_upgrade_to_premium(self):
        """Test can_upgrade_to_premium logic."""
        unlock_with_sheet = User(
            user_id=1,
            tier=UserTier.UNLOCK,
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        unlock_without_sheet = User(user_id=2, tier=UserTier.UNLOCK)
        
        assert unlock_with_sheet.can_upgrade_to_premium()
        assert not unlock_without_sheet.can_upgrade_to_premium()
    
    def test_user_string_representation(self):
        """Test __str__ and __repr__ methods."""
        user = User(user_id=123, telegram_username="testuser", tier=UserTier.UNLOCK)
        
        str_repr = str(user)
        assert "123" in str_repr
        assert "testuser" in str_repr
        assert "UNLOCK" in str_repr
