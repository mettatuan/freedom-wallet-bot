"""
Force clean migration: Drop and recreate users table with CA schema
"""

import sqlite3

db_path = "D:/Projects/FreedomWalletBot/data/bot.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("🔄 Starting CLEAN migration...")
    
    # 1. Drop users_legacy if exists
    cursor.execute("DROP TABLE IF EXISTS users_legacy")
    print("✅ Dropped users_legacy if it existed")
    
    # 2. Rename current users table
    cursor.execute("ALTER TABLE users RENAME TO users_legacy")
    print("✅ Renamed users → users_legacy")
    
    # 3. Create new users table with CA schema
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
    
    # 4. Copy data from legacy to new schema
    cursor.execute("""
        INSERT INTO users (user_id, telegram_username, email, phone, tier, sheet_url, webapp_url, created_at, updated_at)
        SELECT 
            id,
            username,
            email,
            phone,
            CASE 
                WHEN subscription_tier = 'premium' THEN 'PREMIUM'
                WHEN subscription_tier = 'unlock' OR subscription_tier IS NOT NULL THEN 'UNLOCK'
                ELSE 'FREE'
            END as tier,
            spreadsheet_id,
            web_app_url,
            created_at,
            COALESCE(last_active, created_at)
        FROM users_legacy
    """)
    
    rows_migrated = cursor.rowcount
    print(f"✅ Migrated {rows_migrated} users from legacy schema")
    
    conn.commit()
    print("\n🎉 Migration complete!")
    print(f"✅ {rows_migrated} users now in Clean Architecture schema")
    print("\nOld table preserved as 'users_legacy' for safety.")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    conn.rollback()
    print("Database rolled back")
finally:
    conn.close()
