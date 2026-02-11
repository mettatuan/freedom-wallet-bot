import sqlite3
import os

db_path = "D:/Projects/FreedomWalletBot/data/bot.db"

if os.path.exists(db_path):
    print(f"✅ Database exists: {db_path}")
    print(f"📦 Size: {os.path.getsize(db_path)} bytes")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n📋 Tables ({len(tables)}):")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Get users table schema
    if any('users' in str(table) for table in tables):
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print(f"\n👤 users table columns ({len(columns)}):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
    
    conn.close()
else:
    print(f"❌ Database not found: {db_path}")
