"""
Test Renewal Logic - Test approve_payment với các scenarios khác nhau
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import get_db, PaymentVerification, User
from bot.services.payment_service import PaymentVerificationService
from loguru import logger


async def setup_test_users():
    """Setup 3 test users with different Premium states"""
    
    db = next(get_db())
    
    # User 1: Never had Premium (new registration)
    user1 = db.query(User).filter(User.id == 1299465308).first()
    if user1:
        user1.subscription_tier = "FREE"
        user1.premium_expires_at = None
        user1.premium_started_at = None
        print(f"✅ User 1 ({user1.username}): FREE - Never had Premium")
    
    # User 2: Premium with 20 days left (renewal eligible)
    user2 = db.query(User).filter(User.id == 6588506476).first()
    if user2:
        future_expiry = datetime.utcnow() + timedelta(days=20)
        user2.subscription_tier = "PREMIUM"
        user2.premium_expires_at = future_expiry
        user2.premium_started_at = datetime.utcnow() - timedelta(days=345)
        print(f"✅ User 2 ({user2.username}): PREMIUM - Expires in 20 days ({future_expiry.strftime('%d/%m/%Y')})")
    
    db.commit()
    db.close()
    
    print("\n✅ Test users setup complete!\n")


async def create_test_payments():
    """Create test payment verifications"""
    
    db = next(get_db())
    
    # Payment 1: User 1 (new registration)
    ver1 = PaymentVerification(
        user_id=1299465308,
        amount=999000,
        transaction_info="Test payment for new registration",
        transfer_code="FW1299465308",
        status="PENDING",
        submitted_by=1299465308,
        created_at=datetime.utcnow()
    )
    db.add(ver1)
    
    # Payment 2: User 2 (renewal with 20 days left)
    ver2 = PaymentVerification(
        user_id=6588506476,
        amount=999000,
        transaction_info="Test renewal payment",
        transfer_code="FW6588506476",
        status="PENDING",
        submitted_by=6588506476,
        created_at=datetime.utcnow()
    )
    db.add(ver2)
    
    db.commit()
    
    print(f"✅ Created VER{ver1.id} for User 1 (new registration)")
    print(f"✅ Created VER{ver2.id} for User 2 (renewal)")
    print()
    
    db.close()
    
    return ver1.id, ver2.id


async def test_renewal_logic():
    """Test the renewal logic"""
    
    print("\n" + "="*70)
    print("🧪 TESTING RENEWAL LOGIC")
    print("="*70 + "\n")
    
    # Setup test users
    await setup_test_users()
    
    # Create test payments
    ver1_id, ver2_id = await create_test_payments()
    
    print("="*70)
    print("📊 BEFORE APPROVAL:")
    print("="*70 + "\n")
    
    db = next(get_db())
    
    # Show User 1 status
    user1 = db.query(User).filter(User.id == 1299465308).first()
    print(f"User 1 ({user1.username}):")
    print(f"  Tier: {user1.subscription_tier}")
    print(f"  Expires: {user1.premium_expires_at}")
    print()
    
    # Show User 2 status
    user2 = db.query(User).filter(User.id == 6588506476).first()
    print(f"User 2 ({user2.username}):")
    print(f"  Tier: {user2.subscription_tier}")
    if user2.premium_expires_at:
        days_left = (user2.premium_expires_at - datetime.utcnow()).days
        print(f"  Expires: {user2.premium_expires_at.strftime('%d/%m/%Y %H:%M')} ({days_left} days left)")
    print()
    
    db.close()
    
    # Approve payments
    print("="*70)
    print("🔄 APPROVING PAYMENTS...")
    print("="*70 + "\n")
    
    # Approve payment 1 (new registration)
    print(f"Approving VER{ver1_id} (User 1 - New Registration)...")
    success1 = await PaymentVerificationService.approve_payment(ver1_id, approved_by=6588506476)
    print(f"Result: {'✅ SUCCESS' if success1 else '❌ FAILED'}\n")
    
    # Approve payment 2 (renewal)
    print(f"Approving VER{ver2_id} (User 2 - Renewal)...")
    success2 = await PaymentVerificationService.approve_payment(ver2_id, approved_by=6588506476)
    print(f"Result: {'✅ SUCCESS' if success2 else '❌ FAILED'}\n")
    
    # Show results
    print("="*70)
    print("📊 AFTER APPROVAL:")
    print("="*70 + "\n")
    
    db = next(get_db())
    
    # Show User 1 status
    user1 = db.query(User).filter(User.id == 1299465308).first()
    print(f"User 1 ({user1.username}):")
    print(f"  Tier: {user1.subscription_tier}")
    if user1.premium_expires_at:
        days_total = (user1.premium_expires_at - datetime.utcnow()).days
        print(f"  Expires: {user1.premium_expires_at.strftime('%d/%m/%Y %H:%M')} ({days_total} days from now)")
        print(f"  ✅ Expected: ~365 days from now (new registration)")
    print()
    
    # Show User 2 status
    user2 = db.query(User).filter(User.id == 6588506476).first()
    print(f"User 2 ({user2.username}):")
    print(f"  Tier: {user2.subscription_tier}")
    if user2.premium_expires_at:
        days_total = (user2.premium_expires_at - datetime.utcnow()).days
        print(f"  Expires: {user2.premium_expires_at.strftime('%d/%m/%Y %H:%M')} ({days_total} days from now)")
        print(f"  ✅ Expected: ~385 days from now (20 days left + 365 renewal)")
    print()
    
    db.close()
    
    print("="*70)
    print("✅ TEST COMPLETE!")
    print("="*70 + "\n")
    
    print("💡 RESULTS ANALYSIS:")
    print("   - User 1 (new): Should get 365 days from today")
    print("   - User 2 (renewal): Should get 385 days from today (20 + 365)")
    print()


async def cleanup_test_data():
    """Cleanup test payment verifications"""
    
    print("\n🧹 Cleaning up test data...")
    
    db = next(get_db())
    
    # Delete test verifications
    test_vers = db.query(PaymentVerification).filter(
        PaymentVerification.transaction_info.like('%Test%')
    ).all()
    
    for ver in test_vers:
        print(f"   Deleting VER{ver.id}...")
        db.delete(ver)
    
    db.commit()
    db.close()
    
    print("✅ Cleanup complete!\n")


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Renewal Logic Test\n")
    
    try:
        # Run test
        asyncio.run(test_renewal_logic())
        
        # Ask for cleanup
        print("\n❓ Do you want to cleanup test data? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice == 'y':
            asyncio.run(cleanup_test_data())
        else:
            print("Skipped cleanup.\n")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
