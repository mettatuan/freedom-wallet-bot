"""
Simple migration script - NO emoji, safe for Windows cp1252 encoding.
Adds missing columns to the users table on VPS.
"""
import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bot.db")
print(f"DB path: {DB_PATH}")
print(f"DB exists: {os.path.exists(DB_PATH)}")

conn = sqlite3.connect(DB_PATH)

# Get current columns
cols = [r[1] for r in conn.execute("PRAGMA table_info(users)")]
print(f"Current columns: {cols}")

NEW_COLUMNS = [
    ("admin_tag",            "TEXT"),
    ("user_status",          "TEXT DEFAULT 'PENDING'"),
    ("total_interactions",   "INTEGER DEFAULT 0"),
    ("last_command",         "TEXT"),
    ("last_command_at",      "DATETIME"),
    ("daily_active_days",    "INTEGER DEFAULT 0"),
    ("last_daily_reset",     "DATETIME"),
    ("first_seen_at",        "DATETIME"),
    ("activation_source",    "TEXT"),
]

added = []
skipped = []

for col_name, col_def in NEW_COLUMNS:
    if col_name not in cols:
        try:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
            added.append(col_name)
            print(f"  ADDED: {col_name}")
        except Exception as e:
            print(f"  ERROR adding {col_name}: {e}")
    else:
        skipped.append(col_name)
        print(f"  SKIP (exists): {col_name}")

conn.commit()
conn.close()

print(f"\nDone. Added: {added}")
print(f"Skipped (already existed): {skipped}")

# Verify
conn2 = sqlite3.connect(DB_PATH)
final_cols = [r[1] for r in conn2.execute("PRAGMA table_info(users)")]
conn2.close()
print(f"Final columns: {final_cols}")

missing = [c for c, _ in NEW_COLUMNS if c not in final_cols]
if missing:
    print(f"STILL MISSING: {missing}")
    sys.exit(1)
else:
    print("SUCCESS: All required columns present.")
    sys.exit(0)
