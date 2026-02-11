"""Phone value object with Vietnamese format validation."""

import re
from dataclasses import dataclass
from typing import ClassVar, Optional


@dataclass(frozen=True)
class Phone:
    """
    Phone value object - immutable and self-validating.
    
    Business Rules:
    - Supports Vietnamese phone formats (+84, 0)
    - Normalizes to international format (+84xxxxxxxxx)
    - Validates length (10-11 digits)
    - Immutable (frozen dataclass)
    """
    
    value: str
    
    # Vietnamese phone patterns
    INTERNATIONAL_REGEX: ClassVar[re.Pattern] = re.compile(r'^\+84[0-9]{9,10}$')
    LOCAL_REGEX: ClassVar[re.Pattern] = re.compile(r'^0[0-9]{9,10}$')
    
    def __post_init__(self):
        """Validate and normalize phone after initialization."""
        normalized = self._normalize(self.value)
        object.__setattr__(self, 'value', normalized)
        self._validate()
    
    def _normalize(self, phone: str) -> str:
        """
        Normalize phone to international format.
        
        Args:
            phone: Input phone number
            
        Returns:
            Normalized phone in +84 format
        """
        # Remove all whitespace and special characters
        phone = re.sub(r'[\s\-\(\)]', '', phone.strip())
        
        # Convert local format (0xxx) to international (+84xxx)
        if phone.startswith('0'):
            return f"+84{phone[1:]}"
        
        # Add + if missing
        if phone.startswith('84') and not phone.startswith('+84'):
            return f"+{phone}"
        
        return phone
    
    def _validate(self) -> None:
        """
        Validate phone format.
        
        Raises:
            ValueError: If phone is invalid
        """
        if not self.value:
            raise ValueError("Phone number cannot be empty.")
        
        if not self.INTERNATIONAL_REGEX.match(self.value):
            raise ValueError(f"Invalid Vietnamese phone format: {self.value}")
    
    def local_format(self) -> str:
        """
        Get phone in local format (0xxx).
        
        Returns:
            Phone in local format (e.g., "0901234567")
        """
        return f"0{self.value[3:]}"
    
    def international_format(self) -> str:
        """
        Get phone in international format (+84xxx).
        
        Returns:
            Phone in international format (e.g., "+84901234567")
        """
        return self.value
    
    def formatted(self) -> str:
        """
        Get formatted phone with spaces.
        
        Returns:
            Formatted phone (e.g., "+84 90 123 4567")
        """
        # Format as +84 XX XXX XXXX
        digits = self.value[3:]
        if len(digits) == 9:
            return f"+84 {digits[0:2]} {digits[2:5]} {digits[5:]}"
        else:  # 10 digits
            return f"+84 {digits[0:3]} {digits[3:6]} {digits[6:]}"
    
    def __str__(self) -> str:
        """String representation (international format)."""
        return self.value
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"Phone('{self.value}')"
