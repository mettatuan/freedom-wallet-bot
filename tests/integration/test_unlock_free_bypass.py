"""
Script bypass để test FREE tier nhanh chóng
Unlock user thành FREE ngay lập tức mà không cần 2 referrals
"""

import sys
from datetime import datetime
from bot.utils.database import SessionLocal, User

def unlock_free_for_user(user_id: int):
    """Unlock FREE tier for user (bypass referral requirement)"""
    
    db = SessionLocal()
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ User {user_id} không tồn tại trong database")
            print(f"\n💡 Hãy /start bot trước, sau đó chạy lại script này")
            return False
        
        # Check current status
        print(f"\n📊 TRẠNG THÁI HIỆN TẠI:")
        print(f"   User: {user.first_name} {user.last_name or ''}")
        print(f"   Username: @{user.username or 'N/A'}")
        print(f"   Telegram ID: {user.id}")
        print(f"   FREE Unlocked: {user.is_free_unlocked}")
        print(f"   Referral Count: {user.referral_count}")
        print(f"   VIP Tier: {user.vip_tier or 'None'}")
        print(f"   Created: {user.created_at}")
        
        if user.is_free_unlocked:
            print(f"\n⚠️  User này đã unlock FREE rồi!")
            print(f"   Referral count: {user.referral_count}")
            
            # Ask if want to re-unlock
            response = input("\nBạn có muốn unlock lại? (y/n): ").strip().lower()
            if response != 'y':
                print("❌ Hủy bỏ")
                return False
        
        # Unlock FREE
        print(f"\n🔓 ĐANG UNLOCK FREE...")
        
        user.is_free_unlocked = True
        user.referral_count = 2  # Set to 2 for consistency
        
        db.commit()
        db.refresh(user)
        
        # Verify
        print(f"\n✅ UNLOCK THÀNH CÔNG!")
        print(f"\n📊 TRẠNG THÁI MỚI:")
        print(f"   FREE Unlocked: {user.is_free_unlocked}")
        print(f"   Referral Count: {user.referral_count}")
        
        print(f"\n🎉 User {user.first_name} đã sở hữu FREE tier mãi mãi!")
        print(f"\n🧪 BẮT ĐẦU TEST:")
        print(f"   1. Mở bot trong Telegram")
        print(f"   2. Gửi /start hoặc tap menu")
        print(f"   3. Verify các features:")
        print(f"      ✅ Google Sheets setup")
        print(f"      ✅ AI Assistant (5 msgs/day)")
        print(f"      ✅ Quick Record")
        print(f"      ✅ Community access")
        
        return True
        
    finally:
        db.close()

def show_all_users():
    """Show all users in database"""
    
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.created_at.desc()).limit(10).all()
        
        if not users:
            print("❌ Không có user nào trong database")
            return
        
        print(f"\n📋 10 USERS GẦN NHẤT:")
        print(f"{'ID':<12} {'Name':<20} {'Username':<15} {'FREE':<6} {'VIP':<10} {'Created'}")
        print("=" * 90)
        
        for user in users:
            free_status = "✅" if user.is_free_unlocked else "❌"
            vip_status = user.vip_tier or "None"
            created = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()[:19] or "N/A"
            
            print(f"{user.id:<12} {name:<20} "
                  f"{('@' + user.username if user.username else 'N/A')[:14]:<15} "
                  f"{free_status:<6} {vip_status:<10} {created}")
    
    finally:
        db.close()

def main():
    print("=" * 60)
    print("🧪 FREE TIER BYPASS TEST SCRIPT")
    print("=" * 60)
    print("\nScript này sẽ unlock FREE tier ngay lập tức")
    print("(bypass yêu cầu 2 referrals để test nhanh)")
    
    # Show users first
    show_all_users()
    
    print("\n" + "=" * 60)
    print("NHẬP TELEGRAM ID CỦA USER CẦN UNLOCK:")
    print("=" * 60)
    
    try:
        user_id = int(input("\nTelegram ID: ").strip())
    except ValueError:
        print("❌ Telegram ID phải là số!")
        return
    
    # Confirm
    print(f"\n⚠️  Bạn sắp unlock FREE cho user: {user_id}")
    confirm = input("Tiếp tục? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Hủy bỏ")
        return
    
    # Execute unlock
    success = unlock_free_for_user(user_id)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ HOÀN TẤT! SẴN SÀNG TEST!")
        print("=" * 60)
        print("\n📖 Xem hướng dẫn test chi tiết tại:")
        print("   TEST_FREE_FLOW.md")
        print("\n💡 Tips:")
        print("   - Test tất cả features trong FREE tier")
        print("   - Verify messaging: 'Sở hữu mãi mãi' ♾️")
        print("   - Check AI limit: 5 msgs/day")
        print("   - Verify không có urgency/scarcity")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Script bị hủy bởi user")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
