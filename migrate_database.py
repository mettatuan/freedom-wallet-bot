"""
Phase 3: Database Migration Script
Backup old database and create new schema with Transaction table
"""
import os
import shutil
from datetime import datetime
from pathlib import Path

# Database file path
DB_PATH = Path("data/bot.db")
BACKUP_DIR = Path("data/backups")

def backup_database():
    """Backup existing database"""
    if not DB_PATH.exists():
        print(f"ℹ️ No existing database found at {DB_PATH}")
        return None
    
    # Create backup directory
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"bot_db_backup_{timestamp}.db"
    
    # Copy database
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    
    return backup_path


def recreate_database():
    """Delete old database and recreate with new schema"""
    
    # Backup first
    backup_path = backup_database()
    
    # Delete old database
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"✅ Old database deleted")
    
    # Import database module to trigger table creation
    print(f"📦 Importing database models...")
    from bot.utils.database import Base, engine
    
    # Create all tables
    print(f"🔨 Creating database tables...")
    Base.metadata.create_all(engine)
    
    print(f"✅ New database created at: {DB_PATH}")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📊 Created {len(tables)} tables:")
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"   ✅ {table} ({len(columns)} columns)")
    
    print(f"\n🎉 Database migration complete!")
    print(f"   Old database backed up to: {backup_path}")
    print(f"   New database ready at: {DB_PATH}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 PHASE 3: DATABASE MIGRATION")
    print("="*60)
    print(f"This will backup and recreate the database with new schema")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        recreate_database()
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS: Database migration completed")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR: Database migration failed")
        print(f"Error: {e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
