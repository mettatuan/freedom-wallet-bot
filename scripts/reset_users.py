"""
Reset all user data from the database for clean testing.
Clears: users, referrals, conversation_context, payment_verifications, usage_tracking
Preserves: table schema
"""
import sqlite3
import os
import sys

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bot.db')
db_path = os.path.abspath(db_path)

print(f"\n📂 Database: {db_path}")
if not os.path.exists(db_path):
    print("❌ Database file not found!")
    sys.exit(1)

conn = sqlite3.connect(db_path)

# Show current state
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
tables = [t[0] for t in tables]
print(f"\n📋 Tables found: {tables}")
print("\n📊 Row counts BEFORE clear:")
for t in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
    print(f"   {t}: {count} rows")

# Tables to clear (ordering matters for FK constraints)
CLEAR_ORDER = [
    "payment_verifications",
    "usage_tracking",
    "conversation_context",
    "referrals",
    "users",
]

print("\n🧹 Clearing tables...")
conn.execute("PRAGMA foreign_keys = OFF")
for t in CLEAR_ORDER:
    if t in tables:
        conn.execute(f"DELETE FROM [{t}]")
        print(f"   ✅ Cleared: {t}")
    else:
        print(f"   ⏭  Skipped (not found): {t}")

# Also clear any other user-related tables
for t in tables:
    if t not in CLEAR_ORDER and t not in ("alembic_version", "sqlite_sequence"):
        conn.execute(f"DELETE FROM [{t}]")
        print(f"   ✅ Cleared extra: {t}")

# Reset auto-increment counters
try:
    conn.execute("DELETE FROM sqlite_sequence")
except Exception:
    pass  # sqlite_sequence may not exist if no AUTOINCREMENT tables

conn.execute("PRAGMA foreign_keys = ON")
conn.commit()

print("\n📊 Row counts AFTER clear:")
for t in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
    print(f"   {t}: {count} rows")

conn.close()
print("\n✅ Done! Database is clean. Bot can be restarted.\n")
