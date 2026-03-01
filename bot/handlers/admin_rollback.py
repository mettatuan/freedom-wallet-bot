"""
Admin Commands for Rollback System
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from loguru import logger
from config.settings import settings


async def handle_rollback_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: /rollback_status
    
    Show rollback system status and recent history.
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return
    
    try:
        from bot.core.rollback_system import get_rollback_system
        
        rollback_system = get_rollback_system()
        
        # Current config
        status = "✅ Enabled" if rollback_system.enabled else "⏸️ Disabled"
        
        lines = [
            "🔄 <b>AUTO-ROLLBACK STATUS</b>\n",
            f"<b>Status:</b> {status}",
            f"<b>Monitoring Window:</b> {rollback_system.monitoring_window_minutes} minutes",
            f"<b>Error Rate Threshold:</b> {rollback_system.error_rate_threshold}x",
            f"<b>Response Time Threshold:</b> {rollback_system.response_time_threshold}x",
            f"<b>Critical Error Threshold:</b> {rollback_system.critical_error_threshold}",
            f"\n<b>Current Commit:</b> <code>{rollback_system.get_current_commit()}</code>",
            f"<b>Snapshots Stored:</b> {len(rollback_system.snapshots)}",
        ]
        
        # Recent rollbacks
        if rollback_system.rollback_history:
            lines.append("\n<b>📜 Recent Rollbacks:</b>")
            for entry in rollback_system.rollback_history[-5:]:
                from datetime import datetime
                timestamp = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
                status_icon = "✅" if entry.get("success", False) else "❌"
                lines.append(
                    f"{status_icon} {timestamp}\n"
                    f"   → <code>{entry['to_commit']}</code>\n"
                    f"   Reason: {entry['reason'][:80]}"
                )
        else:
            lines.append("\n✅ No rollbacks yet")
        
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")
    
    except Exception as e:
        logger.error(f"Error in /rollback_status: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Error: {str(e)[:100]}",
            parse_mode="HTML"
        )


async def handle_rollback_enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: /rollback_enable
    
    Enable auto-rollback system.
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return
    
    try:
        from bot.core.rollback_system import get_rollback_system
        
        rollback_system = get_rollback_system()
        rollback_system.enabled = True
        rollback_system._save_to_disk()
        
        logger.info(f"Admin {user_id} enabled auto-rollback")
        await update.message.reply_text(
            "✅ Auto-rollback system <b>ENABLED</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in /rollback_enable: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")


async def handle_rollback_disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: /rollback_disable
    
    Disable auto-rollback system.
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return
    
    try:
        from bot.core.rollback_system import get_rollback_system
        
        rollback_system = get_rollback_system()
        rollback_system.enabled = False
        rollback_system._save_to_disk()
        
        logger.warning(f"Admin {user_id} disabled auto-rollback")
        await update.message.reply_text(
            "⏸️ Auto-rollback system <b>DISABLED</b>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in /rollback_disable: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")


async def handle_rollback_snapshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: /rollback_snapshot
    
    Manually create health snapshot.
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return
    
    try:
        from bot.core.rollback_system import get_rollback_system
        
        rollback_system = get_rollback_system()
        snapshot = rollback_system.create_snapshot()
        
        await update.message.reply_text(
            f"📸 <b>Health Snapshot Created</b>\n\n"
            f"Commit: <code>{snapshot.git_commit}</code>\n"
            f"Errors (5min): {snapshot.error_count}\n"
            f"Critical: {snapshot.critical_error_count}\n"
            f"Timestamp: {snapshot.timestamp:.0f}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in /rollback_snapshot: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")


async def handle_rollback_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin command: /rollback_now <commit>
    
    Manually trigger rollback to specific commit.
    Requires confirmation.
    """
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ <b>Manual Rollback</b>\n\n"
            "Usage: <code>/rollback_now &lt;commit_hash&gt; CONFIRM</code>\n\n"
            "Example:\n"
            "<code>/rollback_now abc123 CONFIRM</code>",
            parse_mode="HTML"
        )
        return
    
    target_commit = context.args[0]
    
    # Require CONFIRM keyword
    if len(context.args) < 2 or context.args[1] != "CONFIRM":
        await update.message.reply_text(
            f"⚠️ <b>Rollback to <code>{target_commit}</code>?</b>\n\n"
            f"This will reset code and restart bot.\n\n"
            f"To confirm, send:\n"
            f"<code>/rollback_now {target_commit} CONFIRM</code>",
            parse_mode="HTML"
        )
        return
    
    try:
        from bot.core.rollback_system import get_rollback_system
        
        rollback_system = get_rollback_system()
        
        await update.message.reply_text(
            f"🔄 Rolling back to <code>{target_commit}</code>...",
            parse_mode="HTML"
        )
        
        success = await rollback_system.execute_rollback(
            target_commit,
            f"Manual rollback by admin {user_id}"
        )
        
        if success:
            await update.message.reply_text(
                "✅ Rollback successful! Bot will restart...",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                "❌ Rollback failed! Check logs for details.",
                parse_mode="HTML"
            )
    
    except Exception as e:
        logger.error(f"Error in /rollback_now: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Rollback failed: {str(e)[:100]}",
            parse_mode="HTML"
        )


def register_rollback_admin_handlers(application, group: int = -10):
    """Register rollback admin command handlers."""
    application.add_handler(CommandHandler("rollback_status", handle_rollback_status), group=group)
    application.add_handler(CommandHandler("rollback_enable", handle_rollback_enable), group=group)
    application.add_handler(CommandHandler("rollback_disable", handle_rollback_disable), group=group)
    application.add_handler(CommandHandler("rollback_snapshot", handle_rollback_snapshot), group=group)
    application.add_handler(CommandHandler("rollback_now", handle_rollback_now), group=group)
    logger.info(f"✅ Rollback admin handlers registered (group={group})")
