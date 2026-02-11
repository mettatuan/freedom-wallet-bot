"""Update Web App URL for user"""
from bot.utils.database import SessionLocal, User

db = SessionLocal()
USER_ID = 1299465308
NEW_URL = "https://script.google.com/macros/s/AKfycbw2pEp-fWuvdndvuM9HiynoZUreK4iOQxdXlvm_Cb6GX6VDCpl02rzG-Hp7h21E48qkag/exec"

user = db.query(User).filter(User.id == USER_ID).first()

if user:
    old_url = user.web_app_url
    user.web_app_url = NEW_URL
    db.commit()
    
    print("=" * 60)
    print("✅ WEB APP URL UPDATED")
    print("=" * 60)
    print(f"User ID: {USER_ID}")
    print(f"Username: {user.username}")
    print(f"\nOld URL: {old_url[:80] if old_url else 'NOT SET'}...")
    print(f"\nNew URL: {NEW_URL}")
    print("=" * 60)
else:
    print(f"❌ User {USER_ID} not found")

db.close()
