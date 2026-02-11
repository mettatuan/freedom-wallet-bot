"""Transaction repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from ..entities.transaction import Transaction


class TransactionRepository(ABC):
    """
    Repository interface for Transaction entity.
    
    This is a domain interface - implementation will be in infrastructure layer.
    """
    
    @abstractmethod
    async def save(self, transaction: Transaction) -> Transaction:
        """
        Save transaction (create or update).
        
        Args:
            transaction: Transaction to save
            
        Returns:
            Saved transaction instance
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(self, transaction_id: str) -> bool:
        """
        Delete transaction by ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def get_recent(self, user_id: int, limit: int = 10) -> List[Transaction]:
        """
        Get recent transactions for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of transactions to return
            
        Returns:
            List of recent transactions (newest first)
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Transaction]:
        """
        Get transactions within date range.
        
        Args:
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of transactions in date range
        """
        pass
    
    @abstractmethod
    async def get_by_category(self, user_id: int, category: str) -> List[Transaction]:
        """
        Get transactions by category.
        
        Args:
            user_id: User ID
            category: Category name
            
        Returns:
            List of transactions in category
        """
        pass
    
    @abstractmethod
    async def get_income_total(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """
        Calculate total income for user.
        
        Args:
            user_id: User ID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Total income amount
        """
        pass
    
    @abstractmethod
    async def get_expense_total(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """
        Calculate total expenses for user.
        
        Args:
            user_id: User ID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Total expense amount (absolute value)
        """
        pass
    
    @abstractmethod
    async def count_by_user(self, user_id: int) -> int:
        """
        Count transactions for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of transactions
        """
        pass
