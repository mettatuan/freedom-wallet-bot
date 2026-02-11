"""Unit tests for Money value object."""

import pytest
from decimal import Decimal

from src.domain.value_objects.money import Money


class TestMoneyValueObject:
    """Test suite for Money value object."""
    
    def test_create_money(self):
        """Test creating money with Decimal."""
        money = Money(Decimal("50000"), "VND")
        
        assert money.amount == Decimal("50000")
        assert money.currency == "VND"
    
    def test_create_money_with_int(self):
        """Test creating money with int (auto-converted to Decimal)."""
        money = Money(50000, "VND")
        
        assert isinstance(money.amount, Decimal)
        assert money.amount == Decimal("50000")
    
    def test_create_money_with_float(self):
        """Test creating money with float."""
        money = Money(50000.99, "VND")
        
        # VND should round to integer
        assert money.amount == Decimal("50001")
    
    def test_default_currency_vnd(self):
        """Test default currency is VND."""
        money = Money(Decimal("50000"))
        
        assert money.currency == "VND"
    
    def test_vnd_rounded_to_integer(self):
        """Test that VND amounts are rounded to integer."""
        money = Money(Decimal("50000.7"), "VND")
        
        assert money.amount == Decimal("50001")
    
    def test_negative_amount_not_allowed(self):
        """Test that negative amount raises error."""
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            Money(Decimal("-50000"), "VND")
    
    def test_unsupported_currency(self):
        """Test that unsupported currency raises error."""
        with pytest.raises(ValueError, match="Unsupported currency"):
            Money(Decimal("50000"), "EUR")
    
    def test_formatted_vnd(self):
        """Test formatting VND with thousand separators."""
        money = Money(Decimal("50000"), "VND")
        
        assert money.formatted() == "50.000đ"
    
    def test_formatted_large_amount(self):
        """Test formatting large amount."""
        money = Money(Decimal("1500000"), "VND")
        
        assert money.formatted() == "1.500.000đ"
    
    def test_formatted_without_currency(self):
        """Test formatting without currency symbol."""
        money = Money(Decimal("50000"), "VND")
        
        assert money.formatted(show_currency=False) == "50.000"
    
    def test_formatted_usd(self):
        """Test formatting USD."""
        money = Money(Decimal("100"), "USD")
        
        assert money.formatted() == "$100"
    
    def test_add_money(self):
        """Test adding two money objects."""
        money1 = Money(Decimal("50000"), "VND")
        money2 = Money(Decimal("30000"), "VND")
        
        result = money1.add(money2)
        
        assert result.amount == Decimal("80000")
        assert result.currency == "VND"
    
    def test_add_different_currencies(self):
        """Test that adding different currencies raises error."""
        vnd = Money(Decimal("50000"), "VND")
        usd = Money(Decimal("100"), "USD")
        
        with pytest.raises(ValueError, match="Cannot add different currencies"):
            vnd.add(usd)
    
    def test_subtract_money(self):
        """Test subtracting two money objects."""
        money1 = Money(Decimal("50000"), "VND")
        money2 = Money(Decimal("30000"), "VND")
        
        result = money1.subtract(money2)
        
        assert result.amount == Decimal("20000")
        assert result.currency == "VND"
    
    def test_subtract_result_negative(self):
        """Test that subtract with negative result raises error."""
        money1 = Money(Decimal("30000"), "VND")
        money2 = Money(Decimal("50000"), "VND")
        
        with pytest.raises(ValueError, match="Result cannot be negative"):
            money1.subtract(money2)
    
    def test_subtract_different_currencies(self):
        """Test that subtracting different currencies raises error."""
        vnd = Money(Decimal("50000"), "VND")
        usd = Money(Decimal("100"), "USD")
        
        with pytest.raises(ValueError, match="Cannot subtract different currencies"):
            vnd.subtract(usd)
    
    def test_multiply_money(self):
        """Test multiplying money by factor."""
        money = Money(Decimal("50000"), "VND")
        
        result = money.multiply(Decimal("2"))
        
        assert result.amount == Decimal("100000")
        assert result.currency == "VND"
    
    def test_is_zero(self):
        """Test is_zero method."""
        zero = Money(Decimal("0"), "VND")
        non_zero = Money(Decimal("50000"), "VND")
        
        assert zero.is_zero()
        assert not non_zero.is_zero()
    
    def test_is_positive(self):
        """Test is_positive method."""
        zero = Money(Decimal("0"), "VND")
        positive = Money(Decimal("50000"), "VND")
        
        assert not zero.is_positive()
        assert positive.is_positive()
    
    def test_money_equality(self):
        """Test money equality."""
        money1 = Money(Decimal("50000"), "VND")
        money2 = Money(Decimal("50000"), "VND")
        money3 = Money(Decimal("30000"), "VND")
        
        assert money1 == money2
        assert money1 != money3
    
    def test_money_comparison_less_than(self):
        """Test money less than comparison."""
        money1 = Money(Decimal("30000"), "VND")
        money2 = Money(Decimal("50000"), "VND")
        
        assert money1 < money2
        assert not money2 < money1
    
    def test_money_comparison_greater_than(self):
        """Test money greater than comparison."""
        money1 = Money(Decimal("50000"), "VND")
        money2 = Money(Decimal("30000"), "VND")
        
        assert money1 > money2
        assert not money2 > money1
    
    def test_money_comparison_different_currencies(self):
        """Test that comparing different currencies raises error."""
        vnd = Money(Decimal("50000"), "VND")
        usd = Money(Decimal("100"), "USD")
        
        with pytest.raises(ValueError, match="Cannot compare different currencies"):
            vnd < usd
    
    def test_money_immutable(self):
        """Test that money is immutable (frozen dataclass)."""
        money = Money(Decimal("50000"), "VND")
        
        with pytest.raises(Exception):  # FrozenInstanceError
            money.amount = Decimal("60000")
    
    def test_money_str(self):
        """Test __str__ method."""
        money = Money(Decimal("50000"), "VND")
        
        assert str(money) == "50.000đ"
    
    def test_money_repr(self):
        """Test __repr__ method."""
        money = Money(Decimal("50000"), "VND")
        
        repr_str = repr(money)
        assert "Money" in repr_str
        assert "50000" in repr_str
        assert "VND" in repr_str
