"""
Daily Background Jobs (Week 4)

Scheduled tasks that run periodically:
- Super VIP decay monitoring (daily at 10 AM UTC)
- Future: Analytics reports, cleanup tasks, etc.
"""
from telegram.ext import ContextTypes
from loguru import logger
from app.core.state_machine import StateManager
from app.utils.database import SessionLocal, User
from datetime import datetime


async def check_super_vip_decay_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Daily job to check Super VIP users for inactivity
    
    Runs every day at 10:00 AM UTC
    - Warns users after 7 days inactive
    - Downgrades users after 14 days inactive
    """
    logger.info("🔍 Running Super VIP decay check...")
    
    try:
        with StateManager() as sm:
            decay_results = sm.check_all_super_vip_decay()
            
            if not decay_results:
                logger.info("✅ No Super VIP decay actions needed")
                return
            
            # Process each decay action
            for result in decay_results:
                user_id = result['user_id']
                action = result['action']
                days = result['days_inactive']
                username = result.get('username', 'Unknown')
                
                try:
                    if action == 'warn':
                        # Send warning message
                        await send_decay_warning(user_id, days, context)
                        logger.info(f"⚠️ Sent decay warning to {username} ({user_id}) - {days} days inactive")
                    
                    elif action == 'downgrade':
                        # Send downgrade notification
                        await send_downgrade_notification(user_id, days, context)
                        logger.info(f"🔻 Downgraded {username} ({user_id}) to VIP - {days} days inactive")
                
                except Exception as e:
                    logger.error(f"Failed to process decay for user {user_id}: {e}")
            
            logger.info(f"✅ Super VIP decay check complete: {len(decay_results)} actions processed")
    
    except Exception as e:
        logger.error(f"❌ Super VIP decay job failed: {e}")
        import traceback
        traceback.print_exc()


async def send_decay_warning(user_id: int, days_inactive: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Send warning message to Super VIP user about inactivity
    
    Sent after 7 days of inactivity
    """
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🏠 Vào Dashboard", callback_data="start")],
        [InlineKeyboardButton("🔗 Chia sẻ link", callback_data="referral_menu")],
        [InlineKeyboardButton("💬 Chat với Admin", callback_data="contact_support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=user_id,
        text=f"━━━━━━━━━━━━━━━━━━━━━\n"
             f"⚠️ **LƯU Ý QUAN TRỌNG**\n"
             f"━━━━━━━━━━━━━━━━━━━━━\n\n"
             f"👋 Chào bạn!\n\n"
             f"Mình thấy bạn chưa hoạt động trong **{days_inactive} ngày**.\n\n"
             f"🌟 **Để giữ danh hiệu Super VIP:**\n"
             f"• Bạn cần duy trì hoạt động thường xuyên\n"
             f"• Nếu không hoạt động trong **14 ngày**, danh hiệu sẽ bị thu hồi\n"
             f"• Còn **{14 - days_inactive} ngày** để giữ Super VIP\n\n"
             f"💡 **Cách duy trì hoạt động:**\n"
             f"✓ Chia sẻ link giới thiệu\n"
             f"✓ Tham gia Group Super VIP\n"
             f"✓ Sử dụng bot thường xuyên\n"
             f"✓ Tương tác với Dashboard\n\n"
             f"━━━━━━━━━━━━━━━━━━━━━\n"
             f"🤝 Chúng mình muốn bạn tiếp tục là Super VIP!\n"
             f"Hãy quay lại hoạt động để giữ đặc quyền nhé!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def send_downgrade_notification(user_id: int, days_inactive: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Send notification when Super VIP is downgraded to VIP
    
    Sent after 14 days of inactivity
    """
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🏠 Dashboard", callback_data="start")],
        [InlineKeyboardButton("🔗 Xem link giới thiệu", callback_data="referral_menu")],
        [InlineKeyboardButton("🌟 Làm sao để lên lại Super VIP?", callback_data="super_vip_benefits")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=user_id,
        text=f"━━━━━━━━━━━━━━━━━━━━━\n"
             f"📢 **THÔNG BÁO QUAN TRỌNG**\n"
             f"━━━━━━━━━━━━━━━━━━━━━\n\n"
             f"Xin chào! 👋\n\n"
             f"Do bạn đã không hoạt động trong **{days_inactive} ngày**,\n"
             f"danh hiệu **Super VIP** của bạn đã được chuyển về **VIP**.\n\n"
             f"⭐ **Bạn vẫn là VIP với đầy đủ quyền lợi:**\n"
             f"✓ Toàn bộ tính năng Freedom Wallet\n"
             f"✓ Templates & Scripts\n"
             f"✓ Group hỗ trợ VIP\n"
             f"✓ Cập nhật miễn phí\n\n"
             f"🌟 **Muốn lên lại Super VIP?**\n"
             f"• Tiếp tục giới thiệu thêm bạn bè\n"
             f"• Duy trì hoạt động thường xuyên\n"
             f"• Khi đạt 50+ refs và active → Auto lên Super VIP\n\n"
             f"━━━━━━━━━━━━━━━━━━━━━\n"
             f"💙 Cảm ơn bạn đã đồng hành cùng Freedom Wallet!\n"
             f"Chúng mình luôn chào đón bạn quay lại! 🙏",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


def setup_daily_jobs(application):
    """
    Setup all daily scheduled jobs
    
    Call this in main.py after creating the application
    
    Usage:
        from app.jobs.daily_tasks import setup_daily_jobs
        setup_daily_jobs(application)
    """
    from telegram.ext import JobQueue
    from app.services.reminder_scheduler import get_reminder_scheduler
    
    job_queue = application.job_queue
    
    if not job_queue:
        logger.warning("JobQueue not available, daily tasks cannot be scheduled")
        return
    
    # Super VIP decay check - Daily at 10:00 AM UTC
    job_queue.run_daily(
        check_super_vip_decay_job,
        time=datetime.strptime("10:00", "%H:%M").time(),
        name="super_vip_decay_check"
    )
    
    # Initialize daily reminder scheduler (Week 6)
    reminder_scheduler = get_reminder_scheduler(job_queue.scheduler)
    if reminder_scheduler:
        reminder_scheduler.start_daily_reminders(application)
        logger.info("✅ Daily reminder system initialized")
    
    logger.info("✅ Daily jobs scheduled:")
    logger.info("   - Super VIP decay check: 10:00 AM UTC")
    logger.info("   - Morning reminders: 8:00 AM daily")
    logger.info("   - Evening reminders: 8:00 PM daily")
    logger.info("   - Missed days check: 9:00 PM daily")
    
    # Future jobs can be added here:
    # - Analytics reports
    # - Cleanup tasks
    # - Backup tasks
    # etc.

