"""RecordTransactionUseCase - handles recording financial transactions."""

import logging
from datetime import datetime
from decimal import Decimal

from ..common.result import Result
from ..dtos import RecordTransactionInput, RecordTransactionOutput, TransactionDTO
from ...domain.entities.transaction import Transaction
from ...domain.repositories.user_repository import UserRepository
from ...domain.repositories.transaction_repository import TransactionRepository


logger = logging.getLogger(__name__)


class RecordTransactionUseCase:
    """
    Use case for recording a financial transaction.
    
    Business Rules:
    - User must exist
    - Amount must be non-zero
    - Category must be provided
    - Calculates balance after transaction
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        transaction_repository: TransactionRepository
    ):
        self.user_repository = user_repository
        self.transaction_repository = transaction_repository
    
    async def execute(self, input_data: RecordTransactionInput) -> Result[RecordTransactionOutput]:
        """
        Execute transaction recording.
        
        Args:
            input_data: Transaction input data
            
        Returns:
            Result with RecordTransactionOutput or error
        """
        try:
            # Verify user exists
            user = await self.user_repository.get_by_id(input_data.user_id)
            
            if not user:
                return Result.failure(
                    f"User {input_data.user_id} not found",
                    error_code="USER_NOT_FOUND"
                )
            
            # Create transaction entity
            try:
                transaction = Transaction(
                    user_id=input_data.user_id,
                    amount=input_data.amount,
                    category=input_data.category,
                    date=input_data.date or datetime.utcnow(),
                    note=input_data.note
                )
            except ValueError as e:
                return Result.failure(str(e), error_code="INVALID_TRANSACTION")
            
            # Save transaction
            saved_transaction = await self.transaction_repository.save(transaction)
            logger.info(
                f"Recorded transaction for user {input_data.user_id}: "
                f"{saved_transaction.formatted_amount()} in {saved_transaction.category}"
            )
            
            # Calculate current balance
            total_income = await self.transaction_repository.get_income_total(
                input_data.user_id
            )
            total_expense = await self.transaction_repository.get_expense_total(
                input_data.user_id
            )
            
            balance = total_income - total_expense
            
            return Result.success(RecordTransactionOutput(
                transaction=self._transaction_to_dto(saved_transaction),
                balance=balance
            ))
            
        except Exception as e:
            logger.error(f"Error recording transaction: {e}", exc_info=True)
            return Result.error(
                f"Failed to record transaction: {str(e)}",
                error_code="RECORD_ERROR"
            )
    
    def _transaction_to_dto(self, transaction: Transaction) -> TransactionDTO:
        """Convert Transaction entity to TransactionDTO."""
        return TransactionDTO(
            user_id=transaction.user_id,
            amount=transaction.amount,
            category=transaction.category,
            date=transaction.date,
            note=transaction.note,
            transaction_id=transaction.transaction_id,
            formatted_amount=transaction.formatted_amount()
        )
