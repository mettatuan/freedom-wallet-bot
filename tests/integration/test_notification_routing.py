"""
Test Notifications - Verify who receives which notifications
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, User


async def show_users():
    """Show all users to understand notification routing"""
    
    print("\n" + "="*70)
    print("👥 DANH SÁCH USERS TRONG HỆ THỐNG")
    print("="*70 + "\n")
    
    db = next(get_db())
    users = db.query(User).all()
    
    for user in users:
        print(f"User ID: {user.id}")
        print(f"  Username: @{user.username}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Subscription: {user.subscription_tier}")
        if user.premium_expires_at:
            print(f"  Premium Expires: {user.premium_expires_at.strftime('%d/%m/%Y %H:%M')}")
        print()
    
    db.close()
    
    print("="*70)
    print("\n💡 NOTIFICATION ROUTING:\n")
    print("📌 Khi admin APPROVE payment:")
    print("   ✅ User (verification.user_id) nhận: '🎉 CHÚC MỪNG! PREMIUM ĐÃ KÍCH HOẠT'")
    print("   ✅ Admin message: Cập nhật status 'ĐÃ DUYỆT THÀNH CÔNG'")
    print()
    print("📌 Khi admin REJECT payment:")
    print("   ❌ User (verification.user_id) nhận: 'THANH TOÁN BỊ TỪ CHỐI + lý do'")
    print("   ✅ Admin message: Confirm 'ĐÃ TỪ CHỐI'")
    print()
    print("❗ LƯU Ý:")
    print("   Nếu test với admin ID = user ID → Admin sẽ nhận cả 2 messages!")
    print("   Ví dụ: Admin 6588506476 approve payment của chính mình")
    print("   → Thấy cả admin message + user congratulation message")
    print()
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Notification Routing Test\n")
    asyncio.run(show_users())
