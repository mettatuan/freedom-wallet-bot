"""
Premium Keyboards - Menu hierarchy for Premium users
Organized, intuitive, and feature-rich
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ============================================
# MAIN PREMIUM MENU (Landing page)
# ============================================

def premium_main_menu():
    """
    Main Premium menu - 4 primary categories + settings
    Clean, organized, easy to navigate
    """
    keyboard = [
        [
            InlineKeyboardButton("💰 Tài chính", callback_data='premium_finance'),
            InlineKeyboardButton("📊 Báo cáo", callback_data='premium_reports')
        ],
        [
            InlineKeyboardButton("🎯 Mục tiêu", callback_data='premium_goals'),
            InlineKeyboardButton("🤖 AI Insights", callback_data='premium_ai')
        ],
        [
            InlineKeyboardButton("⚙️ Cài đặt", callback_data='premium_settings'),
            InlineKeyboardButton("❓ Trợ giúp", callback_data='premium_help')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# SUB-MENU 1: TÀI CHÍNH (Quick actions)
# ============================================

def finance_menu():
    """
    Financial actions: record, view, manage
    Most frequently used features
    """
    keyboard = [
        [
            InlineKeyboardButton("➕ Ghi giao dịch", callback_data='qr_start'),
            InlineKeyboardButton("💳 Xem số dư", callback_data='view_balance')
        ],
        [
            InlineKeyboardButton("📋 Lịch sử gần đây", callback_data='recent_transactions'),
            InlineKeyboardButton("🔄 Chuyển tiền hũ", callback_data='jar_transfer')
        ],
        [
            InlineKeyboardButton("📝 Sửa giao dịch", callback_data='edit_transaction'),
            InlineKeyboardButton("🗑️ Xóa giao dịch", callback_data='delete_transaction')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def quick_record_category_menu():
    """
    Quick record with category shortcuts
    Faster than typing
    """
    keyboard = [
        [
            InlineKeyboardButton("🍽️ Ăn uống", callback_data='qr_cat_food'),
            InlineKeyboardButton("🏠 Gia đình", callback_data='qr_cat_family')
        ],
        [
            InlineKeyboardButton("🚗 Di chuyển", callback_data='qr_cat_transport'),
            InlineKeyboardButton("💊 Sức khỏe", callback_data='qr_cat_health')
        ],
        [
            InlineKeyboardButton("🎉 Giải trí", callback_data='qr_cat_entertainment'),
            InlineKeyboardButton("📚 Học tập", callback_data='qr_cat_education')
        ],
        [
            InlineKeyboardButton("🛍️ Mua sắm", callback_data='qr_cat_shopping'),
            InlineKeyboardButton("➕ Khác", callback_data='qr_cat_other')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_finance')]
    ]
    return InlineKeyboardMarkup(keyboard)


def balance_view_menu():
    """
    Balance viewing options
    Quick insights + detailed view
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 Tổng quan", callback_data='balance_overview'),
            InlineKeyboardButton("🏺 Chi tiết hũ", callback_data='balance_jars')
        ],
        [
            InlineKeyboardButton("💳 Theo tài khoản", callback_data='balance_accounts'),
            InlineKeyboardButton("📈 Biểu đồ", callback_data='balance_chart')
        ],
        [
            InlineKeyboardButton("🔄 Đồng bộ", callback_data='sync_balance'),
            InlineKeyboardButton("📤 Xuất Excel", callback_data='export_balance')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_finance')]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# SUB-MENU 2: BÁO CÁO (Analytics & Reports)
# ============================================

def reports_menu():
    """
    Analytics, insights, and report generation
    Premium feature highlights
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 Hôm nay", callback_data='report_today'),
            InlineKeyboardButton("📅 Tuần này", callback_data='report_week')
        ],
        [
            InlineKeyboardButton("📆 Tháng này", callback_data='report_month'),
            InlineKeyboardButton("🗓️ Năm nay", callback_data='report_year')
        ],
        [
            InlineKeyboardButton("🔍 Tùy chỉnh", callback_data='report_custom'),
            InlineKeyboardButton("📈 So sánh", callback_data='report_compare')
        ],
        [
            InlineKeyboardButton("💾 Lưu báo cáo", callback_data='save_report'),
            InlineKeyboardButton("📤 Gửi email", callback_data='email_report')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def report_categories_menu():
    """
    Category breakdown analysis
    See where money goes
    """
    keyboard = [
        [
            InlineKeyboardButton("🍽️ Ăn uống", callback_data='cat_report_food'),
            InlineKeyboardButton("🏠 Gia đình", callback_data='cat_report_family')
        ],
        [
            InlineKeyboardButton("🚗 Di chuyển", callback_data='cat_report_transport'),
            InlineKeyboardButton("🎉 Giải trí", callback_data='cat_report_entertainment')
        ],
        [
            InlineKeyboardButton("📊 Tất cả", callback_data='cat_report_all'),
            InlineKeyboardButton("🔝 Top 5", callback_data='cat_report_top5')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_reports')]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# SUB-MENU 3: MỤC TIÊU (Goals & Budgets)
# ============================================

def goals_menu():
    """
    Financial goals and budget management
    Track progress, stay motivated
    """
    keyboard = [
        [
            InlineKeyboardButton("🎯 Mục tiêu hiện tại", callback_data='view_goals'),
            InlineKeyboardButton("➕ Tạo mục tiêu", callback_data='create_goal')
        ],
        [
            InlineKeyboardButton("💰 Ngân sách tháng", callback_data='monthly_budget'),
            InlineKeyboardButton("📊 Tiến độ", callback_data='goal_progress')
        ],
        [
            InlineKeyboardButton("🔔 Nhắc nhở", callback_data='goal_reminders'),
            InlineKeyboardButton("🏆 Thành tích", callback_data='achievements')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def budget_management_menu():
    """
    Budget allocation and tracking
    Control spending by category
    """
    keyboard = [
        [
            InlineKeyboardButton("🍽️ Ăn uống", callback_data='budget_food'),
            InlineKeyboardButton("🚗 Di chuyển", callback_data='budget_transport')
        ],
        [
            InlineKeyboardButton("🎉 Giải trí", callback_data='budget_entertainment'),
            InlineKeyboardButton("🛍️ Mua sắm", callback_data='budget_shopping')
        ],
        [
            InlineKeyboardButton("📊 Xem tất cả", callback_data='budget_all'),
            InlineKeyboardButton("⚙️ Tùy chỉnh", callback_data='budget_custom')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_goals')]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# SUB-MENU 4: AI INSIGHTS (Smart features)
# ============================================

def ai_insights_menu():
    """
    AI-powered insights and recommendations
    Premium exclusive features
    """
    keyboard = [
        [
            InlineKeyboardButton("🧠 Phân tích chi tiêu", callback_data='ai_spending_analysis'),
            InlineKeyboardButton("💡 Gợi ý tiết kiệm", callback_data='ai_saving_tips')
        ],
        [
            InlineKeyboardButton("🔮 Dự đoán xu hướng", callback_data='ai_forecast'),
            InlineKeyboardButton("⚠️ Cảnh báo bất thường", callback_data='ai_anomaly')
        ],
        [
            InlineKeyboardButton("🎯 Tối ưu ngân sách", callback_data='ai_optimize'),
            InlineKeyboardButton("📈 Chiến lược đầu tư", callback_data='ai_investment')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# SUB-MENU 5: CÀI ĐẶT (Settings & Sync)
# ============================================

def settings_menu():
    """
    Settings, sync, and account management
    Configure bot behavior
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 Sheets Settings", callback_data='settings_sheets'),
            InlineKeyboardButton("🔔 Thông báo", callback_data='settings_notifications')
        ],
        [
            InlineKeyboardButton("🌍 Ngôn ngữ", callback_data='settings_language'),
            InlineKeyboardButton("💱 Tiền tệ", callback_data='settings_currency')
        ],
        [
            InlineKeyboardButton("🔄 Đồng bộ", callback_data='settings_sync'),
            InlineKeyboardButton("📤 Xuất dữ liệu", callback_data='settings_export')
        ],
        [
            InlineKeyboardButton("🔐 Bảo mật", callback_data='settings_security'),
            InlineKeyboardButton("ℹ️ Về Premium", callback_data='settings_about')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def sheets_settings_menu():
    """
    Google Sheets configuration
    Connect, sync, troubleshoot
    """
    keyboard = [
        [
            InlineKeyboardButton("🔗 Kết nối Sheet", callback_data='connect_sheets'),
            InlineKeyboardButton("🌐 Cập nhật Web App", callback_data='update_webapp')
        ],
        [
            InlineKeyboardButton("🔄 Đồng bộ ngay", callback_data='sync_now'),
            InlineKeyboardButton("⚙️ Auto-sync", callback_data='toggle_autosync')
        ],
        [
            InlineKeyboardButton("🧪 Test kết nối", callback_data='test_connection'),
            InlineKeyboardButton("📋 Xem log", callback_data='view_sync_log')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_settings')]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# SUB-MENU 6: TRỢ GIÚP (Help & Support)
# ============================================

def help_menu():
    """
    Help, tutorials, and support
    Get user up to speed quickly
    """
    keyboard = [
        [
            InlineKeyboardButton("🎬 Video hướng dẫn", callback_data='help_videos'),
            InlineKeyboardButton("📚 Tài liệu", callback_data='help_docs')
        ],
        [
            InlineKeyboardButton("❓ FAQ", callback_data='help_faq'),
            InlineKeyboardButton("🚀 Hỗ trợ ưu tiên", callback_data='priority_support')
        ],
        [
            InlineKeyboardButton("💬 Nhóm cộng đồng", callback_data='help_community'),
            InlineKeyboardButton("📧 Liên hệ", callback_data='help_contact')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# QUICK ACTION MENUS (Context-specific)
# ============================================

def transaction_actions_menu(transaction_id: str):
    """
    Actions for a specific transaction
    Edit, delete, duplicate, share
    """
    keyboard = [
        [
            InlineKeyboardButton("✏️ Sửa", callback_data=f'edit_tx_{transaction_id}'),
            InlineKeyboardButton("📋 Nhân bản", callback_data=f'duplicate_tx_{transaction_id}')
        ],
        [
            InlineKeyboardButton("🗑️ Xóa", callback_data=f'delete_tx_{transaction_id}'),
            InlineKeyboardButton("🔄 Hoàn tác", callback_data=f'undo_tx_{transaction_id}')
        ],
        [InlineKeyboardButton("« Đóng", callback_data='close_tx_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)


def jar_selection_menu(action: str = "transfer"):
    """
    Jar selection for various actions
    Transfer, view, allocate budget
    """
    keyboard = [
        [
            InlineKeyboardButton("💰 NEC (55%)", callback_data=f'{action}_jar_NEC'),
            InlineKeyboardButton("🎯 FFA (10%)", callback_data=f'{action}_jar_FFA')
        ],
        [
            InlineKeyboardButton("📚 EDU (10%)", callback_data=f'{action}_jar_EDU'),
            InlineKeyboardButton("🎉 PLAY (10%)", callback_data=f'{action}_jar_PLAY')
        ],
        [
            InlineKeyboardButton("💝 GIVE (5%)", callback_data=f'{action}_jar_GIVE'),
            InlineKeyboardButton("💼 LTSS (10%)", callback_data=f'{action}_jar_LTSS')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_finance')]
    ]
    return InlineKeyboardMarkup(keyboard)


def date_range_menu():
    """
    Date range selection for reports
    Common periods + custom
    """
    keyboard = [
        [
            InlineKeyboardButton("📅 7 ngày qua", callback_data='range_7days'),
            InlineKeyboardButton("📆 30 ngày qua", callback_data='range_30days')
        ],
        [
            InlineKeyboardButton("📊 Tháng này", callback_data='range_this_month'),
            InlineKeyboardButton("📈 Tháng trước", callback_data='range_last_month')
        ],
        [
            InlineKeyboardButton("🗓️ Năm nay", callback_data='range_this_year'),
            InlineKeyboardButton("🔍 Tùy chỉnh", callback_data='range_custom')
        ],
        [InlineKeyboardButton("« Quay lại", callback_data='premium_reports')]
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================
# CONFIRMATION & INLINE ACTIONS
# ============================================

def confirm_action_menu(action: str, item_id: str = ""):
    """
    Confirmation dialog for destructive actions
    Delete, reset, etc.
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Xác nhận", callback_data=f'confirm_{action}_{item_id}'),
            InlineKeyboardButton("❌ Hủy", callback_data=f'cancel_{action}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def pagination_menu(page: int, total_pages: int, callback_prefix: str):
    """
    Pagination for lists
    Navigate through results
    """
    keyboard = []
    
    # Navigation buttons
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ Trước", callback_data=f'{callback_prefix}_page_{page-1}'))
    
    nav_row.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data='page_info'))
    
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("➡️ Sau", callback_data=f'{callback_prefix}_page_{page+1}'))
    
    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("« Đóng", callback_data='close_list')])
    
    return InlineKeyboardMarkup(keyboard)


# ============================================
# BACK TO MENU HELPER
# ============================================

def back_to_menu_button(target: str = 'premium_menu'):
    """
    Single back button for simple returns
    """
    keyboard = [[InlineKeyboardButton("« Quay lại menu", callback_data=target)]]
    return InlineKeyboardMarkup(keyboard)

