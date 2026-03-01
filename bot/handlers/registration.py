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
from bot.utils.database import get_user_by_id, SessionLocal, User, Referral
from datetime import datetime
from loguru import logger

# Week 2: Import state machine (soft-integration)
from bot.core.state_machine import StateManager, UserState

# States for ConversationHandler
AWAITING_EMAIL, AWAITING_PHONE, AWAITING_NAME, CONFIRM = range(4)


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start registration process"""
    user = update.effective_user
    logger.info(f"🎯 start_registration called for user {user.id} ({user.username})")
    
    # Handle both callback query (from button) and command (from /register)
    is_callback = bool(update.callback_query)
    logger.info(f"  → is_callback: {is_callback}")
    
    # Check if already registered
    db_user = await get_user_by_id(user.id)
    if db_user and hasattr(db_user, 'email') and db_user.email:
        message_text = (
            "✅ Bạn đã đăng ký rồi!\n\n"
            "Dùng /help để xem các tính năng."
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
        "📝 **ĐĂNG KÝ SỞ HỮU FREEDOM WALLET**\n\n"
        "Để nhận Template Google Sheet và hướng dẫn setup,\n"
        "vui lòng điền thông tin sau:\n\n"
        "👉 **Bước 1/3:** Nhập **Email** của bạn\n"
        "(Chúng tôi sẽ gửi link Template qua email này)"
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
    logger.info(f"  → Returning AWAITING_EMAIL state (value: {AWAITING_EMAIL})")
    return AWAITING_EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate email"""
    logger.info(f"🔍 receive_email called for user {update.effective_user.id}")
    # Maintain conversation state
    context.user_data['conversation_state'] = 'registration'
    email = update.message.text.strip()
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await update.message.reply_text(
            "❌ Email không hợp lệ!\n\n"
            "Vui lòng nhập lại email (ví dụ: name@gmail.com):"
        )
        return AWAITING_EMAIL
    
    # Save to context
    context.user_data['email'] = email
    logger.info(f"✅ Email saved: {email}")
    
    # Request phone
    keyboard = [["/skip"]]
    await update.message.reply_text(
        f"✅ Email: **{email}**\n\n"
        f"👉 **Bước 2/3:** Nhập **Số điện thoại** của bạn\n"
        f"(Để hỗ trợ qua Zalo/WhatsApp nếu cần)\n\n"
        f"Hoặc gõ /skip để bỏ qua.",
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
                "❌ Số điện thoại không hợp lệ!\n\n"
                "Vui lòng nhập lại (VD: 0901234567 hoặc +84901234567)\n"
                "Hoặc gõ /skip để bỏ qua:"
            )
            return AWAITING_PHONE
        
        context.user_data['phone'] = phone
    
    # Request full name
    keyboard = [["/skip"]]
    await update.message.reply_text(
        f"✅ SĐT: **{context.user_data.get('phone', 'Bỏ qua')}**\n\n"
        f"👉 **Bước 3/3:** Nhập **Họ tên** của bạn\n"
        f"(Để cá nhân hóa hướng dẫn)\n\n"
        f"Hoặc gõ /skip để bỏ qua.",
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
    
    # Show confirmation — use .get() with defaults in case context was lost
    email = context.user_data.get('email')
    if not email:
        # Conversation was interrupted, restart
        await update.message.reply_text(
            "⚠️ Thông tin bị lỗi. Vui lòng bắt đầu lại từ /register",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    phone = context.user_data.get('phone', 'Không cung cấp')
    full_name = context.user_data.get('full_name', update.effective_user.first_name or 'Người dùng')
    
    # Use InlineKeyboardButton instead of ReplyKeyboardMarkup
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("✅ Xác nhận", callback_data="confirm_registration_yes")],
        [InlineKeyboardButton("✏️ Nhập lại email", callback_data="confirm_registration_retry")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📋 **XÁC NHẬN THÔNG TIN**\n\n"
        f"👤 Họ tên: **{full_name}**\n"
        f"📧 Email: **{email}**\n"
        f"📱 SĐT: **{phone}**\n\n"
        f"Thông tin có chính xác không?",
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
            "👉 Nhập lại **Email** của bạn:",
            parse_mode="Markdown"
        )
        return AWAITING_EMAIL
    
    if callback_data != "confirm_registration_yes":
        await query.message.reply_text(
            "❌ Vui lòng chọn '✅ Xác nhận' hoặc '✏️ Nhập lại email'",
            parse_mode="Markdown"
        )
        return CONFIRM
    
    user = update.effective_user
    # Defensive checks — use .get() with defaults in case context was lost
    email = context.user_data.get('email')
    phone = context.user_data.get('phone')
    full_name = context.user_data.get('full_name')
    
    # If any required field is missing, restart the registration
    if not email or not full_name:
        await query.answer()
        await query.message.reply_text(
            "⚠️ Thông tin bị lỗi. Vui lòng bắt đầu lại từ /register",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
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
                from bot.core.fraud_detector import check_referral_fraud, generate_device_fingerprint
                
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
                    f"🛡️ Fraud check: referral_id={referral.id}, "
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
                            from bot.handlers.vip import check_vip_milestone
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
                                    logger.info(f"🌟 User {referrer.id} promoted to SUPER VIP! ({referrer.referral_count} refs)")
                                    # Send Super VIP notification
                                    try:
                                        await send_super_vip_notification(referrer.id, referrer.referral_count, full_name, context)
                                    except Exception as e:
                                        logger.error(f"Failed to send Super VIP notification: {e}")
                        
                        # Auto-unlock FREE if >= 2  
                        if referrer.referral_count >= 2:
                            # Already FREE tier by default, just transition to VIP state
                            # Week 2: Transition referrer to VIP state
                            with StateManager() as state_mgr:
                                success, msg = state_mgr.transition_user(
                                    referrer.id, 
                                    UserState.VIP, 
                                    f"Unlocked by 2nd referral: {full_name}"
                                )
                                logger.info(f"🎯 Referrer {referrer.id} → VIP: {msg}")
                            
                            # UNLOCK FLOW v3.0 (Feb 2026) - Ownership-first, Identity-driven
                            try:
                                # Cancel remaining daily nurture messages
                                from bot.handlers.daily_nurture import cancel_remaining_nurture
                                await cancel_remaining_nurture(referrer.id, 0, context)
                                
                                # Send optimized unlock flow Message 1
                                from bot.handlers.unlock_flow_v3 import send_unlock_message_1
                                await send_unlock_message_1(referrer.id, context)
                                
                                logger.info(f"✅ Sent unlock flow v3.0 Message 1 to user {referrer.id}")
                                
                            except Exception as e:
                                logger.error(f"Failed to send unlock flow to {referrer.id}: {e}")
                        else:
                            # GIAI ĐOẠN 3: CẬP NHẬT KHI CÓ NGƯỜI ĐĂNG KÝ (1/2)
                            remaining = 2 - referrer.referral_count
                            try:
                                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                                
                                keyboard = [
                                    [InlineKeyboardButton("🔗 Chia sẻ tiếp", callback_data="share_link")],
                                    [InlineKeyboardButton("📊 Xem tiến độ", callback_data="check_progress")]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                
                                await context.bot.send_message(
                                    chat_id=referrer.id,
                                    text=f"✅ **Chúc mừng!**\n\n"
                                         f"**{full_name}** vừa đăng ký thành công qua link của bạn\n\n"
                                         f"📊 **Tiến độ hiện tại:** {referrer.referral_count} / 2 người\n\n"
                                         f"👉 **Chỉ còn {remaining} người nữa** để mở khóa toàn bộ quà 🎁\n\n"
                                         f"━━━━━━━━━━━━━━━━━━━━━\n"
                                         f"🎁 **Bạn sẽ nhận được:**\n"
                                         f"✅ Full Google Sheet 3.2\n"
                                         f"✅ Full Apps Script\n"
                                         f"✅ Full Hướng dẫn Notion\n"
                                         f"✅ Video tutorials\n"
                                         f"✅ Sử dụng trọn đời",
                                    parse_mode="Markdown",
                                    reply_markup=reply_markup
                                )
                            except Exception as e:
                                logger.error(f"Failed to notify referrer progress {referrer.id}: {e}")
                
                elif review_status == "PENDING_REVIEW":
                    # Medium risk - Flag for manual review, but keep referral pending
                    referral.status = "PENDING"  # Keep as pending until admin reviews
                    logger.warning(
                        f"⚠️ Referral {referral.id} flagged for review: "
                        f"score={fraud_score}, flags={fraud_flags}"
                    )
                    
                    # Notify referred user (transparent communication)
                    await update.message.reply_text(
                        "✅ Đăng ký thành công!\n\n"
                        "⏳ Lượt giới thiệu của bạn đang được xác minh.\n"
                        "Chúng tôi sẽ thông báo kết quả trong 24-48 giờ.\n\n"
                        "💡 Điều này giúp bảo vệ cộng đồng khỏi spam và lạm dụng.",
                        parse_mode="Markdown"
                    )
                    
                    # Notify admin about suspicious referral
                    await notify_admin_fraud_review(referral.id, fraud_score, fraud_flags, context)
                
                elif review_status == "HIGH_RISK":
                    # High risk - Requires immediate admin review
                    referral.status = "PENDING"
                    logger.error(
                        f"🚨 HIGH RISK referral {referral.id}: "
                        f"score={fraud_score}, flags={fraud_flags}"
                    )
                    
                    # Notify referred user
                    await update.message.reply_text(
                        "✅ Đăng ký hoàn tất!\n\n"
                        "⚠️ Lượt giới thiệu của bạn cần được xác minh thủ công.\n"
                        "Team chúng tôi sẽ kiểm tra và thông báo kết quả sớm nhất.\n\n"
                        "❓ Nếu bạn nghĩ đây là nhầm lẫn, vui lòng liên hệ /support",
                        parse_mode="Markdown"
                    )
                    
                    # Urgent notification to admin
                    await notify_admin_fraud_review(referral.id, fraud_score, fraud_flags, context, urgent=True)
            
            session.commit()
        
        # Sync to Google Sheets
        from bot.utils.sheets import sync_user_to_sheet
        await sync_user_to_sheet(user.id, email, phone, full_name)
        
        # Also save to FreedomWallet_Registrations sheet
        try:
            from bot.utils.sheets_registration import save_user_to_registration_sheet
            from bot.utils.database import generate_referral_code
            
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
            logger.info(f"✅ Saved user {user.id} to FreedomWallet_Registrations sheet")
        except Exception as e:
            logger.error(f"Failed to save to registration sheet: {e}")
        
        # Generate referral link for sharing
        from bot.utils.database import generate_referral_code
        referral_code = generate_referral_code(user.id)
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
        
        # Success message - Calm, no FOMO
        await query.message.reply_text(
            "✅ **Cảm ơn bạn!**\n\n"
            "Thông tin đã được lưu lại.",
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
        
        message = """Khi bạn cài đặt và sử dụng Freedom Wallet,
bạn không chỉ dùng một ứng dụng.

Bạn đang tạo một hệ thống tài chính cá nhân
thuộc về riêng bạn.

Sau khi hoàn tất cài đặt, bạn sẽ có:

• Một Google Sheet nằm trên Drive của bạn  
• Một Web App riêng, chạy từ chính dữ liệu của bạn  
• Hệ thống 6 Hũ tiền phân bổ tự động  
• Báo cáo thu – chi theo tháng  
• Theo dõi tài sản, đầu tư, nợ và dòng tiền  
• Cấp độ tài chính hiện tại của bạn

Bạn sẵn sàng tạo hệ thống của riêng mình chưa?"""
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("📋 Tạo Google Sheet", callback_data="free_step3_copy_template")],
            [InlineKeyboardButton("❓ Hỏi thêm", callback_data="learn_more")]
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
            f"❌ Lỗi khi lưu thông tin: {str(e)}\n\n"
            f"Vui lòng thử lại sau hoặc dùng /support"
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
                    caption=f"🌟 **CHÚC MỪNG THÀNH TỰU ĐẶC BIỆT!** 🌟\n\n"
                            f"**{new_ref_name}** vừa hoàn tất đăng ký!\n\n"
                            f"Bạn đã đạt **{ref_count} LƯỢT GIỚI THIỆU THÀNH CÔNG!**",
                    parse_mode="Markdown"
                )
        else:
            # Fallback if no image
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🌟 **CHÚC MỪNG THÀNH TỰU ĐẶC BIỆT!** 🌟\n\n"
                     f"**{new_ref_name}** vừa hoàn tất đăng ký!\n\n"
                     f"Bạn đã đạt **{ref_count} LƯỢT GIỚI THIỆU THÀNH CÔNG!**",
                parse_mode="Markdown"
            )
        
        await asyncio.sleep(1)
        
        # Send Super VIP announcement
        await context.bot.send_message(
            chat_id=user_id,
            text="━━━━━━━━━━━━━━━━━━━━━\n"
                 "👑✨ **BẠN CHÍNH THỨC TRỞ THÀNH**\n"
                 "**SUPER VIP – FREEDOM WALLET**\n"
                 "━━━━━━━━━━━━━━━━━━━━━\n\n"
                 "🎉 Danh hiệu cao quý nhất dành cho\n"
                 "những người đồng hành xuất sắc!\n\n"
                 "🏆 **50+ LƯỢT GIỚI THIỆU THÀNH CÔNG**",
            parse_mode="Markdown"
        )
        
        await asyncio.sleep(1)
        
        # Send exclusive Super VIP benefits menu
        keyboard = [
            [InlineKeyboardButton("🌟 Xem đặc quyền Super VIP", callback_data="super_vip_benefits")],
            [InlineKeyboardButton("🏆 Bảng xếp hạng Top Referrers", callback_data="leaderboard")],
            [InlineKeyboardButton("💬 Group Super VIP Private", url="https://t.me/freedomwallet_supervip")],
            [InlineKeyboardButton("🎁 Nhận quà đặc biệt", callback_data="super_vip_gifts")],
            [InlineKeyboardButton("🏠 Dashboard", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text="━━━━━━━━━━━━━━━━━━━━━\n"
                 "💎 **ĐẶC QUYỀN SUPER VIP:**\n"
                 "━━━━━━━━━━━━━━━━━━━━━\n\n"
                 "✨ **Tất cả quyền lợi VIP PLUS:**\n\n"
                 "🎯 Hỗ trợ ưu tiên cấp cao 24/7\n"
                 "🎁 Quà tặng độc quyền hàng tháng\n"
                 "🏆 Hiển thị trên Bảng xếp hạng\n"
                 "💬 Group Super VIP riêng biệt\n"
                 "🎓 Workshop & Training độc quyền\n"
                 "💰 Commission cao hơn (coming soon)\n"
                 "🌟 Badge đặc biệt trên profile\n\n"
                 "━━━━━━━━━━━━━━━━━━━━━\n"
                 "⚡ **LƯU Ý:** Để giữ danh hiệu Super VIP,\n"
                 "bạn cần duy trì hoạt động thường xuyên.\n"
                 "Bot sẽ nhắc nhở nếu bạn không hoạt động trong 7 ngày.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"✅ Sent Super VIP notification to user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send Super VIP notification to {user_id}: {e}")
        raise


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel registration"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Đã hủy đăng ký.\n\n"
        "Dùng /register bất cứ lúc nào để đăng ký!",
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
    from bot.utils.database import SessionLocal, Referral, User
    
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
        emoji = "🚨" if urgent else "⚠️"
        risk_level = "HIGH RISK" if urgent else "PENDING REVIEW"
        
        message = (
            f"{emoji} **FRAUD ALERT - {risk_level}**\n\n"
            f"**Referral ID:** {referral_id}\n"
            f"**Fraud Score:** {fraud_score}/100\n"
            f"**Flags:** {', '.join(fraud_flags) if fraud_flags else 'None'}\n\n"
            f"**Referrer:** {referrer_name} (ID: {referral.referrer_id})\n"
            f"**Referred:** {referred_name} (ID: {referral.referred_id})\n\n"
            f"**Review Actions:**\n"
            f"• /fraud_review {referral_id} - View details\n"
            f"• /fraud_approve {referral_id} - Approve\n"
            f"• /fraud_reject {referral_id} - Reject\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        
        await context.bot.send_message(
            chat_id=admin_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info(f"✅ Sent fraud notification to admin {admin_id} for referral {referral_id}")
        
    except Exception as e:
        logger.error(f"Failed to notify admin about fraud: {e}")

