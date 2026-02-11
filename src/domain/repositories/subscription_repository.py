"""Subscription repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime

from ..entities.subscription import Subscription
from ..value_objects.user_tier import UserTier


class SubscriptionRepository(ABC):
    """
    Repository interface for Subscription entity.
    
    This is a domain interface - implementation will be in infrastructure layer.
    """
    
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[Subscription]:
        """
        Get active subscription for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Subscription instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def save(self, subscription: Subscription) -> Subscription:
        """
        Save subscription (create or update).
        
        Args:
            subscription: Subscription to save
            
        Returns:
            Saved subscription instance
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
        Delete subscription for user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def find_expiring_soon(self, days: int) -> List[Subscription]:
        """
        Find subscriptions expiring within specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of subscriptions expiring soon
        """
        pass
    
    @abstractmethod
    async def find_expired(self) -> List[Subscription]:
        """
        Find all expired subscriptions (past grace period).
        
        Returns:
            List of expired subscriptions
        """
        pass
    
    @abstractmethod
    async def find_by_tier(self, tier: UserTier) -> List[Subscription]:
        """
        Find all subscriptions by tier.
        
        Args:
            tier: Subscription tier
            
        Returns:
            List of subscriptions with specified tier
        """
        pass
    
    @abstractmethod
    async def count_active(self) -> int:
        """
        Count active subscriptions.
        
        Returns:
            Number of active subscriptions
        """
        pass
    
    @abstractmethod
    async def count_by_tier(self, tier: UserTier) -> int:
        """
        Count subscriptions by tier.
        
        Args:
            tier: Subscription tier
            
        Returns:
            Number of subscriptions with specified tier
        """
        pass
