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

# Handlers
from bot.handlers.start import start, help_menu
from bot.handlers.status import mystatus_command  # DAY 2: ROI Dashboard
from bot.handlers.message import handle_message
from bot.handlers.support import support_command, save_support_ticket, cancel_support
from bot.handlers.callback import handle_callback
from bot.handlers.referral import referral_command
from bot.handlers.registration import (
    start_registration, receive_email, receive_phone, receive_name,
    confirm_registration, cancel_registration,
    AWAITING_EMAIL, AWAITING_PHONE, AWAITING_NAME, CONFIRM
)
from bot.handlers.setup_guide import register_setup_guide_handlers
from bot.handlers.webapp_setup import register_webapp_setup_handlers
from bot.handlers.daily_reminder import register_reminder_handlers
from bot.handlers.user_commands import register_user_command_handlers
from bot.handlers.vip import register_vip_handlers  # VIP Identity Tier (Feb 2026)
from bot.handlers.free_flow import register_free_flow_handlers  # FREE step-by-step flow (Feb 2026)
from bot.handlers.unlock_calm_flow import register_unlock_calm_flow_handlers  # UNLOCK calm flow (Feb 2026)

# Configure logging with UTF-8 encoding
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, settings.LOG_LEVEL),
    handlers=[
        logging.FileHandler('data/logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ],
    encoding='utf-8',
    errors='replace'  # Replace unencodable chars instead of crash
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
    
    # Registration conversation handler (LEGACY - disabled when using CA)
    registration_handler = ConversationHandler(
        entry_points=[
            CommandHandler("register", start_registration),
            CallbackQueryHandler(start_registration, pattern="^start_register$"),
            # REMOVED: start_free_registration now handled by CA conversation (line 209)
            # CallbackQueryHandler(start_registration, pattern="^start_free_registration$")
        ],
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
                CallbackQueryHandler(confirm_registration, pattern="^confirm_registration_")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_registration)],
        per_message=False,  # CRITICAL: Must be False when starting from CallbackQuery
        per_chat=True,
        per_user=True,
        name="registration_conversation"  # Add name for debugging
    )
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(registration_handler)
    
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("mystatus", mystatus_command))  # DAY 2: ROI Dashboard
    application.add_handler(CommandHandler("referral", referral_command))
    application.add_handler(support_handler)
    # application.add_handler(CommandHandler("tutorial", tutorial_command))
    # application.add_handler(CommandHandler("tips", tips_command))
    
    # Register setup guide handlers (Week 5+)
    register_setup_guide_handlers(application)
    
    # Register FREE step-by-step flow (Feb 2026)
    try:
        register_free_flow_handlers(application)
        logger.info("✅ FREE flow handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register FREE flow handlers: {e}", exc_info=True)
    
    # Register UNLOCK calm flow (Feb 2026)
    try:
        register_unlock_calm_flow_handlers(application)
        logger.info("✅ UNLOCK calm flow handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register UNLOCK calm flow handlers: {e}", exc_info=True)
    
    # Register unlock flow v3.0 handlers (Feb 2026)
    try:
        from bot.handlers.unlock_flow_v3 import register_unlock_handlers
        register_unlock_handlers(application)
        logger.info("✅ Unlock flow v3.0 handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register unlock flow handlers: {e}", exc_info=True)
    
    # Register VIP Identity Tier handlers (Feb 2026)
    try:
        register_vip_handlers(application)
        logger.info("✅ VIP handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register VIP handlers: {e}", exc_info=True)
    
    try:
        register_webapp_setup_handlers(application)
        logger.info("✅ Web App Setup handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register webapp_setup handlers: {e}", exc_info=True)
    
    # Register sheets setup handlers (Google Sheets connection)
    try:
        from bot.handlers.sheets_setup import register_sheets_setup_handlers
        logger.info("📦 Importing sheets_setup handlers...")
        register_sheets_setup_handlers(application)
        logger.info("✅ Sheets setup handlers registration COMPLETED")
    except Exception as e:
        logger.error(f"❌ Failed to register sheets_setup handlers: {e}", exc_info=True)
    
    # Register daily reminder handlers (Week 6)
    register_reminder_handlers(application)
    register_user_command_handlers(application)
    
    # Week 2: Web App URL Management
    try:
        from bot.handlers.webapp_url_handler import register_webapp_handlers
        logger.info("📦 Importing webapp_url_handler...")
        register_webapp_handlers(application)
        logger.info("✅ Web App URL handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register webapp_url handlers: {e}", exc_info=True)
    
    # Week 2: Quick Record & Premium Features (Option 3 - Template Integration)
    from bot.handlers.sheets_template_integration import register_sheets_template_handlers
    from bot.handlers.quick_record_template import register_quick_record_handlers
    from bot.handlers.sheets_premium_commands import register_sheets_premium_commands
    
    register_sheets_template_handlers(application)
    register_quick_record_handlers(application)
    register_sheets_premium_commands(application)
    
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
    
    # Admin payment commands
    from bot.handlers.admin_payment import (
        payment_pending_command,
        payment_approve_command,
        payment_reject_command,
        payment_stats_command
    )
    application.add_handler(CommandHandler("payment_pending", payment_pending_command))
    application.add_handler(CommandHandler("payment_approve", payment_approve_command))
    application.add_handler(CommandHandler("payment_reject", payment_reject_command))
    application.add_handler(CommandHandler("payment_stats", payment_stats_command))
    
    # Phase 2: Admin metrics dashboard (Feb 2026)
    try:
        from bot.handlers.admin_metrics import register_admin_metrics_handlers
        register_admin_metrics_handlers(application)
        logger.info("✅ Admin metrics handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register admin_metrics handlers: {e}", exc_info=True)
    
    # Register callback query handler (for inline buttons)
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Register photo handler (for payment proof)
    from bot.handlers.message import handle_payment_proof_photo
    application.add_handler(
        MessageHandler(filters.PHOTO, handle_payment_proof_photo),
        group=50
    )
    
    # Register message handler (for AI conversations - must be last)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
        group=100  # Lowest priority - only trigger if no other handler matched
    )
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Setup daily background jobs (Week 4)
    from bot.jobs import setup_daily_jobs
    from bot.jobs.unlock_trigger import setup_unlock_trigger_job
    setup_daily_jobs(application)
    setup_unlock_trigger_job(application)
    
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
