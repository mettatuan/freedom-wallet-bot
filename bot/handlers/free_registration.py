"""
FREE Flow Registration - Collect user info before starting setup
Calm, value-first approach
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, ConversationHandler
from loguru import logger
from bot.utils.database import SessionLocal, User, generate_referral_code, run_sync
from bot.utils.sheets_registration import save_user_to_registration_sheet
import re
from datetime import datetime
from pathlib import Path

# Conversation states
AWAITING_EMAIL, AWAITING_PHONE, AWAITING_NAME = range(3)


def _check_registration_complete_sync(user_id: int) -> bool:
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == user_id).first()
        return bool(u and u.email and u.phone and u.full_name)
    finally:
        db.close()


def _save_registration_data_sync(user_id: int, email: str, phone: str, full_name: str):
    """Saves registration data. Returns referral_count int, or None if user not found."""
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == user_id).first()
        if not u:
            return None
        u.email = email
        u.phone = phone
        u.full_name = full_name
        u.is_registered = True
        u.registration_date = datetime.now()
        u.source = 'BOT_FREE_FLOW'
        db.commit()
        return u.referral_count or 0
    finally:
        db.close()


async def free_step1_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 1 - Show intro + collect info"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Check if user already has full info
    already_registered = await run_sync(_check_registration_complete_sync, user.id)
    if already_registered:
        # Already have info, skip to step 2
        logger.info(f"User {user.id} already has registration info, skipping to step 2")
        await query.edit_message_text("Đang tải...")
        
        # Import here to avoid circular dependency
        from bot.handlers.free_flow import free_step2_show_value
        update.callback_query = query
        await free_step2_show_value(update, context)
        return ConversationHandler.END
    
    # Send intro message with image
    message = """
Chào bạn,

Freedom Wallet không phải một app để bạn tải về.
Đây là một hệ thống bạn tự sở hữu.

Mỗi người dùng có:
• Google Sheet riêng
• Apps Script riêng
• Web App riêng

Dữ liệu nằm trên Drive của bạn.
Không phụ thuộc vào ai.

Để bắt đầu, tôi cần vài thông tin cơ bản.
"""
    
    # Send photo first, then ask for info
    image_path = Path("media/images/web_apps.jpg")
    
    try:
        await query.message.reply_photo(
            photo=open(image_path, 'rb'),
            caption=message,
            parse_mode="Markdown"
        )
        
        await query.message.reply_text(
            "📧 **Bước 1/3**: Nhập email của bạn\n"
            "(Để gửi hướng dẫn và template)",
            parse_mode="Markdown"
        )
        
        # Delete original message
        await query.message.delete()
        
        return AWAITING_EMAIL
        
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        await query.edit_message_text(
            message + "\n\n📧 **Bước 1/3**: Nhập email của bạn\n"
            "(Để gửi hướng dẫn và template)",
            parse_mode="Markdown"
        )
        return AWAITING_EMAIL


async def receive_free_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate email"""
    email = update.message.text.strip()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await update.message.reply_text(
            "❌ Email không hợp lệ.\n\n"
            "Vui lòng nhập lại (ví dụ: name@gmail.com):"
        )
        return AWAITING_EMAIL
    
    # Save to context
    context.user_data['registration_email'] = email
    
    await update.message.reply_text(
        f"✅ Email: {email}\n\n"
        f"📱 **Bước 2/3**: Nhập số điện thoại\n"
        f"(Để hỗ trợ qua Zalo/WhatsApp nếu cần)\n\n"
        f"Hoặc gõ /skip nếu muốn bỏ qua.",
        parse_mode="Markdown"
    )
    
    return AWAITING_PHONE


