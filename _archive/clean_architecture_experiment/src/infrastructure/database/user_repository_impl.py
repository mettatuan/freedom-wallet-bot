"""SQLAlchemy UserRepository implementation."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...domain.value_objects.user_tier import UserTier
from ..database.models import UserModel, UserTierEnum


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        model = self.session.query(UserModel).filter(UserModel.user_id == user_id).first()
        return self._to_entity(model) if model else None
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        model = self.session.query(UserModel).filter(UserModel.user_id == telegram_id).first()
        return self._to_entity(model) if model else None
    
    async def save(self, user: User) -> User:
        """Save user (create or update)."""
        model = self.session.query(UserModel).filter(UserModel.user_id == user.user_id).first()
        
        if model:
            # Update existing
            model.telegram_username = user.telegram_username
            model.email = user.email
            model.phone = user.phone
            model.tier = self._tier_to_enum(user.tier)
            model.sheet_url = user.sheet_url
            model.webapp_url = user.webapp_url
            model.updated_at = user.updated_at
        else:
            # Create new
            model = UserModel(
                user_id=user.user_id,
                telegram_username=user.telegram_username,
                email=user.email,
                phone=user.phone,
                tier=self._tier_to_enum(user.tier),
                sheet_url=user.sheet_url,
                webapp_url=user.webapp_url,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        
        return self._to_entity(model)
    
    async def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        model = self.session.query(UserModel).filter(UserModel.user_id == user_id).first()
        
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        
        return False
    
    async def find_by_tier(self, tier: UserTier) -> List[User]:
        """Find all users by tier."""
        models = self.session.query(UserModel).filter(
            UserModel.tier == self._tier_to_enum(tier)
        ).all()
        
        return [self._to_entity(model) for model in models]
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email."""
        model = self.session.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(model) if model else None
    
    async def count_by_tier(self, tier: UserTier) -> int:
        """Count users by tier."""
        return self.session.query(func.count(UserModel.user_id)).filter(
            UserModel.tier == self._tier_to_enum(tier)
        ).scalar()
    
    async def exists(self, user_id: int) -> bool:
        """Check if user exists."""
        return self.session.query(
            self.session.query(UserModel).filter(UserModel.user_id == user_id).exists()
        ).scalar()
    
    def _to_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            user_id=model.user_id,
            telegram_username=model.telegram_username,
            email=model.email,
            phone=model.phone,
            tier=self._enum_to_tier(model.tier),
            sheet_url=model.sheet_url,
            webapp_url=model.webapp_url,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _tier_to_enum(self, tier: UserTier) -> UserTierEnum:
        """Convert domain UserTier to database enum."""
        return UserTierEnum[tier.value]
    
    def _enum_to_tier(self, enum_value: UserTierEnum) -> UserTier:
        """Convert database enum to domain UserTier."""
        return UserTier[enum_value.value]
