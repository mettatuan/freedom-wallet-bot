"""Check user's Web App URL and spreadsheet configuration"""
from bot.utils.database import SessionLocal, User

db = SessionLocal()

# User ID from logs
USER_ID = 1299465308

user = db.query(User).filter(User.id == USER_ID).first()

if user:
    print("=" * 60)
    print("USER CONFIGURATION")
    print("=" * 60)
    print(f"Telegram ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Spreadsheet ID: {user.spreadsheet_id or '❌ NOT SET'}")
    print(f"Web App URL: {user.web_app_url or '❌ NOT SET'}")
    print()
    
    if not user.web_app_url:
        print("⚠️  **PROBLEM FOUND!**")
        print("User does NOT have Web App URL saved!")
        print()
        print("SOLUTION:")
        print("User must run: /setwebapp <URL>")
    else:
        print("✅ User has Web App URL configured")
        print(f"URL: {user.web_app_url[:80]}...")
else:
    print(f"❌ User {USER_ID} not found in database")

db.close()
