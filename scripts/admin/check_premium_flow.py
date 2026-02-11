"""
Premium & Trial User Flow Comprehensive Check
Kiểm tra toàn bộ flow từ đăng ký → thanh toán → duyệt → user nhận Premium
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, User, PaymentVerification
from datetime import datetime

def check_premium_flow():
    """Check complete premium flow"""
    
    print("\n" + "="*80)
    print("🔍 PREMIUM & TRIAL USER FLOW CHECK")
    print("="*80)
    
    db = next(get_db())
    
    # 1. Check admin user (test case)
    print("\n📝 STEP 1: CHECK ADMIN USER (PREMIUM)")
    print("-" * 80)
    
    admin_id = 6588506476
    admin = db.query(User).filter(User.id == admin_id).first()
    
    if admin:
        print(f"✅ Admin found: {admin.username}")
        print(f"   - Full name: {admin.full_name or 'Not set'}")
        print(f"   - Email: {admin.email or 'Not set'}")
        print(f"   - Phone: {admin.phone or 'Not set'}")
        print(f"   - Subscription: {admin.subscription_tier}")
        print(f"   - Premium expires: {admin.premium_expires_at or 'Not set'}")
        print(f"   - Spreadsheet ID: {admin.spreadsheet_id or 'Not set'}")
        print(f"   - Web App URL: {admin.web_app_url[:60] if admin.web_app_url else 'Not set'}...")
        print(f"   - Registered: {admin.is_registered}")
    else:
        print(f"❌ Admin user not found")
    
    # 2. Check payment verifications
    print("\n📝 STEP 2: CHECK PAYMENT VERIFICATIONS")
    print("-" * 80)
    
    verifications = db.query(PaymentVerification).order_by(
        PaymentVerification.created_at.desc()
    ).limit(5).all()
    
    if verifications:
        print(f"✅ Found {len(verifications)} recent payments:")
        for v in verifications:
            user = db.query(User).filter(User.id == v.user_id).first()
            username = user.username if user else "Unknown"
            print(f"\n   ID: VER{v.id}")
            print(f"   - User: {username} ({v.user_id})")
            print(f"   - Amount: {v.amount:,} VND")
            print(f"   - Status: {v.status}")
            print(f"   - Created: {v.created_at}")
            if v.status == "APPROVED":
                print(f"   - Approved by: {v.approved_by}")
                print(f"   - Approved at: {v.approved_at}")
    else:
        print("⚠️ No payment verifications found")
    
    # 3. Check Premium users
    print("\n📝 STEP 3: CHECK PREMIUM USERS")
    print("-" * 80)
    
    premium_users = db.query(User).filter(
        User.subscription_tier == "PREMIUM"
    ).all()
    
    if premium_users:
        print(f"✅ Found {len(premium_users)} Premium users:")
        for user in premium_users[:10]:  # Top 10
            print(f"\n   User: {user.username or 'No username'} ({user.id})")
            print(f"   - Full name: {user.full_name or 'Not set'}")
            print(f"   - Subscription: {user.subscription_tier}")
            print(f"   - Expires: {user.premium_expires_at or 'Not set'}")
            print(f"   - Spreadsheet: {user.spreadsheet_id or 'Not connected'}")
            print(f"   - Email: {user.email or 'Not set'}")
            print(f"   - Registered: {user.is_registered}")
    else:
        print("⚠️ No Premium users found")
    
    # 4. Check Trial users
    print("\n📝 STEP 4: CHECK TRIAL USERS")
    print("-" * 80)
    
    trial_users = db.query(User).filter(
        User.subscription_tier == "TRIAL"
    ).all()
    
    if trial_users:
        print(f"✅ Found {len(trial_users)} Trial users:")
        for user in trial_users[:10]:
            print(f"\n   User: {user.username or 'No username'} ({user.id})")
            print(f"   - Subscription: {user.subscription_tier}")
            print(f"   - Trial ends: {user.trial_ends_at or 'Not set'}")
            print(f"   - Started: {user.premium_started_at or 'Not set'}")
    else:
        print("⚠️ No Trial users found")
    
    # 5. Check users with spreadsheet connection
    print("\n📝 STEP 5: CHECK USERS WITH SPREADSHEET CONNECTION")
    print("-" * 80)
    
    users_with_sheets = db.query(User).filter(
        User.spreadsheet_id != None,
        User.spreadsheet_id != ""
    ).all()
    
    if users_with_sheets:
        print(f"✅ Found {len(users_with_sheets)} users with Sheets connected:")
        for user in users_with_sheets[:5]:
            print(f"\n   User: {user.username or 'No username'} ({user.id})")
            print(f"   - Spreadsheet ID: {user.spreadsheet_id}")
            print(f"   - Web App URL: {user.web_app_url[:60] if user.web_app_url else 'Not set'}...")
            print(f"   - Subscription: {user.subscription_tier}")
    else:
        print("⚠️ No users with Spreadsheet connection")
    
    # 6. Flow Analysis
    print("\n📝 STEP 6: FLOW ANALYSIS")
    print("-" * 80)
    
    total_users = db.query(User).count()
    registered_users = db.query(User).filter(User.is_registered == True).count()
    premium_count = db.query(User).filter(User.subscription_tier == "PREMIUM").count()
    trial_count = db.query(User).filter(User.subscription_tier == "TRIAL").count()
    free_count = db.query(User).filter(User.subscription_tier == "FREE").count()
    
    print(f"\n📊 STATISTICS:")
    print(f"   Total users: {total_users}")
    print(f"   Registered users: {registered_users} ({registered_users/total_users*100:.1f}%)")
    print(f"   Premium users: {premium_count} ({premium_count/total_users*100:.1f}%)")
    print(f"   Trial users: {trial_count} ({trial_count/total_users*100:.1f}%)")
    print(f"   Free users: {free_count} ({free_count/total_users*100:.1f}%)")
    
    # 7. Check missing fields for Premium users
    print("\n📝 STEP 7: CHECK PREMIUM USERS MISSING FIELDS")
    print("-" * 80)
    
    premium_users_all = db.query(User).filter(User.subscription_tier == "PREMIUM").all()
    
    missing_issues = []
    for user in premium_users_all:
        issues = []
        if not user.spreadsheet_id:
            issues.append("No Spreadsheet ID")
        if not user.web_app_url:
            issues.append("No Web App URL")
        if not user.email:
            issues.append("No Email")
        if not user.premium_expires_at:
            issues.append("No expiry date")
        
        if issues:
            missing_issues.append({
                'user': user.username or f"User {user.id}",
                'issues': issues
            })
    
    if missing_issues:
        print(f"⚠️ Found {len(missing_issues)} Premium users with missing data:")
        for item in missing_issues[:10]:
            print(f"\n   User: {item['user']}")
            print(f"   Missing: {', '.join(item['issues'])}")
    else:
        print("✅ All Premium users have complete data")
    
    # 8. Suggested Actions
    print("\n📝 STEP 8: SUGGESTED ACTIONS")
    print("-" * 80)
    
    print("\n🎯 TO-DO for Premium Flow:")
    print("   1. ✅ Category matching (FIXED with 50+ keywords)")
    print("   2. ✅ API connection (FIXED with correct key)")
    print("   3. ✅ Sheets integration (FIXED with web_app_url)")
    print("   4. ⚠️ Auto-set spreadsheet_id after payment approval")
    print("   5. ⚠️ Send onboarding message to new Premium users")
    print("   6. ⚠️ Add guide: 'How to connect Sheets'")
    print("   7. ⚠️ Add expiry reminder (7 days before)")
    
    print("\n🎯 TO-DO for Trial Flow:")
    print("   1. ✅ Trial start working (7 days)")
    print("   2. ⚠️ Trial expiry notification")
    print("   3. ⚠️ Upgrade prompt before expiry")
    print("   4. ⚠️ Auto-downgrade after trial ends")
    
    db.close()
    
    print("\n" + "="*80)
    print("✅ FLOW CHECK COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    check_premium_flow()
