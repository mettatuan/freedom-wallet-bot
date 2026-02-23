"""
User Commands - Các lệnh user có thể sử dụng
/stats, /reminder_on, /reminder_off, /record_transaction
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from loguru import logger
from bot.handlers.streak_tracking import get_user_streak_stats, toggle_reminder, record_transaction_event
from bot.utils.database import run_sync


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's streak statistics"""
    user_id = update.effective_user.id
    
    stats = await run_sync(get_user_streak_stats, user_id)
    
    if not stats:
        await update.message.reply_text(
            "❌ Không tìm thấy thông tin của bạn.\n"
            "Vui lòng đăng ký trước: /start"
        )
        return
    
    message = f"""
📊 **THỐNG KÊ GHI CHÉP - {stats['user_name'].upper()}**

━━━━━━━━━━━━━━━━━━━━━

🔥 **STREAK HIỆN TẠI:**
{stats['current_streak']} ngày liên tục

🏆 **STREAK DÀI NHẤT:**
{stats['longest_streak']} ngày

📝 **TỔNG GIAO DỊCH:**
{stats['total_transactions']} giao dịch

📅 **GHI CHÉP GẦN NHẤT:**
{stats['last_transaction_date'] or 'Chưa có'}

━━━━━━━━━━━━━━━━━━━━━

✨ **MILESTONES:**
• 7 ngày: {'✅ Đạt rồi!' if stats['milestones']['7_days'] else '⏳ Chưa đạt'}
• 30 ngày: {'✅ Đạt rồi!' if stats['milestones']['30_days'] else '⏳ Chưa đạt'}
• 90 ngày: {'✅ Đạt rồi!' if stats['milestones']['90_days'] else '⏳ Chưa đạt'}

━━━━━━━━━━━━━━━━━━━━━

{'✅ **Đã ghi chép hôm nay!**' if stats['recorded_today'] else '⚠️ **Chưa ghi chép hôm nay!**'}

💡 *Ghi chép đều đặn để giữ streak!*
"""
    
    await update.message.reply_text(message, parse_mode="Markdown")
    logger.info(f"Showed stats for user {user_id}")


async def reminder_on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable daily reminders"""
    user_id = update.effective_user.id
    
    success = await run_sync(toggle_reminder, user_id, True)
    
    if success:
        await update.message.reply_text(
            "✅ **Đã bật nhắc nhở hàng ngày!**\n\n"
            "Bạn sẽ nhận được:\n"
            "• Nhắc nhở sáng (8:00 AM)\n"
            "• Nhắc nhở tối (8:00 PM)\n\n"
            "💡 *Tắt bất cứ lúc nào: /reminder_off*",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ Không thể bật nhắc nhở.\n"
            "Vui lòng liên hệ support."
        )


async def reminder_off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disable daily reminders"""
    user_id = update.effective_user.id
    
    success = await run_sync(toggle_reminder, user_id, False)
    
    if success:
        await update.message.reply_text(
            "🔕 **Đã tắt nhắc nhở hàng ngày.**\n\n"
            "Bạn sẽ không nhận thông báo tự động nữa.\n\n"
            "💡 *Bật lại bất cứ lúc nào: /reminder_on*",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ Không thể tắt nhắc nhở.\n"
            "Vui lòng liên hệ support."
        )


async def record_transaction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually record that user made a transaction (for testing/manual entry)"""
    user_id = update.effective_user.id
    
    # Record transaction event
    await run_sync(record_transaction_event, user_id, context)
    
    # Get updated stats
    stats = await run_sync(get_user_streak_stats, user_id)
    
    if stats:
        await update.message.reply_text(
            f"✅ **Đã ghi nhận giao dịch!**\n\n"
            f"🔥 Streak hiện tại: **{stats['current_streak']} ngày**\n"
            f"📝 Tổng giao dịch: {stats['total_transactions']}\n\n"
            f"💡 *Tiếp tục giữ streak nhé!*",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("✅ Đã ghi nhận!")
    
    logger.info(f"Manually recorded transaction for user {user_id}")


def register_user_command_handlers(application):
    """Register user command handlers"""
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("reminder_on", reminder_on_command))
    application.add_handler(CommandHandler("reminder_off", reminder_off_command))
    application.add_handler(CommandHandler("record_transaction", record_transaction_command))
    
    logger.info("✅ User command handlers registered")
