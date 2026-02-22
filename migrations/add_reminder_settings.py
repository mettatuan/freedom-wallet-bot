"""
Migration: Add reminder_hour, weekly_reminder_enabled, monthly_reminder_enabled to users table
Date: 2026-02-21
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
        ("reminder_hour",              "INTEGER DEFAULT 8"),
        ("weekly_reminder_enabled",    "BOOLEAN DEFAULT 1"),
        ("monthly_reminder_enabled",   "BOOLEAN DEFAULT 1"),
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


if __name__ == "__main__":
    print("🔄 Running migration: add_reminder_settings")
    run_migration()
    print("✅ Migration completed!")
