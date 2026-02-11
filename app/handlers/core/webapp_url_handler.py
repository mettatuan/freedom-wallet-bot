"""
Web App URL Handler
Allow users to save and retrieve their Freedom Wallet Web App URL
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from app.utils.database import get_db, User
from loguru import logger

# Conversation states
WAITING_FOR_URL = 1

async def cmd_mywebapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show saved Web App URL or prompt to save one"""
    user_id = update.effective_user.id
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            await update.message.reply_text("âŒ User not found. Please /start first.")
            return
        
        if user.web_app_url:
            # User has saved URL
            keyboard = [
                [InlineKeyboardButton("ðŸŒ Má»Ÿ Web App", url=user.web_app_url)],
                [InlineKeyboardButton("âœï¸ Cáº­p nháº­t link", callback_data="update_webapp_url")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"ðŸ“± **Web App cá»§a báº¡n:**\n\n"
                f"`{user.web_app_url}`\n\n"
                f"ðŸ’¡ Nháº¥n nÃºt bÃªn dÆ°á»›i Ä‘á»ƒ má»Ÿ hoáº·c cáº­p nháº­t link!",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            # No URL saved yet
            keyboard = [[InlineKeyboardButton("ðŸ’¾ LÆ°u link Web App", callback_data="save_webapp_url")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"ðŸ“± **LÆ°u link Web App**\n\n"
                f"Báº¡n chÆ°a lÆ°u link Web App cá»§a Freedom Wallet.\n\n"
                f"ðŸ’¡ LÆ°u link Ä‘á»ƒ:\n"
                f"â€¢ Truy cáº­p nhanh khi cáº§n ghi chÃ©p\n"
                f"â€¢ KhÃ´ng pháº£i tÃ¬m láº¡i link má»—i láº§n\n"
                f"â€¢ Bot sáº½ gá»­i link cho báº¡n khi cáº§n\n\n"
                f"Nháº¥n nÃºt bÃªn dÆ°á»›i Ä‘á»ƒ lÆ°u!",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    
    finally:
        db.close()

async def callback_save_webapp_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to send Web App URL"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "ðŸ“± **Gá»­i link Web App cá»§a báº¡n**\n\n"
        "Vui lÃ²ng gá»­i URL cá»§a Freedom Wallet Web App.\n"
        "VD: `https://script.google.com/macros/s/ABC.../exec`\n\n"
        "ðŸ“Œ Báº¡n cÃ³ thá»ƒ tÃ¬m link nÃ y trong Apps Script deployment.\n\n"
        "Hoáº·c gá»­i /cancel Ä‘á»ƒ há»§y.",
        parse_mode="Markdown"
    )
    
    return WAITING_FOR_URL

async def callback_update_webapp_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt user to update Web App URL"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "ðŸ“± **Cáº­p nháº­t link Web App**\n\n"
        "Vui lÃ²ng gá»­i URL má»›i cá»§a Freedom Wallet Web App.\n"
        "VD: `https://script.google.com/macros/s/ABC.../exec`\n\n"
        "Hoáº·c gá»­i /cancel Ä‘á»ƒ há»§y.",
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
            "âŒ URL khÃ´ng há»£p lá»‡. Vui lÃ²ng gá»­i URL báº¯t Ä‘áº§u báº±ng http:// hoáº·c https://\n\n"
            "Hoáº·c /cancel Ä‘á»ƒ há»§y."
        )
        return WAITING_FOR_URL
    
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            await update.message.reply_text("âŒ User not found.")
            return ConversationHandler.END
        
        # Save URL
        user.web_app_url = url
        db.commit()
        
        keyboard = [[InlineKeyboardButton("ðŸŒ Má»Ÿ Web App", url=url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"âœ… **ÄÃ£ lÆ°u link Web App!**\n\n"
            f"`{url}`\n\n"
            f"ðŸ’¡ DÃ¹ng /mywebapp Ä‘á»ƒ xem láº¡i link báº¥t cá»© lÃºc nÃ o!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"âœ… User {user_id} saved Web App URL")
        
    except Exception as e:
        logger.error(f"âŒ Error saving Web App URL: {e}")
        await update.message.reply_text("âŒ CÃ³ lá»—i xáº£y ra. Vui lÃ²ng thá»­ láº¡i sau.")
    
    finally:
        db.close()
    
    return ConversationHandler.END

async def cancel_webapp_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text("âŒ ÄÃ£ há»§y. DÃ¹ng /mywebapp Ä‘á»ƒ thá»­ láº¡i.")
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
    
    logger.info("âœ… Web App URL handlers registered")

