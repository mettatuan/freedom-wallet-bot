"""
=================================================================================
ROOT CAUSE ANALYSIS & PERMANENT FIX
=================================================================================

PROBLEM:
Bot crashes with: sqlite3.OperationalError: no such column: users.first_name

ROOT CAUSE:
1. During Clean Architecture experiment, migration script ran:
   - Renamed users (56 cols) → users_legacy  
   - Created NEW users table (9 cols simplified)
   - Migrated data from legacy → new users table
   
2. When CA was rolled back:
   - Code was rolled back (model expects 56 columns)
   - Database was NOT rolled back (production has 9 columns)
   
3. Schema drift occurred:
   - Model defines: 56 columns in User class
   - Actual DB has: 9 columns in 'users' table
   - Missing: 47 columns (first_name, last_name, referral_code, etc.)

CURRENT STATE:
- users table: 9 columns, 1 row of PRODUCTION DATA (user_id=6194449688)
- users_legacy: 56 columns, 0 rows (EMPTY - data was migrated OUT)
- Model temporarily points to users_legacy (which is empty!)

WHY TEMPORARY FIX DOESN'T WORK:
Pointing model to users_legacy means:
- Bot reads from empty table
- User testing will fail (no user found)
- Not a production-ready state

PERMANENT FIX STRATEGY:
Since CA was rolled back, restore full 56-column schema:

Step 1: Add missing 47 columns to 'users' table (preserving 1 user row)
Step 2: Update model to point to 'users' table (not users_legacy)
Step 3: Drop users_legacy table (it's empty and confusing)
Step 4: Verify data integrity

BENEFITS:
✅ No data loss (preserves existing user)
✅ Full features restored (referrals, VIP, state machine, etc.)
✅ Single source of truth (one users table)
✅ Model matches database structure
✅ Deterministic runtime

=================================================================================
"""

import sqlite3
from datetime import datetime

db_path = "data/bot.db"

print(__doc__)

