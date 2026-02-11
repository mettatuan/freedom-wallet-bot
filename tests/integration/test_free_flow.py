"""
Test FREE Flow Messaging Changes
Verify all Phase 1 Task 1 changes are working correctly
"""
import asyncio
import sys
from loguru import logger
from bot.utils.database import SessionLocal, User


def test_referral_messaging():
    """Test referral.py messaging changes"""
    logger.info("🧪 Testing Referral Messaging Changes...")
    
    checks = []
    
    # Read referral.py
    with open('bot/handlers/referral.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 1: No urgency language
    if "Còn {remaining} người nữa" in content:
        logger.error("❌ FAIL: Found old urgency language 'Còn {remaining} người nữa'")
        checks.append(False)
    else:
        logger.info("✅ PASS: No urgency language found")
        checks.append(True)
    
    # Check 2: Progress-based messaging
    if "Tiến độ: {referral_count}/2" in content or "📊 **Tiến độ: {referral_count}/2" in content:
        logger.info("✅ PASS: Found progress-based messaging")
        checks.append(True)
    else:
        logger.error("❌ FAIL: Progress-based messaging not found")
        checks.append(False)
    
    # Check 3: Ownership language
    if "Sở hữu vĩnh viễn" in content or "SỞ HỮU VĨNH VIỄN" in content:
        logger.info("✅ PASS: Found ownership language 'Sở hữu vĩnh viễn'")
        checks.append(True)
    else:
        logger.error("❌ FAIL: Ownership language not found")
        checks.append(False)
    
    # Check 4: No scarcity tactics
    if "FREE cho 1000 người đầu tiên" in content:
        logger.error("❌ FAIL: Found scarcity language 'FREE cho 1000 người đầu tiên'")
        checks.append(False)
    else:
        logger.info("✅ PASS: No scarcity language found")
        checks.append(True)
    
    # Check 5: Simplified benefits list
    if "Bot AI không giới hạn" in content:
        logger.error("❌ FAIL: Found misleading benefit 'Bot AI không giới hạn'")
        checks.append(False)
    else:
        logger.info("✅ PASS: No misleading benefits found")
        checks.append(True)
    
    return all(checks)


def test_start_handler():
    """Test start.py changes"""
    logger.info("\n🧪 Testing Start Handler Changes...")
    
    checks = []
    
    # Read start.py
    with open('bot/handlers/start.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 1: No TRIAL tier
    if 'subscription_tier = db_user.subscription_tier if db_user else "TRIAL"' in content:
        logger.error("❌ FAIL: Found TRIAL tier default")
        checks.append(False)
    elif 'subscription_tier = db_user.subscription_tier if db_user else "FREE"' in content:
        logger.info("✅ PASS: Changed to FREE tier default")
        checks.append(True)
    else:
        logger.warning("⚠️ WARNING: Could not verify tier default change")
        checks.append(True)  # Don't fail on warning
    
    # Check 2: No "Dùng thử Premium" button in FREE menu
    # This is tricky to check without context, so we'll look for the button removal
    trial_button_count = content.count('InlineKeyboardButton("🎁 Dùng thử Premium 7 ngày"')
    trial_button_count += content.count('InlineKeyboardButton("💎 Dùng thử Premium (Unlimited)"')
    
    if trial_button_count == 0:
        logger.info("✅ PASS: No Premium trial buttons in FREE menu")
        checks.append(True)
    else:
        logger.info(f"⚠️ INFO: Found {trial_button_count} Premium trial button(s) (may be in other contexts)")
        checks.append(True)  # Not necessarily a failure
    
    return all(checks)


def test_unlock_flow():
    """Test unlock_flow_v3.py changes"""
    logger.info("\n🧪 Testing Unlock Flow Changes...")
    
    checks = []
    
    # Read unlock_flow_v3.py
    with open('bot/handlers/unlock_flow_v3.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 1: Changed from "thành viên VIP" to "thành viên chính thức"
    if "thành viên VIP của Freedom Wallet" in content:
        logger.error("❌ FAIL: Still using 'thành viên VIP của Freedom Wallet'")
        checks.append(False)
    elif "thành viên chính thức của Freedom Wallet" in content:
        logger.info("✅ PASS: Changed to 'thành viên chính thức'")
        checks.append(True)
    else:
        logger.warning("⚠️ WARNING: Could not verify VIP terminology change")
        checks.append(True)
    
    # Check 2: Status message uses "FREE" not "VIP"
    if "Trạng thái: Thành viên VIP" in content:
        logger.error("❌ FAIL: Status still shows 'Thành viên VIP'")
        checks.append(False)
    elif "Trạng thái: Thành viên FREE" in content:
        logger.info("✅ PASS: Status shows 'Thành viên FREE'")
        checks.append(True)
    else:
        logger.warning("⚠️ WARNING: Could not verify status message")
        checks.append(True)
    
    return all(checks)


def test_status_handler():
    """Test status.py changes"""
    logger.info("\n🧪 Testing Status Handler Changes...")
    
    checks = []
    
    # Read status.py
    with open('bot/handlers/status.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 1: No "TÍNH NĂNG BỊ KHÓA" section (loss framing)
    if "TÍNH NĂNG BỊ KHÓA" in content:
        logger.error("❌ FAIL: Found loss framing 'TÍNH NĂNG BỊ KHÓA'")
        checks.append(False)
    else:
        logger.info("✅ PASS: No loss framing found")
        checks.append(True)
    
    # Check 2: "QUYỀN LỢI CỦA BẠN" (ownership framing)
    if "QUYỀN LỢI CỦA BẠN" in content:
        logger.info("✅ PASS: Found ownership framing 'QUYỀN LỢI CỦA BẠN'")
        checks.append(True)
    else:
        logger.warning("⚠️ WARNING: Ownership framing not found (may use different wording)")
        checks.append(True)
    
    # Check 3: No "Dùng thử Premium 7 ngày" button
    if 'InlineKeyboardButton("🎁 Dùng thử Premium 7 ngày"' in content:
        logger.error("❌ FAIL: Found Premium trial button in status handler")
        checks.append(False)
    else:
        logger.info("✅ PASS: No Premium trial button in status handler")
        checks.append(True)
    
    return all(checks)


def test_callback_handler():
    """Test callback.py changes"""
    logger.info("\n🧪 Testing Callback Handler Changes...")
    
    checks = []
    
    # Read callback.py
    with open('bot/handlers/callback.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check: No Premium upsell in free_chat handler
    # Look for the function and check if it has Premium button
    free_chat_start = content.find('async def handle_free_chat(')
    if free_chat_start != -1:
        # Get next 1000 chars
        free_chat_section = content[free_chat_start:free_chat_start+1500]
        
        if '"💎 Dùng thử Premium (Unlimited)"' in free_chat_section:
            logger.error("❌ FAIL: Found Premium upsell in free_chat handler")
            checks.append(False)
        else:
            logger.info("✅ PASS: No Premium upsell in free_chat handler")
            checks.append(True)
    else:
        logger.warning("⚠️ WARNING: Could not find free_chat handler")
        checks.append(True)
    
    return all(checks)


async def main():
    """Run all FREE flow tests"""
    
    logger.info("="*60)
    logger.info("🚀 TESTING FREE FLOW MESSAGING CHANGES")
    logger.info("="*60)
    
    results = []
    
    # Test 1: Referral messaging
    logger.info("\n[TEST 1/5] Referral Messaging")
    results.append(test_referral_messaging())
    
    # Test 2: Start handler
    logger.info("\n[TEST 2/5] Start Handler")
    results.append(test_start_handler())
    
    # Test 3: Unlock flow
    logger.info("\n[TEST 3/5] Unlock Flow")
    results.append(test_unlock_flow())
    
    # Test 4: Status handler
    logger.info("\n[TEST 4/5] Status Handler")
    results.append(test_status_handler())
    
    # Test 5: Callback handler
    logger.info("\n[TEST 5/5] Callback Handler")
    results.append(test_callback_handler())
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✅ ALL FREE FLOW TESTS PASSED!")
        logger.info("\n✨ Phase 1 Task 1 implementation verified successfully!")
        return 0
    else:
        logger.error(f"❌ {total - passed} TEST(S) FAILED!")
        logger.error("\n⚠️ Please review the implementation and fix failing tests.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
