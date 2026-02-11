"""Money value object with amount and currency."""

from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Money:
    """
    Money value object - immutable amount with currency.
    
    Business Rules:
    - Amount must be non-negative for balance/price contexts
    - Supports VND (Vietnamese Dong) currency
    - Formats with thousand separators (20.000đ)
    - Precision to 0 decimal places (VND doesn't use decimals)
    - Immutable (frozen dataclass)
    """
    
    amount: Decimal
    currency: str = "VND"
    
    SUPPORTED_CURRENCIES: ClassVar[set] = {"VND", "USD"}
    
    def __post_init__(self):
        """Validate money after initialization."""
        # Convert to Decimal if needed
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        # Round to integer for VND
        if self.currency == "VND":
            rounded = self.amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            object.__setattr__(self, 'amount', rounded)
        
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate money data.
        
        Raises:
            ValueError: If validation fails
        """
        if self.currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {self.currency}. Must be one of {self.SUPPORTED_CURRENCIES}")
        
        if self.amount < 0:
            raise ValueError("Amount cannot be negative.")
    
    def formatted(self, show_currency: bool = True) -> str:
        """
        Format money with thousand separators.
        
        Args:
            show_currency: Whether to show currency symbol
            
        Returns:
            Formatted amount (e.g., "20.000đ", "1.500.000đ")
        """
        amount_int = int(self.amount)
        formatted = f"{amount_int:,}".replace(",", ".")
        
        if show_currency:
            if self.currency == "VND":
                return f"{formatted}đ"
            elif self.currency == "USD":
                return f"${formatted}"
        
        return formatted
    
    def add(self, other: 'Money') -> 'Money':
        """
        Add two money objects.
        
        Args:
            other: Money to add
            
        Returns:
            New Money object with sum
            
        Raises:
            ValueError: If currencies don't match
        """
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """
        Subtract two money objects.
        
        Args:
            other: Money to subtract
            
        Returns:
            New Money object with difference
            
        Raises:
            ValueError: If currencies don't match or result is negative
        """
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies: {self.currency} and {other.currency}")
        
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Result cannot be negative.")
        
        return Money(result, self.currency)
    
    def multiply(self, factor: Decimal) -> 'Money':
        """
        Multiply money by a factor.
        
        Args:
            factor: Multiplication factor
            
        Returns:
            New Money object with product
        """
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        
        return Money(self.amount * factor, self.currency)
    
    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == 0
    
    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > 0
    
    def __str__(self) -> str:
        """String representation."""
        return self.formatted()
    
    def __repr__(self) -> str:
        """Debug representation."""
        return f"Money({self.amount}, '{self.currency}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: 'Money') -> bool:
        """Less than comparison."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare different currencies: {self.currency} and {other.currency}")
        return self.amount < other.amount
    
    def __le__(self, other: 'Money') -> bool:
        """Less than or equal comparison."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare different currencies: {self.currency} and {other.currency}")
        return self.amount <= other.amount
    
    def __gt__(self, other: 'Money') -> bool:
        """Greater than comparison."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare different currencies: {self.currency} and {other.currency}")
        return self.amount > other.amount
    
    def __ge__(self, other: 'Money') -> bool:
        """Greater than or equal comparison."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare different currencies: {self.currency} and {other.currency}")
        return self.amount >= other.amount
