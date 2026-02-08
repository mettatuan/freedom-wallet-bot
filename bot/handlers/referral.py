"""
Referral System Handlers
Manage referral links, tracking, and FREE tier unlocking
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.database import (
    get_user_by_id,
    get_user_referrals,
    check_and_unlock_free
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
    is_unlocked = db_user.is_free_unlocked
    
    # Get referred users
    referred_users = await get_user_referrals(user.id)
    
    # Build referral link
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start={referral_code}"
    
    # Status message
    if is_unlocked:
        status_msg = "✅ **FREE FOREVER đã mở khóa!**\n\n"
    else:
        remaining = 2 - referral_count
        status_msg = f"🎯 **Còn {remaining} người nữa để mở khóa FREE!**\n\n"
    
    # Build message
    message = f"""
🎁 **HỆ THỐNG GIỚI THIỆU BẠN BÈ**

{status_msg}📊 **Thống Kê Của Bạn:**
• Mã giới thiệu: `{referral_code}`
• Đã giới thiệu: {referral_count} người
• Trạng thái: {"✅ FREE Unlocked" if is_unlocked else "🔒 Đang khóa"}

🔗 **Link giới thiệu của bạn:**
`{referral_link}`

📱 **Cách sử dụng:**
1. Copy link trên
2. Gửi cho bạn bè/gia đình qua Telegram, Facebook, Zalo...
3. Khi 2 người đăng ký qua link → Bạn mở khóa **FREE FOREVER**!

💎 **Quyền lợi FREE khi unlock:**
✓ Bot AI không giới hạn
✓ Template Freedom Wallet đầy đủ
✓ Hướng dẫn tạo Web App chi tiết 📚
✓ Tham gia Group hỗ trợ 1-1 💬
✓ Cập nhật tính năng mới miễn phí

🎯 **Mẹo tăng tốc:**
• Share trong nhóm gia đình
• Post lên Facebook cá nhân
• Gửi cho đồng nghiệp quan tâm tài chính
• Share story Instagram/TikTok
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
        "🎁 Freedom Wallet - Ứng dụng quản lý tài chính cá nhân hiện đại!\n\n"
        "✅ FREE cho 1000 người đầu tiên! Giới thiệu 2 bạn để nhận miễn phí trọn đời.\n\n"
        "📊 6 Hũ Tiền | 📈 Theo dõi đầu tư | 💰 Tối ưu chi tiêu"
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
    """Check and notify if user just unlocked FREE"""
    user_id = update.effective_user.id
    unlocked = await check_and_unlock_free(user_id)
    
    if unlocked:
        # Send comprehensive unlock message with guides and group invite
        await context.bot.send_message(
            chat_id=user_id,
            text="""
🎉🎉🎉 **CHÚC MỪNG!** 🎉🎉🎉

Bạn vừa mở khóa **FREE FOREVER**!

✅ **Quyền lợi của bạn:**
✓ Sử dụng Bot không giới hạn
✓ Tải Template Freedom Wallet
✓ Truy cập đầy đủ tính năng
✓ Cập nhật tính năng mới miễn phí

📚 **Tài liệu hướng dẫn:**
👉 [Hướng dẫn tạo Web App](https://eliroxbot.notion.site/freedomwallet)

💬 **Tham gia cộng đồng:**
👉 [Freedom Wallet Group](https://t.me/freedomwalletapp)
(Hỗ trợ 1-1, chia sẻ tips, cập nhật mới)

🚀 Bắt đầu ngay với /help hoặc hỏi mình bất cứ điều gì!
""",
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        return True
    
    return False


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
