"""
Migration: Add alert_enabled and notifications_enabled columns
Date: 2026-02-13
Purpose: Add notification preference columns to support new notification management system
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def migrate():
    """Add alert_enabled and notifications_enabled columns to users table"""
    db_path = Path(__file__).parent.parent / "data" / "bot.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        changes_made = False
        
        # Add alert_enabled column if not exists
        if 'alert_enabled' not in columns:
            print("➕ Adding alert_enabled column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN alert_enabled INTEGER DEFAULT 1
            """)
            changes_made = True
            print("✅ alert_enabled column added")
        else:
            print("ℹ️  alert_enabled column already exists")
        
        # Add notifications_enabled column if not exists
        if 'notifications_enabled' not in columns:
            print("➕ Adding notifications_enabled column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN notifications_enabled INTEGER DEFAULT 1
            """)
            changes_made = True
            print("✅ notifications_enabled column added")
        else:
            print("ℹ️  notifications_enabled column already exists")
        
        if changes_made:
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("✅ No changes needed - database already up to date")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Running migration: add_notification_columns")
    print("=" * 60)
    success = migrate()
    print("=" * 60)
    if success:
        print("✅ Migration complete!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)
