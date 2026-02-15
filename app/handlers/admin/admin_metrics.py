"""
Admin Metrics Dashboard Handler
Telegram commands for viewing Phase 2 metrics
Admin only - requires settings.ADMIN_USER_ID
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from loguru import logger
from config.settings import settings
from app.services.metrics_service import metrics_service


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == settings.ADMIN_USER_ID


async def admin_metrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_metrics - View Phase 2 dashboard (6 metrics)
    Admin only command
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    logger.info(f"📊 Admin {user_id} requested metrics dashboard")
    
    # Show loading message
    loading_msg = await update.message.reply_text("⏳ Đang tính toán metrics...")
    
    try:
        # Get metrics (force fresh calculation)
        force_refresh = '--refresh' in (context.args or [])
        metrics = metrics_service.get_all_metrics(force_refresh=force_refresh)
        
        # Format message
        message = metrics_service.format_telegram_message(metrics)
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="admin_metrics_refresh"),
                InlineKeyboardButton("📊 Google Sheets", url="https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit")
            ],
            [
                InlineKeyboardButton("📅 Weekly View", callback_data="admin_metrics_week"),
                InlineKeyboardButton("💾 Export CSV", callback_data="admin_metrics_export")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Delete loading message
        await loading_msg.delete()
        
        # Send metrics
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        
        logger.info(f"✅ Metrics sent to admin {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error calculating metrics: {e}", exc_info=True)
        await loading_msg.edit_text(
            f"❌ Lỗi khi tính toán metrics:\n\n<code>{str(e)}</code>",
            parse_mode="HTML"
        )


async def admin_metrics_week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_metrics_week - View weekly summary
    Admin only command
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    logger.info(f"📅 Admin {user_id} requested weekly summary")
    
    # TODO: Implement weekly summary view
    # For now, redirect to daily view
    await update.message.reply_text(
        "📅 <b>Weekly Summary</b>\n\n"
        "Tính năng này đang được phát triển.\n"
        "Hiện tại vui lòng xem dashboard hàng ngày với /admin_metrics\n\n"
        "Hoặc truy cập Google Sheets để xem weekly summary:\n"
        "https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


async def admin_metrics_export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_metrics_export - Export metrics to CSV
    Admin only command
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    logger.info(f"💾 Admin {user_id} requested CSV export")
    
    # TODO: Implement CSV export
    # For now, provide instructions
    await update.message.reply_text(
        "💾 <b>Export Metrics</b>\n\n"
        "Để export dữ liệu, vui lòng:\n\n"
        "1. Truy cập Google Sheets:\n"
        "https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit\n\n"
        "2. Click File → Download → CSV\n\n"
        "3. Chọn sheet cần export:\n"
        "   • Sheet 1: Daily Metrics\n"
        "   • Sheet 5: Weekly Summary\n"
        "   • Sheet 6: Raw Data Log\n\n"
        "⚠️ Tự động export qua Telegram sẽ được thêm trong Phase 2.",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


async def admin_metrics_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_metrics_reset - Clear metrics cache
    Admin only command (use with caution)
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    logger.warning(f"🔄 Admin {user_id} requested cache reset")
    
    try:
        # Clear cache
        metrics_service.cache.clear()
        
        await update.message.reply_text(
            "✅ <b>Cache Cleared</b>\n\n"
            "Metrics cache đã được xóa.\n"
            "Lần tính toán tiếp theo sẽ lấy dữ liệu mới từ database.\n\n"
            "Dùng /admin_metrics để xem metrics mới.",
            parse_mode="HTML"
        )
        
        logger.info(f"✅ Cache cleared by admin {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Lỗi khi xóa cache:\n\n<code>{str(e)}</code>",
            parse_mode="HTML"
        )


def register_admin_metrics_handlers(application):
    """Register all admin metrics handlers"""
    logger.info("📊 Registering admin metrics handlers...")
    
    application.add_handler(CommandHandler("admin_metrics", admin_metrics_command))
    application.add_handler(CommandHandler("admin_metrics_week", admin_metrics_week_command))
    application.add_handler(CommandHandler("admin_metrics_export", admin_metrics_export_command))
    application.add_handler(CommandHandler("admin_metrics_reset", admin_metrics_reset_command))
    
    logger.info("✅ Admin metrics handlers registered")

