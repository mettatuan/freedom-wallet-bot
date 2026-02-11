"""
FREE Flow Registration - Collect user info before starting setup
Calm, value-first approach
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, ConversationHandler
from loguru import logger
from app.utils.database import SessionLocal, User, generate_referral_code
from app.utils.sheets_registration import save_user_to_registration_sheet
import re
from datetime import datetime
from pathlib import Path

# Conversation states
AWAITING_EMAIL, AWAITING_PHONE, AWAITING_NAME = range(3)


async def free_step1_intro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 1 - Show intro + collect info"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Check if user already has full info
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if db_user and db_user.email and db_user.phone and db_user.full_name:
            # Already have info, skip to step 2
            logger.info(f"User {user.id} already has registration info, skipping to step 2")
            await query.edit_message_text("Äang táº£i...")
            
            # Import here to avoid circular dependency
            from app.handlers.user.free_flow import free_step2_show_value
            update.callback_query = query
            await free_step2_show_value(update, context)
            return ConversationHandler.END
    finally:
        db.close()
    
    # Send intro message with image
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

Äá»ƒ báº¯t Ä‘áº§u, tÃ´i cáº§n vÃ i thÃ´ng tin cÆ¡ báº£n.
"""
    
    # Send photo first, then ask for info
    image_path = Path("media/images/web_apps.jpg")
    
    try:
        await query.message.reply_photo(
            photo=open(image_path, 'rb'),
            caption=message,
            parse_mode="Markdown"
        )
        
        await query.message.reply_text(
            "ðŸ“§ **BÆ°á»›c 1/3**: Nháº­p email cá»§a báº¡n\n"
            "(Äá»ƒ gá»­i hÆ°á»›ng dáº«n vÃ  template)",
            parse_mode="Markdown"
        )
        
        # Delete original message
        await query.message.delete()
        
        return AWAITING_EMAIL
        
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        await query.edit_message_text(
            message + "\n\nðŸ“§ **BÆ°á»›c 1/3**: Nháº­p email cá»§a báº¡n\n"
            "(Äá»ƒ gá»­i hÆ°á»›ng dáº«n vÃ  template)",
            parse_mode="Markdown"
        )
        return AWAITING_EMAIL


async def receive_free_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate email"""
    email = update.message.text.strip()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await update.message.reply_text(
            "âŒ Email khÃ´ng há»£p lá»‡.\n\n"
            "Vui lÃ²ng nháº­p láº¡i (vÃ­ dá»¥: name@gmail.com):"
        )
        return AWAITING_EMAIL
    
    # Save to context
    context.user_data['registration_email'] = email
    
    await update.message.reply_text(
        f"âœ… Email: {email}\n\n"
        f"ðŸ“± **BÆ°á»›c 2/3**: Nháº­p sá»‘ Ä‘iá»‡n thoáº¡i\n"
        f"(Äá»ƒ há»— trá»£ qua Zalo/WhatsApp náº¿u cáº§n)\n\n"
        f"Hoáº·c gÃµ /skip náº¿u muá»‘n bá» qua.",
        parse_mode="Markdown"
    )
    
    return AWAITING_PHONE


async def receive_free_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive phone number"""
    phone = update.message.text.strip()
    
    # Allow skip
    if phone.lower() == '/skip':
        context.user_data['registration_phone'] = None
        phone_display = "Bá» qua"
    else:
        # Basic phone validation
        phone = re.sub(r'[^0-9+]', '', phone)
        if len(phone) < 10:
            await update.message.reply_text(
                "âŒ Sá»‘ Ä‘iá»‡n thoáº¡i khÃ´ng há»£p lá»‡.\n\n"
                "Vui lÃ²ng nháº­p láº¡i (VD: 0901234567)\n"
                "Hoáº·c gÃµ /skip Ä‘á»ƒ bá» qua:"
            )
            return AWAITING_PHONE
        
        context.user_data['registration_phone'] = phone
        phone_display = phone
    
    await update.message.reply_text(
        f"âœ… Sá»‘ Ä‘iá»‡n thoáº¡i: {phone_display}\n\n"
        f"ðŸ‘¤ **BÆ°á»›c 3/3**: Nháº­p há» tÃªn cá»§a báº¡n\n"
        f"(Äá»ƒ cÃ¡ nhÃ¢n hÃ³a hÆ°á»›ng dáº«n)\n\n"
        f"Hoáº·c gÃµ /skip Ä‘á»ƒ bá» qua.",
        parse_mode="Markdown"
    )
    
    return AWAITING_NAME


