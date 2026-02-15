"""
Daily Nurture Campaign - Gửi nội dung giáo dục hàng ngày
Cho users chưa đủ 2 referrals

Week 3: Integrated with ProgramManager
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime, timedelta

# Week 3: Import ProgramManager
from app.services.program_manager import ProgramManager, ProgramType


# Nội dung nurture theo từng ngày
NURTURE_MESSAGES = {
    1: {
        "title": "📅 DAY 1 – VÌ SAO CẦN QUẢN LÝ TÀI CHÍNH?",
        "content": (
            "❓ **Bạn có biết?**\n\n"
            "**90% người đi làm** không biết tiền của mình đang đi đâu mỗi tháng\n\n"
            "Quản lý tài chính **không phải** để tiết kiệm cực khổ, mà để:\n"
            "✓ **An tâm hơn**\n"
            "✓ **Chủ động hơn**\n"
            "✓ **Không bị tiền chi phối cảm xúc**\n\n"
            "👉 Freedom Wallet giúp bạn nhìn thấy **toàn bộ bức tranh tài chính**"
        ),
        "delay_hours": 24  # Gửi sau 24h đăng ký
    },
    2: {
        "title": "📅 DAY 2 – CÁI GIÁ CỦA VIỆC KHÔNG QUẢN LÝ TIỀN",
        "content": (
            "💥 **Không quản lý tài chính dẫn đến:**\n\n"
            "❌ Làm nhiều nhưng không dư\n"
            "❌ Có tiền vẫn lo\n"
            "❌ Không dám đầu tư dài hạn\n\n"
            "👉 **Quản lý tiền = kiểm soát cuộc sống**\n\n"
            "🔗 Chia sẻ để mở khóa bộ công cụ trọn đời"
        ),
        "delay_hours": 48
    },
    3: {
        "title": "📅 DAY 3 – 6 HŨ TIỀN & 5 CẤP BẬC TÀI CHÍNH",
        "content": (
            "🧠 **Freedom Wallet áp dụng:**\n\n"
            "💰 **6 Hũ Tiền:** phân bổ dòng tiền khoa học\n"
            "• 55% Chi tiêu thiết yếu (NEC)\n"
            "• 10% Tự do tài chính (FFA)\n"
            "• 10% Giáo dục (EDU)\n"
            "• 10% Tiết kiệm dài hạn (LTSS)\n"
            "• 10% Hưởng thụ (PLAY)\n"
            "• 5% Cho đi (GIVE)\n\n"
            "📊 **5 Cấp Bậc Tài Chính:** biết bạn đang ở đâu & đi về đâu\n\n"
            "👉 Không học lý thuyết suông – **áp dụng ngay**"
        ),
        "delay_hours": 72
    },
    4: {
        "title": "📅 DAY 4 – VÌ SAO CHÚNG TÔI TẶNG QUÀ?",
        "content": (
            "🎁 **Vì chúng tôi tin rằng:**\n\n"
            "✅ Người dùng tốt nhất → là người **giới thiệu người tốt**\n"
            "✅ Chia sẻ giá trị → tạo **cộng đồng chất lượng**\n"
            "✅ Giúp nhau → cùng **tiến bộ**\n\n"
            "👉 **Bạn giúp 2 người – bạn nhận hệ thống trọn đời**\n\n"
            "Đơn giản vậy thôi! 💙"
        ),
        "delay_hours": 96
    },
    5: {
        "title": "📅 DAY 5 – NHẮC NHẸ + TẠO CẤP BÁCH",
        "content": (
            "⏳ **Bộ quà chỉ dành cho người hoàn thành đủ 2 lượt giới thiệu**\n\n"
            "Hàng ngàn người đã nhận được:\n"
            "✅ Google Sheet Template\n"
            "✅ Apps Script tự động hóa\n"
            "✅ Hướng dẫn đầy đủ\n"
            "✅ Hỗ trợ 1-1\n\n"
            "👉 **Chỉ còn thiếu bạn!**"
        ),
        "delay_hours": 120
    }
}


async def start_daily_nurture(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Start daily nurture campaign for new user
    
    Week 3: Now uses ProgramManager for enrollment
    Old scheduling logic kept for backward compatibility
    """
    try:
        logger.info(f"Starting daily nurture for user {user_id}")
        
        # Week 3: Use ProgramManager
        with ProgramManager() as pm:
            success = await pm.enroll_user(
                user_id, 
                ProgramType.NURTURE_7_DAY, 
                context,
                force=False  # Don't override existing programs
            )
            
            if success:
                logger.info(f"✅ User {user_id} enrolled in NURTURE_7_DAY via ProgramManager")
            else:
                logger.info(f"⚠️ User {user_id} already in program, skipped NURTURE enrollment")
        
    except Exception as e:
        logger.error(f"❌ Error starting daily nurture for user {user_id}: {e}")
        # Fallback to old method if ProgramManager fails
        await _start_daily_nurture_legacy(user_id, context)


