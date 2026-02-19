"""
Callback Query Handler - Handle inline button clicks
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from config.settings import settings
from bot.services.analytics import Analytics
from bot.handlers.admin_callbacks import (
    handle_admin_approve_callback,
    handle_admin_reject_callback,
    handle_admin_list_pending_callback
)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline buttons"""
    
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    
    callback_data = query.data
    
    # Add try-catch for all callback handling
    try:
        await _handle_callback_internal(update, context, query, callback_data)
    except Exception as e:
        logger.error(f"Error handling callback {callback_data}: {e}", exc_info=True)
        try:
            await query.edit_message_text(
                "😓 Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau!\n"
                "Nếu vấn đề tiếp diễn, dùng /support để liên hệ.",
                parse_mode="Markdown"
            )
        except:
            pass


async def _handle_callback_internal(update: Update, context: ContextTypes.DEFAULT_TYPE, query, callback_data: str):
    
    # Skip sheets-related callbacks (handled by ConversationHandler)
    if callback_data and callback_data.startswith("sheets_"):
        logger.debug(f"Skipping sheets callback: {callback_data} (handled by ConversationHandler)")
        return
    
    # Skip free flow callbacks (handled by free_flow.py)
    if callback_data and callback_data.startswith("free_"):
        logger.debug(f"Skipping free flow callback: {callback_data} (handled by free_flow handlers)")
        return
    
    # Skip unlock flow callbacks (handled by unlock_calm_flow.py)
    if callback_data and callback_data.startswith("unlock_"):
        logger.debug(f"Skipping unlock flow callback: {callback_data} (handled by unlock_calm_flow handlers)")
        return
    
    # Skip learn_more and skip_sharing callbacks (handled by free_flow.py)
    if callback_data in ["learn_more", "skip_sharing", "show_deploy_guide", "back_to_start", "start_free_registration"]:
        logger.debug(f"Skipping free flow helper callback: {callback_data}")
        return
    
    # Week 4: Update Super VIP activity tracking
    from bot.core.state_machine import StateManager
    with StateManager() as sm:
        sm.update_super_vip_activity(query.from_user.id)
    
    logger.info(f"Callback: {callback_data} from user {query.from_user.id}")
    
    # Route usage tracker callbacks (trial start, etc.)
    from bot.middleware.usage_tracker import (
        handle_trial_start,
        handle_view_premium,
        handle_why_premium
    )
    
    if callback_data == "start_trial":
        await handle_trial_start(update, context)
        return
    elif callback_data == "view_premium":
        await handle_view_premium(update, context)
        return
    elif callback_data == "why_premium":
        await handle_why_premium(update, context)
        return
    
    # Onboarding guides for Premium trial users
    elif callback_data == "webapp_setup_guide":
        await handle_webapp_setup_guide(update, context)
        return
    elif callback_data == "premium_usage_guide":
        await handle_premium_usage_guide(update, context)
        return
    
    # DAY 2: ROI & Upsell callbacks
    elif callback_data == "upgrade_to_premium":
        await handle_upgrade_to_premium(update, context)
        return
    elif callback_data == "confirm_payment":
        await handle_confirm_payment(update, context)
        return
    elif callback_data == "view_roi_detail":
        await handle_view_roi_detail(update, context)
        return
    elif callback_data == "optimization_tips":
        await handle_optimization_tips(update, context)
        return
    
    # DAY 3: Analytics tracking callbacks
    elif callback_data == "wow_moment_dismiss":
        await handle_wow_moment_dismiss(update, context)
        return
    
    # Start menu callbacks
    elif callback_data == "free_chat":
        await handle_free_chat(update, context)
        return
    elif callback_data == "upgrade_premium":
        await handle_upgrade_premium_from_start(update, context)
        return
    
    # Route Premium callbacks
    from bot.handlers.premium_commands import PREMIUM_CALLBACKS
    if callback_data in PREMIUM_CALLBACKS:
        handler = PREMIUM_CALLBACKS[callback_data]
        try:
            await handler(update, context)
        except Exception as e:
            logger.error(f"Error in Premium callback {callback_data}: {e}", exc_info=True)
            await query.edit_message_text(
                f"😓 Xin lỗi, có lỗi khi xử lý '{callback_data}'. Vui lòng thử lại!\n\n"
                f"Nếu vấn đề tiếp diễn, dùng /support để liên hệ.",
                parse_mode="Markdown"
            )
        return
    
    # Admin payment approval callbacks
    if callback_data.startswith("admin_approve_"):
        await handle_admin_approve_callback(update, context)
        return
    elif callback_data.startswith("admin_reject_"):
        await handle_admin_reject_callback(update, context)
        return
    elif callback_data == "admin_list_pending":
        await handle_admin_list_pending_callback(update, context)
        return
    
    # Route to appropriate handler based on callback_data
    if callback_data == "start" or callback_data == "back_home":
        # Back to home
        from bot.handlers.start import start
        # Create mock update for start command
        update.message = query.message
        try:
            await start(update, context)
        except Exception as e:
            logger.error(f"Error calling start handler: {e}", exc_info=True)
            await query.edit_message_text(
                "😓 Xin lỗi, có lỗi khi quay về trang chủ. Vui lòng gõ /start để thử lại!",
                parse_mode="Markdown"
            )
        return
    
    elif callback_data == "help_tutorial":
        text = """
📚 **Hướng Dẫn Sử Dụng Freedom Wallet**

🌐 **Xem hướng dẫn đầy đủ tại:**
👉 [eliroxbot.notion.site/freedomwallet](https://eliroxbot.notion.site/freedomwallet)

📖 **Nội dung bao gồm:**
• Hướng dẫn bắt đầu (Getting Started)
• Cài đặt Web App trên điện thoại
• 6 Hũ tiền là gì & cách sử dụng
• Ghi chép giao dịch nhanh
• Phân tích tài chính & ROI
• Gợi ý thông minh

💡 **Hoặc hỏi mình trực tiếp:**
"Làm sao thêm giao dịch?"
"6 hũ tiền là gì?"
"Cách cài Web App?"
"""
        keyboard = [
            [InlineKeyboardButton("🌐 Mở hướng dẫn", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("🏠 Quay lại", callback_data="back_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
    elif callback_data == "help_faq":
        text = """
❓ **Câu Hỏi Thường Gặp (FAQ)**

**📝 Giao dịch:**
• Thêm / Sửa / Xóa giao dịch
• Lọc và tìm kiếm

**🏺 6 Hũ Tiền:**
• Phương pháp 6 Jars là gì?
• Chuyển tiền giữa hũ
• Tại sao số dư hũ sai?

**📈 Đầu tư:**
• Thêm khoản đầu tư
• Tính ROI & lợi nhuận
• Bán đầu tư

**🔧 Khắc phục lỗi:**
• App không load
• Đồng bộ chậm
• Đăng nhập lỗi

💬 **Gõ câu hỏi của bạn để mình trả lời chi tiết!**
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "help_troubleshoot":
        text = """
🔧 **Khắc Phục Lỗi Thường Gặp**

**1️⃣ App không load dữ liệu:**
• Click nút 🔄 để refresh
• Clear browser cache (Ctrl+Shift+Delete)
• Thử browser khác

**2️⃣ Số dư hũ không đúng:**
• Kiểm tra danh mục gắn hũ nào
• Đảm bảo Auto Allocate bật
• Reload data (🔄)

**3️⃣ Đồng bộ chậm:**
• Bình thường! Optimistic UI sync 1-2s
• Đợi background sync hoàn tất
• Nếu quá 10s → F12 console check lỗi

💬 **Nếu vẫn lỗi:** Dùng /support để báo chi tiết!
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "help_tips":
        text = """
💡 **Tips Tài Chính**

**🏺 6 Jars Method:**
Phân chia thu nhập thành 6 phần:
• NEC (55%): Nhu cầu thiết yếu
• LTS (10%): Tiết kiệm dài hạn
• EDU (10%): Giáo dục
• PLAY (10%): Giải trí
• FFA (10%): Tự do tài chính (đầu tư)
• GIVE (5%): Cho đi

💰 **Nguyên tắc vàng:**
1. Trả tiền cho bản thân trước (LTS + FFA)
2. Đầu tư đều đặn mỗi tháng
3. Review báo cáo cuối tháng
4. Điều chỉnh tỷ lệ phù hợp bản thân

📚 Đọc thêm: "6 Hũ Tiền - Bí Mật Tư Duy Triệu Phú"
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "contact_support":
        text = """
🆘 **Liên Hệ Hỗ Trợ**

Gặp vấn đề cần hỗ trợ?

📝 Dùng lệnh: **/support**

Hoặc liên hệ trực tiếp:
📧 Email: support@freedomwallet.com
💬 Telegram: @FreedomWalletSupport

⏱️ *Phản hồi trong 24h làm việc*
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "feedback_solved":
        await query.edit_message_text(
            "🎉 **Tuyệt vời! Vấn đề đã được giải quyết!**\n\n"
            "Nếu cần gì thêm, cứ hỏi mình nhé! 💬",
            parse_mode="Markdown"
        )
    
    elif callback_data == "feedback_unsolved":
        text = """
😔 **Xin lỗi, câu trả lời chưa giải quyết được vấn đề của bạn.**

🆘 **Hãy liên hệ support team:**
Dùng /support để tạo ticket, team sẽ hỗ trợ chi tiết hơn!

Hoặc mô tả lại vấn đề, mình sẽ cố gắng giúp!
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "ask_more":
        await query.edit_message_text(
            "💬 **Hỏi thêm câu khác đi!**\n\nGõ câu hỏi của bạn, mình sẵn sàng trả lời! 😊",
            parse_mode="Markdown"
        )
    # Skip registration callbacks (handled by ConversationHandler)
    if callback_data == "start_register":
        logger.debug(f"Skipping registration callback: {callback_data} (handled by ConversationHandler)")
        return
    
    elif callback_data == "cancel_support":
        await query.edit_message_text(
            "❌ **Đã hủy tạo ticket.**\n\nNếu cần hỗ trợ, dùng /support bất cứ lúc nào!",
            parse_mode="Markdown"
        )
    
    elif callback_data == "referral_menu":
        # Show referral system
        from bot.handlers.referral import referral_command
        from bot.utils.database import get_user_by_id
        
        user = query.from_user
        db_user = await get_user_by_id(user.id)
        
        if not db_user:
            await query.edit_message_text("❌ Lỗi: Không tìm thấy user. Vui lòng /start lại.")
            return
        
        # Get referral stats
        from bot.utils.database import get_user_referrals
        
        referral_code = db_user.referral_code
        referral_count = db_user.referral_count
        is_unlocked = db_user.is_free_unlocked
        referred_users = await get_user_referrals(user.id)
        
        # Build referral link
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        # Status message
        if is_unlocked:
            status_msg = "✅ **FREE FOREVER đã mở khóa!**\n\n"
        else:
            remaining = 2 - referral_count
            status_msg = f"🎯 **Còn {remaining} người nữa để mở khóa FREE!**\n\n"
        
        # Build message
        message = f"""
🎁 **HỆ THỐNG GIỚI THIỆU BẠN BÈ**

{status_msg}📊 **Thống Kê Của Bạn:**
• Mã giới thiệu: `{referral_code}`
• Đã giới thiệu: {referral_count} người
• Trạng thái: {"✅ FREE Unlocked" if is_unlocked else "🔒 Đang khóa"}

🔗 **Link giới thiệu:**
`{referral_link}`

📱 **Cách sử dụng:**
1. Copy link trên
2. Gửi cho bạn bè/gia đình
3. Khi 2 người đăng ký → **FREE FOREVER**!

💎 **Quyền lợi FREE:**
✓ Bot không giới hạn
✓ Template đầy đủ
✓ Hướng dẫn chi tiết
✓ Cộng đồng support
"""
        
        # Show referred users list
        if referred_users:
            message += f"\n👥 **Đã giới thiệu:**\n"
            for idx, ref_user in enumerate(referred_users[:5], 1):  # Max 5
                name = ref_user['name']
                date = ref_user['date'].strftime("%d/%m/%Y")
                message += f"{idx}. {name} ({date})\n"
        
        # Keyboard
        keyboard = [
            [InlineKeyboardButton("📢 Chia sẻ ngay", 
                                 url=f"https://t.me/share/url?url={referral_link}&text=Tham gia Freedom Wallet Bot - Quản lý tài chính thông minh!")],
            [InlineKeyboardButton("« Quay lại", callback_data="start")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    elif callback_data == "share_link":
        # Handle share link button from daily nurture
        from bot.handlers.daily_nurture import handle_share_link_button
        await handle_share_link_button(update, context)
    
    elif callback_data == "check_progress":
        # Handle check progress button
        from bot.handlers.daily_nurture import handle_check_progress_button
        await handle_check_progress_button(update, context)
    
    elif callback_data == "vip_gifts":
        # Show VIP gift menu (6 gift options)
        keyboard = [
            [InlineKeyboardButton("🎁 Nhận Google Sheet 3.2", callback_data="gift_sheet")],
            [InlineKeyboardButton("⚙️ Nhận Google Apps Script", callback_data="gift_script")],
            [InlineKeyboardButton("🌐 Hướng dẫn tạo Web App", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("🎥 Xem video hướng dẫn", callback_data="gift_video")],
            [InlineKeyboardButton("💬 Tham gia Group VIP", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("🏠 Vào Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎁 **MENU NHẬN QUÀ**\n\n"
            "Chọn từng mục bên dưới để nhận quà của bạn:\n\n"
            "🎁 **Google Sheet 3.2** - Công cụ quản lý tài chính\n"
            "⚙️ **Apps Script** - Code tự động hóa\n"
            "🌐 **Web App Guide** - Hướng dẫn deploy\n"
            "🎥 **Video Tutorials** - Học từng bước\n"
            "💬 **VIP Group** - Cộng đồng độc quyền\n\n"
            "💡 Bạn có thể quay lại menu này bất cứ lúc nào!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data == "onboarding_start":
        # Start 7-day onboarding journey
        from bot.handlers.onboarding import start_onboarding_journey
        
        user_id = query.from_user.id
        success = await start_onboarding_journey(user_id, context)
        
        if success:
            await query.edit_message_text(
                "🎓 **HÀNH TRÌNH 7 NGÀY BẮT ĐẦU!**\n\n"
                "Chúc mừng! Bạn vừa đăng ký hành trình học tập 7 ngày.\n\n"
                "📅 **Lịch trình:**\n"
                "• Day 1: Giới thiệu 6 Hũ Tiền\n"
                "• Day 2: Setup Google Sheet cơ bản\n"
                "• Day 3: Quản lý thu chi hàng ngày\n"
                "• Day 4: Apps Script & Automation\n"
                "• Day 5: Phân tích tài chính\n"
                "• Day 6: Mục tiêu & Kế hoạch\n"
                "• Day 7: Dashboard & Báo cáo\n\n"
                "📬 Mỗi ngày bạn sẽ nhận được:\n"
                "✅ 1 bài học ngắn (3-5 phút)\n"
                "✅ Video hướng dẫn chi tiết\n"
                "✅ Bài tập thực hành\n\n"
                "💡 Tin nhắn đầu tiên sẽ đến trong vài phút!\n\n"
                "Chúc bạn học tập hiệu quả! 🚀",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "❌ **Lỗi**\n\n"
                "Không thể bắt đầu hành trình. Vui lòng thử lại sau.",
                parse_mode="Markdown"
            )
    
    elif callback_data == "gift_sheet":
        # Send Google Sheet template link
        keyboard = [
            [InlineKeyboardButton("🎁 Nhận thêm quà khác", callback_data="vip_gifts")],
            [InlineKeyboardButton("🎓 Bắt đầu hành trình 7 ngày", callback_data="onboarding_start")],
            [InlineKeyboardButton("🏠 Về Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📄 **GOOGLE SHEET TEMPLATE 3.2**\n\n"
            "Đây là bộ công cụ quản lý tài chính cá nhân hoàn chỉnh:\n\n"
            "✅ 6 Hũ Tiền tự động\n"
            "✅ Dashboard trực quan\n"
            "✅ Theo dõi 5 Cấp Bậc Tài Chính\n"
            "✅ Quản lý đầu tư & ROI\n"
            "✅ Báo cáo tháng/năm\n\n"
            "👉 **Link Template:**\n"
            f"[Click để copy Template](https://docs.google.com/spreadsheets/d/{settings.YOUR_TEMPLATE_ID})\n\n"
            "📚 **Hướng dẫn sử dụng:**\n"
            "1. Click link trên\n"
            "2. File → Make a copy\n"
            "3. Đổi tên theo ý bạn\n"
            "4. Bắt đầu dùng ngay!\n\n"
            "💡 Xem thêm: /help",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    elif callback_data == "gift_script":
        # Send Apps Script code snippet
        keyboard = [
            [InlineKeyboardButton("🎁 Nhận thêm quà khác", callback_data="vip_gifts")],
            [InlineKeyboardButton("🎓 Bắt đầu hành trình 7 ngày", callback_data="onboarding_start")],
            [InlineKeyboardButton("🏠 Về Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ **GOOGLE APPS SCRIPT**\n\n"
            "Script này tự động hóa việc đồng bộ dữ liệu:\n\n"
            "✅ Auto sync Sheet → Web App\n"
            "✅ Calculate 6 Jars balance\n"
            "✅ Update ROI dashboard\n"
            "✅ Generate reports\n\n"
            "📋 **Cách cài đặt:**\n"
            "1. Mở Google Sheet của bạn\n"
            "2. Extensions → Apps Script\n"
            "3. Copy paste code từ Notion guide\n"
            "4. Deploy as Web App\n\n"
            "🌐 **Full guide:**\n"
            "[Notion - Hướng dẫn chi tiết](https://eliroxbot.notion.site/freedomwallet)\n\n"
            "💡 Cần hỗ trợ? Hỏi mình bất cứ lúc nào!",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    elif callback_data == "gift_video":
        # Send video tutorial links
        keyboard = [
            [InlineKeyboardButton("🎁 Nhận thêm quà khác", callback_data="vip_gifts")],
            [InlineKeyboardButton("🎓 Bắt đầu hành trình 7 ngày", callback_data="onboarding_start")],
            [InlineKeyboardButton("🏠 Về Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎥 **VIDEO TUTORIALS**\n\n"
            "Series video hướng dẫn từng bước:\n\n"
            "📹 **Video 1: Setup cơ bản (3 phút)**\n"
            "• Copy Google Sheet Template\n"
            "• Cấu hình cơ bản\n"
            "• Thêm giao dịch đầu tiên\n\n"
            "📹 **Video 2: Apps Script & Web App (5 phút)**\n"
            "• Deploy Apps Script\n"
            "• Tạo Web App URL\n"
            "• Test đồng bộ\n\n"
            "📹 **Video 3: Advanced features (7 phút)**\n"
            "• 6 Hũ Tiền chi tiết\n"
            "• Quản lý đầu tư\n"
            "• ROI tracking\n\n"
            "🔗 **Link playlist:**\n"
            "[YouTube - Freedom Wallet Tutorials](https://youtube.com/@freedomwallet)\n\n"
            "💬 Xem xong mà còn thắc mắc? Hỏi mình nhé!",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    # ============================================
    # ONBOARDING CALLBACKS (7-Day Journey)
    # ============================================
    
    elif callback_data == "onboard_copy_template":
        # Send template link when user clicks Copy Template
        await query.answer("📑 Đang gửi link template...")
        
        keyboard = [
            [InlineKeyboardButton("🌐 Hướng dẫn Web App", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("✅ Đã copy xong", callback_data="onboard_complete_1")],
            [InlineKeyboardButton("❓ Cần hỗ trợ", callback_data="onboard_help_1")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"📑 **FREEDOM WALLET TEMPLATE**\n\n"
                 f"👉 **Link template:** [Click để mở]({settings.YOUR_TEMPLATE_ID})\n\n"
                 f"**Cách sử dụng:**\n"
                 f"1. Click link ở trên\n"
                 f"2. File → Make a copy\n"
                 f"3. Đặt tên: 'My Freedom Wallet'\n"
                 f"4. Click '✅ Đã copy xong' bên dưới\n\n"
                 f"💡 Template sẽ mở trong Google Drive của bạn!",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    elif callback_data == "onboard_video_day1":
        # Send Day 1 video tutorial
        await query.answer("🎥 Đang gửi video tutorial...")
        
        keyboard = [
            [InlineKeyboardButton("📑 Copy Template", callback_data="onboard_copy_template")],
            [InlineKeyboardButton("🌐 Hướng dẫn Web App", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("✅ Đã xem xong", callback_data="onboard_complete_1")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="🎥 **VIDEO HƯỚNG DẪN SETUP (3 PHÚT)**\n\n"
                 "📹 **Nội dung video:**\n"
                 "• Cách copy template\n"
                 "• Setup Google Apps Script\n"
                 "• Deploy Web App\n"
                 "• Thêm dữ liệu đầu tiên\n\n"
                 "👉 **Link video:** [Xem trên YouTube](https://youtube.com/@freedomwallet)\n\n"
                 "💬 Xem xong mà chưa hiểu? Click 'Cần hỗ trợ' nhé!",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    elif callback_data == "onboard_roadmap":
        # Show 7-day roadmap overview
        await query.answer("📋 Đang gửi lộ trình...")
        
        keyboard = [
            [InlineKeyboardButton("🏠 Về Dashboard", callback_data="start")],
            [InlineKeyboardButton("💬 Tham gia Group VIP", url="https://t.me/freedomwalletapp")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📋 **LỘ TRÌNH 7 NGÀY - FREEDOM WALLET**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎁 **Bước đầu tiên:** Thiết lập Freedom Wallet\n"
            "   • Copy template, tạo Web App, nhập dữ liệu đầu tiên\n"
            "   • Thời gian: 10-15 phút\n\n"
            "💰 **Ngày 2:** Hiểu về 6 Hũ Tiền\n"
            "   • Chi tiêu thiết yếu, Hưởng thụ, Đầu tư...\n"
            "   • Phân bổ % thu nhập hợp lý\n\n"
            "🎯 **Ngày 3:** 5 Cấp Bậc Tài Chính\n"
            "   • Từ Survival → Financial Freedom\n"
            "   • Xác định vị trí hiện tại của bạn\n\n"
            "⚡ **Ngày 4:** Thêm giao dịch & Tracking\n"
            "   • Thói quen ghi chép hàng ngày\n"
            "   • Tips để tracking hiệu quả\n\n"
            "📈 **Ngày 5:** Tính năng nâng cao\n"
            "   • Budget planning, ROI tracking\n"
            "   • Automation với Apps Script\n\n"
            "👥 **Ngày 6:** Tham gia cộng đồng\n"
            "   • Kết nối với VIPs khác\n"
            "   • Chia sẻ & học hỏi kinh nghiệm\n\n"
            "🎊 **Ngày 7:** Ôn tập & Kế hoạch dài hạn\n"
            "   • Review toàn bộ hệ thống\n"
            "   • Lên kế hoạch 30-90 ngày tới\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 Mỗi ngày chỉ mất 5-10 phút.\n"
            "Bạn sẽ nhận tin nhắn vào 10h sáng mỗi ngày!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data.startswith("onboard_complete_"):
        # User completed an onboarding day
        day = callback_data.split("_")[-1]
        
        congratulations = {
            "1": "🎉 **HOÀN THÀNH DAY 1!**\n\nXuất sắc! Bạn đã setup xong Foundation.\n\n📅 **Ngày mai:** Tìm hiểu về 6 Hũ Tiền\n💬 Mình sẽ nhắn bạn khoảng 10h sáng!",
            "2": "💰 **HOÀN THÀNH DAY 2!**\n\nBạn đã hiểu về 6 Hũ Tiền rồi đấy!\n\n📅 **Ngày mai:** 5 Cấp Bậc Tài Chính",
            "3": "🎯 **HOÀN THÀNH DAY 3!**\n\nĐã biết mình đang ở cấp nào chưa?\n\n📅 **Ngày mai:** Thêm giao dịch đầu tiên",
            "4": "⚡ **HOÀN THÀNH DAY 4!**\n\nTracking tốt! Tiếp tục duy trì nhé.\n\n📅 **Ngày mai:** Tính năng nâng cao",
            "5": "📈 **HOÀN THÀNH DAY 5!**\n\nBạn đã master Freedom Wallet rồi!\n\n📅 **Ngày mai:** Challenge 30 ngày",
            "6": "💪 **HOÀN THÀNH DAY 6!**\n\nReady for challenge?\n\n📅 **Ngày mai:** Wrap up & next steps",
            "7": "🏆 **HOÀN THÀNH 7-DAY JOURNEY!**\n\nChúc mừng! Bạn đã hoàn thành hành trình!\n\n🚀 Giờ là lúc áp dụng vào thực tế!"
        }
        
        keyboard = [
            [InlineKeyboardButton("💬 Tham gia Group VIP", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("🏠 Về Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            congratulations.get(day, "✅ Hoàn thành!"),
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # TODO: Update onboarding_progress in database
        logger.info(f"User {query.from_user.id} completed onboarding day {day}")
    
    elif callback_data.startswith("onboard_help_"):
        # User needs help with onboarding
        day = callback_data.split("_")[-1]
        
        keyboard = [
            [InlineKeyboardButton("� Hướng dẫn chi tiết (Notion)", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("💬 Group VIP", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("📞 Liên hệ Admin", url=f"https://t.me/{settings.BOT_USERNAME.replace('Bot', '')}")],
            [InlineKeyboardButton("🔙 Quay lại", callback_data=f"onboard_replay_{day}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"❓ **CẦN HỖ TRỢ?**\n\n"
            f"Không sao cả! Mình ở đây để giúp bạn.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**Bạn có thể:**\n\n"
            f"📖 **Xem hướng dẫn chi tiết** (có ảnh từng bước)\n"
            f"💬 **Hỏi trong Group VIP** (community rất nhiệt tình)\n"
            f"📞 **Nhắn Admin** (hỗ trợ 1-1)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏰ **Thời gian hỗ trợ:**\n"
            f"• Thứ 2-6: 9h-21h\n"
            f"• Thứ 7-CN: 10h-18h\n\n"
            f"💬 Hoặc gõ trực tiếp câu hỏi để mình trả lời nhé!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    # ============================================
    # VIP UNLOCK FLOW CALLBACKS
    # ============================================
    
    elif callback_data == "vip_continue":
        # Message 3B: Action menu after user sees benefits
        await query.answer("✨ Xuất sắc!")
        
        keyboard_3b = [
            [InlineKeyboardButton("✅ Tôi đã tạo xong", callback_data="webapp_ready")],
            [InlineKeyboardButton("📖 Xem hướng dẫn 3 bước", callback_data="webapp_setup_guide")]
        ]
        reply_markup_3b = InlineKeyboardMarkup(keyboard_3b)
        
        await query.edit_message_text(
            "🚀 **Để sử dụng Freedom Wallet,**\n"
            "bạn cần tạo Web App (3–5 phút).\n\n"
            "Bạn đã tạo xong chưa?",
            parse_mode="Markdown",
            reply_markup=reply_markup_3b
        )
    
    # ============================================
    # WEB APP SETUP GUIDE CALLBACKS
    # ============================================
    
    elif callback_data == "webapp_ready":
        # User confirmed they completed Web App setup
        await query.answer("🎉 Tuyệt vời! Chúc mừng bạn!")
        
        keyboard = [
            [InlineKeyboardButton("📊 Xem hướng dẫn sử dụng", callback_data="onboard_complete_1")],
            [InlineKeyboardButton("🎁 Nhận thêm quà VIP", callback_data="vip_gifts")],
            [InlineKeyboardButton("💬 Tham gia Group", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("🏠 Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎉 **XUẤT SẮC! BẠN ĐÃ HOÀN THÀNH SETUP!**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ Web App Freedom Wallet của bạn đã sẵn sàng!\n\n"
            "🚀 **BƯỚC TIẾP THEO:**\n\n"
            "1️⃣ **Thêm giao dịch đầu tiên**\n"
            "   • Mở Web App của bạn\n"
            "   • Click 'Thêm giao dịch'\n"
            "   • Nhập thu/chi hôm nay\n\n"
            "2️⃣ **Khám phá 6 Hũ Tiền**\n"
            "   • Xem phân bổ tự động\n"
            "   • Điều chỉnh % theo nhu cầu\n\n"
            "3️⃣ **Theo dõi dashboard**\n"
            "   • Biểu đồ thu chi\n"
            "   • ROI tracking\n"
            "   • Financial Level\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 **Lời khuyên:**\n"
            "Track mỗi ngày trong 7 ngày đầu để hình thành thói quen!\n\n"
            "📚 Cần hỗ trợ? Hỏi trong Group VIP nhé!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data == "webapp_setup_guide":
        # Send step-by-step setup guide with images
        await query.answer("📖 Đang gửi hướng dẫn chi tiết...")
        
        from pathlib import Path
        import asyncio
        
        # Step 1: Copy template
        step1_image = Path("media/images/buoc-1-copy.jpg.webp")
        if step1_image.exists():
            with open(step1_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption="📋 **BƯỚC 1: TẠO BẢN SAO**\n\n"
                            "1️⃣ Click link template: [v3.2] Freedom Wallet\n"
                            "2️⃣ Vào **File** → **Make a copy**\n"
                            "3️⃣ Đặt tên: 'My Freedom Wallet'\n"
                            "4️⃣ Lưu vào Google Drive của bạn\n\n"
                            "✅ Done? Chờ Bước 2...",
                    parse_mode="Markdown"
                )
        
        await asyncio.sleep(2)
        
        # Step 2: Apps Script
        step2_image = Path("media/images/buoc-2-appscript.jpg")
        if step2_image.exists():
            with open(step2_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption="⚙️ **BƯỚC 2: MỞ APPS SCRIPT**\n\n"
                            "1️⃣ Trong Google Sheet vừa copy\n"
                            "2️⃣ Click **Extensions** (thanh menu trên)\n"
                            "3️⃣ Chọn **Apps Script**\n"
                            "4️⃣ Cửa sổ mới sẽ mở ra\n\n"
                            "💡 Nếu không thấy Extensions, bấm vào 3 chấm (...) ở menu\n\n"
                            "✅ Đã mở Apps Script? Chờ Bước 3...",
                    parse_mode="Markdown"
                )
        
        await asyncio.sleep(2)
        
        # Step 3: Deploy
        step3_image = Path("media/images/buoc-3-deploy.jpg")
        if step3_image.exists():
            with open(step3_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption="🚀 **BƯỚC 3: DEPLOY WEB APP**\n\n"
                            "1️⃣ Trong Apps Script editor\n"
                            "2️⃣ Click nút **Deploy** (góc trên bên phải)\n"
                            "3️⃣ Chọn **New deployment**\n"
                            "4️⃣ Type: **Web app**\n"
                            "5️⃣ Execute as: **Me**\n"
                            "6️⃣ Who has access: **Anyone**\n"
                            "7️⃣ Click **Deploy**\n"
                            "8️⃣ Copy **Web app URL** → Save lại!\n\n"
                            "⚠️ **Lưu ý:** Lần đầu sẽ cần authorize (cho phép quyền)\n\n"
                            "✅ Đã deploy xong? Xem Bước 4...",
                    parse_mode="Markdown"
                )
        
        await asyncio.sleep(2)
        
        # Step 4: Completed
        step4_image = Path("media/images/buoc-4-completed.jpg")
        keyboard = [
            [InlineKeyboardButton("✅ Đã làm xong!", callback_data="webapp_ready")],
            [InlineKeyboardButton("🌐 Hướng dẫn chi tiết", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("❓ Cần hỗ trợ", callback_data="webapp_need_help")],
            [InlineKeyboardButton("🔙 Xem lại từ đầu", callback_data="webapp_setup_guide")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if step4_image.exists():
            with open(step4_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption="🎉 **HOÀN TẤT! WEB APP CỦA BẠN SẴN SÀNG!**\n\n"
                            "━━━━━━━━━━━━━━━━━━━━━\n\n"
                            "🌐 **Web App URL** đã được tạo!\n\n"
                            "📱 **Cách sử dụng:**\n"
                            "• Mở URL trên điện thoại/máy tính\n"
                            "• Add to Home Screen (nếu dùng mobile)\n"
                            "• Bắt đầu thêm giao dịch!\n\n"
                            "━━━━━━━━━━━━━━━━━━━━━\n\n"
                            "💡 **Mẹo:**\n"
                            "• Bookmark URL để truy cập nhanh\n"
                            "• Đồng bộ tự động mỗi khi bạn cập nhật\n"
                            "• Dữ liệu lưu trong Google Sheet của bạn\n\n"
                            "🎯 **Bạn đã làm xong chưa?**",
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
        else:
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text="🎉 **HOÀN TẤT! WEB APP CỦA BẠN SẴN SÀNG!**\n\n"
                     "━━━━━━━━━━━━━━━━━━━━━\n\n"
                     "🌐 **Web App URL** đã được tạo!\n\n"
                     "📱 **Cách sử dụng:**\n"
                     "• Mở URL trên điện thoại/máy tính\n"
                     "• Add to Home Screen (nếu dùng mobile)\n"
                     "• Bắt đầu thêm giao dịch!\n\n"
                     "━━━━━━━━━━━━━━━━━━━━━\n\n"
                     "💡 **Mẹo:**\n"
                     "• Bookmark URL để truy cập nhanh\n"
                     "• Đồng bộ tự động mỗi khi bạn cập nhật\n"
                     "• Dữ liệu lưu trong Google Sheet của bạn\n\n"
                     "🎯 **Bạn đã làm xong chưa?**",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    
    elif callback_data == "webapp_need_help":
        # User needs help with Web App setup
        keyboard = [
            [InlineKeyboardButton("🔙 Xem lại hướng dẫn", callback_data="webapp_setup_guide")],
            [InlineKeyboardButton("🌐 Notion chi tiết", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("💬 Hỏi trong Group", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("📞 Liên hệ Admin", url=f"https://t.me/{settings.BOT_USERNAME.replace('Bot', '')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "❓ **CẦN HỖ TRỢ SETUP WEB APP?**\n\n"
            "Mình sẵn sàng giúp bạn!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "**💬 CÁC CÁCH ĐƯỢC HỖ TRỢ:**\n\n"
            "1️⃣ **Xem lại hướng dẫn**\n"
            "   • Click 'Xem lại hướng dẫn'\n"
            "   • Follow từng bước cẩn thận\n\n"
            "2️⃣ **Đọc Notion chi tiết**\n"
            "   • Hướng dẫn có ảnh chụp màn hình\n"
            "   • Video demo\n"
            "   • FAQ troubleshooting\n\n"
            "3️⃣ **Hỏi Group VIP**\n"
            "   • Response nhanh từ community\n"
            "   • Nhiều người đã setup thành công\n\n"
            "4️⃣ **Liên hệ Admin trực tiếp**\n"
            "   • 1-1 support\n"
            "   • Screen share nếu cần\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⏰ **Thời gian hỗ trợ:**\n"
            "• Thứ 2-6: 9h-21h\n"
            "• Thứ 7-CN: 10h-18h\n\n"
            "**Gặp vấn đề gì cụ thể?**\nGõ mô tả để mình hỗ trợ!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data == "super_vip_benefits":
        # Show Super VIP benefits details
        keyboard = [
            [InlineKeyboardButton("🏆 Xem Bảng xếp hạng", callback_data="leaderboard")],
            [InlineKeyboardButton("🎁 Nhận quà đặc biệt", callback_data="super_vip_gifts")],
            [InlineKeyboardButton("🏠 Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🌟 **ĐẶC QUYỀN SUPER VIP**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "**✨ Tất cả quyền lợi VIP PLUS:**\n\n"
            "🎯 **Hỗ trợ ưu tiên cấp cao 24/7**\n"
            "   • Response time < 30 phút\n"
            "   • Dedicated support team\n"
            "   • Direct line với Admin\n\n"
            "🎁 **Quà tặng độc quyền hàng tháng**\n"
            "   • Templates mới nhất\n"
            "   • Scripts nâng cao\n"
            "   • Exclusive features\n\n"
            "🏆 **Hiển thị trên Bảng xếp hạng**\n"
            "   • Top Referrers public\n"
            "   • Badge đặc biệt\n"
            "   • Recognition từ cộng đồng\n\n"
            "💬 **Group Super VIP Private**\n"
            "   • Networking với top performers\n"
            "   • Share strategies & tips\n"
            "   • Early access features\n\n"
            "🎓 **Workshop & Training độc quyền**\n"
            "   • Monthly masterclasses\n"
            "   • Advanced techniques\n"
            "   • One-on-one coaching\n\n"
            "💰 **Commission cao hơn** (Coming soon)\n"
            "   • Affiliate program\n"
            "   • Revenue sharing\n"
            "   • Partnership opportunities\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ **Lưu ý:** Super VIP cần duy trì\n"
            "hoạt động thường xuyên để giữ danh hiệu.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data == "leaderboard":
        # Show top referrers leaderboard
        from bot.utils.database import SessionLocal, User
        
        session = SessionLocal()
        try:
            # Get top 10 referrers (exclude admins)
            top_users = session.query(User).filter(
                User.referral_count > 0
            ).order_by(
                User.referral_count.desc()
            ).limit(10).all()
            
            leaderboard_text = "━━━━━━━━━━━━━━━━━━━━━\n"
            leaderboard_text += "🏆 **BẢNG XẾP HẠNG TOP REFERRERS**\n"
            leaderboard_text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            medals = ["🥇", "🥈", "🥉"]
            for idx, user in enumerate(top_users, 1):
                medal = medals[idx-1] if idx <= 3 else f"{idx}️⃣"
                name = user.username or user.full_name or "Anonymous"
                refs = user.referral_count
                
                # Show Super VIP badge
                badge = "🌟" if refs >= 50 else "⭐" if refs >= 2 else ""
                
                leaderboard_text += f"{medal} **{name}** {badge}\n"
                leaderboard_text += f"     {refs} lượt giới thiệu\n\n"
            
            leaderboard_text += "━━━━━━━━━━━━━━━━━━━━━\n"
            leaderboard_text += "💡 Bạn muốn lên top? Share link ngay!\n"
            leaderboard_text += "/referral để xem link của bạn"
            
            keyboard = [
                [InlineKeyboardButton("🔗 Xem link giới thiệu", callback_data="referral_menu")],
                [InlineKeyboardButton("🌟 Đặc quyền Super VIP", callback_data="super_vip_benefits")],
                [InlineKeyboardButton("🏠 Dashboard", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                leaderboard_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        finally:
            session.close()
    
    elif callback_data == "super_vip_gifts":
        # Show Super VIP exclusive gifts
        keyboard = [
            [InlineKeyboardButton("📊 Advanced Templates", callback_data="super_gift_templates")],
            [InlineKeyboardButton("⚙️ Premium Scripts", callback_data="super_gift_scripts")],
            [InlineKeyboardButton("🎓 Exclusive Training", url="https://freedomwallet.com/super-vip-training")],
            [InlineKeyboardButton("💬 Join Super VIP Group", url="https://t.me/freedomwallet_supervip")],
            [InlineKeyboardButton("🏠 Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 **QUÀ TẶNG SUPER VIP**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "**Chọn quà bạn muốn nhận:**\n\n"
            "📊 **Advanced Templates**\n"
            "   • Multiple portfolios support\n"
            "   • Advanced analytics dashboard\n"
            "   • Custom reporting tools\n\n"
            "⚙️ **Premium Scripts**\n"
            "   • Auto-sync enhancements\n"
            "   • Bank integration (beta)\n"
            "   • Advanced automation\n\n"
            "🎓 **Exclusive Training**\n"
            "   • Monthly webinars\n"
            "   • Strategy sessions\n"
            "   • Private consultations\n\n"
            "💬 **Super VIP Group**\n"
            "   • Network với top users\n"
            "   • Share best practices\n"
            "   • Early feature access\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🎉 Tất cả đều MIỄN PHÍ cho Super VIP!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    else:
        # Unknown callback
        logger.warning(f"Unknown callback: {callback_data}")
        await query.edit_message_text(
            "⚠️ Lệnh không hợp lệ. Dùng /help để xem menu!",
            parse_mode="Markdown"
        )

# ============================================================================
# ONBOARDING GUIDES - Premium Trial Users
# ============================================================================

async def handle_webapp_setup_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guide user through Web App installation (30 seconds)"""
    query = update.callback_query
    await query.answer()
    
    message = """
📱 **CÀI ĐẶT WEB APP (30 GIÂY)**

━━━━━━━━━━━━━━━━━━━━━
**BƯỚC 1: Mở freedomwallet.vn**
━━━━━━━━━━━━━━━━━━━━━

🌐 Truy cập: freedomwallet.vn
📱 Dùng Safari (iOS) / Chrome (Android)

━━━━━━━━━━━━━━━━━━━━━
**BƯỚC 2: Cài lên Home Screen**
━━━━━━━━━━━━━━━━━━━━━

**iPhone:** 
Share (⬆️) → Add to Home Screen → Add

**Android:**
Menu (⋮) → Add to Home screen → Add

━━━━━━━━━━━━━━━━━━━━━
**BƯỚC 3: Mở App**
━━━━━━━━━━━━━━━━━━━━━

🎯 Tìm icon Freedom Wallet
📲 Mở như app bình thường
🚀 Bắt đầu quản lý tài chính!

💡 **Lưu ý:** Lần đầu hơi lâu (10s), sau đó mượt mà!
"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Hướng dẫn sử dụng", callback_data="premium_usage_guide")],
        [InlineKeyboardButton("🌐 Mở Web App", url="https://freedomwallet.vn")],
        [InlineKeyboardButton("🏠 Menu Premium", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_wow_moment_dismiss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle WOW moment dismiss - User clicked 'OK, đã hiểu'"""
    query = update.callback_query
    await query.answer("Tuyệt vời! Tiếp tục sử dụng Premium nhé! 🚀")
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'wow_moment_dismissed')
    
    await query.edit_message_text(
        "✅ **Đã ghi nhận!**\n\n"
        "Bạn có thể xem lại ROI bất kỳ lúc nào bằng lệnh /mystatus\n\n"
        "💡 Tip: Sử dụng nhiều để tối đa hóa giá trị Premium nhé!",
        parse_mode="Markdown"
    )


async def handle_trial_reminder_viewed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track when user views trial reminder"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'trial_reminder_viewed')
    
    # Handler logic is in upgrade_to_premium or view_roi_detail
    # This is just for tracking
    

async def handle_why_premium_from_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Tại sao nên Premium?' click from trial reminder"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'trial_reminder_upgrade_clicked', {'source': 'why_premium'})
    
    message = """
🤔 **TẠI SAO NÊN PREMIUM?**

━━━━━━━━━━━━━━━━━━━━━
💎 **GIÁ TRỊ VƯỢT TRỘI:**
━━━━━━━━━━━━━━━━━━━━━

**1️⃣ TIẾT KIỆM THỜI GIAN**
⏱️ Mỗi ngày tiết kiệm ~1-2 giờ
   → Không cần tự tính toán
   → Không cần tổng hợp thủ công
   → Không cần lên kế hoạch

**2️⃣ TĂNG HIỆU QUẢ TÀI CHÍNH**
📊 Phân tích thông minh 24/7
   → Phát hiện điểm lãng phí
   → Tối ưu ngân sách
   → Tăng tỷ lệ tiết kiệm

**3️⃣ ĐẦU TƯ NHỎ, LỢI NHUẬN LỚN**
💰 ~2,750 VNĐ/ngày
   → Giá 1 ly cà phê
   → Nhưng giá trị gấp 5-10 lần
   → ROI trung bình +200%

**4️⃣ KHÔNG QUẢNG CÁO**
✨ Trải nghiệm premium thực sự
   → Tập trung 100%
   → Không gián đoạn
   → Không làm phiền

━━━━━━━━━━━━━━━━━━━━━
🎯 **ĐỂ ĐẠT ROI +200%:**
━━━━━━━━━━━━━━━━━━━━━

✅ Chat với AI mỗi ngày (10+ tin)
✅ Check dashboard 2-3 lần/tuần
✅ Đọc gợi ý mỗi sáng
✅ Dùng phân tích khi cần

→ Thời gian tiết kiệm: ~8-10 giờ/tháng
→ Giá trị: ~800K - 1M VNĐ
→ Chi phí: ~83K VNĐ/tháng
→ **Lời: ~700K - 900K VNĐ!**

━━━━━━━━━━━━━━━━━━━━━
💡 **KẾT LUẬN:**
━━━━━━━━━━━━━━━━━━━━━

Premium không phải chi phí,
mà là **đầu tư sinh lời**! 🚀
"""
    
    keyboard = [
        [InlineKeyboardButton("💎 Nâng cấp ngay", callback_data="upgrade_to_premium")],
        [InlineKeyboardButton("📊 Xem ROI của tôi", callback_data="view_roi_detail")],
        [InlineKeyboardButton("🏠 Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ============================================================================
# DAY 2: ROI & UPSELL HANDLERS
# ============================================================================

async def handle_upgrade_to_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upgrade to premium callback - Show payment options with QR code"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = query.from_user.id
        
        # Track analytics
        Analytics.track_event(user_id, 'upgrade_from_status_clicked')
        
        # Get payment info with QR code
        from bot.services.payment_service import PaymentService
        payment_info = PaymentService.get_payment_instructions(user_id, "PREMIUM")
        
        # Format payment message
        message = PaymentService.format_payment_message(payment_info)
        
        keyboard = [
            [InlineKeyboardButton("✅ Đã thanh toán", callback_data="confirm_payment")],
            [InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")],
            [InlineKeyboardButton("📊 Xem ROI chi tiết", callback_data="view_roi_detail")],
            [InlineKeyboardButton("🤔 Tại sao nên Premium?", callback_data="why_premium")],
            [InlineKeyboardButton("« Quay lại", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send QR code image
        try:
            await query.message.reply_photo(
                photo=payment_info['qr_url'],
                caption=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            # Delete the previous message to keep chat clean
            await query.message.delete()
        except Exception as e:
            logger.error(f"Error sending QR code: {e}")
            # Fallback to text only
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in handle_upgrade_to_premium: {e}", exc_info=True)
        await query.edit_message_text(
            "😓 Xin lỗi, có lỗi khi tải thông tin thanh toán. Vui lòng thử lại sau!\n\n"
            "Hoặc liên hệ Admin để được hỗ trợ: /support",
            parse_mode="Markdown"
        )


async def handle_confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment confirmation - Create verification request"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'payment_confirmation_clicked')
    
    # Store user ID in context for next step
    context.user_data['awaiting_payment_proof'] = True
    context.user_data['payment_amount'] = 999000  # Premium price
    
    message = """
✅ **XÁC NHẬN THANH TOÁN**

Cảm ơn bạn đã thanh toán! Để xác nhận nhanh chóng, vui lòng:

**📸 Gửi ảnh chụp màn hình:**
• Thông báo chuyển khoản thành công
• Hoặc lịch sử giao dịch trong app ngân hàng

**✍️ Hoặc gửi thông tin:**
• Số tiền đã chuyển
• Thời gian chuyển khoản
• 4 số cuối STK của bạn (nếu có)

━━━━━━━━━━━━━━━━━━━━━
⏱️ **THỜI GIAN XỬ LÝ:**
━━━━━━━━━━━━━━━━━━━━━

• Tự động: 5-10 phút
• Thủ công: 15-30 phút (giờ hành chính)
• Ngoài giờ: Trong 2 giờ

━━━━━━━━━━━━━━━━━━━━━
💡 **LƯU Ý:**
━━━━━━━━━━━━━━━━━━━━━

✅ Đã chuyển đúng nội dung? → Tự động kích hoạt
⚠️ Chuyển sai nội dung? → Cần xác nhận thủ công

📞 **Cần hỗ trợ?** Nhấn "Liên hệ Admin" bên dưới
"""
    
    keyboard = [
        [InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")],
        [InlineKeyboardButton("« Quay lại", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Delete the QR code message and send new text message
    try:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in handle_confirm_payment: {e}")
        # Fallback: try to edit if message is text
        try:
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except:
            # Last resort: send new message without deleting
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )


async def handle_view_roi_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view ROI detail callback - Show detailed ROI breakdown"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'roi_detail_viewed')
    
    # Get ROI calculation
    from bot.services.roi_calculator import ROICalculator
    from bot.utils.database import get_user_by_id
    from bot.core.subscription import SubscriptionManager, SubscriptionTier
    
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user) if user else SubscriptionTier.FREE
    roi = ROICalculator.calculate_monthly_roi(user_id)
    
    tier_name = tier.value if tier else "FREE"
    
    message = f"""
📊 **ROI DASHBOARD CHI TIẾT**

━━━━━━━━━━━━━━━━━━━━━
📈 **PHÂ N TÍCH SỬ DỤNG:**
━━━━━━━━━━━━━━━━━━━━━

💬 **{roi['messages']} tin nhắn** với AI
   → Tiết kiệm: {roi['messages'] * 3} phút
   
📊 **{roi['analyses']} phân tích** tài chính
   → Tiết kiệm: {roi['analyses'] * 30} phút
   
💡 **{roi['recommendations']} gợi ý** cá nhân
   → Tiết kiệm: {roi['recommendations'] * 15} phút
   
📈 **{roi['dashboard_views']} lần** xem dashboard
   → Tiết kiệm: {roi['dashboard_views'] * 20} phút

━━━━━━━━━━━━━━━━━━━━━
⏱️ **TỔNG THỜI GIAN:**
━━━━━━━━━━━━━━━━━━━━━

Tiết kiệm: **{roi['time_saved']} giờ**
Giá trị: **{roi['value']:,} VNĐ**
(Tính theo 100K VNĐ/giờ)

━━━━━━━━━━━━━━━━━━━━━
💰 **TÍNH TOÁN ROI:**
━━━━━━━━━━━━━━━━━━━━━

Chi phí {tier_name}: {roi['cost']:,} VNĐ/tháng
Giá trị nhận: {roi['value']:,} VNĐ/tháng

→ **Lời/Lỗ: {roi['profit']:,} VNĐ**
→ **ROI: {roi['roi_percent']:+.0f}%**

━━━━━━━━━━━━━━━━━━━━━
💡 **CÁCH TỐI ƯU:**
━━━━━━━━━━━━━━━━━━━━━

• Sử dụng nhiều hơn = ROI cao hơn
• Mục tiêu: ≥+200% ROI
• Chat với AI mỗi ngày
• Dùng tính năng Phân tích thường xuyên
"""
    
    if tier == SubscriptionTier.FREE:
        message += "\n\n💎 Nâng cấp Premium để unlock ROI cao hơn!"
        keyboard = [
            [InlineKeyboardButton("🎁 Dùng thử 7 ngày FREE", callback_data="start_trial")],
            [InlineKeyboardButton("💎 Xem gói Premium", callback_data="view_premium")],
            [InlineKeyboardButton("« Quay lại", callback_data="start")]
        ]
    elif tier == SubscriptionTier.TRIAL:
        keyboard = [
            [InlineKeyboardButton("💎 Nâng cấp Premium ngay", callback_data="upgrade_to_premium")],
            [InlineKeyboardButton("💡 Tips tối ưu", callback_data="optimization_tips")],
            [InlineKeyboardButton("« Quay lại", callback_data="start")]
        ]
    else:  # PREMIUM
        keyboard = [
            [InlineKeyboardButton("💡 Tips tối ưu ROI", callback_data="optimization_tips")],
            [InlineKeyboardButton("📊 Xem status", callback_data="my_status")],
            [InlineKeyboardButton("« Quay lại", callback_data="start")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_optimization_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle optimization tips callback - Show tips to maximize ROI"""
    query = update.callback_query
    await query.answer()
    
    # Track analytics
    Analytics.track_event(query.from_user.id, 'optimization_tips_viewed')
    
    message = """
💡 **TIPS TỐI ƯU ROI PREMIUM**

━━━━━━━━━━━━━━━━━━━━━
🎯 **MỤC TIÊU: ROI ≥ +200%**
━━━━━━━━━━━━━━━━━━━━━

**1️⃣ SỬ DỤNG AI MỖI NGÀY**

💬 Chat với bot ít nhất 10 tin/ngày
   → Hỏi về financial planning
   → Tư vấn tiết kiệm
   → Phân tích thói quen chi tiêu

**2️⃣ DÙNG TÍNH NĂNG PHÂN TÍCH**

📊 Xem dashboard 2-3 lần/tuần
   → Theo dõi xu hướng chi tiêu
   → Phát hiện điểm bất thường
   → Điều chỉnh kịp thời

**3️⃣ NHẬN GỢI Ý CÁ NHÂN**

💡 Check gợi ý mỗi sáng
   → Lời khuyên tối ưu tài chính
   → Tips tiết kiệm theo ngữ cảnh
   → Nhắc nhở quan trọng

**4️⃣ THIẾT LẬP MỤC TIÊU**

⚙️ Cài đặt mục tiêu tài chính
   → Tiết kiệm tháng
   → Kế hoạch đầu tư
   → Budget cho từng danh mục

**5️⃣ HỎI THÔNG MINH**

🧠 Hỏi những câu hỏi cụ thể:
   • "Phân tích chi tiêu tháng này"
   • "Tôi nên tiết kiệm ở đâu?"
   • "ROI đầu tư này bao nhiêu?"
   • "Cách tối ưu 6 hũ tiền?"

━━━━━━━━━━━━━━━━━━━━━
📈 **KẾT QUẢ KỲ VỌNG:**
━━━━━━━━━━━━━━━━━━━━━

✅ 10+ messages/day = +150% ROI
✅ 20+ messages/day = +300% ROI
✅ Active usage = +500% ROI

→ **Premium trả lời bản thân!** 🚀

━━━━━━━━━━━━━━━━━━━━━
💪 **BẮT ĐẦU NGAY HÔM NAY!**
━━━━━━━━━━━━━━━━━━━━━

Gõ câu hỏi đầu tiên về tài chính của bạn 👇
"""
    
    keyboard = [
        [InlineKeyboardButton("💬 Chat với AI ngay", callback_data="start")],
        [InlineKeyboardButton("📊 Xem ROI hiện tại", callback_data="view_roi_detail")],
        [InlineKeyboardButton("🏠 Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_premium_usage_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Premium features usage guide"""
    query = update.callback_query
    await query.answer()
    
    message = """
📖 **HƯỚNG DẪN SỬ DỤNG PREMIUM**

━━━━━━━━━━━━━━━━━━━━━
✨ **6 TÍNH NĂNG CHÍNH**
━━━━━━━━━━━━━━━━━━━━━

**📝 1. Ghi chi tiêu nhanh**
• Gửi: "50k cafe" → Tự động ghi
• Hỗ trợ nhiều định dạng
• Không cần form phức tạp

**📊 2. Tình hình tài chính**
• Xem dashboard real-time
• Thu chi theo ngày/tuần/tháng
• Biểu đồ trực quan

**🔍 3. Phân tích thông minh**
• AI phân tích thói quen chi tiêu
• Phát hiện chi tiêu bất thường
• Dự báo xu hướng

**💡 4. Gợi ý cá nhân hóa**
• Gợi ý tiết kiệm hàng ngày
• Nhắc nhở khi chưa ghi chép
• Tips tối ưu tài chính

**⚙️ 5. Setup nâng cao**
• Tùy chỉnh 6 hũ tiền theo nhu cầu
• Thiết lập mục tiêu tài chính
• Sync dữ liệu tự động

**🆘 6. Hỗ trợ ưu tiên**
• Response trong 30 phút
• Chat trực tiếp với founder
• Hỗ trợ 1-1 qua call nếu cần

━━━━━━━━━━━━━━━━━━━━━
🎯 **BẮT ĐẦU NGAY:**
━━━━━━━━━━━━━━━━━━━━━

1️⃣ Thử ghi 1 giao dịch: "20k trà sữa"
2️⃣ Xem dashboard: Bấm "📊 Tình hình"
3️⃣ Nhận gợi ý: Bấm "💡 Gợi ý"

━━━━━━━━━━━━━━━━━━━━━
📚 **TÀI LIỆU CHI TIẾT:**
━━━━━━━━━━━━━━━━━━━━━

🌐 Xem full guide tại:
👉 [eliroxbot.notion.site/freedomwallet](https://eliroxbot.notion.site/freedomwallet)

🎊 **Chúc bạn quản lý tài chính hiệu quả!**
"""
    
    keyboard = [
        [InlineKeyboardButton("🌐 Xem guide đầy đủ", url="https://eliroxbot.notion.site/freedomwallet")],
        [InlineKeyboardButton("📱 Cài Web App", callback_data="webapp_setup_guide")],
        [InlineKeyboardButton("🏠 Menu Premium", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup,
        disable_web_page_preview=False
    )


async def handle_free_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free_chat callback - Prompt user to ask a question"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'free_chat_clicked')
    
    message = """
💬 **CHAT VỚI BOT (FREE)**

Hãy gõ câu hỏi của bạn, tôi sẽ trả lời ngay! 😊

📋 **Các chủ đề tôi có thể giúp:**
• Hướng dẫn sử dụng Freedom Wallet
• Cách thêm/xóa/sửa giao dịch
• Giải thích về 6 Hũ Tiền
• Cách setup Google Sheet
• Khắc phục lỗi thường gặp
• Tips quản lý tài chính

💬 **Giới hạn hôm nay:** 5 tin nhắn

Gõ câu hỏi của bạn bên dưới! 👇
"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Quay về Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_upgrade_premium_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upgrade_premium callback from start menu - Show trial offer"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'upgrade_premium_clicked_from_start')
    
    message = """
🎁 **DÙNG THỬ PREMIUM 7 NGÀY MIỄN PHÍ**

━━━━━━━━━━━━━━━━━━━━━
✨ **BẠN SẼ NHẬN ĐƯỢC:**
━━━━━━━━━━━━━━━━━━━━━

💬 **Unlimited Chat với AI**
   → Không giới hạn tin nhắn
   → Trả lời 24/7 trong vài giây

📊 **Phân Tích Tài Chính Thông Minh**
   → AI phân tích chi tiêu của bạn
   → Phát hiện điểm lãng phí
   → Đề xuất tối ưu hóa

💡 **Gợi Ý Cá Nhân Hóa**
   → Mỗi ngày nhận 1 tips mới
   → Dựa trên thói quen chi tiêu
   → Giúp tiết kiệm tối đa

📈 **ROI Dashboard**
   → Xem giá trị Premium mang lại
   → Thống kê thời gian tiết kiệm
   → Tính toán lợi nhuận đầu tư

🚀 **Hỗ Trợ Ưu Tiên**
   → Phản hồi trong 30 phút
   → Hỗ trợ 1-1 qua chat
   → Setup & troubleshooting

━━━━━━━━━━━━━━━━━━━━━
🎯 **SAU 7 NGÀY:**
━━━━━━━━━━━━━━━━━━━━━

Nếu thích → Nâng cấp Premium
Nếu không → Quay về FREE (5 msg/ngày)

**100% không mất phí, không cần thẻ tín dụng!**

Bắt đầu ngay? 👇
"""
    
    keyboard = [
        [InlineKeyboardButton("🎁 Bắt đầu dùng thử NGAY", callback_data="start_trial")],
        [InlineKeyboardButton("💰 Xem gói Premium", callback_data="view_premium")],
        [InlineKeyboardButton("❓ Tại sao nên Premium?", callback_data="why_premium")],
        [InlineKeyboardButton("🏠 Quay về Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
