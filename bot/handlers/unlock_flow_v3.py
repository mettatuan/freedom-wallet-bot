"""
Unlock Flow v3.0 - Optimized Post-Unlock Journey
Ownership-first, Identity-driven, User-controlled pacing
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from loguru import logger


async def send_unlock_message_1(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    MESSAGE 1: RECOGNITION & OWNERSHIP
    Chuyển trạng thái tâm lý từ "hoàn thành nhiệm vụ xã hội" → "sở hữu công cụ cá nhân"
    """
    text = """🎉 Chúc mừng bạn!

Bạn đã hoàn tất mốc 2 người giới thiệu.
Từ đây, Freedom Wallet đã sẵn sàng để bạn sử dụng đầy đủ cho chính mình.

Không phải xem thử.
Không phải làm cho có.

👉 Đây là hệ thống quản lý tài chính cá nhân của bạn."""

    keyboard = [
        [InlineKeyboardButton("🔓 Tiếp tục", callback_data="unlock_continue")],
        [InlineKeyboardButton("📊 Xem trạng thái của tôi", callback_data="unlock_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=None
        )
        logger.info(f"✅ Sent unlock Message 1 to user {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send unlock Message 1 to user {user_id}: {e}")


async def handle_unlock_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    MESSAGE 2: IDENTITY + SINGLE NEXT STEP
    Trigger: User clicks "🔓 Tiếp tục"
    """
    query = update.callback_query
    await query.answer()
    
    text = """Từ thời điểm này, bạn là thành viên chính thức của Freedom Wallet.

Thành viên chính thức là những người:
• Chủ động quản lý tiền của mình
• Muốn nhìn rõ dòng tiền, không đoán mò
• Sẵn sàng bắt đầu bằng hành động thực tế

Bước tiếp theo rất đơn giản:
👉 Thiết lập Freedom Wallet để bắt đầu sử dụng."""

    keyboard = [
        [InlineKeyboardButton("🛠 Bắt đầu thiết lập", callback_data="setup_start")],
        [InlineKeyboardButton("🧭 Xem lộ trình cá nhân", callback_data="view_roadmap")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"✅ Sent unlock Message 2 to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send unlock Message 2: {e}")


async def handle_unlock_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ALTERNATIVE PATH: User clicks "📊 Xem trạng thái của tôi"
    """
    query = update.callback_query
    await query.answer()
    
    text = """📊 TRẠNG THÁI CỦA BẠN

✅ Đã hoàn tất: 2/2 giới thiệu
✅ Trạng thái: Thành viên FREE
✅ Quyền truy cập: Đầy đủ tính năng

Bước tiếp theo:
👉 Thiết lập Freedom Wallet để sử dụng."""

    keyboard = [[InlineKeyboardButton("🔓 Bắt đầu ngay", callback_data="unlock_continue")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"✅ Showed status to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to show status: {e}")


async def handle_setup_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    MESSAGE 3: DAY 1 – FIRST REAL USAGE
    Trigger: User clicks "🛠 Bắt đầu thiết lập"
    """
    query = update.callback_query
    await query.answer()
    
    text = """🎯 BƯỚC ĐẦU TIÊN – THIẾT LẬP FREEDOM WALLET

Bạn chỉ cần làm 3 việc (10–15 phút):
1️⃣ Copy Google Sheets Template
2️⃣ Tạo Web App cá nhân
3️⃣ Nhập số dư + 1 giao dịch đầu tiên

👉 Không cần biết code.
👉 Làm chậm cũng hoàn toàn ổn."""

    keyboard = [
        [InlineKeyboardButton("📑 Copy Template", url="https://docs.google.com/spreadsheets/d/1nMJNc3KWEGWs7LMZpGJaxeiqbCFaLg_O3oYE4Wx5lnU/copy")],
        [InlineKeyboardButton("🌐 Hướng dẫn Web App", callback_data="webapp_guide")],
        [InlineKeyboardButton("❓ Cần hỗ trợ", callback_data="setup_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"✅ Sent setup Message 3 to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send setup message: {e}")


async def handle_view_roadmap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ALTERNATIVE PATH: User clicks "🧭 Xem lộ trình cá nhân"
    """
    query = update.callback_query
    await query.answer()
    
    text = """🧭 LỘ TRÌNH CÁ NHÂN

**Hôm nay:**
✓ Thiết lập Web App (10-15 phút)
✓ Nhập giao dịch đầu tiên

**Tuần này:**
• Hiểu về 6 Hũ Tiền
• Theo dõi dòng tiền hàng ngày
• Xem báo cáo chi tiêu

**Tháng này:**
• Xây dựng Quỹ Khẩn Cấp
• Lập kế hoạch tài chính rõ ràng
• Làm chủ tài chính cá nhân

Sẵn sàng bắt đầu?"""

    keyboard = [[InlineKeyboardButton("🛠 Bắt đầu thiết lập", callback_data="setup_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"✅ Showed roadmap to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to show roadmap: {e}")


async def handle_webapp_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User clicks "🌐 Hướng dẫn Web App"
    Send step-by-step setup guide
    """
    query = update.callback_query
    await query.answer()
    
    # Use existing webapp setup handler
    from bot.handlers.webapp_setup import start_webapp_setup
    await start_webapp_setup(update, context)


async def handle_setup_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User clicks "❓ Cần hỗ trợ"
    Show support options
    """
    query = update.callback_query
    await query.answer()
    
    text = """❓ HỖ TRỢ THIẾT LẬP

Chọn cách bạn muốn được hỗ trợ:"""

    keyboard = [
        [InlineKeyboardButton("📚 Xem hướng dẫn Notion", url="https://phamthanhtuan.notion.site/1717ba14c3d0801090cdf4c57ff08652?pvs=105")],
        [InlineKeyboardButton("💬 Tham gia Group", url="https://t.me/+vBZk4Kq59P9mMzY1")],
        [InlineKeyboardButton("👨‍💼 Chat với Admin", url="https://t.me/tuanai_mentor")],
        [InlineKeyboardButton("🔙 Quay lại", callback_data="setup_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"✅ Showed support menu to user {query.from_user.id}")
    except Exception as e:
        logger.error(f"❌ Failed to show support menu: {e}")


async def send_gentle_reminder(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    MESSAGE 4 (OPTIONAL): GENTLE FOLLOW-UP
    Sent 24 hours after Message 1 if user hasn't progressed
    """
    text = """👋 Nhắc nhẹ từ Freedom Wallet

Chỉ cần hoàn thành bước thiết lập đầu tiên,
bạn sẽ bắt đầu thấy dòng tiền của mình rõ ràng hơn.

Khi bạn sẵn sàng, mình ở đây để tiếp tục."""

    keyboard = [[InlineKeyboardButton("🛠 Tiếp tục thiết lập", callback_data="setup_start")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=reply_markup
        )
        logger.info(f"✅ Sent gentle reminder to user {user_id}")
    except Exception as e:
        logger.error(f"❌ Failed to send reminder to user {user_id}: {e}")


def register_unlock_handlers(application):
    """Register all unlock flow v3.0 callback handlers"""
    application.add_handler(CallbackQueryHandler(handle_unlock_continue, pattern="^unlock_continue$"))
    application.add_handler(CallbackQueryHandler(handle_unlock_status, pattern="^unlock_status$"))
    application.add_handler(CallbackQueryHandler(handle_setup_start, pattern="^setup_start$"))
    application.add_handler(CallbackQueryHandler(handle_view_roadmap, pattern="^view_roadmap$"))
    application.add_handler(CallbackQueryHandler(handle_webapp_guide, pattern="^webapp_guide$"))
    application.add_handler(CallbackQueryHandler(handle_setup_help, pattern="^setup_help$"))
    
    logger.info("✅ Unlock flow v3.0 handlers registered")
