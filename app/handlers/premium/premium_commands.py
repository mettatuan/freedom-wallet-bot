"""
Premium Commands - Handlers for Premium menu buttons
6 main buttons: Ghi chi tiÃªu, TÃ¬nh hÃ¬nh, PhÃ¢n tÃ­ch, Gá»£i Ã½, Setup, Há»— trá»£

Design principle: 1 nÃºt = 1 hÃ nh Ä‘á»™ng quen thuá»™c
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime
from app.utils.database import get_user_by_id
from app.services.recommendation import get_recommendation_for_user, get_greeting


async def quick_record_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ðŸ’¬ Ghi chi tiÃªu nhanh
    
    HÃ nh vi láº·p nhiá»u nháº¥t - Neo thÃ³i quen
    Premium cáº£m nháº­n "nháº¹ Ä‘áº§u" rÃµ nháº¥t
    """
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user = await get_user_by_id(user_id)
        
        greeting = get_greeting(user) if user else "ðŸ‘‹ Xin chÃ o!"
        
        message = f"""
{greeting}

ðŸ’¬ **GHI CHI TIÃŠU NHANH**

Báº¡n chi bao nhiÃªu vÃ  cho viá»‡c gÃ¬?

**VÃ­ dá»¥:**
â€¢ "50k cÃ  phÃª"
â€¢ "200k Äƒn trÆ°a"
â€¢ "1tr5 tiá»n nhÃ "

ðŸ’¡ TÃ´i sáº½ hiá»ƒu vÃ  ghi vÃ o Sheet cho báº¡n!
"""
        
        keyboard = [
            [InlineKeyboardButton("Â« Quay láº¡i", callback_data="premium_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Premium user {user_id} opened quick record")
    except Exception as e:
        logger.error(f"Error in quick_record_handler: {e}", exc_info=True)
        await query.edit_message_text(
            "ðŸ˜“ CÃ³ lá»—i xáº£y ra. Vui lÃ²ng thá»­ láº¡i sau!",
            parse_mode="Markdown"
        )


async def today_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ðŸ“Š TÃ¬nh hÃ¬nh hÃ´m nay
    
    Thay tháº¿ cho: /balance, /today, /status
    User khÃ´ng cáº§n biáº¿t há»i cÃ¢u nÃ o
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    if not user:
        await query.edit_message_text("âŒ KhÃ´ng tÃ¬m tháº¥y thÃ´ng tin cá»§a báº¡n.")
        return
    
    # Get today's stats (mock for now - replace with real data)
    today_spent = "450K"  # TODO: Get from Sheet
    budget = "500K"  # TODO: Get from Sheet
    remaining = "50K"
    recorded_today = user.last_transaction_date == datetime.now().date() if user.last_transaction_date else False
    
    message = f"""
ðŸ“Š **TÃŒNH HÃŒNH HÃ”M NAY**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’° **CHI TIÃŠU:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ÄÃ£ chi: {today_spent}
NgÃ¢n sÃ¡ch: {budget}
CÃ²n láº¡i: {remaining}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“ **GIAO Dá»ŠCH:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

{'âœ… ÄÃ£ ghi giao dá»‹ch hÃ´m nay' if recorded_today else 'âš ï¸ ChÆ°a ghi giao dá»‹ch nÃ o'}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ”¥ **STREAK:** {user.streak_count if user else 0} ngÃ y
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¡ {'Tuyá»‡t vá»i! HÃ£y tiáº¿p tá»¥c!' if recorded_today else 'HÃ£y ghi giao dá»‹ch Ä‘á»ƒ giá»¯ streak!'}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("ðŸ“ Ghi ngay", callback_data="quick_record"),
            InlineKeyboardButton("ðŸ§  PhÃ¢n tÃ­ch", callback_data="analysis")
        ],
        [InlineKeyboardButton("Â« Quay láº¡i", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} checked today's status")


async def analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ðŸ§  PhÃ¢n tÃ­ch cho tÃ´i
    
    NÃºt "giÃ¡ trá»‹ Premium"
    KhÃ´ng cáº§n chá»n loáº¡i phÃ¢n tÃ­ch - Bot tá»± quyáº¿t â†’ Ä‘Ãºng vai trá»£ lÃ½
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    # Show loading message
    await query.edit_message_text("ðŸ§  Äang phÃ¢n tÃ­ch dá»¯ liá»‡u cá»§a báº¡n...\n\nâ³ Vui lÃ²ng Ä‘á»£i 2-3 giÃ¢y...")
    
    # TODO: Real analysis from Sheet data
    # For now, show mock analysis
    import asyncio
    await asyncio.sleep(2)
    
    message = f"""
ðŸ§  **PHÃ‚N TÃCH TÃ€I CHÃNH**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“Š **TUáº¦N NÃ€Y:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… **LÃ m tá»‘t:**
â€¢ Ghi chÃ©p Ä‘á»u Ä‘áº·n 7/7 ngÃ y
â€¢ Chi tiÃªu hÅ© NEC giáº£m 20%

âš ï¸ **Cáº§n chÃº Ã½:**
â€¢ Chi hÅ© PLAY tÄƒng 35% (vÆ°á»£t 150K)
â€¢ 3 khoáº£n chi "linh tinh" chÆ°a phÃ¢n loáº¡i

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ **Gá»¢I Ã:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

1. Xem láº¡i khoáº£n chi PLAY (cÃ³ thá»ƒ giáº£m)
2. PhÃ¢n loáº¡i 3 khoáº£n "linh tinh" Ä‘á»ƒ rÃµ rÃ ng
3. Tuáº§n sau nÃªn giá»¯ má»©c chi hiá»‡n táº¡i

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“ˆ **XU HÆ¯á»šNG:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

NhÃ¬n chung báº¡n Ä‘ang lÃ m ráº¥t tá»‘t! ðŸŽ‰
Tiáº¿p tá»¥c duy trÃ¬ streak vÃ  kiá»ƒm soÃ¡t chi tiÃªu.
"""
    
    keyboard = [
        [
            InlineKeyboardButton("ðŸ“Š Xem chi tiáº¿t", callback_data="detailed_report"),
            InlineKeyboardButton("ðŸ’¾ Xuáº¥t bÃ¡o cÃ¡o", callback_data="export_report")
        ],
        [InlineKeyboardButton("Â« Quay láº¡i", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} requested analysis")


async def recommendation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ðŸŽ¯ Gá»£i Ã½ tiáº¿p theo â­ (NÃšT QUAN TRá»ŒNG NHáº¤T)
    
    "Menu Ä‘á» xuáº¥t" Ä‘Ãºng nghÄ©a
    Bot chá»§ Ä‘á»™ng Ä‘á» xuáº¥t viá»‡c user nÃªn lÃ m tiáº¿p theo
    
    ðŸ‘‰ User má»Ÿ bot chá»‰ Ä‘á»ƒ báº¥m nÃºt nÃ y
    ðŸ‘‰ Retention tÄƒng máº¡nh
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get personalized recommendation from engine
    recommendation = get_recommendation_for_user(user_id)
    
    message = f"""
{recommendation['emoji']} **{recommendation['title']}**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

{recommendation['message']}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ *TÃ´i luÃ´n theo dÃµi vÃ  gá»£i Ã½ cho báº¡n!*
"""
    
    # Dynamic keyboard based on recommendation action
    keyboard = []
    
    if recommendation['action'] == 'quick_record':
        keyboard.append([InlineKeyboardButton("ðŸ“ Ghi ngay", callback_data="quick_record")])
    elif recommendation['action'] == 'today_summary':
        keyboard.append([InlineKeyboardButton("ðŸ“Š Xem tÃ¬nh hÃ¬nh", callback_data="today_status")])
    elif recommendation['action'] in ['last_week_analysis', 'month_analysis']:
        keyboard.append([InlineKeyboardButton("ðŸ§  PhÃ¢n tÃ­ch ngay", callback_data="analysis")])
    else:
        keyboard.append([InlineKeyboardButton("ðŸ“Š Xem dashboard", callback_data="today_status")])
    
    keyboard.append([InlineKeyboardButton("Â« Quay láº¡i", callback_data="premium_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} checked recommendation - action: {recommendation['action']}")


async def setup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ðŸ› ï¸ Setup giÃºp tÃ´i
    
    KhÃ¡c biá»‡t Premium ráº¥t rÃµ
    BÃ¡n "tiáº¿t kiá»‡m thá»i gian", khÃ´ng bÃ¡n feature
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    message = f"""
ðŸ› ï¸ **MANAGED SETUP SERVICE**

Äá»ƒ tÃ´i setup giÃºp báº¡n trong 5 phÃºt! âš¡

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“‹ **QUY TRÃŒNH:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

1ï¸âƒ£ Báº¡n cho tÃ´i quyá»n truy cáº­p Sheet
2ï¸âƒ£ TÃ´i copy template + cáº¥u hÃ¬nh
3ï¸âƒ£ TÃ´i setup Apps Script
4ï¸âƒ£ TÃ´i test vÃ  bÃ n giao
5ï¸âƒ£ Báº¡n dÃ¹ng ngay!

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
â±ï¸ **THá»œI GIAN:** 5-10 phÃºt
âœ… **MIá»„N PHÃ** cho Premium
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¡ Báº¡n chá»‰ cáº§n ngá»“i uá»‘ng cÃ  phÃª, tÃ´i lo pháº§n cÃ²n láº¡i!

ðŸ“§ **LiÃªn há»‡ ngay:**
â†’ @freedom_wallet_admin
â†’ email@freedomwallet.app
"""
    
    keyboard = [
        [
            InlineKeyboardButton("ðŸ“§ Chat Admin", url="https://t.me/freedom_wallet_admin"),
            InlineKeyboardButton("ðŸ“… Äáº·t lá»‹ch", callback_data="schedule_setup")
        ],
        [InlineKeyboardButton("ðŸ“¹ Hoáº·c tá»± setup", callback_data="guide_self_setup")],
        [InlineKeyboardButton("Â« Quay láº¡i", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} requested setup service")


async def priority_support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ðŸš€ Há»— trá»£ Æ°u tiÃªn
    
    Premium cáº£m tháº¥y Ä‘Æ°á»£c chÄƒm sÃ³c
    Giáº£m churn, táº¡o cáº£m giÃ¡c "VIP tháº­t"
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    message = f"""
ðŸš€ **Há»– TRá»¢ Æ¯U TIÃŠN - PREMIUM**

Báº¡n cÃ³ quyá»n Ä‘Æ°á»£c há»— trá»£ nhanh chÃ³ng! âš¡

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
â±ï¸ **CAM Káº¾T:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ“± Chat: Tráº£ lá»i trong **30 phÃºt**
ðŸ“§ Email: Tráº£ lá»i trong **2 giá»**
ðŸ“ž Gá»i Ä‘iá»‡n: Äáº·t lá»‹ch trong ngÃ y

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ **CÃC Váº¤N Äá»€ Æ¯U TIÃŠN:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… Há»i phá»©c táº¡p vá» cÃ´ng thá»©c
âœ… Lá»—i khÃ´ng load Ä‘Æ°á»£c dá»¯ liá»‡u
âœ… Cáº§n phÃ¢n tÃ­ch/tÆ° váº¥n ngay
âœ… Sá»± cá»‘ kháº©n cáº¥p vá»›i app

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“ž **LIÃŠN Há»†:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¬ Telegram: @freedom_wallet_admin
ðŸ“§ Email: support@freedomwallet.app
ðŸ“… Äáº·t lá»‹ch gá»i: [Link]

ðŸ’¡ *ChÃºng tÃ´i sáºµn sÃ ng há»— trá»£ 24/7!*
"""
    
    keyboard = [
        [
            InlineKeyboardButton("ðŸ’¬ Chat ngay", url="https://t.me/freedom_wallet_admin")
        ],
        [
            InlineKeyboardButton("ðŸ“§ Gá»­i email", callback_data="send_email"),
            InlineKeyboardButton("ðŸ“… Äáº·t lá»‹ch", callback_data="schedule_call")
        ],
        [InlineKeyboardButton("Â« Quay láº¡i", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} accessed priority support")


async def premium_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show Premium main menu (6 buttons)
    Called from callback_data="premium_menu"
    """
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user = await get_user_by_id(user_id)
        
        greeting = get_greeting(user) if user else "ðŸ‘‹ Xin chÃ o!"
        
        message = f"""
{greeting}

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’Ž **TRá»¢ LÃ TÃ€I CHÃNH Cá»¦A Báº N**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

TÃ´i luÃ´n sáºµn sÃ ng há»— trá»£ báº¡n 24/7! ðŸ¤–

ðŸ“Š **HÃ´m nay:** {datetime.now().strftime('%d/%m/%Y')}
ðŸ”¥ **Streak cá»§a báº¡n:** {user.streak_count if user else 0} ngÃ y

ðŸ’¡ Chá»n viá»‡c báº¡n muá»‘n lÃ m:
"""
        
        keyboard = [
            [
                InlineKeyboardButton("ðŸ’¬ Ghi chi tiÃªu nhanh", callback_data="quick_record"),
                InlineKeyboardButton("ðŸ“Š TÃ¬nh hÃ¬nh hÃ´m nay", callback_data="today_status")
            ],
            [
                InlineKeyboardButton("ðŸ§  PhÃ¢n tÃ­ch cho tÃ´i", callback_data="analysis"),
                InlineKeyboardButton("ðŸŽ¯ Gá»£i Ã½ tiáº¿p theo", callback_data="recommendation")
            ],
            [
                InlineKeyboardButton("ðŸ› ï¸ Setup giÃºp tÃ´i", callback_data="setup"),
                InlineKeyboardButton("ðŸš€ Há»— trá»£ Æ°u tiÃªn", callback_data="priority_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Premium user {user_id} opened premium menu")
    except Exception as e:
        logger.error(f"Error in premium_menu_handler: {e}", exc_info=True)
        await query.edit_message_text(
            "ðŸ˜“ CÃ³ lá»—i xáº£y ra. Vui lÃ²ng gÃµ /start Ä‘á»ƒ quay vá» trang chá»§!",
            parse_mode="Markdown"
        )


# Callback routing map
PREMIUM_CALLBACKS = {
    'quick_record': quick_record_handler,
    'today_status': today_status_handler,
    'analysis': analysis_handler,
    'recommendation': recommendation_handler,
    'setup': setup_handler,
    'priority_support': priority_support_handler,
    'premium_menu': premium_menu_handler,
}