async def receive_free_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive full name and save to database + Google Sheet"""
    name = update.message.text.strip()
    user = update.effective_user
    
    # Allow skip
    if name.lower() == '/skip':
        full_name = user.first_name
    else:
        full_name = name
    
    context.user_data['registration_name'] = full_name
    
    # Get collected data
    email = context.user_data.get('registration_email')
    phone = context.user_data.get('registration_phone')
    
    # Save to database
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if db_user:
            db_user.email = email
            db_user.phone = phone
            db_user.full_name = full_name
            db_user.is_registered = True
            db_user.registration_date = datetime.now()
            db_user.source = 'BOT_FREE_FLOW'
            db.commit()
            
            # Generate referral code
            referral_code = generate_referral_code(user.id)
            bot_username = (await context.bot.get_me()).username
            referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
            
            # Save to Google Sheet
            try:
                await save_user_to_registration_sheet(
                    user_id=user.id,
                    username=user.username,
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    plan="FREE",
                    referral_link=referral_link,
                    referral_count=db_user.referral_count or 0,
                    source="BOT_FREE_FLOW",
                    status="ACTIVE",
                    referred_by=None
                )
                logger.info(f"âœ… Saved user {user.id} to Google Sheet")
            except Exception as e:
                logger.error(f"âŒ Failed to save to Google Sheet: {e}")
            
            await update.message.reply_text(
                f"âœ… Cáº£m Æ¡n {full_name}!\n\n"
                f"ThÃ´ng tin Ä‘Ã£ Ä‘Æ°á»£c lÆ°u láº¡i.\n"
                f"BÃ¢y giá», hÃ£y cÃ¹ng táº¡o há»‡ thá»‘ng cá»§a riÃªng báº¡n.",
                parse_mode="Markdown"
            )
            
            # Wait a moment then go to step 2
            import asyncio
            await asyncio.sleep(1)
            
            # Proceed to step 2
            from app.handlers.user.free_flow import free_step2_show_value
            
            # Create a fake callback query for step 2
            from telegram import CallbackQuery
            fake_query = type('obj', (object,), {
                'answer': lambda: None,
                'edit_message_text': update.message.reply_text,
                'message': update.message,
                'from_user': user
            })()
            
            # Call step 2 directly
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
                [InlineKeyboardButton("Há»i thÃªm", callback_data="learn_more")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                text=message,
                reply_markup=reply_markup
            )
            
            return ConversationHandler.END
            
    except Exception as e:
        logger.error(f"Error saving user info: {e}", exc_info=True)
        await update.message.reply_text(
            "ðŸ˜“ Xin lá»—i, cÃ³ lá»—i xáº£y ra khi lÆ°u thÃ´ng tin.\n"
            "Vui lÃ²ng thá»­ láº¡i sau hoáº·c liÃªn há»‡ /support"
        )
        return ConversationHandler.END
    finally:
        db.close()


async def cancel_free_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel registration"""
    await update.message.reply_text(
        "ÄÃ£ há»§y Ä‘Äƒng kÃ½.\n"
        "Báº¡n cÃ³ thá»ƒ báº¯t Ä‘áº§u láº¡i báº¥t cá»© lÃºc nÃ o báº±ng /start"
    )
    return ConversationHandler.END

