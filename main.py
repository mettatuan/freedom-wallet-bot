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

# === CLEAN ARCHITECTURE (Phase 6: Production Integration) ===
# Feature flag to enable Clean Architecture handlers
USE_CLEAN_ARCHITECTURE = False  # Set to False to use only old handlers

# Clean Architecture imports
if USE_CLEAN_ARCHITECTURE:
    from src.infrastructure import (
        initialize_container,
        init_db,
        get_container
    )
    from src.presentation import (
        start_command as ca_start_command,
        start_sheet_setup as ca_start_sheet_setup,
        receive_email as ca_receive_email,
        receive_phone as ca_receive_phone,
        receive_sheet_url as ca_receive_sheet_url,
        receive_webapp_url as ca_receive_webapp_url,
        cancel_setup as ca_cancel_setup,
        AWAITING_EMAIL as CA_AWAITING_EMAIL,
        AWAITING_PHONE as CA_AWAITING_PHONE,
        AWAITING_SHEET_URL as CA_AWAITING_SHEET_URL,
        AWAITING_WEBAPP_URL as CA_AWAITING_WEBAPP_URL,
        quick_record_transaction as ca_quick_record_transaction,
        balance_command as ca_balance_command,
        recent_transactions_command as ca_recent_command
    )

# Old handlers
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
    
    # === Initialize Clean Architecture (Phase 6) ===
    if USE_CLEAN_ARCHITECTURE:
        try:
            logger.info("🏗️  Initializing Clean Architecture...")
            
            # 1. Initialize database
            init_db()
            logger.info("   ✅ Database initialized")
            
            # 2. Initialize DI Container
            initialize_container(
                bot=application.bot,
                google_credentials_file="google_service_account.json",
                openai_api_key=settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None,
                openai_model="gpt-4"
            )
            logger.info("   ✅ DI Container initialized")
            logger.info("🎉 Clean Architecture ready!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Clean Architecture: {e}", exc_info=True)
            logger.warning("⚠️  Falling back to old handlers only")
    
    # Add any other initialization logic here


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
    
    # === Register Clean Architecture handlers (Phase 6) ===
    if USE_CLEAN_ARCHITECTURE:
        try:
            logger.info("🔌 Registering Clean Architecture handlers...")
            
            # Clean Architecture /start command (overrides old handler)
            application.add_handler(CommandHandler("start", ca_start_command), group=0)
            logger.info("   ✅ CA /start handler registered")
            
            # CA Callback handlers (for buttons in start message)
            from src.presentation.handlers.ca_callbacks import (
                ca_learn_more,
                ca_back_to_start,
                ca_cancel_registration
            )
            # NOTE: ca_start_free_registration is handled by ConversationHandler entry point
            application.add_handler(CallbackQueryHandler(ca_learn_more, pattern="^learn_more$"), group=0)
            application.add_handler(CallbackQueryHandler(ca_back_to_start, pattern="^back_to_start$"), group=0)
            application.add_handler(CallbackQueryHandler(ca_cancel_registration, pattern="^cancel_ca_registration$"), group=0)
            logger.info("   ✅ CA callback handlers registered")
            
            # Clean Architecture Sheet Setup Conversation
            ca_setup_conversation = ConversationHandler(
                entry_points=[
                    CommandHandler("setup_ca", ca_start_sheet_setup),
                    CallbackQueryHandler(ca_start_sheet_setup, pattern="^setup_sheet$"),
                    CallbackQueryHandler(ca_start_sheet_setup, pattern="^start_free_registration$")  # NEW: From /start button
                ],
                states={
                    CA_AWAITING_EMAIL: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, ca_receive_email)
                    ],
                    CA_AWAITING_PHONE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, ca_receive_phone)
                    ],
                    CA_AWAITING_SHEET_URL: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, ca_receive_sheet_url)
                    ],
                    CA_AWAITING_WEBAPP_URL: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, ca_receive_webapp_url)
                    ],
                },
                fallbacks=[CommandHandler("cancel", ca_cancel_setup)],
                per_chat=True,
                per_user=True,
                name="ca_sheet_setup_conversation"
            )
            application.add_handler(ca_setup_conversation, group=0)
            logger.info("   ✅ CA Sheet Setup conversation registered")
            
            # Clean Architecture Balance & Recent commands
            application.add_handler(CommandHandler("balance", ca_balance_command), group=0)
            application.add_handler(CommandHandler("recent", ca_recent_command), group=0)
            logger.info("   ✅ CA Balance/Recent commands registered")
            
            logger.info("✅ Clean Architecture handlers ready!")
            
        except Exception as e:
            logger.error(f"❌ Failed to register CA handlers: {e}", exc_info=True)
    
    # === Register OLD handlers (backward compatibility) ===
    # Note: If USE_CLEAN_ARCHITECTURE=True, /start is overridden by CA handler
    if not USE_CLEAN_ARCHITECTURE:
        application.add_handler(CommandHandler("start", start))
        # Legacy registration handler (disabled when CA is active)
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
    
    # === Clean Architecture Quick Record Transaction (Phase 6) ===
    # Register BEFORE old message handler to intercept transaction messages
    if USE_CLEAN_ARCHITECTURE:
        try:
            application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, ca_quick_record_transaction),
                group=90  # Higher priority than old message handler (group=100)
            )
            logger.info("✅ CA Quick Record Transaction handler registered")
        except Exception as e:
            logger.error(f"❌ Failed to register CA quick record: {e}", exc_info=True)
    
    # Register OLD message handler (for AI conversations - must be last)
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
