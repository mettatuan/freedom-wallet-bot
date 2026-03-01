"""
Freedom Wallet Bot - Main Entry Point
A Telegram bot providing 24/7 customer support for Freedom Wallet app
"""

import asyncio
import html
import logging
import os
import sys
import traceback
from pathlib import Path

# ── Single-instance lock (PID file) ────────────────────────────────────────
_PID_FILE = Path(__file__).parent / "bot.pid"

def _acquire_lock() -> bool:
    """Return True if we acquired the lock; False if another instance is running."""
    if _PID_FILE.exists():
        try:
            old_pid = int(_PID_FILE.read_text().strip())
            # Check if that PID is still alive
            try:
                os.kill(old_pid, 0)  # signal 0 = just check existence
                print(f"[LOCK] Another instance is running (PID {old_pid}). Exiting.", flush=True)
                return False
            except (OSError, ProcessLookupError):
                pass  # PID is stale — safe to overwrite
        except (ValueError, OSError):
            pass
    _PID_FILE.write_text(str(os.getpid()))
    return True

def _release_lock():
    try:
        _PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass

if not _acquire_lock():
    sys.exit(1)

import atexit
atexit.register(_release_lock)
# ───────────────────────────────────────────────────────────────────────────

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PicklePersistence,
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
    """Log + smart alert via ErrorTracker + auto-fix attempts + reply to user."""
    from bot.core.error_tracker import get_tracker
    from bot.core.auto_fix_handlers import try_auto_fix
    error = context.error

    # ── 1. Try auto-fix FIRST (trước khi track) ────────────────────────────
    auto_fix_result = None
    try:
        fix_context = {
            "update": update,
            "user_id": update.effective_user.id if update and update.effective_user else None,
            "chat_id": update.effective_chat.id if update and update.effective_chat else None,
        }
        auto_fix_result = await try_auto_fix(error, fix_context)
        
        if auto_fix_result and auto_fix_result.success:
            logger.info(f"✅ Auto-fix SUCCESS: {auto_fix_result.action_taken}")
            # Nếu fix thành công và should_retry → không cần alert user
            if auto_fix_result.should_retry:
                return  # Silent recovery
    except Exception as fix_error:
        logger.error(f"Auto-fix attempt crashed: {fix_error}", exc_info=True)

    # ── 2. Track lỗi (bỏ qua nếu ignorable, check ngưỡng alert) ──────────
    tracker = get_tracker()
    result = tracker.record(error)

    if result["ignorable"]:
        logger.debug(f"Ignorable error (suppressed): {type(error).__name__}: {error}")
        return

    logger.error("Unhandled exception", exc_info=error)

    # ── 3. Reply to user (best-effort) ───────────────────────────────────────
    try:
        if update and update.effective_message:
            # Nếu có auto-fix result, show action taken
            if auto_fix_result:
                extra = f"\n🔧 {auto_fix_result.action_taken}"
                if auto_fix_result.should_retry:
                    extra += f"\n♻️ Đang thử lại sau {auto_fix_result.retry_delay}s..."
            else:
                hint = result.get("recovery_hint")
                extra = f"\n🔧 {hint}" if hint else ""
            
            await update.effective_message.reply_text(
                f"😓 Xin lỗi, bot gặp lỗi không xử lý được.{extra}\n"
                "Vui lòng thử lại sau hoặc liên hệ admin: @tuanai_mentor\n"
                "Dùng /feedback để báo chi tiết."
            )
    except Exception:
        pass

    if not settings.ADMIN_USER_ID:
        return

    # ── 3. Smart alert: chỉ gửi khi vượt ngưỡng HOẶC lỗi lần đầu ──────────
    is_first_occurrence = result.get("total", 0) == 1
    if not result["alert_needed"] and not is_first_occurrence:
        return

    try:
        tb = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        user_info = ""
        if update and update.effective_user:
            u = update.effective_user
            user_info = (
                f"\n👤 User: <code>{html.escape(u.full_name or '')}</code> "
                f"(<code>{u.id}</code>)"
            )
        chat_info = ""
        if update and update.effective_chat:
            chat_info = f"\n💬 Chat: <code>{update.effective_chat.id}</code>"

        count = result.get('count_in_window', 1)
        badge = f" [{count}x]" if count > 1 else " [mới]"
        tb_escaped = html.escape(tb[-2000:])
        
        # Auto-fix status badge
        autofix_badge = ""
        if auto_fix_result:
            if auto_fix_result.success:
                autofix_badge = f"\n🔧 <b>Auto-fix:</b> ✅ {html.escape(auto_fix_result.action_taken)}"
                if auto_fix_result.should_retry:
                    autofix_badge += " (retrying)"
            else:
                autofix_badge = f"\n🔧 <b>Auto-fix:</b> ❌ {html.escape(auto_fix_result.action_taken)}"
        
        alert = (
            f"🚨 <b>Bot Exception{badge}</b>{user_info}{chat_info}{autofix_badge}\n\n"
            f"<pre>{tb_escaped}</pre>"
        )
        await context.bot.send_message(
            chat_id=settings.ADMIN_USER_ID, text=alert, parse_mode="HTML"
        )
    except Exception as alert_err:
        logger.warning(f"Failed to send error alert: {alert_err}")

    # ── 4. Smart digest alert nếu lỗi lặp vượt ngưỡng ──────────────────────
    if result["alert_needed"]:
        await tracker.send_alert(error, f"{user_info}{chat_info}", result)


