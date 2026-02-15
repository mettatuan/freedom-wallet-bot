"""
Freedom Wallet Template Integration Handlers (Option 3)
User flow: Tạo mới hoặc Đã có Sheets → Nhập ID → Kết nối → Sử dụng
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
    Cho phép user kết nối Google Sheets
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
                InlineKeyboardButton("🔄 Đổi Sheets khác", callback_data="sheets_change"),
                InlineKeyboardButton("✅ Giữ nguyên", callback_data="sheets_keep")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            f"📊 Bạn đã kết nối Google Sheets rồi!\n\n"
            f"🔗 Spreadsheet ID: `{user.spreadsheet_id[:20]}...`\n"
            f"📅 Kết nối lúc: {user.sheets_connected_at.strftime('%d/%m/%Y %H:%M') if user.sheets_connected_at else 'N/A'}\n\n"
            f"Bạn muốn đổi sang Sheets khác không?"
        )
        
        await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        return ConversationHandler.END
    
    # Show options: Create new or Connect existing
    keyboard = [
        [InlineKeyboardButton("🆕 Tạo mới từ Template", callback_data="sheets_create_new")],
        [InlineKeyboardButton("📂 Đã có Sheets rồi", callback_data="sheets_connect_existing")],
        [InlineKeyboardButton("❌ Hủy", callback_data="sheets_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "📊 **KẾT NỐI GOOGLE SHEETS**\n\n"
        "Freedom Wallet Bot cần kết nối với Google Sheets của bạn để:\n"
        "• 📝 Ghi lại giao dịch nhanh\n"
        "• 💰 Xem số dư các hũ\n"
        "• 📊 Phân tích chi tiêu\n\n"
        "**Chọn một trong hai cách:**"
    )
    
    await message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return WAITING_FOR_SHEETS_ID


async def handle_sheets_create_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user chọn tạo mới từ template"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "🆕 **TẠO FREEDOM WALLET MỚI**\n\n"
        "**Bước 1:** Mở link template dưới đây\n"
        "**Bước 2:** Click **\"Tạo bản sao\"** (Make a copy)\n"
        "**Bước 3:** Copy **link** hoặc **Spreadsheet ID**\n"
        "**Bước 4:** Gửi cho bot\n\n"
        f"🔗 **Template:** {TEMPLATE_URL}\n\n"
        "💡 *Tip: ID là đoạn giữa 2 dấu / trong URL*\n"
        "`https://docs.google.com/spreadsheets/d/`**`ID_Ở_ĐÂY`**`/edit`"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return WAITING_FOR_SHEETS_ID


async def handle_sheets_connect_existing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user đã có Sheets sẵn"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "📂 **KẾT NỐI SHEETS CÓ SẴN**\n\n"
        "Gửi cho bot **link** hoặc **Spreadsheet ID** của Freedom Wallet Sheets của bạn.\n\n"
        "📋 **Ví dụ:**\n"
        "• Link: `https://docs.google.com/spreadsheets/d/1ABC.../edit`\n"
        "• Hoặc chỉ ID: `1ABC...`\n\n"
        "💡 *Bot sẽ test kết nối và xác nhận cho bạn.*"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return WAITING_FOR_SHEETS_ID


async def handle_sheets_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler khi user gửi Spreadsheet ID hoặc URL
    Test connection và lưu vào database
    """
    user_input = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Extract spreadsheet ID
    spreadsheet_id = extract_spreadsheet_id(user_input)
    
    if not spreadsheet_id:
        await update.message.reply_text(
            "❌ Không tìm thấy Spreadsheet ID hợp lệ.\n\n"
            "Vui lòng gửi:\n"
            "• Link đầy đủ: `https://docs.google.com/spreadsheets/d/ID/edit`\n"
            "• Hoặc chỉ ID: `1ABC...`\n\n"
            "Thử lại nhé! 😊",
            parse_mode="Markdown"
        )
        return WAITING_FOR_SHEETS_ID
    
    # Test connection
    await update.message.reply_text("🔄 Đang test kết nối...\n⏳ Vui lòng đợi...")
    
    success, message, data = await test_sheets_connection(spreadsheet_id)
    
    if not success:
        # Connection failed
        keyboard = [
            [InlineKeyboardButton("🔄 Thử lại", callback_data="sheets_connect_existing")],
            [InlineKeyboardButton("❌ Hủy", callback_data="sheets_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{message}\n\n"
            "**Nguyên nhân có thể:**\n"
            "• Spreadsheet ID sai\n"
            "• Sheets chưa cài Apps Script\n"
            "• Quyền truy cập bị hạn chế\n\n"
            "Bạn muốn thử lại không?",
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
        logger.info(f"✅ User {user_id} connected Sheets: {spreadsheet_id[:20]}...")
    
    # Show success message with balance info
    await update.message.reply_text(
        f"{message}\n"
        "🎉 **Bạn đã kết nối thành công!**\n\n"
        "**Bây giờ bạn có thể:**\n"
        "• 📝 Ghi nhanh: `chi 50k tiền ăn`\n"
        "• 💰 Xem số dư: /balance\n"
        "• 📊 Phân tích: /spending\n\n"
        "Hãy thử ghi một giao dịch nào đó! 🚀",
        parse_mode="Markdown"
    )
    
    return ConversationHandler.END


async def handle_sheets_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user muốn đổi Sheets khác"""
    query = update.callback_query
    await query.answer()
    
    text = (
        "🔄 **ĐỔI GOOGLE SHEETS**\n\n"
        "Gửi **link** hoặc **Spreadsheet ID** mới cho bot.\n\n"
        "⚠️ *Lưu ý: Kết nối cũ sẽ bị thay thế.*"
    )
    
    await query.edit_message_text(text, parse_mode="Markdown")
    return WAITING_FOR_SHEETS_ID


async def handle_sheets_keep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user giữ nguyên Sheets hiện tại"""
    query = update.callback_query
    await query.answer("✅ Giữ nguyên kết nối hiện tại")
    
    await query.edit_message_text(
        "✅ OK! Giữ nguyên kết nối Google Sheets hiện tại.\n\n"
        "Bạn có thể dùng ngay các lệnh:\n"
        "• 📝 `chi 50k tiền ăn`\n"
        "• 💰 /balance\n"
        "• 📊 /spending",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


async def handle_sheets_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler khi user há»§y"""
    query = update.callback_query
    await query.answer("❌ Đã hủy")
    
    await query.edit_message_text(
        "❌ Đã hủy kết nối Google Sheets.\n\n"
        "Dùng /connectsheets khi bạn muốn kết nối lại nhé! 😊"
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
    logger.info("✅ Sheets template integration handlers registered")