async def _start_daily_nurture_legacy(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Legacy method: Schedule all 5 days at once
    Kept for backward compatibility
    """
    try:
        logger.info(f"Using legacy nurture scheduling for user {user_id}")
        
        logger.info(f"Using legacy nurture scheduling for user {user_id}")
        
        # Schedule all 5 days
        for day, data in NURTURE_MESSAGES.items():
            delay_seconds = data["delay_hours"] * 3600
            
            # Schedule the message
            context.job_queue.run_once(
                send_nurture_message,
                delay_seconds,
                data={
                    "user_id": user_id,
                    "day": day,
                    "title": data["title"],
                    "content": data["content"]
                },
                name=f"nurture_day{day}_user{user_id}"
            )
        
        logger.info(f"✅ Scheduled 5-day nurture (legacy) for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error in legacy nurture scheduling for user {user_id}: {e}")


async def send_nurture_message(context: ContextTypes.DEFAULT_TYPE):
    """
    Send a single nurture message (called by scheduler)
    """
    try:
        job_data = context.job.data
        user_id = job_data["user_id"]
        day = job_data["day"]
        title = job_data["title"]
        content = job_data["content"]
        
        # Check if user already has 2+ referrals (stop nurture if unlocked)
        from app.utils.database import get_user_by_id
        db_user = await get_user_by_id(user_id)
        
        if not db_user:
            logger.warning(f"User {user_id} not found, skipping nurture day {day}")
            return
        
        if db_user.referral_count >= 2:
            logger.info(f"User {user_id} already unlocked (2+ refs), skipping nurture day {day}")
            # Cancel remaining nurture jobs
            await cancel_remaining_nurture(user_id, day, context)
            return
        
        # Get current progress
        referral_count = db_user.referral_count
        remaining = 2 - referral_count
        
        # Generate referral link
        from app.utils.database import generate_referral_code
        referral_code = generate_referral_code(user_id)
        bot_username = (await context.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
        
        # Build keyboard
        keyboard = [
            [InlineKeyboardButton("🔗 Chia sẻ ngay", callback_data="share_link")],
            [InlineKeyboardButton("📊 Xem tiến độ", callback_data="check_progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send message
        message_text = (
            f"{title}\n\n"
            f"{content}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **Tiến độ của bạn:** {referral_count} / 2 người\n"
        )
        
        if referral_count == 0:
            message_text += f"🎯 **Còn 2 người nữa!**\n\n"
        elif referral_count == 1:
            message_text += f"🎯 **Chỉ còn 1 người nữa!** 🔥\n\n"
        
        message_text += f"🔗 **Link của bạn:**\n`{referral_link}`"
        
        await context.bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"✅ Sent nurture day {day} to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error sending nurture message: {e}")


async def cancel_remaining_nurture(user_id: int, current_day: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancel remaining nurture jobs when user unlocks
    """
    try:
        jobs = context.job_queue.get_jobs_by_name(f"nurture_day*_user{user_id}")
        for job in jobs:
            # Extract day number from job name
            job_day = int(job.name.split("day")[1].split("_")[0])
            if job_day > current_day:
                job.schedule_removal()
                logger.info(f"Cancelled nurture day {job_day} for user {user_id}")
    except Exception as e:
        logger.error(f"Error cancelling nurture jobs: {e}")


async def handle_share_link_button(update, context):
    """Handle 'Chia sẻ ngay' button"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Get user data
    from app.utils.database import get_user_by_id
    from app.utils.database import generate_referral_code
    
    db_user = await get_user_by_id(user_id)
    if not db_user:
        await query.edit_message_text("❌ Không tìm thấy thông tin user. Dùng /register để đăng ký.")
        return
    
    referral_count = db_user.referral_count
    referral_code = generate_referral_code(user_id)
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
    
    # Send share message with social buttons
    keyboard = [
        [
            InlineKeyboardButton("📱 Telegram", url=f"https://t.me/share/url?url={referral_link}&text=Tham gia Freedom Wallet cùng tôi!"),
            InlineKeyboardButton("💬 Facebook", url=f"https://www.facebook.com/sharer/sharer.php?u={referral_link}")
        ],
        [
            InlineKeyboardButton("🐦 X (Twitter)", url=f"https://twitter.com/intent/tweet?url={referral_link}&text=Quản lý tài chính cá nhân với Freedom Wallet!")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🔗 **LINK GIỚI THIỆU CỦA BẠN:**\n\n"
        f"`{referral_link}`\n\n"
        f"📊 **Tiến độ:** {referral_count}/2 người\n\n"
        f"👆 Copy link hoặc chia sẻ trực tiếp:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def handle_check_progress_button(update, context):
    """Handle 'Xem tiến độ' button"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Get user data
    from app.utils.database import get_user_by_id
    db_user = await get_user_by_id(user_id)
    
    if not db_user:
        await query.edit_message_text("❌ Không tìm thấy thông tin user. Dùng /register để đăng ký.")
        return
    
    referral_count = db_user.referral_count
    remaining = 2 - referral_count
    
    if referral_count >= 2:
        status = "✅ **ĐÃ MỞ KHÓA TRỌN ĐỜI!**"
    elif referral_count == 1:
        status = "🔥 **Chỉ còn 1 người nữa!**"
    else:
        status = "🎯 **Bắt đầu chia sẻ ngay!**"
    
    keyboard = [
        [InlineKeyboardButton("🔗 Chia sẻ link", callback_data="share_link")],
        [InlineKeyboardButton("🏠 Menu chính", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📊 **TIẾN ĐỘ GIỚI THIỆU**\n\n"
        f"**{referral_count} / 2 người**\n\n"
        f"{status}\n\n"
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

