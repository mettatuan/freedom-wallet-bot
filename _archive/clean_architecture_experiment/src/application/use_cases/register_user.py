"""RegisterUserUseCase - handles user registration workflow."""

from typing import Optional
import logging

from ..common.result import Result
from ..dtos import RegisterUserInput, RegisterUserOutput, UserDTO, SubscriptionDTO
from ...domain.entities.user import User
from ...domain.entities.subscription import Subscription
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.subscription_repository import SubscriptionRepository
from ...domain.value_objects.user_tier import UserTier
from ...domain.value_objects.email import Email
from ...domain.value_objects.phone import Phone


logger = logging.getLogger(__name__)


class RegisterUserUseCase:
    """
    Use case for registering a new user.
    
    Business Rules:
    - Check if user already exists (idempotent)
    - Create FREE tier user
    - Create FREE subscription (never expires)
    - Validate email and phone if provided
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        subscription_repository: SubscriptionRepository
    ):
        self.user_repository = user_repository
        self.subscription_repository = subscription_repository
    
    async def execute(self, input_data: RegisterUserInput) -> Result[RegisterUserOutput]:
        """
        Execute user registration.
        
        Args:
            input_data: Registration input data
            
        Returns:
            Result with RegisterUserOutput or error
        """
        try:
            # Check if user already exists
            existing_user = await self.user_repository.get_by_telegram_id(
                input_data.telegram_user_id
            )
            
            if existing_user:
                logger.info(f"User {input_data.telegram_user_id} already exists")
                
                # Get existing subscription
                subscription = await self.subscription_repository.get_by_user_id(
                    existing_user.user_id
                )
                
                # If user exists but no subscription, create one (data repair)
                if not subscription:
                    logger.warning(f"User {existing_user.user_id} has no subscription. Creating FREE subscription...")
                    free_subscription = Subscription.create_free_subscription(
                        user_id=existing_user.user_id
                    )
                    subscription = await self.subscription_repository.save(free_subscription)
                    logger.info(f"Created missing FREE subscription for user {existing_user.user_id}")
                
                return Result.success(RegisterUserOutput(
                    user=self._user_to_dto(existing_user),
                    subscription=self._subscription_to_dto(subscription),
                    is_new_user=False
                ))
            
            # Validate email if provided
            if input_data.email:
                try:
                    email = Email(input_data.email)
                    validated_email = str(email)
                except ValueError as e:
                    return Result.failure(f"Invalid email: {e}", error_code="INVALID_EMAIL")
            else:
                validated_email = None
            
            # Validate phone if provided
            if input_data.phone:
                try:
                    phone = Phone(input_data.phone)
                    validated_phone = str(phone)
                except ValueError as e:
                    return Result.failure(f"Invalid phone: {e}", error_code="INVALID_PHONE")
            else:
                validated_phone = None
            
            # Create new FREE tier user
            new_user = User(
                user_id=input_data.telegram_user_id,
                telegram_username=input_data.telegram_username,
                email=validated_email,
                phone=validated_phone,
                tier=UserTier.FREE
            )
            
            # Save user
            saved_user = await self.user_repository.save(new_user)
            logger.info(f"Created new user {saved_user.user_id}")
            
            # Create FREE subscription
            free_subscription = Subscription.create_free_subscription(
                user_id=saved_user.user_id
            )
            
            # Save subscription
            saved_subscription = await self.subscription_repository.save(free_subscription)
            logger.info(f"Created FREE subscription for user {saved_user.user_id}")
            
            return Result.success(RegisterUserOutput(
                user=self._user_to_dto(saved_user),
                subscription=self._subscription_to_dto(saved_subscription),
                is_new_user=True
            ))
            
        except Exception as e:
            logger.error(f"Error registering user: {e}", exc_info=True)
            return Result.error(
                f"Failed to register user: {str(e)}",
                error_code="REGISTRATION_ERROR"
            )
    
    def _user_to_dto(self, user: User) -> UserDTO:
        """Convert User entity to UserDTO."""
        return UserDTO(
            user_id=user.user_id,
            telegram_username=user.telegram_username,
            email=user.email,
            phone=user.phone,
            tier=user.tier,
            sheet_url=user.sheet_url,
            webapp_url=user.webapp_url,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def _subscription_to_dto(self, subscription: Subscription) -> SubscriptionDTO:
        """Convert Subscription entity to SubscriptionDTO."""
        return SubscriptionDTO(
            user_id=subscription.user_id,
            tier=subscription.tier,
            started_at=subscription.started_at,
            expires_at=subscription.expires_at,
            auto_renew=subscription.auto_renew,
            is_active=subscription.is_active(),
            days_until_expiry=subscription.days_until_expiry()
        )
