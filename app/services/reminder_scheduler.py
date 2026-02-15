"""
Daily Reminder Scheduler - Schedule morning and evening reminders
Runs independently from 7-day programs
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime, timedelta
from app.utils.database import SessionLocal, User
from app.services.messaging_service import send_morning_reminder, send_evening_reminder
from app.services.streak_service import check_missed_days


class DailyReminderScheduler:
    """
    Manages daily reminder schedules for all VIP users
    
    Schedules:
    - Morning reminder: 8:00 AM daily
    - Evening reminder: 8:00 PM daily  
    - Missed days check: 9:00 PM daily
    """
    
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler
        logger.info("Daily Reminder Scheduler initialized")
    
    def start_daily_reminders(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Start global daily reminder jobs
        Runs for all VIP users automatically
        """
        # Morning reminder - 8:00 AM daily
        self.scheduler.add_job(
            func=self._send_all_morning_reminders,
            trigger=CronTrigger(hour=8, minute=0),
            args=[context],
            id="daily_morning_reminder",
            replace_existing=True,
            name="Daily Morning Motivation (8:00 AM)"
        )
        logger.info("✅ Scheduled morning reminders at 8:00 AM daily")
        
        # Evening reminder - 8:00 PM daily
        self.scheduler.add_job(
            func=self._send_all_evening_reminders,
            trigger=CronTrigger(hour=20, minute=0),
            args=[context],
            id="daily_evening_reminder",
            replace_existing=True,
            name="Daily Evening Check-in (8:00 PM)"
        )
        logger.info("✅ Scheduled evening reminders at 8:00 PM daily")
        
        # Missed days check - 9:00 PM daily
        self.scheduler.add_job(
            func=check_missed_days,
            trigger=CronTrigger(hour=21, minute=0),
            id="daily_missed_days_check",
            replace_existing=True,
            name="Daily Missed Days Check (9:00 PM)"
        )
        logger.info("✅ Scheduled missed days check at 9:00 PM daily")
    
    async def _send_all_morning_reminders(self, context: ContextTypes.DEFAULT_TYPE):
        """Send morning reminders to all eligible users"""
        try:
            db = SessionLocal()
            
            # Get all VIP users with reminders enabled
            users = db.query(User).filter(
                User.user_state.in_(["VIP", "SUPER_VIP"]),
                User.reminder_enabled == True
            ).all()
            
            logger.info(f"Sending morning reminders to {len(users)} users")
            
            for user in users:
                try:
                    await send_morning_reminder(context, user.id)
                except Exception as e:
                    logger.error(f"Failed to send morning reminder to {user.id}: {e}")
            
            db.close()
            logger.info(f"✅ Completed morning reminders for {len(users)} users")
            
        except Exception as e:
            logger.error(f"Error in morning reminder batch: {e}")
    
    async def _send_all_evening_reminders(self, context: ContextTypes.DEFAULT_TYPE):
        """Send evening reminders to all eligible users"""
        try:
            db = SessionLocal()
            
            # Get all VIP users with reminders enabled
            users = db.query(User).filter(
                User.user_state.in_(["VIP", "SUPER_VIP"]),
                User.reminder_enabled == True
            ).all()
            
            logger.info(f"Sending evening reminders to {len(users)} users")
            
            for user in users:
                try:
                    await send_evening_reminder(context, user.id)
                except Exception as e:
                    logger.error(f"Failed to send evening reminder to {user.id}: {e}")
            
            db.close()
            logger.info(f"✅ Completed evening reminders for {len(users)} users")
            
        except Exception as e:
            logger.error(f"Error in evening reminder batch: {e}")
    
    def enable_reminders_for_user(self, user_id: int):
        """Enable daily reminders for a specific user (called when user becomes VIP)"""
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                db.close()
                return False
            
            user.reminder_enabled = True
            db.commit()
            db.close()
            
            logger.info(f"✅ Enabled daily reminders for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling reminders for user {user_id}: {e}")
            return False
    
    def disable_reminders_for_user(self, user_id: int):
        """Disable daily reminders for a specific user"""
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                db.close()
                return False
            
            user.reminder_enabled = False
            db.commit()
            db.close()
            
            logger.info(f"🔕 Disabled daily reminders for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling reminders for user {user_id}: {e}")
            return False


# Global instance
_reminder_scheduler = None

def get_reminder_scheduler(scheduler: AsyncIOScheduler = None) -> DailyReminderScheduler:
    """Get or create reminder scheduler instance"""
    global _reminder_scheduler
    if _reminder_scheduler is None and scheduler:
        _reminder_scheduler = DailyReminderScheduler(scheduler)
    return _reminder_scheduler

