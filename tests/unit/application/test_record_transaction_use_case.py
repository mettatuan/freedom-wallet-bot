"""Unit tests for RecordTransactionUseCase."""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, AsyncMock

from src.application.use_cases.record_transaction import RecordTransactionUseCase
from src.application.dtos import RecordTransactionInput
from src.domain.entities.user import User
from src.domain.value_objects.user_tier import UserTier


class TestRecordTransactionUseCase:
    """Test suite for RecordTransactionUseCase."""
    
    @pytest.fixture
    def user_repository(self):
        """Mock user repository."""
        return Mock()
    
    @pytest.fixture
    def transaction_repository(self):
        """Mock transaction repository."""
        return Mock()
    
    @pytest.fixture
    def use_case(self, user_repository, transaction_repository):
        """Create use case instance."""
        return RecordTransactionUseCase(user_repository, transaction_repository)
    
    @pytest.mark.asyncio
    async def test_record_income_transaction(self, use_case, user_repository, transaction_repository):
        """Test recording an income transaction."""
        # Arrange
        user = User(user_id=123, tier=UserTier.UNLOCK)
        
        input_data = RecordTransactionInput(
            user_id=123,
            amount=Decimal("50000"),
            category="Lương",
            note="Lương tháng 2"
        )
        
        user_repository.get_by_id = AsyncMock(return_value=user)
        transaction_repository.save = AsyncMock(side_effect=lambda t: t)
        transaction_repository.get_income_total = AsyncMock(return_value=Decimal("50000"))
        transaction_repository.get_expense_total = AsyncMock(return_value=Decimal("0"))
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_success()
        assert result.data.transaction.amount == Decimal("50000")
        assert result.data.transaction.category == "Lương"
        assert result.data.transaction.note == "Lương tháng 2"
        assert result.data.transaction.formatted_amount == "+50.000đ"
        assert result.data.balance == Decimal("50000")
        
        transaction_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_record_expense_transaction(self, use_case, user_repository, transaction_repository):
        """Test recording an expense transaction."""
        # Arrange
        user = User(user_id=123, tier=UserTier.UNLOCK)
        
        input_data = RecordTransactionInput(
            user_id=123,
            amount=Decimal("-20000"),
            category="Ăn uống"
        )
        
        user_repository.get_by_id = AsyncMock(return_value=user)
        transaction_repository.save = AsyncMock(side_effect=lambda t: t)
        transaction_repository.get_income_total = AsyncMock(return_value=Decimal("100000"))
        transaction_repository.get_expense_total = AsyncMock(return_value=Decimal("20000"))
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_success()
        assert result.data.transaction.amount == Decimal("-20000")
        assert result.data.transaction.category == "Ăn uống"
        assert result.data.balance == Decimal("80000")
    
    @pytest.mark.asyncio
    async def test_record_transaction_user_not_found(self, use_case, user_repository):
        """Test recording transaction for non-existent user."""
        # Arrange
        input_data = RecordTransactionInput(
            user_id=999,
            amount=Decimal("50000"),
            category="Lương"
        )
        
        user_repository.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "USER_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_record_transaction_zero_amount(self, use_case, user_repository):
        """Test recording transaction with zero amount."""
        # Arrange
        user = User(user_id=123, tier=UserTier.UNLOCK)
        
        input_data = RecordTransactionInput(
            user_id=123,
            amount=Decimal("0"),
            category="Test"
        )
        
        user_repository.get_by_id = AsyncMock(return_value=user)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "INVALID_TRANSACTION"
        assert "cannot be zero" in result.error_message
    
    @pytest.mark.asyncio
    async def test_record_transaction_empty_category(self, use_case, user_repository):
        """Test recording transaction with empty category."""
        # Arrange
        user = User(user_id=123, tier=UserTier.UNLOCK)
        
        input_data = RecordTransactionInput(
            user_id=123,
            amount=Decimal("50000"),
            category=""
        )
        
        user_repository.get_by_id = AsyncMock(return_value=user)
        
        # Act
        result = await use_case.execute(input_data)
        
        # Assert
        assert result.is_failure()
        assert result.error_code == "INVALID_TRANSACTION"
        assert "Category is required" in result.error_message