async def receive_free_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive phone number"""
    phone = update.message.text.strip()
    
    # Allow skip
    if phone.lower() == '/skip':
        context.user_data['registration_phone'] = None
        phone_display = "Bỏ qua"
    else:
        # Basic phone validation
        phone = re.sub(r'[^0-9+]', '', phone)
        if len(phone) < 10:
            await update.message.reply_text(
                "❌ Số điện thoại không hợp lệ.\n\n"
                "Vui lòng nhập lại (VD: 0901234567)\n"
                "Hoặc gõ /skip để bỏ qua:"
            )
            return AWAITING_PHONE
        
        context.user_data['registration_phone'] = phone
        phone_display = phone
    
    await update.message.reply_text(
        f"✅ Số điện thoại: {phone_display}\n\n"
        f"👤 **Bước 3/3**: Nhập họ tên của bạn\n"
        f"(Để cá nhân hóa hướng dẫn)\n\n"
        f"Hoặc gõ /skip để bỏ qua.",
        parse_mode="Markdown"
    )
    
    return AWAITING_NAME


async def receive_free_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive full name and save to database + Google Sheet"""
    name = update.message.text.strip()
    user = update.effective_user
    
    # Allow skip
    if name.lower() == '/skip':
        full_name = user.first_name
    else:
        full_name = name
    
    context.user_data['registration_name'] = full_name
    
    # Get collected data
    email = context.user_data.get('registration_email')
    phone = context.user_data.get('registration_phone')
    
    # Save to database
    referral_count = await run_sync(_save_registration_data_sync, user.id, email, phone, full_name)
    
    if referral_count is not None:
        # Generate referral code
        referral_code = generate_referral_code(user.id)
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
        
        # Save to Google Sheet
        try:
            await save_user_to_registration_sheet(
                user_id=user.id,
                username=user.username,
                full_name=full_name,
                email=email,
                phone=phone,
                plan="FREE",
                referral_link=referral_link,
                referral_count=referral_count,
                source="BOT_FREE_FLOW",
                status="ACTIVE",
                referred_by=None
            )
            logger.info(f"✅ Saved user {user.id} to Google Sheet")
        except Exception as e:
            logger.error(f"❌ Failed to save to Google Sheet: {e}")
        
        await update.message.reply_text(
            f"✅ Cảm ơn {full_name}!\n\n"
            f"Thông tin đã được lưu lại.\n"
            f"Bây giờ, hãy cùng tạo hệ thống của riêng bạn.",
            parse_mode="Markdown"
        )
        
        # Wait a moment then go to step 2
        import asyncio
        await asyncio.sleep(1)
        
        # Proceed to step 2
        from bot.handlers.free_flow import free_step2_show_value
        
        # Create a fake callback query for step 2
        from telegram import CallbackQuery
        fake_query = type('obj', (object,), {
            'answer': lambda: None,
            'edit_message_text': update.message.reply_text,
            'message': update.message,
            'from_user': user
        })()
        
        # Call step 2 directly
        message = """
Trước khi làm bất cứ bước kỹ thuật nào,
bạn cần biết mình sẽ nhận được điều gì.

Khi hệ thống hoàn tất, bạn sẽ thấy:

• Tổng tài sản hiện có
• Dòng tiền thu – chi theo tháng
• 6 Hũ tiền phân bổ tự động
• Cấp độ tài chính hiện tại của bạn
• Tình trạng đầu tư, nợ và tài sản

Không phải để xem cho vui.
Mà để bạn biết rõ tiền của mình đang ở đâu.

Bạn sẵn sàng tạo hệ thống của riêng mình chưa?
"""
        
        keyboard = [
            [InlineKeyboardButton("Tạo hệ thống", callback_data="free_step3_copy_template")],
            [InlineKeyboardButton("Hỏi thêm", callback_data="learn_more")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=message,
            reply_markup=reply_markup
        )
        
        return ConversationHandler.END


async def cancel_free_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel registration"""
    await update.message.reply_text(
        "Đã hủy đăng ký.\n"
        "Bạn có thể bắt đầu lại bất cứ lúc nào bằng /start"
    )
    return ConversationHandler.END
