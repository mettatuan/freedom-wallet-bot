"""
Update admin user's spreadsheet_id and webapp_url
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, User


def update_admin_user():
    """Update admin user with correct spreadsheet and webapp URL"""
    
    print("\n" + "="*70)
    print("📝 UPDATE ADMIN USER - SPREADSHEET & WEBAPP URL")
    print("="*70 + "\n")
    
    admin_id = 6588506476
    spreadsheet_id = "1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI"
    webapp_url = "https://script.google.com/macros/s/AKfycbw2pEp-fWuvdndvuM9HiynoZUreK4iOQxdXlvm_Cb6GX6VDCpl02rzG-Hp7h21E48qkag/exec"
    
    print(f"Admin ID: {admin_id}")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print(f"WebApp URL: {webapp_url}")
    
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.id == admin_id).first()
        
        if not user:
            print(f"\n❌ User {admin_id} not found!")
            return
        
        print(f"\n✅ User found: {user.full_name or user.username}")
        print(f"   Current spreadsheet_id: {user.spreadsheet_id}")
        print(f"   Current web_app_url: {user.web_app_url}")
        
        # Update both fields
        user.spreadsheet_id = spreadsheet_id
        user.web_app_url = webapp_url
        db.commit()
        
        print(f"\n✅ Updated successfully:")
        print(f"   spreadsheet_id: {spreadsheet_id}")
        print(f"   web_app_url: {webapp_url}")
        
        # Verify
        db.refresh(user)
        print(f"\n📋 Verification:")
        print(f"   User: {user.full_name or user.username}")
        print(f"   Spreadsheet ID: {user.spreadsheet_id}")
        print(f"   WebApp URL: {user.web_app_url}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    print(f"\n{'='*70}")
    print("✅ UPDATE COMPLETE")
    print(f"{'='*70}\n")
    print("💡 Now run: python test_get_categories_api.py to test")


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Update Admin User\n")
    update_admin_user()
