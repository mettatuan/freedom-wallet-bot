"""
Inline Registration - Start registration from button click (not /register command)
"""

from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger


async def start_free_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start registration flow from button click"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Check if already registered
    from app.utils.database import get_user_by_id
    db_user = await get_user_by_id(user.id)
    
    if db_user and db_user.email and db_user.full_name:
        # Already registered, go to step 2
        await query.message.delete()
        await query.message.reply_text("Báº¡n Ä‘Ã£ Ä‘Äƒng kÃ½ rá»“i. Äang chuyá»ƒn Ä‘áº¿n bÆ°á»›c tiáº¿p theo...")
        
        # Import and call step 2
        from app.handlers.free_flow import free_step2_show_value
        # Create fake callback for step 2
        update.callback_query = query
        await free_step2_show_value(update, context)
        return
    
    # Not registered yet, guide to use /register command
    try:
        await query.message.delete()
    except:
        pass
    
    await query.message.reply_text(
        "ðŸ“ **Äá»ƒ Ä‘Äƒng kÃ½, vui lÃ²ng gÃµ lá»‡nh:**\n\n"
        "/register\n\n"
        "TÃ´i sáº½ hÆ°á»›ng dáº«n báº¡n tá»«ng bÆ°á»›c.",
        parse_mode="Markdown"
    )


