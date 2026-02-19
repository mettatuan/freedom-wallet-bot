"""
Comprehensive Flow Testing Script
Tests all 20 active flows in FreedomWallet Bot
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger
import asyncio
from datetime import datetime

# Test results storage
test_results = {
    "total_flows": 20,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "details": []
}


def log_test_result(flow_name, status, message="", error=None):
    """Log test result"""
    result = {
        "flow": flow_name,
        "status": status,
        "message": message,
        "error": str(error) if error else None,
        "timestamp": datetime.now().isoformat()
    }
    test_results["details"].append(result)
    
    if status == "PASS":
        test_results["passed"] += 1
        logger.success(f"✅ {flow_name}: {message}")
    elif status == "FAIL":
        test_results["failed"] += 1
        logger.error(f"❌ {flow_name}: {message} | Error: {error}")
    else:
        test_results["skipped"] += 1
        logger.warning(f"⚠️ {flow_name}: {message}")


# ============================================================
# CORE FLOWS TESTS (6)
# ============================================================

def test_registration_flow():
    """Test 1: Registration ConversationHandler"""
    flow_name = "Registration Flow"
    try:
        from app.handlers.user.registration import (
            start_registration, receive_email, receive_phone, 
            receive_name, confirm_registration,
            AWAITING_EMAIL, AWAITING_PHONE, AWAITING_NAME, CONFIRM
        )
        
        # Check all states exist
        assert AWAITING_EMAIL is not None
        assert AWAITING_PHONE is not None
        assert AWAITING_NAME is not None
        assert CONFIRM is not None
        
        # Check handlers exist
        assert callable(start_registration)
        assert callable(receive_email)
        assert callable(receive_phone)
        assert callable(receive_name)
        assert callable(confirm_registration)
        
        log_test_result(flow_name, "PASS", "All states and handlers exist")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import or assertion failed", e)
        return False


def test_usage_guide_flow():
    """Test 2: Usage Guide (10 steps)"""
    flow_name = "Usage Guide Flow"
    try:
        from app.handlers.support.setup_guide import (
            SETUP_GUIDE_STEPS,
            register_usage_guide_handlers,
            huongdan_command,
            usage_callback_handler
        )
        
        # Check 10 steps exist (0-9)
        assert len(SETUP_GUIDE_STEPS) == 10
        for i in range(10):
            assert i in SETUP_GUIDE_STEPS
            assert 'title' in SETUP_GUIDE_STEPS[i]
            assert 'content' in SETUP_GUIDE_STEPS[i]
        
        # Check handlers
        assert callable(register_usage_guide_handlers)
        assert callable(huongdan_command)
        assert callable(usage_callback_handler)
        
        log_test_result(flow_name, "PASS", "10 steps validated, all handlers exist")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import or validation failed", e)
        return False


def test_deploy_guide_flow():
    """Test 3: Deploy Guide (13 steps)"""
    flow_name = "Deploy Guide Flow"
    try:
        from app.handlers.user.free_flow import (
            show_deploy_guide,
            show_deploy_guide_step_0,
            taoweb_command,
            register_free_flow_handlers
        )
        
        # Check handlers exist
        assert callable(show_deploy_guide)
        assert callable(show_deploy_guide_step_0)
        assert callable(taoweb_command)
        assert callable(register_free_flow_handlers)
        
        log_test_result(flow_name, "PASS", "All deploy guide handlers exist")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_main_menu_flow():
    """Test 4: Main Menu System"""
    flow_name = "Main Menu Flow"
    try:
        from app.handlers.core.main_menu import register_main_menu_handlers
        
        assert callable(register_main_menu_handlers)
        
        log_test_result(flow_name, "PASS", "Main menu handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_reply_keyboard_flow():
    """Test 5: Persistent Reply Keyboard (6 buttons)"""
    flow_name = "Reply Keyboard Flow"
    try:
        from app.handlers.core.reply_keyboard import (
            register_reply_keyboard_handlers,
            get_main_reply_keyboard
        )
        
        assert callable(register_reply_keyboard_handlers)
        assert callable(get_main_reply_keyboard)
        
        # Test keyboard generation
        keyboard = get_main_reply_keyboard()
        assert keyboard is not None
        
        log_test_result(flow_name, "PASS", "Keyboard handlers exist and functional")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import or generation failed", e)
        return False


def test_webapp_url_handler_flow():
    """Test 6: Webapp URL ConversationHandler"""
    flow_name = "Webapp URL Handler Flow"
    try:
        from app.handlers.core.webapp_url_handler import register_webapp_handlers
        
        assert callable(register_webapp_handlers)
        
        log_test_result(flow_name, "PASS", "Webapp URL handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


# ============================================================
# USER FLOWS TESTS (6)
# ============================================================

def test_simplified_registration_flow():
    """Test 7: Simplified Registration (Pay What You Want)"""
    flow_name = "Simplified Registration Flow"
    try:
        from app.handlers.user.simplified_registration import (
            register_simplified_registration_handlers,
            start_quick_registration,
            confirm_registration_yes,
            re_register_handler
        )
        
        assert callable(register_simplified_registration_handlers)
        assert callable(start_quick_registration)
        assert callable(confirm_registration_yes)
        assert callable(re_register_handler)
        
        log_test_result(flow_name, "PASS", "All simplified registration handlers exist")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_free_flow():
    """Test 8: FREE Step-by-step Flow (8 steps)"""
    flow_name = "FREE Flow"
    try:
        from app.handlers.user.free_flow import (
            free_check_registration,
            free_step2_show_value,
            free_step3_copy_template,
            register_free_flow_handlers
        )
        
        assert callable(free_check_registration)
        assert callable(free_step2_show_value)
        assert callable(free_step3_copy_template)
        assert callable(register_free_flow_handlers)
        
        log_test_result(flow_name, "PASS", "FREE flow handlers exist")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_quick_record_template_flow():
    """Test 9: Quick Record Template"""
    flow_name = "Quick Record Template Flow"
    try:
        from app.handlers.user.quick_record_template import register_quick_record_handlers
        
        assert callable(register_quick_record_handlers)
        
        log_test_result(flow_name, "PASS", "Quick record template handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_quick_record_webhook_flow():
    """Test 10: Quick Record Webhook"""
    flow_name = "Quick Record Webhook Flow"
    try:
        from app.handlers.user.quick_record_webhook import register_quick_record_webhook_handlers
        
        assert callable(register_quick_record_webhook_handlers)
        
        log_test_result(flow_name, "PASS", "Quick record webhook handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_user_commands_flow():
    """Test 11: User Commands (balance, reports, etc)"""
    flow_name = "User Commands Flow"
    try:
        from app.handlers.user.user_commands import register_user_command_handlers
        
        assert callable(register_user_command_handlers)
        
        log_test_result(flow_name, "PASS", "User commands handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_sheets_template_flow():
    """Test 12: Sheets Template Integration"""
    flow_name = "Sheets Template Flow"
    try:
        from app.handlers.sheets.sheets_template_integration import register_sheets_template_handlers
        
        assert callable(register_sheets_template_handlers)
        
        log_test_result(flow_name, "PASS", "Sheets template handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


# ============================================================
# PREMIUM FLOWS TESTS (4)
# ============================================================

def test_vip_flow():
    """Test 13: VIP Identity Tier"""
    flow_name = "VIP Identity Tier Flow"
    try:
        from app.handlers.premium.vip import register_vip_handlers
        
        assert callable(register_vip_handlers)
        
        log_test_result(flow_name, "PASS", "VIP handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_unlock_flow_v3():
    """Test 14: Unlock Flow v3"""
    flow_name = "Unlock Flow v3"
    try:
        from app.handlers.premium.unlock_flow_v3 import register_unlock_handlers
        
        assert callable(register_unlock_handlers)
        
        log_test_result(flow_name, "PASS", "Unlock v3 handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_unlock_calm_flow():
    """Test 15: Unlock Calm Flow"""
    flow_name = "Unlock Calm Flow"
    try:
        from app.handlers.premium.unlock_calm_flow import register_unlock_calm_flow_handlers
        
        assert callable(register_unlock_calm_flow_handlers)
        
        log_test_result(flow_name, "PASS", "Unlock calm flow handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_premium_menu_flow():
    """Test 16: Premium Menu"""
    flow_name = "Premium Menu Flow"
    try:
        from app.handlers.premium.premium_menu_implementation import register_premium_menu_handlers
        
        assert callable(register_premium_menu_handlers)
        
        log_test_result(flow_name, "PASS", "Premium menu handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


# ============================================================
# SUPPORT & ENGAGEMENT FLOWS TESTS (4)
# ============================================================

def test_daily_reminder_flow():
    """Test 17: Daily Reminder System"""
    flow_name = "Daily Reminder Flow"
    try:
        from app.handlers.engagement.daily_reminder import register_reminder_handlers
        
        assert callable(register_reminder_handlers)
        
        log_test_result(flow_name, "PASS", "Daily reminder handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_sheets_setup_flow():
    """Test 18: Sheets Setup (Legacy)"""
    flow_name = "Sheets Setup Flow"
    try:
        from app.handlers.sheets.sheets_setup import register_sheets_setup_handlers
        
        assert callable(register_sheets_setup_handlers)
        
        log_test_result(flow_name, "PASS", "Sheets setup handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_callback_handler_flow():
    """Test 19: Central Callback Handler"""
    flow_name = "Callback Handler Flow"
    try:
        from app.handlers.core.callback import handle_callback
        
        assert callable(handle_callback)
        
        log_test_result(flow_name, "PASS", "Callback handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


def test_message_handler_flow():
    """Test 20: Message Handler (AI Fallback)"""
    flow_name = "Message Handler Flow"
    try:
        from app.handlers.core.message import handle_message
        
        assert callable(handle_message)
        
        log_test_result(flow_name, "PASS", "Message handler exists")
        return True
        
    except Exception as e:
        log_test_result(flow_name, "FAIL", "Import failed", e)
        return False


# ============================================================
# MAIN TEST RUNNER
# ============================================================

def run_all_tests():
    """Run all flow tests"""
    logger.info("="*80)
    logger.info("🧪 STARTING COMPREHENSIVE FLOW TESTS")
    logger.info("="*80)
    logger.info(f"Total flows to test: {test_results['total_flows']}")
    logger.info("")
    
    # Core Flows (6)
    logger.info("📦 TESTING CORE FLOWS (6)")
    logger.info("-"*80)
    test_registration_flow()
    test_usage_guide_flow()
    test_deploy_guide_flow()
    test_main_menu_flow()
    test_reply_keyboard_flow()
    test_webapp_url_handler_flow()
    logger.info("")
    
    # User Flows (6)
    logger.info("👤 TESTING USER FLOWS (6)")
    logger.info("-"*80)
    test_simplified_registration_flow()
    test_free_flow()
    test_quick_record_template_flow()
    test_quick_record_webhook_flow()
    test_user_commands_flow()
    test_sheets_template_flow()
    logger.info("")
    
    # Premium Flows (4)
    logger.info("💎 TESTING PREMIUM FLOWS (4)")
    logger.info("-"*80)
    test_vip_flow()
    test_unlock_flow_v3()
    test_unlock_calm_flow()
    test_premium_menu_flow()
    logger.info("")
    
    # Support & Engagement Flows (4)
    logger.info("🔧 TESTING SUPPORT & ENGAGEMENT FLOWS (4)")
    logger.info("-"*80)
    test_daily_reminder_flow()
    test_sheets_setup_flow()
    test_callback_handler_flow()
    test_message_handler_flow()
    logger.info("")
    
    # Print Summary
    print_summary()


def print_summary():
    """Print test summary"""
    logger.info("="*80)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*80)
    logger.info(f"Total Flows Tested: {test_results['total_flows']}")
    logger.success(f"✅ Passed: {test_results['passed']}")
    logger.error(f"❌ Failed: {test_results['failed']}")
    logger.warning(f"⚠️ Skipped: {test_results['skipped']}")
    logger.info("")
    
    pass_rate = (test_results['passed'] / test_results['total_flows']) * 100
    logger.info(f"Pass Rate: {pass_rate:.1f}%")
    logger.info("")
    
    # Print failed tests details
    if test_results['failed'] > 0:
        logger.error("❌ FAILED FLOWS:")
        logger.error("-"*80)
        for detail in test_results['details']:
            if detail['status'] == 'FAIL':
                logger.error(f"  • {detail['flow']}: {detail['message']}")
                if detail['error']:
                    logger.error(f"    Error: {detail['error']}")
        logger.info("")
    
    # Overall result
    if test_results['failed'] == 0:
        logger.success("🎉 ALL FLOWS PASSED!")
    else:
        logger.warning(f"⚠️ {test_results['failed']} flow(s) need attention")
    
    logger.info("="*80)
    
    # Save report to file
    save_report()


def save_report():
    """Save test report to file"""
    import json
    from datetime import datetime
    
    report_file = f"tests/flow_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Report saved to: {report_file}")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")


if __name__ == "__main__":
    run_all_tests()
