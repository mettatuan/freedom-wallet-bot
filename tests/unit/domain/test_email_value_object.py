"""Unit tests for Email value object."""

import pytest

from src.domain.value_objects.email import Email


class TestEmailValueObject:
    """Test suite for Email value object."""
    
    def test_create_valid_email(self):
        """Test creating a valid email."""
        email = Email("test@example.com")
        
        assert email.value == "test@example.com"
        assert str(email) == "test@example.com"
    
    def test_email_normalized_to_lowercase(self):
        """Test that email is normalized to lowercase."""
        email = Email("Test@EXAMPLE.COM")
        
        assert email.value == "test@example.com"
    
    def test_email_trimmed(self):
        """Test that email is trimmed."""
        email = Email("  test@example.com  ")
        
        assert email.value == "test@example.com"
    
    def test_invalid_email_no_at(self):
        """Test that email without @ is invalid."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("testexample.com")
    
    def test_invalid_email_no_domain(self):
        """Test that email without domain is invalid."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test@")
    
    def test_invalid_email_no_local(self):
        """Test that email without local part is invalid."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("@example.com")
    
    def test_invalid_email_no_tld(self):
        """Test that email without TLD is invalid."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test@example")
    
    def test_empty_email(self):
        """Test that empty email is invalid."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")
    
    def test_email_too_long(self):
        """Test that email longer than 254 characters is invalid."""
        long_email = "a" * 250 + "@test.com"
        
        with pytest.raises(ValueError, match="Email is too long"):
            Email(long_email)
    
    def test_extract_domain(self):
        """Test extracting domain from email."""
        email = Email("test@example.com")
        
        assert email.domain() == "example.com"
    
    def test_extract_local_part(self):
        """Test extracting local part from email."""
        email = Email("test@example.com")
        
        assert email.local_part() == "test"
    
    def test_is_gmail(self):
        """Test is_gmail method."""
        gmail = Email("test@gmail.com")
        other = Email("test@example.com")
        
        assert gmail.is_gmail()
        assert not other.is_gmail()
    
    def test_email_immutable(self):
        """Test that email is immutable (frozen dataclass)."""
        email = Email("test@example.com")
        
        with pytest.raises(Exception):  # FrozenInstanceError
            email.value = "new@example.com"
    
    def test_email_equality(self):
        """Test email equality."""
        email1 = Email("test@example.com")
        email2 = Email("Test@EXAMPLE.COM")  # Same after normalization
        email3 = Email("other@example.com")
        
        assert email1 == email2
        assert email1 != email3
    
    def test_email_repr(self):
        """Test __repr__ method."""
        email = Email("test@example.com")
        
        repr_str = repr(email)
        assert "Email" in repr_str
        assert "test@example.com" in repr_str
