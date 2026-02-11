"""
Trial Churn Prevention - Remind users before trial ends

Goal: Reduce trial->cancellation rate
Triggers: Day 6 of 7-day trial (24h before expiry)
"""
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal, User
from app.core.subscription import SubscriptionManager, SubscriptionTier
from app.services.roi_calculator import ROICalculator
from app.services.analytics import Analytics
from loguru import logger
from config.settings import settings


class TrialChurnPrevention:
    """Service for preventing trial churn"""
    
    @staticmethod
    async def send_trial_day6_reminder(user_id: int):
        """Send reminder 24h before trial ends"""
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.warning(f"User {user_id} not found for trial reminder")
                return
            
            # Verify user is still on trial
            tier = SubscriptionManager.get_user_tier(user)
            if tier != SubscriptionTier.TRIAL:
                logger.info(f"User {user_id} no longer on trial, skipping reminder")
                return
            
            # Calculate ROI for the trial period
            roi = ROICalculator.calculate_monthly_roi(user_id, db)
            
            # Craft compelling message
            trial_end = user.trial_ends_at.strftime("%d/%m/%Y %H:%M") if user.trial_ends_at else "N/A"
            
            message = f"""
â° **TRIAL Káº¾T THÃšC SAU 24H!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸŽ¯ **7 NGÃ€Y TRIAL Cá»¦A Báº N:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“… Káº¿t thÃºc: {trial_end}
â³ CÃ²n láº¡i: **24 giá»**

{ROICalculator.format_roi_message(roi, "TRIAL")}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’Ž **Náº¾U TIáº¾P Tá»¤C PREMIUM:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… Unlimited tin nháº¯n (khÃ´ng giá»›i háº¡n)
âœ… AI phÃ¢n tÃ­ch tÃ i chÃ­nh 24/7
âœ… Dashboard thÃ´ng minh
âœ… Gá»£i Ã½ cÃ¡ nhÃ¢n hÃ³a má»—i ngÃ y
âœ… Há»— trá»£ Æ°u tiÃªn 30 phÃºt
âœ… Web App khÃ´ng quáº£ng cÃ¡o

ðŸ’° **GiÃ¡:** 999,000 VNÄ/nÄƒm (~2,750 VNÄ/ngÃ y)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ”„ **Náº¾U KHÃ”NG TIáº¾P Tá»¤C:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

Sau 24h, báº¡n sáº½ quay vá» FREE:
â€¢ Chá»‰ 5 tin nháº¯n/ngÃ y
â€¢ KhÃ´ng cÃ³ phÃ¢n tÃ­ch AI
â€¢ KhÃ´ng gá»£i Ã½ cÃ¡ nhÃ¢n
â€¢ Dashboard bá»‹ khÃ³a

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ **QUYáº¾T Äá»ŠNH NGAY:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ‘‡ Chá»n hÃ nh Ä‘á»™ng bÃªn dÆ°á»›i:
"""
            
            # Action buttons
            keyboard = [
                [InlineKeyboardButton("ðŸ’Ž NÃ¢ng cáº¥p Premium ngay", callback_data="upgrade_to_premium")],
                [InlineKeyboardButton("ðŸ“Š Xem ROI chi tiáº¿t", callback_data="view_roi_detail")],
                [InlineKeyboardButton("ðŸ¤” Táº¡i sao nÃªn Premium?", callback_data="why_premium")],
                [InlineKeyboardButton("ðŸ’¬ Chat vá»›i Support", callback_data="contact_support")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            # Track event
            Analytics.track_event(user_id, 'trial_reminder_sent', {
                'roi_percent': roi.get('roi_percent', 0),
                'messages': roi.get('messages', 0)
            })
            
            logger.info(f"Sent trial day-6 reminder to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending trial reminder to {user_id}: {e}")
        finally:
            db.close()
    
    @staticmethod
    async def send_trial_ended_notification(user_id: int):
        """Send notification when trial has ended"""
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return
            
            message = """
â° **TRIAL ÄÃƒ Káº¾T THÃšC**

Cáº£m Æ¡n báº¡n Ä‘Ã£ tráº£i nghiá»‡m Premium Trial 7 ngÃ y! ðŸ™

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ†“ **TÃ€I KHOáº¢N FREE:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

Báº¡n Ä‘Ã£ quay vá» tÃ i khoáº£n FREE:
â€¢ 5 tin nháº¯n/ngÃ y vá»›i bot
â€¢ Truy cáº­p Web App cÆ¡ báº£n
â€¢ Há»— trá»£ cá»™ng Ä‘á»“ng

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’Ž **MUá»N QUAY Láº I PREMIUM?**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

NÃ¢ng cáº¥p báº¥t cá»© lÃºc nÃ o:
ðŸ’° 999,000 VNÄ/nÄƒm
âš¡ KÃ­ch hoáº¡t ngay láº­p tá»©c

GÃµ /upgrade Ä‘á»ƒ xem chi tiáº¿t!
"""
            
            keyboard = [
                [InlineKeyboardButton("ðŸ’Ž NÃ¢ng cáº¥p Premium", callback_data="upgrade_to_premium")],
                [InlineKeyboardButton("ðŸ  Menu FREE", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
            logger.info(f"Sent trial ended notification to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending trial ended notification to {user_id}: {e}")
        finally:
            db.close()


def schedule_trial_reminder_job(user_id: int, trial_end_date: datetime, scheduler):
    """Schedule trial day-6 reminder (24h before end)"""
    
    # Calculate reminder time (24h before trial ends)
    reminder_time = trial_end_date - timedelta(hours=24)
    
    # Only schedule if reminder time is in the future
    if reminder_time > datetime.now():
        scheduler.add_job(
            TrialChurnPrevention.send_trial_day6_reminder,
            'date',
            run_date=reminder_time,
            args=[user_id],
            id=f"trial_reminder_{user_id}_{int(datetime.now().timestamp())}",
            replace_existing=True
        )
        
        logger.info(f"Scheduled trial day-6 reminder for user {user_id} at {reminder_time}")
    else:
        logger.warning(f"Trial reminder time {reminder_time} is in the past for user {user_id}")


def schedule_trial_end_job(user_id: int, trial_end_date: datetime, scheduler):
    """Schedule trial end notification"""
    
    if trial_end_date > datetime.now():
        scheduler.add_job(
            TrialChurnPrevention.send_trial_ended_notification,
            'date',
            run_date=trial_end_date,
            args=[user_id],
            id=f"trial_end_{user_id}_{int(datetime.now().timestamp())}",
            replace_existing=True
        )
        
        logger.info(f"Scheduled trial end notification for user {user_id} at {trial_end_date}")

