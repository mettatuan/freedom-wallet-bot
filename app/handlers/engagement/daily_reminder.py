"""
Daily Reminder System - Nháº¯c nhá»Ÿ ghi chÃ©p hÃ ng ngÃ y
GiÃºp user táº¡o thÃ³i quen tracking tÃ i chÃ­nh 
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from loguru import logger
from datetime import datetime, timedelta
from app.utils.database import SessionLocal, User


# Morning Reminder Content (8:00 AM)
MORNING_REMINDER_TEMPLATE = """
ðŸŒ… **ChÃ o buá»•i sÃ¡ng {name}!**

ðŸ’ª **HÃ´m nay lÃ  ngÃ y thá»© {streak} ghi chÃ©p cá»§a báº¡n!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŽ¯ **Má»¥c tiÃªu hÃ´m nay:**
â€¢ Ghi Ã­t nháº¥t 3 giao dá»‹ch
â€¢ Nhá»› phÃ¢n loáº¡i Ä‘Ãºng hÅ© tiá»n
â€¢ Review tá»•ng chi tiÃªu

{streak_message}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¡ **Tip:** Ghi chÃ©p ngay khi chi tiÃªu â†’ khÃ´ng bao giá» quÃªn!
"""

# Evening Reminder Content (8:00 PM)
EVENING_REMINDER_TEMPLATE = """
ðŸŒ™ **TrÆ°á»›c khi ngá»§... {name}**

â“ **HÃ´m nay báº¡n Ä‘Ã£ ghi chÃ©p chÆ°a?**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

{streak_status}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¤ **Ghi ngay trÆ°á»›c khi quÃªn:**
â€¢ Bá»¯a Äƒn hÃ´m nay
â€¢ Di chuyá»ƒn (xÄƒng, grab...)
â€¢ Cafe, giáº£i trÃ­
â€¢ Mua sáº¯m

ðŸ’¡ *Chá»‰ máº¥t 30 giÃ¢y thÃ´i!*
"""

# Skip Alert (náº¿u khÃ´ng ghi 2 ngÃ y liÃªn tiáº¿p)
SKIP_ALERT_TEMPLATE = """
ðŸ˜¢ **Uhm... {name}, báº¡n á»•n chá»©?**

MÃ¬nh tháº¥y báº¡n Ä‘Ã£ khÃ´ng ghi chÃ©p {skip_days} ngÃ y rá»“i.

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¡ **Gáº·p khÃ³ khÄƒn gÃ¬ khÃ´ng?**
â€¢ QuÃªn máº¥t?
â€¢ App gáº·p lá»—i?
â€¢ ChÆ°a rÃµ cÃ¡ch ghi?

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

MÃ¬nh á»Ÿ Ä‘Ã¢y giÃºp báº¡n! Nháº¯n cho mÃ¬nh nhÃ© ðŸ’¬