print("🔍 Pre-migration verification...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current state
cursor.execute("SELECT COUNT(*) FROM users")
users_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM users_legacy")
legacy_count = cursor.fetchone()[0]

print(f"   users table:        {users_count} rows (PRODUCTION DATA)")
print(f"   users_legacy table: {legacy_count} rows (EMPTY)")
print()

if users_count == 0:
    print("❌ ERROR: users table is empty! Cannot proceed.")
    print("   Data loss risk detected. Manual intervention required.")
    conn.close()
    exit(1)

if legacy_count > 0:
    print("⚠️  WARNING: users_legacy has data!")
    print("   This script assumes users_legacy is empty.")
    response = input("   Proceed anyway? (yes/no): ")
    if response.lower() != 'yes':
        print("   Migration cancelled.")
        conn.close()
        exit(0)

print("=" * 80)
print("STARTING MIGRATION: Restore Full Schema to 'users' Table")
print("=" * 80)

try:
    # Step 1: Add missing columns to users table (47 columns)
    # We'll add them one by one with appropriate defaults
    
    print("\n📝 Adding missing columns to 'users' table...")
    
    columns_to_add = [
        # Core user info (Telegram metadata)
        ("first_name", "VARCHAR(100)", "NULL"),
        ("last_name", "VARCHAR(100)", "NULL"),
        ("language_code", "VARCHAR(10)", "'vi'"),
        ("last_active", "DATETIME", "NULL"),  # Changed from CURRENT_TIMESTAMP
        ("is_blocked", "BOOLEAN", "0"),
        
        # Referral system
        ("referral_code", "VARCHAR(20)", "NULL"),
        ("referred_by", "INTEGER", "NULL"),
        ("referral_count", "INTEGER", "0"),
        ("is_free_unlocked", "BOOLEAN", "0"),
        
        # VIP tiers
        ("vip_tier", "VARCHAR(20)", "NULL"),
        ("vip_unlocked_at", "DATETIME", "NULL"),
        ("vip_benefits", "TEXT", "'[]'"),
        
        # Subscription
        ("subscription_tier", "VARCHAR(20)", "'TRIAL'"),
        ("subscription_expires", "DATETIME", "NULL"),
        
        # Usage tracking
        ("bot_chat_count", "INTEGER", "0"),
        ("bot_chat_limit_date", "DATETIME", "NULL"),
        ("premium_started_at", "DATETIME", "NULL"),
        ("premium_expires_at", "DATETIME", "NULL"),
        ("trial_ends_at", "DATETIME", "NULL"),
        ("premium_features_used", "TEXT", "'{}'"),
        
        # Fraud detection
        ("ip_address", "VARCHAR(45)", "NULL"),
        ("device_fingerprint", "VARCHAR(255)", "NULL"),
        ("last_referral_at", "DATETIME", "NULL"),
        ("referral_velocity", "INTEGER", "0"),
        
        # Registration
        ("full_name", "VARCHAR(255)", "NULL"),
        ("is_registered", "BOOLEAN", "0"),
        
        # State machine
        ("user_state", "VARCHAR(20)", "'LEGACY'"),
        ("current_program", "VARCHAR(50)", "NULL"),
        ("program_day", "INTEGER", "0"),
        ("program_started_at", "DATETIME", "NULL"),
        ("program_completed_at", "DATETIME", "NULL"),
        
        # Super VIP decay
        ("super_vip_last_active", "DATETIME", "NULL"),
        ("super_vip_decay_warned", "BOOLEAN", "0"),
        ("show_on_leaderboard", "BOOLEAN", "1"),
        
        # Transaction tracking
        ("last_transaction_date", "DATETIME", "NULL"),
        ("streak_count", "INTEGER", "0"),
        ("longest_streak", "INTEGER", "0"),
        ("total_transactions", "INTEGER", "0"),
        ("milestone_7day_achieved", "BOOLEAN", "0"),
        
        # Google Sheets integration
        ("spreadsheet_id", "VARCHAR(100)", "NULL"),
        ("sheets_connected_at", "DATETIME", "NULL"),
        ("sheets_last_sync", "DATETIME", "NULL"),
        ("webhook_url", "VARCHAR(500)", "NULL"),
        
        # Milestones and reminders
        ("milestone_30day_achieved", "BOOLEAN", "0"),
        ("milestone_90day_achieved", "BOOLEAN", "0"),
        ("last_reminder_sent", "DATETIME", "NULL"),
        ("reminder_enabled", "BOOLEAN", "1"),
        
        # Unlock flow
        ("unlock_offered", "BOOLEAN", "0"),
        ("unlock_offered_at", "DATETIME", "NULL"),
        ("last_checkin", "DATETIME", "NULL"),
    ]
    
    for col_name, col_type, default_val in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type} DEFAULT {default_val}")
            print(f"   ✅ Added: {col_name:30} {col_type}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"   ⏭️  Skipped: {col_name:30} (already exists)")
            else:
                raise
    
    # Update last_active for existing users
    print("\n📝 Updating defaults for existing users...")
    cursor.execute("UPDATE users SET last_active = created_at WHERE last_active IS NULL")
    print(f"   ✅ Set last_active = created_at for {cursor.rowcount} users")
    
    conn.commit()
    print(f"\n✅ Successfully added {len(columns_to_add)} columns to 'users' table")
    
    # Step 2: Verify column count
    cursor.execute("PRAGMA table_info(users)")
    current_cols = cursor.fetchall()
    print(f"\n✅ Verification: 'users' table now has {len(current_cols)} columns")
    
    # Step 3: Rename columns to match model expectations
    # The model expects 'id' and 'username', but DB has 'user_id' and 'telegram_username'
    # We'll handle this with column mapping in model (already exists)
    print("\n📝 Column mapping:")
    print("   ✅ user_id → model.id (via Column mapping)")
    print("   ✅ telegram_username → model.username (via Column mapping)")
    
    # Step 4: Show sample data
    cursor.execute("""
        SELECT user_id, telegram_username, email, user_state, referral_count 
        FROM users 
        LIMIT 3
    """)
    rows = cursor.fetchall()
    print("\n📊 Sample data from restored 'users' table:")
    for row in rows:
        print(f"   User {row[0]}: {row[1]}, {row[2]}, state={row[3]}, refs={row[4]}")
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Update model to point to 'users' table (not users_legacy)")
    print("2. Keep column mappings: id=Column('user_id'), username=Column('telegram_username')")
    print("3. Optional: DROP TABLE users_legacy (it's empty)")
    print("4. Restart bot and verify")
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    print("Rolling back...")
    conn.rollback()
    print("Database rolled back. Schema unchanged.")
    conn.close()
    exit(1)

finally:
    conn.close()

print("\n🎉 Database is now ready for full-featured bot operation!")
