"""
Status Command - Show user subscription status and ROI

Shows:
- Current tier (FREE/TRIAL/PREMIUM)
- Usage stats
- ROI for premium users
- Days remaining for trial
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils.database import get_user_by_id
from bot.core.subscription import SubscriptionManager, SubscriptionTier
from bot.services.roi_calculator import ROICalculator
from bot.services.analytics import Analytics
from datetime import datetime
from loguru import logger


async def mystatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mystatus command"""
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)  # FIX: Added await
    
    if not user:
        await update.message.reply_text(
            "❌ Không tìm thấy thông tin user.\n"
            "Gõ /start để bắt đầu!"
        )
        return
    
    # Get user tier
    tier = SubscriptionManager.get_user_tier(user)
    
    # Build message based on tier
    if tier == SubscriptionTier.FREE:
        message = _build_free_status_message(user)  # FIX: Removed await (not async)
        keyboard = [
            [InlineKeyboardButton("📊 Xem tiến độ", callback_data="referral_progress")],
            [InlineKeyboardButton("📖 Hướng dẫn", callback_data="help_tutorial")],
            [InlineKeyboardButton("🏠 Menu", callback_data="start")]
        ]
    
    elif tier == SubscriptionTier.TRIAL:
        message = _build_trial_status_message(user, user_id)  # FIX: Removed await
        keyboard = [
            [InlineKeyboardButton("💎 Nâng cấp Premium ngay", callback_data="upgrade_to_premium")],
            [InlineKeyboardButton("📊 Xem ROI chi tiết", callback_data="view_roi_detail")],
            [InlineKeyboardButton("🏠 Menu", callback_data="start")]
        ]
    
    elif tier == SubscriptionTier.PREMIUM:
        message = _build_premium_status_message(user, user_id)  # FIX: Removed await
        keyboard = [
            [InlineKeyboardButton("📊 ROI Dashboard đầy đủ", callback_data="view_roi_detail")],
            [InlineKeyboardButton("💡 Tối ưu sử dụng", callback_data="optimization_tips")],
            [InlineKeyboardButton("🏠 Menu", callback_data="start")]
        ]
    
    else:
        message = "⚠️ Lỗi: Không xác định được tier"
        keyboard = [[InlineKeyboardButton("🏠 Menu", callback_data="start")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Track analytics
    Analytics.track_event(user_id, 'mystatus_viewed', {
        'tier': tier.value,
        'messages_today': user.bot_chat_count or 0
    })
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


def _build_free_status_message(user) -> str:
    """Build status message for FREE users"""
    
    messages_today = user.bot_chat_count or 0
    remaining = max(0, 5 - messages_today)
    referral_count = user.referral_count or 0
    is_unlocked = user.is_free_unlocked
    
    if is_unlocked:
        status_emoji = "✅"
        status_text = "FREE FOREVER"
    else:
        status_emoji = "📊"
        status_text = f"FREE (Tiến độ: {referral_count}/2)"
    
    message = f"""
{status_emoji} **TÀI KHOẢN {status_text}**

━━━━━━━━━━━━━━━━━━━━━
📊 **SỬ DỤNG HÔM NAY:**
━━━━━━━━━━━━━━━━━━━━━

💬 Tin nhắn: {messages_today}/5
📍 Còn lại: {remaining} tin nhắn

━━━━━━━━━━━━━━━━━━━━━
🎁 **QUYỀN LỢI CỦA BẠN:**
━━━━━━━━━━━━━━━━━━━━━

✓ Template Freedom Wallet đầy đủ
✓ Bot hỗ trợ 5 message/ngày
✓ Kết nối Google Sheets
✓ Cộng đồng hỗ trợ

{"" if is_unlocked else f"""
━━━━━━━━━━━━━━━━━━━━━
💡 **MỞ KHÓA ĐẦY ĐỦ:**
━━━━━━━━━━━━━━━━━━━━━

Giới thiệu 2 bạn → Sở hữu vĩnh viễn ♾️
Gõ /referral để xem link của bạn.
"""}
"""
    
    return message


def _build_trial_status_message(user, user_id: int) -> str:
    """Build status message for TRIAL users"""
    
    # Calculate days remaining
    if user.trial_ends_at:
        now = datetime.utcnow()
        time_remaining = user.trial_ends_at - now
        days_remaining = max(0, time_remaining.days)
        hours_remaining = max(0, int(time_remaining.total_seconds() / 3600))
        trial_end_str = user.trial_ends_at.strftime("%d/%m/%Y %H:%M")
    else:
        days_remaining = 0
        hours_remaining = 0
        trial_end_str = "N/A"
    
    # Get ROI stats
    roi = ROICalculator.calculate_monthly_roi(user_id)
    
    message = f"""
🎁 **TÀI KHOẢN TRIAL**

━━━━━━━━━━━━━━━━━━━━━
⏰ **THỜI GIAN TRIAL:**
━━━━━━━━━━━━━━━━━━━━━

📅 Kết thúc: {trial_end_str}
⏳ Còn lại: **{days_remaining} ngày** ({hours_remaining}h)

{ROICalculator.format_roi_message(roi, "TRIAL")}

━━━━━━━━━━━━━━━━━━━━━
✨ **TÍNH NĂNG ĐÃ MỞ:**
━━━━━━━━━━━━━━━━━━━━━

✅ Unlimited tin nhắn
✅ AI phân tích tài chính
✅ Dashboard thông minh
✅ Gợi ý cá nhân hóa
✅ Hỗ trợ ưu tiên 30 phút

━━━━━━━━━━━━━━━━━━━━━
💡 **SAU KHI TRIAL KẾT THÚC:**
━━━━━━━━━━━━━━━━━━━━━

Nâng cấp Premium để tiếp tục:
💰 999,000 VNĐ/năm (~2,750 VNĐ/ngày)
🚀 Kích hoạt ngay lập tức
"""
    
    return message


def _build_premium_status_message(user, user_id: int) -> str:
    """Build status message for PREMIUM users"""
    
    # Calculate expiry date
    if user.premium_expires_at:
        days_remaining = (user.premium_expires_at - datetime.utcnow()).days
        expiry_date = user.premium_expires_at.strftime("%d/%m/%Y")
    else:
        days_remaining = 365
        expiry_date = "N/A"
    
    # Get ROI stats
    roi = ROICalculator.calculate_monthly_roi(user_id)
    
    message = f"""
💎 **TÀI KHOẢN PREMIUM**

━━━━━━━━━━━━━━━━━━━━━
⏰ **THÔNG TIN:**
━━━━━━━━━━━━━━━━━━━━━

📅 Hết hạn: {expiry_date}
⏳ Còn lại: {days_remaining} ngày

{ROICalculator.format_roi_message(roi, "PREMIUM")}

━━━━━━━━━━━━━━━━━━━━━
🎯 **TỐI ƯU HÓA GIÁ TRỊ:**
━━━━━━━━━━━━━━━━━━━━━

💡 Sử dụng nhiều hơn = ROI cao hơn!

**Gợi ý:**
• Chat với AI mỗi ngày
• Dùng Dashboard thường xuyên
• Thử tính năng Phân tích
• Nhận Gợi ý cá nhân

→ Mục tiêu: ROI ≥ +200% 🚀
"""
    
    return message
