"""
Example Implementation: Premium Menu Integration
How to use the new keyboards_premium module
"""
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.utils.keyboards_premium import (
    premium_main_menu,
    finance_menu,
    reports_menu,
    goals_menu,
    ai_insights_menu,
    settings_menu,
    help_menu,
    balance_view_menu,
    quick_record_category_menu,
    jar_selection_menu,
    back_to_menu_button
)
import logging

logger = logging.getLogger(__name__)


# ============================================
# MAIN PREMIUM MENU HANDLER
# ============================================

async def show_premium_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display main premium menu
    Entry point for premium users
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get user data (example)
    # user = get_user_by_id(user_id)
    # streak = user.current_streak if user else 0
    streak = 7  # Mock data
    
    message = f"""
ðŸŒŸ **FREEDOM WALLET PREMIUM**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’Ž ChÃ o má»«ng báº¡n Ä‘áº¿n vá»›i Premium!
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“Š **HÃ´m nay:** 09/02/2026
ðŸ”¥ **Streak:** {streak} ngÃ y
ðŸ’° **Sá»‘ dÆ°:** 5,000,000 â‚«

ðŸ’¡ Chá»n chá»©c nÄƒng báº¡n muá»‘n sá»­ dá»¥ng:
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=premium_main_menu()
    )
    
    logger.info(f"User {user_id} opened premium menu")


# ============================================
# SUB-MENU HANDLERS
# ============================================

async def show_finance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show finance sub-menu"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ’° **TÃ€I CHÃNH**

Quáº£n lÃ½ giao dá»‹ch vÃ  sá»‘ dÆ° cá»§a báº¡n.
Chá»n thao tÃ¡c báº¡n muá»‘n thá»±c hiá»‡n:
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=finance_menu()
    )


async def show_reports_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show reports sub-menu"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ“Š **BÃO CÃO & PHÃ‚N TÃCH**

Xem chi tiáº¿t thu chi vÃ  xu hÆ°á»›ng chi tiÃªu.
Chá»n khoáº£ng thá»i gian:
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reports_menu()
    )


async def show_goals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show goals sub-menu"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸŽ¯ **Má»¤C TIÃŠU & NGÃ‚N SÃCH**

Theo dÃµi tiáº¿n Ä‘á»™ vÃ  quáº£n lÃ½ ngÃ¢n sÃ¡ch.
Báº¡n muá»‘n lÃ m gÃ¬?
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=goals_menu()
    )


async def show_ai_insights_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show AI insights sub-menu"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ¤– **AI INSIGHTS**

PhÃ¢n tÃ­ch thÃ´ng minh vÃ  gá»£i Ã½ cÃ¡ nhÃ¢n hÃ³a.
KhÃ¡m phÃ¡ cÃ¡c tÃ­nh nÄƒng AI:
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=ai_insights_menu()
    )


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings sub-menu"""
    query = update.callback_query
    await query.answer()
    
    message = """
âš™ï¸ **CÃ€I Äáº¶T**

TÃ¹y chá»‰nh bot theo nhu cáº§u cá»§a báº¡n.
Chá»n má»¥c cÃ i Ä‘áº·t:
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=settings_menu()
    )


async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help sub-menu"""
    query = update.callback_query
    await query.answer()
    
    message = """
â“ **TRá»¢ GIÃšP & Há»– TRá»¢**

ChÃºng tÃ´i luÃ´n sáºµn sÃ ng há»— trá»£ báº¡n 24/7!
Báº¡n cáº§n giÃºp Ä‘á»¡ gÃ¬?
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=help_menu()
    )


# ============================================
# BALANCE VIEW HANDLERS
# ============================================

async def show_balance_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show balance viewing options"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ’³ **XEM Sá» DÆ¯**

Chá»n cÃ¡ch xem sá»‘ dÆ°:
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=balance_view_menu()
    )


async def show_balance_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show balance overview"""
    query = update.callback_query
    await query.answer("ðŸ”„ Äang táº£i sá»‘ dÆ°...")
    
    # Mock data - Replace with actual API call
    message = """
ðŸ’° **Tá»”NG QUAN Sá» DÆ¯**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
**Tá»•ng tÃ i sáº£n:** 10,500,000 â‚«
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**PhÃ¢n bá»• theo hÅ©:**
ðŸ’° NEC (55%): 5,775,000 â‚«
ðŸŽ¯ FFA (10%): 1,050,000 â‚«
ðŸ“š EDU (10%): 1,050,000 â‚«
ðŸŽ‰ PLAY (10%): 1,050,000 â‚«
ðŸ’ GIVE (5%): 525,000 â‚«
ðŸ’¼ LTSS (10%): 1,050,000 â‚«

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
**TÃ i khoáº£n:**
ðŸ’³ Cash: 3,500,000 â‚«
ðŸ¦ VCB: 5,000,000 â‚«
ðŸ’° MB: 2,000,000 â‚«

ðŸ”„ Cáº­p nháº­t: 09/02/2026 22:30
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=back_to_menu_button('view_balance')
    )


# ============================================
# QUICK RECORD WITH CATEGORIES
# ============================================

async def show_quick_record_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show category shortcuts for quick record"""
    query = update.callback_query
    await query.answer()
    
    message = """
âž• **GHI GIAO Dá»ŠCH NHANH**

Chá»n danh má»¥c chi tiÃªu:
(Sau Ä‘Ã³ nháº­p sá»‘ tiá»n)
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=quick_record_category_menu()
    )


async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Handle category selection"""
    query = update.callback_query
    await query.answer()
    
    # Store selected category in context
    context.user_data['selected_category'] = category
    context.user_data['waiting_for_amount'] = True
    
    category_names = {
        'food': 'ðŸ½ï¸ Ä‚n uá»‘ng',
        'family': 'ðŸ  Gia Ä‘Ã¬nh',
        'transport': 'ðŸš— Di chuyá»ƒn',
        'health': 'ðŸ’Š Sá»©c khá»e',
        'entertainment': 'ðŸŽ‰ Giáº£i trÃ­',
        'education': 'ðŸ“š Há»c táº­p',
        'shopping': 'ðŸ›ï¸ Mua sáº¯m',
        'other': 'âž• KhÃ¡c'
    }
    
    message = f"""
âž• **GHI GIAO Dá»ŠCH**

Danh má»¥c: **{category_names.get(category, 'N/A')}**

ðŸ“ Nháº­p sá»‘ tiá»n:
VÃ­ dá»¥: 50k, 100000, 1.5tr
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=back_to_menu_button('qr_start')
    )


# ============================================
# JAR TRANSFER HANDLERS
# ============================================

async def show_jar_transfer_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show jar selection for transfer source"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ”„ **CHUYá»‚N TIá»€N GIá»®A CÃC HÅ¨**

Chá»n hÅ© nguá»“n (chuyá»ƒn tá»«):
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=jar_selection_menu('transfer_from')
    )


async def show_jar_transfer_destination(update: Update, context: ContextTypes.DEFAULT_TYPE, from_jar: str):
    """Show jar selection for transfer destination"""
    query = update.callback_query
    await query.answer()
    
    # Store source jar
    context.user_data['transfer_from_jar'] = from_jar
    
    jar_names = {
        'NEC': 'ðŸ’° NEC',
        'FFA': 'ðŸŽ¯ FFA',
        'EDU': 'ðŸ“š EDU',
        'PLAY': 'ðŸŽ‰ PLAY',
        'GIVE': 'ðŸ’ GIVE',
        'LTSS': 'ðŸ’¼ LTSS'
    }
    
    message = f"""
