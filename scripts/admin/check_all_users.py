"""Check all users' webapp URLs"""
import asyncio
from bot.utils.database import SessionLocal, User

def check_all_users():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.web_app_url.isnot(None)).all()
        
        print(f"\n{'='*80}")
        print(f"📊 FOUND {len(users)} USERS WITH WEB APP URL")
        print(f"{'='*80}\n")
        
        for user in users:
            print(f"👤 User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Full Name: {user.full_name}")
            print(f"   Tier: {user.subscription_tier}")
            print(f"   📊 Spreadsheet: {user.spreadsheet_id}")
            print(f"   🌐 Web App URL: {user.web_app_url}")
            print(f"   {'─'*80}\n")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_all_users()
