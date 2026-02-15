"""
UNLOCK Flow Trigger - Auto-suggest Telegram connection after 7-10 days of FREE usage
Philosophy: Natural transition, not forced upgrade
"""

from datetime import datetime, timedelta
from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def check_and_trigger_unlock_offer(context):
    """
    Daily job: Check users who are ready for UNLOCK flow
    Criteria:
    - Using FREE for 7-10 days
    - Has logged at least 5 transactions
    - Not yet connected Telegram
    - Not yet received UNLOCK offer
    """
    from app.utils.database import SessionLocal, User
    
    db = SessionLocal()
    try:
        # Find users eligible for UNLOCK offer
        threshold_date = datetime.utcnow() - timedelta(days=7)
        max_date = datetime.utcnow() - timedelta(days=10)
        
        eligible_users = db.query(User).filter(
            User.created_at >= max_date,
            User.created_at <= threshold_date,
            User.is_free_unlocked == False,  # Not yet unlocked Telegram
            User.unlock_offered == False,  # Not yet offered
            User.total_transactions >= 5  # At least 5 transactions logged (use total_transactions)
        ).all()
        
        logger.info(f"Found {len(eligible_users)} users eligible for UNLOCK offer")
        
        for user in eligible_users:
            try:
                await send_unlock_offer(context, user.user_id)
                
                # Mark as offered
                user.unlock_offered = True
                user.unlock_offered_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"✅ Sent UNLOCK offer to user {user.user_id}")
                
            except Exception as e:
                logger.error(f"Failed to send UNLOCK offer to {user.user_id}: {e}")
                
    finally:
        db.close()


async def send_unlock_offer(context, user_id: int):
    """
    Send UNLOCK offer message to eligible user
    Calm, natural transition - not a sales pitch
    """
    message = """
Bạn đã dùng Freedom Wallet được một thời gian.

Nhiều người ở giai đoạn này nhận ra:
Việc mở Web App mỗi lần để ghi chi tiêu
không phải lúc nào cũng tiện.

Không phải vì lười.
Chỉ là cuộc sống bận.

Nếu bạn muốn,
mình có thể kết nối Telegram với Sheet của bạn.
Bạn sẽ ghi giao dịch ngay trong chat này.
Khoảng 5 giây.
"""
    
    keyboard = [
        [InlineKeyboardButton("Kết nối Telegram", callback_data="unlock_step2_explain")],
        [InlineKeyboardButton("Hỏi thêm", callback_data="unlock_ask_question")],
        [InlineKeyboardButton("Để sau", callback_data="unlock_skip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=user_id,
        text=message,
        reply_markup=reply_markup
    )


def setup_unlock_trigger_job(application):
    """
    Setup daily job to check and trigger UNLOCK offers
    Run once per day at 10:00 AM UTC
    """
    from telegram.ext import Application
    
    # Schedule daily check at 10:00 AM UTC
    application.job_queue.run_daily(
        check_and_trigger_unlock_offer,
        time=datetime.strptime("10:00", "%H:%M").time(),
        name="unlock_offer_check"
    )
    
    logger.info("✅ UNLOCK offer trigger job scheduled (10:00 AM UTC daily)")

