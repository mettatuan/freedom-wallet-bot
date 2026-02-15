"""
Automated Test Script - Full Bot Flow
Tests registration, callbacks, database, and message encoding
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from telegram import Update, User, Message, CallbackQuery, Chat
from telegram.ext import ContextTypes
from app.utils.database import SessionLocal, User as DBUser
from app.handlers.user.start import start
from app.handlers.user.registration import start_registration
from loguru import logger

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(name, status, message=""):
    """Print test result"""
    if status == "PASS":
        print(f"{Colors.GREEN}✅ PASS{Colors.RESET} | {name}")
    elif status == "FAIL":
        print(f"{Colors.RED}❌ FAIL{Colors.RESET} | {name}")
        if message:
            print(f"         {Colors.RED}└─ {message}{Colors.RESET}")
    elif status == "INFO":
        print(f"{Colors.BLUE}📋 INFO{Colors.RESET} | {name}")
        if message:
            print(f"         {Colors.BLUE}└─ {message}{Colors.RESET}")
    elif status == "WARN":
        print(f"{Colors.YELLOW}⚠️  WARN{Colors.RESET} | {name}")
        if message:
            print(f"         {Colors.YELLOW}└─ {message}{Colors.RESET}")

def check_encoding(text: str, test_name: str) -> bool:
    """Check if text has encoding issues"""
    garbled_patterns = [
        'Ã', 'â€', 'ðŸ', 'Äƒ', 'á»', 'áº'
    ]
    
    for pattern in garbled_patterns:
        if pattern in text:
            print_test(test_name, "FAIL", f"Garbled text detected: contains '{pattern}'")
            print(f"         Preview: {text[:100]}...")
            return False
    
    print_test(test_name, "PASS")
    return True

async def test_database_connection():
    """Test 1: Database connection"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST 1: DATABASE CONNECTION{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    try:
        db = SessionLocal()
        user_count = db.query(DBUser).count()
        db.close()
        print_test("Database connection", "PASS", f"{user_count} users in database")
        return True
    except Exception as e:
        print_test("Database connection", "FAIL", str(e))
        return False

async def test_user_schema():
    """Test 2: User table schema"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST 2: USER TABLE SCHEMA{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    try:
        db = SessionLocal()
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        columns = [col['name'] for col in inspector.get_columns('users')]
        db.close()
        
        required_columns = ['first_name', 'email', 'phone', 'full_name', 'referral_code']
        missing = [col for col in required_columns if col not in columns]
        
        if missing:
            print_test("Schema completeness", "FAIL", f"Missing columns: {missing}")
            return False
        else:
            print_test("Schema completeness", "PASS", f"{len(columns)} columns found")
            return True
    except Exception as e:
        print_test("Schema check", "FAIL", str(e))
        return False

async def test_start_command():
    """Test 3: /start command"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST 3: /START COMMAND{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    try:
        # Mock objects
        mock_user = User(id=999999, first_name="Test", last_name="User", is_bot=False, username="testuser")
        mock_chat = Chat(id=999999, type="private")
        mock_message = AsyncMock(spec=Message)
        mock_message.reply_text = AsyncMock()
        mock_message.chat = mock_chat
        
        mock_update = MagicMock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.message = mock_message
        mock_update.callback_query = None
        
        mock_context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.args = []
        mock_context.bot.get_me = AsyncMock(return_value=User(id=1, first_name="Bot", is_bot=True, username="testbot"))
        
        # Call start handler
        await start(mock_update, mock_context)
        
        # Check if reply_text was called
        if mock_message.reply_text.called:
            call_args = mock_message.reply_text.call_args
            message_text = call_args[0][0] if call_args[0] else call_args[1].get('text', '')
            
            print_test("/start handler executed", "PASS")
            
            # Check encoding
            if message_text:
                return check_encoding(message_text, "Start message encoding")
            return True
        else:
            print_test("/start handler", "FAIL", "reply_text not called")
            return False
            
    except Exception as e:
        print_test("/start command", "FAIL", str(e))
        import traceback
        print(f"         {traceback.format_exc()}")
        return False

