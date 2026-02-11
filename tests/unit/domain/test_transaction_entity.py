"""Unit tests for Transaction entity."""

import pytest
from decimal import Decimal
from datetime import datetime

from src.domain.entities.transaction import Transaction


class TestTransactionEntity:
    """Test suite for Transaction entity."""
    
    def test_create_income_transaction(self):
        """Test creating an income transaction."""
        txn = Transaction(
            user_id=123,
            amount=Decimal("50000"),
            category="Lương"
        )
        
        assert txn.user_id == 123
        assert txn.amount == Decimal("50000")
        assert txn.category == "Lương"
        assert txn.is_income()
        assert not txn.is_expense()
    
    def test_create_expense_transaction(self):
        """Test creating an expense transaction."""
        txn = Transaction(
            user_id=123,
            amount=Decimal("-20000"),
            category="Ăn uống"
        )
        
        assert txn.amount == Decimal("-20000")
        assert txn.is_expense()
        assert not txn.is_income()
    
    def test_transaction_with_note(self):
        """Test creating transaction with note."""
        txn = Transaction(
            user_id=123,
            amount=Decimal("50000"),
            category="Lương",
            note="Lương tháng 2"
        )
        
        assert txn.note == "Lương tháng 2"
    
    def test_amount_auto_conversion_to_decimal(self):
        """Test that amount is auto-converted to Decimal."""
        txn = Transaction(
            user_id=123,
            amount=50000,  # int
            category="Lương"
        )
        
        assert isinstance(txn.amount, Decimal)
        assert txn.amount == Decimal("50000")
    
    def test_amount_validation_zero(self):
        """Test that zero amount is not allowed."""
        with pytest.raises(ValueError, match="Amount cannot be zero"):
            Transaction(
                user_id=123,
                amount=Decimal("0"),
                category="Test"
            )
    
    def test_amount_validation_invalid(self):
        """Test that invalid amount raises error."""
        with pytest.raises(ValueError, match="Amount must be numeric"):
            Transaction(
                user_id=123,
                amount="invalid",
                category="Test"
            )
    
    def test_category_validation_empty(self):
        """Test that empty category is not allowed."""
        with pytest.raises(ValueError, match="Category is required"):
            Transaction(
                user_id=123,
                amount=Decimal("50000"),
                category=""
            )
    
    def test_category_validation_whitespace(self):
        """Test that whitespace-only category is not allowed."""
        with pytest.raises(ValueError, match="Category is required"):
            Transaction(
                user_id=123,
                amount=Decimal("50000"),
                category="   "
            )
    
    def test_category_trimmed(self):
        """Test that category is trimmed."""
        txn = Transaction(
            user_id=123,
            amount=Decimal("50000"),
            category="  Lương  "
        )
        
        assert txn.category == "Lương"
    
    def test_absolute_amount(self):
        """Test absolute_amount method."""
        income = Transaction(user_id=123, amount=Decimal("50000"), category="Lương")
        expense = Transaction(user_id=123, amount=Decimal("-20000"), category="Ăn uống")
        
        assert income.absolute_amount() == Decimal("50000")
        assert expense.absolute_amount() == Decimal("20000")
    
    def test_formatted_amount_income(self):
        """Test formatted_amount for income."""
        txn = Transaction(user_id=123, amount=Decimal("50000"), category="Lương")
        
        assert txn.formatted_amount() == "+50.000đ"
        assert txn.formatted_amount(show_sign=False) == "50.000đ"
    
    def test_formatted_amount_expense(self):
        """Test formatted_amount for expense."""
        txn = Transaction(user_id=123, amount=Decimal("-1500000"), category="Tiền nhà")
        
        assert txn.formatted_amount() == "-1.500.000đ"
        assert txn.formatted_amount(show_sign=False) == "1.500.000đ"
    
    def test_get_type(self):
        """Test get_type method."""
        income = Transaction(user_id=123, amount=Decimal("50000"), category="Lương")
        expense = Transaction(user_id=123, amount=Decimal("-20000"), category="Ăn uống")
        
        assert income.get_type() == "income"
        assert expense.get_type() == "expense"
    
    def test_update_amount(self):
        """Test updating transaction amount."""
        txn = Transaction(user_id=123, amount=Decimal("50000"), category="Lương")
        
        txn.update_amount(Decimal("60000"))
        
        assert txn.amount == Decimal("60000")
    
    def test_update_amount_validation(self):
        """Test that update_amount validates input."""
        txn = Transaction(user_id=123, amount=Decimal("50000"), category="Lương")
        
        with pytest.raises(ValueError, match="Amount cannot be zero"):
            txn.update_amount(Decimal("0"))
    
    def test_update_category(self):
        """Test updating transaction category."""
        txn = Transaction(user_id=123, amount=Decimal("50000"), category="Lương")
        
        txn.update_category("Thu nhập khác")
        
        assert txn.category == "Thu nhập khác"
    
    def test_update_category_validation(self):
        """Test that update_category validates input."""
        txn = Transaction(user_id=123, amount=Decimal("50000"), category="Lương")
        
        with pytest.raises(ValueError, match="Category is required"):
            txn.update_category("")
    
    def test_update_note(self):
        """Test updating transaction note."""
        txn = Transaction(user_id=123, amount=Decimal("50000"), category="Lương")
        
        txn.update_note("Lương tháng 2")
        assert txn.note == "Lương tháng 2"
        
        txn.update_note(None)
        assert txn.note is None
    
    def test_transaction_string_representation(self):
        """Test __str__ and __repr__ methods."""
        txn = Transaction(
            user_id=123,
            amount=Decimal("50000"),
            category="Lương",
            note="Lương tháng 2"
        )
        
        str_repr = str(txn)
        assert "+50.000đ" in str_repr
        assert "Lương" in str_repr