async def post_init(application: Application) -> None:
    """Initialize bot after startup."""
    logger.info("[BOT] Freedom Wallet Bot is starting...")
    # Wire up ErrorTracker with bot instance for alerts
    from bot.core.error_tracker import get_tracker
    from config.settings import settings as _settings
    if _settings.ADMIN_USER_ID:
        get_tracker().setup(application.bot, _settings.ADMIN_USER_ID)


async def post_shutdown(application: Application) -> None:
    """Cleanup after bot shutdown."""
    logger.info("[BOT] Freedom Wallet Bot is shutting down...")
    # Add any cleanup logic here


def main() -> None:
    """Start the bot."""
    # Create application
    # Persist user_data to disk so pending_tx survives bot restarts
    persistence = PicklePersistence(filepath="data/bot_persistence.pkl")

    builder = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .persistence(persistence)
        .concurrent_updates(32)
        .connect_timeout(60)
        .read_timeout(30)
        .write_timeout(30)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
    )
    # Cloudflare Worker proxy: set TELEGRAM_BASE_URL in .env to bypass regional blocks
    if settings.TELEGRAM_BASE_URL:
        base = settings.TELEGRAM_BASE_URL.rstrip('/')
        builder = builder.base_url(f"{base}/bot").base_file_url(f"{base}/file/bot")
        logger.info(f"[INFO] Using Telegram proxy: {base}")
    application = builder.build()
    
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
        entry_points=[
            CommandHandler("register", start_registration),
            CallbackQueryHandler(start_registration, pattern="^start_register$"),
            CallbackQueryHandler(start_registration, pattern="^start_free_registration$")
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
    
    # ── Admin menu (group=-10: intercepts commands even inside ConversationHandlers) ──
    from bot.handlers.admin_menu import register_admin_menu_handlers
    register_admin_menu_handlers(application)
    
    # ── Admin user management commands ──
    from bot.handlers.admin_users import register_admin_user_handlers
    register_admin_user_handlers(application)

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
    
    # Phase 2: Transaction Engine (Retention-First Model)
    try:
        from bot.handlers.transaction import register_transaction_handlers
        logger.info("📦 Importing transaction handlers...")
        register_transaction_handlers(application)
        logger.info("✅ Transaction Engine handlers registered")
    except Exception as e:
        logger.error(f"❌ Failed to register transaction handlers: {e}", exc_info=True)
    
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
    
    # Week 5: Admin fraud review commands (group=-10: work even inside conversations)
    from bot.handlers.admin_fraud import (
        fraud_queue_command,
        fraud_review_command,
        fraud_approve_command,
        fraud_reject_command,
        fraud_stats_command
    )
    application.add_handler(CommandHandler("fraud_queue", fraud_queue_command), group=-10)
    application.add_handler(CommandHandler("fraud_review", fraud_review_command), group=-10)
    application.add_handler(CommandHandler("fraud_approve", fraud_approve_command), group=-10)
    application.add_handler(CommandHandler("fraud_reject", fraud_reject_command), group=-10)
    application.add_handler(CommandHandler("fraud_stats", fraud_stats_command), group=-10)
    
    # Admin payment commands
    from bot.handlers.admin_payment import (
        payment_pending_command,
        payment_approve_command,
        payment_reject_command,
        payment_stats_command
    )
    application.add_handler(CommandHandler("payment_pending", payment_pending_command), group=-10)
    application.add_handler(CommandHandler("payment_approve", payment_approve_command), group=-10)
    application.add_handler(CommandHandler("payment_reject", payment_reject_command), group=-10)
    application.add_handler(CommandHandler("payment_stats", payment_stats_command), group=-10)
    
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
    setup_daily_jobs(application)

    # Landing page sync — runs every 30 mins to pull Google Sheet registrations into bot DB
    async def sync_landing_page_wrapper(context):
        from bot.utils.sync_landing_page import sync_landing_page_users_to_db
        await sync_landing_page_users_to_db()
    
    application.job_queue.run_repeating(
        sync_landing_page_wrapper, 
        interval=1800,  # 30 minutes
        first=120,      # Start after 2 mins (give time for bot to init)
        name="landing_page_sync"
    )
    logger.info("✅ Landing page sync job registered (every 30min)")

    # Health monitor — runs every 5 mins
    from bot.jobs.health_monitor import health_check_job, register_health_handlers
    application.job_queue.run_repeating(health_check_job, interval=300, first=60, name="health_monitor")
    register_health_handlers(application, group=-10)
    logger.info("✅ Health monitor job registered (every 5min)")

    # User feedback handler
    from bot.handlers.feedback import register_feedback_handler
    register_feedback_handler(application)
    logger.info("✅ Feedback handler registered")

    # Admin broadcast handler (group=-10: commands work even inside conversations)
    from bot.handlers.admin_broadcast import register_broadcast_handlers
    register_broadcast_handlers(application, group=-10)
    logger.info("✅ Broadcast handlers registered (group=-10)")
    
    # Auto-fix metrics admin handlers (group=-10)
    try:
        from bot.handlers.admin_autofix import register_autofix_admin_handlers
        register_autofix_admin_handlers(application, group=-10)
        logger.info("✅ Auto-fix admin handlers registered (group=-10)")
    except Exception as e:
        logger.error(f"❌ Failed to register auto-fix admin handlers: {e}")
    
    # Rollback admin handlers (group=-10)
    try:
        from bot.handlers.admin_rollback import register_rollback_admin_handlers
        register_rollback_admin_handlers(application, group=-10)
        logger.info("✅ Rollback admin handlers registered (group=-10)")
    except Exception as e:
        logger.error(f"❌ Failed to register rollback admin handlers: {e}")
    
    # Rollback monitoring job — runs every 2 mins
    try:
        from bot.core.rollback_system import get_rollback_system
        
        async def rollback_monitor_job(context):
            """Periodic rollback monitoring."""
            rollback_system = get_rollback_system()
            await rollback_system.monitor_and_rollback_if_needed()
        
        application.job_queue.run_repeating(
            rollback_monitor_job,
            interval=120,  # 2 minutes
            first=180,  # Start after 3 minutes (let bot warm up)
            name="rollback_monitor"
        )
        logger.info("✅ Rollback monitoring job registered (every 2min)")
    except Exception as e:
        logger.error(f"❌ Failed to register rollback monitor: {e}")
    
    # Start bot
    logger.info(f"[OK] Bot started in {settings.ENV} mode")
    logger.info(f"[INFO] Log level: {settings.LOG_LEVEL}")
    logger.info(f"[INFO] ADMIN_USER_ID: {settings.ADMIN_USER_ID} {'✅' if settings.ADMIN_USER_ID == 6588506476 else '⚠️ WRONG ID!'}")
    
    # Start polling (connect_timeout=60 handles slow Telegram API at startup)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
