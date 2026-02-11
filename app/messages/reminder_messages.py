"""
Daily Reminder Message Templates

Templates for morning/evening reminders and skip alerts.
Used by: app.services.messaging_service, app.handlers.engagement.daily_reminder
"""

# Morning Reminder Content (8:00 AM)
MORNING_REMINDER_TEMPLATE = """
🌅 **Chào buổi sáng {name}!**

💪 **Hôm nay là ngày thứ {streak} ghi chép của bạn!**

────────────────────────

🎯 **Mục tiêu hôm nay:**
• Ghi ít nhất 3 giao dịch
• Nhớ phân loại đúng hũ tiền
• Review tổng chi tiêu

{streak_message}

────────────────────────

💡 **Tip:** Ghi chép ngay khi chi tiêu → không bao giờ quên!
"""

# Evening Reminder Content (8:00 PM)
EVENING_REMINDER_TEMPLATE = """
🌙 **Trước khi ngủ... {name}**

❓ **Hôm nay bạn đã ghi chép chưa?**

────────────────────────

{streak_status}

────────────────────────

💤 **Ghi ngay trước khi quên:**
• Bữa ăn hôm nay
• Di chuyển (xăng, grab...)
• Cafe, giải trí
• Mua sắm

💡 *Chỉ mất 30 giây thôi!*
"""

# Skip Alert (nếu không ghi 2 ngày liên tiếp)
SKIP_ALERT_TEMPLATE = """
😢 **Uhm... {name}, bạn ổn chứ?**

Mình thấy bạn đã không ghi chép {skip_days} ngày rồi.

────────────────────────

💡 **Gặp khó khăn gì không?**
• Quên mất?
• App gặp lỗi?
• Chưa rõ cách ghi?

────────────────────────

Mình ở đây giúp bạn! Nhắn cho mình nhé 💬

*"Thành công không đến từ động lực - mà đến từ hành động!"*
"""


def get_streak_message(streak: int) -> str:
    """
    Generate encouraging message based on current streak
    
    Args:
        streak: Current streak count (days)
        
    Returns:
        Encouraging message string
    """
    if streak == 1:
        return "🌱 **Streak mới bắt đầu!** Hãy tiếp tục nhé!"
    elif streak < 3:
        return f"🔥 **Streak: {streak} ngày!** Cố gắng thêm một chút nữa!"
    elif streak < 7:
        return f"🔥 **Streak: {streak} ngày!** Tuyệt vời! Còn {7-streak} ngày nữa đạt 7 ngày!"
    elif streak == 7:
        return "🎉 **CHÚC MỪNG! 7 NGÀY LIÊN TỤC!** Hôm nay bạn sẽ nhận quà đặc biệt!"
    elif streak < 21:
        return f"🔥 **Streak: {streak} ngày!** Amazing! Đang trên đường hình thành thói quen!"
    elif streak < 30:
        return f"🔥 **Streak: {streak} ngày!** Xuất sắc! Còn {30-streak} ngày nữa đạt 30 ngày!"
    elif streak == 30:
        return "🏆 **CHÚC MỪNG! 30 NGÀY LIÊN TỤC!** Bạn sẽ nhận huy chương danh dự!"
    elif streak < 90:
        return f"🏆 **Streak: {streak} ngày!** Legendary! Bạn đã là master!"
    else:
        return f"👑 **Streak: {streak} ngày!** GODLIKE! Bạn là huyền thoại!"
