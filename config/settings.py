import os
from dotenv import load_dotenv

# Explicitly load .env file from the project root directory
project_root = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path}")

"""
Configuration Settings for Freedom Wallet Bot
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Bot configuration loaded from environment variables"""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "FreedomWalletBot")
    ADMIN_USER_ID: Optional[int] = int(os.getenv("ADMIN_USER_ID", 0)) if os.getenv("ADMIN_USER_ID") else None  # Week 5: Fraud review admin
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", 1000))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/bot.db")
    
    # Google Sheets (for support tickets)
    GOOGLE_SHEETS_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    SUPPORT_SHEET_ID: Optional[str] = os.getenv("SUPPORT_SHEET_ID")
    SUPPORT_SHEET_NAME: str = os.getenv("SUPPORT_SHEET_NAME", "Support Tickets")
    
    # Freedom Wallet Template
    YOUR_TEMPLATE_ID: str = os.getenv("YOUR_TEMPLATE_ID", "")
    
    # Redis (for caching - Phase 3)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Rate Limiting
    MAX_MESSAGES_PER_MINUTE: int = int(os.getenv("MAX_MESSAGES_PER_MINUTE", 10))
    MAX_SUPPORT_TICKETS_PER_DAY: int = int(os.getenv("MAX_SUPPORT_TICKETS_PER_DAY", 3))
    
    # Context Memory
    CONTEXT_MEMORY_SIZE: int = int(os.getenv("CONTEXT_MEMORY_SIZE", 5))
    
    # Freedom Wallet API (Phase 3)
    FREEDOM_WALLET_API_URL: Optional[str] = os.getenv("FREEDOM_WALLET_API_URL")
    FREEDOM_WALLET_API_KEY: Optional[str] = os.getenv("FREEDOM_WALLET_API_KEY")
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "data/logs/bot.log")
    
    # Feature Flags
    ENABLE_AI: bool = os.getenv("ENABLE_AI", "False").lower() in ("true", "1", "t")
    ENABLE_VOICE: bool = os.getenv("ENABLE_VOICE", "False").lower() in ("true", "1", "t")
    ENABLE_ADMIN: bool = os.getenv("ENABLE_ADMIN", "False").lower() in ("true", "1", "t")
    
    # Payment Configuration
    PAYMENT_BANK_NAME: str = os.getenv("PAYMENT_BANK_NAME", "OCB")
    PAYMENT_ACCOUNT_NAME: str = os.getenv("PAYMENT_ACCOUNT_NAME", "PHAM THANH TUAN")
    PAYMENT_ACCOUNT_NUMBER: str = os.getenv("PAYMENT_ACCOUNT_NUMBER", "0107103241416363")
    PREMIUM_PRICE_VND: int = int(os.getenv("PREMIUM_PRICE_VND", "999000"))
    PAYMENT_QR_API: str = os.getenv("PAYMENT_QR_API", "https://img.vietqr.io/image/{bank_code}-{account_number}-{template}.jpg")
    
    class Config:
        # No longer need env_file here as we load it manually
        pass


# Global settings instance
settings = Settings()
