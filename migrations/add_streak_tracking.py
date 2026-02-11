"""
Database Migration - Add Streak Tracking Fields
Run this to add new columns to User table (SQLite compatible)
"""
from bot.utils.database import engine, Base, SessionLocal, User
from sqlalchemy import text, inspect
from loguru import logger


def column_exists(conn, table_name, column_name):
    """Check if column exists in SQLite table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_add_streak_fields():
    """Add streak tracking and reminder fields to users table (SQLite)"""
    try:
        # List of columns to add
        new_columns = {
            "last_transaction_date": "TIMESTAMP",
            "streak_count": "INTEGER DEFAULT 0",
            "longest_streak": "INTEGER DEFAULT 0",
            "total_transactions": "INTEGER DEFAULT 0",
            "milestone_7day_achieved": "BOOLEAN DEFAULT 0",
            "milestone_30day_achieved": "BOOLEAN DEFAULT 0",
            "milestone_90day_achieved": "BOOLEAN DEFAULT 0",
            "last_reminder_sent": "TIMESTAMP",
            "reminder_enabled": "BOOLEAN DEFAULT 1"
        }
        
        with engine.connect() as conn:
            for column_name, column_type in new_columns.items():
                # Check if column exists
                if column_exists(conn, 'users', column_name):
                    logger.info(f"⏭️  Column '{column_name}' already exists, skipping")
                    continue
                
                # Add column (SQLite syntax)
                cmd = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                try:
                    conn.execute(text(cmd))
                    conn.commit()
                    logger.info(f"✅ Added column: {column_name}")
                except Exception as e:
                    logger.error(f"❌ Error adding {column_name}: {e}")
            
            logger.info("✅ Migration completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    print("="*50)
    print("Running database migration for SQLite...")
    print("Adding streak tracking fields to users table...")
    print("="*50)
    migrate_add_streak_fields()
    print("\n✅ Migration completed! Restart your bot now.")
    print("="*50)
