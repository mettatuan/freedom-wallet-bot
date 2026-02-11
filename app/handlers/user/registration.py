"""
Registration Handler - Collect user information
User must complete registration to verify referral
Week 2: Soft-integrated with State Machine
Week 5: Integrated with Fraud Detection
"""
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
import re
from typing import List
from app.utils.database import get_user_by_id, SessionLocal, User, Referral
from datetime import datetime
from loguru import logger

# Week 2: Import state machine (soft-integration)
from app.core.state_machine import StateManager, UserState

# States for ConversationHandler
AWAITING_EMAIL, AWAITING_PHONE, AWAITING_NAME, CONFIRM = range(4)


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start registration process"""
    user = update.effective_user
    logger.info(f"ðŸŽ¯ start_registration called for user {user.id} ({user.username})")
    
    # Handle both callback query (from button) and command (from /register)
    is_callback = bool(update.callback_query)
    logger.info(f"  â†’ is_callback: {is_callback}")
    
    # Check if already registered
    db_user = await get_user_by_id(user.id)
    if db_user and hasattr(db_user, 'email') and db_user.email:
        message_text = (
            "âœ… Báº¡n Ä‘Ã£ Ä‘Äƒng kÃ½ rá»“i!\n\n"
            "DÃ¹ng /help Ä‘á»ƒ xem cÃ¡c tÃ­nh nÄƒng."
        )
        
        if is_callback:
            await update.callback_query.answer()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_text,
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                message_text,
                reply_markup=ReplyKeyboardRemove()
            )
        return ConversationHandler.END
    
    registration_text = (
        "ðŸ“ **ÄÄ‚NG KÃ Sá»ž Há»®U FREEDOM WALLET**\n\n"
        "Äá»ƒ nháº­n Template Google Sheet vÃ  hÆ°á»›ng dáº«n setup,\n"
        "vui lÃ²ng Ä‘iá»n thÃ´ng tin sau:\n\n"
        "ðŸ‘‰ **BÆ°á»›c 1/3:** Nháº­p **Email** cá»§a báº¡n\n"
        "(ChÃºng tÃ´i sáº½ gá»­i link Template qua email nÃ y)"
    )
    
    if is_callback:
        await update.callback_query.answer()
        # Don't delete - just edit or send new message
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=registration_text,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            registration_text,
            parse_mode="Markdown"
        )
    
    # Set conversation state flag to prevent AI chat handler interference
    context.user_data['conversation_state'] = 'registration'
    logger.info(f"  â†’ Returning AWAITING_EMAIL state (value: {AWAITING_EMAIL})")
    return AWAITING_EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate email"""
    logger.info(f"ðŸ” receive_email called for user {update.effective_user.id}")
    # Maintain conversation state
    context.user_data['conversation_state'] = 'registration'
    email = update.message.text.strip()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await update.message.reply_text(
            "âŒ Email khÃ´ng há»£p lá»‡!\n\n"
            "Vui lÃ²ng nháº­p láº¡i email (vÃ­ dá»¥: name@gmail.com):"
        )
        return AWAITING_EMAIL
    
    # Save to context
    context.user_data['email'] = email
    logger.info(f"âœ… Email saved: {email}")
    
    # Request phone
    keyboard = [["/skip"]]
    await update.message.reply_text(
        f"âœ… Email: **{email}**\n\n"
        f"ðŸ‘‰ **BÆ°á»›c 2/3:** Nháº­p **Sá»‘ Ä‘iá»‡n thoáº¡i** cá»§a báº¡n\n"
        f"(Äá»ƒ há»— trá»£ qua Zalo/WhatsApp náº¿u cáº§n)\n\n"
        f"Hoáº·c gÃµ /skip Ä‘á»ƒ bá» qua.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    
    return AWAITING_PHONE


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive phone number"""
    # Maintain conversation state
    context.user_data['conversation_state'] = 'registration'
    phone = update.message.text.strip()
    
    # Allow skip
    if phone.lower() == '/skip':
        context.user_data['phone'] = None
    else:
        # Basic phone validation (Vietnamese format)
        phone = re.sub(r'[^0-9+]', '', phone)  # Remove non-digits except +
        if len(phone) < 10:
            await update.message.reply_text(
                "âŒ Sá»‘ Ä‘iá»‡n thoáº¡i khÃ´ng há»£p lá»‡!\n\n"
                "Vui lÃ²ng nháº­p láº¡i (VD: 0901234567 hoáº·c +84901234567)\n"
                "Hoáº·c gÃµ /skip Ä‘á»ƒ bá» qua:"
            )
            return AWAITING_PHONE
        
        context.user_data['phone'] = phone
    
    # Request full name
    keyboard = [["/skip"]]
    await update.message.reply_text(
        f"âœ… SÄT: **{context.user_data.get('phone', 'Bá» qua')}**\n\n"
        f"ðŸ‘‰ **BÆ°á»›c 3/3:** Nháº­p **Há» tÃªn** cá»§a báº¡n\n"
        f"(Äá»ƒ cÃ¡ nhÃ¢n hÃ³a hÆ°á»›ng dáº«n)\n\n"
        f"Hoáº·c gÃµ /skip Ä‘á»ƒ bá» qua.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    
    return AWAITING_NAME


async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive full name and confirm"""
    # Maintain conversation state
    context.user_data['conversation_state'] = 'registration'
    name = update.message.text.strip()
    
    # Allow skip
    if name.lower() == '/skip':
        context.user_data['full_name'] = update.effective_user.first_name
    else:
        context.user_data['full_name'] = name
    
    # Show confirmation
    email = context.user_data['email']
    phone = context.user_data.get('phone', 'KhÃ´ng cung cáº¥p')
    full_name = context.user_data['full_name']
    
    # Use InlineKeyboardButton instead of ReplyKeyboardMarkup
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("âœ… XÃ¡c nháº­n", callback_data="confirm_registration_yes")],
        [InlineKeyboardButton("âœï¸ Nháº­p láº¡i email", callback_data="confirm_registration_retry")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "ðŸ“‹ **XÃC NHáº¬N THÃ”NG TIN**\n\n"
        f"ðŸ‘¤ Há» tÃªn: **{full_name}**\n"
        f"ðŸ“§ Email: **{email}**\n"
        f"ðŸ“± SÄT: **{phone}**\n\n"
        f"ThÃ´ng tin cÃ³ chÃ­nh xÃ¡c khÃ´ng?",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    return CONFIRM


async def confirm_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and save registration"""
    # Handle CallbackQuery instead of text message
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == "confirm_registration_retry":
        await query.message.edit_text(
            "ðŸ‘‰ Nháº­p láº¡i **Email** cá»§a báº¡n:",
            parse_mode="Markdown"
        )
        return AWAITING_EMAIL
    
    if callback_data != "confirm_registration_yes":
        await query.message.reply_text(
            "âŒ Vui lÃ²ng chá»n 'âœ… XÃ¡c nháº­n' hoáº·c 'âœï¸ Nháº­p láº¡i email'",
            parse_mode="Markdown"
        )
        return CONFIRM
    
    user = update.effective_user
    email = context.user_data['email']
    phone = context.user_data.get('phone')
    full_name = context.user_data['full_name']
    
    # Save to database
    session = SessionLocal()
    try:
        db_user = session.query(User).filter(User.id == user.id).first()
        if db_user:
            db_user.email = email
            db_user.phone = phone
            db_user.full_name = full_name
            db_user.is_registered = True
            
            # Week 2: Transition user to REGISTERED state
            with StateManager() as state_mgr:
                current_state, is_legacy = state_mgr.get_user_state(user.id)
                if is_legacy or current_state == UserState.VISITOR:
                    state_mgr.transition_user(user.id, UserState.REGISTERED, "Completed registration")
            
            # Verify referral if exists
            referral = session.query(Referral).filter(
                Referral.referred_id == user.id,
                Referral.status == "PENDING"
            ).first()
            
            if referral:
                # Week 5: FRAUD DETECTION BEFORE VERIFICATION
                from app.core.fraud_detector import check_referral_fraud, generate_device_fingerprint
                
                # Get user-agent from Telegram update (if available)
                user_agent = None
                try:
                    # Try to get user-agent from update context
                    # Note: Telegram API doesn't expose real user-agent, 
                    # so we use a synthetic one based on user info
                    user_agent = f"Telegram/{user.id}/{user.username or 'unknown'}"
                except:
                    user_agent = "Telegram/Unknown"
                
                # IP address not available in Telegram bot
                ip_address = None
                
                # Run fraud check
                fraud_score, fraud_flags, review_status = check_referral_fraud(
                    referrer_id=referral.referrer_id,
                    referred_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                # Update referral with fraud info
                referral.velocity_score = fraud_score
                referral.review_status = review_status
                referral.user_agent = user_agent
                referral.ip_address = ip_address
                
                if user_agent:
                    referral.device_fingerprint = generate_device_fingerprint(user_agent, user.id)
                
                logger.info(
                    f"ðŸ›¡ï¸ Fraud check: referral_id={referral.id}, "
                    f"score={fraud_score}, status={review_status}, flags={fraud_flags}"
                )
                
                # Handle based on fraud score
                if review_status == "AUTO_APPROVED":
                    # Low risk - Auto approve
                    referral.status = "VERIFIED"
                    referral.verified_at = datetime.utcnow()
                    
                    # Update referrer count (ONLY if auto-approved)
                    referrer = session.query(User).filter(User.id == referral.referrer_id).first()
                    if referrer:
                        referrer.referral_count += 1
                        
                        # Check VIP milestones (10/50/100 refs) - Identity Layer
                        try:
                            from app.handlers.vip import check_vip_milestone
                            await check_vip_milestone(referrer.id, context)
                        except Exception as e:
                            logger.error(f"Failed to check VIP milestone for {referrer.id}: {e}")
                        
                        # Week 4: Update Super VIP activity (getting referral is activity)
                        with StateManager() as state_mgr:
                            state_mgr.update_super_vip_activity(referrer.id)
                    
                    # Week 4: Check for Super VIP promotion (50+ refs)
                        if referrer.referral_count >= 50:
                            with StateManager() as state_mgr:
                                new_state = state_mgr.check_and_update_state_by_referrals(referrer.id)
                                if new_state == UserState.SUPER_VIP:
                                    logger.info(f"ðŸŒŸ User {referrer.id} promoted to SUPER VIP! ({referrer.referral_count} refs)")
                                    # Send Super VIP notification
                                    try:
                                        await send_super_vip_notification(referrer.id, referrer.referral_count, full_name, context)
                                    except Exception as e:
                                        logger.error(f"Failed to send Super VIP notification: {e}")
                        
                        # Auto-unlock FREE if >= 2
                        if referrer.referral_count >= 2 and not referrer.is_free_unlocked:
                            referrer.is_free_unlocked = True
                            referrer.subscription_tier = "FREE"
                            
                            # Week 2: Transition referrer to VIP state
                            with StateManager() as state_mgr:
                                success, msg = state_mgr.transition_user(
                                    referrer.id, 
                                    UserState.VIP, 
                                    f"Unlocked by 2nd referral: {full_name}"
                                )
                                logger.info(f"ðŸŽ¯ Referrer {referrer.id} â†’ VIP: {msg}")
                            
                            # UNLOCK FLOW v3.0 (Feb 2026) - Ownership-first, Identity-driven
                            try:
                                # Cancel remaining daily nurture messages
                                from app.handlers.daily_nurture import cancel_remaining_nurture
                                await cancel_remaining_nurture(referrer.id, 0, context)
                                
                                # Send optimized unlock flow Message 1
                                from app.handlers.unlock_flow_v3 import send_unlock_message_1
                                await send_unlock_message_1(referrer.id, context)
                                
                                logger.info(f"âœ… Sent unlock flow v3.0 Message 1 to user {referrer.id}")
                                
                            except Exception as e:
                                logger.error(f"Failed to send unlock flow to {referrer.id}: {e}")
                        else:
                            # GIAI ÄOáº N 3: Cáº¬P NHáº¬T KHI CÃ“ NGÆ¯á»œI ÄÄ‚NG KÃ (1/2)
                            remaining = 2 - referrer.referral_count
                            try:
                                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                                
                                keyboard = [
                                    [InlineKeyboardButton("ðŸ”— Chia sáº» tiáº¿p", callback_data="share_link")],
                                    [InlineKeyboardButton("ðŸ“Š Xem tiáº¿n Ä‘á»™", callback_data="check_progress")]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                
                                await context.bot.send_message(
                                    chat_id=referrer.id,
                                    text=f"âœ… **ChÃºc má»«ng!**\n\n"
                                         f"**{full_name}** vá»«a Ä‘Äƒng kÃ½ thÃ nh cÃ´ng qua link cá»§a báº¡n\n\n"
                                         f"ðŸ“Š **Tiáº¿n Ä‘á»™ hiá»‡n táº¡i:** {referrer.referral_count} / 2 ngÆ°á»i\n\n"
                                         f"ðŸ‘‰ **Chá»‰ cÃ²n {remaining} ngÆ°á»i ná»¯a** Ä‘á»ƒ má»Ÿ khÃ³a toÃ n bá»™ quÃ  ðŸŽ\n\n"
                                         f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
                                         f"ðŸŽ **Báº¡n sáº½ nháº­n Ä‘Æ°á»£c:**\n"
                                         f"âœ… Full Google Sheet 3.2\n"
                                         f"âœ… Full Apps Script\n"
                                         f"âœ… Full HÆ°á»›ng dáº«n Notion\n"
                                         f"âœ… Video tutorials\n"
                                         f"âœ… Sá»­ dá»¥ng trá»n Ä‘á»i",
                                    parse_mode="Markdown",
                                    reply_markup=reply_markup
                                )
                            except Exception as e:
                                logger.error(f"Failed to notify referrer progress {referrer.id}: {e}")
                
                elif review_status == "PENDING_REVIEW":
                    # Medium risk - Flag for manual review, but keep referral pending
                    referral.status = "PENDING"  # Keep as pending until admin reviews
                    logger.warning(
                        f"âš ï¸ Referral {referral.id} flagged for review: "
                        f"score={fraud_score}, flags={fraud_flags}"
                    )
                    
                    # Notify referred user (transparent communication)
                    await update.message.reply_text(
                        "âœ… ÄÄƒng kÃ½ thÃ nh cÃ´ng!\n\n"
                        "â³ LÆ°á»£t giá»›i thiá»‡u cá»§a báº¡n Ä‘ang Ä‘Æ°á»£c xÃ¡c minh.\n"
                        "ChÃºng tÃ´i sáº½ thÃ´ng bÃ¡o káº¿t quáº£ trong 24-48 giá».\n\n"
                        "ðŸ’¡ Äiá»u nÃ y giÃºp báº£o vá»‡ cá»™ng Ä‘á»“ng khá»i spam vÃ  láº¡m dá»¥ng.",
                        parse_mode="Markdown"
                    )
                    
                    # Notify admin about suspicious referral
                    await notify_admin_fraud_review(referral.id, fraud_score, fraud_flags, context)
                
                elif review_status == "HIGH_RISK":
                    # High risk - Requires immediate admin review
                    referral.status = "PENDING"
                    logger.error(
                        f"ðŸš¨ HIGH RISK referral {referral.id}: "
                        f"score={fraud_score}, flags={fraud_flags}"
                    )
                    
                    # Notify referred user
                    await update.message.reply_text(
                        "âœ… ÄÄƒng kÃ½ hoÃ n táº¥t!\n\n"
                        "âš ï¸ LÆ°á»£t giá»›i thiá»‡u cá»§a báº¡n cáº§n Ä‘Æ°á»£c xÃ¡c minh thá»§ cÃ´ng.\n"
                        "Team chÃºng tÃ´i sáº½ kiá»ƒm tra vÃ  thÃ´ng bÃ¡o káº¿t quáº£ sá»›m nháº¥t.\n\n"
                        "â“ Náº¿u báº¡n nghÄ© Ä‘Ã¢y lÃ  nháº§m láº«n, vui lÃ²ng liÃªn há»‡ /support",
                        parse_mode="Markdown"
                    )
                    
                    # Urgent notification to admin
                    await notify_admin_fraud_review(referral.id, fraud_score, fraud_flags, context, urgent=True)
            
            session.commit()
        
        # Sync to Google Sheets
        from app.utils.sheets import sync_user_to_sheet
        await sync_user_to_sheet(user.id, email, phone, full_name)
        
        # Also save to FreedomWallet_Registrations sheet
        try:
            from app.utils.sheets_registration import save_user_to_registration_sheet
            from app.utils.database import generate_referral_code
            
            referral_code = generate_referral_code(user.id)
            bot_username = (await context.bot.get_me()).username
            referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
            
            await save_user_to_registration_sheet(
                user_id=user.id,
                username=user.username or "",
                full_name=full_name,
                email=email,
                phone=phone or "",
                plan="FREE",
                referral_link=referral_link,
                referral_count=db_user.referral_count or 0,
                source="BOT_REGISTRATION",
                status="ACTIVE",
                referred_by=None
            )
            logger.info(f"âœ… Saved user {user.id} to FreedomWallet_Registrations sheet")
        except Exception as e:
            logger.error(f"Failed to save to registration sheet: {e}")
        
        # Generate referral link for sharing
        from app.utils.database import generate_referral_code
        referral_code = generate_referral_code(user.id)
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
        
        # Success message - Calm, no FOMO
        await query.message.reply_text(
            "âœ… **Cáº£m Æ¡n báº¡n!**\n\n"
            "ThÃ´ng tin Ä‘Ã£ Ä‘Æ°á»£c lÆ°u láº¡i.",
            parse_mode="Markdown"
        )
        
        # Clear context
        context.user_data.clear()
        
        # Wait a moment then show what they'll receive
        import asyncio
        await asyncio.sleep(1.5)
        
        # Show new message with hu_tien.jpg image
        import os
        image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'media', 'images', 'hu_tien.jpg')
        
        message = """Khi báº¡n cÃ i Ä‘áº·t vÃ  sá»­ dá»¥ng Freedom Wallet,
báº¡n khÃ´ng chá»‰ dÃ¹ng má»™t á»©ng dá»¥ng.

Báº¡n Ä‘ang táº¡o má»™t há»‡ thá»‘ng tÃ i chÃ­nh cÃ¡ nhÃ¢n
thuá»™c vá» riÃªng báº¡n.

Sau khi hoÃ n táº¥t cÃ i Ä‘áº·t, báº¡n sáº½ cÃ³:

â€¢ Má»™t Google Sheet náº±m trÃªn Drive cá»§a báº¡n  
â€¢ Má»™t Web App riÃªng, cháº¡y tá»« chÃ­nh dá»¯ liá»‡u cá»§a báº¡n  
â€¢ Há»‡ thá»‘ng 6 HÅ© tiá»n phÃ¢n bá»• tá»± Ä‘á»™ng  
â€¢ BÃ¡o cÃ¡o thu â€“ chi theo thÃ¡ng  
â€¢ Theo dÃµi tÃ i sáº£n, Ä‘áº§u tÆ°, ná»£ vÃ  dÃ²ng tiá»n  
â€¢ Cáº¥p Ä‘á»™ tÃ i chÃ­nh hiá»‡n táº¡i cá»§a báº¡n

Báº¡n sáºµn sÃ ng táº¡o há»‡ thá»‘ng cá»§a riÃªng mÃ¬nh chÆ°a?"""
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("ðŸ“‹ Táº¡o Google Sheet", callback_data="free_step3_copy_template")],
            [InlineKeyboardButton("â“ Há»i thÃªm", callback_data="learn_more")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            with open(image_path, 'rb') as photo:
                await query.message.reply_photo(
                    photo=photo,
                    caption=message,
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            # Fallback: send text only
            await query.message.reply_text(
                text=message,
                reply_markup=reply_markup
            )
        
        # Clear conversation state flag before ending
        context.user_data.pop('conversation_state', None)
        return ConversationHandler.END
        
    except Exception as e:
        session.rollback()
        await query.message.reply_text(
            f"âŒ Lá»—i khi lÆ°u thÃ´ng tin: {str(e)}\n\n"
            f"Vui lÃ²ng thá»­ láº¡i sau hoáº·c dÃ¹ng /support"
        )
        # Clear conversation state flag
        context.user_data.pop('conversation_state', None)
        return ConversationHandler.END
    finally:
        session.close()


async def send_super_vip_notification(user_id: int, ref_count: int, new_ref_name: str, context: ContextTypes.DEFAULT_TYPE):
    """
    Send Super VIP promotion notification (Week 4)
    
    Called when user reaches 50+ referrals
    """
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from pathlib import Path
    import asyncio
    
    try:
        # Send congratulation image if available
        image_path = Path("media/images/super_vip.png")
        if image_path.exists():
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=f"ðŸŒŸ **CHÃšC Má»ªNG THÃ€NH Tá»°U Äáº¶C BIá»†T!** ðŸŒŸ\n\n"
                            f"**{new_ref_name}** vá»«a hoÃ n táº¥t Ä‘Äƒng kÃ½!\n\n"
                            f"Báº¡n Ä‘Ã£ Ä‘áº¡t **{ref_count} LÆ¯á»¢T GIá»šI THIá»†U THÃ€NH CÃ”NG!**",
                    parse_mode="Markdown"
                )
        else:
            # Fallback if no image
            await context.bot.send_message(
                chat_id=user_id,
                text=f"ðŸŒŸ **CHÃšC Má»ªNG THÃ€NH Tá»°U Äáº¶C BIá»†T!** ðŸŒŸ\n\n"
                     f"**{new_ref_name}** vá»«a hoÃ n táº¥t Ä‘Äƒng kÃ½!\n\n"
                     f"Báº¡n Ä‘Ã£ Ä‘áº¡t **{ref_count} LÆ¯á»¢T GIá»šI THIá»†U THÃ€NH CÃ”NG!**",
                parse_mode="Markdown"
            )
        
        await asyncio.sleep(1)
        
        # Send Super VIP announcement
        await context.bot.send_message(
            chat_id=user_id,
            text="â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
                 "ðŸ‘‘âœ¨ **Báº N CHÃNH THá»¨C TRá»ž THÃ€NH**\n"
                 "**SUPER VIP â€“ FREEDOM WALLET**\n"
                 "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                 "ðŸŽ‰ Danh hiá»‡u cao quÃ½ nháº¥t dÃ nh cho\n"
                 "nhá»¯ng ngÆ°á»i Ä‘á»“ng hÃ nh xuáº¥t sáº¯c!\n\n"
                 "ðŸ† **50+ LÆ¯á»¢T GIá»šI THIá»†U THÃ€NH CÃ”NG**",
            parse_mode="Markdown"
        )
        
        await asyncio.sleep(1)
        
        # Send exclusive Super VIP benefits menu
        keyboard = [
            [InlineKeyboardButton("ðŸŒŸ Xem Ä‘áº·c quyá»n Super VIP", callback_data="super_vip_benefits")],
            [InlineKeyboardButton("ðŸ† Báº£ng xáº¿p háº¡ng Top Referrers", callback_data="leaderboard")],
            [InlineKeyboardButton("ðŸ’¬ Group Super VIP Private", url="https://t.me/freedomwallet_supervip")],
            [InlineKeyboardButton("ðŸŽ Nháº­n quÃ  Ä‘áº·c biá»‡t", callback_data="super_vip_gifts")],
            [InlineKeyboardButton("ðŸ  Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text="â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
                 "ðŸ’Ž **Äáº¶C QUYá»€N SUPER VIP:**\n"
                 "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n\n"
                 "âœ¨ **Táº¥t cáº£ quyá»n lá»£i VIP PLUS:**\n\n"
                 "ðŸŽ¯ Há»— trá»£ Æ°u tiÃªn cáº¥p cao 24/7\n"
                 "ðŸŽ QuÃ  táº·ng Ä‘á»™c quyá»n hÃ ng thÃ¡ng\n"
                 "ðŸ† Hiá»ƒn thá»‹ trÃªn Báº£ng xáº¿p háº¡ng\n"
                 "ðŸ’¬ Group Super VIP riÃªng biá»‡t\n"
                 "ðŸŽ“ Workshop & Training Ä‘á»™c quyá»n\n"
                 "ðŸ’° Commission cao hÆ¡n (coming soon)\n"
                 "ðŸŒŸ Badge Ä‘áº·c biá»‡t trÃªn profile\n\n"
                 "â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
                 "âš¡ **LÆ¯U Ã:** Äá»ƒ giá»¯ danh hiá»‡u Super VIP,\n"
                 "báº¡n cáº§n duy trÃ¬ hoáº¡t Ä‘á»™ng thÆ°á»ng xuyÃªn.\n"
                 "Bot sáº½ nháº¯c nhá»Ÿ náº¿u báº¡n khÃ´ng hoáº¡t Ä‘á»™ng trong 7 ngÃ y.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"âœ… Sent Super VIP notification to user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send Super VIP notification to {user_id}: {e}")
        raise


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel registration"""
    context.user_data.clear()
    await update.message.reply_text(
        "âŒ ÄÃ£ há»§y Ä‘Äƒng kÃ½.\n\n"
        "DÃ¹ng /register báº¥t cá»© lÃºc nÃ o Ä‘á»ƒ Ä‘Äƒng kÃ½!",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def notify_admin_fraud_review(
    referral_id: int, 
    fraud_score: int, 
    fraud_flags: List[str], 
    context: ContextTypes.DEFAULT_TYPE,
    urgent: bool = False
) -> None:
    """
    Notify admin about suspicious referral (Week 5 - Fraud Detection)
    
    Args:
        referral_id: ID of flagged referral
        fraud_score: Fraud score (0-100)
        fraud_flags: List of fraud flags
        context: Telegram context
        urgent: If True, mark as HIGH_RISK
    """
    from config.settings import settings
    from app.utils.database import SessionLocal, Referral, User
    
    # Get admin user ID from settings (add this to your settings)
    admin_id = settings.ADMIN_USER_ID if hasattr(settings, 'ADMIN_USER_ID') else None
    
    if not admin_id:
        logger.warning("ADMIN_USER_ID not configured, cannot send fraud notifications")
        return
    
    try:
        session = SessionLocal()
        
        # Get referral details
        referral = session.query(Referral).filter(Referral.id == referral_id).first()
        if not referral:
            session.close()
            return
        
        # Get user details
        referrer = session.query(User).filter(User.id == referral.referrer_id).first()
        referred = session.query(User).filter(User.id == referral.referred_id).first()
        
        referrer_name = referrer.username or referrer.full_name if referrer else 'Unknown'
        referred_name = referred.username or referred.full_name if referred else 'Unknown'
        
        session.close()
        
        # Build notification message
        emoji = "ðŸš¨" if urgent else "âš ï¸"
        risk_level = "HIGH RISK" if urgent else "PENDING REVIEW"
        
        message = (
            f"{emoji} **FRAUD ALERT - {risk_level}**\n\n"
            f"**Referral ID:** {referral_id}\n"
            f"**Fraud Score:** {fraud_score}/100\n"
            f"**Flags:** {', '.join(fraud_flags) if fraud_flags else 'None'}\n\n"
            f"**Referrer:** {referrer_name} (ID: {referral.referrer_id})\n"
            f"**Referred:** {referred_name} (ID: {referral.referred_id})\n\n"
            f"**Review Actions:**\n"
            f"â€¢ /fraud_review {referral_id} - View details\n"
            f"â€¢ /fraud_approve {referral_id} - Approve\n"
            f"â€¢ /fraud_reject {referral_id} - Reject\n\n"
            f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”"
        )
        
        await context.bot.send_message(
            chat_id=admin_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info(f"âœ… Sent fraud notification to admin {admin_id} for referral {referral_id}")
        
    except Exception as e:
        logger.error(f"Failed to notify admin about fraud: {e}")


