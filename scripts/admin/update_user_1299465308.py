"""Update webapp URL for user 1299465308 (Mettatuan)"""
import asyncio
from bot.utils.database import SessionLocal, User

def update_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1299465308).first()
        
        if not user:
            print("❌ User 1299465308 not found!")
            return
            
        old_url = user.web_app_url
        new_url = "https://script.google.com/macros/s/AKfycbxuVMMtTGXIrWphC3qzTTm5uudBLWunQzWONDEFX8RAoi3AiL0fXUbPz9MpEv_IWOpZ/exec"
        
        print(f"\n{'='*80}")
        print(f"🔧 UPDATING USER 1299465308 (Mettatuan)")
        print(f"{'='*80}\n")
        print(f"👤 User: {user.username} ({user.full_name})")
        print(f"📊 Spreadsheet: {user.spreadsheet_id}")
        print(f"\n❌ OLD URL:\n   {old_url}")
        print(f"\n✅ NEW URL:\n   {new_url}")
        
        user.web_app_url = new_url
        db.commit()
        
        print(f"\n{'='*80}")
        print(f"✅ UPDATED SUCCESSFULLY!")
        print(f"{'='*80}\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    update_user()
