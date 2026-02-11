"""
Update webapp URL mới sau khi deploy Apps Script
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from bot.utils.database import SessionLocal, User

def update_webapp_url():
    db = SessionLocal()
    try:
        # Admin user ID
        user_id = 6588506476
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ User {user_id} not found!")
            return
        
        print(f"\n📝 Before:")
        print(f"   Telegram: @{user.username}")
        print(f"   Spreadsheet ID: {user.spreadsheet_id}")
        print(f"   Old Webapp URL: {user.web_app_url}")
        
        # Update với URL mới
        new_url = "https://script.google.com/macros/s/AKfycbxuVMMtTGXIrWphC3qzTTm5uudBLWunQzWONDEFX8RAoi3AiL0fXUbPz9MpEv_IWOpZ/exec"
        user.web_app_url = new_url
        
        db.commit()
        
        print(f"\n✅ After:")
        print(f"   New Webapp URL: {user.web_app_url}")
        print(f"\n🎉 Update successful!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_webapp_url()
