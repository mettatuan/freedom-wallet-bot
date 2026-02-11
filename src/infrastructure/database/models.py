"""SQLAlchemy database models."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .config import Base


class UserTierEnum(str, enum.Enum):
    """User tier enumeration for database."""
    FREE = "FREE"
    UNLOCK = "UNLOCK"
    PREMIUM = "PREMIUM"


class UserModel(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    telegram_username = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    tier = Column(SQLEnum(UserTierEnum), default=UserTierEnum.FREE, nullable=False, index=True)
    sheet_url = Column(String, nullable=True)
    webapp_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    subscription = relationship("SubscriptionModel", back_populates="user", uselist=False)
    transactions = relationship("TransactionModel", back_populates="user", cascade="all, delete-orphan")


class SubscriptionModel(Base):
    """Subscription database model."""
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    tier = Column(SQLEnum(UserTierEnum), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)
    auto_renew = Column(Boolean, default=False, nullable=False)
    last_payment_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="subscription")


class TransactionModel(Base):
    """Transaction database model."""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)  # Precision 15, Scale 2
    category = Column(String, nullable=False, index=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="transactions")
