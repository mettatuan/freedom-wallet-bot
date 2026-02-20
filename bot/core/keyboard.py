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
        # Row 1: Overview + Quick Record
        [
            KeyboardButton("📊 Tổng quan"),
            KeyboardButton("➕ Ghi giao dịch")
        ],
        # Row 2: Weekly Report + Insights
        [
            KeyboardButton("📈 Báo cáo tuần"),
            KeyboardButton("💡 Insight")
        ],
        # Row 3: Drive Sync + Web App
        [
            KeyboardButton("🔗 Kết nối Drive"),
            KeyboardButton("🌐 Mở Web App")
        ],
        # Row 4: Referral + Settings
        [
            KeyboardButton("🎁 Giới thiệu"),
            KeyboardButton("⚙️ Cài đặt")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,  # Fit to screen
        one_time_keyboard=False,  # Always visible
        input_field_placeholder="VD: Cà phê 35k 💬"  # Hint for quick input
    )


# Button text constants for handler matching
BTN_OVERVIEW = "📊 Tổng quan"
BTN_RECORD = "➕ Ghi giao dịch"
BTN_WEEKLY = "📈 Báo cáo tuần"
BTN_INSIGHT = "💡 Insight"
BTN_DRIVE = "🔗 Kết nối Drive"
BTN_WEBAPP = "🌐 Mở Web App"
BTN_REFERRAL = "🎁 Giới thiệu"
BTN_SETTINGS = "⚙️ Cài đặt"
