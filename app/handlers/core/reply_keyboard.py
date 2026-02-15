"""
Reply Keyboard Handler for FreedomWallet Bot
Persistent main menu keyboard for easy user access
"""
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, MessageHandler, filters, Application, ApplicationHandlerStop
from loguru import logger


def get_main_reply_keyboard():
    """
    Create persistent Reply Keyboard with 6 main buttons
    Layout: 2-2-2 pattern for balanced design
    """
    keyboard = [
        # Row 1: Core actions
        [KeyboardButton("📝 Ghi nhanh"), KeyboardButton("📊 Báo cáo")],
        # Row 2: Access & Help
        [KeyboardButton("Web Apps"), KeyboardButton("Hướng dẫn")],
        # Row 3: Community & Settings
        [KeyboardButton("Đóng góp"), KeyboardButton("Cài đặt")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,      # Auto-size buttons for optimal display
        one_time_keyboard=False,   # Keyboard stays visible (persistent)
        input_field_placeholder="Chọn chức năng hoặc gõ giao dịch..."
    )


async def handle_reply_keyboard_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Central router for Reply Keyboard button presses
    Maps button text to corresponding callback handlers
    """
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    logger.info(f"Reply keyboard button pressed: '{text}' by user {user_id}")
    
    # Import handlers dynamically to avoid circular imports
    from app.handlers.core.main_menu import (
        show_quick_record_menu,
        show_quick_report_menu, 
        show_help_menu,
        show_settings_menu
    )
    from app.utils.database import SessionLocal, User
    
    # Button 1: 📝 Ghi nhanh
    if text == "📝 Ghi nhanh":
        # Create fake callback query for menu handlers
        from telegram import CallbackQuery
        from unittest.mock import MagicMock
        
        # Mock callback query
        query = MagicMock(spec=CallbackQuery)
        query.answer = lambda: None
        query.message = update.message
        
        # Call quick record menu handler
        keyboard = [
            [{"text": "💸 Ghi chi tiêu", "callback_data": "qr_start_chi"}],
            [{"text": "💰 Ghi thu nhập", "callback_data": "qr_start_thu"}],
            [{"text": "📊 Xem giao dịch hôm nay", "callback_data": "show_today_transactions"}]
        ]
        
        message = """
📝 **GHI NHANH THU CHI**

Cách nhanh nhất để ghi giao dịch:

━━━━━━━━━━━━━━━━━━━━━

**💬 Gửi tin nhắn trực tiếp**

Ví dụ:
• `Cà phê 35k`
• `Ăn trưa 50k`
• `Lương 15tr`
• `Mua sách 150k`

→ Bot tự động lưu vào Sheet! ✨

━━━━━━━━━━━━━━━━━━━━━

💡 **Tip:** Ghi trong 5 giây, không cần mở app!
"""
        
        await update.message.reply_text(
            text=message,
            parse_mode="Markdown",
            reply_markup=get_main_reply_keyboard()  # Keep keyboard visible
        )
        raise ApplicationHandlerStop()
    
    # Button 2: 📊 Báo cáo
    elif text == "📊 Báo cáo":
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.spreadsheet_id:
                await update.message.reply_text(
                    "❌ Bạn chưa kết nối Sheet!\n\n"
                    "Vui lòng kết nối trước: /connectsheets",
                    parse_mode="Markdown",
                    reply_markup=get_main_reply_keyboard()
                )
                raise ApplicationHandlerStop()
            
            message = """
📊 **BÁO CÁO NHANH**

Xem tổng quan tài chính của bạn:

━━━━━━━━━━━━━━━━━━━━━

**💰 Tài khoản** - Số dư hiện tại
**🏺 Hũ tiền** - Tình trạng các hũ
**📊 Thu chi** - Tháng này
**🌐 Web App** - Xem chi tiết

━━━━━━━━━━━━━━━━━━━━━

💡 **Tip:** Dùng Web App để xem báo cáo sâu hơn!
"""
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("💼 Tài khoản", callback_data="show_accounts_report")],
                [InlineKeyboardButton("🏺 Hũ tiền", callback_data="show_jars_report")],
                [InlineKeyboardButton("📊 Thu chi (tháng này)", callback_data="show_monthly_income_expense")],
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user.web_app_url else "https://script.google.com")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        finally:
            db.close()
        raise ApplicationHandlerStop()
    
    # Button 3: Web Apps - Open directly if URL exists
    elif text == "Web Apps":
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                await update.message.reply_text(
                    "❌ User not found. Please /start first.",
                    reply_markup=get_main_reply_keyboard()
                )
            elif user.web_app_url:
                # Open directly with single button
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = [
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url)],
                    [InlineKeyboardButton("✏️ Cập nhật link", callback_data="update_webapp_url")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"🌐 **Truy cập Freedom Wallet Web App**\n\n"
                    f"📱 Nhấn nút bên dưới để mở!\n\n"
                    f"💡 Lưu link vào bookmark để truy cập nhanh hơn.",
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            else:
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = [[InlineKeyboardButton("💾 Lưu link Web App", callback_data="save_webapp_url")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"📱 **Lưu link Web App**\n\n"
                    f"Bạn chưa lưu link Web App của Freedom Wallet.\n\n"
                    f"💡 Lưu link để:\n"
                    f"• Truy cập nhanh khi cần ghi chép\n"
                    f"• Không phải tìm lại link mỗi lần\n"
                    f"• Bot sẽ gửi link cho bạn khi cần\n\n"
                    f"Nhấn nút bên dưới để lưu!",
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
        finally:
            db.close()
        raise ApplicationHandlerStop()
    
    # Button 4: Hướng dẫn
    elif text == "Hướng dẫn":
        message = """
📖 **HƯỚNG DẪN SỬ DỤNG**

Chào mừng đến Freedom Wallet Bot! 🎉

━━━━━━━━━━━━━━━━━━━━━

**🚀 Bắt đầu nhanh:**

1️⃣ **Kết nối Sheet**
   `/connectsheets` - Kết nối Google Sheet của bạn

2️⃣ **Ghi nhanh giao dịch**
   Gửi tin nhắn: `Cà phê 35k`, `Lương 15tr`
   
3️⃣ **Xem báo cáo**
   Dùng nút "📊 Báo cáo" để xem tổng quan

━━━━━━━━━━━━━━━━━━━━━

**💡 Các lệnh hữu ích:**

• `/balance` - Xem số dư
• `/spending` - Chi tiêu tháng này
• `/income` - Thu nhập tháng này
• `/recent` - Giao dịch gần đây
• `/mywebapp` - Quản lý link Web App
• `/mystatus` - Trạng thái tài khoản
• `/help` - Trợ giúp chi tiết

━━━━━━━━━━━━━━━━━━━━━

**📝 Cú pháp ghi nhanh:**

✅ Đúng:
• `Cà phê 35k`
• `Ăn trưa 50000`
• `Lương tháng 15tr`
• `Mua sách 150k sách kỹ năng`

❌ Sai:
• `35k cà phê` (số phải sau chữ)
• `cafe` (không có số tiền)

━━━━━━━━━━━━━━━━━━━━━

📱 **Cần hỗ trợ?** 
Dùng `/support` để liên hệ admin!
"""
        
        await update.message.reply_text(
            text=message,
            parse_mode="Markdown",
            reply_markup=get_main_reply_keyboard()
        )
        raise ApplicationHandlerStop()
    
    # Button 5: Đóng góp (4 options)
    elif text == "Đóng góp":
        message = """
💝 **ĐÓNG GÓP CHO FREEDOM WALLET**

Trân trọng biết ơn bạn đã quan tâm đến sự phát triển của Freedom Wallet! 🙏

━━━━━━━━━━━━━━━━━━━━━

**🎯 Chọn cách đóng góp:**

**1️⃣ Đóng góp ý tưởng**
   Gửi ý tưởng tính năng mới, cải tiến UX

**2️⃣ Báo lỗi**
   Phát hiện bug? Báo ngay để được fix!

**3️⃣ Đóng góp tài chính**
   Hỗ trợ chi phí phát triển & duy trì

**4️⃣ Giới thiệu bạn bè**
   Chia sẻ Freedom Wallet với người thân

━━━━━━━━━━━━━━━━━━━━━

**🌟 Roadmap 2026:**

• 🤖 AI phân tích chi tiêu thông minh
• 📊 Báo cáo đa chiều nâng cao  
• 🔔 Nhắc nhở thông minh theo ngữ cảnh
• 💎 Tính năng Premium mới
• 🌐 Web App tích hợp sâu hơn

💡 **Ý tưởng của bạn có thể trở thành tính năng tiếp theo!**
"""
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("💡 Đóng góp ý tưởng", callback_data="contribute_idea")],
            [InlineKeyboardButton("🐛 Báo lỗi", callback_data="report_bug")],
            [InlineKeyboardButton("💰 Đóng góp tài chính", callback_data="financial_support")],
            [InlineKeyboardButton("🎁 Giới thiệu bạn bè", callback_data="show_referral")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        # IMPORTANT: Stop handler propagation to prevent message handler from triggering
        raise ApplicationHandlerStop()
    
    # Button 6: Cài đặt
    elif text == "Cài đặt":
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                await update.message.reply_text(
                    "❌ User not found. Please /start first.",
                    reply_markup=get_main_reply_keyboard()
                )
            else:
                # Check connection status
                has_sheet = bool(user.spreadsheet_id)
                has_webapp = bool(user.web_app_url)
                has_reminder = bool(user.reminder_time)
                
                status_sheet = "✅" if has_sheet else "❌"
                status_webapp = "✅" if has_webapp else "❌"
                status_reminder = "✅" if has_reminder else "❌"
                
                message = f"""
⚙️ **CÀI ĐẶT HỆ THỐNG**

**📊 Trạng thái kết nối:**

{status_sheet} Google Sheet
{status_webapp} Web App URL
{status_reminder} Nhắc nhở hàng ngày

━━━━━━━━━━━━━━━━━━━━━

**🔧 Cài đặt nhanh:**

• `/connectsheets` - Kết nối Sheet
• `/mywebapp` - Quản lý Web App URL
• `/reminder` - Cài đặt nhắc nhở
• `/mystatus` - Xem trạng thái chi tiết

━━━━━━━━━━━━━━━━━━━━━

**💡 Tip:** Kết nối đầy đủ để trải nghiệm tốt nhất!
"""
                
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = []
                
                if not has_sheet:
                    keyboard.append([InlineKeyboardButton("📊 Kết nối Sheet", callback_data="start_sheets_setup")])
                
                if not has_webapp:
                    keyboard.append([InlineKeyboardButton("🌐 Lưu Web App URL", callback_data="save_webapp_url")])
                
                keyboard.append([InlineKeyboardButton("🔔 Cài đặt nhắc nhở", callback_data="setup_reminders")])
                keyboard.append([InlineKeyboardButton("📌 Xem hướng dẫn", callback_data="show_setup_guide")])
                
                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                
                await update.message.reply_text(
                    text=message,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
        finally:
            db.close()
        raise ApplicationHandlerStop()


def register_reply_keyboard_handlers(application: Application):
    """
    Register Reply Keyboard handlers to application
    Must be registered BEFORE general message handler to capture button presses
    Priority: HIGH (order matters!)
    """
    
    # Define exact button texts to match
    button_texts = [
        "📝 Ghi nhanh",
        "📊 Báo cáo", 
        "Web Apps",
        "Hướng dẫn",
        "Đóng góp",
        "Cài đặt"
    ]
    
    # Create filter for exact button text matching
    reply_keyboard_filter = filters.TEXT & filters.Regex(
        f"^({'|'.join([text.replace('(', '\\(').replace(')', '\\)') for text in button_texts])})$"
    )
    
    # Register handler with high priority (group 0, runs before general message handler)
    application.add_handler(
        MessageHandler(
            reply_keyboard_filter,
            handle_reply_keyboard_button
        ),
        group=0  # High priority - runs first
    )
    
    logger.info("✅ Reply Keyboard handlers registered (6 buttons)")
