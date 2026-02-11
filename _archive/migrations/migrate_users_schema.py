"""
Quick fix: Migrate legacy users table to Clean Architecture schema.

This script will:
1. Backup existing users table
2. Rename it to users_legacy
3. Create new users table with CA schema
4. Copy data from legacy to new schema
"""

import sqlite3

db_path = "D:/Projects/FreedomWalletBot/data/bot.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("🔄 Starting migration...")
    
    # 1. Rename existing users table
    cursor.execute("ALTER TABLE users RENAME TO users_legacy")
    print("✅ Renamed users → users_legacy")
    
    # 2. Create new users table with CA schema
    cursor.execute("""
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            telegram_username VARCHAR(100),
            email VARCHAR(255),
            phone VARCHAR(50),
            tier VARCHAR(20) NOT NULL DEFAULT 'FREE',
            sheet_url VARCHAR(500),
            webapp_url VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created new users table with CA schema")
    
    # 3. Copy data from legacy to new schema
    cursor.execute("""
        INSERT INTO users (user_id, telegram_username, email, phone, tier, sheet_url, webapp_url, created_at, updated_at)
        SELECT 
            id,
            username,
            email,
            phone,
            CASE 
                WHEN subscription_tier = 'premium' THEN 'PREMIUM'
                WHEN subscription_tier = 'unlock' THEN 'UNLOCK'
                ELSE 'FREE'
            END as tier,
            spreadsheet_id,
            web_app_url,
            created_at,
            last_active
        FROM users_legacy
    """)
    
    rows_migrated = cursor.rowcount
    print(f"✅ Migrated {rows_migrated} users from legacy schema")
    
    conn.commit()
    print("\n🎉 Migration complete!")
    print("\nOld table preserved as 'users_legacy' for safety.")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    conn.rollback()
    print("Database rolled back to previous state")
finally:
    conn.close()
