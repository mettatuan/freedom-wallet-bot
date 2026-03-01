"""Check admin user DB state"""
import sqlite3
import sys
import os

DB = r"C:\FreedomWalletBot\data\bot.db"
ADMIN_ID = 6588506476

conn = sqlite3.connect(DB)
# Check admin user
row = conn.execute(
    "SELECT id, is_registered, web_app_url, user_status, admin_tag FROM users WHERE id=?",
    (ADMIN_ID,)
).fetchone()
print(f"Admin user ({ADMIN_ID}):", row)

# Check total users
total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
print(f"Total users: {total}")

# Check columns presence
cols = [r[1] for r in conn.execute("PRAGMA table_info(users)")]
for c in ["admin_tag", "user_status", "total_interactions"]:
    print(f"  column {c}: {'EXISTS' if c in cols else 'MISSING'}")

conn.close()
