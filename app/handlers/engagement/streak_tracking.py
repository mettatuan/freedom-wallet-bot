"""
Streak Tracking System - Theo dÃµi vÃ  cáº­p nháº­t streak
PhÃ¡t hiá»‡n khi user ghi giao dá»‹ch vÃ  update streak
"""
from loguru import logger
from datetime import datetime, timedelta
from app.utils.database import SessionLocal, User
from app.handlers.celebration import check_and_celebrate_milestone
from app.handlers.daily_reminder import send_skip_alert


def record_transaction_event(user_id: int, context=None):
    """
    Record that user made a transaction
    Updates streak and checks for milestones
    
    Call this function whenever user records a transaction in Web App
    Can be triggered via:
    - Webhook from Google Sheets
    - Manual /record_transaction command
    - API callback
    """
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"User {user_id} not found for transaction event")
            db.close()
            return
        
        today = datetime.utcnow().date()
        last_transaction = user.last_transaction_date
        
        # Check if already recorded today
        if last_transaction and last_transaction.date() == today:
            # Already recorded today, just increment total
            user.total_transactions += 1
            db.commit()
            db.close()
            logger.info(f"User {user_id} recorded another transaction today (total: {user.total_transactions})")
            return
        
        # Check streak continuity
        if last_transaction:
            yesterday = today - timedelta(days=1)
            
            if last_transaction.date() == yesterday:
                # Consecutive day! Increment streak
                user.streak_count += 1
                logger.info(f"User {user_id} streak increased to {user.streak_count}")
            elif last_transaction.date() < yesterday:
                # Missed days, reset streak
                missed_days = (today - last_transaction.date()).days
                logger.info(f"User {user_id} missed {missed_days} days, resetting streak")
                
                # Send skip alert if context available
                if context and missed_days >= 2:
                    context.application.create_task(
                        send_skip_alert(context, user_id, missed_days)
                    )
                
                user.streak_count = 1  # Start fresh
            # If same day (already handled above), do nothing
        else:
            # First transaction ever
            user.streak_count = 1
            logger.info(f"User {user_id} recorded first transaction, streak = 1")
        
        # Update longest streak
        if user.streak_count > (user.longest_streak or 0):
            user.longest_streak = user.streak_count
        
        # Update transaction date and count
        user.last_transaction_date = datetime.utcnow()
        user.total_transactions += 1
        
        # Commit changes
        db.commit()
        
        # Check for milestone celebrations
        if context:
            check_and_celebrate_milestone(user, context)
        
        db.close()
        
        logger.info(
            f"Transaction recorded for user {user_id}: "
            f"streak={user.streak_count}, total={user.total_transactions}"
        )
        
    except Exception as e:
        logger.error(f"Error recording transaction event for user {user_id}: {e}")


def check_missed_days():
    """
    Check all users for missed recording days
    Run this daily to detect users who need reminders
    
    Should be scheduled to run at 9 PM daily
    """
    try:
        db = SessionLocal()
        
        # Get all active VIP users
        users = db.query(User).filter(
            User.user_state.in_(["VIP", "SUPER_VIP"]),
            User.reminder_enabled == True
        ).all()
        
        today = datetime.utcnow().date()
        
        for user in users:
            if not user.last_transaction_date:
                continue
            
            last_transaction = user.last_transaction_date.date()
            days_since_last = (today - last_transaction).days
            
            # If missed 2+ days and still has streak, break it
            if days_since_last >= 2 and user.streak_count > 0:
                logger.warning(
                    f"User {user.id} missed {days_since_last} days, "
                    f"breaking streak {user.streak_count}"
                )
                user.streak_count = 0
        
        db.commit()
        db.close()
        
        logger.info("Completed daily missed days check")
        
    except Exception as e:
        logger.error(f"Error checking missed days: {e}")


def get_user_streak_stats(user_id: int) -> dict:
    """
    Get streak statistics for a user
    Returns dict with streak info
    """
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return None
        
        today = datetime.utcnow().date()
        last_transaction = user.last_transaction_date
        
        stats = {
            "user_id": user.id,
            "user_name": user.full_name or user.first_name,
            "current_streak": user.streak_count or 0,
            "longest_streak": user.longest_streak or 0,
            "total_transactions": user.total_transactions or 0,
            "last_transaction_date": last_transaction.strftime("%Y-%m-%d") if last_transaction else None,
            "recorded_today": last_transaction and last_transaction.date() == today,
            "milestones": {
                "7_days": user.milestone_7day_achieved,
                "30_days": user.milestone_30day_achieved,
                "90_days": user.milestone_90day_achieved
            }
        }
        
        db.close()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting streak stats for user {user_id}: {e}")
        return None


def reset_user_streak(user_id: int):
    """
    Manually reset a user's streak
    Use with caution - should only be for corrections
    """
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return False
        
        user.streak_count = 0
        db.commit()
        db.close()
        
        logger.info(f"Manually reset streak for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error resetting streak for user {user_id}: {e}")
        return False


def toggle_reminder(user_id: int, enabled: bool) -> bool:
    """Toggle reminder on/off for a user"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return False
        
        user.reminder_enabled = enabled
        db.commit()
        db.close()
        
        status = "enabled" if enabled else "disabled"
        logger.info(f"Reminder {status} for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error toggling reminder for user {user_id}: {e}")
        return False

