"""
Premium Keyboards Module
Provides keyboard layouts for premium features
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def premium_main_menu():
    """Main premium menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("💰 Tài chính", callback_data="premium_finance"),
            InlineKeyboardButton("📊 Báo cáo", callback_data="premium_reports")
        ],
        [
            InlineKeyboardButton("🎯 Mục tiêu", callback_data="premium_goals"),
            InlineKeyboardButton("🤖 AI Insights", callback_data="premium_ai")
        ],
        [
            InlineKeyboardButton("⚙️ Cài đặt", callback_data="premium_settings"),
            InlineKeyboardButton("❓ Trợ giúp", callback_data="premium_help")
        ],
        [InlineKeyboardButton("🏠 Trang chủ", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def finance_menu():
    """Finance submenu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("💳 Tài khoản", callback_data="premium_accounts"),
            InlineKeyboardButton("💰 Số dư", callback_data="premium_balance")
        ],
        [
            InlineKeyboardButton("📝 Ghi nhanh", callback_data="premium_quick_record"),
            InlineKeyboardButton("🏺 6 Hũ Tiền", callback_data="premium_jars")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def reports_menu():
    """Reports submenu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📅 Tuần này", callback_data="report_week"),
            InlineKeyboardButton("📆 Tháng này", callback_data="report_month")
        ],
        [
            InlineKeyboardButton("📈 Xu hướng", callback_data="report_trends"),
            InlineKeyboardButton("💹 So sánh", callback_data="report_compare")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def goals_menu():
    """Goals submenu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Mục tiêu hiện tại", callback_data="goals_current"),
            InlineKeyboardButton("➕ Tạo mục tiêu", callback_data="goals_create")
        ],
        [
            InlineKeyboardButton("📊 Tiến độ", callback_data="goals_progress"),
            InlineKeyboardButton("🏆 Đã đạt", callback_data="goals_completed")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def ai_insights_menu():
    """AI Insights submenu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("💡 Phân tích chi tiêu", callback_data="ai_spending"),
            InlineKeyboardButton("🎯 Đề xuất", callback_data="ai_suggestions")
        ],
        [
            InlineKeyboardButton("📈 Dự đoán", callback_data="ai_predictions"),
            InlineKeyboardButton("🔍 Phát hiện bất thường", callback_data="ai_anomalies")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def settings_menu():
    """Settings submenu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🔔 Thông báo", callback_data="settings_notifications"),
            InlineKeyboardButton("🌐 Ngôn ngữ", callback_data="settings_language")
        ],
        [
            InlineKeyboardButton("🔗 Kết nối", callback_data="settings_connections"),
            InlineKeyboardButton("👤 Hồ sơ", callback_data="settings_profile")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def help_menu():
    """Help submenu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📖 Hướng dẫn", callback_data="help_guide"),
            InlineKeyboardButton("❓ FAQ", callback_data="help_faq")
        ],
        [
            InlineKeyboardButton("💬 Hỗ trợ", callback_data="help_support"),
            InlineKeyboardButton("📹 Video", callback_data="help_videos")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def balance_view_menu():
    """Balance view keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Làm mới", callback_data="balance_refresh"),
            InlineKeyboardButton("📊 Chi tiết", callback_data="balance_details")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_finance")]
    ]
    return InlineKeyboardMarkup(keyboard)


def quick_record_category_menu():
    """Quick record category selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🍜 Ăn uống", callback_data="qr_cat_food"),
            InlineKeyboardButton("🏠 Nhà ở", callback_data="qr_cat_housing")
        ],
        [
            InlineKeyboardButton("🚗 Di chuyển", callback_data="qr_cat_transport"),
            InlineKeyboardButton("🎉 Giải trí", callback_data="qr_cat_entertainment")
        ],
        [
            InlineKeyboardButton("🛒 Mua sắm", callback_data="qr_cat_shopping"),
            InlineKeyboardButton("💊 Sức khỏe", callback_data="qr_cat_health")
        ],
        [InlineKeyboardButton("« Hủy", callback_data="premium_finance")]
    ]
    return InlineKeyboardMarkup(keyboard)


def jar_selection_menu():
    """6 Jars selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🏠 Thiết yếu (55%)", callback_data="jar_necessities"),
            InlineKeyboardButton("🎉 Hưởng thụ (10%)", callback_data="jar_play")
        ],
        [
            InlineKeyboardButton("🎓 Giáo dục (10%)", callback_data="jar_education"),
            InlineKeyboardButton("💰 Tiết kiệm (10%)", callback_data="jar_savings")
        ],
        [
            InlineKeyboardButton("💼 Đầu tư (10%)", callback_data="jar_investment"),
            InlineKeyboardButton("❤️ Cho đi (5%)", callback_data="jar_giving")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_finance")]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_menu_button(callback_data="premium_menu"):
    """Generic back to menu button"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("« Quay lại menu", callback_data=callback_data)
    ]])
