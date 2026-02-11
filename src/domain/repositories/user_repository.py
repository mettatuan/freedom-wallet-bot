"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities.user import User
from ..value_objects.user_tier import UserTier


class UserRepository(ABC):
    """
    Repository interface for User entity.
    
    This is a domain interface - implementation will be in infrastructure layer.
    Follows repository pattern for data persistence abstraction.
    """
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Save user (create or update).
        
        Args:
            user: User to save
            
        Returns:
            Saved user instance
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def find_by_tier(self, tier: UserTier) -> List[User]:
        """
        Find all users by tier.
        
        Args:
            tier: User tier to filter by
            
        Returns:
            List of users with specified tier
        """
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Find user by email.
        
        Args:
            email: Email address
            
        Returns:
            User instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def count_by_tier(self, tier: UserTier) -> int:
        """
        Count users by tier.
        
        Args:
            tier: User tier to count
            
        Returns:
            Number of users with specified tier
        """
        pass
    
    @abstractmethod
    async def exists(self, user_id: int) -> bool:
        """
        Check if user exists.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
