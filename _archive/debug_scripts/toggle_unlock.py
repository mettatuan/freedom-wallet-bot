"""Toggle FREE unlock status để test cả hai flows"""
from bot.utils.database import SessionLocal, User
import sys

def toggle_unlock(user_id: int, force_lock: bool = False):
    """Toggle hoặc force lock user để test"""
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ User {user_id} không tồn tại")
            return
        
        print(f"\n📊 TRẠNG THÁI HIỆN TẠI:")
        print(f"   User: {user.first_name} {user.last_name or ''} (@{user.username or 'N/A'})")
        print(f"   FREE Unlocked: {user.is_free_unlocked}")
        print(f"   Referral Count: {user.referral_count}")
        
        if force_lock or user.is_free_unlocked:
            # Lock user (set to 0 refs để test unlock flow)
            user.is_free_unlocked = False
            user.referral_count = 0
            db.commit()
            
            print(f"\n🔒 ĐÃ LOCK USER!")
            print(f"   FREE Unlocked: {user.is_free_unlocked}")
            print(f"   Referral Count: {user.referral_count}")
            print(f"\n🧪 Bây giờ /start bot để test flow CHƯA UNLOCK")
            print(f"   Message sẽ hiển thị: Cách mở khóa + 2 referrals")
        else:
            # Unlock user
            user.is_free_unlocked = True
            user.referral_count = 2
            db.commit()
            
            print(f"\n🔓 ĐÃ UNLOCK USER!")
            print(f"   FREE Unlocked: {user.is_free_unlocked}")
            print(f"   Referral Count: {user.referral_count}")
            print(f"\n🧪 Bây giờ /start bot để test flow ĐÃ UNLOCK")
            print(f"   Message sẽ hiển thị: Sở hữu mãi mãi + features")
        
    finally:
        db.close()

if __name__ == "__main__":
    # Default user: son23699
    user_id = 6194449688
    
    if len(sys.argv) > 1:
        try:
            user_id = int(sys.argv[1])
        except:
            print(f"❌ Invalid user ID: {sys.argv[1]}")
            sys.exit(1)
    
    print("=" * 60)
    print("🔄 TOGGLE FREE UNLOCK STATUS")
    print("=" * 60)
    print(f"\nUser ID: {user_id}")
    
    toggle_unlock(user_id)
    
    print("\n" + "=" * 60)
    print("✅ DONE! Gửi /start trong Telegram để xem thay đổi")
    print("=" * 60)
