"""
UNLOCK Flow - "GIá»® NHá»ŠP Má»–I NGÃ€Y"
Philosophy: Reduce friction to maintain habit, NOT unlock features
Triggered: After 7-10 days of FREE usage (natural transition)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime, timedelta


async def unlock_step1_natural_transition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    STEP 1 - Natural transition after 7-10 days of FREE usage
    NOT triggered by referrals, NOT a feature unlock
    """
    query = update.callback_query
    await query.answer()
    
    message = """
Báº¡n Ä‘Ã£ dÃ¹ng Freedom Wallet Ä‘Æ°á»£c má»™t thá»i gian.

Nhiá»u ngÆ°á»i á»Ÿ giai Ä‘oáº¡n nÃ y nháº­n ra:
Viá»‡c má»Ÿ Web App má»—i láº§n Ä‘á»ƒ ghi chi tiÃªu
khÃ´ng pháº£i lÃºc nÃ o cÅ©ng tiá»‡n.

KhÃ´ng pháº£i vÃ¬ lÆ°á»i.
Chá»‰ lÃ  cuá»™c sá»‘ng báº­n.

Náº¿u báº¡n muá»‘n,
mÃ¬nh cÃ³ thá»ƒ káº¿t ná»‘i Telegram vá»›i Sheet cá»§a báº¡n.
Báº¡n sáº½ ghi giao dá»‹ch ngay trong chat nÃ y.
Khoáº£ng 5 giÃ¢y.
"""
    
    keyboard = [
        [InlineKeyboardButton("Káº¿t ná»‘i Telegram", callback_data="unlock_step2_explain")],
        [InlineKeyboardButton("Há»i thÃªm", callback_data="unlock_ask_question")],
        [InlineKeyboardButton("Äá»ƒ sau", callback_data="unlock_skip")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def unlock_step2_explain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 2 - Explain clearly, no technical jargon"""
    query = update.callback_query
    await query.answer()
    
    message = """
Telegram khÃ´ng thay tháº¿ há»‡ thá»‘ng cá»§a báº¡n.

Sheet váº«n náº±m trÃªn Drive cá»§a báº¡n.
Web App váº«n hoáº¡t Ä‘á»™ng nhÆ° cÅ©.

Telegram chá»‰ lÃ  cáº§u ná»‘i,
giÃºp báº¡n ghi nhanh mÃ  khÃ´ng cáº§n má»Ÿ app.
"""
    
    keyboard = [
        [InlineKeyboardButton("Tiáº¿p tá»¥c káº¿t ná»‘i", callback_data="unlock_step3_prepare")],
        [InlineKeyboardButton("Xem láº¡i cÃ¡ch hoáº¡t Ä‘á»™ng", callback_data="unlock_explain_how")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def unlock_step3_prepare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 3 - Prepare connection (simple, not scary)"""
    query = update.callback_query
    await query.answer()
    
    message = """
Äá»ƒ káº¿t ná»‘i,
mÃ¬nh cáº§n:

â€¢ ID Google Sheet cá»§a báº¡n
â€¢ Link Web App Ä‘Ã£ deploy

Chá»‰ cáº§n lÃ m theo tá»«ng bÆ°á»›c.
Náº¿u chÆ°a rÃµ chá»— nÃ o,
mÃ¬nh sáº½ hÆ°á»›ng dáº«n tiáº¿p.
"""
    
    keyboard = [
        [InlineKeyboardButton("Nháº­p Sheet ID", callback_data="unlock_input_sheet_id")],
        [InlineKeyboardButton("TÃ´i chÆ°a rÃµ", callback_data="unlock_help_sheet_id")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def unlock_step4_connection_success(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 4 - After successful connection"""
    # This can be called from sheets_setup flow after successful connection
    user = update.effective_user
    
    message = """
Káº¿t ná»‘i hoÃ n táº¥t.

Tá»« giá», báº¡n cÃ³ thá»ƒ ghi giao dá»‹ch ngay táº¡i Ä‘Ã¢y.

VÃ­ dá»¥:
Chi 50k Äƒn sÃ¡ng
Thu 5 triá»‡u lÆ°Æ¡ng
Chi 200k xÄƒng xe

KhÃ´ng cáº§n Ä‘Ãºng cÃº phÃ¡p tuyá»‡t Ä‘á»‘i.
MÃ¬nh sáº½ tá»± hiá»ƒu.
"""
    
    keyboard = [
        [InlineKeyboardButton("Thá»­ ghi giao dá»‹ch", callback_data="unlock_try_first_transaction")],
        [InlineKeyboardButton("Xem vÃ­ dá»¥ khÃ¡c", callback_data="unlock_show_examples")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=reply_markup
        )
    elif update.message:
        await update.message.reply_text(
            text=message,
            reply_markup=reply_markup
        )


async def unlock_step5_first_transaction_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 5 - Encourage first transaction"""
    query = update.callback_query
    await query.answer()
    
    message = """
Thá»­ ghi má»™t khoáº£n ngay bÃ¢y giá».

Chá»‰ má»™t khoáº£n thÃ´i.

Viá»‡c quan trá»ng khÃ´ng pháº£i sá»‘ tiá»n.
MÃ  lÃ  viá»‡c báº¡n giá»¯ Ä‘Æ°á»£c nhá»‹p má»—i ngÃ y.
"""
    
    # No buttons - let user type naturally
    await query.edit_message_text(text=message)


async def unlock_step6_after_first_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 6 - After first successful transaction via Telegram"""
    message = """
ÄÃ£ ghi.

Báº¡n khÃ´ng cáº§n má»Ÿ Web App.
Báº¡n khÃ´ng cáº§n nhá»› cuá»‘i ngÃ y.
Báº¡n chá»‰ cáº§n ghi ngay khi phÃ¡t sinh.

ThÃ³i quen Ä‘Æ°á»£c giá»¯ báº±ng sá»± Ä‘Æ¡n giáº£n.
"""
    
    keyboard = [
        [InlineKeyboardButton("Xem trÃªn Web App", callback_data="open_webapp")],
        [InlineKeyboardButton("Tiáº¿p tá»¥c ghi", callback_data="continue_logging")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup
    )


async def unlock_checkin_after_silence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check-in after 3-4 days of no activity
    IMPORTANT: Calm tone, no pressure, no surveillance feeling
    Maximum 1x per week if user is silent
    """
    user_id = context.job.data['user_id']
    
    message = """
CÃ³ váº» vÃ i ngÃ y rá»“i báº¡n chÆ°a ghi giao dá»‹ch.

KhÃ´ng sao cáº£.
Khi nÃ o phÃ¡t sinh khoáº£n má»›i,
chá»‰ cáº§n nháº¯n vÃ o Ä‘Ã¢y.

MÃ¬nh váº«n á»Ÿ Ä‘Ã¢y.
"""
    
    # No buttons, no pressure, no push
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=message
        )
        logger.info(f"âœ… Sent calm check-in to user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send check-in to {user_id}: {e}")


async def unlock_milestone_7days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    After 7 consecutive days of logging
    NO emoji, NO gamification, NO badges
    Simple acknowledgment
    """
    message = """
Báº¡n Ä‘Ã£ ghi giao dá»‹ch liÃªn tá»¥c má»™t tuáº§n.

Má»™t tuáº§n trÆ°á»›c,
viá»‡c quáº£n lÃ½ tiá»n cÃ³ thá»ƒ cÃ²n mÆ¡ há»“.

BÃ¢y giá»,
má»i khoáº£n thu â€“ chi Ä‘á»u cÃ³ dáº¥u váº¿t.

Chá»‰ cáº§n tiáº¿p tá»¥c nhÆ° váº­y.
"""
    
    # No buttons, no celebration, just acknowledgment
    await update.message.reply_text(text=message)


async def unlock_show_examples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show more transaction examples"""
    query = update.callback_query
    await query.answer()
    
    message = """
CÃ¡c cÃ¡ch ghi giao dá»‹ch:

**Thu nháº­p:**
Thu 10 triá»‡u lÆ°Æ¡ng
Nháº­n 500k tiá»n thÆ°á»Ÿng
Thu 2 triá»‡u tá»« dá»± Ã¡n

**Chi tiÃªu:**
Chi 200k Äƒn trÆ°a
Mua 150k cÃ  phÃª
Tráº£ 500k Ä‘iá»‡n nÆ°á»›c

**Chuyá»ƒn khoáº£n:**
Chuyá»ƒn 1 triá»‡u vÃ o tiáº¿t kiá»‡m
Dá»i 500k sang Ä‘áº§u tÆ°

Ghi tá»± nhiÃªn, mÃ¬nh sáº½ hiá»ƒu.
"""
    
    keyboard = [
        [InlineKeyboardButton("Thá»­ ghi ngay", callback_data="unlock_try_first_transaction")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def unlock_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose to skip Telegram connection"""
    query = update.callback_query
    await query.answer()
    
    message = """
KhÃ´ng sao.

Báº¡n váº«n cÃ³ thá»ƒ dÃ¹ng Web App nhÆ° bÃ¬nh thÆ°á»ng.

Náº¿u muá»‘n thá»­ Telegram sau nÃ y,
báº¡n cÃ³ thá»ƒ vÃ o /start vÃ  chá»n "Káº¿t ná»‘i Telegram".
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ  Vá» trang chá»§", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def unlock_ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answer common questions about Telegram connection"""
    query = update.callback_query
    await query.answer()
    
    message = """
**CÃ¢u há»i thÆ°á»ng gáº·p:**

**1. Dá»¯ liá»‡u cÃ³ máº¥t khÃ´ng?**
KhÃ´ng. Dá»¯ liá»‡u váº«n náº±m trÃªn Sheet cá»§a báº¡n.
Telegram chá»‰ gá»­i lá»‡nh, khÃ´ng lÆ°u trá»¯.

**2. Web App cÃ³ cÃ²n hoáº¡t Ä‘á»™ng khÃ´ng?**
CÃ³. Web App hoáº¡t Ä‘á»™ng Ä‘á»™c láº­p.
Telegram chá»‰ lÃ  thÃªm 1 cÃ¡ch ghi nhanh.

**3. CÃ³ báº¯t buá»™c khÃ´ng?**
KhÃ´ng. Báº¡n cÃ³ thá»ƒ chá»‰ dÃ¹ng Web App.
Telegram lÃ  tuá»³ chá»n.

**4. CÃ³ máº¥t phÃ­ khÃ´ng?**
KhÃ´ng. Káº¿t ná»‘i Telegram miá»…n phÃ­.
"""
    
    keyboard = [
        [InlineKeyboardButton("Káº¿t ná»‘i Telegram", callback_data="unlock_step2_explain")],
        [InlineKeyboardButton("Quay láº¡i", callback_data="unlock_step1_natural_transition")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def unlock_explain_how(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Explain how Telegram connection works"""
    query = update.callback_query
    await query.answer()
    
    message = """
**CÃ¡ch hoáº¡t Ä‘á»™ng:**

1. Báº¡n gÃµ giao dá»‹ch trong Telegram
   VÃ­ dá»¥: "Chi 50k Äƒn sÃ¡ng"

2. Bot hiá»ƒu vÃ  gá»­i lá»‡nh Ä‘áº¿n Web App

3. Web App cáº­p nháº­t vÃ o Google Sheet

4. Sheet tÃ­nh toÃ¡n tá»± Ä‘á»™ng

5. Báº¡n cÃ³ thá»ƒ xem káº¿t quáº£ á»Ÿ Web App
   hoáº·c há»i bot "sá»‘ dÆ°"

**Dá»¯ liá»‡u váº«n á»Ÿ Sheet cá»§a báº¡n.**
**Telegram chá»‰ lÃ  remote control.**
"""
    
    keyboard = [
        [InlineKeyboardButton("Hiá»ƒu rá»“i, tiáº¿p tá»¥c", callback_data="unlock_step3_prepare")],
        [InlineKeyboardButton("Quay láº¡i", callback_data="unlock_step1_natural_transition")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def schedule_silent_checkin(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Schedule a check-in if user has been silent for 3-4 days
    Call this from daily jobs, but only send if:
    - Last activity > 3 days ago
    - Last check-in > 7 days ago (max 1x per week)
    """
    from app.utils.database import get_user_by_id
    
    db_user = await get_user_by_id(user_id)
    if not db_user or not db_user.is_free_unlocked:
        return  # Only for unlocked users
    
    # Check last activity (use last_active field)
    if not db_user.last_active:
        return
    
    days_silent = (datetime.utcnow() - db_user.last_active).days
    
    # Only send if silent for 3-4 days
    if days_silent < 3 or days_silent > 4:
        return
    
    # Check if we sent check-in recently
    if db_user.last_checkin:
        days_since_checkin = (datetime.utcnow() - db_user.last_checkin).days
        if days_since_checkin < 7:
            return  # Don't spam, max 1x per week
    
    # Schedule the check-in
    context.job_queue.run_once(
        unlock_checkin_after_silence,
        when=10,  # Send after 10 seconds
        data={'user_id': user_id},
        name=f"checkin_{user_id}"
    )
    
    # Update last_checkin timestamp
    from app.utils.database import SessionLocal
    db = SessionLocal()
    db_user.last_checkin = datetime.utcnow()
    db.commit()
    db.close()


def register_unlock_calm_flow_handlers(application):
    """Register all UNLOCK calm flow handlers"""
    from telegram.ext import CallbackQueryHandler
    
    application.add_handler(CallbackQueryHandler(unlock_step1_natural_transition, pattern="^unlock_step1_natural_transition$"))
    application.add_handler(CallbackQueryHandler(unlock_step2_explain, pattern="^unlock_step2_explain$"))
    application.add_handler(CallbackQueryHandler(unlock_step3_prepare, pattern="^unlock_step3_prepare$"))
    application.add_handler(CallbackQueryHandler(unlock_step4_connection_success, pattern="^unlock_step4_connection_success$"))
    application.add_handler(CallbackQueryHandler(unlock_step5_first_transaction_prompt, pattern="^unlock_try_first_transaction$"))
    application.add_handler(CallbackQueryHandler(unlock_show_examples, pattern="^unlock_show_examples$"))
    application.add_handler(CallbackQueryHandler(unlock_skip, pattern="^unlock_skip$"))
    application.add_handler(CallbackQueryHandler(unlock_ask_question, pattern="^unlock_ask_question$"))
    application.add_handler(CallbackQueryHandler(unlock_explain_how, pattern="^unlock_explain_how$"))
    
    # Redirect to sheets_setup for actual connection
    async def redirect_to_sheets_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        # Forward to sheets_setup flow
        from app.handlers.sheets.sheets_setup import start_sheets_setup_flow
        await start_sheets_setup_flow(update, context)
    
    application.add_handler(CallbackQueryHandler(redirect_to_sheets_setup, pattern="^unlock_input_sheet_id$"))
    application.add_handler(CallbackQueryHandler(redirect_to_sheets_setup, pattern="^unlock_help_sheet_id$"))
    
    logger.info("âœ… UNLOCK calm flow handlers registered")

