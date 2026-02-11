"""
Test Payment Rejection - Verify rejection flow works correctly
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User
from bot.services.payment_service import PaymentVerificationService


async def test_rejection():
    """Test payment rejection flow"""
    
    print("\n" + "="*70)
    print("🧪 TEST PAYMENT REJECTION FLOW")
    print("="*70 + "\n")
    
    db = next(get_db())
    
    # Get a PENDING verification
    pending = db.query(PaymentVerification).filter(
        PaymentVerification.status == "PENDING"
    ).first()
    
    if not pending:
        print("❌ Không có PENDING verification nào để test")
        print("💡 Tạo test verification trước:")
        print("   python test_admin_approval.py")
        db.close()
        return
    
    verification_id = f"VER{pending.id}"
    user = db.query(User).filter(User.id == pending.user_id).first()
    
    print(f"📋 PENDING Verification:")
    print(f"   ID: {verification_id}")
    print(f"   User: {user.full_name if user else 'N/A'} (@{user.username if user else 'N/A'})")
    print(f"   Amount: {pending.amount:,.0f} VND")
    print(f"   Created: {pending.created_at.strftime('%d/%m/%Y %H:%M')}")
    print()
    
    db.close()
    
    # Test rejection with various reasons
    test_reasons = [
        "Sai số tiền",
        "Thiếu nội dung chuyển khoản",
        "Số tiền không khớp (chuyển 500k thay vì 999k)",
        "Nội dung CK: 'FW1234' nhưng user ID là 5678",
        "Ảnh không rõ ràng & không thể xác nhận",
    ]
    
    print("="*70)
    print("🧪 TEST REJECTION REASONS:")
    print("="*70 + "\n")
    
    for idx, reason in enumerate(test_reasons, 1):
        print(f"{idx}. {reason}")
    
    print()
    print("❓ Chọn lý do test (1-5) hoặc nhập lý do tùy chỉnh: ", end="")
    choice = input().strip()
    
    if choice.isdigit() and 1 <= int(choice) <= 5:
        test_reason = test_reasons[int(choice) - 1]
    else:
        test_reason = choice if choice else "Sai số tiền"
    
    print()
    print("="*70)
    print("🔄 EXECUTING REJECTION...")
    print("="*70 + "\n")
    
    print(f"Verification ID: {verification_id}")
    print(f"Rejected by: Admin (6588506476)")
    print(f"Reason: {test_reason}")
    print()
    
    # Execute rejection
    success = await PaymentVerificationService.reject_payment(
        verification_id=verification_id,
        rejected_by=6588506476,
        reason=test_reason
    )
    
    if success:
        print("✅ REJECTION SUCCESSFUL!\n")
        
        # Show updated verification
        db = next(get_db())
        ver_id = int(verification_id.replace("VER", ""))
        verification = db.query(PaymentVerification).filter(
            PaymentVerification.id == ver_id
        ).first()
        
        if verification:
            print("="*70)
            print("📊 UPDATED VERIFICATION:")
            print("="*70 + "\n")
            print(f"ID: {verification_id}")
            print(f"Status: {verification.status}")
            print(f"Rejected by: {verification.approved_by}")
            print(f"Rejected at: {verification.approved_at.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"Reason: {verification.notes}")
            print()
        
        db.close()
        
        print("="*70)
        print("💡 NEXT STEPS:")
        print("="*70 + "\n")
        print("1. Check logs: User should receive rejection notification")
        print("2. Check Google Sheets: Rejection should be logged with red color")
        print("3. Test again with another PENDING verification")
        print()
        
    else:
        print("❌ REJECTION FAILED!")
        print("Check logs for error details.\n")


async def show_all_pending():
    """Show all pending verifications"""
    
    print("\n" + "="*70)
    print("📋 ALL PENDING VERIFICATIONS")
    print("="*70 + "\n")
    
    db = next(get_db())
    pending = db.query(PaymentVerification).filter(
        PaymentVerification.status == "PENDING"
    ).order_by(PaymentVerification.created_at.desc()).all()
    
    if not pending:
        print("✅ Không có pending verification nào\n")
    else:
        print(f"Tìm thấy {len(pending)} PENDING verifications:\n")
        
        for ver in pending:
            user = db.query(User).filter(User.id == ver.user_id).first()
            print(f"VER{ver.id}:")
            print(f"  User: {user.full_name if user else 'N/A'} (@{user.username if user else 'N/A'})")
            print(f"  Amount: {ver.amount:,.0f} VND")
            print(f"  Created: {ver.created_at.strftime('%d/%m/%Y %H:%M')}")
            print()
    
    db.close()


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Payment Rejection Test\n")
    
    # Show pending verifications first
    asyncio.run(show_all_pending())
    
    # Ask if want to test rejection
    print("❓ Test rejection flow? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        asyncio.run(test_rejection())
    else:
        print("Skipped test.\n")
