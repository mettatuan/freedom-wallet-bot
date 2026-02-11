"""CalculateBalanceUseCase - calculates user's financial balance."""

import logging
from decimal import Decimal

from ..common.result import Result
from ..dtos import CalculateBalanceOutput
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.transaction_repository import TransactionRepository


logger = logging.getLogger(__name__)


class CalculateBalanceUseCase:
    """
    Use case for calculating user's balance.
    
    Calculates:
    - Total income
    - Total expenses
    - Net balance (income - expenses)
    - Transaction count
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_repository: TransactionRepository
    ):
        self.user_repository = user_repository
        self.transaction_repository = transaction_repository
    
    async def execute(self, user_id: int) -> Result[CalculateBalanceOutput]:
        """
        Execute balance calculation.
        
        Args:
            user_id: User ID
            
        Returns:
            Result with CalculateBalanceOutput or error
        """
        try:
            # Verify user exists
            user = await self.user_repository.get_by_id(user_id)
            
            if not user:
                return Result.failure(
                    f"User {user_id} not found",
                    error_code="USER_NOT_FOUND"
                )
            
            # Calculate totals
            total_income = await self.transaction_repository.get_income_total(user_id)
            total_expense = await self.transaction_repository.get_expense_total(user_id)
            transaction_count = await self.transaction_repository.count_by_user(user_id)
            
            # Calculate balance
            balance = total_income - total_expense
            
            logger.info(
                f"Calculated balance for user {user_id}: "
                f"income={total_income}, expense={total_expense}, balance={balance}"
            )
            
            return Result.success(CalculateBalanceOutput(
                user_id=user_id,
                total_income=total_income,
                total_expense=total_expense,
                balance=balance,
                transaction_count=transaction_count
            ))
            
        except Exception as e:
            logger.error(f"Error calculating balance: {e}", exc_info=True)
            return Result.error(
                f"Failed to calculate balance: {str(e)}",
                error_code="CALCULATION_ERROR"
            )
