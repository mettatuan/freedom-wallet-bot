"""Unit tests for Phone value object."""

import pytest

from src.domain.value_objects.phone import Phone


class TestPhoneValueObject:
    """Test suite for Phone value object."""
    
    def test_create_phone_international_format(self):
        """Test creating phone with international format."""
        phone = Phone("+84901234567")
        
        assert phone.value == "+84901234567"
        assert str(phone) == "+84901234567"
    
    def test_create_phone_local_format(self):
        """Test creating phone with local format (0xxx)."""
        phone = Phone("0901234567")
        
        # Should be normalized to international format
        assert phone.value == "+84901234567"
    
    def test_normalize_phone_with_spaces(self):
        """Test that spaces are removed."""
        phone = Phone("0901 234 567")
        
        assert phone.value == "+84901234567"
    
    def test_normalize_phone_with_dashes(self):
        """Test that dashes are removed."""
        phone = Phone("0901-234-567")
        
        assert phone.value == "+84901234567"
    
    def test_normalize_phone_with_parentheses(self):
        """Test that parentheses are removed."""
        phone = Phone("(090) 123-4567")
        
        assert phone.value == "+84901234567"
    
    def test_normalize_84_without_plus(self):
        """Test normalizing 84xxx format."""
        phone = Phone("84901234567")
        
        assert phone.value == "+84901234567"
    
    def test_invalid_phone_too_short(self):
        """Test that too short phone is invalid."""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone format"):
            Phone("+8490123")
    
    def test_invalid_phone_too_long(self):
        """Test that too long phone is invalid."""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone format"):
            Phone("+849012345678901")
    
    def test_invalid_phone_not_vietnamese(self):
        """Test that non-Vietnamese phone is invalid."""
        with pytest.raises(ValueError, match="Invalid Vietnamese phone format"):
            Phone("+1234567890")
    
    def test_empty_phone(self):
        """Test that empty phone is invalid."""
        with pytest.raises(ValueError, match="Phone number cannot be empty"):
            Phone("")
    
    def test_local_format_method(self):
        """Test local_format method."""
        phone = Phone("+84901234567")
        
        assert phone.local_format() == "0901234567"
    
    def test_international_format_method(self):
        """Test international_format method."""
        phone = Phone("0901234567")
        
        assert phone.international_format() == "+84901234567"
    
    def test_formatted_9_digits(self):
        """Test formatted method for 9-digit phone."""
        phone = Phone("+84901234567")
        
        assert phone.formatted() == "+84 90 123 4567"
    
    def test_formatted_10_digits(self):
        """Test formatted method for 10-digit phone."""
        phone = Phone("+849012345678")
        
        assert phone.formatted() == "+84 901 234 5678"
    
    def test_phone_immutable(self):
        """Test that phone is immutable (frozen dataclass)."""
        phone = Phone("+84901234567")
        
        with pytest.raises(Exception):  # FrozenInstanceError
            phone.value = "+84987654321"
    
    def test_phone_equality(self):
        """Test phone equality."""
        phone1 = Phone("+84901234567")
        phone2 = Phone("0901234567")  # Same after normalization
        phone3 = Phone("+84987654321")
        
        assert phone1 == phone2
        assert phone1 != phone3
    
    def test_phone_repr(self):
        """Test __repr__ method."""
        phone = Phone("+84901234567")
        
        repr_str = repr(phone)
        assert "Phone" in repr_str
        assert "+84901234567" in repr_str