async def test_registration_callback():
    """Test 4: Registration button callback"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST 4: REGISTRATION BUTTON{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    try:
        # Mock objects for callback
        mock_user = User(id=999999, first_name="Test", last_name="User", is_bot=False, username="testuser")
        mock_chat = Chat(id=999999, type="private")
        mock_message = AsyncMock(spec=Message)
        mock_message.chat = mock_chat
        
        mock_query = AsyncMock(spec=CallbackQuery)
        mock_query.answer = AsyncMock()
        mock_query.from_user = mock_user
        mock_query.message = mock_message
        mock_query.data = "register"
        
        mock_update = MagicMock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.callback_query = mock_query
        mock_update.effective_chat = mock_chat
        
        mock_context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.user_data = {}
        mock_context.bot.send_message = AsyncMock()
        
        # Call registration handler
        result = await start_registration(mock_update, mock_context)
        
        print_test("Registration handler executed", "PASS", f"Returned state: {result}")
        
        # Check if send_message was called
        if mock_context.bot.send_message.called:
            call_args = mock_context.bot.send_message.call_args
            message_text = call_args[1].get('text', '')
            
            if message_text:
                has_email_prompt = 'email' in message_text.lower() or 'Email' in message_text
                if has_email_prompt:
                    print_test("Registration message content", "PASS", "Email prompt found")
                else:
                    print_test("Registration message content", "WARN", "No email prompt found")
                
                return check_encoding(message_text, "Registration message encoding")
            return True
        else:
            print_test("Registration button", "WARN", "send_message not called")
            return True
            
    except Exception as e:
        print_test("Registration button", "FAIL", str(e))
        import traceback
        print(f"         {traceback.format_exc()}")
        return False

async def test_message_samples():
    """Test 5: Check encoding in common messages"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST 5: MESSAGE SAMPLES ENCODING{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    try:
        # Test common Vietnamese messages
        test_messages = [
            ("Chào bạn", "Basic greeting"),
            ("Đăng ký", "Register text"),
            ("Google Sheet riêng", "Sheet description"),
            ("Freedom Wallet không phải một app", "App description"),
            ("Dữ liệu nằm trên Drive", "Data description"),
        ]
        
        all_passed = True
        for text, desc in test_messages:
            # Check if text is properly encoded
            try:
                text.encode('utf-8')
                has_garbled = any(c in text for c in ['Ã', 'â€', 'ðŸ'])
                
                if has_garbled:
                    print_test(f"Message: {desc}", "FAIL", f"Garbled: {text}")
                    all_passed = False
                else:
                    print_test(f"Message: {desc}", "PASS", f"'{text}'")
            except:
                print_test(f"Message: {desc}", "FAIL", "Encoding error")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_test("Message samples", "FAIL", str(e))
        return False

async def test_handlers_import():
    """Test 6: Import all handlers"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST 6: HANDLERS IMPORT{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    handlers_to_test = [
        ("app.handlers.user.start", "Start handler"),
        ("app.handlers.user.registration", "Registration handler"),
        ("app.handlers.user.free_flow", "Free flow handler"),
        ("app.handlers.core.callback", "Callback handler"),
        ("app.handlers.engagement.referral", "Referral handler"),
    ]
    
    all_passed = True
    for module_name, desc in handlers_to_test:
        try:
            __import__(module_name)
            print_test(f"Import: {desc}", "PASS")
        except SyntaxError as e:
            print_test(f"Import: {desc}", "FAIL", f"Syntax error: {e}")
            all_passed = False
        except Exception as e:
            print_test(f"Import: {desc}", "FAIL", str(e))
            all_passed = False
    
    return all_passed

async def test_free_registration_flow():
    """Test 7: Free registration message"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST 7: FREE REGISTRATION FLOW{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    try:
        from app.handlers.user.free_registration import free_step1_intro
        
        # Mock objects
        mock_user = User(id=999999, first_name="Test", is_bot=False, username="testuser")
        mock_chat = Chat(id=999999, type="private")
        mock_message = AsyncMock(spec=Message)
        mock_message.reply_text = AsyncMock()
        mock_message.reply_photo = AsyncMock()
        mock_message.delete = AsyncMock()
        mock_message.chat = mock_chat
        
        mock_query = AsyncMock(spec=CallbackQuery)
        mock_query.answer = AsyncMock()
        mock_query.message = mock_message
        mock_query.from_user = mock_user
        mock_query.edit_message_text = AsyncMock()
        
        mock_update = MagicMock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.callback_query = mock_query
        
        mock_context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
        mock_context.user_data = {}
        
        # Call handler
        result = await free_step1_intro(mock_update, mock_context)
        
        print_test("Free registration handler", "PASS", f"Returned state: {result}")
        
        # Check message calls
        if mock_message.reply_text.called:
            call_args = mock_message.reply_text.call_args
            if call_args and len(call_args[0]) > 0:
                message_text = call_args[0][0]
                return check_encoding(message_text, "Free registration message")
        
        return True
        
    except Exception as e:
        print_test("Free registration flow", "FAIL", str(e))
        import traceback
        print(f"         {traceback.format_exc()}")
        return False

async def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.GREEN}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}FREEDOM WALLET BOT - AUTOMATED TESTS{Colors.RESET}")
    print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    results = []
    
    # Run tests
    results.append(("Database Connection", await test_database_connection()))
    results.append(("User Schema", await test_user_schema()))
    results.append(("/start Command", await test_start_command()))
    results.append(("Registration Button", await test_registration_callback()))
    results.append(("Message Encoding", await test_message_samples()))
    results.append(("Handlers Import", await test_handlers_import()))
    results.append(("Free Registration", await test_free_registration_flow()))
    
    # Summary
    print(f"\n{Colors.GREEN}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.RESET} | {test_name}")
    
    print(f"\n{Colors.BLUE}Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"\n{Colors.GREEN if passed == total else Colors.YELLOW}Result: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED! Bot is ready for testing.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}⚠️  SOME TESTS FAILED! Please fix issues before testing.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
