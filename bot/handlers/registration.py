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
    
    # Check if already registered
    db_user = await get_user_by_id(user.id)
    if db_user and hasattr(db_user, 'email') and db_user.email:
        await update.message.reply_text(
            "✅ Bạn đã đăng ký rồi!\n\n"
            "Dùng /help để xem các tính năng.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📝 **ĐĂNG KÝ TẢI FREEDOM WALLET MIỄN PHÍ**\n\n"
        "Để nhận Template Google Sheet và hướng dẫn setup,\n"
        "vui lòng điền thông tin sau:\n\n"
        "👉 **Bước 1/3:** Nhập **Email** của bạn\n"
        "(Chúng tôi sẽ gửi link Template qua email này)",
        parse_mode="Markdown"
    )
    
    return AWAITING_EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive and validate email"""
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
    name = update.message.text.strip()
    
    # Allow skip
    if name.lower() == '/skip':
        context.user_data['full_name'] = update.effective_user.first_name
    else:
        context.user_data['full_name'] = name
    
    # Show confirmation
    email = context.user_data['email']
    phone = context.user_data.get('phone', 'Không cung cấp')
    full_name = context.user_data['full_name']
    
    keyboard = [
        ["✅ Xác nhận"],
        ["✏️ Nhập lại email"]
    ]
    
    await update.message.reply_text(
        "📋 **XÁC NHẬN THÔNG TIN**\n\n"
        f"👤 Họ tên: **{full_name}**\n"
        f"📧 Email: **{email}**\n"
        f"📱 SĐT: **{phone}**\n\n"
        f"Thông tin có chính xác không?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    
    return CONFIRM


async def confirm_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and save registration"""
    response = update.message.text.strip()
    
    if response == "✏️ Nhập lại email":
        await update.message.reply_text(
            "👉 Nhập lại **Email** của bạn:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return AWAITING_EMAIL
    
    if response != "✅ Xác nhận":
        await update.message.reply_text(
            "❌ Vui lòng chọn '✅ Xác nhận' hoặc '✏️ Nhập lại email'",
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
                                logger.info(f"🎯 Referrer {referrer.id} → VIP: {msg}")
                            
                            # GIAI ĐOẠN 4: VINH DANH + KÍCH HOẠT VIP
                            try:
                                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                                from pathlib import Path
                                
                                # Cancel remaining daily nurture messages
                                from bot.handlers.daily_nurture import cancel_remaining_nurture
                                await cancel_remaining_nurture(referrer.id, 0, context)
                                
                                # Send congratulation image first
                                image_path = Path("media/images/chucmung.png")
                                if image_path.exists():
                                    with open(image_path, 'rb') as photo:
                                        await context.bot.send_photo(
                                            chat_id=referrer.id,
                                            photo=photo,
                                            caption=f"🎉 **CHÚC MỪNG!** 🎉\n\n"
                                                    f"**{full_name}** vừa hoàn tất đăng ký!\n\n"
                                                    f"Bạn đã **HOÀN THÀNH 2 / 2 LƯỢT GIỚI THIỆU**",
                                            parse_mode="Markdown"
                                        )
                                
                                import asyncio
                                await asyncio.sleep(1)
                                
                                # Send VIP congratulations with identity anchor
                                await context.bot.send_message(
                                    chat_id=referrer.id,
                                    text=f"━━━━━━━━━━━━━━━━━━━━━\n"
                                         f"👑 **CHÀO MỪNG BẠN TRỞ THÀNH**\n"
                                         f"**THÀNH VIÊN VIP – FREEDOM WALLET**\n"
                                         f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                                         f"Bạn đã chính thức bước sang\n"
                                         f"giai đoạn sử dụng sâu hơn và hiệu quả hơn.\n\n"
                                         f"💡 Thành viên VIP là những người:\n"
                                         f"• Đã chủ động hành động\n"
                                         f"• Muốn quản lý tài chính nghiêm túc\n"
                                         f"• Sẵn sàng đi sâu hơn thay vì chỉ xem",
                                    parse_mode="Markdown"
                                )
                                
                                await asyncio.sleep(2)
                                
                                # Message 3A: Benefits with single CTA
                                keyboard_3a = [
                                    [InlineKeyboardButton("➡️ Tiếp tục", callback_data="vip_continue")]
                                ]
                                reply_markup_3a = InlineKeyboardMarkup(keyboard_3a)
                                
                                await context.bot.send_message(
                                    chat_id=referrer.id,
                                    text="🎁 **QUYỀN LỢI DÀNH CHO BẠN:**\n\n"
                                         "✅ Công cụ quản lý tài chính đầy đủ\n"
                                         "✅ Web App cá nhân\n"
                                         "✅ Hướng dẫn từng bước\n"
                                         "✅ Group VIP hỗ trợ trực tiếp\n\n"
                                         "👉 Bước tiếp theo rất đơn giản.",
                                    parse_mode="Markdown",
                                    reply_markup=reply_markup_3a
                                )
                                
                                # Store flag to send Message 3B when user clicks "Tiếp tục"
                                # Message 3B will be sent via callback handler
                                
                                # Start onboarding journey with 10-minute delay (not immediate)
                                # This allows user to process VIP status first
                                from bot.handlers.onboarding import start_onboarding_journey
                                await start_onboarding_journey(referrer.id, context, initial_delay_minutes=10)
                                
                            except Exception as e:
                                logger.error(f"Failed to notify referrer {referrer.id}: {e}")
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
        
        # Generate referral link for sharing
        from bot.utils.database import generate_referral_code
        referral_code = generate_referral_code(user.id)
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
        
        # Success message with REFERRAL FIRST approach
        await update.message.reply_text(
            "🎉 **ĐĂNG KÝ THÀNH CÔNG!**\n\n"
            "✅ Bạn đã hoàn tất đăng ký!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 **NHẬN TEMPLATE + HƯỚNG DẪN**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "**Cho trước, nhận sau!**\n"
            "Giới thiệu **2 bạn bè** để mở khóa:\n\n"
            "✓ Google Sheets Template\n"
            "✓ Hướng dẫn tạo Web App chi tiết\n"
            "✓ Video tutorials 3 phút\n"
            "✓ Truy cập đầy đủ tính năng Bot\n"
            "✓ Cập nhật miễn phí mãi mãi\n\n"
            f"📊 **Tiến độ hiện tại:** 0/2 người\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 **LINK GIỚI THIỆU CỦA BẠN:**\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"`{referral_link}`\n\n"
            "👆 Copy link trên và chia sẻ qua:\n"
            "• Telegram\n"
            "• Facebook\n"
            "• Zalo\n"
            "• WhatsApp\n"
            "• TikTok\n"
            "• X (Twitter)\n\n"
            "💡 **Mẹo:** Khi bạn bè đăng ký xong,\n"
            "bot sẽ tự động thông báo cho bạn!\n\n"
            "🚀 Dùng /help để xem thêm lệnh",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Clear context
        context.user_data.clear()
        
        # Send 3 welcome messages according to new flow
        # MESSAGE 1: Chào mừng + Gợi mở giá trị
        await update.message.reply_text(
            "🎉 **Chúc mừng bạn đã đăng ký thành công Freedom Wallet!**\n\n"
            "Bạn vừa bước vào hành trình quản lý tài chính thông minh – "
            "hướng tới tự do tài chính 💙\n\n"
            "👉 Chỉ cần **giới thiệu 2 người hoàn thành đăng ký**, "
            "bạn sẽ nhận **BỘ QUÀ ĐẶC BIỆT TRỌN ĐỜI** 🎁",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        
        import asyncio
        await asyncio.sleep(2)
        
        # MESSAGE 2: Nhắc rõ món quà
        await update.message.reply_text(
            "🎁 **ĐÂY LÀ NHỮNG GÌ BẠN SẼ NHẬN ĐƯỢC SAU KHI CHIA SẺ 2 NGƯỜI:**\n\n"
            "✅ **Full Google Sheet** Quản lý tài chính cá nhân 3.2\n"
            "✅ **Full Google Apps Script** tích hợp sẵn\n"
            "✅ **Full Hướng dẫn** tạo Web App trên Notion\n"
            "✅ **Video hướng dẫn** chi tiết từng bước\n"
            "✅ **Toàn bộ tính năng** – sử dụng trọn đời\n\n"
            "💎 **Giá trị thực tế:** Hệ thống – Không phải lý thuyết",
            parse_mode="Markdown"
        )
        
        await asyncio.sleep(2)
        
        # MESSAGE 3: Tiến độ + CTA với buttons
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("🔗 Chia sẻ ngay", callback_data="share_link")],
            [InlineKeyboardButton("📘 Tìm hiểu thêm", url="https://freedomwallet.app")],
            [InlineKeyboardButton("📊 Xem tiến độ của tôi", callback_data="check_progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📊 **Tiến độ giới thiệu của bạn:**\n"
            f"**0 / 2 người**\n\n"
            "👉 Mỗi người chỉ cần đăng ký hoàn tất là được tính\n\n"
            "⏩ **Bắt đầu ngay để mở khóa quà** 🎁\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 **LINK CỦA BẠN:**\n"
            f"`{referral_link}`\n\n"
            "Copy link và chia sẻ ngay! 👆",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        # Start daily nurture journey (Day 1-5 until they reach 2 refs)
        from bot.handlers.daily_nurture import start_daily_nurture
        await start_daily_nurture(user.id, context)
        
        return ConversationHandler.END
        
    except Exception as e:
        session.rollback()
        await update.message.reply_text(
            f"❌ Lỗi khi lưu thông tin: {str(e)}\n\n"
            f"Vui lòng thử lại sau hoặc dùng /support",
            reply_markup=ReplyKeyboardRemove()
        )
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

