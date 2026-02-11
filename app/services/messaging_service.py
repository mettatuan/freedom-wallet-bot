"""
Messaging Service - Send programmatic messages to users

This service contains functions that send messages to users outside of
the normal request/response flow (e.g., scheduled reminders, program messages).

Pattern: Schedulers/Jobs → Messaging Service → Telegram API
"""
from datetime import datetime
from telegram.ext import ContextTypes
from loguru import logger
from app.utils.database import SessionLocal, User


async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """
    Send morning reminder to a specific user.
    Called by reminder_scheduler.py
    """
    from app.messages.reminder_messages import MORNING_REMINDER_TEMPLATE, get_streak_message
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return
            
        # Calculate streak & get message
        streak = user.streak_days or 0
        streak_message = get_streak_message(streak)
        
        message = MORNING_REMINDER_TEMPLATE.format(
            name=user.name or "bạn",
            streak=streak + 1,
            streak_message=streak_message
        )
        
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Morning reminder sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending morning reminder to {user_id}: {e}")
    finally:
        db.close()


async def send_evening_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """
    Send evening reminder to a specific user.
    Called by reminder_scheduler.py
    """
    from app.messages.reminder_messages import EVENING_REMINDER_TEMPLATE
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return
            
        streak = user.streak_days or 0
        
        # Check if user recorded today
        today = datetime.now().date()
        last_record = user.last_record_date
        recorded_today = last_record and last_record == today
        
        if recorded_today:
            streak_status = f"✅ **Đã ghi {user.today_record_count or 0} giao dịch** - Tuyệt vời!"
        else:
            streak_status = f"⚠️ **Chưa ghi chép gì** - Chuỗi {streak} ngày sắp mất!"
        
        message = EVENING_REMINDER_TEMPLATE.format(
            name=user.name or "bạn",
            streak_status=streak_status
        )
        
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Evening reminder sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending evening reminder to {user_id}: {e}")
    finally:
        db.close()


async def send_program_message(context: ContextTypes.DEFAULT_TYPE, user_id: int, message: str):
    """
    Send a program/nurture message to a specific user.
    Called by program_manager.py
    """
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='Markdown'
        )
        logger.info(f"Program message sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending program message to {user_id}: {e}")
