"""Sheet setup handler using Clean Architecture."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from loguru import logger
import re

from ...infrastructure.di_container import get_container
from ...application.dtos import SetupSheetInput


# Conversation states
AWAITING_EMAIL, AWAITING_PHONE, AWAITING_SHEET_URL, AWAITING_WEBAPP_URL = range(4)


async def start_sheet_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start sheet setup conversation."""
    user = update.effective_user
    logger.info(f"User {user.id} started sheet setup (Clean Architecture)")
    
    # Handle both callback query and command
    is_callback = bool(update.callback_query)
    
    message_text = (
        f"{user.first_name} ơi\n\n"
        "Bạn đang chuẩn bị tạo hệ thống Freedom Wallet của riêng mình.\n\n"
        "Để mình gửi hướng dẫn cài đặt\n"
        "và thông tin cấu hình cần thiết,\n"
        "vui lòng cho mình email của bạn.\n\n"
        "📧 **Email chỉ dùng để:**\n"
        "• Gửi hướng dẫn setup\n"
        "• Hỗ trợ khi bạn cần\n"
        "• Thông báo cập nhật quan trọng\n\n"
        "👉 Bạn có thể gõ email ngay bây giờ."
    )
    
    if is_callback:
        await update.callback_query.answer()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            message_text,
            parse_mode="Markdown"
        )
    
    return AWAITING_EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate email."""
    email = update.message.text.strip()
    
    # Basic email validation (will use Email value object later)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await update.message.reply_text(
            "❌ Email không hợp lệ!\n\n"
            "Vui lòng nhập lại email (ví dụ: name@gmail.com):"
        )
        return AWAITING_EMAIL
    
    context.user_data['email'] = email
    logger.info(f"✅ Email saved: {email}")
    
    await update.message.reply_text(
        f"✅ Email: {email}\n\n"
        f"👉 **Bước 2/4:** Nhập **Số điện thoại** của bạn\n"
        f"(Ví dụ: 0901234567 hoặc +84901234567):"
    )
    
    return AWAITING_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate phone number."""
    phone = update.message.text.strip()
    
    # Basic phone validation (will use Phone value object later)
    phone_pattern = r'^(\+84|0)[0-9]{9,10}$'
    if not re.match(phone_pattern, phone):
        await update.message.reply_text(
            "❌ Số điện thoại không hợp lệ!\n\n"
            "Vui lòng nhập lại (ví dụ: 0901234567):"
        )
        return AWAITING_PHONE
    
    context.user_data['phone'] = phone
    logger.info(f"✅ Phone saved: {phone}")
    
    await update.message.reply_text(
        f"✅ Số điện thoại: {phone}\n\n"
        f"👉 **Bước 3/4:** Nhập **Link Google Sheet** của bạn\n"
        f"(Ví dụ: https://docs.google.com/spreadsheets/d/...):"
    )
    
    return AWAITING_SHEET_URL


async def receive_sheet_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate Google Sheet URL."""
    sheet_url = update.message.text.strip()
    
    # Basic URL validation
    if not sheet_url.startswith("https://docs.google.com/spreadsheets/"):
        await update.message.reply_text(
            "❌ Link Google Sheet không hợp lệ!\n\n"
            "Vui lòng nhập lại link Sheet (phải bắt đầu bằng https://docs.google.com/spreadsheets/):"
        )
        return AWAITING_SHEET_URL
    
    context.user_data['sheet_url'] = sheet_url
    logger.info(f"✅ Sheet URL saved")
    
    await update.message.reply_text(
        f"✅ Google Sheet URL đã lưu\n\n"
        f"👉 **Bước 4/4:** Nhập **WebApp URL**\n"
        f"(Link WebApp để ghi chi tiêu nhanh):"
    )
    
    return AWAITING_WEBAPP_URL


async def receive_webapp_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive WebApp URL and complete setup using SetupSheetUseCase."""
    user = update.effective_user
    webapp_url = update.message.text.strip()
    
    # Basic URL validation
    if not webapp_url.startswith("https://"):
        await update.message.reply_text(
            "❌ WebApp URL không hợp lệ!\n\n"
            "Vui lòng nhập lại (phải bắt đầu bằng https://):"
        )
        return AWAITING_WEBAPP_URL
    
    context.user_data['webapp_url'] = webapp_url
    logger.info(f"✅ WebApp URL saved")
    
    # Get all collected data
    email = context.user_data.get('email')
    phone = context.user_data.get('phone')
    sheet_url = context.user_data.get('sheet_url')
    
    await update.message.reply_text("⏳ Đang setup Sheet và nâng cấp tài khoản...")
    
    try:
        # Get DI container and execute use case
        container = get_container()
        session = container.get_db_session()
        
        try:
            setup_use_case = container.get_setup_sheet_use_case(session)
            
            result = await setup_use_case.execute(SetupSheetInput(
                user_id=user.id,
                email=email,
                phone=phone,
                sheet_url=sheet_url,
                webapp_url=webapp_url
            ))
            
            if result.is_failure():
                logger.error(f"Setup sheet failed for user {user.id}: {result.error_message}")
                await update.message.reply_text(
                    f"❌ Setup thất bại: {result.error_message}\n\n"
                    f"Vui lòng thử lại bằng /setup"
                )
                return ConversationHandler.END
            
            # Success!
            user_dto = result.data.user
            subscription_dto = result.data.subscription
            
            logger.info(f"✅ User {user.id} upgraded to {subscription_dto.tier}")
            
            success_message = (
                "🎉 **SETUP THÀNH CÔNG!**\n\n"
                f"✅ Tài khoản: **{subscription_dto.tier}**\n"
                f"✅ Google Sheet đã kết nối\n"
                f"✅ Thời hạn: 30 ngày\n\n"
                f"⚡ **Bây giờ bạn có thể:**\n"
                f"• Ghi chi tiêu nhanh: `chi 50k ăn sáng`\n"
                f"• Ghi thu nhập: `thu 5000000 lương tháng 1`\n"
                f"• Xem số dư: /balance\n\n"
                f"Thử ghi khoản đầu tiên ngay nhé! 🚀"
            )
            
            keyboard = [
                [InlineKeyboardButton("💰 Xem số dư", callback_data="balance")],
                [InlineKeyboardButton("📊 Giao dịch gần đây", callback_data="recent")],
                [InlineKeyboardButton("❓ Hướng dẫn", callback_data="help")],
            ]
            
            await update.message.reply_text(
                success_message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            
            # Clear conversation data
            context.user_data.clear()
            
            return ConversationHandler.END
            
        finally:
            session.close()
    
    except Exception as e:
        logger.exception(f"Error in sheet setup for user {user.id}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra trong quá trình setup.\n"
            "Vui lòng thử lại sau."
        )
        return ConversationHandler.END


async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel sheet setup conversation."""
    await update.message.reply_text(
        "❌ Đã hủy setup Sheet.\n\n"
        "Bạn có thể bắt đầu lại bằng /setup"
    )
    
    context.user_data.clear()
    return ConversationHandler.END
