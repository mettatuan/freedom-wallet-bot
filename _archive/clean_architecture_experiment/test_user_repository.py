"""Tests for SQLAlchemyUserRepository."""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.config import Base
from src.infrastructure.database.user_repository_impl import SQLAlchemyUserRepository
from src.domain.entities.user import User
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
def user_repository(db_session):
    """Create UserRepository instance."""
    return SQLAlchemyUserRepository(db_session)


@pytest.mark.asyncio
async def test_save_new_user(user_repository):
    """Test saving a new user."""
    user = User(
        user_id=123456,
        telegram_username="testuser",
        email="test@example.com",
        phone="+84901234567",
        tier=UserTier.FREE
    )
    
    saved_user = await user_repository.save(user)
    
    assert saved_user.user_id == 123456
    assert saved_user.telegram_username == "testuser"
    assert saved_user.email == "test@example.com"
    assert saved_user.tier == UserTier.FREE


@pytest.mark.asyncio
async def test_get_by_id(user_repository):
    """Test getting user by ID."""
    user = User(user_id=123456, telegram_username="testuser", tier=UserTier.FREE)
    await user_repository.save(user)
    
    retrieved = await user_repository.get_by_id(123456)
    
    assert retrieved is not None
    assert retrieved.user_id == 123456
    assert retrieved.telegram_username == "testuser"


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_repository):
    """Test getting non-existent user."""
    retrieved = await user_repository.get_by_id(999999)
    
    assert retrieved is None


@pytest.mark.asyncio
async def test_update_user(user_repository):
    """Test updating existing user."""
    user = User(user_id=123456, telegram_username="testuser", tier=UserTier.FREE)
    await user_repository.save(user)
    
    # Update tier
    user.upgrade_to_unlock("https://sheets.google.com/test", "https://webapp.com/test")
    updated_user = await user_repository.save(user)
    
    assert updated_user.tier == UserTier.UNLOCK
    assert updated_user.sheet_url == "https://sheets.google.com/test"


@pytest.mark.asyncio
async def test_delete_user(user_repository):
    """Test deleting user."""
    user = User(user_id=123456, telegram_username="testuser", tier=UserTier.FREE)
    await user_repository.save(user)
    
    deleted = await user_repository.delete(123456)
    assert deleted is True
    
    retrieved = await user_repository.get_by_id(123456)
    assert retrieved is None


@pytest.mark.asyncio
async def test_find_by_tier(user_repository):
    """Test finding users by tier."""
    user1 = User(user_id=111, telegram_username="user1", tier=UserTier.FREE)
    user2 = User(user_id=222, telegram_username="user2", tier=UserTier.UNLOCK)
    user3 = User(user_id=333, telegram_username="user3", tier=UserTier.FREE)
    
    await user_repository.save(user1)
    await user_repository.save(user2)
    await user_repository.save(user3)
    
    free_users = await user_repository.find_by_tier(UserTier.FREE)
    
    assert len(free_users) == 2
    assert all(u.tier == UserTier.FREE for u in free_users)


@pytest.mark.asyncio
async def test_find_by_email(user_repository):
    """Test finding user by email."""
    user = User(
        user_id=123456,
        telegram_username="testuser",
        email="test@example.com",
        tier=UserTier.FREE
    )
    await user_repository.save(user)
    
    found = await user_repository.find_by_email("test@example.com")
    
    assert found is not None
    assert found.email == "test@example.com"


@pytest.mark.asyncio
async def test_count_by_tier(user_repository):
    """Test counting users by tier."""
    user1 = User(user_id=111, telegram_username="user1", tier=UserTier.FREE)
    user2 = User(user_id=222, telegram_username="user2", tier=UserTier.UNLOCK)
    user3 = User(user_id=333, telegram_username="user3", tier=UserTier.FREE)
    
    await user_repository.save(user1)
    await user_repository.save(user2)
    await user_repository.save(user3)
    
    free_count = await user_repository.count_by_tier(UserTier.FREE)
    unlock_count = await user_repository.count_by_tier(UserTier.UNLOCK)
    
    assert free_count == 2
    assert unlock_count == 1


@pytest.mark.asyncio
async def test_exists(user_repository):
    """Test checking if user exists."""
    user = User(user_id=123456, telegram_username="testuser", tier=UserTier.FREE)
    await user_repository.save(user)
    
    exists = await user_repository.exists(123456)
    not_exists = await user_repository.exists(999999)
    
    assert exists is True
    assert not_exists is False
