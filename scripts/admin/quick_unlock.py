"""Quick unlock script - Auto unlock user 6194449688"""
from bot.utils.database import SessionLocal, User

def auto_unlock():
    user_id = 6194449688  # son23699
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ User {user_id} không tồn tại")
            return
        
        print(f"\n📊 BEFORE:")
        print(f"   User: {user.first_name} {user.last_name or ''}")
        print(f"   FREE: {user.is_free_unlocked}")
        print(f"   Refs: {user.referral_count}")
        
        # Unlock
        user.is_free_unlocked = True
        user.referral_count = 2
        db.commit()
        
        print(f"\n✅ UNLOCKED!")
        print(f"   FREE: {user.is_free_unlocked}")
        print(f"   Refs: {user.referral_count}")
        print(f"\n🎉 Sẵn sàng test! Mở Telegram bot và /start")
        
    finally:
        db.close()

if __name__ == "__main__":
    auto_unlock()
