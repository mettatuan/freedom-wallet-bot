"""
Database Migration: Add VIP Identity Tier Fields
Migration Date: Feb 10, 2026
Phase: Phase 1 - Three Tier Strategy

Changes:
- Add vip_tier field (VARCHAR 20)
- Add vip_unlocked_at field (TIMESTAMP)
- Add vip_benefits field (TEXT)

VIP Tiers:
- RISING_STAR (10 refs)
- SUPER_VIP (50 refs)
- LEGEND (100 refs)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import Column, String, DateTime, Text
from bot.utils.database import engine, Base, SessionLocal, User
from loguru import logger


def upgrade():
    """Add VIP fields to users table"""
    from sqlalchemy import inspect, text
    
    logger.info("🔄 Starting VIP fields migration...")
    
    # Check if columns already exist
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    with engine.connect() as conn:
        # Add vip_tier column
        if 'vip_tier' not in columns:
            logger.info("➕ Adding vip_tier column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN vip_tier VARCHAR(20) DEFAULT NULL
            """))
            conn.commit()
            logger.info("✅ Added vip_tier column")
        else:
            logger.info("⏭️ vip_tier column already exists")
        
        # Add vip_unlocked_at column
        if 'vip_unlocked_at' not in columns:
            logger.info("➕ Adding vip_unlocked_at column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN vip_unlocked_at TIMESTAMP DEFAULT NULL
            """))
            conn.commit()
            logger.info("✅ Added vip_unlocked_at column")
        else:
            logger.info("⏭️ vip_unlocked_at column already exists")
        
        # Add vip_benefits column
        if 'vip_benefits' not in columns:
            logger.info("➕ Adding vip_benefits column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN vip_benefits TEXT DEFAULT '[]'
            """))
            conn.commit()
            logger.info("✅ Added vip_benefits column")
        else:
            logger.info("⏭️ vip_benefits column already exists")
    
    logger.info("✅ VIP fields migration completed successfully!")


def downgrade():
    """Remove VIP fields from users table"""
    from sqlalchemy import text
    
    logger.info("🔄 Rolling back VIP fields migration...")
    
    with engine.connect() as conn:
        logger.info("➖ Dropping vip_tier column...")
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS vip_tier"))
        conn.commit()
        
        logger.info("➖ Dropping vip_unlocked_at column...")
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS vip_unlocked_at"))
        conn.commit()
        
        logger.info("➖ Dropping vip_benefits column...")
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS vip_benefits"))
        conn.commit()
    
    logger.info("✅ Rollback completed successfully!")


def verify():
    """Verify migration was successful"""
    from sqlalchemy import inspect
    
    logger.info("🔍 Verifying migration...")
    
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    required_columns = ['vip_tier', 'vip_unlocked_at', 'vip_benefits']
    missing = [col for col in required_columns if col not in columns]
    
    if missing:
        logger.error(f"❌ Migration verification FAILED! Missing columns: {missing}")
        return False
    
    logger.info("✅ Migration verification PASSED!")
    logger.info(f"   Found all required columns: {required_columns}")
    
    # Test write/read
    session = SessionLocal()
    try:
        # Get first user (or create test user)
        user = session.query(User).first()
        if user:
            logger.info(f"📊 Testing with user {user.id}...")
            
            # Test fields are accessible
            _ = user.vip_tier
            _ = user.vip_unlocked_at
            _ = user.vip_benefits
            
            logger.info("✅ All VIP fields are readable!")
        else:
            logger.warning("⚠️ No users in database to test with")
    except Exception as e:
        logger.error(f"❌ Field access test FAILED: {e}")
        return False
    finally:
        session.close()
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='VIP Fields Database Migration')
    parser.add_argument('action', choices=['upgrade', 'downgrade', 'verify'],
                       help='Migration action to perform')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'upgrade':
            upgrade()
            verify()
        elif args.action == 'downgrade':
            downgrade()
        elif args.action == 'verify':
            success = verify()
            sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        sys.exit(1)
