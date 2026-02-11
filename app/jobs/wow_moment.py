"""
24h WOW Moment Job - Send value realization message after trial start

Goal: Show concrete ROI after 24h to reduce churn
Triggers: 24h after trial_start or premium_start
"""
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal, User
from app.core.subscription import SubscriptionManager, SubscriptionTier
from app.services.analytics import Analytics
from loguru import logger
from config.settings import settings


class WOWMomentService:
    """Service for sending 24h WOW moment messages"""
    
    HOURLY_VALUE = 100_000  # VNÄ/hour (user's time value)
    TIME_PER_MESSAGE = 3  # minutes saved per AI message
    TIME_PER_ANALYSIS = 30  # minutes saved per analysis
    
    @staticmethod
    def calculate_24h_value(user_id: int, db: Session) -> dict:
        """Calculate value received in first 24 hours"""
        
        # Count messages sent in last 24h
        from datetime import datetime, timedelta
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        # Count bot messages (from analytics or database)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get message count (simplified - use bot_chat_count as proxy)
        messages_sent = user.bot_chat_count or 0
        
        # Calculate time saved
        time_saved_minutes = messages_sent * WOWMomentService.TIME_PER_MESSAGE
        time_saved_hours = time_saved_minutes / 60
        
        # Calculate monetary value
        value = time_saved_hours * WOWMomentService.HOURLY_VALUE
        
        # Premium cost (daily rate)
        premium_daily_cost = 83_000 / 30  # ~2,767 VNÄ/day
        
        # ROI calculation
        profit = value - premium_daily_cost
        roi_percent = (profit / premium_daily_cost * 100) if premium_daily_cost > 0 else 0
        
        return {
            'messages': messages_sent,
            'time_saved_hours': round(time_saved_hours, 1),
            'value': int(value),
            'cost': int(premium_daily_cost),
            'profit': int(profit),
            'roi_percent': round(roi_percent, 1)
        }
    
    @staticmethod
    async def send_24h_wow_moment(user_id: int):
        """Send 24h WOW moment message to user"""
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.warning(f"User {user_id} not found for WOW moment")
                return
            
            # Check if still on trial/premium
            tier = SubscriptionManager.get_user_tier(user)
            if tier not in [SubscriptionTier.TRIAL, SubscriptionTier.PREMIUM]:
                logger.info(f"User {user_id} no longer trial/premium, skipping WOW moment")
                return
            
            # Calculate value stats
            stats = WOWMomentService.calculate_24h_value(user_id, db)
            
            if not stats:
                logger.error(f"Failed to calculate stats for user {user_id}")
                return
            
            # Craft message
            days_remaining = 6 if tier == SubscriptionTier.TRIAL else "nhiá»u"
            tier_name = "Trial" if tier == SubscriptionTier.TRIAL else "Premium"
            
            message = f"""
ðŸŽŠ **24 GIá»œ Vá»šI {tier_name.upper()}!**

ChÃºc má»«ng báº¡n Ä‘Ã£ tráº£i nghiá»‡m 24h Ä‘áº§u tiÃªn! ðŸŽ‰

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“Š **THá»NG KÃŠ 24H:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¬ **{stats['messages']} cÃ¢u tráº£ lá»i AI**
   â†’ KhÃ´ng giá»›i háº¡n, khÃ´ng lo háº¿t quota

â±ï¸ **{stats['time_saved_hours']} giá» tiáº¿t kiá»‡m**
   â†’ TÆ°Æ¡ng Ä‘Æ°Æ¡ng {stats['time_saved_hours']} giá» lÃ m viá»‡c

ðŸ’° **GiÃ¡ trá»‹ nháº­n Ä‘Æ°á»£c: ~{stats['value']:,} VNÄ**
   â†’ TÃ­nh theo 100K VNÄ/giá»

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’Ž **ROI HIá»†N Táº I:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

Chi: {stats['cost']:,} VNÄ/ngÃ y
Nháº­n: {stats['value']:,} VNÄ/ngÃ y

â†’ **Báº¡n Ä‘ang "lá»i" {stats['profit']:,} VNÄ!** ðŸš€
â†’ ROI: +{stats['roi_percent']}%

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ **TIáº¾P Tá»¤C:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… CÃ²n {days_remaining} ngÃ y Ä‘á»ƒ tráº£i nghiá»‡m
âœ… Táº¥t cáº£ tÃ­nh nÄƒng Premium Ä‘Ã£ má»Ÿ khÃ³a
âœ… Há»— trá»£ Æ°u tiÃªn trong 30 phÃºt

ðŸŽ¯ **Tip:** Thá»­ tÃ­nh nÄƒng "ðŸ’¡ Gá»£i Ã½" Ä‘á»ƒ tá»‘i Æ°u tÃ i chÃ­nh hÆ¡n ná»¯a!
"""
            
            # Create interactive buttons
            keyboard = [
                [InlineKeyboardButton("ðŸ“Š Xem ROI chi tiáº¿t", callback_data="view_roi_detail")],
                [InlineKeyboardButton("ðŸ’¡ Tá»‘i Æ°u hÆ¡n ná»¯a", callback_data="optimization_tips")],
                [InlineKeyboardButton("âœ… OK, Ä‘Ã£ hiá»ƒu", callback_data="wow_moment_dismiss")]
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
            Analytics.track_event(user_id, 'wow_moment_sent', {
                'messages': stats['messages'],
                'value': stats['value'],
                'roi': stats['roi_percent']
            })
            
            logger.info(f"Sent 24h WOW moment to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending WOW moment to {user_id}: {e}")
        finally:
            db.close()


def schedule_wow_moment_job(user_id: int, scheduler):
    """Schedule 24h WOW moment job"""
    from datetime import datetime, timedelta
    
    run_date = datetime.now() + timedelta(hours=24)
    
    scheduler.add_job(
        WOWMomentService.send_24h_wow_moment,
        'date',
        run_date=run_date,
        args=[user_id],
        id=f"wow_moment_{user_id}_{int(datetime.now().timestamp())}",
        replace_existing=True
    )
    
    logger.info(f"Scheduled 24h WOW moment for user {user_id} at {run_date}")

