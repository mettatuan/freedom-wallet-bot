"""
Unlock Flow v3.0 - Optimized Post-Unlock Journey
Ownership-first, Identity-driven, User-controlled pacing
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from loguru import logger


async def send_unlock_message_1(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    MESSAGE 1: RECOGNITION & OWNERSHIP
    Chuyá»ƒn tráº¡ng thÃ¡i tÃ¢m lÃ½ tá»« "hoÃ n thÃ nh nhiá»‡m vá»¥ xÃ£ há»™i" â†’ "sá»Ÿ há»¯u cÃ´ng cá»¥ cÃ¡ nhÃ¢n"
    """
    text = """ðŸŽ‰ ChÃºc má»«ng báº¡n!

Báº¡n Ä‘Ã£ hoÃ n táº¥t má»‘c 2 ngÆ°á»i giá»›i thiá»‡u.
Tá»« Ä‘Ã¢y, Freedom Wallet Ä‘Ã£ sáºµn sÃ ng Ä‘á»ƒ báº¡n sá»­ dá»¥ng Ä‘áº§y Ä‘á»§ cho chÃ­nh mÃ¬nh.

KhÃ´ng pháº£i xem thá»­.
KhÃ´ng pháº£i lÃ m cho cÃ³.

ðŸ‘‰ ÄÃ¢y lÃ  há»‡ thá»‘ng quáº£n lÃ½ tÃ i chÃ­nh cÃ¡ nhÃ¢n cá»§a báº¡n."""

    keyboard = [
        [InlineKeyboardButton("ðŸ”“ Tiáº¿p tá»¥c", callback_data="unlock_continue")],
        [InlineKeyboardButton("ðŸ“Š Xem tráº¡ng thÃ¡i cá»§a tÃ´i", callback_data="unlock_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=None
        )
        logger.info(f"âœ… Sent unlock Message 1 to user {user_id}")
    except Exception as e:
        logger.error(f"âŒ Failed to send unlock Message 1 to user {user_id}: {e}")


async def handle_unlock_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    MESSAGE 2: IDENTITY + SINGLE NEXT STEP
    Trigger: User clicks "ðŸ”“ Tiáº¿p tá»¥c"
    """
    query = update.callback_query
    await query.answer()
    
    text = """Tá»« thá»i Ä‘iá»ƒm nÃ y, báº¡n lÃ  thÃ nh viÃªn chÃ­nh thá»©c cá»§a Freedom Wallet.

ThÃ nh viÃªn chÃ­nh thá»©c lÃ  nhá»¯ng ngÆ°á»i:
â€¢ Chá»§ Ä‘á»™ng quáº£n lÃ½ tiá»n cá»§a mÃ¬nh
â€¢ Muá»‘n nhÃ¬n rÃµ dÃ²ng tiá»n, khÃ´ng Ä‘oÃ¡n mÃ²
â€¢ Sáºµn sÃ ng báº¯t Ä‘áº§u báº±ng hÃ nh Ä‘á»™ng thá»±c táº¿

BÆ°á»›c tiáº¿p theo ráº¥t Ä‘Æ¡n giáº£n:
ðŸ‘‰ Thiáº¿t láº­p Freedom Wallet Ä‘á»ƒ báº¯t Ä‘áº§u sá»­ dá»¥ng."""

    keyboard = [
        [InlineKeyboardButton("ðŸ›  Báº¯t Ä‘áº§u thiáº¿t láº­p", callback_data="setup_start")],
        [InlineKeyboardButton("ðŸ§­ Xem lá»™ trÃ¬nh cÃ¡ nhÃ¢n", callback_data="view_roadmap")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"âœ… Sent unlock Message 2 to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"âŒ Failed to send unlock Message 2: {e}")


async def handle_unlock_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ALTERNATIVE PATH: User clicks "ðŸ“Š Xem tráº¡ng thÃ¡i cá»§a tÃ´i"
    """
    query = update.callback_query
    await query.answer()
    
    text = """ðŸ“Š TRáº NG THÃI Cá»¦A Báº N

âœ… ÄÃ£ hoÃ n táº¥t: 2/2 giá»›i thiá»‡u
âœ… Tráº¡ng thÃ¡i: ThÃ nh viÃªn FREE
âœ… Quyá»n truy cáº­p: Äáº§y Ä‘á»§ tÃ­nh nÄƒng

BÆ°á»›c tiáº¿p theo:
ðŸ‘‰ Thiáº¿t láº­p Freedom Wallet Ä‘á»ƒ sá»­ dá»¥ng."""

    keyboard = [[InlineKeyboardButton("ðŸ”“ Báº¯t Ä‘áº§u ngay", callback_data="unlock_continue")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"âœ… Showed status to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"âŒ Failed to show status: {e}")


async def handle_setup_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    MESSAGE 3: DAY 1 â€“ FIRST REAL USAGE
    Trigger: User clicks "ðŸ›  Báº¯t Ä‘áº§u thiáº¿t láº­p"
    """
    query = update.callback_query
    await query.answer()
    
    text = """ðŸŽ¯ BÆ¯á»šC Äáº¦U TIÃŠN â€“ THIáº¾T Láº¬P FREEDOM WALLET

Báº¡n chá»‰ cáº§n lÃ m 3 viá»‡c (10â€“15 phÃºt):
1ï¸âƒ£ Copy Google Sheets Template
2ï¸âƒ£ Táº¡o Web App cÃ¡ nhÃ¢n
3ï¸âƒ£ Nháº­p sá»‘ dÆ° + 1 giao dá»‹ch Ä‘áº§u tiÃªn

ðŸ‘‰ KhÃ´ng cáº§n biáº¿t code.
ðŸ‘‰ LÃ m cháº­m cÅ©ng hoÃ n toÃ n á»•n."""

    keyboard = [
        [InlineKeyboardButton("ðŸ“‘ Copy Template", url="https://docs.google.com/spreadsheets/d/1nMJNc3KWEGWs7LMZpGJaxeiqbCFaLg_O3oYE4Wx5lnU/copy")],
        [InlineKeyboardButton("ðŸŒ HÆ°á»›ng dáº«n Web App", callback_data="webapp_guide")],
        [InlineKeyboardButton("â“ Cáº§n há»— trá»£", callback_data="setup_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"âœ… Sent setup Message 3 to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"âŒ Failed to send setup message: {e}")


async def handle_view_roadmap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ALTERNATIVE PATH: User clicks "ðŸ§­ Xem lá»™ trÃ¬nh cÃ¡ nhÃ¢n"
    """
    query = update.callback_query
    await query.answer()
    
    text = """ðŸ§­ Lá»˜ TRÃŒNH CÃ NHÃ‚N

**HÃ´m nay:**
âœ“ Thiáº¿t láº­p Web App (10-15 phÃºt)
âœ“ Nháº­p giao dá»‹ch Ä‘áº§u tiÃªn

**Tuáº§n nÃ y:**
â€¢ Hiá»ƒu vá» 6 HÅ© Tiá»n
â€¢ Theo dÃµi dÃ²ng tiá»n hÃ ng ngÃ y
â€¢ Xem bÃ¡o cÃ¡o chi tiÃªu

**ThÃ¡ng nÃ y:**
â€¢ XÃ¢y dá»±ng Quá»¹ Kháº©n Cáº¥p
â€¢ Láº­p káº¿ hoáº¡ch tÃ i chÃ­nh rÃµ rÃ ng
â€¢ LÃ m chá»§ tÃ i chÃ­nh cÃ¡ nhÃ¢n

Sáºµn sÃ ng báº¯t Ä‘áº§u?"""

    keyboard = [[InlineKeyboardButton("ðŸ›  Báº¯t Ä‘áº§u thiáº¿t láº­p", callback_data="setup_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"âœ… Showed roadmap to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"âŒ Failed to show roadmap: {e}")


async def handle_webapp_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User clicks "ðŸŒ HÆ°á»›ng dáº«n Web App"
    Send step-by-step setup guide
    """
    query = update.callback_query
    await query.answer()
    
    # Use existing webapp setup handler
    from app.handlers.webapp_setup import start_webapp_setup
    await start_webapp_setup(update, context)


async def handle_setup_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User clicks "â“ Cáº§n há»— trá»£"
    Show support options
    """
    query = update.callback_query
    await query.answer()
    
    text = """â“ Há»– TRá»¢ THIáº¾T Láº¬P

Chá»n cÃ¡ch báº¡n muá»‘n Ä‘Æ°á»£c há»— trá»£:"""

    keyboard = [
        [InlineKeyboardButton("ðŸ“š Xem hÆ°á»›ng dáº«n Notion", url="https://phamthanhtuan.notion.site/1717ba14c3d0801090cdf4c57ff08652?pvs=105")],
        [InlineKeyboardButton("ðŸ’¬ Tham gia Group", url="https://t.me/+vBZk4Kq59P9mMzY1")],
        [InlineKeyboardButton("ðŸ‘¨â€ðŸ’¼ Chat vá»›i Admin", url="https://t.me/tuanai_mentor")],
        [InlineKeyboardButton("ðŸ”™ Quay láº¡i", callback_data="setup_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"âœ… Showed support menu to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"âŒ Failed to show support menu: {e}")


async def send_gentle_reminder(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    MESSAGE 4 (OPTIONAL): GENTLE FOLLOW-UP
    Sent 24 hours after Message 1 if user hasn't progressed
    """
    text = """ðŸ‘‹ Nháº¯c nháº¹ tá»« Freedom Wallet

Chá»‰ cáº§n hoÃ n thÃ nh bÆ°á»›c thiáº¿t láº­p Ä‘áº§u tiÃªn,
báº¡n sáº½ báº¯t Ä‘áº§u tháº¥y dÃ²ng tiá»n cá»§a mÃ¬nh rÃµ rÃ ng hÆ¡n.

Khi báº¡n sáºµn sÃ ng, mÃ¬nh á»Ÿ Ä‘Ã¢y Ä‘á»ƒ tiáº¿p tá»¥c."""

    keyboard = [[InlineKeyboardButton("ðŸ›  Tiáº¿p tá»¥c thiáº¿t láº­p", callback_data="setup_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"âœ… Sent gentle reminder to user {user_id}")
    except Exception as e:
        logger.error(f"âŒ Failed to send reminder to user {user_id}: {e}")


def register_unlock_handlers(application):
    """Register all unlock flow v3.0 callback handlers"""
    application.add_handler(CallbackQueryHandler(handle_unlock_continue, pattern="^unlock_continue$"))
    application.add_handler(CallbackQueryHandler(handle_unlock_status, pattern="^unlock_status$"))
    application.add_handler(CallbackQueryHandler(handle_setup_start, pattern="^setup_start$"))
    application.add_handler(CallbackQueryHandler(handle_view_roadmap, pattern="^view_roadmap$"))
    application.add_handler(CallbackQueryHandler(handle_webapp_guide, pattern="^webapp_guide$"))
    application.add_handler(CallbackQueryHandler(handle_setup_help, pattern="^setup_help$"))
    
    logger.info("âœ… Unlock flow v3.0 handlers registered")

