"""
Callback Query Handler - Handle inline button clicks
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from config.settings import settings
from app.services.analytics import Analytics
from app.handlers.admin.admin_callbacks import (
    handle_admin_approve_callback,
    handle_admin_reject_callback,
    handle_admin_list_pending_callback
)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline buttons"""
    
    query = update.callback_query
    await query.answer()  # Acknowledge the button click
    
    callback_data = query.data
    
    # Add try-catch for all callback handling
    try:
        await _handle_callback_internal(update, context, query, callback_data)
    except Exception as e:
        logger.error(f"Error handling callback {callback_data}: {e}", exc_info=True)
        try:
            await query.edit_message_text(
                "ðŸ˜“ Xin lá»—i, cÃ³ lá»—i xáº£y ra. Vui lÃ²ng thá»­ láº¡i sau!\n"
                "Náº¿u váº¥n Ä‘á» tiáº¿p diá»…n, dÃ¹ng /support Ä‘á»ƒ liÃªn há»‡.",
                parse_mode="Markdown"
            )
        except:
            pass


async def _handle_callback_internal(update: Update, context: ContextTypes.DEFAULT_TYPE, query, callback_data: str):
    
    # Skip sheets-related callbacks (handled by ConversationHandler)
    if callback_data and callback_data.startswith("sheets_"):
        logger.debug(f"Skipping sheets callback: {callback_data} (handled by ConversationHandler)")
        return
    
    # Skip free flow callbacks (handled by free_flow.py)
    if callback_data and callback_data.startswith("free_"):
        logger.debug(f"Skipping free flow callback: {callback_data} (handled by free_flow handlers)")
        return
    
    # Skip unlock flow callbacks (handled by unlock_calm_flow.py)
    if callback_data and callback_data.startswith("unlock_"):
        logger.debug(f"Skipping unlock flow callback: {callback_data} (handled by unlock_calm_flow handlers)")
        return
    
    # Skip learn_more and skip_sharing callbacks (handled by free_flow.py)
    if callback_data in ["learn_more", "skip_sharing", "show_deploy_guide", "back_to_start", "start_free_registration"]:
        logger.debug(f"Skipping free flow helper callback: {callback_data}")
        return
    
    # Week 4: Update Super VIP activity tracking
    from app.core.state_machine import StateManager
    with StateManager() as sm:
        sm.update_super_vip_activity(query.from_user.id)
    
    logger.info(f"Callback: {callback_data} from user {query.from_user.id}")
    
    # Route usage tracker callbacks (trial start, etc.)
    from app.middleware.usage_tracker import (
        handle_trial_start,
        handle_view_premium,
        handle_why_premium
    )
    
    if callback_data == "start_trial":
        await handle_trial_start(update, context)
        return
    elif callback_data == "view_premium":
        await handle_view_premium(update, context)
        return
    elif callback_data == "why_premium":
        await handle_why_premium(update, context)
        return
    
    # Onboarding guides for Premium trial users
    elif callback_data == "webapp_setup_guide":
        await handle_webapp_setup_guide(update, context)
        return
    elif callback_data == "premium_usage_guide":
        await handle_premium_usage_guide(update, context)
        return
    
    # DAY 2: ROI & Upsell callbacks
    elif callback_data == "upgrade_to_premium":
        await handle_upgrade_to_premium(update, context)
        return
    elif callback_data == "confirm_payment":
        await handle_confirm_payment(update, context)
        return
    elif callback_data == "view_roi_detail":
        await handle_view_roi_detail(update, context)
        return
    elif callback_data == "optimization_tips":
        await handle_optimization_tips(update, context)
        return
    
    # DAY 3: Analytics tracking callbacks
    elif callback_data == "wow_moment_dismiss":
        await handle_wow_moment_dismiss(update, context)
        return
    
    # Start menu callbacks
    elif callback_data == "free_chat":
        await handle_free_chat(update, context)
        return
    elif callback_data == "upgrade_premium":
        await handle_upgrade_premium_from_start(update, context)
        return
    
    # Route Premium callbacks
    from app.handlers.premium.premium_commands import PREMIUM_CALLBACKS
    if callback_data in PREMIUM_CALLBACKS:
        handler = PREMIUM_CALLBACKS[callback_data]
        try:
            await handler(update, context)
        except Exception as e:
            logger.error(f"Error in Premium callback {callback_data}: {e}", exc_info=True)
            await query.edit_message_text(
                f"ðŸ˜“ Xin lá»—i, cÃ³ lá»—i khi xá»­ lÃ½ '{callback_data}'. Vui lÃ²ng thá»­ láº¡i!\n\n"
                f"Náº¿u váº¥n Ä‘á» tiáº¿p diá»…n, dÃ¹ng /support Ä‘á»ƒ liÃªn há»‡.",
                parse_mode="Markdown"
            )
        return
    
    # Admin payment approval callbacks
    if callback_data.startswith("admin_approve_"):
        await handle_admin_approve_callback(update, context)
        return
    elif callback_data.startswith("admin_reject_"):
        await handle_admin_reject_callback(update, context)
        return
    elif callback_data == "admin_list_pending":
        await handle_admin_list_pending_callback(update, context)
        return
    
    # Route to appropriate handler based on callback_data
    if callback_data == "start" or callback_data == "back_home":
        # Back to home
        from app.handlers.user.start import start
        # Create mock update for start command
        update.message = query.message
        try:
            await start(update, context)
        except Exception as e:
            logger.error(f"Error calling start handler: {e}", exc_info=True)
            await query.edit_message_text(
                "ðŸ˜“ Xin lá»—i, cÃ³ lá»—i khi quay vá» trang chá»§. Vui lÃ²ng gÃµ /start Ä‘á»ƒ thá»­ láº¡i!",
                parse_mode="Markdown"
            )
        return
    
    elif callback_data == "help_tutorial":
        text = """
ðŸ“š **HÆ°á»›ng Dáº«n Sá»­ Dá»¥ng Freedom Wallet**

ðŸŒ **Xem hÆ°á»›ng dáº«n Ä‘áº§y Ä‘á»§ táº¡i:**
ðŸ‘‰ [eliroxbot.notion.site/freedomwallet](https://eliroxbot.notion.site/freedomwallet)

ðŸ“– **Ná»™i dung bao gá»“m:**
â€¢ HÆ°á»›ng dáº«n báº¯t Ä‘áº§u (Getting Started)
â€¢ CÃ i Ä‘áº·t Web App trÃªn Ä‘iá»‡n thoáº¡i
â€¢ 6 HÅ© tiá»n lÃ  gÃ¬ & cÃ¡ch sá»­ dá»¥ng
â€¢ Ghi chÃ©p giao dá»‹ch nhanh
â€¢ PhÃ¢n tÃ­ch tÃ i chÃ­nh & ROI
â€¢ Gá»£i Ã½ thÃ´ng minh

ðŸ’¡ **Hoáº·c há»i mÃ¬nh trá»±c tiáº¿p:**
"LÃ m sao thÃªm giao dá»‹ch?"
"6 hÅ© tiá»n lÃ  gÃ¬?"
"CÃ¡ch cÃ i Web App?"
"""
        keyboard = [
            [InlineKeyboardButton("ðŸŒ Má»Ÿ hÆ°á»›ng dáº«n", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("ðŸ  Quay láº¡i", callback_data="back_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    
    elif callback_data == "help_faq":
        text = """
â“ **CÃ¢u Há»i ThÆ°á»ng Gáº·p (FAQ)**

**ðŸ“ Giao dá»‹ch:**
â€¢ ThÃªm / Sá»­a / XÃ³a giao dá»‹ch
â€¢ Lá»c vÃ  tÃ¬m kiáº¿m

**ðŸº 6 HÅ© Tiá»n:**
â€¢ PhÆ°Æ¡ng phÃ¡p 6 Jars lÃ  gÃ¬?
â€¢ Chuyá»ƒn tiá»n giá»¯a hÅ©
â€¢ Táº¡i sao sá»‘ dÆ° hÅ© sai?

**ðŸ“ˆ Äáº§u tÆ°:**
â€¢ ThÃªm khoáº£n Ä‘áº§u tÆ°
â€¢ TÃ­nh ROI & lá»£i nhuáº­n
â€¢ BÃ¡n Ä‘áº§u tÆ°

**ðŸ”§ Kháº¯c phá»¥c lá»—i:**
â€¢ App khÃ´ng load
â€¢ Äá»“ng bá»™ cháº­m
â€¢ ÄÄƒng nháº­p lá»—i

ðŸ’¬ **GÃµ cÃ¢u há»i cá»§a báº¡n Ä‘á»ƒ mÃ¬nh tráº£ lá»i chi tiáº¿t!**
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "help_troubleshoot":
        text = """
ðŸ”§ **Kháº¯c Phá»¥c Lá»—i ThÆ°á»ng Gáº·p**

**1ï¸âƒ£ App khÃ´ng load dá»¯ liá»‡u:**
â€¢ Click nÃºt ðŸ”„ Ä‘á»ƒ refresh
â€¢ Clear browser cache (Ctrl+Shift+Delete)
â€¢ Thá»­ browser khÃ¡c

**2ï¸âƒ£ Sá»‘ dÆ° hÅ© khÃ´ng Ä‘Ãºng:**
â€¢ Kiá»ƒm tra danh má»¥c gáº¯n hÅ© nÃ o
â€¢ Äáº£m báº£o Auto Allocate báº­t
â€¢ Reload data (ðŸ”„)

**3ï¸âƒ£ Äá»“ng bá»™ cháº­m:**
â€¢ BÃ¬nh thÆ°á»ng! Optimistic UI sync 1-2s
â€¢ Äá»£i background sync hoÃ n táº¥t
â€¢ Náº¿u quÃ¡ 10s â†’ F12 console check lá»—i

ðŸ’¬ **Náº¿u váº«n lá»—i:** DÃ¹ng /support Ä‘á»ƒ bÃ¡o chi tiáº¿t!
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "help_tips":
        text = """
ðŸ’¡ **Tips TÃ i ChÃ­nh**

**ðŸº 6 Jars Method:**
PhÃ¢n chia thu nháº­p thÃ nh 6 pháº§n:
â€¢ NEC (55%): Nhu cáº§u thiáº¿t yáº¿u
â€¢ LTS (10%): Tiáº¿t kiá»‡m dÃ i háº¡n
â€¢ EDU (10%): GiÃ¡o dá»¥c
â€¢ PLAY (10%): Giáº£i trÃ­
â€¢ FFA (10%): Tá»± do tÃ i chÃ­nh (Ä‘áº§u tÆ°)
â€¢ GIVE (5%): Cho Ä‘i

ðŸ’° **NguyÃªn táº¯c vÃ ng:**
1. Tráº£ tiá»n cho báº£n thÃ¢n trÆ°á»›c (LTS + FFA)
2. Äáº§u tÆ° Ä‘á»u Ä‘áº·n má»—i thÃ¡ng
3. Review bÃ¡o cÃ¡o cuá»‘i thÃ¡ng
4. Äiá»u chá»‰nh tá»· lá»‡ phÃ¹ há»£p báº£n thÃ¢n

ðŸ“š Äá»c thÃªm: "6 HÅ© Tiá»n - BÃ­ Máº­t TÆ° Duy Triá»‡u PhÃº"
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "contact_support":
        text = """
ðŸ†˜ **LiÃªn Há»‡ Há»— Trá»£**

Gáº·p váº¥n Ä‘á» cáº§n há»— trá»£?

ðŸ“ DÃ¹ng lá»‡nh: **/support**

Hoáº·c liÃªn há»‡ trá»±c tiáº¿p:
ðŸ“§ Email: support@freedomwallet.com
ðŸ’¬ Telegram: @FreedomWalletSupport

â±ï¸ *Pháº£n há»“i trong 24h lÃ m viá»‡c*
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "feedback_solved":
        await query.edit_message_text(
            "ðŸŽ‰ **Tuyá»‡t vá»i! Váº¥n Ä‘á» Ä‘Ã£ Ä‘Æ°á»£c giáº£i quyáº¿t!**\n\n"
            "Náº¿u cáº§n gÃ¬ thÃªm, cá»© há»i mÃ¬nh nhÃ©! ðŸ’¬",
            parse_mode="Markdown"
        )
    
    elif callback_data == "feedback_unsolved":
        text = """
ðŸ˜” **Xin lá»—i, cÃ¢u tráº£ lá»i chÆ°a giáº£i quyáº¿t Ä‘Æ°á»£c váº¥n Ä‘á» cá»§a báº¡n.**

ðŸ†˜ **HÃ£y liÃªn há»‡ support team:**
DÃ¹ng /support Ä‘á»ƒ táº¡o ticket, team sáº½ há»— trá»£ chi tiáº¿t hÆ¡n!

Hoáº·c mÃ´ táº£ láº¡i váº¥n Ä‘á», mÃ¬nh sáº½ cá»‘ gáº¯ng giÃºp!
"""
        await query.edit_message_text(text, parse_mode="Markdown")
    
    elif callback_data == "ask_more":
        await query.edit_message_text(
            "ðŸ’¬ **Há»i thÃªm cÃ¢u khÃ¡c Ä‘i!**\n\nGÃµ cÃ¢u há»i cá»§a báº¡n, mÃ¬nh sáºµn sÃ ng tráº£ lá»i! ðŸ˜Š",
            parse_mode="Markdown"
        )
    
    elif callback_data == "cancel_support":
        await query.edit_message_text(
            "âŒ **ÄÃ£ há»§y táº¡o ticket.**\n\nNáº¿u cáº§n há»— trá»£, dÃ¹ng /support báº¥t cá»© lÃºc nÃ o!",
            parse_mode="Markdown"
        )
    
    elif callback_data == "start_register":
        # Start registration flow
        await query.edit_message_text(
            "ðŸ“ **Báº®T Äáº¦U ÄÄ‚NG KÃ**\n\n"
            "Báº¡n sáº½ nháº­n:\n"
            "âœ… Template Google Sheet miá»…n phÃ­\n"
            "âœ… HÆ°á»›ng dáº«n setup chi tiáº¿t\n"
            "âœ… Quyá»n unlock FREE tier (náº¿u Ä‘Æ°á»£c giá»›i thiá»‡u)\n\n"
            "ðŸ‘‰ GÃµ **/register** Ä‘á»ƒ báº¯t Ä‘áº§u!",
            parse_mode="Markdown"
        )
    
    elif callback_data == "referral_menu":
        # Show referral system
        from app.handlers.engagement.referral import referral_command
        from app.utils.database import get_user_by_id
        
        user = query.from_user
        db_user = await get_user_by_id(user.id)
        
        if not db_user:
            await query.edit_message_text("âŒ Lá»—i: KhÃ´ng tÃ¬m tháº¥y user. Vui lÃ²ng /start láº¡i.")
            return
        
        # Get referral stats
        from app.utils.database import get_user_referrals
        
        referral_code = db_user.referral_code
        referral_count = db_user.referral_count
        is_unlocked = db_user.is_free_unlocked
        referred_users = await get_user_referrals(user.id)
        
        # Build referral link
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        # Status message
        if is_unlocked:
            status_msg = "âœ… **FREE FOREVER Ä‘Ã£ má»Ÿ khÃ³a!**\n\n"
        else:
            remaining = 2 - referral_count
            status_msg = f"ðŸŽ¯ **CÃ²n {remaining} ngÆ°á»i ná»¯a Ä‘á»ƒ má»Ÿ khÃ³a FREE!**\n\n"
        
        # Build message
        message = f"""
ðŸŽ **Há»† THá»NG GIá»šI THIá»†U Báº N BÃˆ**

{status_msg}ðŸ“Š **Thá»‘ng KÃª Cá»§a Báº¡n:**
â€¢ MÃ£ giá»›i thiá»‡u: `{referral_code}`
â€¢ ÄÃ£ giá»›i thiá»‡u: {referral_count} ngÆ°á»i
â€¢ Tráº¡ng thÃ¡i: {"âœ… FREE Unlocked" if is_unlocked else "ðŸ”’ Äang khÃ³a"}

ðŸ”— **Link giá»›i thiá»‡u:**
`{referral_link}`

ðŸ“± **CÃ¡ch sá»­ dá»¥ng:**
1. Copy link trÃªn
2. Gá»­i cho báº¡n bÃ¨/gia Ä‘Ã¬nh
3. Khi 2 ngÆ°á»i Ä‘Äƒng kÃ½ â†’ **FREE FOREVER**!

ðŸ’Ž **Quyá»n lá»£i FREE:**
âœ“ Bot khÃ´ng giá»›i háº¡n
âœ“ Template Ä‘áº§y Ä‘á»§
âœ“ HÆ°á»›ng dáº«n chi tiáº¿t
âœ“ Cá»™ng Ä‘á»“ng support
"""
        
        # Show referred users list
        if referred_users:
            message += f"\nðŸ‘¥ **ÄÃ£ giá»›i thiá»‡u:**\n"
            for idx, ref_user in enumerate(referred_users[:5], 1):  # Max 5
                name = ref_user['name']
                date = ref_user['date'].strftime("%d/%m/%Y")
                message += f"{idx}. {name} ({date})\n"
        
        # Keyboard
        keyboard = [
            [InlineKeyboardButton("ðŸ“¢ Chia sáº» ngay", 
                                 url=f"https://t.me/share/url?url={referral_link}&text=Tham gia Freedom Wallet Bot - Quáº£n lÃ½ tÃ i chÃ­nh thÃ´ng minh!")],
            [InlineKeyboardButton("Â« Quay láº¡i", callback_data="start")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    elif callback_data == "share_link":
        # Handle share link button from daily nurture
        from app.handlers.engagement.daily_nurture import handle_share_link_button
        await handle_share_link_button(update, context)
    
    elif callback_data == "check_progress":
        # Handle check progress button
        from app.handlers.engagement.daily_nurture import handle_check_progress_button
        await handle_check_progress_button(update, context)
    
    elif callback_data == "vip_gifts":
        # Show VIP gift menu (6 gift options)
        keyboard = [
            [InlineKeyboardButton("ðŸŽ Nháº­n Google Sheet 3.2", callback_data="gift_sheet")],
            [InlineKeyboardButton("âš™ï¸ Nháº­n Google Apps Script", callback_data="gift_script")],
            [InlineKeyboardButton("ðŸŒ HÆ°á»›ng dáº«n táº¡o Web App", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("ðŸŽ¥ Xem video hÆ°á»›ng dáº«n", callback_data="gift_video")],
            [InlineKeyboardButton("ðŸ’¬ Tham gia Group VIP", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("ðŸ  VÃ o Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "ðŸŽ **MENU NHáº¬N QUÃ€**\n\n"
            "Chá»n tá»«ng má»¥c bÃªn dÆ°á»›i Ä‘á»ƒ nháº­n quÃ  cá»§a báº¡n:\n\n"
            "ðŸŽ **Google Sheet 3.2** - CÃ´ng cá»¥ quáº£n lÃ½ tÃ i chÃ­nh\n"
            "âš™ï¸ **Apps Script** - Code tá»± Ä‘á»™ng hÃ³a\n"
            "ðŸŒ **Web App Guide** - HÆ°á»›ng dáº«n deploy\n"
            "ðŸŽ¥ **Video Tutorials** - Há»c tá»«ng bÆ°á»›c\n"
            "ðŸ’¬ **VIP Group** - Cá»™ng Ä‘á»“ng Ä‘á»™c quyá»n\n\n"
            "ðŸ’¡ Báº¡n cÃ³ thá»ƒ quay láº¡i menu nÃ y báº¥t cá»© lÃºc nÃ o!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data == "onboarding_start":
        # Start 7-day onboarding journey
        from app.handlers.user.onboarding import start_onboarding_journey
        
        user_id = query.from_user.id
        success = await start_onboarding_journey(user_id, context)
        
        if success:
            await query.edit_message_text(
                "ðŸŽ“ **HÃ€NH TRÃŒNH 7 NGÃ€Y Báº®T Äáº¦U!**\n\n"
                "ChÃºc má»«ng! Báº¡n vá»«a Ä‘Äƒng kÃ½ hÃ nh trÃ¬nh há»c táº­p 7 ngÃ y.\n\n"
                "ðŸ“… **Lá»‹ch trÃ¬nh:**\n"
                "â€¢ Day 1: Giá»›i thiá»‡u 6 HÅ© Tiá»n\n"
                "â€¢ Day 2: Setup Google Sheet cÆ¡ báº£n\n"
                "â€¢ Day 3: Quáº£n lÃ½ thu chi hÃ ng ngÃ y\n"
                "â€¢ Day 4: Apps Script & Automation\n"
                "â€¢ Day 5: PhÃ¢n tÃ­ch tÃ i chÃ­nh\n"
                "â€¢ Day 6: Má»¥c tiÃªu & Káº¿ hoáº¡ch\n"
                "â€¢ Day 7: Dashboard & BÃ¡o cÃ¡o\n\n"
                "ðŸ“¬ Má»—i ngÃ y báº¡n sáº½ nháº­n Ä‘Æ°á»£c:\n"
                "âœ… 1 bÃ i há»c ngáº¯n (3-5 phÃºt)\n"
                "âœ… Video hÆ°á»›ng dáº«n chi tiáº¿t\n"
                "âœ… BÃ i táº­p thá»±c hÃ nh\n\n"
                "ðŸ’¡ Tin nháº¯n Ä‘áº§u tiÃªn sáº½ Ä‘áº¿n trong vÃ i phÃºt!\n\n"
                "ChÃºc báº¡n há»c táº­p hiá»‡u quáº£! ðŸš€",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "âŒ **Lá»—i**\n\n"
                "KhÃ´ng thá»ƒ báº¯t Ä‘áº§u hÃ nh trÃ¬nh. Vui lÃ²ng thá»­ láº¡i sau.",
                parse_mode="Markdown"
            )
    
    elif callback_data == "gift_sheet":
        # Send Google Sheet template link
        keyboard = [
            [InlineKeyboardButton("ðŸŽ Nháº­n thÃªm quÃ  khÃ¡c", callback_data="vip_gifts")],
            [InlineKeyboardButton("ðŸŽ“ Báº¯t Ä‘áº§u hÃ nh trÃ¬nh 7 ngÃ y", callback_data="onboarding_start")],
            [InlineKeyboardButton("ðŸ  Vá» Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "ðŸ“„ **GOOGLE SHEET TEMPLATE 3.2**\n\n"
            "ÄÃ¢y lÃ  bá»™ cÃ´ng cá»¥ quáº£n lÃ½ tÃ i chÃ­nh cÃ¡ nhÃ¢n hoÃ n chá»‰nh:\n\n"
            "âœ… 6 HÅ© Tiá»n tá»± Ä‘á»™ng\n"
            "âœ… Dashboard trá»±c quan\n"
            "âœ… Theo dÃµi 5 Cáº¥p Báº­c TÃ i ChÃ­nh\n"
            "âœ… Quáº£n lÃ½ Ä‘áº§u tÆ° & ROI\n"
            "âœ… BÃ¡o cÃ¡o thÃ¡ng/nÄƒm\n\n"
            "ðŸ‘‰ **Link Template:**\n"
            f"[Click Ä‘á»ƒ copy Template](https://docs.google.com/spreadsheets/d/{settings.YOUR_TEMPLATE_ID})\n\n"
            "ðŸ“š **HÆ°á»›ng dáº«n sá»­ dá»¥ng:**\n"
            "1. Click link trÃªn\n"
            "2. File â†’ Make a copy\n"
            "3. Äá»•i tÃªn theo Ã½ báº¡n\n"
            "4. Báº¯t Ä‘áº§u dÃ¹ng ngay!\n\n"
            "ðŸ’¡ Xem thÃªm: /help",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    elif callback_data == "gift_script":
        # Send Apps Script code snippet
        keyboard = [
            [InlineKeyboardButton("ðŸŽ Nháº­n thÃªm quÃ  khÃ¡c", callback_data="vip_gifts")],
            [InlineKeyboardButton("ðŸŽ“ Báº¯t Ä‘áº§u hÃ nh trÃ¬nh 7 ngÃ y", callback_data="onboarding_start")],
            [InlineKeyboardButton("ðŸ  Vá» Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "âš™ï¸ **GOOGLE APPS SCRIPT**\n\n"
            "Script nÃ y tá»± Ä‘á»™ng hÃ³a viá»‡c Ä‘á»“ng bá»™ dá»¯ liá»‡u:\n\n"
            "âœ… Auto sync Sheet â†’ Web App\n"
            "âœ… Calculate 6 Jars balance\n"
            "âœ… Update ROI dashboard\n"
            "âœ… Generate reports\n\n"
            "ðŸ“‹ **CÃ¡ch cÃ i Ä‘áº·t:**\n"
            "1. Má»Ÿ Google Sheet cá»§a báº¡n\n"
            "2. Extensions â†’ Apps Script\n"
            "3. Copy paste code tá»« Notion guide\n"
            "4. Deploy as Web App\n\n"
            "ðŸŒ **Full guide:**\n"
            "[Notion - HÆ°á»›ng dáº«n chi tiáº¿t](https://eliroxbot.notion.site/freedomwallet)\n\n"
            "ðŸ’¡ Cáº§n há»— trá»£? Há»i mÃ¬nh báº¥t cá»© lÃºc nÃ o!",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    elif callback_data == "gift_video":
        # Send video tutorial links
        keyboard = [
            [InlineKeyboardButton("ðŸŽ Nháº­n thÃªm quÃ  khÃ¡c", callback_data="vip_gifts")],
            [InlineKeyboardButton("ðŸŽ“ Báº¯t Ä‘áº§u hÃ nh trÃ¬nh 7 ngÃ y", callback_data="onboarding_start")],
            [InlineKeyboardButton("ðŸ  Vá» Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "ðŸŽ¥ **VIDEO TUTORIALS**\n\n"
            "Series video hÆ°á»›ng dáº«n tá»«ng bÆ°á»›c:\n\n"
            "ðŸ“¹ **Video 1: Setup cÆ¡ báº£n (3 phÃºt)**\n"
            "â€¢ Copy Google Sheet Template\n"
            "â€¢ Cáº¥u hÃ¬nh cÆ¡ báº£n\n"
            "â€¢ ThÃªm giao dá»‹ch Ä‘áº§u tiÃªn\n\n"
            "ðŸ“¹ **Video 2: Apps Script & Web App (5 phÃºt)**\n"
            "â€¢ Deploy Apps Script\n"
            "â€¢ Táº¡o Web App URL\n"
            "â€¢ Test Ä‘á»“ng bá»™\n\n"
            "ðŸ“¹ **Video 3: Advanced features (7 phÃºt)**\n"
            "â€¢ 6 HÅ© Tiá»n chi tiáº¿t\n"
            "â€¢ Quáº£n lÃ½ Ä‘áº§u tÆ°\n"
            "â€¢ ROI tracking\n\n"
            "ðŸ”— **Link playlist:**\n"
            "[YouTube - Freedom Wallet Tutorials](https://youtube.com/@freedomwallet)\n\n"
            "ðŸ’¬ Xem xong mÃ  cÃ²n tháº¯c máº¯c? Há»i mÃ¬nh nhÃ©!",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    # ============================================
    # ONBOARDING CALLBACKS (7-Day Journey)
    # ============================================
    
    elif callback_data == "onboard_copy_template":
        # Send template link when user clicks Copy Template
        await query.answer("ðŸ“‘ Äang gá»­i link template...")
        
        keyboard = [
            [InlineKeyboardButton("ðŸŒ HÆ°á»›ng dáº«n Web App", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("âœ… ÄÃ£ copy xong", callback_data="onboard_complete_1")],
            [InlineKeyboardButton("â“ Cáº§n há»— trá»£", callback_data="onboard_help_1")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"ðŸ“‘ **FREEDOM WALLET TEMPLATE**\n\n"
                 f"ðŸ‘‰ **Link template:** [Click Ä‘á»ƒ má»Ÿ]({settings.YOUR_TEMPLATE_ID})\n\n"
                 f"**CÃ¡ch sá»­ dá»¥ng:**\n"
                 f"1. Click link á»Ÿ trÃªn\n"
                 f"2. File â†’ Make a copy\n"
                 f"3. Äáº·t tÃªn: 'My Freedom Wallet'\n"
                 f"4. Click 'âœ… ÄÃ£ copy xong' bÃªn dÆ°á»›i\n\n"
                 f"ðŸ’¡ Template sáº½ má»Ÿ trong Google Drive cá»§a báº¡n!",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    elif callback_data == "onboard_video_day1":
        # Send Day 1 video tutorial
        await query.answer("ðŸŽ¥ Äang gá»­i video tutorial...")
        
        keyboard = [
            [InlineKeyboardButton("ðŸ“‘ Copy Template", callback_data="onboard_copy_template")],
            [InlineKeyboardButton("ðŸŒ HÆ°á»›ng dáº«n Web App", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("âœ… ÄÃ£ xem xong", callback_data="onboard_complete_1")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text="ðŸŽ¥ **VIDEO HÆ¯á»šNG DáºªN SETUP (3 PHÃšT)**\n\n"
                 "ðŸ“¹ **Ná»™i dung video:**\n"
                 "â€¢ CÃ¡ch copy template\n"
                 "â€¢ Setup Google Apps Script\n"
                 "â€¢ Deploy Web App\n"
                 "â€¢ ThÃªm dá»¯ liá»‡u Ä‘áº§u tiÃªn\n\n"
                 "ðŸ‘‰ **Link video:** [Xem trÃªn YouTube](https://youtube.com/@freedomwallet)\n\n"
                 "ðŸ’¬ Xem xong mÃ  chÆ°a hiá»ƒu? Click 'Cáº§n há»— trá»£' nhÃ©!",
            parse_mode="Markdown",
            disable_web_page_preview=False,
            reply_markup=reply_markup
        )
    
    elif callback_data == "onboard_roadmap":
        # Show 7-day roadmap overview
        await query.answer("ðŸ“‹ Äang gá»­i lá»™ trÃ¬nh...")
        
        keyboard = [
            [InlineKeyboardButton("ðŸ  Vá» Dashboard", callback_data="start")],
            [InlineKeyboardButton("ðŸ’¬ Tham gia Group VIP", url="https://t.me/freedomwalletapp")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "ðŸ“‹ **Lá»˜ TRÃŒNH 7 NGÃ€Y - FREEDOM WALLET**\n\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            "ðŸŽ **BÆ°á»›c Ä‘áº§u tiÃªn:** Thiáº¿t láº­p Freedom Wallet\n"
            "   â€¢ Copy template, táº¡o Web App, nháº­p dá»¯ liá»‡u Ä‘áº§u tiÃªn\n"
            "   â€¢ Thá»i gian: 10-15 phÃºt\n\n"
            "ðŸ’° **NgÃ y 2:** Hiá»ƒu vá» 6 HÅ© Tiá»n\n"
            "   â€¢ Chi tiÃªu thiáº¿t yáº¿u, HÆ°á»Ÿng thá»¥, Äáº§u tÆ°...\n"
            "   â€¢ PhÃ¢n bá»• % thu nháº­p há»£p lÃ½\n\n"
            "ðŸŽ¯ **NgÃ y 3:** 5 Cáº¥p Báº­c TÃ i ChÃ­nh\n"
            "   â€¢ Tá»« Survival â†’ Financial Freedom\n"
            "   â€¢ XÃ¡c Ä‘á»‹nh vá»‹ trÃ­ hiá»‡n táº¡i cá»§a báº¡n\n\n"
            "âš¡ **NgÃ y 4:** ThÃªm giao dá»‹ch & Tracking\n"
            "   â€¢ ThÃ³i quen ghi chÃ©p hÃ ng ngÃ y\n"
            "   â€¢ Tips Ä‘á»ƒ tracking hiá»‡u quáº£\n\n"
            "ðŸ“ˆ **NgÃ y 5:** TÃ­nh nÄƒng nÃ¢ng cao\n"
            "   â€¢ Budget planning, ROI tracking\n"
            "   â€¢ Automation vá»›i Apps Script\n\n"
            "ðŸ‘¥ **NgÃ y 6:** Tham gia cá»™ng Ä‘á»“ng\n"
            "   â€¢ Káº¿t ná»‘i vá»›i VIPs khÃ¡c\n"
            "   â€¢ Chia sáº» & há»c há»i kinh nghiá»‡m\n\n"
            "ðŸŽŠ **NgÃ y 7:** Ã”n táº­p & Káº¿ hoáº¡ch dÃ i háº¡n\n"
            "   â€¢ Review toÃ n bá»™ há»‡ thá»‘ng\n"
            "   â€¢ LÃªn káº¿ hoáº¡ch 30-90 ngÃ y tá»›i\n\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            "ðŸ’¡ Má»—i ngÃ y chá»‰ máº¥t 5-10 phÃºt.\n"
            "Báº¡n sáº½ nháº­n tin nháº¯n vÃ o 10h sÃ¡ng má»—i ngÃ y!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data.startswith("onboard_complete_"):
        # User completed an onboarding day
        day = callback_data.split("_")[-1]
        
        congratulations = {
            "1": "ðŸŽ‰ **HOÃ€N THÃ€NH DAY 1!**\n\nXuáº¥t sáº¯c! Báº¡n Ä‘Ã£ setup xong Foundation.\n\nðŸ“… **NgÃ y mai:** TÃ¬m hiá»ƒu vá» 6 HÅ© Tiá»n\nðŸ’¬ MÃ¬nh sáº½ nháº¯n báº¡n khoáº£ng 10h sÃ¡ng!",
            "2": "ðŸ’° **HOÃ€N THÃ€NH DAY 2!**\n\nBáº¡n Ä‘Ã£ hiá»ƒu vá» 6 HÅ© Tiá»n rá»“i Ä‘áº¥y!\n\nðŸ“… **NgÃ y mai:** 5 Cáº¥p Báº­c TÃ i ChÃ­nh",
            "3": "ðŸŽ¯ **HOÃ€N THÃ€NH DAY 3!**\n\nÄÃ£ biáº¿t mÃ¬nh Ä‘ang á»Ÿ cáº¥p nÃ o chÆ°a?\n\nðŸ“… **NgÃ y mai:** ThÃªm giao dá»‹ch Ä‘áº§u tiÃªn",
            "4": "âš¡ **HOÃ€N THÃ€NH DAY 4!**\n\nTracking tá»‘t! Tiáº¿p tá»¥c duy trÃ¬ nhÃ©.\n\nðŸ“… **NgÃ y mai:** TÃ­nh nÄƒng nÃ¢ng cao",
            "5": "ðŸ“ˆ **HOÃ€N THÃ€NH DAY 5!**\n\nBáº¡n Ä‘Ã£ master Freedom Wallet rá»“i!\n\nðŸ“… **NgÃ y mai:** Challenge 30 ngÃ y",
            "6": "ðŸ’ª **HOÃ€N THÃ€NH DAY 6!**\n\nReady for challenge?\n\nðŸ“… **NgÃ y mai:** Wrap up & next steps",
            "7": "ðŸ† **HOÃ€N THÃ€NH 7-DAY JOURNEY!**\n\nChÃºc má»«ng! Báº¡n Ä‘Ã£ hoÃ n thÃ nh hÃ nh trÃ¬nh!\n\nðŸš€ Giá» lÃ  lÃºc Ã¡p dá»¥ng vÃ o thá»±c táº¿!"
        }
        
        keyboard = [
            [InlineKeyboardButton("ðŸ’¬ Tham gia Group VIP", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("ðŸ  Vá» Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            congratulations.get(day, "âœ… HoÃ n thÃ nh!"),
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # TODO: Update onboarding_progress in database
        logger.info(f"User {query.from_user.id} completed onboarding day {day}")
    
    elif callback_data.startswith("onboard_help_"):
        # User needs help with onboarding
        day = callback_data.split("_")[-1]
        
        keyboard = [
            [InlineKeyboardButton("ï¿½ HÆ°á»›ng dáº«n chi tiáº¿t (Notion)", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("ðŸ’¬ Group VIP", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("ðŸ“ž LiÃªn há»‡ Admin", url=f"https://t.me/{settings.BOT_USERNAME.replace('Bot', '')}")],
            [InlineKeyboardButton("ðŸ”™ Quay láº¡i", callback_data=f"onboard_replay_{day}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"â“ **Cáº¦N Há»– TRá»¢?**\n\n"
            f"KhÃ´ng sao cáº£! MÃ¬nh á»Ÿ Ä‘Ã¢y Ä‘á»ƒ giÃºp báº¡n.\n\n"
            f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            f"**Báº¡n cÃ³ thá»ƒ:**\n\n"
            f"ðŸ“– **Xem hÆ°á»›ng dáº«n chi tiáº¿t** (cÃ³ áº£nh tá»«ng bÆ°á»›c)\n"
            f"ðŸ’¬ **Há»i trong Group VIP** (community ráº¥t nhiá»‡t tÃ¬nh)\n"
            f"ðŸ“ž **Nháº¯n Admin** (há»— trá»£ 1-1)\n\n"
            f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            f"â° **Thá»i gian há»— trá»£:**\n"
            f"â€¢ Thá»© 2-6: 9h-21h\n"
            f"â€¢ Thá»© 7-CN: 10h-18h\n\n"
            f"ðŸ’¬ Hoáº·c gÃµ trá»±c tiáº¿p cÃ¢u há»i Ä‘á»ƒ mÃ¬nh tráº£ lá»i nhÃ©!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    # ============================================
    # VIP UNLOCK FLOW CALLBACKS
    # ============================================
    
    elif callback_data == "vip_continue":
        # Message 3B: Action menu after user sees benefits
        await query.answer("âœ¨ Xuáº¥t sáº¯c!")
        
        keyboard_3b = [
            [InlineKeyboardButton("âœ… TÃ´i Ä‘Ã£ táº¡o xong", callback_data="webapp_ready")],
            [InlineKeyboardButton("ðŸ“– Xem hÆ°á»›ng dáº«n 3 bÆ°á»›c", callback_data="webapp_setup_guide")]
        ]
        reply_markup_3b = InlineKeyboardMarkup(keyboard_3b)
        
        await query.edit_message_text(
            "ðŸš€ **Äá»ƒ sá»­ dá»¥ng Freedom Wallet,**\n"
            "báº¡n cáº§n táº¡o Web App (3â€“5 phÃºt).\n\n"
            "Báº¡n Ä‘Ã£ táº¡o xong chÆ°a?",
            parse_mode="Markdown",
            reply_markup=reply_markup_3b
        )
    
    # ============================================
    # WEB APP SETUP GUIDE CALLBACKS
    # ============================================
    
    elif callback_data == "webapp_ready":
        # User confirmed they completed Web App setup
        await query.answer("ðŸŽ‰ Tuyá»‡t vá»i! ChÃºc má»«ng báº¡n!")
        
        keyboard = [
            [InlineKeyboardButton("ðŸ“Š Xem hÆ°á»›ng dáº«n sá»­ dá»¥ng", callback_data="onboard_complete_1")],
            [InlineKeyboardButton("ðŸŽ Nháº­n thÃªm quÃ  VIP", callback_data="vip_gifts")],
            [InlineKeyboardButton("ðŸ’¬ Tham gia Group", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("ðŸ  Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "ðŸŽ‰ **XUáº¤T Sáº®C! Báº N ÄÃƒ HOÃ€N THÃ€NH SETUP!**\n\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            "âœ… Web App Freedom Wallet cá»§a báº¡n Ä‘Ã£ sáºµn sÃ ng!\n\n"
            "ðŸš€ **BÆ¯á»šC TIáº¾P THEO:**\n\n"
            "1ï¸âƒ£ **ThÃªm giao dá»‹ch Ä‘áº§u tiÃªn**\n"
            "   â€¢ Má»Ÿ Web App cá»§a báº¡n\n"
            "   â€¢ Click 'ThÃªm giao dá»‹ch'\n"
            "   â€¢ Nháº­p thu/chi hÃ´m nay\n\n"
            "2ï¸âƒ£ **KhÃ¡m phÃ¡ 6 HÅ© Tiá»n**\n"
            "   â€¢ Xem phÃ¢n bá»• tá»± Ä‘á»™ng\n"
            "   â€¢ Äiá»u chá»‰nh % theo nhu cáº§u\n\n"
            "3ï¸âƒ£ **Theo dÃµi dashboard**\n"
            "   â€¢ Biá»ƒu Ä‘á»“ thu chi\n"
            "   â€¢ ROI tracking\n"
            "   â€¢ Financial Level\n\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            "ðŸ’¡ **Lá»i khuyÃªn:**\n"
            "Track má»—i ngÃ y trong 7 ngÃ y Ä‘áº§u Ä‘á»ƒ hÃ¬nh thÃ nh thÃ³i quen!\n\n"
            "ðŸ“š Cáº§n há»— trá»£? Há»i trong Group VIP nhÃ©!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data == "webapp_setup_guide":
        # Send step-by-step setup guide with images
        await query.answer("ðŸ“– Äang gá»­i hÆ°á»›ng dáº«n chi tiáº¿t...")
        
        from pathlib import Path
        import asyncio
        
        # Step 1: Copy template
        step1_image = Path("media/images/buoc-1-copy.jpg.webp")
        if step1_image.exists():
            with open(step1_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption="ðŸ“‹ **BÆ¯á»šC 1: Táº O Báº¢N SAO**\n\n"
                            "1ï¸âƒ£ Click link template: [v3.2] Freedom Wallet\n"
                            "2ï¸âƒ£ VÃ o **File** â†’ **Make a copy**\n"
                            "3ï¸âƒ£ Äáº·t tÃªn: 'My Freedom Wallet'\n"
                            "4ï¸âƒ£ LÆ°u vÃ o Google Drive cá»§a báº¡n\n\n"
                            "âœ… Done? Chá» BÆ°á»›c 2...",
                    parse_mode="Markdown"
                )
        
        await asyncio.sleep(2)
        
        # Step 2: Apps Script
        step2_image = Path("media/images/buoc-2-appscript.jpg")
        if step2_image.exists():
            with open(step2_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption="âš™ï¸ **BÆ¯á»šC 2: Má»ž APPS SCRIPT**\n\n"
                            "1ï¸âƒ£ Trong Google Sheet vá»«a copy\n"
                            "2ï¸âƒ£ Click **Extensions** (thanh menu trÃªn)\n"
                            "3ï¸âƒ£ Chá»n **Apps Script**\n"
                            "4ï¸âƒ£ Cá»­a sá»• má»›i sáº½ má»Ÿ ra\n\n"
                            "ðŸ’¡ Náº¿u khÃ´ng tháº¥y Extensions, báº¥m vÃ o 3 cháº¥m (...) á»Ÿ menu\n\n"
                            "âœ… ÄÃ£ má»Ÿ Apps Script? Chá» BÆ°á»›c 3...",
                    parse_mode="Markdown"
                )
        
        await asyncio.sleep(2)
        
        # Step 3: Deploy
        step3_image = Path("media/images/buoc-3-deploy.jpg")
        if step3_image.exists():
            with open(step3_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption="ðŸš€ **BÆ¯á»šC 3: DEPLOY WEB APP**\n\n"
                            "1ï¸âƒ£ Trong Apps Script editor\n"
                            "2ï¸âƒ£ Click nÃºt **Deploy** (gÃ³c trÃªn bÃªn pháº£i)\n"
                            "3ï¸âƒ£ Chá»n **New deployment**\n"
                            "4ï¸âƒ£ Type: **Web app**\n"
                            "5ï¸âƒ£ Execute as: **Me**\n"
                            "6ï¸âƒ£ Who has access: **Anyone**\n"
                            "7ï¸âƒ£ Click **Deploy**\n"
                            "8ï¸âƒ£ Copy **Web app URL** â†’ Save láº¡i!\n\n"
                            "âš ï¸ **LÆ°u Ã½:** Láº§n Ä‘áº§u sáº½ cáº§n authorize (cho phÃ©p quyá»n)\n\n"
                            "âœ… ÄÃ£ deploy xong? Xem BÆ°á»›c 4...",
                    parse_mode="Markdown"
                )
        
        await asyncio.sleep(2)
        
        # Step 4: Completed
        step4_image = Path("media/images/buoc-4-completed.jpg")
        keyboard = [
            [InlineKeyboardButton("âœ… ÄÃ£ lÃ m xong!", callback_data="webapp_ready")],
            [InlineKeyboardButton("ðŸŒ HÆ°á»›ng dáº«n chi tiáº¿t", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("â“ Cáº§n há»— trá»£", callback_data="webapp_need_help")],
            [InlineKeyboardButton("ðŸ”™ Xem láº¡i tá»« Ä‘áº§u", callback_data="webapp_setup_guide")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if step4_image.exists():
            with open(step4_image, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.from_user.id,
                    photo=photo,
                    caption="ðŸŽ‰ **HOÃ€N Táº¤T! WEB APP Cá»¦A Báº N Sáº´N SÃ€NG!**\n\n"
                            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                            "ðŸŒ **Web App URL** Ä‘Ã£ Ä‘Æ°á»£c táº¡o!\n\n"
                            "ðŸ“± **CÃ¡ch sá»­ dá»¥ng:**\n"
                            "â€¢ Má»Ÿ URL trÃªn Ä‘iá»‡n thoáº¡i/mÃ¡y tÃ­nh\n"
                            "â€¢ Add to Home Screen (náº¿u dÃ¹ng mobile)\n"
                            "â€¢ Báº¯t Ä‘áº§u thÃªm giao dá»‹ch!\n\n"
                            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                            "ðŸ’¡ **Máº¹o:**\n"
                            "â€¢ Bookmark URL Ä‘á»ƒ truy cáº­p nhanh\n"
                            "â€¢ Äá»“ng bá»™ tá»± Ä‘á»™ng má»—i khi báº¡n cáº­p nháº­t\n"
                            "â€¢ Dá»¯ liá»‡u lÆ°u trong Google Sheet cá»§a báº¡n\n\n"
                            "ðŸŽ¯ **Báº¡n Ä‘Ã£ lÃ m xong chÆ°a?**",
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
        else:
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text="ðŸŽ‰ **HOÃ€N Táº¤T! WEB APP Cá»¦A Báº N Sáº´N SÃ€NG!**\n\n"
                     "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                     "ðŸŒ **Web App URL** Ä‘Ã£ Ä‘Æ°á»£c táº¡o!\n\n"
                     "ðŸ“± **CÃ¡ch sá»­ dá»¥ng:**\n"
                     "â€¢ Má»Ÿ URL trÃªn Ä‘iá»‡n thoáº¡i/mÃ¡y tÃ­nh\n"
                     "â€¢ Add to Home Screen (náº¿u dÃ¹ng mobile)\n"
                     "â€¢ Báº¯t Ä‘áº§u thÃªm giao dá»‹ch!\n\n"
                     "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                     "ðŸ’¡ **Máº¹o:**\n"
                     "â€¢ Bookmark URL Ä‘á»ƒ truy cáº­p nhanh\n"
                     "â€¢ Äá»“ng bá»™ tá»± Ä‘á»™ng má»—i khi báº¡n cáº­p nháº­t\n"
                     "â€¢ Dá»¯ liá»‡u lÆ°u trong Google Sheet cá»§a báº¡n\n\n"
                     "ðŸŽ¯ **Báº¡n Ä‘Ã£ lÃ m xong chÆ°a?**",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    
    elif callback_data == "webapp_need_help":
        # User needs help with Web App setup
        keyboard = [
            [InlineKeyboardButton("ðŸ”™ Xem láº¡i hÆ°á»›ng dáº«n", callback_data="webapp_setup_guide")],
            [InlineKeyboardButton("ðŸŒ Notion chi tiáº¿t", url="https://eliroxbot.notion.site/freedomwallet")],
            [InlineKeyboardButton("ðŸ’¬ Há»i trong Group", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("ðŸ“ž LiÃªn há»‡ Admin", url=f"https://t.me/{settings.BOT_USERNAME.replace('Bot', '')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "â“ **Cáº¦N Há»– TRá»¢ SETUP WEB APP?**\n\n"
            "MÃ¬nh sáºµn sÃ ng giÃºp báº¡n!\n\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            "**ðŸ’¬ CÃC CÃCH ÄÆ¯á»¢C Há»– TRá»¢:**\n\n"
            "1ï¸âƒ£ **Xem láº¡i hÆ°á»›ng dáº«n**\n"
            "   â€¢ Click 'Xem láº¡i hÆ°á»›ng dáº«n'\n"
            "   â€¢ Follow tá»«ng bÆ°á»›c cáº©n tháº­n\n\n"
            "2ï¸âƒ£ **Äá»c Notion chi tiáº¿t**\n"
            "   â€¢ HÆ°á»›ng dáº«n cÃ³ áº£nh chá»¥p mÃ n hÃ¬nh\n"
            "   â€¢ Video demo\n"
            "   â€¢ FAQ troubleshooting\n\n"
            "3ï¸âƒ£ **Há»i Group VIP**\n"
            "   â€¢ Response nhanh tá»« community\n"
            "   â€¢ Nhiá»u ngÆ°á»i Ä‘Ã£ setup thÃ nh cÃ´ng\n\n"
            "4ï¸âƒ£ **LiÃªn há»‡ Admin trá»±c tiáº¿p**\n"
            "   â€¢ 1-1 support\n"
            "   â€¢ Screen share náº¿u cáº§n\n\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            "â° **Thá»i gian há»— trá»£:**\n"
            "â€¢ Thá»© 2-6: 9h-21h\n"
            "â€¢ Thá»© 7-CN: 10h-18h\n\n"
            "**Gáº·p váº¥n Ä‘á» gÃ¬ cá»¥ thá»ƒ?**\nGÃµ mÃ´ táº£ Ä‘á»ƒ mÃ¬nh há»— trá»£!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data == "super_vip_benefits":
        # Show Super VIP benefits details
        keyboard = [
            [InlineKeyboardButton("ðŸ† Xem Báº£ng xáº¿p háº¡ng", callback_data="leaderboard")],
            [InlineKeyboardButton("ðŸŽ Nháº­n quÃ  Ä‘áº·c biá»‡t", callback_data="super_vip_gifts")],
            [InlineKeyboardButton("ðŸ  Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            "ðŸŒŸ **Äáº¶C QUYá»€N SUPER VIP**\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            "**âœ¨ Táº¥t cáº£ quyá»n lá»£i VIP PLUS:**\n\n"
            "ðŸŽ¯ **Há»— trá»£ Æ°u tiÃªn cáº¥p cao 24/7**\n"
            "   â€¢ Response time < 30 phÃºt\n"
            "   â€¢ Dedicated support team\n"
            "   â€¢ Direct line vá»›i Admin\n\n"
            "ðŸŽ **QuÃ  táº·ng Ä‘á»™c quyá»n hÃ ng thÃ¡ng**\n"
            "   â€¢ Templates má»›i nháº¥t\n"
            "   â€¢ Scripts nÃ¢ng cao\n"
            "   â€¢ Exclusive features\n\n"
            "ðŸ† **Hiá»ƒn thá»‹ trÃªn Báº£ng xáº¿p háº¡ng**\n"
            "   â€¢ Top Referrers public\n"
            "   â€¢ Badge Ä‘áº·c biá»‡t\n"
            "   â€¢ Recognition tá»« cá»™ng Ä‘á»“ng\n\n"
            "ðŸ’¬ **Group Super VIP Private**\n"
            "   â€¢ Networking vá»›i top performers\n"
            "   â€¢ Share strategies & tips\n"
            "   â€¢ Early access features\n\n"
            "ðŸŽ“ **Workshop & Training Ä‘á»™c quyá»n**\n"
            "   â€¢ Monthly masterclasses\n"
            "   â€¢ Advanced techniques\n"
            "   â€¢ One-on-one coaching\n\n"
            "ðŸ’° **Commission cao hÆ¡n** (Coming soon)\n"
            "   â€¢ Affiliate program\n"
            "   â€¢ Revenue sharing\n"
            "   â€¢ Partnership opportunities\n\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            "âš¡ **LÆ°u Ã½:** Super VIP cáº§n duy trÃ¬\n"
            "hoáº¡t Ä‘á»™ng thÆ°á»ng xuyÃªn Ä‘á»ƒ giá»¯ danh hiá»‡u.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    elif callback_data == "leaderboard":
        # Show top referrers leaderboard
        from app.utils.database import SessionLocal, User
        
        session = SessionLocal()
        try:
            # Get top 10 referrers (exclude admins)
            top_users = session.query(User).filter(
                User.referral_count > 0
            ).order_by(
                User.referral_count.desc()
            ).limit(10).all()
            
            leaderboard_text = "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            leaderboard_text += "ðŸ† **Báº¢NG Xáº¾P Háº NG TOP REFERRERS**\n"
            leaderboard_text += "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            
            medals = ["ðŸ¥‡", "ðŸ¥ˆ", "ðŸ¥‰"]
            for idx, user in enumerate(top_users, 1):
                medal = medals[idx-1] if idx <= 3 else f"{idx}ï¸âƒ£"
                name = user.username or user.full_name or "Anonymous"
                refs = user.referral_count
                
                # Show Super VIP badge
                badge = "ðŸŒŸ" if refs >= 50 else "â­" if refs >= 2 else ""
                
                leaderboard_text += f"{medal} **{name}** {badge}\n"
                leaderboard_text += f"     {refs} lÆ°á»£t giá»›i thiá»‡u\n\n"
            
            leaderboard_text += "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            leaderboard_text += "ðŸ’¡ Báº¡n muá»‘n lÃªn top? Share link ngay!\n"
            leaderboard_text += "/referral Ä‘á»ƒ xem link cá»§a báº¡n"
            
            keyboard = [
                [InlineKeyboardButton("ðŸ”— Xem link giá»›i thiá»‡u", callback_data="referral_menu")],
                [InlineKeyboardButton("ðŸŒŸ Äáº·c quyá»n Super VIP", callback_data="super_vip_benefits")],
                [InlineKeyboardButton("ðŸ  Dashboard", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                leaderboard_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        finally:
            session.close()
    
    elif callback_data == "super_vip_gifts":
        # Show Super VIP exclusive gifts
        keyboard = [
            [InlineKeyboardButton("ðŸ“Š Advanced Templates", callback_data="super_gift_templates")],
            [InlineKeyboardButton("âš™ï¸ Premium Scripts", callback_data="super_gift_scripts")],
            [InlineKeyboardButton("ðŸŽ“ Exclusive Training", url="https://freedomwallet.com/super-vip-training")],
            [InlineKeyboardButton("ðŸ’¬ Join Super VIP Group", url="https://t.me/freedomwallet_supervip")],
            [InlineKeyboardButton("ðŸ  Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            "ðŸŽ **QUÃ€ Táº¶NG SUPER VIP**\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
            "**Chá»n quÃ  báº¡n muá»‘n nháº­n:**\n\n"
            "ðŸ“Š **Advanced Templates**\n"
            "   â€¢ Multiple portfolios support\n"
            "   â€¢ Advanced analytics dashboard\n"
            "   â€¢ Custom reporting tools\n\n"
            "âš™ï¸ **Premium Scripts**\n"
            "   â€¢ Auto-sync enhancements\n"
            "   â€¢ Bank integration (beta)\n"
            "   â€¢ Advanced automation\n\n"
            "ðŸŽ“ **Exclusive Training**\n"
            "   â€¢ Monthly webinars\n"
            "   â€¢ Strategy sessions\n"
            "   â€¢ Private consultations\n\n"
            "ðŸ’¬ **Super VIP Group**\n"
            "   â€¢ Network vá»›i top users\n"
            "   â€¢ Share best practices\n"
            "   â€¢ Early feature access\n\n"
            "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
            "ðŸŽ‰ Táº¥t cáº£ Ä‘á»u MIá»„N PHÃ cho Super VIP!",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    else:
        # Unknown callback
        logger.warning(f"Unknown callback: {callback_data}")
        await query.edit_message_text(
            "âš ï¸ Lá»‡nh khÃ´ng há»£p lá»‡. DÃ¹ng /help Ä‘á»ƒ xem menu!",
            parse_mode="Markdown"
        )

# ============================================================================
# ONBOARDING GUIDES - Premium Trial Users
# ============================================================================

async def handle_webapp_setup_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guide user through Web App installation (30 seconds)"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ“± **CÃ€I Äáº¶T WEB APP (30 GIÃ‚Y)**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
**BÆ¯á»šC 1: Má»Ÿ freedomwallet.vn**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŒ Truy cáº­p: freedomwallet.vn
ðŸ“± DÃ¹ng Safari (iOS) / Chrome (Android)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
**BÆ¯á»šC 2: CÃ i lÃªn Home Screen**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**iPhone:** 
Share (â¬†ï¸) â†’ Add to Home Screen â†’ Add

**Android:**
Menu (â‹®) â†’ Add to Home screen â†’ Add

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
**BÆ¯á»šC 3: Má»Ÿ App**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŽ¯ TÃ¬m icon Freedom Wallet
ðŸ“² Má»Ÿ nhÆ° app bÃ¬nh thÆ°á»ng
ðŸš€ Báº¯t Ä‘áº§u quáº£n lÃ½ tÃ i chÃ­nh!

ðŸ’¡ **LÆ°u Ã½:** Láº§n Ä‘áº§u hÆ¡i lÃ¢u (10s), sau Ä‘Ã³ mÆ°á»£t mÃ !
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ“– HÆ°á»›ng dáº«n sá»­ dá»¥ng", callback_data="premium_usage_guide")],
        [InlineKeyboardButton("ðŸŒ Má»Ÿ Web App", url="https://freedomwallet.vn")],
        [InlineKeyboardButton("ðŸ  Menu Premium", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_wow_moment_dismiss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle WOW moment dismiss - User clicked 'OK, Ä‘Ã£ hiá»ƒu'"""
    query = update.callback_query
    await query.answer("Tuyá»‡t vá»i! Tiáº¿p tá»¥c sá»­ dá»¥ng Premium nhÃ©! ðŸš€")
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'wow_moment_dismissed')
    
    await query.edit_message_text(
        "âœ… **ÄÃ£ ghi nháº­n!**\n\n"
        "Báº¡n cÃ³ thá»ƒ xem láº¡i ROI báº¥t ká»³ lÃºc nÃ o báº±ng lá»‡nh /mystatus\n\n"
        "ðŸ’¡ Tip: Sá»­ dá»¥ng nhiá»u Ä‘á»ƒ tá»‘i Ä‘a hÃ³a giÃ¡ trá»‹ Premium nhÃ©!",
        parse_mode="Markdown"
    )


async def handle_trial_reminder_viewed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track when user views trial reminder"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'trial_reminder_viewed')
    
    # Handler logic is in upgrade_to_premium or view_roi_detail
    # This is just for tracking
    

async def handle_why_premium_from_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 'Táº¡i sao nÃªn Premium?' click from trial reminder"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'trial_reminder_upgrade_clicked', {'source': 'why_premium'})
    
    message = """
ðŸ¤” **Táº I SAO NÃŠN PREMIUM?**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’Ž **GIÃ TRá»Š VÆ¯á»¢T TRá»˜I:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**1ï¸âƒ£ TIáº¾T KIá»†M THá»œI GIAN**
â±ï¸ Má»—i ngÃ y tiáº¿t kiá»‡m ~1-2 giá»
   â†’ KhÃ´ng cáº§n tá»± tÃ­nh toÃ¡n
   â†’ KhÃ´ng cáº§n tá»•ng há»£p thá»§ cÃ´ng
   â†’ KhÃ´ng cáº§n lÃªn káº¿ hoáº¡ch

**2ï¸âƒ£ TÄ‚NG HIá»†U QUáº¢ TÃ€I CHÃNH**
ðŸ“Š PhÃ¢n tÃ­ch thÃ´ng minh 24/7
   â†’ PhÃ¡t hiá»‡n Ä‘iá»ƒm lÃ£ng phÃ­
   â†’ Tá»‘i Æ°u ngÃ¢n sÃ¡ch
   â†’ TÄƒng tá»· lá»‡ tiáº¿t kiá»‡m

**3ï¸âƒ£ Äáº¦U TÆ¯ NHá»Ž, Lá»¢I NHUáº¬N Lá»šN**
ðŸ’° ~2,750 VNÄ/ngÃ y
   â†’ GiÃ¡ 1 ly cÃ  phÃª
   â†’ NhÆ°ng giÃ¡ trá»‹ gáº¥p 5-10 láº§n
   â†’ ROI trung bÃ¬nh +200%

**4ï¸âƒ£ KHÃ”NG QUáº¢NG CÃO**
âœ¨ Tráº£i nghiá»‡m premium thá»±c sá»±
   â†’ Táº­p trung 100%
   â†’ KhÃ´ng giÃ¡n Ä‘oáº¡n
   â†’ KhÃ´ng lÃ m phiá»n

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸŽ¯ **Äá»‚ Äáº T ROI +200%:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… Chat vá»›i AI má»—i ngÃ y (10+ tin)
âœ… Check dashboard 2-3 láº§n/tuáº§n
âœ… Äá»c gá»£i Ã½ má»—i sÃ¡ng
âœ… DÃ¹ng phÃ¢n tÃ­ch khi cáº§n

â†’ Thá»i gian tiáº¿t kiá»‡m: ~8-10 giá»/thÃ¡ng
â†’ GiÃ¡ trá»‹: ~800K - 1M VNÄ
â†’ Chi phÃ­: ~83K VNÄ/thÃ¡ng
â†’ **Lá»i: ~700K - 900K VNÄ!**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ **Káº¾T LUáº¬N:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

Premium khÃ´ng pháº£i chi phÃ­,
mÃ  lÃ  **Ä‘áº§u tÆ° sinh lá»i**! ðŸš€
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ’Ž NÃ¢ng cáº¥p ngay", callback_data="upgrade_to_premium")],
        [InlineKeyboardButton("ðŸ“Š Xem ROI cá»§a tÃ´i", callback_data="view_roi_detail")],
        [InlineKeyboardButton("ðŸ  Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ============================================================================
# DAY 2: ROI & UPSELL HANDLERS
# ============================================================================

async def handle_upgrade_to_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upgrade to premium callback - Show payment options with QR code"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = query.from_user.id
        
        # Track analytics
        Analytics.track_event(user_id, 'upgrade_from_status_clicked')
        
        # Get payment info with QR code
        from app.services.payment_service import PaymentService
        payment_info = PaymentService.get_payment_instructions(user_id, "PREMIUM")
        
        # Format payment message
        message = PaymentService.format_payment_message(payment_info)
        
        keyboard = [
            [InlineKeyboardButton("âœ… ÄÃ£ thanh toÃ¡n", callback_data="confirm_payment")],
            [InlineKeyboardButton("ðŸ’¬ LiÃªn há»‡ Admin", callback_data="contact_support")],
            [InlineKeyboardButton("ðŸ“Š Xem ROI chi tiáº¿t", callback_data="view_roi_detail")],
            [InlineKeyboardButton("ðŸ¤” Táº¡i sao nÃªn Premium?", callback_data="why_premium")],
            [InlineKeyboardButton("Â« Quay láº¡i", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send QR code image
        try:
            await query.message.reply_photo(
                photo=payment_info['qr_url'],
                caption=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            # Delete the previous message to keep chat clean
            await query.message.delete()
        except Exception as e:
            logger.error(f"Error sending QR code: {e}")
            # Fallback to text only
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error in handle_upgrade_to_premium: {e}", exc_info=True)
        await query.edit_message_text(
            "ðŸ˜“ Xin lá»—i, cÃ³ lá»—i khi táº£i thÃ´ng tin thanh toÃ¡n. Vui lÃ²ng thá»­ láº¡i sau!\n\n"
            "Hoáº·c liÃªn há»‡ Admin Ä‘á»ƒ Ä‘Æ°á»£c há»— trá»£: /support",
            parse_mode="Markdown"
        )


async def handle_confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment confirmation - Create verification request"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'payment_confirmation_clicked')
    
    # Store user ID in context for next step
    context.user_data['awaiting_payment_proof'] = True
    context.user_data['payment_amount'] = 999000  # Premium price
    
    message = """
âœ… **XÃC NHáº¬N THANH TOÃN**

Cáº£m Æ¡n báº¡n Ä‘Ã£ thanh toÃ¡n! Äá»ƒ xÃ¡c nháº­n nhanh chÃ³ng, vui lÃ²ng:

**ðŸ“¸ Gá»­i áº£nh chá»¥p mÃ n hÃ¬nh:**
â€¢ ThÃ´ng bÃ¡o chuyá»ƒn khoáº£n thÃ nh cÃ´ng
â€¢ Hoáº·c lá»‹ch sá»­ giao dá»‹ch trong app ngÃ¢n hÃ ng

**âœï¸ Hoáº·c gá»­i thÃ´ng tin:**
â€¢ Sá»‘ tiá»n Ä‘Ã£ chuyá»ƒn
â€¢ Thá»i gian chuyá»ƒn khoáº£n
â€¢ 4 sá»‘ cuá»‘i STK cá»§a báº¡n (náº¿u cÃ³)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
â±ï¸ **THá»œI GIAN Xá»¬ LÃ:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

â€¢ Tá»± Ä‘á»™ng: 5-10 phÃºt
â€¢ Thá»§ cÃ´ng: 15-30 phÃºt (giá» hÃ nh chÃ­nh)
â€¢ NgoÃ i giá»: Trong 2 giá»

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ **LÆ¯U Ã:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… ÄÃ£ chuyá»ƒn Ä‘Ãºng ná»™i dung? â†’ Tá»± Ä‘á»™ng kÃ­ch hoáº¡t
âš ï¸ Chuyá»ƒn sai ná»™i dung? â†’ Cáº§n xÃ¡c nháº­n thá»§ cÃ´ng

ðŸ“ž **Cáº§n há»— trá»£?** Nháº¥n "LiÃªn há»‡ Admin" bÃªn dÆ°á»›i
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ’¬ LiÃªn há»‡ Admin", callback_data="contact_support")],
        [InlineKeyboardButton("Â« Quay láº¡i", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Delete the QR code message and send new text message
    try:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in handle_confirm_payment: {e}")
        # Fallback: try to edit if message is text
        try:
            await query.edit_message_text(
                message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except:
            # Last resort: send new message without deleting
            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )


async def handle_view_roi_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view ROI detail callback - Show detailed ROI breakdown"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'roi_detail_viewed')
    
    # Get ROI calculation
    from app.services.roi_calculator import ROICalculator
    from app.utils.database import get_user_by_id
    from app.core.subscription import SubscriptionManager, SubscriptionTier
    
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user) if user else SubscriptionTier.FREE
    roi = ROICalculator.calculate_monthly_roi(user_id)
    
    tier_name = tier.value if tier else "FREE"
    
    message = f"""
ðŸ“Š **ROI DASHBOARD CHI TIáº¾T**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“ˆ **PHÃ‚ N TÃCH Sá»¬ Dá»¤NG:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¬ **{roi['messages']} tin nháº¯n** vá»›i AI
   â†’ Tiáº¿t kiá»‡m: {roi['messages'] * 3} phÃºt
   
ðŸ“Š **{roi['analyses']} phÃ¢n tÃ­ch** tÃ i chÃ­nh
   â†’ Tiáº¿t kiá»‡m: {roi['analyses'] * 30} phÃºt
   
ðŸ’¡ **{roi['recommendations']} gá»£i Ã½** cÃ¡ nhÃ¢n
   â†’ Tiáº¿t kiá»‡m: {roi['recommendations'] * 15} phÃºt
   
ðŸ“ˆ **{roi['dashboard_views']} láº§n** xem dashboard
   â†’ Tiáº¿t kiá»‡m: {roi['dashboard_views'] * 20} phÃºt

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
â±ï¸ **Tá»”NG THá»œI GIAN:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

Tiáº¿t kiá»‡m: **{roi['time_saved']} giá»**
GiÃ¡ trá»‹: **{roi['value']:,} VNÄ**
(TÃ­nh theo 100K VNÄ/giá»)

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’° **TÃNH TOÃN ROI:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

Chi phÃ­ {tier_name}: {roi['cost']:,} VNÄ/thÃ¡ng
GiÃ¡ trá»‹ nháº­n: {roi['value']:,} VNÄ/thÃ¡ng

â†’ **Lá»i/Lá»—: {roi['profit']:,} VNÄ**
â†’ **ROI: {roi['roi_percent']:+.0f}%**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’¡ **CÃCH Tá»I Æ¯U:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

â€¢ Sá»­ dá»¥ng nhiá»u hÆ¡n = ROI cao hÆ¡n
â€¢ Má»¥c tiÃªu: â‰¥+200% ROI
â€¢ Chat vá»›i AI má»—i ngÃ y
â€¢ DÃ¹ng tÃ­nh nÄƒng PhÃ¢n tÃ­ch thÆ°á»ng xuyÃªn
"""
    
    if tier == SubscriptionTier.FREE:
        message += "\n\nðŸ’Ž NÃ¢ng cáº¥p Premium Ä‘á»ƒ unlock ROI cao hÆ¡n!"
        keyboard = [
            [InlineKeyboardButton("ðŸŽ DÃ¹ng thá»­ 7 ngÃ y FREE", callback_data="start_trial")],
            [InlineKeyboardButton("ðŸ’Ž Xem gÃ³i Premium", callback_data="view_premium")],
            [InlineKeyboardButton("Â« Quay láº¡i", callback_data="start")]
        ]
    elif tier == SubscriptionTier.TRIAL:
        keyboard = [
            [InlineKeyboardButton("ðŸ’Ž NÃ¢ng cáº¥p Premium ngay", callback_data="upgrade_to_premium")],
            [InlineKeyboardButton("ðŸ’¡ Tips tá»‘i Æ°u", callback_data="optimization_tips")],
            [InlineKeyboardButton("Â« Quay láº¡i", callback_data="start")]
        ]
    else:  # PREMIUM
        keyboard = [
            [InlineKeyboardButton("ðŸ’¡ Tips tá»‘i Æ°u ROI", callback_data="optimization_tips")],
            [InlineKeyboardButton("ðŸ“Š Xem status", callback_data="my_status")],
            [InlineKeyboardButton("Â« Quay láº¡i", callback_data="start")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_optimization_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle optimization tips callback - Show tips to maximize ROI"""
    query = update.callback_query
    await query.answer()
    
    # Track analytics
    Analytics.track_event(query.from_user.id, 'optimization_tips_viewed')
    
    message = """
ðŸ’¡ **TIPS Tá»I Æ¯U ROI PREMIUM**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸŽ¯ **Má»¤C TIÃŠU: ROI â‰¥ +200%**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**1ï¸âƒ£ Sá»¬ Dá»¤NG AI Má»–I NGÃ€Y**

ðŸ’¬ Chat vá»›i bot Ã­t nháº¥t 10 tin/ngÃ y
   â†’ Há»i vá» financial planning
   â†’ TÆ° váº¥n tiáº¿t kiá»‡m
   â†’ PhÃ¢n tÃ­ch thÃ³i quen chi tiÃªu

**2ï¸âƒ£ DÃ™NG TÃNH NÄ‚NG PHÃ‚N TÃCH**

ðŸ“Š Xem dashboard 2-3 láº§n/tuáº§n
   â†’ Theo dÃµi xu hÆ°á»›ng chi tiÃªu
   â†’ PhÃ¡t hiá»‡n Ä‘iá»ƒm báº¥t thÆ°á»ng
   â†’ Äiá»u chá»‰nh ká»‹p thá»i

**3ï¸âƒ£ NHáº¬N Gá»¢I Ã CÃ NHÃ‚N**

ðŸ’¡ Check gá»£i Ã½ má»—i sÃ¡ng
   â†’ Lá»i khuyÃªn tá»‘i Æ°u tÃ i chÃ­nh
   â†’ Tips tiáº¿t kiá»‡m theo ngá»¯ cáº£nh
   â†’ Nháº¯c nhá»Ÿ quan trá»ng

**4ï¸âƒ£ THIáº¾T Láº¬P Má»¤C TIÃŠU**

âš™ï¸ CÃ i Ä‘áº·t má»¥c tiÃªu tÃ i chÃ­nh
   â†’ Tiáº¿t kiá»‡m thÃ¡ng
   â†’ Káº¿ hoáº¡ch Ä‘áº§u tÆ°
   â†’ Budget cho tá»«ng danh má»¥c

**5ï¸âƒ£ Há»ŽI THÃ”NG MINH**

ðŸ§  Há»i nhá»¯ng cÃ¢u há»i cá»¥ thá»ƒ:
   â€¢ "PhÃ¢n tÃ­ch chi tiÃªu thÃ¡ng nÃ y"
   â€¢ "TÃ´i nÃªn tiáº¿t kiá»‡m á»Ÿ Ä‘Ã¢u?"
   â€¢ "ROI Ä‘áº§u tÆ° nÃ y bao nhiÃªu?"
   â€¢ "CÃ¡ch tá»‘i Æ°u 6 hÅ© tiá»n?"

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“ˆ **Káº¾T QUáº¢ Ká»² Vá»ŒNG:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… 10+ messages/day = +150% ROI
âœ… 20+ messages/day = +300% ROI
âœ… Active usage = +500% ROI

â†’ **Premium tráº£ lá»i báº£n thÃ¢n!** ðŸš€

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’ª **Báº®T Äáº¦U NGAY HÃ”M NAY!**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

GÃµ cÃ¢u há»i Ä‘áº§u tiÃªn vá» tÃ i chÃ­nh cá»§a báº¡n ðŸ‘‡
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ’¬ Chat vá»›i AI ngay", callback_data="start")],
        [InlineKeyboardButton("ðŸ“Š Xem ROI hiá»‡n táº¡i", callback_data="view_roi_detail")],
        [InlineKeyboardButton("ðŸ  Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_premium_usage_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show Premium features usage guide"""
    query = update.callback_query
    await query.answer()
    
    message = """
ðŸ“– **HÆ¯á»šNG DáºªN Sá»¬ Dá»¤NG PREMIUM**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
âœ¨ **6 TÃNH NÄ‚NG CHÃNH**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

**ðŸ“ 1. Ghi chi tiÃªu nhanh**
â€¢ Gá»­i: "50k cafe" â†’ Tá»± Ä‘á»™ng ghi
â€¢ Há»— trá»£ nhiá»u Ä‘á»‹nh dáº¡ng
â€¢ KhÃ´ng cáº§n form phá»©c táº¡p

**ðŸ“Š 2. TÃ¬nh hÃ¬nh tÃ i chÃ­nh**
â€¢ Xem dashboard real-time
â€¢ Thu chi theo ngÃ y/tuáº§n/thÃ¡ng
â€¢ Biá»ƒu Ä‘á»“ trá»±c quan

**ðŸ” 3. PhÃ¢n tÃ­ch thÃ´ng minh**
â€¢ AI phÃ¢n tÃ­ch thÃ³i quen chi tiÃªu
â€¢ PhÃ¡t hiá»‡n chi tiÃªu báº¥t thÆ°á»ng
â€¢ Dá»± bÃ¡o xu hÆ°á»›ng

**ðŸ’¡ 4. Gá»£i Ã½ cÃ¡ nhÃ¢n hÃ³a**
â€¢ Gá»£i Ã½ tiáº¿t kiá»‡m hÃ ng ngÃ y
â€¢ Nháº¯c nhá»Ÿ khi chÆ°a ghi chÃ©p
â€¢ Tips tá»‘i Æ°u tÃ i chÃ­nh

**âš™ï¸ 5. Setup nÃ¢ng cao**
â€¢ TÃ¹y chá»‰nh 6 hÅ© tiá»n theo nhu cáº§u
â€¢ Thiáº¿t láº­p má»¥c tiÃªu tÃ i chÃ­nh
â€¢ Sync dá»¯ liá»‡u tá»± Ä‘á»™ng

**ðŸ†˜ 6. Há»— trá»£ Æ°u tiÃªn**
â€¢ Response trong 30 phÃºt
â€¢ Chat trá»±c tiáº¿p vá»›i founder
â€¢ Há»— trá»£ 1-1 qua call náº¿u cáº§n

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸŽ¯ **Báº®T Äáº¦U NGAY:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

1ï¸âƒ£ Thá»­ ghi 1 giao dá»‹ch: "20k trÃ  sá»¯a"
2ï¸âƒ£ Xem dashboard: Báº¥m "ðŸ“Š TÃ¬nh hÃ¬nh"
3ï¸âƒ£ Nháº­n gá»£i Ã½: Báº¥m "ðŸ’¡ Gá»£i Ã½"

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“š **TÃ€I LIá»†U CHI TIáº¾T:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸŒ Xem full guide táº¡i:
ðŸ‘‰ [eliroxbot.notion.site/freedomwallet](https://eliroxbot.notion.site/freedomwallet)

ðŸŽŠ **ChÃºc báº¡n quáº£n lÃ½ tÃ i chÃ­nh hiá»‡u quáº£!**
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸŒ Xem guide Ä‘áº§y Ä‘á»§", url="https://eliroxbot.notion.site/freedomwallet")],
        [InlineKeyboardButton("ðŸ“± CÃ i Web App", callback_data="webapp_setup_guide")],
        [InlineKeyboardButton("ðŸ  Menu Premium", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup,
        disable_web_page_preview=False
    )


async def handle_free_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle free_chat callback - Prompt user to ask a question"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'free_chat_clicked')
    
    message = """
ðŸ’¬ **CHAT Vá»šI BOT (FREE)**

HÃ£y gÃµ cÃ¢u há»i cá»§a báº¡n, tÃ´i sáº½ tráº£ lá»i ngay! ðŸ˜Š

ðŸ“‹ **CÃ¡c chá»§ Ä‘á» tÃ´i cÃ³ thá»ƒ giÃºp:**
â€¢ HÆ°á»›ng dáº«n sá»­ dá»¥ng Freedom Wallet
â€¢ CÃ¡ch thÃªm/xÃ³a/sá»­a giao dá»‹ch
â€¢ Giáº£i thÃ­ch vá» 6 HÅ© Tiá»n
â€¢ CÃ¡ch setup Google Sheet
â€¢ Kháº¯c phá»¥c lá»—i thÆ°á»ng gáº·p
â€¢ Tips quáº£n lÃ½ tÃ i chÃ­nh

ðŸ’¬ **Giá»›i háº¡n hÃ´m nay:** 5 tin nháº¯n

GÃµ cÃ¢u há»i cá»§a báº¡n bÃªn dÆ°á»›i! ðŸ‘‡
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ  Quay vá» Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_upgrade_premium_from_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle upgrade_premium callback from start menu - Show trial offer"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Track analytics
    Analytics.track_event(user_id, 'upgrade_premium_clicked_from_start')
    
    message = """
ðŸŽ **DÃ™NG THá»¬ PREMIUM 7 NGÃ€Y MIá»„N PHÃ**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
âœ¨ **Báº N Sáº¼ NHáº¬N ÄÆ¯á»¢C:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ’¬ **Unlimited Chat vá»›i AI**
   â†’ KhÃ´ng giá»›i háº¡n tin nháº¯n
   â†’ Tráº£ lá»i 24/7 trong vÃ i giÃ¢y

ðŸ“Š **PhÃ¢n TÃ­ch TÃ i ChÃ­nh ThÃ´ng Minh**
   â†’ AI phÃ¢n tÃ­ch chi tiÃªu cá»§a báº¡n
   â†’ PhÃ¡t hiá»‡n Ä‘iá»ƒm lÃ£ng phÃ­
   â†’ Äá» xuáº¥t tá»‘i Æ°u hÃ³a

ðŸ’¡ **Gá»£i Ã CÃ¡ NhÃ¢n HÃ³a**
   â†’ Má»—i ngÃ y nháº­n 1 tips má»›i
   â†’ Dá»±a trÃªn thÃ³i quen chi tiÃªu
   â†’ GiÃºp tiáº¿t kiá»‡m tá»‘i Ä‘a

ðŸ“ˆ **ROI Dashboard**
   â†’ Xem giÃ¡ trá»‹ Premium mang láº¡i
   â†’ Thá»‘ng kÃª thá»i gian tiáº¿t kiá»‡m
   â†’ TÃ­nh toÃ¡n lá»£i nhuáº­n Ä‘áº§u tÆ°

ðŸš€ **Há»— Trá»£ Æ¯u TiÃªn**
   â†’ Pháº£n há»“i trong 30 phÃºt
   â†’ Há»— trá»£ 1-1 qua chat
   â†’ Setup & troubleshooting

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸŽ¯ **SAU 7 NGÃ€Y:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

Náº¿u thÃ­ch â†’ NÃ¢ng cáº¥p Premium
Náº¿u khÃ´ng â†’ Quay vá» FREE (5 msg/ngÃ y)

**100% khÃ´ng máº¥t phÃ­, khÃ´ng cáº§n tháº» tÃ­n dá»¥ng!**

Báº¯t Ä‘áº§u ngay? ðŸ‘‡
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸŽ Báº¯t Ä‘áº§u dÃ¹ng thá»­ NGAY", callback_data="start_trial")],
        [InlineKeyboardButton("ðŸ’° Xem gÃ³i Premium", callback_data="view_premium")],
        [InlineKeyboardButton("â“ Táº¡i sao nÃªn Premium?", callback_data="why_premium")],
        [InlineKeyboardButton("ðŸ  Quay vá» Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

