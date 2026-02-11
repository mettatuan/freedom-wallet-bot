"""Transaction entity - represents a financial transaction."""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Transaction:
    """
    Transaction entity representing a financial transaction.
    
    Business Rules:
    - Amount must be numeric (Decimal for precision)
    - Positive amount = income, negative = expense
    - Category must be valid (validated by domain service)
    - Date defaults to current datetime if not specified
    """
    
    user_id: int
    amount: Decimal
    category: str
    date: datetime = field(default_factory=datetime.utcnow)
    note: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate transaction after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate transaction data.
        
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(self.amount, Decimal):
            try:
                self.amount = Decimal(str(self.amount))
            except (ValueError, TypeError, Exception) as e:
                raise ValueError(f"Amount must be numeric: {e}")
        
        if self.amount == 0:
            raise ValueError("Amount cannot be zero.")
        
        if not self.category or not self.category.strip():
            raise ValueError("Category is required.")
        
        self.category = self.category.strip()
    
    def is_income(self) -> bool:
        """
        Check if transaction is income.
        
        Returns:
            True if amount is positive (income)
        """
        return self.amount > 0
    
    def is_expense(self) -> bool:
        """
        Check if transaction is expense.
        
        Returns:
            True if amount is negative (expense)
        """
        return self.amount < 0
    
    def absolute_amount(self) -> Decimal:
        """
        Get absolute value of amount.
        
        Returns:
            Absolute amount
        """
        return abs(self.amount)
    
    def formatted_amount(self, show_sign: bool = True) -> str:
        """
        Format amount with Vietnamese currency formatting.
        
        Args:
            show_sign: Whether to show +/- sign
            
        Returns:
            Formatted amount string (e.g., "+20.000đ", "-1.500.000đ")
        """
        abs_amount = self.absolute_amount()
        
        # Format with thousand separators
        amount_int = int(abs_amount)
        formatted = f"{amount_int:,}".replace(",", ".")
        
        # Add sign
        if show_sign:
            sign = "+" if self.is_income() else "-"
            return f"{sign}{formatted}đ"
        else:
            return f"{formatted}đ"
    
    def get_type(self) -> str:
        """
        Get transaction type as string.
        
        Returns:
            "income" or "expense"
        """
        return "income" if self.is_income() else "expense"
    
    def update_amount(self, new_amount: Decimal) -> None:
        """
        Update transaction amount.
        
        Args:
            new_amount: New amount value
            
        Raises:
            ValueError: If amount is invalid
        """
        if not isinstance(new_amount, Decimal):
            try:
                new_amount = Decimal(str(new_amount))
            except (ValueError, TypeError, Exception) as e:
                raise ValueError(f"Amount must be numeric: {e}")
        
        if new_amount == 0:
            raise ValueError("Amount cannot be zero.")
        
        self.amount = new_amount
    
    def update_category(self, new_category: str) -> None:
        """
        Update transaction category.
        
        Args:
            new_category: New category name
            
        Raises:
            ValueError: If category is invalid
        """
        if not new_category or not new_category.strip():
            raise ValueError("Category is required.")
        
        self.category = new_category.strip()
    
    def update_note(self, new_note: Optional[str]) -> None:
        """
        Update transaction note.
        
        Args:
            new_note: New note text (can be None)
        """
        self.note = new_note.strip() if new_note else None
    
    def __str__(self) -> str:
        """String representation of transaction."""
        return f"Transaction({self.formatted_amount()}, {self.category}, {self.date.strftime('%Y-%m-%d')})"
    
    def __repr__(self) -> str:
        """Debug representation of transaction."""
        note_preview = f", note='{self.note[:20]}...'" if self.note and len(self.note) > 20 else f", note='{self.note}'" if self.note else ""
        return (f"Transaction(user_id={self.user_id}, amount={self.formatted_amount()}, "
                f"category='{self.category}'{note_preview})")
