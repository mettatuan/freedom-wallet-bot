"""Check and migrate all CA tables"""
import sqlite3

db_path = "data/bot.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🔍 Checking current schema...\n")

# Check subscriptions
cursor.execute("PRAGMA table_info(subscriptions)")
sub_cols = cursor.fetchall()
print(f"📋 subscriptions table ({len(sub_cols)} columns):")
for col in sub_cols:
    print(f"   - {col[1]} ({col[2]})")

# Check transactions  
cursor.execute("PRAGMA table_info(transactions)")
trans_cols = cursor.fetchall()
print(f"\n📋 transactions table ({len(trans_cols)} columns):")
for col in trans_cols:
    print(f"   - {col[1]} ({col[2]})")

conn.close()

print("\n" + "="*60)
print("🔧 REQUIRED CA SCHEMA:")
print("="*60)

print("\n✅ subscriptions (CA):")
print("   - id (INTEGER PK)")
print("   - user_id (INTEGER FK)")
print("   - tier (VARCHAR)")
print("   - started_at (DATETIME) ← MISSING")
print("   - expires_at (DATETIME)")
print("   - auto_renew (BOOLEAN) ← MISSING")
print("   - last_payment_at (DATETIME) ← MISSING")
print("   - created_at (DATETIME)")
print("   - updated_at (DATETIME)")

print("\n✅ transactions (CA):")
print("   - transaction_id (VARCHAR PK)")
print("   - user_id (INTEGER FK)")
print("   - amount (NUMERIC)")
print("   - category (VARCHAR)")
print("   - date (DATETIME)")
print("   - note (TEXT)")
print("   - created_at (DATETIME)")
