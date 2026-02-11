"""
VIP Identity Tier Handler
Rising Star (10 refs) â†’ Super VIP (50 refs) â†’ Legend (100 refs)

VIP = Identity Layer, NOT sales layer
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.utils.database import get_user_by_id
from loguru import logger
from datetime import datetime


# VIP Milestones Configuration
VIP_MILESTONES = {
    10: {
        'tier': 'RISING_STAR',
        'name': 'â­ Rising Star',
        'benefits': [
            'VIP Telegram group access',
            'Early access to beta features',
            '20% Premium discount (if interested)',
            'Direct feedback channel'
        ],
        'message': """
â­ðŸŽ‰ RISING STAR UNLOCKED!

Báº¡n Ä‘Ã£ giÃºp 10 ngÆ°á»i báº¯t Ä‘áº§u quáº£n lÃ½ tiá»n!

ðŸŽ¯ Báº¡n giá» lÃ  VIP Rising Star:
â€¢ Truy cáº­p VIP Community group
â€¢ Early access features má»›i
â€¢ Voice trong roadmap sáº£n pháº©m

Welcome to the inner circle! ðŸš€

[Join VIP Group] [Roadmap] [Badge]
"""
    },
    50: {
        'tier': 'SUPER_VIP',
        'name': 'ðŸ† Super VIP',
        'benefits': [
            'Premium 1 year FREE',
            'Founder office hours access',
            'Feature voting rights',
            'Monthly strategy sessions'
        ],
        'message': """
ðŸ†ðŸ”¥ SUPER VIP UNLOCKED!

50 ngÆ°á»i! Báº¡n Ä‘Ã£ chá»©ng minh niá»m tin vÃ o Freedom Wallet!

ðŸŽ¯ Báº¡n giá» lÃ  Super VIP:
â€¢ Premium 1 nÄƒm FREE (gift)
â€¢ Direct line to founder
â€¢ Feature voting rights
â€¢ Exclusive training

You're now part of the core! ðŸ’Ž

[Activate Premium] [Founder AMA] [VIP Portal]
"""
    },
    100: {
        'tier': 'LEGEND',
        'name': 'ðŸ‘‘ Legend',
        'benefits': [
            'Premium LIFETIME FREE',
            'Co-creator status',
            'Annual VIP retreat',
            'Product advisory board'
        ],
        'message': """
ðŸ‘‘âœ¨ LEGEND STATUS!

100 ngÆ°á»i! Báº¡n lÃ  Champion thá»±c thá»¥ cá»§a Freedom Wallet!

ðŸŽ¯ Báº¡n giá» lÃ  Legend:
â€¢ Premium LIFETIME FREE
â€¢ Co-creator credit
â€¢ Annual VIP retreat
â€¢ Advisory board seat

You've built something bigger! ðŸŒŸ

[Activate Lifetime] [Legend Portal] [Impact]
"""
    }
}


async def check_vip_milestone(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Check and grant VIP milestone rewards
    Called after successful referral in referral.py
    
    Args:
        user_id: Telegram user ID of referrer
        context: Telegram context
    
    Returns:
        bool: True if milestone was reached, False otherwise
    """
    db_user = await get_user_by_id(user_id)
    if not db_user:
        return False
    
    referral_count = db_user.referral_count
    
    # Check if user just hit a milestone
    if referral_count not in VIP_MILESTONES:
        return False
    
    milestone = VIP_MILESTONES[referral_count]
    
    # Update user VIP status in database
    try:
        # Update VIP fields
        db_user.vip_tier = milestone['tier']
        db_user.vip_unlocked_at = datetime.utcnow()
        db_user.vip_benefits = milestone['benefits']
        
        # Commit to database
        from app.utils.database import db_session
        db_session.commit()
        
        logger.info(f"âœ… User {user_id} reached VIP milestone: {milestone['tier']} ({referral_count} refs)")
    except Exception as e:
        logger.error(f"âŒ Failed to update VIP status for user {user_id}: {e}")
        return False
    
    # Send VIP unlock message
    keyboard = [
        [InlineKeyboardButton("ðŸŽ Xem quyá»n lá»£i VIP", callback_data=f"vip_benefits_{milestone['tier']}")],
        [InlineKeyboardButton("ðŸ‘¥ Join VIP Group", url="https://t.me/+vBZk4Kq59P9mMzY1")],
        [InlineKeyboardButton("ðŸ—ºï¸ Xem Roadmap", callback_data="vip_roadmap")]
    ]
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=milestone['message'],
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        logger.info(f"âœ… Sent VIP unlock message to user {user_id}")
        return True
    except Exception as e:
        logger.error(f"âŒ Failed to send VIP message to user {user_id}: {e}")
        return False


