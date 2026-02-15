"""
Interactive Test - Simulate real Telegram user flow
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Message, CallbackQuery, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def simulate_user_flow():
    """Simulate complete user registration flow"""
    print("\n" + "="*60)
    print("🤖 SIMULATING REAL USER FLOW")
    print("="*60 + "\n")
    
    # Test user
    test_user = User(id=999999, first_name="Son", is_bot=False, username="son_test")
    
    # STEP 1: User sends /start
    print("📱 Step 1: User sends /start")
    print("-" * 60)
    
    from app.handlers.user.start import start
    
    mock_chat = Chat(id=999999, type="private")
    mock_message = AsyncMock(spec=Message)
    mock_message.chat = mock_chat
    
    # Track what was sent
    sent_messages = []
    
    async def capture_reply(*args, **kwargs):
        text = args[0] if args else kwargs.get('text', '')
        reply_markup = kwargs.get('reply_markup', None)
        sent_messages.append({
            'text': text,
            'has_buttons': reply_markup is not None,
            'buttons': []
        })
        
        if reply_markup and isinstance(reply_markup, InlineKeyboardMarkup):
            for row in reply_markup.inline_keyboard:
                for button in row:
                    sent_messages[-1]['buttons'].append({
                        'text': button.text,
                        'callback_data': button.callback_data
                    })
        
        print(f"   ✅ Bot replied: {text[:80]}...")
        if reply_markup:
            print(f"   🔘 Buttons: {[b['text'] for b in sent_messages[-1]['buttons']]}")
        return AsyncMock()
    
    mock_message.reply_text = capture_reply
    
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = test_user
    mock_update.message = mock_message
    mock_update.callback_query = None
    
    mock_context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    mock_context.args = []
    mock_context.bot.get_me = AsyncMock(return_value=User(id=1, first_name="FreedomBot", is_bot=True, username="freedomwalletbot"))
    
    try:
        await start(mock_update, mock_context)
        print(f"   ✅ /start executed successfully")
    except Exception as e:
        print(f"   ❌ /start failed: {e}")
        return False
    
    # STEP 2: User clicks "Đăng ký ngay" button
    print(f"\n📱 Step 2: User clicks button")
    print("-" * 60)
    
    if not sent_messages or not sent_messages[0]['has_buttons']:
        print("   ❌ No buttons found in /start response!")
        print(f"   📊 Messages sent: {len(sent_messages)}")
        return False
    
    # Find register button
    register_button = None
    for btn in sent_messages[0]['buttons']:
        if btn['callback_data'] == 'register' or 'register' in btn['callback_data'].lower():
            register_button = btn
            break
    
    if not register_button:
        print(f"   ❌ No register button found!")
        print(f"   Available buttons: {[b['text'] for b in sent_messages[0]['buttons']]}")
        return False
    
    print(f"   ✅ Found button: '{register_button['text']}'")
    print(f"   📌 Callback data: {register_button['callback_data']}")
    
    # Simulate button click
    from app.handlers.user.registration import start_registration
    
    sent_messages.clear()
    
    mock_query = AsyncMock(spec=CallbackQuery)
    mock_query.answer = AsyncMock()
    mock_query.from_user = test_user
    mock_query.message = mock_message
    mock_query.data = register_button['callback_data']
    
    mock_update_callback = MagicMock(spec=Update)
    mock_update_callback.effective_user = test_user
    mock_update_callback.callback_query = mock_query
    mock_update_callback.effective_chat = mock_chat
    
    mock_context_callback = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    mock_context_callback.user_data = {}
    
    async def capture_send_message(*args, **kwargs):
        text = kwargs.get('text', '')
        sent_messages.append({'text': text})
        print(f"   ✅ Bot sent: {text[:80]}...")
        return AsyncMock()
    
    mock_context_callback.bot.send_message = capture_send_message
    
    try:
        result = await start_registration(mock_update_callback, mock_context_callback)
        print(f"   ✅ Registration handler executed")
        print(f"   📊 Conversation state: {result}")
        
        if sent_messages:
            message_text = sent_messages[0]['text']
            
            # Check for Vietnamese encoding
            if 'Ã' in message_text or 'â€' in message_text:
                print(f"   ❌ ENCODING ERROR detected in message")
                print(f"      Preview: {message_text[:150]}")
                return False
            
            # Check for email prompt
            if 'email' in message_text.lower() or 'Email' in message_text:
                print(f"   ✅ Email prompt detected - Registration flow working!")
                return True
            else:
                print(f"   ⚠️  No email prompt found")
                print(f"      Message: {message_text[:150]}")
                return False
        else:
            print(f"   ⚠️  No messages sent")
            return False
            
    except Exception as e:
        print(f"   ❌ Registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await simulate_user_flow()
    
    print("\n" + "="*60)
    if success:
        print("✅ USER FLOW TEST PASSED")
        print("="*60)
        print("\n🎉 Registration button is working correctly!")
        print("📋 Next: Test manually in Telegram")
        print("   1. Send /start to bot")
        print("   2. Click 'Đăng ký ngay' button")
        print("   3. Bot should ask for email\n")
        return 0
    else:
        print("❌ USER FLOW TEST FAILED")
        print("="*60)
        print("\n⚠️  Issues detected - fix before manual test\n")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
