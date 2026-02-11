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
ðŸ†˜ **LiÃªn Há»‡ Há»— Trá»£**

Báº¡n gáº·p váº¥n Ä‘á» cáº§n há»— trá»£ tá»« team?

ðŸ“ **Vui lÃ²ng mÃ´ táº£ váº¥n Ä‘á» chi tiáº¿t:**
â€¢ Báº¡n Ä‘ang lÃ m gÃ¬?
â€¢ Lá»—i gÃ¬ xáº£y ra?
â€¢ áº¢nh chá»¥p mÃ n hÃ¬nh (náº¿u cÃ³)

ðŸ’¬ **Gá»­i tin nháº¯n tiáº¿p theo Ä‘á»ƒ táº¡o ticket!**

â±ï¸ *Team sáº½ pháº£n há»“i trong 24h lÃ m viá»‡c*
"""
    
    keyboard = [[InlineKeyboardButton("âŒ Há»§y", callback_data="cancel_support")]]
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
âœ… **ÄÃ£ ghi nháº­n yÃªu cáº§u há»— trá»£!**

ðŸŽ« **Ticket ID:** #{ticket_id}
ðŸ“… **Thá»i gian:** {timestamp}

ðŸ“§ **Ná»™i dung:**
"{message[:200]}{'...' if len(message) > 200 else ''}"

â±ï¸ *Team sáº½ xem xÃ©t vÃ  pháº£n há»“i trong 24h lÃ m viá»‡c.*

ðŸ’¬ Báº¡n cÃ³ thá»ƒ tiáº¿p tá»¥c há»i bot hoáº·c chá» pháº£n há»“i qua Telegram!

ðŸ™ Cáº£m Æ¡n báº¡n Ä‘Ã£ sá»­ dá»¥ng Freedom Wallet!
"""
            
        else:
            # Fallback if Sheets not configured
            logger.warning("Google Sheets not configured, ticket saved to logs only")
            success_text = f"""
âœ… **ÄÃ£ ghi nháº­n yÃªu cáº§u!**

ðŸŽ« **Ticket ID:** #{ticket_id}

âš ï¸ *Há»‡ thá»‘ng support táº¡m thá»i báº£o trÃ¬. Team sáº½ liÃªn há»‡ báº¡n sá»›m nháº¥t!*

ðŸ“§ Email: support@freedomwallet.com
ðŸ’¬ Telegram: @FreedomWalletSupport
"""
        
        keyboard = [[InlineKeyboardButton("ðŸ  Vá» trang chá»§", callback_data="start")]]
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
ðŸ˜“ **Xin lá»—i, cÃ³ lá»—i xáº£y ra khi lÆ°u ticket.**

ðŸ”„ Vui lÃ²ng thá»­ láº¡i sau hoáº·c liÃªn há»‡:
ðŸ“§ Email: support@freedomwallet.com
ðŸ’¬ Telegram: @FreedomWalletSupport

ðŸ™ Xin lá»—i vÃ¬ sá»± báº¥t tiá»‡n!
"""
        
        await update.message.reply_text(error_text, parse_mode="Markdown")
        return ConversationHandler.END


async def cancel_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel support ticket creation"""
    
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "âŒ **ÄÃ£ há»§y táº¡o ticket há»— trá»£.**\n\nðŸ’¬ Báº¡n cÃ³ thá»ƒ tiáº¿p tá»¥c chat vá»›i bot hoáº·c dÃ¹ng /support náº¿u cáº§n!",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END

