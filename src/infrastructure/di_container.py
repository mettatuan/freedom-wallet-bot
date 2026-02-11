"""Dependency Injection Container for FreedomWalletBot."""

from typing import Optional
from sqlalchemy.orm import Session
from telegram import Bot

from ..domain.repositories.user_repository import UserRepository
from ..domain.repositories.subscription_repository import SubscriptionRepository
from ..domain.repositories.transaction_repository import TransactionRepository

from ..application.use_cases.register_user import RegisterUserUseCase
from ..application.use_cases.setup_sheet import SetupSheetUseCase
from ..application.use_cases.unlock_tier import UnlockTierUseCase
from ..application.use_cases.record_transaction import RecordTransactionUseCase
from ..application.use_cases.calculate_balance import CalculateBalanceUseCase

from .database import (
    SessionLocal,
    SQLAlchemyUserRepository,
    SQLAlchemySubscriptionRepository,
    SQLAlchemyTransactionRepository
)
from .telegram import TelegramAdapter
from .google_sheets import GoogleSheetsAdapter
from .ai import AIServiceAdapter


class DIContainer:
    """
    Dependency Injection Container for managing application dependencies.
    
    Responsibilities:
    - Create and manage repository instances
    - Create and manage use case instances
    - Create and manage adapter instances
    - Provide factory methods for dependency injection
    """
    
    def __init__(
        self,
        bot: Optional[Bot] = None,
        google_credentials_file: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        openai_model: str = "gpt-4"
    ):
        """
        Initialize DI Container.
        
        Args:
            bot: Telegram Bot instance
            google_credentials_file: Path to Google service account credentials
            openai_api_key: OpenAI API key
            openai_model: OpenAI model name
        """
        self.bot = bot
        self.google_credentials_file = google_credentials_file
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        
        # Lazy-initialized adapters
        self._telegram_adapter: Optional[TelegramAdapter] = None
        self._google_sheets_adapter: Optional[GoogleSheetsAdapter] = None
        self._ai_service_adapter: Optional[AIServiceAdapter] = None
    
    # === Database Session Factory ===
    
    def get_db_session(self) -> Session:
        """
        Get new database session.
        
        Returns:
            SQLAlchemy session
        """
        return SessionLocal()
    
    # === Repository Factories ===
    
    def get_user_repository(self, session: Optional[Session] = None) -> UserRepository:
        """
        Get UserRepository instance.
        
        Args:
            session: Optional SQLAlchemy session (creates new if None)
            
        Returns:
            UserRepository implementation
        """
        if session is None:
            session = self.get_db_session()
        
        return SQLAlchemyUserRepository(session)
    
    def get_subscription_repository(self, session: Optional[Session] = None) -> SubscriptionRepository:
        """
        Get SubscriptionRepository instance.
        
        Args:
            session: Optional SQLAlchemy session (creates new if None)
            
        Returns:
            SubscriptionRepository implementation
        """
        if session is None:
            session = self.get_db_session()
        
        return SQLAlchemySubscriptionRepository(session)
    
    def get_transaction_repository(self, session: Optional[Session] = None) -> TransactionRepository:
        """
        Get TransactionRepository instance.
        
        Args:
            session: Optional SQLAlchemy session (creates new if None)
            
        Returns:
            TransactionRepository implementation
        """
        if session is None:
            session = self.get_db_session()
        
        return SQLAlchemyTransactionRepository(session)
    
    # === Use Case Factories ===
    
    def get_register_user_use_case(self, session: Optional[Session] = None) -> RegisterUserUseCase:
        """
        Get RegisterUserUseCase instance.
        
        Args:
            session: Optional SQLAlchemy session
            
        Returns:
            RegisterUserUseCase instance
        """
        if session is None:
            session = self.get_db_session()
        
        user_repo = self.get_user_repository(session)
        subscription_repo = self.get_subscription_repository(session)
        
        return RegisterUserUseCase(user_repo, subscription_repo)
    
    def get_setup_sheet_use_case(self, session: Optional[Session] = None) -> SetupSheetUseCase:
        """
        Get SetupSheetUseCase instance.
        
        Args:
            session: Optional SQLAlchemy session
            
        Returns:
            SetupSheetUseCase instance
        """
        if session is None:
            session = self.get_db_session()
        
        user_repo = self.get_user_repository(session)
        subscription_repo = self.get_subscription_repository(session)
        
        return SetupSheetUseCase(user_repo, subscription_repo)
    
    def get_unlock_tier_use_case(self, session: Optional[Session] = None) -> UnlockTierUseCase:
        """
        Get UnlockTierUseCase instance.
        
        Args:
            session: Optional SQLAlchemy session
            
        Returns:
            UnlockTierUseCase instance
        """
        if session is None:
            session = self.get_db_session()
        
        user_repo = self.get_user_repository(session)
        subscription_repo = self.get_subscription_repository(session)
        
        return UnlockTierUseCase(user_repo, subscription_repo)
    
    def get_record_transaction_use_case(self, session: Optional[Session] = None) -> RecordTransactionUseCase:
        """
        Get RecordTransactionUseCase instance.
        
        Args:
            session: Optional SQLAlchemy session
            
        Returns:
            RecordTransactionUseCase instance
        """
        if session is None:
            session = self.get_db_session()
        
        user_repo = self.get_user_repository(session)
        transaction_repo = self.get_transaction_repository(session)
        
        return RecordTransactionUseCase(user_repo, transaction_repo)
    
    def get_calculate_balance_use_case(self, session: Optional[Session] = None) -> CalculateBalanceUseCase:
        """
        Get CalculateBalanceUseCase instance.
        
        Args:
            session: Optional SQLAlchemy session
            
        Returns:
            CalculateBalanceUseCase instance
        """
        if session is None:
            session = self.get_db_session()
        
        user_repo = self.get_user_repository(session)
        transaction_repo = self.get_transaction_repository(session)
        
        return CalculateBalanceUseCase(
            user_repository=user_repo,
            transaction_repository=transaction_repo
        )
    
    # === Adapter Factories ===
    
    def get_telegram_adapter(self) -> Optional[TelegramAdapter]:
        """
        Get TelegramAdapter instance (singleton).
        
        Returns:
            TelegramAdapter instance or None if bot not configured
        """
        if self._telegram_adapter is None and self.bot is not None:
            self._telegram_adapter = TelegramAdapter(self.bot)
        
        return self._telegram_adapter
    
    def get_google_sheets_adapter(self) -> Optional[GoogleSheetsAdapter]:
        """
        Get GoogleSheetsAdapter instance (singleton).
        
        Returns:
            GoogleSheetsAdapter instance or None if credentials not configured
        """
        if self._google_sheets_adapter is None and self.google_credentials_file is not None:
            self._google_sheets_adapter = GoogleSheetsAdapter(self.google_credentials_file)
        
        return self._google_sheets_adapter
    
    def get_ai_service_adapter(self) -> Optional[AIServiceAdapter]:
        """
        Get AIServiceAdapter instance (singleton).
        
        Returns:
            AIServiceAdapter instance or None if API key not configured
        """
        if self._ai_service_adapter is None and self.openai_api_key is not None:
            self._ai_service_adapter = AIServiceAdapter(
                api_key=self.openai_api_key,
                model=self.openai_model
            )
        
        return self._ai_service_adapter


# Global container instance (initialized in main.py)
_container: Optional[DIContainer] = None


def initialize_container(
    bot: Optional[Bot] = None,
    google_credentials_file: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    openai_model: str = "gpt-4"
) -> DIContainer:
    """
    Initialize global DI container.
    
    Args:
        bot: Telegram Bot instance
        google_credentials_file: Path to Google credentials
        openai_api_key: OpenAI API key
        openai_model: OpenAI model name
        
    Returns:
        Initialized DIContainer instance
    """
    global _container
    _container = DIContainer(
        bot=bot,
        google_credentials_file=google_credentials_file,
        openai_api_key=openai_api_key,
        openai_model=openai_model
    )
    return _container


def get_container() -> DIContainer:
    """
    Get global DI container instance.
    
    Returns:
        DIContainer instance
        
    Raises:
        RuntimeError: If container not initialized
    """
    if _container is None:
        raise RuntimeError(
            "DI Container not initialized. Call initialize_container() first."
        )
    
    return _container
