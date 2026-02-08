"""
Start Command Handler - Welcome Message
Week 2: Soft-integrated with State Machine
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from bot.utils.database import save_user_to_db, get_user_by_id, update_user_registration
from bot.handlers.referral import handle_referral_start
from bot.utils.sheets import sync_web_registration
from config.settings import settings

# Week 2: Import state machine (soft-integration)
from bot.core.state_machine import StateManager, UserState


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Show welcome message with menu"""
    
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    # Save user to database
    db_user = await save_user_to_db(user)
    
    # Week 4: Update Super VIP activity tracking
    from bot.core.state_machine import StateManager
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
                    # UNLOCKED: Send congratulation image + template + start onboarding
                    from pathlib import Path
                    
                    # Send congratulation image
                    image_path = Path("media/images/chucmung.png")
                    if image_path.exists():
                        with open(image_path, 'rb') as photo:
                            await update.message.reply_photo(
                                photo=photo,
                                caption=f"🎉 **CHÚC MỪNG {web_data.get('full_name', user.first_name).upper()}!** 🎉\n\n"
                                        f"✅ Bạn đã mở khóa thành công sau khi giới thiệu 2 người!",
                                parse_mode="Markdown"
                            )
                    
                    # Send detailed message
                    await update.message.reply_text(
                        f"🎁 **{tier}**\n\n"
                        f"🎁 **NHẬN NGAY:**\n\n"
                        f"📄 **1. Google Sheets Template:**\n"
                        f"👉 [Nhấn để copy Template](https://docs.google.com/spreadsheets/d/{settings.YOUR_TEMPLATE_ID})\n\n"
                        f"📚 **2. Hướng dẫn tạo Web App:**\n"
                        f"👉 [Notion Guide chi tiết](https://eliroxbot.notion.site/freedomwallet)\n\n"
                        f"🎥 **3. Video Tutorial (3 phút):**\n"
                        f"• Cách copy template\n"
                        f"• Tạo Web App trong 5 bước\n"
                        f"• Tips sử dụng hiệu quả\n\n"
                        f"💬 **4. Tham gia Group:**\n"
                        f"👉 [Freedom Wallet Community](https://t.me/freedomwalletapp)\n"
                        f"(Hỗ trợ 1-1, chia sẻ tips, cập nhật mới)\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🚀 **BẮT ĐẦU HÀNH TRÌNH TÀI CHÍNH!**\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"Trong 7 ngày tới, mình sẽ hướng dẫn bạn:\n"
                        f"• Ngày 1: Setup Web App ✓\n"
                        f"• Ngày 2: Hiểu về 6 Hũ Tiền\n"
                        f"• Ngày 3: 5 Cấp Bậc Tài Chính\n"
                        f"• Ngày 4: Thêm giao dịch đầu tiên\n"
                        f"• Ngày 5: Tính năng nâng cao\n"
                        f"• Ngày 6-7: Chiến lược đầu tư\n\n"
                        f"🤖 Sẵn sàng bắt đầu chưa?\n"
                        f"Hỏi mình bất cứ điều gì nhé! Dùng /help để xem menu.",
                        parse_mode="Markdown",
                        disable_web_page_preview=False
                    )
                    
                    # Start onboarding journey (Day 1 scheduled)
                    from bot.handlers.onboarding import start_onboarding_journey
                    await start_onboarding_journey(user.id, context)
                    
                    logger.info(f"✅ Web user {user.id} unlocked VIP and started onboarding")
                    return
                    
                else:
                    # Week 2: Transition to REGISTERED if not yet VIP
                    with StateManager() as state_mgr:
                        current_state, is_legacy = state_mgr.get_user_state(user.id)
                        if is_legacy or current_state == UserState.VISITOR:
                            state_mgr.transition_user(user.id, UserState.REGISTERED, "Web registration not unlocked")
                    # NOT UNLOCKED: Show referral link and progress with buttons
                    from bot.utils.database import generate_referral_code
                    
                    referral_code = generate_referral_code(user.id)
                    bot_username = (await context.bot.get_me()).username
                    referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
                    
                    remaining = 2 - referral_count
                    
                    keyboard = [
                        [InlineKeyboardButton("🔗 Chia sẻ ngay", callback_data="share_link")],
                        [InlineKeyboardButton("📘 Tìm hiểu thêm", url="https://freedomwallet.app")],
                        [InlineKeyboardButton("📊 Xem tiến độ", callback_data="check_progress")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        f"👋 **Chào mừng trở lại {web_data.get('full_name', user.first_name)}!**\n\n"
                        f"{tier}\n\n"
                        f"📊 **Tiến độ giới thiệu:** {referral_count} / 2 người\n"
                        f"🎯 **Còn {remaining} người nữa!**\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎁 **Bạn sẽ nhận được sau khi đủ 2 người:**\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"✅ Full Google Sheet Quản lý tài chính 3.2\n"
                        f"✅ Full Google Apps Script\n"
                        f"✅ Full Hướng dẫn tạo Web App\n"
                        f"✅ Video tutorials chi tiết\n"
                        f"✅ Toàn bộ tính năng trọn đời\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔗 **LINK CỦA BẠN:**\n"
                        f"`{referral_link}`",
                        parse_mode="Markdown",
                        reply_markup=reply_markup
                    )
                    
                    # Continue daily nurture if not started
                    from bot.handlers.daily_nurture import start_daily_nurture
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
    subscription_tier = db_user.subscription_tier if db_user else "TRIAL"
    referral_count = db_user.referral_count if db_user else 0
    is_free_unlocked = db_user.is_free_unlocked if db_user else False
    
    # Build status badge
    if subscription_tier == "PREMIUM":
        tier_badge = "💎 PREMIUM"
    elif is_free_unlocked:
        tier_badge = "✅ FREE FOREVER"
    elif subscription_tier == "TRIAL":
        tier_badge = f"🎯 TRIAL ({referral_count}/2 refs)"
    else:
        tier_badge = "🔒 LOCKED"
    
    # Welcome message
    welcome_text = f"""
👋 **Xin chào {user.first_name}!**

{tier_badge}

Mình là **Freedom Wallet Bot** 🤖 - trợ lý AI hỗ trợ bạn 24/7 về:

✅ **Tính năng app:** Giao dịch, 6 Hũ, Đầu tư, Tài sản
✅ **Hướng dẫn:** Step-by-step chi tiết
✅ **Khắc phục lỗi:** Giải quyết nhanh các vấn đề
✅ **Tư vấn tài chính:** Tips về 6 Jars method

💡 **Bạn có thể hỏi gì?**
• "Làm sao thêm giao dịch?"
• "6 hũ tiền là gì?"
• "Tại sao số dư hũ sai?"
• "Cách tính ROI đầu tư?"

📱 **Hoặc chọn menu bên dưới:**
"""
    
    # Inline keyboard with quick actions
    keyboard = []
    
    # Add registration button if not registered
    if not db_user.is_registered:
        keyboard.append([
            InlineKeyboardButton("📝 Đăng ký nhận Template FREE", callback_data="start_register")
        ])
    
    keyboard.extend([
        [
            InlineKeyboardButton("📚 Hướng dẫn", callback_data="help_tutorial"),
            InlineKeyboardButton("❓ FAQ", callback_data="help_faq")
        ],
        [
            InlineKeyboardButton("🔧 Khắc phục lỗi", callback_data="help_troubleshoot"),
            InlineKeyboardButton("💡 Tips tài chính", callback_data="help_tips")
        ],
        [
            InlineKeyboardButton("🎁 Giới thiệu bạn bè", callback_data="referral_menu")
        ],
        [
            InlineKeyboardButton("🆘 Liên hệ hỗ trợ", callback_data="contact_support")
        ],
        [
            InlineKeyboardButton("🌐 Mở Freedom Wallet", url="https://script.google.com/...")
        ]
    ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send welcome message
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
