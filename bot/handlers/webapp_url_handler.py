"""
Web App URL Handler
Allow users to save and retrieve their Freedom Wallet Web App URL
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from bot.utils.database import get_db, User, SessionLocal, run_sync
from loguru import logger

# Conversation states
WAITING_FOR_URL = 1


def _get_webapp_url_sync(user_id: int):
    """Returns {'web_app_url': ...} if user exists, else None."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return {"web_app_url": user.web_app_url}
    finally:
        db.close()


def _save_webapp_url_sync(user_id: int, url: str) -> bool:
    """Saves web_app_url. Returns True if user found and saved, False otherwise."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        user.web_app_url = url
        
        # Auto-update user_status when web app is set
        if url and url not in ["", "pending"]:
            user.user_status = "ACTIVE"
        elif user.is_registered:
            user.user_status = "WEBAPP_SETUP"
        
        db.commit()
        return True
    finally:
        db.close()

async def cmd_mywebapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show saved Web App URL or prompt to save one"""
    user_id = update.effective_user.id
    user_data = await run_sync(_get_webapp_url_sync, user_id)
    
    if user_data is None:
        await update.message.reply_text("❌ User not found. Please /start first.")
        return
    
    if user_data['web_app_url']:
        # User has saved URL
        keyboard = [
            [InlineKeyboardButton("🌐 Mở Web App", url=user_data['web_app_url'])],
            [InlineKeyboardButton("✏️ Cập nhật link", callback_data="update_webapp_url")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📱 **Web App của bạn:**\n\n"
            f"`{user_data['web_app_url']}`\n\n"
            f"💡 Nhấn nút bên dưới để mở hoặc cập nhật link!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        # No URL saved yet
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

async def callback_save_webapp_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to send Web App URL"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📱 **Gửi link Web App của bạn**\n\n"
        "Vui lòng gửi URL của Freedom Wallet Web App.\n"
        "VD: `https://script.google.com/macros/s/ABC.../exec`\n\n"
        "📌 Bạn có thể tìm link này trong Apps Script deployment.\n\n"
        "Hoặc gửi /cancel để hủy.",
        parse_mode="Markdown"
    )
    
    return WAITING_FOR_URL

async def callback_update_webapp_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to update Web App URL"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📱 **Cập nhật link Web App**\n\n"
        "Vui lòng gửi URL mới của Freedom Wallet Web App.\n"
        "VD: `https://script.google.com/macros/s/ABC.../exec`\n\n"
        "Hoặc gửi /cancel để hủy.",
        parse_mode="Markdown"
    )
    
    return WAITING_FOR_URL

async def handle_webapp_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the Web App URL to database"""
    user_id = update.effective_user.id
    url = update.message.text.strip()
    
    # Basic validation
    if not url.startswith("http"):
        await update.message.reply_text(
            "❌ URL không hợp lệ. Vui lòng gửi URL bắt đầu bằng http:// hoặc https://\n\n"
            "Hoặc /cancel để hủy."
        )
        return WAITING_FOR_URL
    
    saved = await run_sync(_save_webapp_url_sync, user_id, url)
    
    if not saved:
        await update.message.reply_text("❌ User not found.")
        return ConversationHandler.END
    
    keyboard = [[InlineKeyboardButton("🌐 Mở Web App", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_text(
            f"✅ **Đã lưu link Web App!**\n\n"
            f"`{url}`\n\n"
            f"💡 Dùng /mywebapp để xem lại link bất cứ lúc nào!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"✅ User {user_id} saved Web App URL")
    except Exception as e:
        logger.error(f"❌ Error sending save confirmation: {e}")
        await update.message.reply_text("❌ Có lỗi xảy ra. Vui lòng thử lại sau.")
    
    return ConversationHandler.END

async def cancel_webapp_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text("❌ Đã hủy. Dùng /mywebapp để thử lại.")
    return ConversationHandler.END

def register_webapp_handlers(application):
    """Register Web App URL handlers"""
    
    # Conversation handler for saving URL
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback_save_webapp_url, pattern="^save_webapp_url$"),
            CallbackQueryHandler(callback_update_webapp_url, pattern="^update_webapp_url$"),
        ],
        states={
            WAITING_FOR_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_webapp_url_input)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_webapp_url)],
        name="webapp_url_conversation",
        persistent=False,
        per_message=False
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("mywebapp", cmd_mywebapp))
    
    logger.info("✅ Web App URL handlers registered")
