"""
Migration: Add usage tracking and subscription tier columns
Run: python migrations/add_usage_tracking.py
"""
from sqlalchemy import create_engine, text
from config.settings import settings
from loguru import logger

def upgrade():
    """Add columns for usage tracking and subscription management"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Add subscription tier columns
            logger.info("Adding subscription_tier column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS subscription_tier TEXT DEFAULT 'FREE'
            """))
            
            logger.info("Adding premium_started_at column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS premium_started_at TIMESTAMP
            """))
            
            logger.info("Adding premium_expires_at column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS premium_expires_at TIMESTAMP
            """))
            
            logger.info("Adding trial_ends_at column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMP
            """))
            
            # Add usage tracking columns
            logger.info("Adding bot_chat_count column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS bot_chat_count INTEGER DEFAULT 0
            """))
            
            logger.info("Adding bot_chat_limit_date column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS bot_chat_limit_date DATE
            """))
            
            logger.info("Adding premium_features_used column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS premium_features_used TEXT DEFAULT '{}'
            """))
            
            # Add fraud tracking columns (for future use)
            logger.info("Adding ip_address column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS ip_address TEXT
            """))
            
            logger.info("Adding device_fingerprint column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS device_fingerprint TEXT
            """))
            
            logger.info("Adding last_referral_at column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS last_referral_at TIMESTAMP
            """))
            
            logger.info("Adding referral_velocity column...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS referral_velocity INTEGER DEFAULT 0
            """))
            
            conn.commit()
            logger.info("✅ Migration completed successfully!")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Migration failed: {e}")
            raise

def downgrade():
    """Remove added columns (rollback)"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            columns = [
                'subscription_tier', 'premium_started_at', 'premium_expires_at',
                'trial_ends_at', 'bot_chat_count', 'bot_chat_limit_date',
                'premium_features_used', 'ip_address', 'device_fingerprint',
                'last_referral_at', 'referral_velocity'
            ]
            
            for col in columns:
                logger.info(f"Removing {col} column...")
                conn.execute(text(f"ALTER TABLE users DROP COLUMN IF EXISTS {col}"))
            
            conn.commit()
            logger.info("✅ Rollback completed!")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Rollback failed: {e}")
            raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        print("Rolling back migration...")
        downgrade()
    else:
        print("Running migration...")
        upgrade()
