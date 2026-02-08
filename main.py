"""
Freedom Wallet Bot - Main Entry Point
A Telegram bot providing 24/7 customer support for Freedom Wallet app
"""

import asyncio
import logging
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# Add bot directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from bot.handlers.start import start, help_menu
from bot.handlers.message import handle_message
from bot.handlers.support import support_command, save_support_ticket, cancel_support
from bot.handlers.callback import handle_callback
from bot.handlers.referral import referral_command
from bot.handlers.registration import (
    start_registration, receive_email, receive_phone, receive_name,
    confirm_registration, cancel_registration,
    AWAITING_EMAIL, AWAITING_PHONE, AWAITING_NAME, CONFIRM
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL),
    handlers=[
        logging.FileHandler('data/logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def error_handler(update: Update, context) -> None:
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😓 Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau!\n"
            "Nếu vấn đề tiếp diễn, dùng /support để liên hệ."
        )


async def post_init(application: Application) -> None:
    """Initialize bot after startup."""
    logger.info("[BOT] Freedom Wallet Bot is starting...")
    # Add any initialization logic here


async def post_shutdown(application: Application) -> None:
    """Cleanup after bot shutdown."""
    logger.info("[BOT] Freedom Wallet Bot is shutting down...")
    # Add any cleanup logic here


def main() -> None:
    """Start the bot."""
    # Create application
    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    
    # Support conversation handler
    from telegram.ext import ConversationHandler
    support_handler = ConversationHandler(
        entry_points=[CommandHandler("support", support_command)],
        states={
            "WAITING_SUPPORT_MESSAGE": [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_support_ticket)
            ]
        },
        fallbacks=[CallbackQueryHandler(cancel_support, pattern="^cancel_support$")]
    )
    
    # Registration conversation handler
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("register", start_registration)],
        states={
            AWAITING_EMAIL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)
            ],
            AWAITING_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)
            ],
            AWAITING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)
            ],
            CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_registration)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_registration)]
    )
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("referral", referral_command))
    application.add_handler(support_handler)
    application.add_handler(registration_handler)
    # application.add_handler(CommandHandler("tutorial", tutorial_command))
    # application.add_handler(CommandHandler("tips", tips_command))
    
    # Week 5: Admin fraud review commands
    from bot.handlers.admin_fraud import (
        fraud_queue_command,
        fraud_review_command,
        fraud_approve_command,
        fraud_reject_command,
        fraud_stats_command
    )
    application.add_handler(CommandHandler("fraud_queue", fraud_queue_command))
    application.add_handler(CommandHandler("fraud_review", fraud_review_command))
    application.add_handler(CommandHandler("fraud_approve", fraud_approve_command))
    application.add_handler(CommandHandler("fraud_reject", fraud_reject_command))
    application.add_handler(CommandHandler("fraud_stats", fraud_stats_command))
    
    # Register callback query handler (for inline buttons)
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Register message handler (for AI conversations - must be last)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Setup daily background jobs (Week 4)
    from bot.jobs import setup_daily_jobs
    setup_daily_jobs(application)
    
    # Start bot
    logger.info(f"[OK] Bot started in {settings.ENV} mode")
    logger.info(f"[INFO] Log level: {settings.LOG_LEVEL}")
    
    # Run bot (polling mode for development, webhook for production)
    if settings.ENV == "development":
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    else:
        # TODO: Configure webhook for production
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
