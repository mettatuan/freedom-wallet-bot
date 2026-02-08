"""
Database Migration Script
Add registration fields to User table
"""
import sqlite3
from config.settings import settings

def migrate():
    """Run migration to add new columns"""
    print("🔧 Running database migration...")
    
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Add new columns (ignore if already exist)
        columns_to_add = [
            ("email", "VARCHAR(255)"),
            ("phone", "VARCHAR(50)"),
            ("full_name", "VARCHAR(255)"),
            ("is_registered", "BOOLEAN DEFAULT 0")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⏭️  Column {col_name} already exists, skipping")
                else:
                    raise
        
        conn.commit()
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"📊 Total users: {count}")
        
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
