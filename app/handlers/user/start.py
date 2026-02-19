"""
Start Command Handler - Welcome Message
Week 2: Soft-integrated with State Machine
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime
from app.utils.database import save_user_to_db, get_user_by_id, update_user_registration
from app.handlers.engagement.referral import handle_referral_start
from app.utils.sheets import sync_web_registration
from config.settings import settings

# Week 2: Import state machine (soft-integration)
from app.core.state_machine import StateManager, UserState

# Reply Keyboard (persistent main menu)
from app.handlers.core.reply_keyboard import get_main_reply_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Show welcome message with menu"""
    
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    # Save user to database
    db_user = await save_user_to_db(user)
    
    # Week 4: Update Super VIP activity tracking
    from app.core.state_machine import StateManager
    with StateManager() as sm:
        sm.update_super_vip_activity(user.id)
    
    # Check for deep link code: /start CODE
    if context.args:
        code = context.args[0]
        logger.info(f"User {user.id} started with code: {code}")
        
        # Case 1: WEB registration (from freedomwallet.app)
        if code.startswith("WEB_"):
            email_hash = code[4:]  # Remove "WEB_" prefix
            logger.info(f"🌐 Web registration detected: {email_hash}")
            
            # Try to sync from Google Sheets
            web_data = await sync_web_registration(user.id, user.username or '', email_hash)
            
            if web_data:
                # Update user in database with web registration data
                await update_user_registration(
                    user_id=user.id,
                    email=web_data.get('email'),
                    phone=web_data.get('phone'),
                    full_name=web_data.get('full_name'),
                    source='WEB',
                    referral_count=web_data.get('referral_count', 0)
                )
                
                # Reload user to check unlock status
                db_user = await get_user_by_id(user.id)
                referral_count = db_user.referral_count if db_user else 0
                is_unlocked = referral_count >= 2
                
                # Week 2: Auto-upgrade state if unlocked
                if is_unlocked:
                    with StateManager() as state_mgr:
                        new_state = state_mgr.check_and_update_state_by_referrals(user.id)
                        if new_state:
                            logger.info(f"🎯 User {user.id} auto-upgraded to {new_state.value}")
                
                tier = "💎 PREMIUM" if web_data.get('plan') == 'premium' else "🎁 FREE"
                
                if is_unlocked:
                    # UNLOCKED: Start onboarding calmly
                    from pathlib import Path
                    
                    # Send calm affirmation (not celebration)
                    await update.message.reply_text(
                        f"Chào {web_data.get('full_name', user.first_name)},\n\n"
                        f"Bạn vừa kết nối Sheet với Bot thành công.\n\n"
                        f"Bây giờ bạn có thể ghi chi tiêu ngay trong chat này.\n"
                        f"5 giây. Không cần mở Sheet.\n\n"
                        f"Sheet vẫn là của bạn.\n"
                        f"Bot chỉ là cầu nối để bạn ghi nhanh hơn.\n\n"
                        f"Thử ghi khoản chi tiêu đầu tiên nhé.",
                        parse_mode="Markdown"
                    )
                    

                    
                    # Start onboarding journey (Day 1 scheduled)
                    from app.handlers.user.onboarding import start_onboarding_journey
                    await start_onboarding_journey(user.id, context)
                    
                    # Enable daily reminders for new VIP user
                    from app.utils.database import SessionLocal
                    db = SessionLocal()
                    db_user = db.merge(db_user)  # Merge into new session
                    db_user.reminder_enabled = True
                    db.commit()
                    db.close()
                    logger.info(f"✅ Enabled daily reminders for new VIP user {user.id}")
                    
                    logger.info(f"✅ Web user {user.id} unlocked VIP and started onboarding")
                    return
                    
                else:
                    # Week 2: Transition to REGISTERED if not yet VIP
                    with StateManager() as state_mgr:
                        current_state, is_legacy = state_mgr.get_user_state(user.id)
                        if is_legacy or current_state == UserState.VISITOR:
                            state_mgr.transition_user(user.id, UserState.REGISTERED, "Web registration not unlocked")
                    # NOT UNLOCKED: Show referral link and progress with buttons
                    from app.utils.database import generate_referral_code
                    
                    referral_code = generate_referral_code(user.id)
                    bot_username = (await context.bot.get_me()).username
                    referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
                    
                    remaining = 2 - referral_count
                    
                    keyboard = [
                        [InlineKeyboardButton("🔗 Kết nối Sheet", callback_data="sheets_setup")],
                        [InlineKeyboardButton("❓ Cần hỗ trợ setup", callback_data="help_unlock")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"Chào {web_data.get('full_name', user.first_name)},\n\n"
                        f"Bạn đã setup Sheet thành công!\n"
                        f"Hệ thống quản lý tài chính riêng đã sẵn sàng.\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"💡 **Bây giờ bạn có thể:**\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"✅ Mở Sheet và bắt đầu ghi thu chi\n"
                        f"✅ Xem phân bổ 6 hũ tiền\n"
                        f"✅ Kiểm tra cấp độ tài chính\n"
                        f"✅ Xem báo cáo chi tiết\n\n"
                        f"Tuần đầu, thử ghi tay vào Sheet.\n"
                        f"Dù chậm, nhưng đây là lúc bạn \"nhìn rõ tiền\".\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🤝 **Muốn ghi nhanh hơn qua Telegram?**\n\n"
                        f"Kết nối Telegram với Sheet cần cấu hình API,\n"
                        f"hơi kỹ thuật và dễ sai.\n\n"
                        f"Nếu bạn giới thiệu 2 người bạn\n"
                        f"cũng thật sự muốn quản lý tài chính,\n"
                        f"tôi sẽ hỗ trợ bạn setup 1-1,\n"
                        f"đảm bảo kết nối thành công.\n\n"
                        f"🔗 Link giới thiệu: `{referral_link}`",
                        parse_mode="Markdown",
                        reply_markup=reply_markup
                    )
                    
                    # Continue daily nurture if not started
                    from app.handlers.engagement.daily_nurture import start_daily_nurture
                    await start_daily_nurture(user.id, context)
                    
                    return
                
            else:
                # Email hash not found in Sheets
                await update.message.reply_text(
                    "❌ **Lỗi xác thực**\n\n"
                    "Không tìm thấy thông tin đăng ký của bạn từ website.\n\n"
                    "Vui lòng:\n"
                    "1️⃣ Đăng ký lại tại [freedomwallet.app](https://freedomwallet.app)\n"
                    "2️⃣ Hoặc đăng ký trực tiếp trong bot: /register",
                    parse_mode="Markdown"
                )
                return
        
        # Case 2: Referral link (from Telegram)
        else:
            referral_code = code
            logger.info(f"🎁 Referral detected: {referral_code}")
            
            # Handle referral (will show special welcome + notify referrer)
            referred = await handle_referral_start(update, context, referral_code)
            
            if referred:
                # Show brief pause before main menu
                import asyncio
                await asyncio.sleep(2)
    
    # Get user subscription status
    subscription_tier = db_user.subscription_tier if db_user else "FREE"
    referral_count = db_user.referral_count if db_user else 0
    is_free_unlocked = db_user.is_free_unlocked if db_user else False
    
    # Determine user stage (not "tier")
    user_stage = "PREMIUM" if subscription_tier == "PREMIUM" else ("UNLOCKED" if is_free_unlocked else "FREE")
    
    # Welcome message - Different for FREE vs PREMIUM
    from app.services.recommendation import get_greeting
    greeting = get_greeting(db_user) if db_user else f"👋 Xin chào {user.first_name}!"
    
    # PREMIUM MENU - Calm, supportive
    if subscription_tier == "PREMIUM":
        days_tracking = db_user.streak_count if db_user else 0
        
        welcome_text = f"""
{greeting}

━━━━━━━━━━━━━━━━━━━━━
💎 **PREMIUM - Giảm tải não**
━━━━━━━━━━━━━━━━━━━━━

Bạn đã ghi chi tiêu được {days_tracking} ngày.

Sheet của bạn đã có đầy đủ dữ liệu và báo cáo.
Premium không thêm chart hay dashboard.

Premium giúp bạn:

• Không phải canh tiền mỗi ngày
• Được cảnh báo sớm khi có rủi ro
• Không quên khoản định kỳ
• Phát hiện chi tiêu bất thường

👉 Bạn nghĩ về tiền ÍT hơn,
nhưng kiểm soát TỐT hơn.

💡 Ghi chi tiêu, hoặc hỏi tôi bất cứ lúc nào.
"""
        
        keyboard = [
            [
                InlineKeyboardButton("💬 Ghi chi tiêu", callback_data="quick_record")
            ],
            [
                InlineKeyboardButton("📊 Xem tổng quan", callback_data="today_status"),
                InlineKeyboardButton("🛠️ Cài đặt", callback_data="setup")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    # FREE & UNLOCKED - Calm, value-focused
    else:
        if is_free_unlocked:
            # UNLOCKED: Bot is connected, user can log quickly
            days_tracking = db_user.streak_count if db_user else 0
            
            # Get user info for display
            email = db_user.email if db_user and db_user.email else "Chưa cập nhật"
            phone = db_user.phone if db_user and db_user.phone else "Chưa cập nhật"
            
            welcome_text = f"""
✅ Bạn đã đăng ký & kết nối Web App rồi!

📧 Email: {email}
📱 Phone: {phone}
🔗 Web App: Đã kết nối ✅

━━━━━━━━━━━━━━━━━━━━━

🎯 BẮT ĐẦU SỬ DỤNG NGAY:

💬 Ghi nhanh: Gửi tin nhắn `Cà phê 35k` → Tự động lưu!
🤖 Hỏi bất cứ lúc nào: "Tôi chi bao nhiêu tháng này?"

👇 Hoặc chọn menu bên dưới:
"""
            
            keyboard = [
                [InlineKeyboardButton("💬 Ghi nhanh thu chi", callback_data="quick_record")],
                [InlineKeyboardButton("📊 Báo cáo nhanh", callback_data="today_status")],
                [InlineKeyboardButton("📖 Hướng dẫn", callback_data="help_tutorial"), InlineKeyboardButton("⚙️ Cài đặt", callback_data="setup")]
            ]
        else:
            # FREE: Clear positioning first, no sales pressure
            from pathlib import Path
            
            welcome_text = f"""
Chào {user.first_name},

Tôi là trợ lý tài chính của bạn.

Freedom Wallet không phải là một ứng dụng để tải về.
Đây là một hệ thống quản lý tài chính bạn tự tạo và tự sở hữu.

Mỗi người dùng có:
• Một Google Sheet riêng
• Một Apps Script riêng
• Một Web App riêng

Toàn bộ dữ liệu nằm trên Google Drive của bạn.
Bạn toàn quyền kiểm soát.
Không phụ thuộc vào nền tảng trung gian.

Nếu bạn muốn bắt đầu,
tôi sẽ hướng dẫn từng bước một.
Rõ ràng, đơn giản và dễ làm theo.
"""
            
            keyboard = [
                [InlineKeyboardButton("📝 Đăng ký ngay", callback_data="start_free_registration")],
                [InlineKeyboardButton("📖 Tìm hiểu thêm", callback_data="learn_more")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send image with message
            image_path = Path("media/images/web_apps.jpg")
            
            try:
                await update.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption=welcome_text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
                return
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                # Fallback to text only
                pass
        
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send welcome message with inline buttons
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - Show help menu"""
    
    help_text = """
📋 **Danh Sách Lệnh**

**/start** - Hiện menu chính
**/help** - Hiện menu này
**/tutorial** - Hướng dẫn có hình ảnh
**/support** - Liên hệ support team
**/tips** - Nhận tips tài chính hàng ngày
**/status** - Kiểm tra tình trạng app

💬 **Hoặc chat trực tiếp với mình:**
Gõ câu hỏi bằng tiếng Việt hoặc English!

📚 **Ví dụ câu hỏi:**
• Làm sao thêm giao dịch?
• 6 hũ tiền là gì?
• Cách chuyển tiền giữa hũ?
• App không load được dữ liệu

🤖 Mình sẽ trả lời ngay lập tức!
"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

