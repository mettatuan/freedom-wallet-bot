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
🌟 **FREEDOM WALLET PREMIUM**

━━━━━━━━━━━━━━━━━━━━━
💎 Chào mừng bạn đến với Premium!
━━━━━━━━━━━━━━━━━━━━━

📊 **Hôm nay:** 09/02/2026
🔥 **Streak:** {streak} ngày
💰 **Số dư:** 5,000,000 ₫

💡 Chọn chức năng bạn muốn sử dụng:
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
💰 **TÀI CHÍNH**

Quản lý giao dịch và số dư của bạn.
Chọn thao tác bạn muốn thực hiện:
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
📊 **BÁO CÁO & PHÂN TÍCH**

Xem chi tiết thu chi và xu hướng chi tiêu.
Chọn khoảng thời gian:
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
🎯 **MỤC TIÊU & NGÂN SÁCH**

Theo dõi tiến độ và quản lý ngân sách.
Bạn muốn làm gì?
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
🤖 **AI INSIGHTS**

Phân tích thông minh và gợi ý cá nhân hóa.
Khám phá các tính năng AI:
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
⚙️ **CÀI ĐẶT**

Tùy chỉnh bot theo nhu cầu của bạn.
Chọn mục cài đặt:
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
❓ **TRỢ GIÚP & HỖ TRỢ**

Chúng tôi luôn sẵn sàng hỗ trợ bạn 24/7!
Bạn cần giúp đỡ gì?
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
💳 **XEM SỐ DƯ**

Chọn cách xem số dư:
"""
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=balance_view_menu()
    )


async def show_balance_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show balance overview"""
    query = update.callback_query
    await query.answer("🔄 Đang tải số dư...")
    
    # Mock data - Replace with actual API call
    message = """
💰 **TỔNG QUAN SỐ DƯ**

━━━━━━━━━━━━━━━━━━━━━
**Tổng tài sản:** 10,500,000 ₫
━━━━━━━━━━━━━━━━━━━━━

**Phân bổ theo hũ:**
💰 NEC (55%): 5,775,000 ₫
🎯 FFA (10%): 1,050,000 ₫
📚 EDU (10%): 1,050,000 ₫
🎉 PLAY (10%): 1,050,000 ₫
💝 GIVE (5%): 525,000 ₫
💼 LTSS (10%): 1,050,000 ₫

━━━━━━━━━━━━━━━━━━━━━
**Tài khoản:**
💳 Cash: 3,500,000 ₫
🏦 VCB: 5,000,000 ₫
💰 MB: 2,000,000 ₫

🔄 Cập nhật: 09/02/2026 22:30
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
➕ **GHI GIAO DỊCH NHANH**

Chọn danh mục chi tiêu:
(Sau đó nhập số tiền)
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
        'food': '🍽️ Ăn uống',
        'family': '🏠 Gia đình',
        'transport': '🚗 Di chuyển',
        'health': '💊 Sức khỏe',
        'entertainment': '🎉 Giải trí',
        'education': '📚 Học tập',
        'shopping': '🛍️ Mua sắm',
        'other': '➕ Khác'
    }
    
    message = f"""
➕ **GHI GIAO DỊCH**

Danh mục: **{category_names.get(category, 'N/A')}**

📝 Nhập số tiền:
Ví dụ: 50k, 100000, 1.5tr
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
🔄 **CHUYỂN TIỀN GIỮA CÁC HŨ**

Chọn hũ nguồn (chuyển từ):
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
        'NEC': '💰 NEC',
        'FFA': '🎯 FFA',
        'EDU': '📚 EDU',
        'PLAY': '🎉 PLAY',
        'GIVE': '💝 GIVE',
        'LTSS': '💼 LTSS'
    }
    
    message = f"""
🔄 **CHUYỂN TIỀN GIỮA CÁC HŨ**

Từ: **{jar_names.get(from_jar, 'N/A')}**

Chọn hũ đích (chuyển đến):
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
    
    logger.info("✅ Premium menu handlers registered")


# ============================================
# USAGE IN MAIN.PY
# ============================================

"""
# In main.py, add this:

from app.handlers.premium.premium_menu_implementation import register_premium_menu_handlers

def main():
    application = Application.builder().token(TOKEN).build()
    
    # ... other handlers ...
    
    # Register premium menu handlers
    register_premium_menu_handlers(application)
    
    application.run_polling()

if __name__ == '__main__':
    main()
"""

