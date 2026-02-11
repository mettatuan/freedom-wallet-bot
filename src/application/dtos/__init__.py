"""DTOs (Data Transfer Objects) for use cases."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal

from ...domain.value_objects.user_tier import UserTier


@dataclass
class UserDTO:
    """User data transfer object."""
    user_id: int
    telegram_username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    tier: UserTier = UserTier.FREE
    sheet_url: Optional[str] = None
    webapp_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SubscriptionDTO:
    """Subscription data transfer object."""
    user_id: int
    tier: UserTier
    started_at: datetime
    expires_at: Optional[datetime] = None
    auto_renew: bool = False
    is_active: bool = True
    days_until_expiry: Optional[int] = None


@dataclass
class TransactionDTO:
    """Transaction data transfer object."""
    user_id: int
    amount: Decimal
    category: str
    date: datetime
    note: Optional[str] = None
    transaction_id: Optional[str] = None
    formatted_amount: Optional[str] = None


@dataclass
class RegisterUserInput:
    """Input for RegisterUserUseCase."""
    telegram_user_id: int
    telegram_username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class RegisterUserOutput:
    """Output for RegisterUserUseCase."""
    user: UserDTO
    subscription: SubscriptionDTO
    is_new_user: bool


@dataclass
class SetupSheetInput:
    """Input for SetupSheetUseCase."""
    user_id: int
    sheet_url: str
    webapp_url: str
    email: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class SetupSheetOutput:
    """Output for SetupSheetUseCase."""
    user: UserDTO
    subscription: SubscriptionDTO
    upgraded_to_unlock: bool


@dataclass
class UnlockTierInput:
    """Input for UnlockTierUseCase."""
    user_id: int
    sheet_url: str
    webapp_url: str


@dataclass
class UnlockTierOutput:
    """Output for UnlockTierUseCase."""
    user: UserDTO
    subscription: SubscriptionDTO


@dataclass
class RecordTransactionInput:
    """Input for RecordTransactionUseCase."""
    user_id: int
    amount: Decimal
    category: str
    note: Optional[str] = None
    date: Optional[datetime] = None


@dataclass
class RecordTransactionOutput:
    """Output for RecordTransactionUseCase."""
    transaction: TransactionDTO
    balance: Decimal


@dataclass
class CalculateBalanceOutput:
    """Output for CalculateBalanceUseCase."""
    user_id: int
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    transaction_count: int
