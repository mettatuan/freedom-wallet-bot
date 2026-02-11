"""
Debug user connection - Check nếu user có spreadsheet_id
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, User

# Check user bạn đang test (admin user)
user_id = 6588506476  # Thay bằng user ID bạn test

db = next(get_db())
user = db.query(User).filter(User.id == user_id).first()

print("\n" + "="*80)
print(f"🔍 USER CONNECTION CHECK - ID: {user_id}")
print("="*80)

if user:
    print(f"\n✅ User found: {user.username}")
    print(f"   Full name: {user.full_name}")
    print(f"   Subscription: {user.subscription_tier}")
    print(f"   Spreadsheet ID: {user.spreadsheet_id or '❌ NOT SET'}")
    print(f"   Web App URL: {user.web_app_url[:60] if user.web_app_url else '❌ NOT SET'}...")
    print(f"   Registered: {user.is_registered}")
    
    print("\n" + "-"*80)
    if user.spreadsheet_id:
        print("✅ QUICK RECORD SHOULD WORK")
        print("   ✓ User có Spreadsheet connected")
        print(f"   ✓ Subscription tier: {user.subscription_tier}")
    else:
        print("❌ QUICK RECORD WILL NOT WORK")
        print("   ✗ User chưa có Spreadsheet ID")
        print("   → Bot sẽ trả lời: 'Bạn chưa kết nối Google Sheets!'")
        print("   → Message sẽ pass xuống AI handler")
else:
    print(f"\n❌ User {user_id} not found in database!")

print("\n" + "="*80 + "\n")

db.close()
