"""
Premium Commands - Handlers for Premium menu buttons
6 main buttons: Ghi chi tiêu, Tình hình, Phân tích, Gợi ý, Setup, Hỗ trợ

Design principle: 1 nút = 1 hành động quen thuộc
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime
from bot.utils.database import get_user_by_id
from bot.services.recommendation import get_recommendation_for_user, get_greeting


async def quick_record_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    💬 Ghi chi tiêu nhanh
    
    Hành vi lặp nhiều nhất - Neo thói quen
    Premium cảm nhận "nhẹ đầu" rõ nhất
    """
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user = await get_user_by_id(user_id)
        
        greeting = get_greeting(user) if user else "👋 Xin chào!"
        
        message = f"""
{greeting}

💬 **GHI CHI TIÊU NHANH**

Bạn chi bao nhiêu và cho việc gì?

**Ví dụ:**
• "50k cà phê"
• "200k ăn trưa"
• "1tr5 tiền nhà"

💡 Tôi sẽ hiểu và ghi vào Sheet cho bạn!
"""
        
        keyboard = [
            [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Premium user {user_id} opened quick record")
    except Exception as e:
        logger.error(f"Error in quick_record_handler: {e}", exc_info=True)
        await query.edit_message_text(
            "😓 Có lỗi xảy ra. Vui lòng thử lại sau!",
            parse_mode="Markdown"
        )


async def today_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    📊 Tình hình hôm nay
    
    Thay thế cho: /balance, /today, /status
    User không cần biết hỏi câu nào
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    if not user:
        await query.edit_message_text("❌ Không tìm thấy thông tin của bạn.")
        return
    
    # Get today's stats (mock for now - replace with real data)
    today_spent = "450K"  # TODO: Get from Sheet
    budget = "500K"  # TODO: Get from Sheet
    remaining = "50K"
    recorded_today = user.last_transaction_date == datetime.now().date() if user.last_transaction_date else False
    
    message = f"""
📊 **TÌNH HÌNH HÔM NAY**

━━━━━━━━━━━━━━━━━━━━━
💰 **CHI TIÊU:**
━━━━━━━━━━━━━━━━━━━━━

Đã chi: {today_spent}
Ngân sách: {budget}
Còn lại: {remaining}

━━━━━━━━━━━━━━━━━━━━━
📝 **GIAO DỊCH:**
━━━━━━━━━━━━━━━━━━━━━

{'✅ Đã ghi giao dịch hôm nay' if recorded_today else '⚠️ Chưa ghi giao dịch nào'}

━━━━━━━━━━━━━━━━━━━━━
🔥 **STREAK:** {user.streak_count if user else 0} ngày
━━━━━━━━━━━━━━━━━━━━━

💡 {'Tuyệt vời! Hãy tiếp tục!' if recorded_today else 'Hãy ghi giao dịch để giữ streak!'}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Ghi ngay", callback_data="quick_record"),
            InlineKeyboardButton("🧠 Phân tích", callback_data="analysis")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} checked today's status")


async def analysis_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    🧠 Phân tích cho tôi
    
    Nút "giá trị Premium"
    Không cần chọn loại phân tích - Bot tự quyết → đúng vai trợ lý
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    # Show loading message
    await query.edit_message_text("🧠 Đang phân tích dữ liệu của bạn...\n\n⏳ Vui lòng đợi 2-3 giây...")
    
    # TODO: Real analysis from Sheet data
    # For now, show mock analysis
    import asyncio
    await asyncio.sleep(2)
    
    message = f"""
🧠 **PHÂN TÍCH TÀI CHÍNH**

━━━━━━━━━━━━━━━━━━━━━
📊 **TUẦN NÀY:**
━━━━━━━━━━━━━━━━━━━━━

✅ **Làm tốt:**
• Ghi chép đều đặn 7/7 ngày
• Chi tiêu hũ NEC giảm 20%

⚠️ **Cần chú ý:**
• Chi hũ PLAY tăng 35% (vượt 150K)
• 3 khoản chi "linh tinh" chưa phân loại

━━━━━━━━━━━━━━━━━━━━━
💡 **GỢI Ý:**
━━━━━━━━━━━━━━━━━━━━━

1. Xem lại khoản chi PLAY (có thể giảm)
2. Phân loại 3 khoản "linh tinh" để rõ ràng
3. Tuần sau nên giữ mức chi hiện tại

━━━━━━━━━━━━━━━━━━━━━
📈 **XU HƯỚNG:**
━━━━━━━━━━━━━━━━━━━━━

Nhìn chung bạn đang làm rất tốt! 🎉
Tiếp tục duy trì streak và kiểm soát chi tiêu.
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Xem chi tiết", callback_data="detailed_report"),
            InlineKeyboardButton("💾 Xuất báo cáo", callback_data="export_report")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} requested analysis")


async def recommendation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    🎯 Gợi ý tiếp theo ⭐ (NÚT QUAN TRỌNG NHẤT)
    
    "Menu đề xuất" đúng nghĩa
    Bot chủ động đề xuất việc user nên làm tiếp theo
    
    👉 User mở bot chỉ để bấm nút này
    👉 Retention tăng mạnh
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get personalized recommendation from engine
    recommendation = get_recommendation_for_user(user_id)
    
    message = f"""
{recommendation['emoji']} **{recommendation['title']}**

━━━━━━━━━━━━━━━━━━━━━

{recommendation['message']}

━━━━━━━━━━━━━━━━━━━━━
💡 *Tôi luôn theo dõi và gợi ý cho bạn!*
"""
    
    # Dynamic keyboard based on recommendation action
    keyboard = []
    
    if recommendation['action'] == 'quick_record':
        keyboard.append([InlineKeyboardButton("📝 Ghi ngay", callback_data="quick_record")])
    elif recommendation['action'] == 'today_summary':
        keyboard.append([InlineKeyboardButton("📊 Xem tình hình", callback_data="today_status")])
    elif recommendation['action'] in ['last_week_analysis', 'month_analysis']:
        keyboard.append([InlineKeyboardButton("🧠 Phân tích ngay", callback_data="analysis")])
    else:
        keyboard.append([InlineKeyboardButton("📊 Xem dashboard", callback_data="today_status")])
    
    keyboard.append([InlineKeyboardButton("« Quay lại", callback_data="premium_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} checked recommendation - action: {recommendation['action']}")


async def setup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    🛠️ Setup giúp tôi
    
    Khác biệt Premium rất rõ
    Bán "tiết kiệm thời gian", không bán feature
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    message = f"""
🛠️ **MANAGED SETUP SERVICE**

Để tôi setup giúp bạn trong 5 phút! ⚡

━━━━━━━━━━━━━━━━━━━━━
📋 **QUY TRÌNH:**
━━━━━━━━━━━━━━━━━━━━━

1️⃣ Bạn cho tôi quyền truy cập Sheet
2️⃣ Tôi copy template + cấu hình
3️⃣ Tôi setup Apps Script
4️⃣ Tôi test và bàn giao
5️⃣ Bạn dùng ngay!

━━━━━━━━━━━━━━━━━━━━━
⏱️ **THỜI GIAN:** 5-10 phút
✅ **MIỄN PHÍ** cho Premium
━━━━━━━━━━━━━━━━━━━━━

💡 Bạn chỉ cần ngồi uống cà phê, tôi lo phần còn lại!

📧 **Liên hệ ngay:**
→ @freedom_wallet_admin
→ email@freedomwallet.app
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📧 Chat Admin", url="https://t.me/freedom_wallet_admin"),
            InlineKeyboardButton("📅 Đặt lịch", callback_data="schedule_setup")
        ],
        [InlineKeyboardButton("📹 Hoặc tự setup", callback_data="guide_self_setup")],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} requested setup service")


async def priority_support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    🚀 Hỗ trợ ưu tiên
    
    Premium cảm thấy được chăm sóc
    Giảm churn, tạo cảm giác "VIP thật"
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    message = f"""
🚀 **HỖ TRỢ ƯU TIÊN - PREMIUM**

Bạn có quyền được hỗ trợ nhanh chóng! ⚡

━━━━━━━━━━━━━━━━━━━━━
⏱️ **CAM KẾT:**
━━━━━━━━━━━━━━━━━━━━━

📱 Chat: Trả lời trong **30 phút**
📧 Email: Trả lời trong **2 giờ**
📞 Gọi điện: Đặt lịch trong ngày

━━━━━━━━━━━━━━━━━━━━━
💡 **CÁC VẤN ĐỀ ƯU TIÊN:**
━━━━━━━━━━━━━━━━━━━━━

✅ Hỏi phức tạp về công thức
✅ Lỗi không load được dữ liệu
✅ Cần phân tích/tư vấn ngay
✅ Sự cố khẩn cấp với app

━━━━━━━━━━━━━━━━━━━━━
📞 **LIÊN HỆ:**
━━━━━━━━━━━━━━━━━━━━━

💬 Telegram: @freedom_wallet_admin
📧 Email: support@freedomwallet.app
📅 Đặt lịch gọi: [Link]

💡 *Chúng tôi sẵn sàng hỗ trợ 24/7!*
"""
    
    keyboard = [
        [
            InlineKeyboardButton("💬 Chat ngay", url="https://t.me/freedom_wallet_admin")
        ],
        [
            InlineKeyboardButton("📧 Gửi email", callback_data="send_email"),
            InlineKeyboardButton("📅 Đặt lịch", callback_data="schedule_call")
        ],
        [InlineKeyboardButton("« Quay lại", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
    logger.info(f"Premium user {user_id} accessed priority support")


async def premium_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show Premium main menu (6 buttons)
    Called from callback_data="premium_menu"
    """
    query = update.callback_query
    await query.answer()
    
    try:
        user_id = update.effective_user.id
        user = await get_user_by_id(user_id)
        
        greeting = get_greeting(user) if user else "👋 Xin chào!"
        
        message = f"""
{greeting}

━━━━━━━━━━━━━━━━━━━━━
💎 **TRỢ LÝ TÀI CHÍNH CỦA BẠN**
━━━━━━━━━━━━━━━━━━━━━

Tôi luôn sẵn sàng hỗ trợ bạn 24/7! 🤖

📊 **Hôm nay:** {datetime.now().strftime('%d/%m/%Y')}
🔥 **Streak của bạn:** {user.streak_count if user else 0} ngày

💡 Chọn việc bạn muốn làm:
"""
        
        keyboard = [
            [
                InlineKeyboardButton("💬 Ghi chi tiêu nhanh", callback_data="quick_record"),
                InlineKeyboardButton("📊 Tình hình hôm nay", callback_data="today_status")
            ],
            [
                InlineKeyboardButton("🧠 Phân tích cho tôi", callback_data="analysis"),
                InlineKeyboardButton("🎯 Gợi ý tiếp theo", callback_data="recommendation")
            ],
            [
                InlineKeyboardButton("🛠️ Setup giúp tôi", callback_data="setup"),
                InlineKeyboardButton("🚀 Hỗ trợ ưu tiên", callback_data="priority_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Premium user {user_id} opened premium menu")
    except Exception as e:
        logger.error(f"Error in premium_menu_handler: {e}", exc_info=True)
        await query.edit_message_text(
            "😓 Có lỗi xảy ra. Vui lòng gõ /start để quay về trang chủ!",
            parse_mode="Markdown"
        )


# Callback routing map
PREMIUM_CALLBACKS = {
    'quick_record': quick_record_handler,
    'today_status': today_status_handler,
    'analysis': analysis_handler,
    'recommendation': recommendation_handler,
    'setup': setup_handler,
    'priority_support': priority_support_handler,
    'premium_menu': premium_menu_handler,
}
