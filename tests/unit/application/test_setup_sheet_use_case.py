"""Unit tests for SetupSheetUseCase."""

import pytest
from unittest.mock import Mock, AsyncMock

from src.application.use_cases.setup_sheet import SetupSheetUseCase
from src.application.dtos import SetupSheetInput
from src.domain.entities.user import User
from src.domain.value_objects.user_tier import UserTier


class TestSetupSheetUseCase:
    """Test suite for SetupSheetUseCase."""
    
    @pytest.fixture
    def user_repository(self):
        """Mock user repository."""
        return Mock()
    
    @pytest.fixture
    def subscription_repository(self):
        """Mock subscription repository."""
        return Mock()
    
    @pytest.fixture
    def use_case(self, user_repository, subscription_repository):
        """Create use case instance."""
        return SetupSheetUseCase(user_repository, subscription_repository)
    
    @pytest.mark.asyncio
    async def test_setup_sheet_success(self, use_case, user_repository, subscription_repository):
        """Test successful sheet setup."""
        # Arrange
        free_user = User(user_id=123, tier=UserTier.FREE)
        
        input_data = SetupSheetInput(
            user_id=123,
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        
        user_repository.get_by_id = AsyncMock(return_value=free_user)
        user_repository.save = AsyncMock(side_effect=lambda u: u)
        subscription_repository.save = AsyncMock(side_effect=lambda s: s)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_success()
        assert result.data.upgraded_to_unlock is True
        assert result.data.user.tier == UserTier.UNLOCK
        assert result.data.user.sheet_url == input_data.sheet_url
        assert result.data.user.webapp_url == input_data.webapp_url
        assert result.data.subscription.tier == UserTier.UNLOCK
        assert result.data.subscription.days_until_expiry in [29, 30]
        
        user_repository.save.assert_called_once()
        subscription_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_setup_sheet_user_not_found(self, use_case, user_repository):
        """Test sheet setup with non-existent user."""
        # Arrange
        input_data = SetupSheetInput(
            user_id=999,
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        
        user_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "USER_NOT_FOUND"
        assert "not found" in result.error_message
    
    @pytest.mark.asyncio
    async def test_setup_sheet_invalid_tier(self, use_case, user_repository):
        """Test sheet setup for non-FREE tier user."""
        # Arrange
        unlock_user = User(user_id=123, tier=UserTier.UNLOCK)
        
        input_data = SetupSheetInput(
            user_id=123,
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        
        user_repository.get_by_id = AsyncMock(return_value=unlock_user)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "INVALID_TIER"
        assert "already UNLOCK" in result.error_message
    
    @pytest.mark.asyncio
    async def test_setup_sheet_missing_sheet_url(self, use_case, user_repository):
        """Test sheet setup with missing sheet URL."""
        # Arrange
        free_user = User(user_id=123, tier=UserTier.FREE)
        
        input_data = SetupSheetInput(
            user_id=123,
            sheet_url="",
            webapp_url="https://script.google.com/macros/s/xyz789/exec"
        )
        
        user_repository.get_by_id = AsyncMock(return_value=free_user)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "MISSING_SHEET_URL"
    
    @pytest.mark.asyncio
    async def test_setup_sheet_missing_webapp_url(self, use_case, user_repository):
        """Test sheet setup with missing webapp URL."""
        # Arrange
        free_user = User(user_id=123, tier=UserTier.FREE)
        
        input_data = SetupSheetInput(
            user_id=123,
            sheet_url="https://docs.google.com/spreadsheets/d/abc123",
            webapp_url=""
        )
        
        user_repository.get_by_id = AsyncMock(return_value=free_user)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "MISSING_WEBAPP_URL"
