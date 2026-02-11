"""
Streak Service - Manage user streaks and missed days
"""
from datetime import datetime
from loguru import logger
from app.utils.database import SessionLocal, User


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
        
        logger.info("✅ Completed daily missed days check")
        
    except Exception as e:
        logger.error(f"❌ Error checking missed days: {e}")
