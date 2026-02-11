"""
Migrate subscriptions and transactions to Clean Architecture schema
"""
import sqlite3
from datetime import datetime

db_path = "data/bot.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("🔄 Migrating subscriptions table...\n")
    
    # 1. Backup and rename existing table
    cursor.execute("DROP TABLE IF EXISTS subscriptions_legacy")
    cursor.execute("ALTER TABLE subscriptions RENAME TO subscriptions_legacy")
    print("✅ Renamed subscriptions → subscriptions_legacy")
    
    # 2. Create new subscriptions table with CA schema
    cursor.execute("""
        CREATE TABLE subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            tier VARCHAR(20) NOT NULL,
            started_at DATETIME NOT NULL,
            expires_at DATETIME,
            auto_renew BOOLEAN NOT NULL DEFAULT 0,
            last_payment_at DATETIME,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    print("✅ Created new subscriptions table")
    
    # 3. Migrate data
    cursor.execute("""
        INSERT INTO subscriptions 
        (id, user_id, tier, started_at, expires_at, auto_renew, last_payment_at, created_at, updated_at)
        SELECT 
            id,
            user_id,
            tier,
            COALESCE(start_date, CURRENT_TIMESTAMP) as started_at,
            end_date as expires_at,
            COALESCE(auto_renew, 0) as auto_renew,
            NULL as last_payment_at,
            COALESCE(start_date, CURRENT_TIMESTAMP) as created_at,
            COALESCE(start_date, CURRENT_TIMESTAMP) as updated_at
        FROM subscriptions_legacy
    """)
    sub_count = cursor.rowcount
    print(f"✅ Migrated {sub_count} subscriptions")
    
    print("\n🔄 Migrating transactions table...\n")
    
    # 4. Backup and rename transactions
    cursor.execute("DROP TABLE IF EXISTS transactions_legacy")
    cursor.execute("ALTER TABLE transactions RENAME TO transactions_legacy")
    print("✅ Renamed transactions → transactions_legacy")
    
    # 5. Create new transactions table
    cursor.execute("""
        CREATE TABLE transactions (
            transaction_id VARCHAR(36) PRIMARY KEY,
            user_id INTEGER NOT NULL,
            amount NUMERIC(15, 2) NOT NULL,
            category VARCHAR(100),
            date DATETIME NOT NULL,
            note TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    print("✅ Created new transactions table")
    
    # 6. Migrate transactions data
    cursor.execute("""
        INSERT INTO transactions 
        (transaction_id, user_id, amount, category, date, note, created_at)
        SELECT 
            COALESCE(transaction_id, 'tx_' || id) as transaction_id,
            user_id,
            amount,
            category,
            date,
            note,
            COALESCE(created_at, CURRENT_TIMESTAMP) as created_at
        FROM transactions_legacy
    """)
    trans_count = cursor.rowcount
    print(f"✅ Migrated {trans_count} transactions")
    
    conn.commit()
    
    print("\n" + "="*60)
    print("🎉 MIGRATION COMPLETE!")
    print("="*60)
    print(f"✅ Subscriptions: {sub_count} rows")
    print(f"✅ Transactions: {trans_count} rows")
    print("\nOld tables preserved as *_legacy for safety")
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    conn.rollback()
    print("Database rolled back")
    raise
finally:
    conn.close()
