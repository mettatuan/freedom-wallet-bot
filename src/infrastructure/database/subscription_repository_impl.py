"""SQLAlchemy SubscriptionRepository implementation."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from ...domain.entities.subscription import Subscription
from ...domain.repositories.subscription_repository import SubscriptionRepository
from ...domain.value_objects.user_tier import UserTier
from ..database.models import SubscriptionModel, UserTierEnum


class SQLAlchemySubscriptionRepository(SubscriptionRepository):
    """SQLAlchemy implementation of SubscriptionRepository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_by_user_id(self, user_id: int) -> Optional[Subscription]:
        """Get active subscription for user."""
        model = self.session.query(SubscriptionModel).filter(
            SubscriptionModel.user_id == user_id
        ).first()
        
        return self._to_entity(model) if model else None
    
    async def save(self, subscription: Subscription) -> Subscription:
        """Save subscription (create or update)."""
        model = self.session.query(SubscriptionModel).filter(
            SubscriptionModel.user_id == subscription.user_id
        ).first()
        
        if model:
            # Update existing
            model.tier = self._tier_to_enum(subscription.tier)
            model.started_at = subscription.started_at
            model.expires_at = subscription.expires_at
            model.auto_renew = subscription.auto_renew
            model.last_payment_at = subscription.last_payment_at
            model.updated_at = subscription.updated_at
        else:
            # Create new
            model = SubscriptionModel(
                user_id=subscription.user_id,
                tier=self._tier_to_enum(subscription.tier),
                started_at=subscription.started_at,
                expires_at=subscription.expires_at,
                auto_renew=subscription.auto_renew,
                last_payment_at=subscription.last_payment_at,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            )
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        
        return self._to_entity(model)
    
    async def delete(self, user_id: int) -> bool:
        """Delete subscription for user."""
        model = self.session.query(SubscriptionModel).filter(
            SubscriptionModel.user_id == user_id
        ).first()
        
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        
        return False
    
    async def find_expiring_soon(self, days: int) -> List[Subscription]:
        """Find subscriptions expiring within specified days."""
        now = datetime.utcnow()
        future = now + timedelta(days=days)
        
        models = self.session.query(SubscriptionModel).filter(
            and_(
                SubscriptionModel.expires_at.isnot(None),
                SubscriptionModel.expires_at > now,
                SubscriptionModel.expires_at <= future
            )
        ).all()
        
        return [self._to_entity(model) for model in models]
    
    async def find_expired(self) -> List[Subscription]:
        """Find all expired subscriptions (past grace period)."""
        now = datetime.utcnow()
        grace_period_end = now - timedelta(days=Subscription.GRACE_PERIOD_DAYS)
        
        models = self.session.query(SubscriptionModel).filter(
            and_(
                SubscriptionModel.expires_at.isnot(None),
                SubscriptionModel.expires_at < grace_period_end
            )
        ).all()
        
        return [self._to_entity(model) for model in models]
    
    async def find_by_tier(self, tier: UserTier) -> List[Subscription]:
        """Find all subscriptions by tier."""
        models = self.session.query(SubscriptionModel).filter(
            SubscriptionModel.tier == self._tier_to_enum(tier)
        ).all()
        
        return [self._to_entity(model) for model in models]
    
    async def count_active(self) -> int:
        """Count active subscriptions."""
        now = datetime.utcnow()
        
        return self.session.query(func.count(SubscriptionModel.id)).filter(
            (SubscriptionModel.expires_at.is_(None)) | (SubscriptionModel.expires_at > now)
        ).scalar()
    
    async def count_by_tier(self, tier: UserTier) -> int:
        """Count subscriptions by tier."""
        return self.session.query(func.count(SubscriptionModel.id)).filter(
            SubscriptionModel.tier == self._tier_to_enum(tier)
        ).scalar()
    
    def _to_entity(self, model: SubscriptionModel) -> Subscription:
        """Convert database model to domain entity."""
        return Subscription(
            user_id=model.user_id,
            tier=self._enum_to_tier(model.tier),
            started_at=model.started_at,
            expires_at=model.expires_at,
            auto_renew=model.auto_renew,
            last_payment_at=model.last_payment_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _tier_to_enum(self, tier: UserTier) -> UserTierEnum:
        """Convert domain UserTier to database enum."""
        return UserTierEnum[tier.value]
    
    def _enum_to_tier(self, enum_value: UserTierEnum) -> UserTier:
        """Convert database enum to domain UserTier."""
        return UserTier[enum_value.value]
