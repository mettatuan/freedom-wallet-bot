"""
Usage Tracking Middleware - Message limit enforcement
Intercepts all user messages and enforces FREE tier limits
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from app.utils.database import get_user_by_id
from app.core.subscription import SubscriptionManager, SubscriptionTier
from app.services.analytics import Analytics


async def check_message_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Middleware to check if user can send message
    
    Returns:
        bool: True if message allowed, False if blocked
    """
    if not update.message or not update.message.text:
        return True  # Allow non-text messages
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)  # FIX: Added await
    
    if not user:
        # New user, allow first message
        return True
    
    # Check if user can send message
    can_send, error_msg = SubscriptionManager.can_send_message(user)
    
    if not can_send:
        # Track limit hit event
        Analytics.track_event(user_id, 'chat_limit_hit', {
            'messages_today': user.bot_chat_count,
            'tier': user.subscription_tier
        })
        
        # Send upgrade prompt
        await send_upgrade_prompt(update, context, error_msg)
        
        logger.warning(f"User {user_id} hit message limit ({user.bot_chat_count}/{SubscriptionManager.FREE_DAILY_MESSAGES})")
        return False  # Block message
    
    # Increment message count for FREE users
    SubscriptionManager.increment_message_count(user)
    
    # Track message sent
    remaining = SubscriptionManager.get_remaining_messages(user)
    Analytics.track_event(user_id, 'message_sent', {
        'tier': user.subscription_tier,
        'remaining': remaining
    })
    
    # Warn if approaching limit (1 message left)
    if remaining == 1:
        tier = SubscriptionManager.get_user_tier(user)
        if tier == SubscriptionTier.FREE:
            await update.message.reply_text(
                "âš ï¸ **CÃ²n 1 tin nháº¯n cuá»‘i cÃ¹ng hÃ´m nay!**\n\n"
                "ðŸ’Ž NÃ¢ng cáº¥p Premium = Unlimited messages + AI insights\n\n"
                "ðŸŽ DÃ¹ng thá»­ FREE 7 ngÃ y!",
                parse_mode="Markdown"
            )
    
    return True  # Allow message