*"ThÃ nh cÃ´ng khÃ´ng Ä‘áº¿n tá»« Ä‘á»™ng lá»±c - mÃ  Ä‘áº¿n tá»« hÃ nh Ä‘á»™ng!"*
"""


def get_streak_message(streak: int) -> str:
    """Generate encouraging message based on streak"""
    if streak == 1:
        return "ðŸŒ± **Streak má»›i báº¯t Ä‘áº§u!** HÃ£y tiáº¿p tá»¥c nhÃ©!"
    elif streak < 3:
        return f"ðŸ”¥ **Streak: {streak} ngÃ y!** Cá»‘ gáº¯ng thÃªm má»™t chÃºt ná»¯a!"
    elif streak < 7:
        return f"ðŸ”¥ **Streak: {streak} ngÃ y!** Tuyá»‡t vá»i! CÃ²n {7-streak} ngÃ y ná»¯a Ä‘áº¡t 7 ngÃ y!"
    elif streak == 7:
        return "ðŸŽ‰ **CHÃšC Má»ªNG! 7 NGÃ€Y LIÃŠN Tá»¤C!** HÃ´m nay báº¡n sáº½ nháº­n quÃ  Ä‘áº·c biá»‡t!"
    elif streak < 21:
        return f"ðŸ”¥ **Streak: {streak} ngÃ y!** Amazing! Äang trÃªn Ä‘Æ°á»ng hÃ¬nh thÃ nh thÃ³i quen!"
    elif streak < 30:
        return f"ðŸ”¥ **Streak: {streak} ngÃ y!** Xuáº¥t sáº¯c! CÃ²n {30-streak} ngÃ y ná»¯a Ä‘áº¡t 30 ngÃ y!"
    elif streak == 30:
        return "ðŸ† **CHÃšC Má»ªNG! 30 NGÃ€Y LIÃŠN Tá»¤C!** Báº¡n sáº½ nháº­n huy chÆ°Æ¡ng danh dá»±!"
    elif streak < 90:
        return f"ðŸ”¥ **Streak: {streak} ngÃ y!** Legendary! Báº¡n lÃ  master rá»“i!"
    else:
        return f"ðŸ‘‘ **Streak: {streak} ngÃ y!** Báº N LÃ€ HUYá»€N THOáº I!"


async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send morning motivation reminder"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.reminder_enabled:
            db.close()
            return
        
        # Get user name
        name = user.full_name or user.first_name or "báº¡n"
        streak = user.streak_count or 0
        
        # Generate message
        streak_message = get_streak_message(streak)
        message = MORNING_REMINDER_TEMPLATE.format(
            name=name,
            streak=streak if streak > 0 else 1,
            streak_message=streak_message
        )
        
        # Keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ðŸ“ Má»Ÿ App ngay", callback_data="reminder_open_app")],
            [InlineKeyboardButton("â° Nháº¯c tÃ´i tá»‘i nay", callback_data="reminder_snooze_evening")],
            [InlineKeyboardButton("ðŸ”• Táº¯t nháº¯c nhá»Ÿ hÃ´m nay", callback_data="reminder_disable_today")]
        ])
        
        # Send message
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        # Update last reminder sent
        user.last_reminder_sent = datetime.utcnow()
        db.commit()
        db.close()
        
        logger.info(f"Sent morning reminder to user {user_id} (streak: {streak})")
        
    except Exception as e:
        logger.error(f"Error sending morning reminder to {user_id}: {e}")


async def send_evening_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send evening reminder to record transactions"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.reminder_enabled:
            db.close()
            return
        
        # Get user name
        name = user.full_name or user.first_name or "báº¡n"
        streak = user.streak_count or 0
        
        # Check if user recorded transaction today
        today = datetime.utcnow().date()
        last_transaction = user.last_transaction_date
        recorded_today = last_transaction and last_transaction.date() == today
        
        if recorded_today:
            streak_status = f"âœ… **Tuyá»‡t vá»i!** Báº¡n Ä‘Ã£ ghi chÃ©p hÃ´m nay!\n\nðŸ”¥ **Streak: {streak} ngÃ y liÃªn tá»¥c!**"
        else:
            streak_status = "âš ï¸ **ChÆ°a ghi chÃ©p hÃ´m nay!**\n\nGhi ngay Ä‘á»ƒ giá»¯ streak nhÃ©!"
        
        # Generate message
        message = EVENING_REMINDER_TEMPLATE.format(
            name=name,
            streak_status=streak_status
        )
        
        # Keyboard
        if recorded_today:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("ðŸ“Š Xem bÃ¡o cÃ¡o", callback_data="reminder_view_report")],
                [InlineKeyboardButton("ðŸ“ Ghi thÃªm", callback_data="reminder_open_app")]
            ])
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("ðŸ“ Ghi ngay", callback_data="reminder_open_app")],
                [InlineKeyboardButton("âœ… ÄÃ£ ghi xong", callback_data="reminder_done")],
                [InlineKeyboardButton("â° Nháº¯c tÃ´i sau 1h", callback_data="reminder_snooze_1h")]
            ])
        
        # Send message
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        # Update last reminder sent
        user.last_reminder_sent = datetime.utcnow()
        db.commit()
        db.close()
        
        logger.info(f"Sent evening reminder to user {user_id} (recorded_today: {recorded_today})")
        
    except Exception as e:
        logger.error(f"Error sending evening reminder to {user_id}: {e}")


async def send_skip_alert(context: ContextTypes.DEFAULT_TYPE, user_id: int, skip_days: int):
    """Send alert when user skips recording for 2+ days"""
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return
        
        # Get user name
        name = user.full_name or user.first_name or "báº¡n"
        
        # Generate message
        message = SKIP_ALERT_TEMPLATE.format(
            name=name,
            skip_days=skip_days
        )
        
        # Keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ðŸ“ Ghi bÃ¹ ngay", callback_data="reminder_catch_up")],
            [InlineKeyboardButton("ðŸ’¬ Cáº§n há»— trá»£", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("â° Nháº¯c tÃ´i sÃ¡ng mai", callback_data="reminder_snooze_tomorrow")]
        ])
        
        # Send message
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        logger.info(f"Sent skip alert to user {user_id} (skip_days: {skip_days})")
        db.close()
        
    except Exception as e:
        logger.error(f"Error sending skip alert to {user_id}: {e}")


# Callback handlers for reminder buttons
async def reminder_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reminder button callbacks"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = update.effective_user.id
    
    try:
        if callback_data == "reminder_open_app":
            await query.edit_message_text(
                text="ðŸ“± **HÃ£y má»Ÿ Web App cá»§a báº¡n Ä‘á»ƒ ghi chÃ©p!**\n\n"
                     "Link Web App náº±m trong message Day 1 cá»§a báº¡n.\n\n"
                     "ðŸ’¡ *Tip: Pin message chá»©a Web App Ä‘á»ƒ truy cáº­p nhanh!*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("ðŸ‘¥ Group VIP", url="https://t.me/freedomwalletapp")
                ]])
            )
        
        elif callback_data == "reminder_done":
            await query.edit_message_text(
                text="âœ… **Tuyá»‡t vá»i! Cáº£m Æ¡n báº¡n Ä‘Ã£ ghi chÃ©p!**\n\n"
                     "ðŸ”¥ Streak cá»§a báº¡n Ä‘Æ°á»£c giá»¯ nguyÃªn!\n\n"
                     "Háº¹n gáº·p láº¡i báº¡n vÃ o sÃ¡ng mai! ðŸ˜Š",
                parse_mode="Markdown"
            )
        
        elif callback_data == "reminder_disable_today":
            db = SessionLocal()
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.reminder_enabled = False
                db.commit()
            db.close()
            
            await query.edit_message_text(
                text="ðŸ”• **ÄÃ£ táº¯t nháº¯c nhá»Ÿ hÃ´m nay.**\n\n"
                     "Báº¡n cÃ³ thá»ƒ báº­t láº¡i báº¥t cá»© lÃºc nÃ o báº±ng lá»‡nh /reminder_on",
                parse_mode="Markdown"
            )
        
        elif callback_data in ["reminder_snooze_evening", "reminder_snooze_1h", "reminder_snooze_tomorrow"]:
            await query.edit_message_text(
                text="â° **Okay! MÃ¬nh sáº½ nháº¯c báº¡n sau!**\n\n"
                     "Äá»«ng quÃªn ghi chÃ©p nhÃ©! ðŸ˜Š",
                parse_mode="Markdown"
            )
        
        elif callback_data == "reminder_view_report":
            await query.edit_message_text(
                text="ðŸ“Š **Xem bÃ¡o cÃ¡o trong Web App cá»§a báº¡n!**\n\n"
                     "VÃ o menu â†’ Reports Ä‘á»ƒ xem chi tiáº¿t:\n"
                     "â€¢ Chi tiÃªu theo danh má»¥c\n"
                     "â€¢ PhÃ¢n bá»• 6 HÅ© Tiá»n\n"
                     "â€¢ Xu hÆ°á»›ng theo thá»i gian\n\n"
                     "ðŸ’¡ *Review hÃ ng tuáº§n Ä‘á»ƒ tá»‘i Æ°u tÃ i chÃ­nh!*",
                parse_mode="Markdown"
            )
        
        elif callback_data == "reminder_catch_up":
            await query.edit_message_text(
                text="ðŸ’ª **Tuyá»‡t! HÃ£y ghi bÃ¹ nhá»¯ng giao dá»‹ch Ä‘Ã£ bá» lá»¡!**\n\n"
                     "ðŸ“ **Tips ghi bÃ¹:**\n"
                     "1. Má»Ÿ Web App\n"
                     "2. ThÃªm giao dá»‹ch â†’ Chá»n ngÃ y cÅ©\n"
                     "3. Ghi táº¥t cáº£ giao dá»‹ch Ä‘Ã£ nhá»› ra\n\n"
                     "ðŸŽ¯ Sau khi ghi xong, streak sáº½ Ä‘Æ°á»£c cáº­p nháº­t!",
                parse_mode="Markdown"
            )
        
    except Exception as e:
        logger.error(f"Error in reminder callback handler: {e}")


def register_reminder_handlers(application):
    """Register reminder callback handlers"""
    application.add_handler(CallbackQueryHandler(reminder_callback_handler, pattern="^reminder_"))
    logger.info("âœ… Daily reminder handlers registered")

