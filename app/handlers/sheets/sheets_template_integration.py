"""
Freedom Wallet Template Integration Handlers (Option 3)
User flow: Táº¡o má»›i hoáº·c ÄÃ£ cÃ³ Sheets â†’ Nháº­p ID â†’ Káº¿t ná»‘i â†’ Sá»­ dá»¥ng
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from app.utils.database import get_db, User
from app.services.sheets_api_client import (
    TEMPLATE_URL,
    extract_spreadsheet_id,
    test_sheets_connection
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_SHEETS_ID = 1


async def handle_connect_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler cho command /connectsheets
    Cho phÃ©p user káº¿t ná»‘i Google Sheets
    """
    query = update.callback_query
    if query:
        await query.answer()
        message = query.message
    else:
        message = update.message
    
    # Check if already connected
    db = next(get_db())
    user = db.query(User).filter(User.id == update.effective_user.id).first()
    
    if user and user.spreadsheet_id:
        keyboard = [
            [
                InlineKeyboardButton("ðŸ”„ Äá»•i Sheets khÃ¡c", callback_data="sheets_change"),
                InlineKeyboardButton("âœ… Giá»¯ nguyÃªn", callback_data="sheets_keep")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            f"ðŸ“Š Báº¡n Ä‘Ã£ káº¿t ná»‘i Google Sheets rá»“i!\n\n"
            f"ðŸ”— Spreadsheet ID: `{user.spreadsheet_id[:20]}...`\n"
            f"ðŸ“… Káº¿t ná»‘i lÃºc: {user.sheets_connected_at.strftime('%d/%m/%Y %H:%M') if user.sheets_connected_at else 'N/A'}\n\n"
            f"Báº¡n muá»‘n Ä‘á»•i sang Sheets khÃ¡c khÃ´ng?"
        )
        
        await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return ConversationHandler.END
    
    # Show options: Create new or Connect existing
    keyboard = [
        [InlineKeyboardButton("ðŸ†• Táº¡o má»›i tá»« Template", callback_data="sheets_create_new")],
        [InlineKeyboardButton("ðŸ“‚ ÄÃ£ cÃ³ Sheets rá»“i", callback_data="sheets_connect_existing")],
        [InlineKeyboardButton("âŒ Há»§y", callback_data="sheets_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "ðŸ“Š **Káº¾T Ná»I GOOGLE SHEETS**\n\n"
        "Freedom Wallet Bot cáº§n káº¿t ná»‘i vá»›i Google Sheets cá»§a báº¡n Ä‘á»ƒ:\n"
        "â€¢ ðŸ“ Ghi láº¡i giao dá»‹ch nhanh\n"
        "â€¢ ðŸ’° Xem sá»‘ dÆ° cÃ¡c hÅ©\n"
        "â€¢ ðŸ“Š PhÃ¢n tÃ­ch chi tiÃªu\n\n"
        "**Chá»n má»™t trong hai cÃ¡ch:**"
    )
    
    await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return WAITING_FOR_SHEETS_ID


async def handle_sheets_create_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user chá»n táº¡o má»›i tá»« template"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "ðŸ†• **Táº O FREEDOM WALLET Má»šI**\n\n"
        "**BÆ°á»›c 1:** Má»Ÿ link template dÆ°á»›i Ä‘Ã¢y\n"
        "**BÆ°á»›c 2:** Click **\"Táº¡o báº£n sao\"** (Make a copy)\n"
        "**BÆ°á»›c 3:** Copy **link** hoáº·c **Spreadsheet ID**\n"
        "**BÆ°á»›c 4:** Gá»­i cho bot\n\n"
        f"ðŸ”— **Template:** {TEMPLATE_URL}\n\n"
        "ðŸ’¡ *Tip: ID lÃ  Ä‘oáº¡n giá»¯a 2 dáº¥u / trong URL*\n"
        "`https://docs.google.com/spreadsheets/d/`**`ID_á»ž_ÄÃ‚Y`**`/edit`"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return WAITING_FOR_SHEETS_ID


async def handle_sheets_connect_existing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user Ä‘Ã£ cÃ³ Sheets sáºµn"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "ðŸ“‚ **Káº¾T Ná»I SHEETS CÃ“ Sáº´N**\n\n"
        "Gá»­i cho bot **link** hoáº·c **Spreadsheet ID** cá»§a Freedom Wallet Sheets cá»§a báº¡n.\n\n"
        "ðŸ“‹ **VÃ­ dá»¥:**\n"
        "â€¢ Link: `https://docs.google.com/spreadsheets/d/1ABC.../edit`\n"
        "â€¢ Hoáº·c chá»‰ ID: `1ABC...`\n\n"
        "ðŸ’¡ *Bot sáº½ test káº¿t ná»‘i vÃ  xÃ¡c nháº­n cho báº¡n.*"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return WAITING_FOR_SHEETS_ID


async def handle_sheets_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler khi user gá»­i Spreadsheet ID hoáº·c URL
    Test connection vÃ  lÆ°u vÃ o database
    """
    user_input = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Extract spreadsheet ID
    spreadsheet_id = extract_spreadsheet_id(user_input)
    
    if not spreadsheet_id:
        await update.message.reply_text(
            "âŒ KhÃ´ng tÃ¬m tháº¥y Spreadsheet ID há»£p lá»‡.\n\n"
            "Vui lÃ²ng gá»­i:\n"
            "â€¢ Link Ä‘áº§y Ä‘á»§: `https://docs.google.com/spreadsheets/d/ID/edit`\n"
            "â€¢ Hoáº·c chá»‰ ID: `1ABC...`\n\n"
            "Thá»­ láº¡i nhÃ©! ðŸ˜Š",
            parse_mode="Markdown"
        )
        return WAITING_FOR_SHEETS_ID
    
    # Test connection
    await update.message.reply_text("ðŸ”„ Äang test káº¿t ná»‘i...\nâ³ Vui lÃ²ng Ä‘á»£i...")
    
    success, message, data = await test_sheets_connection(spreadsheet_id)
    
    if not success:
        # Connection failed
        keyboard = [
            [InlineKeyboardButton("ðŸ”„ Thá»­ láº¡i", callback_data="sheets_connect_existing")],
            [InlineKeyboardButton("âŒ Há»§y", callback_data="sheets_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{message}\n\n"
            "**NguyÃªn nhÃ¢n cÃ³ thá»ƒ:**\n"
            "â€¢ Spreadsheet ID sai\n"
            "â€¢ Sheets chÆ°a cÃ i Apps Script\n"
            "â€¢ Quyá»n truy cáº­p bá»‹ háº¡n cháº¿\n\n"
            "Báº¡n muá»‘n thá»­ láº¡i khÃ´ng?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return WAITING_FOR_SHEETS_ID
    
    # Success! Save to database
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if user:
        user.spreadsheet_id = spreadsheet_id
        user.sheets_connected_at = datetime.now()
        user.sheets_last_sync = datetime.now()
        db.commit()
        logger.info(f"âœ… User {user_id} connected Sheets: {spreadsheet_id[:20]}...")
    
    # Show success message with balance info
    await update.message.reply_text(
        f"{message}\n"
        "ðŸŽ‰ **Báº¡n Ä‘Ã£ káº¿t ná»‘i thÃ nh cÃ´ng!**\n\n"
        "**BÃ¢y giá» báº¡n cÃ³ thá»ƒ:**\n"
        "â€¢ ðŸ“ Ghi nhanh: `chi 50k tiá»n Äƒn`\n"
        "â€¢ ðŸ’° Xem sá»‘ dÆ°: /balance\n"
        "â€¢ ðŸ“Š PhÃ¢n tÃ­ch: /spending\n\n"
        "HÃ£y thá»­ ghi má»™t giao dá»‹ch nÃ o Ä‘Ã³! ðŸš€",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END


async def handle_sheets_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user muá»‘n Ä‘á»•i Sheets khÃ¡c"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "ðŸ”„ **Äá»”I GOOGLE SHEETS**\n\n"
        "Gá»­i **link** hoáº·c **Spreadsheet ID** má»›i cho bot.\n\n"
        "âš ï¸ *LÆ°u Ã½: Káº¿t ná»‘i cÅ© sáº½ bá»‹ thay tháº¿.*"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return WAITING_FOR_SHEETS_ID


async def handle_sheets_keep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user giá»¯ nguyÃªn Sheets hiá»‡n táº¡i"""
    query = update.callback_query
    await query.answer("âœ… Giá»¯ nguyÃªn káº¿t ná»‘i hiá»‡n táº¡i")
    
    await query.edit_message_text(
        "âœ… OK! Giá»¯ nguyÃªn káº¿t ná»‘i Google Sheets hiá»‡n táº¡i.\n\n"
        "Báº¡n cÃ³ thá»ƒ dÃ¹ng ngay cÃ¡c lá»‡nh:\n"
        "â€¢ ðŸ“ `chi 50k tiá»n Äƒn`\n"
        "â€¢ ðŸ’° /balance\n"
        "â€¢ ðŸ“Š /spending",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def handle_sheets_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user há»§y"""
    query = update.callback_query
    await query.answer("âŒ ÄÃ£ há»§y")
    
    await query.edit_message_text(
        "âŒ ÄÃ£ há»§y káº¿t ná»‘i Google Sheets.\n\n"
        "DÃ¹ng /connectsheets khi báº¡n muá»‘n káº¿t ná»‘i láº¡i nhÃ©! ðŸ˜Š"
    )
    return ConversationHandler.END


def register_sheets_template_handlers(application):
    """Register all sheets template integration handlers"""
    
    # Conversation handler for sheets connection
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("connectsheets", handle_connect_sheets),
            CallbackQueryHandler(handle_connect_sheets, pattern="^premium_sheets$")
        ],
        states={
            WAITING_FOR_SHEETS_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sheets_id_input),
                CallbackQueryHandler(handle_sheets_create_new, pattern="^sheets_create_new$"),
                CallbackQueryHandler(handle_sheets_connect_existing, pattern="^sheets_connect_existing$"),
                CallbackQueryHandler(handle_sheets_change, pattern="^sheets_change$"),
                CallbackQueryHandler(handle_sheets_cancel, pattern="^sheets_cancel$"),
                CallbackQueryHandler(handle_sheets_keep, pattern="^sheets_keep$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(handle_sheets_cancel, pattern="^sheets_cancel$")
        ],
        name="sheets_connection",
        persistent=False
    )
    
    application.add_handler(conv_handler)
    logger.info("âœ… Sheets template integration handlers registered")

