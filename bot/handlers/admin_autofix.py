"""
Admin Commands for Auto-Fix Metrics Dashboard
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from loguru import logger
from config.settings import settings


async def handle_autofix_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: /autofix_stats
    
    Show auto-fix metrics summary.
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return
    
    try:
        from bot.core.autofix_metrics import get_metrics
        metrics = get_metrics()
        report = metrics.get_summary_report()
        
        await update.message.reply_text(report, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in /autofix_stats: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error loading metrics: {str(e)[:100]}",
            parse_mode="HTML"
        )


async def handle_autofix_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: /autofix_history [limit]
    
    Show recent auto-fix attempts.
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return
    
    try:
        # Parse limit from args (default 20)
        limit = 20
        if context.args and len(context.args) > 0:
            try:
                limit = int(context.args[0])
                limit = min(max(limit, 5), 50)  # Clamp between 5-50
            except ValueError:
                pass
        
        from bot.core.autofix_metrics import get_metrics
        metrics = get_metrics()
        report = metrics.get_history_report(limit=limit)
        
        await update.message.reply_text(report, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error in /autofix_history: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error loading history: {str(e)[:100]}",
            parse_mode="HTML"
        )


async def handle_autofix_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: /autofix_reset
    
    Reset all auto-fix metrics (requires confirmation).
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return
    
    # Require confirmation: /autofix_reset CONFIRM
    if not context.args or context.args[0] != "CONFIRM":
        await update.message.reply_text(
            "⚠️ <b>Reset Auto-Fix Metrics?</b>\n\n"
            "This will delete all metrics history.\n\n"
            "To confirm, send:\n"
            "<code>/autofix_reset CONFIRM</code>",
            parse_mode="HTML"
        )
        return
    
    try:
        from bot.core.autofix_metrics import get_metrics
        from pathlib import Path
        
        metrics = get_metrics()
        
        # Clear in-memory data
        metrics.handler_stats.clear()
        metrics.fix_history.clear()
        
        # Delete metrics file
        metrics_file = Path("data/metrics/autofix_metrics.json")
        if metrics_file.exists():
            metrics_file.unlink()
        
        logger.warning(f"Admin {user_id} reset auto-fix metrics")
        
        await update.message.reply_text(
            "✅ Auto-fix metrics reset successfully.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in /autofix_reset: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error resetting metrics: {str(e)[:100]}",
            parse_mode="HTML"
        )


def register_autofix_admin_handlers(application, group: int = -10):
    """Register auto-fix admin command handlers."""
    application.add_handler(CommandHandler("autofix_stats", handle_autofix_stats), group=group)
    application.add_handler(CommandHandler("autofix_history", handle_autofix_history), group=group)
    application.add_handler(CommandHandler("autofix_reset", handle_autofix_reset), group=group)
    logger.info(f"✅ Auto-fix admin handlers registered (group={group})")
