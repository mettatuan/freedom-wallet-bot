"""
Update admin user spreadsheet_id in database
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, User
from config.settings import settings


def update_admin_spreadsheet():
    """Update spreadsheet_id for admin user"""
    
    print("\n" + "="*70)
    print("📝 UPDATE ADMIN SPREADSHEET ID")
    print("="*70 + "\n")
    
    admin_id = settings.ADMIN_USER_ID
    # Hardcode spreadsheet ID from .env TEST_SPREADSHEET_ID
    spreadsheet_id = "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg"
    
    print(f"Admin ID: {admin_id}")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.id == admin_id).first()
        
        if not user:
            print(f"\n❌ User {admin_id} not found!")
            return
        
        print(f"\n✅ User found: {user.full_name or user.username}")
        print(f"   Current spreadsheet_id: {user.spreadsheet_id}")
        
        # Update
        user.spreadsheet_id = spreadsheet_id
        db.commit()
        
        print(f"\n✅ Updated spreadsheet_id to: {spreadsheet_id}")
        print(f"   User can now access categories from Google Sheets!")
        
        # Verify
        db.refresh(user)
        print(f"\n📋 Verification:")
        print(f"   User: {user.full_name or user.username}")
        print(f"   Spreadsheet ID: {user.spreadsheet_id}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()
    
    print(f"\n{'='*70}")
    print("✅ UPDATE COMPLETE")
    print(f"{'='*70}\n")
    print("💡 Now run: python test_get_categories_api.py to test")


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Update Admin Spreadsheet\n")
    
    confirm = input("⚠️  This will update admin user's spreadsheet_id. Continue? (y/N): ")
    if confirm.lower() == 'y':
        update_admin_spreadsheet()
    else:
        print("❌ Cancelled")
