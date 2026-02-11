"""Email value object with validation."""

import re
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Email:
    """
    Email value object - immutable and self-validating.
    
    Business Rules:
    - Must be valid email format (RFC 5322 compliant)
    - Case-insensitive (stored lowercase)
    - Immutable (frozen dataclass)
    """
    
    value: str
    
    EMAIL_REGEX: ClassVar[re.Pattern] = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __post_init__(self):
        """Validate email after initialization."""
        # Normalize to lowercase
        object.__setattr__(self, 'value', self.value.lower().strip())
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate email format.
        
        Raises:
            ValueError: If email is invalid
        """
        if not self.value:
            raise ValueError("Email cannot be empty.")
        
        if not self.EMAIL_REGEX.match(self.value):
            raise ValueError(f"Invalid email format: {self.value}")
        
        if len(self.value) > 254:  # RFC 5321
            raise ValueError("Email is too long (max 254 characters).")
    
    def domain(self) -> str:
        """
        Extract domain from email.
        
        Returns:
            Domain part of email (e.g., "gmail.com")
        """
        return self.value.split('@')[1]
    
    def local_part(self) -> str:
        """
        Extract local part from email.
        
        Returns:
            Local part of email (e.g., "user")
        """
        return self.value.split('@')[0]
    
    def is_gmail(self) -> bool:
        """Check if email is Gmail."""
        return self.domain() == 'gmail.com'
    
    def __str__(self) -> str:
        """String representation."""
        return self.value
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"Email('{self.value}')"
