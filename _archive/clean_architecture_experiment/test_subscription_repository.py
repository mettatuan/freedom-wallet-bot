"""Tests for SQLAlchemySubscriptionRepository."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.config import Base
from src.infrastructure.database.subscription_repository_impl import SQLAlchemySubscriptionRepository
from src.domain.entities.subscription import Subscription
from src.domain.value_objects.user_tier import UserTier


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def subscription_repository(db_session):
    """Create SubscriptionRepository instance."""
    return SQLAlchemySubscriptionRepository(db_session)


@pytest.mark.asyncio
async def test_save_new_subscription(subscription_repository):
    """Test saving a new subscription."""
    subscription = Subscription(user_id=123456, tier=UserTier.FREE)
    
    saved = await subscription_repository.save(subscription)
    
    assert saved.user_id == 123456
    assert saved.tier == UserTier.FREE
    assert saved.expires_at is None  # FREE never expires


@pytest.mark.asyncio
async def test_get_by_user_id(subscription_repository):
    """Test getting subscription by user ID."""
    subscription = Subscription(user_id=123456, tier=UserTier.UNLOCK, expires_at=datetime.utcnow() + timedelta(days=30))
    await subscription_repository.save(subscription)
    
    retrieved = await subscription_repository.get_by_user_id(123456)
    
    assert retrieved is not None
    assert retrieved.user_id == 123456
    assert retrieved.tier == UserTier.UNLOCK


@pytest.mark.asyncio
async def test_update_subscription(subscription_repository):
    """Test updating existing subscription."""
    subscription = Subscription(user_id=123456, tier=UserTier.UNLOCK, expires_at=datetime.utcnow() + timedelta(days=30))
    await subscription_repository.save(subscription)
    
    # Upgrade to premium
    subscription.tier = UserTier.PREMIUM
    subscription.auto_renew = True
    
    updated = await subscription_repository.save(subscription)
    
    assert updated.tier == UserTier.PREMIUM
    assert updated.auto_renew is True


@pytest.mark.asyncio
async def test_delete_subscription(subscription_repository):
    """Test deleting subscription."""
    subscription = Subscription(user_id=123456, tier=UserTier.FREE)
    await subscription_repository.save(subscription)
    
    deleted = await subscription_repository.delete(123456)
    assert deleted is True
    
    retrieved = await subscription_repository.get_by_user_id(123456)
    assert retrieved is None


@pytest.mark.asyncio
async def test_find_expiring_soon(subscription_repository):
    """Test finding subscriptions expiring soon."""
    now = datetime.utcnow()
    
    # Expires in 5 days (should be found)
    sub1 = Subscription(user_id=111, tier=UserTier.UNLOCK, expires_at=now + timedelta(days=5))
    # Expires in 15 days (should NOT be found with 7-day window)
    sub2 = Subscription(user_id=222, tier=UserTier.UNLOCK, expires_at=now + timedelta(days=15))
    # Already expired
    sub3 = Subscription(user_id=333, tier=UserTier.UNLOCK, expires_at=now - timedelta(days=1))
    
    await subscription_repository.save(sub1)
    await subscription_repository.save(sub2)
    await subscription_repository.save(sub3)
    
    expiring = await subscription_repository.find_expiring_soon(days=7)
    
    assert len(expiring) == 1
    assert expiring[0].user_id == 111


@pytest.mark.asyncio
async def test_find_expired(subscription_repository):
    """Test finding expired subscriptions."""
    now = datetime.utcnow()
    grace_period = Subscription.GRACE_PERIOD_DAYS
    
    # Expired beyond grace period
    sub1 = Subscription(user_id=111, tier=UserTier.UNLOCK, expires_at=now - timedelta(days=grace_period + 5))
    # Still in grace period
    sub2 = Subscription(user_id=222, tier=UserTier.UNLOCK, expires_at=now - timedelta(days=grace_period - 1))
    # Active
    sub3 = Subscription(user_id=333, tier=UserTier.UNLOCK, expires_at=now + timedelta(days=10))
    
    await subscription_repository.save(sub1)
    await subscription_repository.save(sub2)
    await subscription_repository.save(sub3)
    
    expired = await subscription_repository.find_expired()
    
    assert len(expired) == 1
    assert expired[0].user_id == 111


@pytest.mark.asyncio
async def test_count_active(subscription_repository):
    """Test counting active subscriptions."""
    now = datetime.utcnow()
    
    sub1 = Subscription(user_id=111, tier=UserTier.FREE)  # No expiry
    sub2 = Subscription(user_id=222, tier=UserTier.UNLOCK, expires_at=now + timedelta(days=30))  # Active
    sub3 = Subscription(user_id=333, tier=UserTier.UNLOCK, expires_at=now - timedelta(days=10))  # Expired
    
    await subscription_repository.save(sub1)
    await subscription_repository.save(sub2)
    await subscription_repository.save(sub3)
    
    active_count = await subscription_repository.count_active()
    
    assert active_count == 2  # sub1 and sub2


@pytest.mark.asyncio
async def test_count_by_tier(subscription_repository):
    """Test counting subscriptions by tier."""
    sub1 = Subscription(user_id=111, tier=UserTier.FREE)
    sub2 = Subscription(user_id=222, tier=UserTier.UNLOCK, expires_at=datetime.utcnow() + timedelta(days=30))
    sub3 = Subscription(user_id=333, tier=UserTier.FREE)
    
    await subscription_repository.save(sub1)
    await subscription_repository.save(sub2)
    await subscription_repository.save(sub3)
    
    free_count = await subscription_repository.count_by_tier(UserTier.FREE)
    unlock_count = await subscription_repository.count_by_tier(UserTier.UNLOCK)
    
    assert free_count == 2
    assert unlock_count == 1
