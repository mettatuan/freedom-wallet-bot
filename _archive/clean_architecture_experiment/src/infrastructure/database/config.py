"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
import sys
from pathlib import Path

# Add project root to path to import settings
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from config.settings import settings
    # Use the same DATABASE_URL as legacy code for compatibility
    DATABASE_URL = settings.DATABASE_URL
except ImportError:
    # Fallback if settings can't be imported
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/bot.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database (create all tables)."""
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
