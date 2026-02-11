"""
FREE Flow - Step-by-step guided setup
No FOMO, no pressure, clear value proposition
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from app.utils.database import SessionLocal, User


async def free_check_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user has registration info"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Check if user has complete info
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        
        if db_user and db_user.email and db_user.full_name:
            # Has info, go to step 2
            logger.info(f"User {user.id} has registration info, proceeding to step 2")
            await free_step2_show_value(update, context)
        else:
            # No info yet, ask to register first
            logger.info(f"User {user.id} missing registration info")
            
            from pathlib import Path
            
            message = """
ChÃ o báº¡n,

Freedom Wallet khÃ´ng pháº£i má»™t app Ä‘á»ƒ báº¡n táº£i vá».
ÄÃ¢y lÃ  má»™t há»‡ thá»‘ng báº¡n tá»± sá»Ÿ há»¯u.

Má»—i ngÆ°á»i dÃ¹ng cÃ³:
â€¢ Google Sheet riÃªng
â€¢ Apps Script riÃªng
â€¢ Web App riÃªng

Dá»¯ liá»‡u náº±m trÃªn Drive cá»§a báº¡n.
KhÃ´ng phá»¥ thuá»™c vÃ o ai.

Äá»ƒ báº¯t Ä‘áº§u, vui lÃ²ng nháº­p lá»‡nh /register 
Ä‘á»ƒ Ä‘iá»n thÃ´ng tin Ä‘Äƒng kÃ½.
"""
            
            image_path = Path("media/images/web_apps.jpg")
            
            try:
                # Delete the original message
                await query.message.delete()
                
                # Send photo with caption
                await query.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption=message,
                    parse_mode="Markdown"
                )
                
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                await query.edit_message_text(
                    message,
                    parse_mode="Markdown"
                )
                
    finally:
        db.close()


async def free_step2_show_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 2 - Show value before any technical setup"""
    query = update.callback_query
    await query.answer()
    
    message = """
TrÆ°á»›c khi lÃ m báº¥t cá»© bÆ°á»›c ká»¹ thuáº­t nÃ o,
báº¡n cáº§n biáº¿t mÃ¬nh sáº½ nháº­n Ä‘Æ°á»£c Ä‘iá»u gÃ¬.

Khi há»‡ thá»‘ng hoÃ n táº¥t, báº¡n sáº½ tháº¥y:

â€¢ Tá»•ng tÃ i sáº£n hiá»‡n cÃ³
â€¢ DÃ²ng tiá»n thu â€“ chi theo thÃ¡ng
â€¢ 6 HÅ© tiá»n phÃ¢n bá»• tá»± Ä‘á»™ng
â€¢ Cáº¥p Ä‘á»™ tÃ i chÃ­nh hiá»‡n táº¡i cá»§a báº¡n
â€¢ TÃ¬nh tráº¡ng Ä‘áº§u tÆ°, ná»£ vÃ  tÃ i sáº£n

KhÃ´ng pháº£i Ä‘á»ƒ xem cho vui.
MÃ  Ä‘á»ƒ báº¡n biáº¿t rÃµ tiá»n cá»§a mÃ¬nh Ä‘ang á»Ÿ Ä‘Ã¢u.

Báº¡n sáºµn sÃ ng táº¡o há»‡ thá»‘ng cá»§a riÃªng mÃ¬nh chÆ°a?
"""
    
    keyboard = [
        [InlineKeyboardButton("Táº¡o há»‡ thá»‘ng", callback_data="free_step3_copy_template")],
        [InlineKeyboardButton("Há»i thÃªm", callback_data="free_ask_question")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def free_step3_copy_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 3 - Copy Google Sheet template"""
    query = update.callback_query
    await query.answer()
    
    message = """
**BÆ°á»›c 1: Táº¡o Google Sheet cá»§a riÃªng báº¡n.**

Nháº¥n nÃºt bÃªn dÆ°á»›i.
Chá»n "Táº¡o báº£n sao".
Äáº·t tÃªn theo Ã½ báº¡n.

Tá»« Ä‘Ã¢y trá»Ÿ Ä‘i,
Ä‘Ã¢y lÃ  há»‡ thá»‘ng tÃ i chÃ­nh cÃ¡ nhÃ¢n cá»§a báº¡n.
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ“‹ Copy Template", url="https://docs.google.com/spreadsheets/d/YOUR_TEMPLATE_ID/copy")],
        [InlineKeyboardButton("âœ… TÃ´i Ä‘Ã£ copy xong", callback_data="free_step4_deploy_script")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def free_step4_deploy_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 4 - Deploy Apps Script"""
    query = update.callback_query
    await query.answer()
    
    message = """
**BÆ°á»›c 2: KÃ­ch hoáº¡t Web App.**

Apps Script giÃºp Sheet cá»§a báº¡n trá»Ÿ thÃ nh má»™t á»©ng dá»¥ng thá»±c thá»¥.

Chá»‰ cáº§n lÃ m theo hÆ°á»›ng dáº«n,
khoáº£ng 3â€“5 phÃºt.

Äá»«ng lo náº¿u chÆ°a quen ká»¹ thuáº­t.
LÃ m cháº­m tá»«ng bÆ°á»›c lÃ  Ä‘Æ°á»£c.
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ“– Xem hÆ°á»›ng dáº«n", callback_data="show_deploy_guide")],
        [InlineKeyboardButton("âœ… TÃ´i Ä‘Ã£ deploy xong", callback_data="free_step5_open_webapp")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def free_step5_open_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 5 - Open Web App first time"""
    query = update.callback_query
    await query.answer()
    
    message = """
BÃ¢y giá» báº¡n cÃ³ thá»ƒ má»Ÿ Web App cá»§a mÃ¬nh.

Láº§n Ä‘áº§u má»Ÿ, báº¡n sáº½ tháº¥y:
â€¢ Tá»•ng tÃ i sáº£n
â€¢ DÃ²ng tiá»n
â€¢ Biá»ƒu Ä‘á»“ chi tiÃªu
â€¢ Cáº¥p Ä‘á»™ tÃ i chÃ­nh

ÄÃ¢y lÃ  láº§n Ä‘áº§u báº¡n nhÃ¬n toÃ n cáº£nh tiá»n cá»§a mÃ¬nh á»Ÿ má»™t nÆ¡i.
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸŒ Má»Ÿ Web App", callback_data="get_webapp_url")],
        [InlineKeyboardButton("âœ… TÃ´i Ä‘Ã£ xem", callback_data="free_step6_first_action")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def free_step6_first_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 6 - First important action"""
    query = update.callback_query
    await query.answer()
    
    message = """
Viá»‡c quan trá»ng nháº¥t hÃ´m nay:

Nháº­p:
â€¢ Sá»‘ dÆ° hiá»‡n táº¡i
â€¢ 1â€“2 giao dá»‹ch gáº§n Ä‘Ã¢y

KhÃ´ng cáº§n nhiá»u.
Chá»‰ cáº§n báº¯t Ä‘áº§u.

Tá»± do tÃ i chÃ­nh khÃ´ng Ä‘áº¿n tá»« káº¿ hoáº¡ch lá»›n.
NÃ³ Ä‘áº¿n tá»« viá»‡c báº¡n biáº¿t tiá»n mÃ¬nh Ä‘ang á»Ÿ Ä‘Ã¢u.
"""
    
    keyboard = [
        [InlineKeyboardButton("âœ… TÃ´i Ä‘Ã£ nháº­p", callback_data="free_step7_reinforce")],
        [InlineKeyboardButton("â“ Cáº§n há»— trá»£", callback_data="ask_support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def free_step7_reinforce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 7 - Reinforce awareness behavior"""
    query = update.callback_query
    await query.answer()
    
    message = """
Tá»« hÃ´m nay,
báº¡n khÃ´ng cÃ²n mÆ¡ há»“ vá» tiá»n ná»¯a.

Má»—i khoáº£n thu â€“ chi Ä‘á»u cÃ³ nÆ¡i ghi láº¡i.
Má»—i quyáº¿t Ä‘á»‹nh Ä‘á»u cÃ³ dá»¯ liá»‡u phÃ­a sau.

Tuáº§n Ä‘áº§u, chá»‰ cáº§n:
**Ghi láº¡i má»i khoáº£n phÃ¡t sinh.**

Äá»«ng cá»‘ tá»‘i Æ°u.
Chá»‰ cáº§n trung thá»±c vá»›i con sá»‘.
"""
    
    keyboard = [
        [InlineKeyboardButton("Tiáº¿p tá»¥c", callback_data="free_step8_optional_sharing")],
        [InlineKeyboardButton("Nháº¯c tÃ´i sau", callback_data="schedule_reminder")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def free_step8_optional_sharing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 8 - Optional sharing (natural, no pressure)"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    from app.utils.database import get_user_by_id
    db_user = await get_user_by_id(user.id)
    
    ref_code = db_user.referral_code if db_user else "unknown"
    ref_link = f"https://t.me/FreedomWalletVNBot?start={ref_code}"
    
    message = f"""
Náº¿u báº¡n tháº¥y há»‡ thá»‘ng nÃ y cÃ³ Ã­ch,
báº¡n cÃ³ thá»ƒ chia sáº» vá»›i 2 ngÆ°á»i báº¡n
cÅ©ng Ä‘ang muá»‘n quáº£n lÃ½ tiá»n rÃµ rÃ ng hÆ¡n.

Khi báº¡n giá»›i thiá»‡u 2 ngÆ°á»i tháº­t sá»± dÃ¹ng,
bÃªn mÃ¬nh sáº½ há»— trá»£ báº¡n cáº¥u hÃ¬nh thÃªm Telegram,
Ä‘á»ƒ báº¡n ghi thu chi ngay trong chat nÃ y.

KhÃ´ng báº¯t buá»™c.
Chá»‰ khi báº¡n tháº¥y phÃ¹ há»£p.

ðŸ”— Link cá»§a báº¡n: `{ref_link}`
"""
    
    keyboard = [
        [InlineKeyboardButton("Chia sáº» vá»›i báº¡n bÃ¨", callback_data="show_share_guide")],
        [InlineKeyboardButton("TÃ¬m hiá»ƒu Telegram", callback_data="explain_telegram_unlock")],
        [InlineKeyboardButton("Äá»ƒ sau", callback_data="skip_sharing")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def learn_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show more details about Freedom Wallet"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Check if user is registered
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        has_registration = db_user and db_user.email and db_user.full_name
    finally:
        db.close()
    
    message = """
**Freedom Wallet lÃ  gÃ¬?**

Há»‡ thá»‘ng quáº£n lÃ½ tÃ i chÃ­nh cÃ¡ nhÃ¢n dá»±a trÃªn:
â€¢ Google Sheets (dá»¯ liá»‡u cá»§a báº¡n)
â€¢ Apps Script (logic tá»± Ä‘á»™ng)
â€¢ Web App (giao diá»‡n thÃ¢n thiá»‡n)

**KhÃ¡c gÃ¬ app khÃ¡c?**

â€¢ Báº¡n sá»Ÿ há»¯u 100% dá»¯ liá»‡u
â€¢ KhÃ´ng phá»¥ thuá»™c vÃ o dá»‹ch vá»¥ nÃ o
â€¢ Miá»…n phÃ­, khÃ´ng giá»›i háº¡n thá»i gian
â€¢ TÃ¹y biáº¿n theo nhu cáº§u riÃªng

**PhÃ¹ há»£p vá»›i ai?**

â€¢ NgÆ°á»i muá»‘n kiá»ƒm soÃ¡t tiá»n rÃµ rÃ ng
â€¢ KhÃ´ng thÃ­ch app thu phÃ­ hÃ ng thÃ¡ng
â€¢ Muá»‘n hiá»ƒu sÃ¢u vá» dÃ²ng tiá»n cá»§a mÃ¬nh
â€¢ Coi trá»ng quyá»n riÃªng tÆ° dá»¯ liá»‡u

Báº¡n muá»‘n báº¯t Ä‘áº§u chá»©?
"""
    
    if has_registration:
        # Already registered, can start setup
        keyboard = [
            [InlineKeyboardButton("ðŸš€ Báº¯t Ä‘áº§u setup", callback_data="free_start_step2")],
            [InlineKeyboardButton("Â« Quay láº¡i", callback_data="back_to_start")]
        ]
    else:
        # Not registered yet, need to register first
        keyboard = [
            [InlineKeyboardButton("ðŸ“ ÄÄƒng kÃ½ ngay", callback_data="start_free_registration")],
            [InlineKeyboardButton("Â« Quay láº¡i", callback_data="back_to_start")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Delete the photo message and send new text message
    try:
        await query.message.delete()
        await query.message.reply_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in learn_more: {e}")
        await query.message.reply_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to start menu"""
    query = update.callback_query
    await query.answer()
    
    # Import start function and call it
    from app.handlers.start import start
    
    # Simulate /start command
    await query.message.delete()
    
    # Create a fake message for start command
    class FakeMessage:
        def __init__(self, original_message):
            self.reply_text = original_message.reply_text
            self.reply_photo = original_message.reply_photo
            self.chat = original_message.chat
            
    class FakeUpdate:
        def __init__(self, original_update):
            self.effective_user = original_update.effective_user
            self.message = FakeMessage(original_update.callback_query.message)
    
    fake_update = FakeUpdate(update)
    await start(fake_update, context)


async def skip_sharing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose to skip sharing"""
    query = update.callback_query
    await query.answer()
    
    message = """
KhÃ´ng sao cáº£.

Báº¡n Ä‘Ã£ cÃ³ há»‡ thá»‘ng riÃªng rá»“i.
Äiá»u quan trá»ng nháº¥t lÃ  báº¡n dÃ¹ng nÃ³ má»—i ngÃ y.

Náº¿u cáº§n trá»£ giÃºp báº¥t cá»© lÃºc nÃ o,
gÃµ /help hoáº·c há»i tÃ´i trá»±c tiáº¿p.

ChÃºc báº¡n quáº£n lÃ½ tiá»n tá»‘t! ðŸ’ª
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ  Vá» trang chá»§", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def show_deploy_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed deploy guide"""
    query = update.callback_query
    await query.answer()
    
    message = """
**ðŸš€ HÆ¯á»šNG DáºªN DEPLOY WEB APP**

**1ï¸âƒ£ Má»Ÿ Apps Script Editor**
â€¢ Trong Sheet â†’ Extensions â†’ Apps Script

**2ï¸âƒ£ Click Deploy**
â€¢ Click nÃºt "Deploy" (gÃ³c trÃªn bÃªn pháº£i)
â€¢ Chá»n "New deployment"

**3ï¸âƒ£ Chá»n type: Web app**
â€¢ Click icon âš™ï¸ 
â€¢ Chá»n "Web app"

**4ï¸âƒ£ Cáº¥u hÃ¬nh**
â€¢ **Execute as**: Chá»n "Me"
â€¢ **Who has access**: Chá»n "Anyone"

**5ï¸âƒ£ Deploy**
â€¢ Click "Deploy"
â€¢ Click "Authorize access"
â€¢ Chá»n tÃ i khoáº£n Google cá»§a báº¡n

**6ï¸âƒ£ Authorize**
â€¢ Click "Advanced"
â€¢ Click "Go to [project name] (unsafe)"
â€¢ Click "Allow"

**7ï¸âƒ£ LÆ°u Web App URL**
â€¢ Copy URL hiá»‡n ra
â€¢ LÆ°u láº¡i Ä‘á»ƒ dÃ¹ng sau

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… **Xong!** Báº¡n Ä‘Ã£ cÃ³ Web App riÃªng.
"""
    
    keyboard = [
        [InlineKeyboardButton("âœ… TÃ´i Ä‘Ã£ deploy xong", callback_data="free_step5_open_webapp")],
        [InlineKeyboardButton("Â« Quay láº¡i", callback_data="free_step4_deploy_script")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# Register all handlers
def register_free_flow_handlers(application):
    """Register all FREE flow handlers"""
    from telegram.ext import CallbackQueryHandler
    
    # Note: start_free_registration is handled by registration ConversationHandler in main.py
    
    application.add_handler(CallbackQueryHandler(free_check_registration, pattern="^free_check_registration$"))
    application.add_handler(CallbackQueryHandler(free_step2_show_value, pattern="^free_start_step2$"))
    application.add_handler(CallbackQueryHandler(free_step3_copy_template, pattern="^free_step3_copy_template$"))
    application.add_handler(CallbackQueryHandler(free_step4_deploy_script, pattern="^free_step4_deploy_script$"))
    application.add_handler(CallbackQueryHandler(show_deploy_guide, pattern="^show_deploy_guide$"))
    application.add_handler(CallbackQueryHandler(free_step5_open_webapp, pattern="^free_step5_open_webapp$"))
    application.add_handler(CallbackQueryHandler(free_step6_first_action, pattern="^free_step6_first_action$"))
    application.add_handler(CallbackQueryHandler(free_step7_reinforce, pattern="^free_step7_reinforce$"))
    application.add_handler(CallbackQueryHandler(free_step8_optional_sharing, pattern="^free_step8_optional_sharing$"))
    application.add_handler(CallbackQueryHandler(learn_more, pattern="^learn_more$"))
    application.add_handler(CallbackQueryHandler(back_to_start, pattern="^back_to_start$"))
    application.add_handler(CallbackQueryHandler(skip_sharing, pattern="^skip_sharing$"))
    
    logger.info("âœ… FREE flow handlers registered")

