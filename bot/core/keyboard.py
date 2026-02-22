"""
Main Keyboard - Retention-First Design
Always-visible 4x2 keyboard for quick access to core features
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Get the main keyboard with 4x2 layout.
    
    Layout (per RETENTION_FIRST_REDESIGN.md):
    ┌─────────────────┬─────────────────┐
    │ 📊 Tổng quan    │ ➕ Ghi giao dịch│
    ├─────────────────┼─────────────────┤
    │ 📈 Báo cáo tuần │ 💡 Insight      │
    ├─────────────────┼─────────────────┤
    │ 🔗 Kết nối Drive│ 🌐 Mở Web App   │
    ├─────────────────┼─────────────────┤
    │ 🎁 Giới thiệu   │ ⚙️ Cài đặt      │
    └─────────────────┴─────────────────┘
    
    Features:
    - Always visible (persistent keyboard)
    - One-tap access to core features
    - No hidden menus or navigation flow
    - Resizable to fit screen
    
    Returns:
        ReplyKeyboardMarkup configured with main keyboard
    """
    keyboard = [
        [KeyboardButton("✍️ Ghi giao dịch"),  KeyboardButton("📊 Báo cáo")],
        [KeyboardButton("📂 Mở Google Sheet"), KeyboardButton("🌐 Mở Web App")],
        [KeyboardButton("🔗 Chia sẻ"),         KeyboardButton("💝 Đóng góp")],
        [KeyboardButton("📖 Hướng dẫn"),       KeyboardButton("⚙️ Cài đặt")],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="VD: Cà phê 35k 💬"
    )


# Button text constants
BTN_RECORD   = "✍️ Ghi giao dịch"
BTN_REPORT   = "📊 Báo cáo"
BTN_SHEETS   = "📂 Mở Google Sheet"
BTN_WEBAPP   = "🌐 Mở Web App"
BTN_SHARE    = "🔗 Chia sẻ"
BTN_DONATE   = "💝 Đóng góp"
BTN_GUIDE    = "📖 Hướng dẫn"
BTN_SETTINGS = "⚙️ Cài đặt"

# Legacy aliases (for any leftover references in other files)
BTN_OVERVIEW = BTN_REPORT
BTN_WEEKLY   = BTN_REPORT
BTN_INSIGHT  = BTN_REPORT
BTN_DRIVE    = BTN_SHEETS
BTN_REFERRAL = BTN_SHARE
