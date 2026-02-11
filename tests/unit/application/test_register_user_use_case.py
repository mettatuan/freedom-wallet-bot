"""Unit tests for RegisterUserUseCase."""

import pytest
from decimal import Decimal
from unittest.mock import Mock, AsyncMock

from src.application.use_cases.register_user import RegisterUserUseCase
from src.application.dtos import RegisterUserInput
from src.domain.entities.user import User
from src.domain.entities.subscription import Subscription
from src.domain.value_objects.user_tier import UserTier


class TestRegisterUserUseCase:
    """Test suite for RegisterUserUseCase."""
    
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
        return RegisterUserUseCase(user_repository, subscription_repository)
    
    @pytest.mark.asyncio
    async def test_register_new_user(self, use_case, user_repository, subscription_repository):
        """Test registering a new user."""
        # Arrange
        input_data = RegisterUserInput(
            telegram_user_id=123,
            telegram_username="testuser"
        )
        
        user_repository.get_by_telegram_id = AsyncMock(return_value=None)
        user_repository.save = AsyncMock(return_value=User(
            user_id=123,
            telegram_username="testuser",
            tier=UserTier.FREE
        ))
        
        subscription_repository.save = AsyncMock(return_value=Subscription.create_free_subscription(123))
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_success()
        assert result.data.is_new_user is True
        assert result.data.user.user_id == 123
        assert result.data.user.tier == UserTier.FREE
        assert result.data.subscription.tier == UserTier.FREE
        assert result.data.subscription.expires_at is None
        
        user_repository.save.assert_called_once()
        subscription_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_existing_user(self, use_case, user_repository, subscription_repository):
        """Test registering an existing user (idempotent)."""
        # Arrange
        existing_user = User(user_id=123, telegram_username="testuser", tier=UserTier.UNLOCK)
        existing_subscription = Subscription.create_unlock_subscription(123)
        
        input_data = RegisterUserInput(
            telegram_user_id=123,
            telegram_username="testuser"
        )
        
        user_repository.get_by_telegram_id = AsyncMock(return_value=existing_user)
        subscription_repository.get_by_user_id = AsyncMock(return_value=existing_subscription)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_success()
        assert result.data.is_new_user is False
        assert result.data.user.tier == UserTier.UNLOCK
        
        user_repository.save.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_register_with_valid_email(self, use_case, user_repository, subscription_repository):
        """Test registering with valid email."""
        # Arrange
        input_data = RegisterUserInput(
            telegram_user_id=123,
            telegram_username="testuser",
            email="test@example.com"
        )
        
        user_repository.get_by_telegram_id = AsyncMock(return_value=None)
        user_repository.save = AsyncMock(return_value=User(
            user_id=123,
            email="test@example.com",
            tier=UserTier.FREE
        ))
        subscription_repository.save = AsyncMock(return_value=Subscription.create_free_subscription(123))
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_success()
        assert result.data.user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_register_with_invalid_email(self, use_case, user_repository):
        """Test registering with invalid email."""
        # Arrange
        input_data = RegisterUserInput(
            telegram_user_id=123,
            email="invalid-email"
        )
        
        user_repository.get_by_telegram_id = AsyncMock(return_value=None)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "INVALID_EMAIL"
        assert "Invalid email" in result.error_message
    
    @pytest.mark.asyncio
    async def test_register_with_valid_phone(self, use_case, user_repository, subscription_repository):
        """Test registering with valid phone."""
        # Arrange
        input_data = RegisterUserInput(
            telegram_user_id=123,
            phone="0901234567"
        )
        
        user_repository.get_by_telegram_id = AsyncMock(return_value=None)
        user_repository.save = AsyncMock(return_value=User(
            user_id=123,
            phone="+84901234567",
            tier=UserTier.FREE
        ))
        subscription_repository.save = AsyncMock(return_value=Subscription.create_free_subscription(123))
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_success()
        assert result.data.user.phone == "+84901234567"
    
    @pytest.mark.asyncio
    async def test_register_with_invalid_phone(self, use_case, user_repository):
        """Test registering with invalid phone."""
        # Arrange
        input_data = RegisterUserInput(
            telegram_user_id=123,
            phone="123"
        )
        
        user_repository.get_by_telegram_id = AsyncMock(return_value=None)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "INVALID_PHONE"
        assert "Invalid phone" in result.error_message
