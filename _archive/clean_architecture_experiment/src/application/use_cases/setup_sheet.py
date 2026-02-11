"""SetupSheetUseCase - handles Google Sheets setup workflow."""

import logging

from ..common.result import Result
from ..dtos import SetupSheetInput, SetupSheetOutput, UserDTO, SubscriptionDTO
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.subscription_repository import SubscriptionRepository
from ...domain.value_objects.user_tier import UserTier


logger = logging.getLogger(__name__)


class SetupSheetUseCase:
    """
    Use case for setting up Google Sheets for a user.
    
    Business Rules:
    - User must exist
    - User must be FREE tier
    - Sheet URL and Web App URL must be valid
    - Upgrades user to UNLOCK tier
    - Creates new UNLOCK subscription (30 days)
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        subscription_repository: SubscriptionRepository
    ):
        self.user_repository = user_repository
        self.subscription_repository = subscription_repository
    
    async def execute(self, input_data: SetupSheetInput) -> Result[SetupSheetOutput]:
        """
        Execute sheet setup.
        
        Args:
            input_data: Sheet setup input data
            
        Returns:
            Result with SetupSheetOutput or error
        """
        try:
            # Get user
            user = await self.user_repository.get_by_id(input_data.user_id)
            
            if not user:
                return Result.failure(
                    f"User {input_data.user_id} not found",
                    error_code="USER_NOT_FOUND"
                )
            
            # Check if user is FREE tier
            if user.tier != UserTier.FREE:
                return Result.failure(
                    f"User is already {user.tier} tier. Sheet setup is for FREE tier only.",
                    error_code="INVALID_TIER"
                )
            
            # Validate URLs
            if not input_data.sheet_url or not input_data.sheet_url.strip():
                return Result.failure("Sheet URL is required", error_code="MISSING_SHEET_URL")
            
            if not input_data.webapp_url or not input_data.webapp_url.strip():
                return Result.failure("Web App URL is required", error_code="MISSING_WEBAPP_URL")
            
            # Update email and phone if provided
            if input_data.email:
                user.email = input_data.email.strip()
            if input_data.phone:
                user.phone = input_data.phone.strip()
            
            # Upgrade user to UNLOCK
            try:
                user.upgrade_to_unlock(
                    sheet_url=input_data.sheet_url.strip(),
                    webapp_url=input_data.webapp_url.strip()
                )
            except ValueError as e:
                return Result.failure(str(e), error_code="UPGRADE_FAILED")
            
            # Save updated user
            saved_user = await self.user_repository.save(user)
            logger.info(f"User {saved_user.user_id} upgraded to UNLOCK")
            
            # Create UNLOCK subscription (30 days)
            from ...domain.entities.subscription import Subscription
            unlock_subscription = Subscription.create_unlock_subscription(
                user_id=saved_user.user_id
            )
            
            # Save subscription
            saved_subscription = await self.subscription_repository.save(unlock_subscription)
            logger.info(f"Created UNLOCK subscription for user {saved_user.user_id}")
            
            return Result.success(SetupSheetOutput(
                user=self._user_to_dto(saved_user),
                subscription=self._subscription_to_dto(saved_subscription),
                upgraded_to_unlock=True
            ))
            
        except Exception as e:
            logger.error(f"Error setting up sheet: {e}", exc_info=True)
            return Result.error(
                f"Failed to setup sheet: {str(e)}",
                error_code="SETUP_ERROR"
            )
    
    def _user_to_dto(self, user) -> UserDTO:
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
    
    def _subscription_to_dto(self, subscription) -> SubscriptionDTO:
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
