"""
Migration: Add google_sheets_url column to users table
Date: 2026-02-21
"""
import sys
import os
# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from config.settings import settings
from loguru import logger

def run_migration():
    """Add google_sheets_url column to users table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM pragma_table_info('users') 
                WHERE name='google_sheets_url'
            """))
            
            if result.scalar() == 0:
                # Column doesn't exist, add it
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN google_sheets_url VARCHAR(500)
                """))
                conn.commit()
                logger.info("✅ Added google_sheets_url column to users table")
            else:
                logger.info("⏭️ Column google_sheets_url already exists, skipping")
                
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    print("🔄 Running migration: add_google_sheets_url")
    run_migration()
    print("✅ Migration completed!")
