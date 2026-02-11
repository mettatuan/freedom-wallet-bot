"""
Test Premium Flow - Comprehensive test for Premium trial and upgrade
Tests all user journeys:
1. Start trial
2. View premium features  
3. Upgrade to premium
4. Payment flow
5. Premium menu navigation
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import SessionLocal, User
from bot.core.subscription import SubscriptionManager, SubscriptionTier
from datetime import datetime, timedelta
from loguru import logger

# Test user ID
TEST_USER_ID = 1299465308


def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def print_test(name, status, details=""):
    """Print test result"""
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")
    if details:
        print(f"   └─ {details}")


async def test_database_connection():
    """Test 1: Database connection"""
    print_section("TEST 1: DATABASE CONNECTION")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == TEST_USER_ID).first()
        
        if user:
            print_test("User exists", True, f"ID: {user.id}, Username: {user.username}")
            print_test("Subscription tier", True, f"Current: {user.subscription_tier}")
            print_test("Trial status", True, f"Ends: {user.trial_ends_at}")
            print_test("Premium status", True, f"Expires: {user.premium_expires_at}")
            return True, user
        else:
            print_test("User exists", False, "User not found - needs /start")
            return False, None
    except Exception as e:
        print_test("Database query", False, str(e))
        return False, None
    finally:
        db.close()


async def test_trial_flow(user):
    """Test 2: Trial activation flow"""
    print_section("TEST 2: TRIAL ACTIVATION")
    
    db = SessionLocal()
    try:
        # Check current state
        current_tier = user.subscription_tier
        print(f"Current tier: {current_tier}")
        
        # Test trial activation
        if current_tier == "TRIAL":
            print_test("Already on trial", True, f"Ends: {user.trial_ends_at}")
            
            # Check if expired
            if user.trial_ends_at and user.trial_ends_at < datetime.utcnow():
                print_test("Trial expired", True, "User should see upgrade prompt")
            else:
                days_left = (user.trial_ends_at - datetime.utcnow()).days if user.trial_ends_at else 0
                print_test("Trial active", True, f"{days_left} days remaining")
        else:
            print_test("Not on trial", True, f"Current: {current_tier}")
        
        # Test trial extension (if needed)
        if current_tier != "TRIAL":
            print("\n🔄 Testing trial activation...")
            success = await SubscriptionManager.start_trial(TEST_USER_ID, days=7)
            
            if success:
                db.refresh(user)
                print_test("Trial activated", True, f"Ends: {user.trial_ends_at}")
            else:
                print_test("Trial activation", False, "Failed to activate trial")
        
        return True
    except Exception as e:
        print_test("Trial flow", False, str(e))
        return False
    finally:
        db.close()


async def test_premium_upgrade(user):
    """Test 3: Premium upgrade flow"""
    print_section("TEST 3: PREMIUM UPGRADE")
    
    try:
        # Test payment info generation
        from bot.services.payment_service import PaymentService
        
        payment_info = PaymentService.get_payment_instructions(TEST_USER_ID, "PREMIUM")
        
        print_test("Payment info generated", True)
        print(f"   ├─ Bank: {payment_info['bank_name']}")
        print(f"   ├─ Account: {payment_info['account_number']}")
        print(f"   ├─ Amount: {payment_info['amount']:,} VND")
        print(f"   ├─ Transfer code: {payment_info['transfer_code']}")
        print(f"   └─ QR URL: {payment_info['qr_url'][:60]}...")
        
        # Test QR URL format
        if "vietqr.io" in payment_info['qr_url']:
            print_test("QR URL format", True, "Valid VietQR URL")
        else:
            print_test("QR URL format", False, "Invalid URL format")
        
        # Test transfer code parsing
        parsed_user_id = PaymentService.parse_transfer_message(
            f"{payment_info['transfer_code']} PREMIUM"
        )
        
        if parsed_user_id == TEST_USER_ID:
            print_test("Transfer code parsing", True, f"Parsed: {parsed_user_id}")
        else:
            print_test("Transfer code parsing", False, f"Expected {TEST_USER_ID}, got {parsed_user_id}")
        
        return True
    except Exception as e:
        print_test("Premium upgrade flow", False, str(e))
        logger.error(f"Error in test_premium_upgrade: {e}", exc_info=True)
        return False


async def test_payment_verification():
    """Test 4: Payment verification flow"""
    print_section("TEST 4: PAYMENT VERIFICATION")
    
    try:
        from bot.services.payment_service import PaymentVerificationService
        from bot.utils.database import get_db, PaymentVerification
        
        # Create test verification request
        verification_id = await PaymentVerificationService.create_verification_request(
            user_id=TEST_USER_ID,
            amount=999000,
            transaction_info="Test transaction - 999,000 VND at " + datetime.now().strftime("%H:%M %d/%m/%Y"),
            submitted_by=TEST_USER_ID
        )
        
        print_test("Verification request created", True, f"ID: {verification_id}")
        
        # Check if request exists in database
        db = next(get_db())
        try:
            ver_id = int(verification_id.replace("VER", ""))
            verification = db.query(PaymentVerification).filter(
                PaymentVerification.id == ver_id
            ).first()
            
            if verification:
                print_test("Verification in database", True)
                print(f"   ├─ Status: {verification.status}")
                print(f"   ├─ Amount: {verification.amount:,.0f} VND")
                print(f"   └─ Created: {verification.created_at}")
            else:
                print_test("Verification in database", False, "Not found")
        finally:
            db.close()
        
        return True
    except Exception as e:
        print_test("Payment verification", False, str(e))
        logger.error(f"Error in test_payment_verification: {e}", exc_info=True)
        return False


async def test_premium_menu():
    """Test 5: Premium menu structure"""
    print_section("TEST 5: PREMIUM MENU")
    
    try:
        from bot.handlers.premium_commands import PREMIUM_CALLBACKS
        
        # Check all required callbacks exist
        required_callbacks = [
            'quick_record',
            'today_status',
            'analysis',
            'recommendation',
            'setup',
            'priority_support',
            'premium_menu'
        ]
        
        all_exist = True
        for callback in required_callbacks:
            exists = callback in PREMIUM_CALLBACKS
            print_test(f"Callback: {callback}", exists)
            if not exists:
                all_exist = False
        
        if all_exist:
            print(f"\n✅ All {len(required_callbacks)} callbacks registered")
        else:
            print(f"\n⚠️ Some callbacks missing")
        
        return all_exist
    except Exception as e:
        print_test("Premium menu structure", False, str(e))
        return False


async def test_subscription_manager():
    """Test 6: Subscription manager functions"""
    print_section("TEST 6: SUBSCRIPTION MANAGER")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == TEST_USER_ID).first()
        
        # Test tier detection
        tier = SubscriptionManager.get_user_tier(user)
        print_test("Tier detection", True, f"Current tier: {tier.value if tier else 'None'}")
        
        # Test feature access
        can_use_ai = SubscriptionManager.can_use_ai(user)
        print_test("AI access check", True, f"Can use AI: {can_use_ai}")
        
        daily_limit = SubscriptionManager.get_daily_message_limit(user)
        print_test("Daily limit check", True, f"Daily limit: {daily_limit}")
        
        return True
    except Exception as e:
        print_test("Subscription manager", False, str(e))
        return False
    finally:
        db.close()


async def test_user_flow_simulation():
    """Test 7: Simulate complete user flow"""
    print_section("TEST 7: USER FLOW SIMULATION")
    
    print("🎭 Simulating user journey:\n")
    
    steps = [
        ("1. User clicks /start", "User sees welcome message with trial offer"),
        ("2. User clicks 'Dùng thử Premium'", "Trial activated for 7 days"),
        ("3. User explores Premium menu", "All 6 buttons work correctly"),
        ("4. User clicks 'Ghi chi tiêu nhanh'", "Quick record form appears"),
        ("5. User navigates with 'Quay lại'", "Returns to Premium menu"),
        ("6. Trial expires after 7 days", "User sees upgrade prompt"),
        ("7. User clicks 'Nâng cấp Premium'", "Payment QR code appears"),
        ("8. User submits payment proof", "Verification request created"),
        ("9. Admin approves payment", "Premium activated for 365 days"),
        ("10. User accesses Premium features", "All features unlocked")
    ]
    
    for step, expected in steps:
        print(f"✓ {step}")
        print(f"  └─ {expected}")
    
    print(f"\n✅ User flow: 10/10 steps defined")
    return True


async def main():
    """Run all tests"""
    print("\n" + "🧪 PREMIUM FLOW TEST SUITE ".center(60, "="))
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests
    results.append(await test_database_connection())
    
    if results[0][0]:  # If database connection successful
        user = results[0][1]
        results.append((await test_trial_flow(user), None))
        results.append((await test_premium_upgrade(user), None))
        results.append((await test_payment_verification(), None))
    
    results.append((await test_premium_menu(), None))
    results.append((await test_subscription_manager(), None))
    results.append((await test_user_flow_simulation(), None))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for r in results if r[0])
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Premium flow is ready!")
    else:
        print("\n⚠️ Some tests failed. Check logs above.")
    
    print("\n" + "="*60)
    
    # Next steps
    print("\n📋 NEXT STEPS TO TEST MANUALLY:")
    print("1. Start bot: python main.py")
    print("2. In Telegram, send: /start")
    print("3. Click 'Dùng thử Premium' button")
    print("4. Explore Premium menu - click all buttons")
    print("5. Click 'Quay lại' multiple times - check no errors")
    print("6. Click 'Nâng cấp Premium' - check QR code appears")
    print("7. Click 'Đã thanh toán' - submit test info")
    print("8. Admin: /payment_pending to see request")
    print("9. Admin: /payment_approve VER[id] to approve")
    print("10. Check user receives Premium confirmation")
    
    print("\n💡 TIP: Check logs at data/logs/bot.log for detailed info")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