async def vip_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /vip command - Show user's current VIP status
    """
    user = update.effective_user
    db_user = await get_user_by_id(user.id)
    
    if not db_user:
        await update.message.reply_text("âŒ Lá»—i: User khÃ´ng tÃ¬m tháº¥y")
        return
    
    referral_count = db_user.referral_count or 0
    vip_tier = db_user.vip_tier if hasattr(db_user, 'vip_tier') else None
    
    # Determine current & next milestone
    if referral_count >= 100:
        current_status = "ðŸ‘‘ Legend"
        next_milestone = None
    elif referral_count >= 50:
        current_status = "ðŸ† Super VIP"
        next_milestone = f"{100 - referral_count} refs â†’ ðŸ‘‘ Legend"
    elif referral_count >= 10:
        current_status = "â­ Rising Star"
        next_milestone = f"{50 - referral_count} refs â†’ ðŸ† Super VIP"
    else:
        current_status = "Community Member"
        next_milestone = f"{10 - referral_count} refs â†’ â­ Rising Star"
    
    # Get benefits for current tier
    current_benefits = []
    if referral_count >= 10:
        for threshold in [10, 50, 100]:
            if referral_count >= threshold:
                current_benefits.extend(VIP_MILESTONES[threshold]['benefits'])
    
    if not current_benefits:
        current_benefits = ['Share to help friends unlock FREE']
    
    message = f"""
ðŸ† **VIP STATUS**

ðŸ“Š **Hiá»‡n táº¡i:**
â€¢ Status: {current_status}
â€¢ Referrals: {referral_count}

{f"ðŸŽ¯ **Next Milestone:**\nâ€¢ {next_milestone}" if next_milestone else "ðŸŽ‰ **You've reached the top!**"}

ðŸ’¡ **VIP Benefits:**
{chr(10).join(f"â€¢ {b}" for b in current_benefits[:5])}
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ‘¥ VIP Community", url="https://t.me/+vBZk4Kq59P9mMzY1")],
        [InlineKeyboardButton("ðŸ—ºï¸ Product Roadmap", callback_data="vip_roadmap")],
        [InlineKeyboardButton("Â« Back", callback_data="back_to_menu")]
    ]
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def handle_vip_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle callback: vip_benefits_{TIER}
    Show detailed benefits for VIP tier
    """
    query = update.callback_query
    await query.answer()
    
    # Extract tier from callback data
    tier = query.data.replace("vip_benefits_", "")
    
    # Find milestone config
    milestone = None
    for count, config in VIP_MILESTONES.items():
        if config['tier'] == tier:
            milestone = config
            break
    
    if not milestone:
        await query.edit_message_text("âŒ Lá»—i: KhÃ´ng tÃ¬m tháº¥y thÃ´ng tin VIP tier")
        return
    
    message = f"""
{milestone['name']} **BENEFITS**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

{chr(10).join(f"âœ“ {b}" for b in milestone['benefits'])}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¡ **Note:** VIP lÃ  vá» identity & belonging,
khÃ´ng pháº£i vá» sales. Enjoy the journey! ðŸš€
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ‘¥ Join VIP Group", url="https://t.me/+vBZk4Kq59P9mMzY1")],
        [InlineKeyboardButton("Â« Back", callback_data="vip_status")]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def handle_vip_roadmap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle callback: vip_roadmap
    Show product roadmap
    """
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ—ºï¸ **PRODUCT ROADMAP**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸš§ **IN PROGRESS:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

â€¢ AI-powered budgeting suggestions
â€¢ Multi-currency support
â€¢ Investment tracking improvements

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“‹ **UPCOMING (Q2 2026):**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

â€¢ Family accounts
â€¢ Goal tracking v2
â€¢ Bank integration (beta)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ **VIP VOTING:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

As a VIP, you can vote on feature priority!
Join VIP group to participate.
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ‘¥ Join VIP Group", url="https://t.me/+vBZk4Kq59P9mMzY1")],
        [InlineKeyboardButton("Â« Back", callback_data="vip_status")]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# Export handler registration function
def register_vip_handlers(application):
    """
    Register all VIP-related handlers
    Call this from main.py
    """
    from telegram.ext import CommandHandler, CallbackQueryHandler
    
    # Command handlers
    application.add_handler(CommandHandler("vip", vip_status_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(handle_vip_benefits, pattern="^vip_benefits_"))
    application.add_handler(CallbackQueryHandler(handle_vip_roadmap, pattern="^vip_roadmap$"))
    
    logger.info("âœ… VIP handlers registered")

