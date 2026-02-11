"""
Test Admin Approval Flow & Google Sheets Sync
Tạo yêu cầu thanh toán test để admin duyệt
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.services.payment_service import PaymentVerificationService
from bot.utils.database import get_db, User, PaymentVerification
from loguru import logger


async def create_test_payment_request():
    """Tạo yêu cầu thanh toán test"""
    
    print("\n" + "="*60)
    print("🧪 TEST ADMIN APPROVAL & GOOGLE SHEETS SYNC")
    print("="*60 + "\n")
    
    # Get user info
    db = next(get_db())
    
    # Tìm user hiện tại (admin)
    admin_user = db.query(User).filter(User.id == 6588506476).first()
    
    if not admin_user:
        print("❌ Admin user không tồn tại. Tạo user test...")
        from bot.utils.database import save_user_to_db
        
        # Tạo user test
        test_user_data = {
            'id': 1299465308,
            'username': 'Mettatuan',
            'first_name': 'PHAM',
            'last_name': 'THANH TUAN',
            'full_name': 'PHAM THANH TUAN'
        }
        
        user = save_user_to_db(
            user_id=test_user_data['id'],
            username=test_user_data['username'],
            first_name=test_user_data['first_name'],
            last_name=test_user_data['last_name']
        )
        user_id = test_user_data['id']
        username = test_user_data['username']
        full_name = test_user_data['full_name']
    else:
        user_id = admin_user.id
        username = admin_user.username or "testuser"
        full_name = admin_user.full_name or "Test User"
    
    print(f"👤 User: {full_name} (@{username})")
    print(f"🆔 User ID: {user_id}\n")
    
    # Tạo verification request
    print("📝 Tạo yêu cầu xác nhận thanh toán...")
    
    verification_id = await PaymentVerificationService.create_verification_request(
        user_id=user_id,
        amount=999000,
        transaction_info=f"""
Mã giao dịch: FW{user_id}
Nội dung: FW{user_id} PREMIUM
Ngân hàng: OCB
STK: 0107103241416363
Tên TK: PHAM THANH TUAN
Số tiền: 999,000 VND

✅ ĐÃ CHUYỂN KHOẢN THÀNH CÔNG
[TEST - Created by test_admin_approval.py]
        """.strip(),
        submitted_by=user_id
    )
    
    if verification_id:
        print(f"✅ Đã tạo yêu cầu: {verification_id}\n")
        
        # Get verification details
        db = next(get_db())
        ver_id = int(verification_id.replace("VER", ""))
        verification = db.query(PaymentVerification).filter(
            PaymentVerification.id == ver_id
        ).first()
        
        if verification:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("📋 THÔNG TIN YÊU CẦU:")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"Mã: {verification_id}")
            print(f"User ID: {verification.user_id}")
            print(f"Số tiền: {verification.amount:,.0f} VND")
            print(f"Trạng thái: {verification.status}")
            print(f"Thời gian: {verification.created_at}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            
            print("✅ ADMIN SẼ NHẬN ĐƯỢC NOTIFICATION TRÊN BOT")
            print("   với 3 nút bấm:")
            print("   • ✅ Duyệt")
            print("   • ❌ Từ chối")
            print("   • 📋 Xem tất cả pending\n")
            
            print("📌 SAU KHI DUYỆT:")
            print("   1. User được nâng cấp Premium (365 ngày)")
            print("   2. Dữ liệu ghi vào Google Sheets:")
            print("      https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/")
            print("   3. User nhận thông báo kích hoạt\n")
            
            print("🎯 BƯỚC TIẾP THEO:")
            print("   1. Mở bot @FreedomWalletBot")
            print("   2. Admin sẽ thấy notification")
            print("   3. Click '✅ Duyệt' để test approve")
            print("   4. Kiểm tra Google Sheets có log không\n")
            
            # Show all pending
            pending = db.query(PaymentVerification).filter(
                PaymentVerification.status == "PENDING"
            ).all()
            
            if len(pending) > 1:
                print(f"ℹ️  Có {len(pending)} yêu cầu đang chờ duyệt")
                print("   Hoặc gửi /payment_pending trên bot để xem tất cả\n")
            
            print("="*60)
            return verification_id
        
    else:
        print("❌ Không thể tạo yêu cầu xác nhận\n")
        return None


async def send_test_notification_to_admin():
    """Gửi notification test đến admin qua bot"""
    try:
        from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
        from config.settings import settings
        import os
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        admin_id = int(os.getenv('ADMIN_USER_ID', '6588506476'))
        
        if not bot_token:
            print("⚠️  Không tìm thấy TELEGRAM_BOT_TOKEN")
            return False
        
        bot = Bot(token=bot_token)
        
        # Get latest pending verification
        db = next(get_db())
        verification = db.query(PaymentVerification).filter(
            PaymentVerification.status == "PENDING"
        ).order_by(PaymentVerification.created_at.desc()).first()
        
        if not verification:
            print("⚠️  Không có yêu cầu pending nào")
            return False
        
        user = db.query(User).filter(User.id == verification.user_id).first()
        
        import html
        safe_username = html.escape(user.username or 'N/A')
        safe_fullname = html.escape(user.full_name or 'N/A')
        safe_transaction = html.escape(verification.transaction_info or 'N/A')
        
        verification_id = f"VER{verification.id}"
        
        message = f"""
🔔 <b>YÊU CẦU XÁC NHẬN THANH TOÁN MỚI</b>

Mã: <code>{verification_id}</code>
User ID: <code>{verification.user_id}</code>
Username: @{safe_username}
Tên: {safe_fullname}
Số tiền: {verification.amount:,.0f} VND

📋 <b>Thông tin giao dịch:</b>
{safe_transaction[:200]}...

━━━━━━━━━━━━━━━━━━━━━
⏰ <i>{verification.created_at.strftime('%d/%m/%Y %H:%M:%S')}</i>

💡 <b>Click nút bên dưới để xử lý:</b>
"""
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Duyệt", callback_data=f"admin_approve_{verification_id}"),
                InlineKeyboardButton("❌ Từ chối", callback_data=f"admin_reject_{verification_id}")
            ],
            [InlineKeyboardButton("📋 Xem tất cả pending", callback_data="admin_list_pending")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=admin_id,
            text=message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        print(f"\n✅ Đã gửi notification đến admin (ID: {admin_id})")
        return True
        
    except Exception as e:
        print(f"\n❌ Lỗi khi gửi notification: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    try:
        # Create test payment request
        verification_id = await create_test_payment_request()
        
        if verification_id:
            print("\n🤖 Đang gửi notification đến admin...\n")
            success = await send_test_notification_to_admin()
            
            if success:
                print("\n✅ TEST HOÀN TẤT")
                print("   Mở bot để xem notification và test duyệt!\n")
            else:
                print("\n⚠️  Tạo request thành công nhưng không gửi notification được")
                print("   Admin có thể gửi /payment_pending trên bot để xem\n")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
