"""
Migration 001: Add State Machine & Program Tracking Columns
Week 1 - Foundation Phase
Date: 2026-02-08

Changes:
- Add state machine columns to users table
- Add fraud detection columns to referrals table
- Backfill existing user states based on referral_count
"""

import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from datetime import datetime

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def upgrade():
    """Apply migration"""
    session = SessionLocal()
    
    try:
        print("🚀 Starting Migration 001: State Machine Foundation")
        print("=" * 60)
        
        # ========== STEP 1: ADD NEW COLUMNS TO USERS TABLE ==========
        print("\n📝 Step 1: Adding state machine columns to users table...")
        
        user_columns = [
            ("user_state", "VARCHAR(20) DEFAULT 'LEGACY'"),
            ("current_program", "VARCHAR(50) NULL"),
            ("program_day", "INTEGER DEFAULT 0"),
            ("program_started_at", "TIMESTAMP NULL"),
            ("program_completed_at", "TIMESTAMP NULL"),
            ("super_vip_last_active", "TIMESTAMP NULL"),
            ("super_vip_decay_warned", "BOOLEAN DEFAULT 0"),
            ("show_on_leaderboard", "BOOLEAN DEFAULT 1"),
        ]
        
        for column_name, column_def in user_columns:
            try:
                session.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"))
                print(f"   ✅ Added column: {column_name}")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"   ⚠️  Column {column_name} already exists, skipping")
                else:
                    raise e
        
        session.commit()
        print("   ✅ All user columns added successfully")
        
        # ========== STEP 2: ADD FRAUD DETECTION TO REFERRALS ==========
        print("\n🔍 Step 2: Adding fraud detection to referrals table...")
        
        referral_columns = [
            ("ip_address", "VARCHAR(45) NULL"),
            ("user_agent", "VARCHAR(255) NULL"),
            ("device_fingerprint", "VARCHAR(64) NULL"),
            ("velocity_score", "INTEGER DEFAULT 0"),
            ("review_status", "VARCHAR(20) DEFAULT 'AUTO_APPROVED'"),
            ("reviewed_by", "INTEGER NULL"),
            ("reviewed_at", "TIMESTAMP NULL"),
        ]
        
        for column_name, column_def in referral_columns:
            try:
                session.execute(text(f"ALTER TABLE referrals ADD COLUMN {column_name} {column_def}"))
                print(f"   ✅ Added column: {column_name}")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"   ⚠️  Column {column_name} already exists, skipping")
                else:
                    raise e
        
        session.commit()
        print("   ✅ All referral columns added successfully")
        
        # ========== STEP 3: BACKFILL EXISTING USER STATES ==========
        print("\n🔄 Step 3: Backfilling existing user states...")
        
        # Get all users with their referral count
        result = session.execute(text("""
            SELECT id, username, referral_count, is_free_unlocked, created_at
            FROM users
            WHERE user_state = 'LEGACY'
        """))
        users = result.fetchall()
        
        backfill_stats = {
            "VISITOR": 0,
            "REGISTERED": 0,
            "VIP": 0,
        }
        
        for user in users:
            user_id, username, ref_count, is_free, created_at = user
            
            # Determine state based on existing data
            if is_free or ref_count >= 2:
                new_state = "VIP"
                backfill_stats["VIP"] += 1
            elif ref_count >= 1 or username:  # Has started using bot
                new_state = "REGISTERED"
                backfill_stats["REGISTERED"] += 1
            else:
                new_state = "VISITOR"
                backfill_stats["VISITOR"] += 1
            
            # Update user state
            session.execute(text(f"""
                UPDATE users 
                SET user_state = '{new_state}'
                WHERE id = {user_id}
            """))
        
        session.commit()
        
        print(f"   ✅ Migrated {len(users)} users:")
        for state, count in backfill_stats.items():
            print(f"      • {state}: {count} users")
        
        # ========== STEP 4: VERIFY MIGRATION ==========
        print("\n✅ Step 4: Verifying migration...")
        
        # Check columns exist
        result = session.execute(text("PRAGMA table_info(users)"))
        user_cols = [row[1] for row in result.fetchall()]
        
        required_cols = ["user_state", "current_program", "program_day"]
        missing_cols = [col for col in required_cols if col not in user_cols]
        
        if missing_cols:
            raise Exception(f"Missing columns: {missing_cols}")
        
        print(f"   ✅ All required columns present in users table")
        
        # Check state distribution
        result = session.execute(text("""
            SELECT user_state, COUNT(*) as count
            FROM users
            GROUP BY user_state
        """))
        
        print("   📊 Current state distribution:")
        for row in result.fetchall():
            state, count = row
            print(f"      • {state}: {count} users")
        
        print("\n" + "=" * 60)
        print("🎉 Migration 001 completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        session.rollback()
        raise e
    finally:
        session.close()


def downgrade():
    """Revert migration (if needed)"""
    session = SessionLocal()
    
    try:
        print("⏪ Reverting Migration 001...")
        
        # Drop columns from users
        user_columns = [
            "user_state", "current_program", "program_day", 
            "program_started_at", "program_completed_at",
            "super_vip_last_active", "super_vip_decay_warned", "show_on_leaderboard"
        ]
        
        for col in user_columns:
            try:
                session.execute(text(f"ALTER TABLE users DROP COLUMN {col}"))
                print(f"   ✅ Dropped column: {col}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {col}: {e}")
        
        # Drop columns from referrals
        referral_columns = [
            "ip_address", "user_agent", "device_fingerprint",
            "velocity_score", "review_status", "reviewed_by", "reviewed_at"
        ]
        
        for col in referral_columns:
            try:
                session.execute(text(f"ALTER TABLE referrals DROP COLUMN {col}"))
                print(f"   ✅ Dropped column: {col}")
            except Exception as e:
                print(f"   ⚠️  Could not drop {col}: {e}")
        
        session.commit()
        print("✅ Migration reverted successfully")
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
