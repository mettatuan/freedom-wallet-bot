"""Callback handlers for Clean Architecture start flow."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger


async def ca_start_free_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle 'Đăng ký ngay' button from CA start handler.
    
    This starts the FREE registration flow.
    """
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    logger.info(f"User {user.id} clicked 'Đăng ký ngay' (CA flow)")
    
    # Import CA sheet setup constants and function
    from src.presentation.handlers.sheets_handler import start_sheet_setup, AWAITING_EMAIL
    
    # Trigger the existing CA sheet setup flow
    # This properly starts the ConversationHandler
    await query.answer()
    return await start_sheet_setup(update, context)


async def ca_learn_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle 'Tìm hiểu thêm' button from CA start handler.
    
    Shows detailed information about Freedom Wallet.
    """
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    logger.info(f"User {user.id} clicked 'Tìm hiểu thêm' (CA flow)")
    
    info_text = """📖 **FREEDOM WALLET LÀ GÌ?**

🎯 **3 Thành phần:**
1. **Google Sheet** - Lưu trữ dữ liệu trên Drive của bạn
2. **Apps Script** - Backend xử lý logic
3. **Web App** - Giao diện đẹp để quản lý tài chính

🔐 **Bảo mật:**
• Dữ liệu trên Drive CỦA BẠN (không ở server của ai)
• Bạn có toàn quyền kiểm soát
• Không phụ thuộc vào dịch vụ bên ngoài

⚡ **Tính năng:**
• Ghi chi tiêu siêu nhanh qua bot
• Phân loại tự động theo 6 Jars
• Báo cáo chi tiết, biểu đồ trực quan
• Nhắc nhở thông minh

💎 **Các gói:**
• **FREE** - Xem hướng dẫn + Setup tự động
• **UNLOCK** - Ghi chi tiêu qua bot (99k/tháng)
• **PREMIUM** - Full tính năng + AI (199k/tháng)"""
    
    keyboard = [
        [InlineKeyboardButton("📝 Đăng ký ngay", callback_data="start_free_registration")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_caption(
        caption=info_text,
        reply_markup=reply_markup
    )


async def ca_back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Quay lại' button - return to start message."""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    # Resend start message
    from pathlib import Path
    
    welcome_text = f"""Chào {user.first_name},

Freedom Wallet không phải một app để bạn tải về.
Đây là một hệ thống bạn tự sở hữu.

Mỗi người dùng có:
• Google Sheet riêng
• Apps Script riêng
• Web App riêng

Dữ liệu nằm trên Drive của bạn.
Không phụ thuộc vào ai.

Nếu bạn muốn đăng ký sở hữu hệ thống web app này,
mình sẽ hướng dẫn từng bước, rất rõ ràng."""
    
    keyboard = [
        [InlineKeyboardButton("📝 Đăng ký ngay", callback_data="start_free_registration")],
        [InlineKeyboardButton("📖 Tìm hiểu thêm", callback_data="learn_more")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Try to edit with image
    image_path = Path("media/images/web_apps.jpg")
    try:
        # If current message has photo, edit caption
        if query.message.photo:
            await query.edit_message_caption(
                caption=welcome_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            # If text message, need to delete and resend
            await query.message.delete()
            if image_path.exists():
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=open(image_path, 'rb'),
                    caption=welcome_text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=welcome_text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
    except Exception as e:
        logger.error(f"Error in back_to_start: {e}")
        # Fallback: send new message
        await query.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def ca_cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel registration button."""
    query = update.callback_query
    await query.answer("❌ Đã hủy đăng ký")
    
    # Clear state
    context.user_data.pop('ca_registration_state', None)
    
    # Back to start
    await ca_back_to_start(update, context)
