"""
Referral System Handlers
Manage referral links and tracking (growth metrics only, no feature unlocking)
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.database import (
    get_user_by_id,
    get_user_referrals
)


async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's referral stats and link"""
    user = update.effective_user
    db_user = await get_user_by_id(user.id)
    
    if not db_user:
        await update.message.reply_text(
            "❌ Lỗi: Không tìm thấy thông tin user. Vui lòng /start lại."
        )
        return
    
    # Get referral stats
    referral_code = db_user.referral_code
    referral_count = db_user.referral_count
    
    # Get referred users
    referred_users = await get_user_referrals(user.id)
    
    # Build referral link
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start={referral_code}"
    
    # Build message
    message = f"""
🎁 **GIỚI THIỆU BẠN BÈ**

📊 **Thống Kê Của Bạn:**
• Mã giới thiệu: `{referral_code}`
• Đã giới thiệu: {referral_count} người

🔗 **Link giới thiệu của bạn:**
`{referral_link}`

📱 **Cách sử dụng:**
1. Copy link trên
2. Gửi cho bạn bè/gia đình qua Telegram, Facebook, Zalo...
3. Mỗi người đăng ký giúp bạn xây dựng cộng đồng!

👋 **Chia sẻ với:**
• Bạn bè quan tâm quản lý tiền
• Người muốn bắt đầu tiết kiệm
• Ai cần công cụ miễn phí & đơn giản

💡 **Tất cả tính năng miễn phí cho mọi người!**
"""
    
    # Show referred users list
    if referred_users:
        message += f"\n👥 **Đã giới thiệu thành công:**\n"
        for idx, ref_user in enumerate(referred_users, 1):
            name = ref_user['name']
            date = ref_user['date'].strftime("%d/%m/%Y")
            message += f"{idx}. {name} ({date})\n"
    
    # Keyboard
    share_text = (
        "🎁 Freedom Wallet - Quản lý tài chính cá nhân đơn giản!\n\n"
        "Miễn phí vĩnh viễn cho mọi người!\n\n"
        "📊 6 Hũ Tiền | 📈 Google Sheets | 💰 Template sẵn"
    )
    keyboard = [
        [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_ref_{referral_code}")],
        [InlineKeyboardButton("📢 Chia sẻ ngay", 
                             url=f"https://t.me/share/url?url={referral_link}&text={share_text}")],
        [InlineKeyboardButton("« Quay lại", callback_data="back_to_menu")]
    ]
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def check_unlock_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DEPRECATED: Unlock system removed. Kept for backward compatibility."""
    # No-op: All users have full access from day 1
    pass


async def handle_referral_start(update: Update, context: ContextTypes.DEFAULT_TYPE, referral_code: str):
    """Handle when user starts bot via referral link"""
    from bot.utils.database import (
        get_user_by_referral_code,
        create_referral,
        save_user_to_db
    )
    
    user = update.effective_user
    
    # Save new user first
    await save_user_to_db(user)
    
    # Get referrer
    referrer = await get_user_by_referral_code(referral_code)
    
    if not referrer:
        # Invalid code, just show normal start
        return False
    
    if referrer.id == user.id:
        await update.message.reply_text(
            "😅 Bạn không thể tự giới thiệu chính mình nhé!\n\n"
            "Hãy gửi link cho bạn bè để nhận ưu đãi."
        )
        return False
    
    # Create referral relationship
    referral, error = await create_referral(referrer.id, user.id, referral_code)
    
    if error:
        await update.message.reply_text(f"❌ {error}")
        return False
    
    if referral:
        referrer_name = referrer.first_name or referrer.username or "một người bạn"
        
        # Welcome message + explain registration requirement
        await update.message.reply_text(
            f"🎉 **Chào mừng bạn đến Freedom Wallet!**\n\n"
            f"Bạn được giới thiệu bởi **{referrer_name}**.\n\n"
            f"📝 **Bước tiếp theo:**\n"
            f"Để nhận **Template Google Sheet miễn phí** và giúp {referrer_name} "
            f"mở khóa FREE tier, vui lòng:\n\n"
            f"👉 Điền thông tin đăng ký (30 giây)\n"
            f"👉 Nhận link Template qua email\n"
            f"👉 Bắt đầu quản lý tài chính ngay!\n\n"
            f"Bấm /register để bắt đầu ngay! 🚀",
            parse_mode="Markdown"
        )
        
        # Store referral context for later use
        context.user_data['referred_by'] = referrer.id
        context.user_data['referrer_name'] = referrer_name
        
        # Notify referrer (PENDING status)
        try:
            await context.bot.send_message(
                chat_id=referrer.id,
                text=f"🎊 **Tin vui!**\n\n"
                     f"**{user.first_name or user.username}** vừa nhấn vào link giới thiệu của bạn!\n\n"
                     f"⏳ Đang chờ họ hoàn tất đăng ký...\n"
                     f"(Sẽ thông báo khi xong)",
                parse_mode="Markdown"
            )
        except:
            pass  # Referrer might have blocked bot
        
        return True
    
    return False
