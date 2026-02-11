"""
Premium Renewal Logic
Xử lý thanh toán gia hạn khi Premium hết hạn
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User
from bot.services.payment_service import PaymentVerificationService
from bot.core.subscription import SubscriptionManager
from loguru import logger


def check_renewal_eligibility(user):
    """
    Kiểm tra user có đủ điều kiện gia hạn không
    
    Returns:
        (eligible, reason, days_until_expiry)
    """
    if not user:
        return False, "User không tồn tại", None
    
    # Check if user is Premium
    if user.subscription_tier != "PREMIUM":
        return True, "User chưa Premium, có thể đăng ký", None
    
    # Check expiry date
    if not user.premium_expires_at:
        return True, "Không có ngày hết hạn, có thể gia hạn", None
    
    now = datetime.utcnow()
    expires_at = user.premium_expires_at
    
    if expires_at < now:
        # Premium đã hết hạn
        days_expired = (now - expires_at).days
        return True, f"Premium đã hết hạn {days_expired} ngày trước", 0
    
    days_until_expiry = (expires_at - now).days
    
    # Cho phép gia hạn trước 30 ngày
    if days_until_expiry <= 30:
        return True, f"Premium còn {days_until_expiry} ngày, có thể gia hạn sớm", days_until_expiry
    else:
        return False, f"Premium còn {days_until_expiry} ngày, chưa cần gia hạn", days_until_expiry


async def handle_renewal_payment(verification_id: str, approved_by: int):
    """
    Xử lý thanh toán gia hạn thông minh
    
    - Nếu Premium chưa hết hạn: Extend từ ngày hết hạn cũ + 365 ngày
    - Nếu Premium đã hết hạn: Start từ now + 365 ngày
    """
    
    db = next(get_db())
    
    # Get verification
    ver_id = int(verification_id.replace("VER", ""))
    verification = db.query(PaymentVerification).filter(
        PaymentVerification.id == ver_id
    ).first()
    
    if not verification:
        print(f"❌ Không tìm thấy verification {verification_id}")
        return False
    
    # Get user
    user = db.query(User).filter(User.id == verification.user_id).first()
    
    if not user:
        print(f"❌ Không tìm thấy user {verification.user_id}")
        return False
    
    # Check eligibility
    eligible, reason, days_left = check_renewal_eligibility(user)
    
    print(f"\n📊 THÔNG TIN USER:")
    print(f"   Tên: {user.full_name}")
    print(f"   Username: @{user.username}")
    print(f"   Tier hiện tại: {user.subscription_tier}")
    
    if user.premium_expires_at:
        print(f"   Premium hết hạn: {user.premium_expires_at.strftime('%d/%m/%Y')}")
        
        now = datetime.utcnow()
        if user.premium_expires_at < now:
            print(f"   ⚠️  ĐÃ HẾT HẠN {(now - user.premium_expires_at).days} ngày")
        else:
            print(f"   ✅ Còn {(user.premium_expires_at - now).days} ngày")
    else:
        print(f"   Premium: Chưa kích hoạt")
    
    print(f"\n🔍 KIỂM TRA GIA HẠN:")
    print(f"   {reason}\n")
    
    if not eligible:
        print(f"❌ User chưa đủ điều kiện gia hạn!")
        print(f"   Cần đợi đến {(user.premium_expires_at - timedelta(days=30)).strftime('%d/%m/%Y')}")
        return False
    
    # Approve payment
    verification.status = "APPROVED"
    verification.approved_by = approved_by
    verification.approved_at = datetime.utcnow()
    
    # Calculate new expiry date
    now = datetime.utcnow()
    
    if user.subscription_tier == "PREMIUM" and user.premium_expires_at and user.premium_expires_at > now:
        # RENEWAL: Extend từ ngày hết hạn cũ
        new_expiry = user.premium_expires_at + timedelta(days=365)
        is_renewal = True
        print(f"🔄 GIA HẠN:")
        print(f"   Từ: {user.premium_expires_at.strftime('%d/%m/%Y')}")
        print(f"   Đến: {new_expiry.strftime('%d/%m/%Y')}")
        print(f"   Thêm: 365 ngày")
    else:
        # NEW or EXPIRED: Start từ now
        new_expiry = now + timedelta(days=365)
        is_renewal = False
        print(f"🆕 KÍCH HOẠT MỚI:")
        print(f"   Từ: {now.strftime('%d/%m/%Y')}")
        print(f"   Đến: {new_expiry.strftime('%d/%m/%Y')}")
        print(f"   Thời hạn: 365 ngày")
    
    # Update user
    user.subscription_tier = "PREMIUM"
    user.premium_expires_at = new_expiry
    
    if not user.premium_started_at or not is_renewal:
        user.premium_started_at = now
    
    db.commit()
    
    print(f"\n✅ Đã cập nhật Premium cho user!")
    print(f"   Hết hạn mới: {new_expiry.strftime('%d/%m/%Y')}\n")
    
    db.close()
    return True


async def simulate_scenarios():
    """Mô phỏng các tình huống gia hạn"""
    
    print("\n" + "="*70)
    print("🎭 MÔ PHỎNG CÁC TÌNH HUỐNG GIA HẠN")
    print("="*70 + "\n")
    
    db = next(get_db())
    
    # Scenario 1: User Premium còn 300 ngày
    print("📌 SCENARIO 1: User Premium còn 300 ngày")
    print("   → ❌ KHÔNG cho phép gia hạn (phải đợi còn 30 ngày)")
    print("   → User cần đợi thêm 270 ngày\n")
    
    # Scenario 2: User Premium còn 20 ngày
    print("📌 SCENARIO 2: User Premium còn 20 ngày")
    print("   → ✅ CHO PHÉP gia hạn sớm")
    print("   → Khi duyệt: Extend từ ngày hết hạn cũ + 365 ngày")
    print("   → Ví dụ: Hết hạn 01/03/2026 → Mới 01/03/2027\n")
    
    # Scenario 3: User Premium đã hết hạn 10 ngày
    print("📌 SCENARIO 3: User Premium đã hết hạn 10 ngày")
    print("   → ✅ CHO PHÉP gia hạn")
    print("   → Khi duyệt: Start từ hôm nay + 365 ngày")
    print("   → User không mất thời gian đã hết hạn\n")
    
    # Scenario 4: User chưa từng Premium
    print("📌 SCENARIO 4: User chưa từng Premium")
    print("   → ✅ CHO PHÉP đăng ký")
    print("   → Khi duyệt: Start từ hôm nay + 365 ngày\n")
    
    # Scenario 5: User có 2 APPROVED
    print("📌 SCENARIO 5: User có 2 APPROVED (năm 1 + năm 2)")
    print("   → Cleanup KHÔNG xóa")
    print("   → Lịch sử thanh toán được giữ nguyên\n")
    
    print("="*70 + "\n")
    
    db.close()


async def demo_renewal_flow():
    """Demo flow gia hạn thực tế"""
    
    print("\n" + "💡 "*25)
    print("        DEMO: LUỒNG GIA HẠN PREMIUM")
    print("💡 "*25 + "\n")
    
    db = next(get_db())
    
    # Get current users
    users = db.query(User).filter(User.subscription_tier == "PREMIUM").all()
    
    if not users:
        print("⚠️  Chưa có user Premium nào để demo\n")
        db.close()
        return
    
    for user in users:
        print(f"\n👤 User: {user.full_name} (@{user.username})")
        
        eligible, reason, days_left = check_renewal_eligibility(user)
        
        if eligible:
            print(f"   ✅ {reason}")
            print(f"   💡 User có thể submit payment proof mới")
            print(f"   💡 Admin duyệt → Premium extend thêm 365 ngày")
        else:
            print(f"   ⏳ {reason}")
            print(f"   💡 User cần đợi thêm {days_left - 30} ngày để gia hạn")
        
        print()
    
    db.close()


async def main():
    """Main function"""
    
    print("\n" + "🔄 "*25)
    print("           PREMIUM RENEWAL SYSTEM")
    print("🔄 "*25 + "\n")
    
    # Show simulation
    await simulate_scenarios()
    
    # Show current status
    await demo_renewal_flow()
    
    print("="*70)
    print("📚 HƯỚNG DẪN SỬ DỤNG:")
    print("="*70 + "\n")
    
    print("1️⃣  USER GIA HẠN:")
    print("   - User còn ≤ 30 ngày Premium → Có thể gửi proof thanh toán")
    print("   - User Premium hết hạn → Có thể gửi proof bất kỳ lúc nào")
    print("   - Bot tự động tạo PaymentVerification mới\n")
    
    print("2️⃣  ADMIN DUYỆT:")
    print("   - Admin click 'Duyệt' như bình thường")
    print("   - Hệ thống tự detect renewal → Extend từ ngày hết hạn cũ")
    print("   - Hoặc activate mới nếu đã hết hạn\n")
    
    print("3️⃣  CLEANUP:")
    print("   - Cleanup chỉ xóa duplicate trong CÙNG KỲ")
    print("   - Lịch sử thanh toán các năm được giữ nguyên")
    print("   - VD: User có APPROVED năm 2025 + APPROVED năm 2026 = OK\n")
    
    print("4️⃣  GOOGLE SHEETS:")
    print("   - Mỗi lần thanh toán = 1 dòng trong Payments")
    print("   - Admin có thể track lịch sử gia hạn\n")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
