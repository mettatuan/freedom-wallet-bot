"""Infrastructure layer."""

from .database import (
    Base,
    engine,
    SessionLocal,
    get_db,
    init_db,
    drop_db,
    UserModel,
    SubscriptionModel,
    TransactionModel,
    SQLAlchemyUserRepository,
    SQLAlchemySubscriptionRepository,
    SQLAlchemyTransactionRepository
)
from .telegram import TelegramAdapter
from .google_sheets import GoogleSheetsAdapter
from .ai import AIServiceAdapter
from .di_container import DIContainer, initialize_container, get_container

__all__ = [
    # Database
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_db",
    "drop_db",
    "UserModel",
    "SubscriptionModel",
    "TransactionModel",
    "SQLAlchemyUserRepository",
    "SQLAlchemySubscriptionRepository",
    "SQLAlchemyTransactionRepository",
    # Adapters
    "TelegramAdapter",
    "GoogleSheetsAdapter",
    "AIServiceAdapter",
    # DI Container
    "DIContainer",
    "initialize_container",
    "get_container",
]
