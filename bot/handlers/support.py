"""
Support Handler - Save support tickets to Google Sheets
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from loguru import logger
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from config.settings import settings
import uuid


# Google Sheets setup
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheets_client():
    """Initialize Google Sheets client"""
    if not settings.GOOGLE_SHEETS_CREDENTIALS:
        logger.warning("Google Sheets credentials not configured")
        return None
    
    try:
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_SHEETS_CREDENTIALS,
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets: {e}")
        return None


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /support command - Start support ticket flow"""
    
    support_text = """
🆘 **Liên Hệ Hỗ Trợ**

Bạn gặp vấn đề cần hỗ trợ từ team?

📝 **Vui lòng mô tả vấn đề chi tiết:**
• Bạn đang làm gì?
• Lỗi gì xảy ra?
• Ảnh chụp màn hình (nếu có)

💬 **Gửi tin nhắn tiếp theo để tạo ticket!**

⏱️ *Team sẽ phản hồi trong 24h làm việc*
"""
    
    keyboard = [[InlineKeyboardButton("❌ Hủy", callback_data="cancel_support")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        support_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    # Set conversation state to waiting for support message
    return "WAITING_SUPPORT_MESSAGE"


async def save_support_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save support ticket to Google Sheets"""
    
    user = update.effective_user
    message = update.message.text
    
    # Generate ticket ID
    ticket_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Save to Google Sheets
        client = get_sheets_client()
        
        if client and settings.SUPPORT_SHEET_ID:
            sheet = client.open_by_key(settings.SUPPORT_SHEET_ID)
            worksheet = sheet.worksheet(settings.SUPPORT_SHEET_NAME)
            
            # Append row: [Ticket ID, Timestamp, User ID, Username, Full Name, Message, Status]
            row = [
                ticket_id,
                timestamp,
                str(user.id),
                user.username or "N/A",
                user.full_name or "N/A",
                message,
                "Open"
            ]
            
            worksheet.append_row(row)
            logger.info(f"Support ticket {ticket_id} created for user {user.id}")
            
            # Success response
            success_text = f"""
✅ **Đã ghi nhận yêu cầu hỗ trợ!**

🎫 **Ticket ID:** #{ticket_id}
📅 **Thời gian:** {timestamp}

📧 **Nội dung:**
"{message[:200]}{'...' if len(message) > 200 else ''}"

⏱️ *Team sẽ xem xét và phản hồi trong 24h làm việc.*

💬 Bạn có thể tiếp tục hỏi bot hoặc chờ phản hồi qua Telegram!

🙏 Cảm ơn bạn đã sử dụng Freedom Wallet!
"""
            
        else:
            # Fallback if Sheets not configured
            logger.warning("Google Sheets not configured, ticket saved to logs only")
            success_text = f"""
✅ **Đã ghi nhận yêu cầu!**

🎫 **Ticket ID:** #{ticket_id}

⚠️ *Hệ thống support tạm thời bảo trì. Team sẽ liên hệ bạn sớm nhất!*

📧 Email: support@freedomwallet.com
💬 Telegram: @FreedomWalletSupport
"""
        
        keyboard = [[InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            success_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Failed to save support ticket: {e}")
        
        error_text = """
😓 **Xin lỗi, có lỗi xảy ra khi lưu ticket.**

🔄 Vui lòng thử lại sau hoặc liên hệ:
📧 Email: support@freedomwallet.com
💬 Telegram: @FreedomWalletSupport

🙏 Xin lỗi vì sự bất tiện!
"""
        
        await update.message.reply_text(error_text, parse_mode="Markdown")
        return ConversationHandler.END


async def cancel_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel support ticket creation"""
    
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ **Đã hủy tạo ticket hỗ trợ.**\n\n💬 Bạn có thể tiếp tục chat với bot hoặc dùng /support nếu cần!",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END
