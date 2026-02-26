"""
Admin Menu — Menu tập trung cho admin.

Command:
  /admin — Hiện toàn bộ lệnh admin dưới dạng menu đẹp
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from config.settings import settings

logger = logging.getLogger(__name__)

# ─── Kiểm tra admin ────────────────────────────────────────────────────────────
def _is_admin(user_id: int) -> bool:
    return settings.ADMIN_USER_ID and user_id == int(settings.ADMIN_USER_ID)


# ─── Menu chính ─────────────────────────────────────────────────────────────────
ADMIN_MENU_TEXT = (
    "🛡️ <b>FREEDOM WALLET — ADMIN PANEL</b>\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "Chọn nhóm lệnh bên dưới:"
)

def _main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Thống kê", callback_data="adm:stats"),
            InlineKeyboardButton("📤 Broadcast", callback_data="adm:broadcast"),
        ],
        [
            InlineKeyboardButton("💰 Thanh toán", callback_data="adm:payment"),
            InlineKeyboardButton("🔍 Gian lận", callback_data="adm:fraud"),
        ],
        [
            InlineKeyboardButton("🏥 Health", callback_data="adm:health"),
            InlineKeyboardButton("❌ Đóng", callback_data="adm:close"),
        ],
    ])


# ─── Sub-menu texts ───────────────────────────────────────────────────────────
MENUS = {
    "adm:stats": {
        "text": (
            "📊 <b>THỐNG KÊ & GIÁM SÁT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "• /broadcast_status — Số user đã đăng ký vs chưa setup\n"
            "• /admin_errors — Lỗi bot trong 24h qua\n"
            "• /healthcheck — Tình trạng bot ngay bây giờ\n"
            "• /fraud_stats — Thống kê gian lận\n"
            "• /payment_stats — Thống kê thanh toán"
        ),
        "back": "adm:main",
    },
    "adm:broadcast": {
        "text": (
            "📤 <b>BROADCAST — GỬI THÔNG BÁO</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "• /broadcast_status — Xem số user từng nhóm\n"
            "• /broadcast_setup — Preview tin nhắn setup Web App\n"
            "• /broadcast_setup confirm — <b>Gửi thật</b> tới user chưa setup\n"
            "• /broadcast_all confirm [tin] — Gửi tới TẤT CẢ user đã đăng ký\n\n"
            "⚠️ <i>broadcast_all dùng cẩn thận — không thể thu hồi</i>"
        ),
        "back": "adm:main",
    },
    "adm:payment": {
        "text": (
            "💰 <b>QUẢN LÝ THANH TOÁN</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "• /payment_pending — Danh sách chờ duyệt\n"
            "• /payment_approve [id] — Duyệt thanh toán\n"
            "• /payment_reject [id] [lý do] — Từ chối\n"
            "• /payment_stats — Báo cáo tổng hợp"
        ),
        "back": "adm:main",
    },
    "adm:fraud": {
        "text": (
            "🔍 <b>PHÁT HIỆN GIAN LẬN</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "• /fraud_queue — Hàng đợi cần review\n"
            "• /fraud_review [id] — Xem chi tiết case\n"
            "• /fraud_approve [id] — Bỏ qua (hợp lệ)\n"
            "• /fraud_reject [id] — Đánh dấu gian lận\n"
            "• /fraud_stats — Thống kê tổng hợp"
        ),
        "back": "adm:main",
    },
    "adm:health": {
        "text": (
            "🏥 <b>HEALTH MONITOR</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "• /healthcheck — Kiểm tra ngay trạng thái bot\n"
            "• /admin_errors — Lỗi được ghi nhận gần đây\n\n"
            "ℹ️ <i>Bot tự kiểm tra mỗi 5 phút. Nếu có ≥10 lỗi\n"
            "trong 10 phút, admin nhận cảnh báo tự động.</i>"
        ),
        "back": "adm:main",
    },
}

def _sub_keyboard(back_key: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Quay lại", callback_data=back_key)],
    ])


# ─── Handlers ─────────────────────────────────────────────────────────────────
async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: /admin"""
    user = update.effective_user
    if not user or not _is_admin(user.id):
        await update.message.reply_text("⛔ Chỉ admin mới dùng được lệnh này.")
        return

    await update.message.reply_text(
        ADMIN_MENU_TEXT,
        parse_mode="HTML",
        reply_markup=_main_keyboard(),
    )


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý các nút trong admin menu."""
    query = update.callback_query
    user = query.from_user

    if not _is_admin(user.id):
        await query.answer("⛔ Không có quyền.", show_alert=True)
        return

    await query.answer()
    data = query.data

    if data == "adm:close":
        await query.edit_message_text("✅ Admin panel đã đóng.")
        return

    if data == "adm:main":
        await query.edit_message_text(
            ADMIN_MENU_TEXT,
            parse_mode="HTML",
            reply_markup=_main_keyboard(),
        )
        return

    menu = MENUS.get(data)
    if menu:
        await query.edit_message_text(
            menu["text"],
            parse_mode="HTML",
            reply_markup=_sub_keyboard(menu["back"]),
        )
        return

    await query.answer("Không rõ lệnh.", show_alert=True)


# ─── Register ─────────────────────────────────────────────────────────────────
def register_admin_menu_handlers(application):
    """Đăng ký admin menu. Gọi TRƯỚC ConversationHandlers để có priority cao."""
    application.add_handler(
        CommandHandler("admin", handle_admin_menu),
        group=-10,  # Priority cao hơn mọi handler khác
    )
    application.add_handler(
        CallbackQueryHandler(handle_admin_callback, pattern=r"^adm:"),
        group=-10,
    )
    logger.info("✅ Admin menu handlers registered (group=-10)")