ðŸ”„ **CHUYá»‚N TIá»€N GIá»®A CÃC HÅ¨**

Tá»«: **{jar_names.get(from_jar, 'N/A')}**

Chá»n hÅ© Ä‘Ã­ch (chuyá»ƒn Ä‘áº¿n):
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=jar_selection_menu('transfer_to')
    )


# ============================================
# CALLBACK ROUTING MAP
# ============================================

PREMIUM_MENU_CALLBACKS = {
    # Main menu
    'premium_menu': show_premium_menu,
    
    # Sub-menus
    'premium_finance': show_finance_menu,
    'premium_reports': show_reports_menu,
    'premium_goals': show_goals_menu,
    'premium_ai': show_ai_insights_menu,
    'premium_settings': show_settings_menu,
    'premium_help': show_help_menu,
    
    # Finance actions
    'view_balance': show_balance_options,
    'balance_overview': show_balance_overview,
    'qr_start': show_quick_record_categories,
    'jar_transfer': show_jar_transfer_source,
    
    # Add more handlers as needed...
}


# ============================================
# REGISTER HANDLERS
# ============================================

def register_premium_menu_handlers(application):
    """
    Register all premium menu handlers
    Call this in main.py during bot initialization
    """
    
    # Main menu handler
    application.add_handler(
        CallbackQueryHandler(show_premium_menu, pattern='^premium_menu$')
    )
    
    # Sub-menu handlers
    application.add_handler(
        CallbackQueryHandler(show_finance_menu, pattern='^premium_finance$')
    )
    application.add_handler(
        CallbackQueryHandler(show_reports_menu, pattern='^premium_reports$')
    )
    application.add_handler(
        CallbackQueryHandler(show_goals_menu, pattern='^premium_goals$')
    )
    application.add_handler(
        CallbackQueryHandler(show_ai_insights_menu, pattern='^premium_ai$')
    )
    application.add_handler(
        CallbackQueryHandler(show_settings_menu, pattern='^premium_settings$')
    )
    application.add_handler(
        CallbackQueryHandler(show_help_menu, pattern='^premium_help$')
    )
    
    # Balance handlers
    application.add_handler(
        CallbackQueryHandler(show_balance_options, pattern='^view_balance$')
    )
    application.add_handler(
        CallbackQueryHandler(show_balance_overview, pattern='^balance_overview$')
    )
    
    # Quick record handlers
    application.add_handler(
        CallbackQueryHandler(show_quick_record_categories, pattern='^qr_start$')
    )
    
    # Category selection handlers
    category_patterns = ['food', 'family', 'transport', 'health', 
                        'entertainment', 'education', 'shopping', 'other']
    for cat in category_patterns:
        application.add_handler(
            CallbackQueryHandler(
                lambda u, c, cat=cat: handle_category_selection(u, c, cat),
                pattern=f'^qr_cat_{cat}$'
            )
        )
    
    # Jar transfer handlers
    application.add_handler(
        CallbackQueryHandler(show_jar_transfer_source, pattern='^jar_transfer$')
    )
    
    logger.info("âœ… Premium menu handlers registered")


# ============================================
# USAGE IN MAIN.PY
# ============================================

"""
# In main.py, add this:

from app.handlers.premium_menu_implementation import register_premium_menu_handlers

def main():
    application = Application.builder().token(TOKEN).build()
    
    # ... other handlers ...
    
    # Register premium menu handlers
    register_premium_menu_handlers(application)
    
    application.run_polling()

if __name__ == '__main__':
    main()
"""

