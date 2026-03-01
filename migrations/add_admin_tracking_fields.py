"""
Migration: Add admin_tag, user_status, interaction tracking fields to users table
Date: 2026-03-01
Purpose: Enhanced admin user management and interaction tracking
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config.settings import settings
from loguru import logger


def run_migration():
    engine = create_engine(settings.DATABASE_URL)
    columns = [
        # Admin management fields
        ("admin_tag",              "TEXT DEFAULT NULL"),  # Admin's personal note for user
        ("user_status",            "VARCHAR(50) DEFAULT 'PENDING'"),  # PENDING, WEBAPP_SETUP, ACTIVE, INACTIVE, CHURNED
        
        # Enhanced interaction tracking
        ("total_interactions",     "INTEGER DEFAULT 0"),  # Total bot interactions (messages, commands, callbacks)
        ("last_command",           "VARCHAR(100) DEFAULT NULL"),  # Last command executed
        ("last_command_at",        "TIMESTAMP DEFAULT NULL"),  # When last command was executed
        ("daily_active_days",      "INTEGER DEFAULT 0"),  # Count of days user was active
        ("last_daily_reset",       "TIMESTAMP DEFAULT NULL"),  # Last time daily stats were reset
        
        # Engagement metrics
        ("first_seen_at",          "TIMESTAMP DEFAULT NULL"),  # First interaction with bot
        ("activation_source",      "VARCHAR(50) DEFAULT 'BOT'"),  # BOT, LANDING_PAGE, REFERRAL
    ]
    
    with engine.connect() as conn:
        for col_name, col_def in columns:
            try:
                result = conn.execute(text(
                    f"SELECT COUNT(*) FROM pragma_table_info('users') WHERE name='{col_name}'"
                ))
                if result.scalar() == 0:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"))
                    conn.commit()
                    logger.info(f"✅ Added column '{col_name}' to users table")
                else:
                    logger.info(f"⏭️  Column '{col_name}' already exists, skipping")
            except Exception as e:
                logger.error(f"❌ Failed to add column {col_name}: {e}")
                raise
        
        # Initialize user_status based on current data
        try:
            # Users with web_app_url = ACTIVE
            conn.execute(text("""
                UPDATE users 
                SET user_status = 'ACTIVE' 
                WHERE web_app_url IS NOT NULL 
                  AND web_app_url != '' 
                  AND web_app_url != 'pending'
                  AND user_status = 'PENDING'
            """))
            
            # Registered but no webapp = WEBAPP_SETUP
            conn.execute(text("""
                UPDATE users 
                SET user_status = 'WEBAPP_SETUP' 
                WHERE is_registered = 1 
                  AND (web_app_url IS NULL OR web_app_url = '' OR web_app_url = 'pending')
                  AND user_status = 'PENDING'
            """))
            
            # Initialize first_seen_at from created_at if null
            conn.execute(text("""
                UPDATE users 
                SET first_seen_at = created_at 
                WHERE first_seen_at IS NULL
            """))
            
            conn.commit()
            logger.info("✅ Initialized user_status and first_seen_at for existing users")
        except Exception as e:
            logger.error(f"❌ Failed to initialize data: {e}")
            raise


if __name__ == "__main__":
    print("🔄 Running migration: add_admin_tracking_fields")
    run_migration()
    print("✅ Migration completed!")