async def send_upgrade_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, error_msg: str):
    """Send upgrade prompt when user hits limit"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸŽ DÃ¹ng thá»­ Premium 7 ngÃ y FREE", callback_data="start_trial")],
        [InlineKeyboardButton("ðŸ’Ž Xem gÃ³i Premium", callback_data="view_premium")],
        [InlineKeyboardButton("ðŸ“Š Táº¡i sao nÃªn nÃ¢ng cáº¥p?", callback_data="why_premium")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
{error_msg}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’Ž **PREMIUM = UNLIMITED**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ¨ KhÃ´ng giá»›i háº¡n tin nháº¯n
ðŸ§  AI phÃ¢n tÃ­ch tÃ i chÃ­nh
ðŸ“Š Dashboard thÃ´ng minh
ðŸŽ¯ Gá»£i Ã½ cÃ¡ nhÃ¢n hÃ³a
ðŸš€ Há»— trá»£ Æ°u tiÃªn 30 phÃºt

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’° **CHá»ˆ 83K/THÃNG**
(= 1 ly cÃ  phÃª/tuáº§n)

ðŸŽ **DÃ¹ng thá»­ FREE 7 ngÃ y - KhÃ´ng cáº§n tháº»!**
"""
    
    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_trial_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle trial start callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    if not user:
        await query.edit_message_text("âŒ Lá»—i: KhÃ´ng tÃ¬m tháº¥y thÃ´ng tin user")
        return
    
    # Check if already on trial or premium
    tier = SubscriptionManager.get_user_tier(user)
    if tier in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await query.edit_message_text(
            f"âœ… Báº¡n Ä‘ang dÃ¹ng {tier.value}!\n\n"
            f"Sá»­ dá»¥ng /mystatus Ä‘á»ƒ xem chi tiáº¿t."
        )
        return
    
    # Start 7-day trial (pass scheduler for job scheduling)
    scheduler = context.application.job_queue.scheduler if hasattr(context.application, 'job_queue') else None
    SubscriptionManager.start_trial(user, days=7, scheduler=scheduler)
    
    # Track conversion
    Analytics.track_event(user_id, 'trial_started', {
        'source': 'chat_limit_hit'
    })
    
    from datetime import datetime
    trial_end = user.trial_ends_at.strftime('%d/%m/%Y %H:%M') if user.trial_ends_at else 'N/A'
    
    message = f"""
ðŸŽ‰ **CHÃšC Má»ªNG! KÃCH HOáº T THÃ€NH CÃ”NG**

âœ… Premium Trial Ä‘Ã£ Ä‘Æ°á»£c kÃ­ch hoáº¡t!

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
â° **THÃ”NG TIN:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŽ Trial: 7 ngÃ y miá»…n phÃ­
ðŸ“… Káº¿t thÃºc: {trial_end}
ðŸ’³ KhÃ´ng cáº§n tháº» tÃ­n dá»¥ng

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
âœ¨ **ÄÃƒ Má»ž KHÃ“A:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… Unlimited tin nháº¯n vá»›i bot
âœ… AI phÃ¢n tÃ­ch tÃ i chÃ­nh thÃ´ng minh  
âœ… Dashboard chi tiÃªu trá»±c quan
âœ… Gá»£i Ã½ cÃ¡ nhÃ¢n hÃ³a má»—i ngÃ y
âœ… Há»— trá»£ Æ°u tiÃªn trong 30 phÃºt

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸš€ **BÆ¯á»šC TIáº¾P THEO:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

1ï¸âƒ£ CÃ i Ä‘áº·t Web App (30 giÃ¢y)
2ï¸âƒ£ Xem hÆ°á»›ng dáº«n sá»­ dá»¥ng
3ï¸âƒ£ Báº¯t Ä‘áº§u quáº£n lÃ½ tÃ i chÃ­nh!

ðŸ‘‡ Chá»n hÃ nh Ä‘á»™ng bÃªn dÆ°á»›i:
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ“± HÆ°á»›ng dáº«n cÃ i Web App", callback_data="webapp_setup_guide")],
        [InlineKeyboardButton("ðŸ“– HÆ°á»›ng dáº«n sá»­ dá»¥ng Premium", callback_data="premium_usage_guide")],
        [InlineKeyboardButton("ðŸ  Xem menu Premium", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"User {user_id} started 7-day trial")


async def handle_view_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view premium info callback"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ’Ž **GÃ“I PREMIUM**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’° **GIÃ:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

999,000 VNÄ/nÄƒm
= 83,250 VNÄ/thÃ¡ng
= 2,750 VNÄ/ngÃ y (1 ly cÃ  phÃª/tuáº§n!)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
âœ¨ **TÃNH NÄ‚NG:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¬ **Unlimited messages** (vs FREE 5/day)
ðŸ§  **AI phÃ¢n tÃ­ch tÃ i chÃ­nh** - Auto insights
ðŸ“Š **Dashboard thÃ´ng minh** - Real-time
ðŸŽ¯ **Gá»£i Ã½ cÃ¡ nhÃ¢n hÃ³a** - Context-aware
ðŸ“ **Ghi chi tiÃªu 1-click** - NLP parser
ðŸ› ï¸ **Managed setup** - LÃ m giÃºp 5 phÃºt
ðŸš€ **Há»— trá»£ Æ°u tiÃªn** - Tráº£ lá»i 30 phÃºt
ðŸ“ˆ **ROI tracking** - Xem lá»£i nhuáº­n
ðŸ’¾ **Export bÃ¡o cÃ¡o** - Excel + PDF

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
â±ï¸ **TIáº¾T KIá»†M:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

~6.5 giá»/thÃ¡ng = 650K value
Chi: 83K
â†’ **ROI: 780%** ðŸš€

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸŽ **Æ¯U ÄÃƒI:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… DÃ¹ng thá»­ 7 ngÃ y FREE
âœ… KhÃ´ng cáº§n tháº» tÃ­n dá»¥ng
âœ… Huá»· báº¥t cá»© lÃºc nÃ o
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸŽ DÃ¹ng thá»­ FREE 7 ngÃ y", callback_data="start_trial")],
        [InlineKeyboardButton("Â« Quay láº¡i", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_why_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle why upgrade callback"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ¤” **Táº I SAO NÃŠN NÃ‚NG Cáº¤P?**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
â° **TIáº¾T KIá»†M THá»œI GIAN:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âŒ FREE: Má»Ÿ Sheet, tÃ¬m data, tá»± tÃ­nh = 10 phÃºt
âœ… PREMIUM: Há»i bot, nháº­n ngay = 5 giÃ¢y

**Má»—i ngÃ y tiáº¿t kiá»‡m 15-20 phÃºt!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’° **Ráºº HÆ N 1 LY CÃ€ PHÃŠ:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

83K/thÃ¡ng = 2,750 VNÄ/ngÃ y

So sÃ¡nh:
â€¢ 1 ly Highlands: ~50K
â€¢ 1 bá»¯a cÆ¡m: ~70K
â€¢ Premium: 3K/ngÃ y!

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸš€ **ÄÆ¯á»¢C GÃŒ?**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… Trá»£ lÃ½ AI 24/7 khÃ´ng giá»›i háº¡n
âœ… Setup giÃºp báº¡n (khÃ´ng tá»± lÃ m)
âœ… Insights tá»± Ä‘á»™ng (khÃ´ng tá»± tÃ­nh)
âœ… Priority support (30 phÃºt tráº£ lá»i)

â†’ **KhÃ´ng pháº£i "feature bundle"**
â†’ **LÃ  "trá»£ lÃ½ cÃ¡ nhÃ¢n" tháº­t sá»±**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“Š **CASE STUDY:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

User A (FREE):
â€¢ Má»Ÿ Sheet 10 láº§n/ngÃ y = 30 phÃºt
â€¢ Tá»± lÃ m report = 1 giá»/tuáº§n
â€¢ Tá»± debug lá»—i = 2 giá»/thÃ¡ng

**Total: 13 giá»/thÃ¡ng lÃ£ng phÃ­**

User B (PREMIUM):
â€¢ Há»i bot = 5 giÃ¢y
â€¢ Report tá»± Ä‘á»™ng = 0 phÃºt
â€¢ Priority support fix ngay

**Total: 13 giá»/thÃ¡ng tiáº¿t kiá»‡m = 1.3M value**

Chi: 83K
â†’ ROI: **1,466%** ðŸš€
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸŽ OK, tÃ´i dÃ¹ng thá»­!", callback_data="start_trial")],
        [InlineKeyboardButton("Â« Quay láº¡i", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

