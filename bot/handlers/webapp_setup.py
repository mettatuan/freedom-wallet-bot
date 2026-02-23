"""
Web App Setup Guide Handler - 6-step guide to create Freedom Wallet Web App
Based on Huong_dan_tao_wepapp.html

Must be completed BEFORE using the app
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ApplicationHandlerStop
from loguru import logger
from datetime import datetime
import os
import re
from bot.utils.database import get_user_by_id, SessionLocal, User, run_sync


def _get_user_urls_sync(user_id: int):
    """Return {'web_app_url': ..., 'google_sheets_url': ...} or None."""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return None
        return {
            'web_app_url': user.web_app_url,
            'google_sheets_url': user.google_sheets_url,
        }
    finally:
        db.close()


def _save_webapp_url_sync_ws(user_id: int, url: str) -> bool:
    """Save web_app_url for user. Returns True if user found, False otherwise."""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return False
        user.web_app_url = url
        db.commit()
        return True
    finally:
        db.close()


def _check_sheets_already_connected_sync(user_id: int) -> bool:
    """Return True if user already has google_sheets_url set."""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        return bool(user and user.google_sheets_url)
    finally:
        db.close()


def _save_sheets_url_sync_ws(user_id: int, url: str, spreadsheet_id: str) -> bool:
    """Save google_sheets_url + spreadsheet_id for user. Returns True if user found."""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return False
        user.google_sheets_url = url
        user.spreadsheet_id = spreadsheet_id
        user.sheets_connected_at = datetime.utcnow()
        db.commit()
        return True
    finally:
        db.close()

# Usage guide steps: shown after sheets connection
WEBAPP_USAGE_STEPS = {
    0: {
        "title": "� HƯỚNG DẪN SỬ DỤNG WEB APP (1/10)",
        "content": (
            "<b>🔐 BƯỚC 1: ĐĂNG NHẬP WEB APP</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Bấm <b>🌐 Mở Web App</b> bên dưới, khi thấy màn hình đăng nhập:\n\n"
            "👤 <b>Tên đăng nhập:</b> <code>Admin</code>\n"
            "🔑 <b>Mật khẩu:</b> <code>2369</code>\n\n"
            "<i>💡 Có thể đổi mật khẩu sau trong phần Cài đặt</i>"
        ),
        "image": "media/images/login.jpg"
    },
    1: {
        "title": "🧹 HƯỚNG DẪN SỬ DỤNG WEB APP (2/10)",
        "content": (
            "<b>🧹 BƯỚC 2: LÀM SẠCH DỮ LIỆU MẪU</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Web App có sẵn dữ liệu mẫu để minh họa. Vào tab <b>Cài đặt</b> → nhấn nút\n"
            "<b>🗑️ Xóa toàn bộ dữ liệu mẫu</b> → xác nhận → xong!\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<b>💡 Trong Cài đặt bạn cũng có thể:</b>\n"
            "• 🔑 Đổi mật khẩu đăng nhập (khuyến nghị đổi ngay)\n"
            "• 💱 Chọn đơn vị tiền tệ\n"
            "• 🎨 Chuyển giao diện sáng/tối\n\n"
            "<i>⚠️ Nếu không xóa, số liệu mẫu sẽ lẫn vào dữ liệu thật → báo cáo sai</i>"
        ),
        "image": "media/images/cai_dat.png"
    },
    2: {
        "title": "📊 HƯỚNG DẪN SỬ DỤNG WEB APP (3/10)",
        "content": (
            "<b>📊 BƯỚC 3: LẬP KẾ HOẠCH XÀI TIỀN + 5 CẤP BẬC TÀI CHÍNH</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Nhấn nút <b>⚙️ Thiết Lập Tính Toán</b> ở góc phải để bắt đầu.\n\n"
            "<b>1️⃣ Lập kế hoạch chi tiêu theo 6 hũ</b> — ví dụ thu nhập 35tr/tháng:\n"
            "• 🍚 Nhu cầu thiết yếu: Ăn uống 10tr · Nhà ở 10tr · Đi lại 2tr · Điện nước 1.5tr · Y tế 1.5tr\n"
            "• 📈 Tự do tài chính: Đầu tư Crypto 4tr\n"
            "• 📚 Giáo dục: Khóa học tài chính 2tr\n"
            "• 💰 Tiết kiệm dài hạn: Bảo hiểm nhân thọ 2tr\n"
            "• 🎮 Giải trí: Du lịch cuối tuần 1tr\n"
            "• 🎁 Cho đi: Giúp đỡ gia đình 1tr\n\n"
            "<b>2️⃣ Thiết lập công thức 5 cấp bậc tài chính:</b>\n"
            "• L1 - Đảm bảo: Thu nhập >= chi tiêu cơ bản × 1 tháng\n"
            "• L2 - An toàn: Tiết kiệm >= chi tiêu × 6 tháng\n"
            "• L3 - Độc lập: Tài sản >= (chi tiêu × 12) / 4%\n"
            "• L4 - Tự do: L3 × 5\n"
            "• L5 - Di sản: L4 × 5\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Sau khi điền xong → nhấn <b>💾 Lưu thiết lập</b>"
        ),
        "image": "media/images/5_cap_bac_tai_chinh.jpg"
    },
    3: {
        "title": "🏦 HƯỚNG DẪN SỬ DỤNG WEB APP (4/10)",
        "content": (
            "<b>🏦 BƯỚC 4: THIẾT LẬP TÀI KHOẢN</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Vào tab <b>Tài khoản</b> → thêm các tài khoản bạn đang dùng:\n\n"
            "• 💵 Tiền mặt\n"
            "• 💳 ATM / Tài khoản ngân hàng\n"
            "• 📱 Momo, ZaloPay, VNPay...\n"
            "• 💰 Tài khoản tiết kiệm\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<b>Quan trọng:</b> Điền <b>số dư thực tế hiện tại</b> của từng tài khoản\n"
            "<i>→ Đây là nền tảng để báo cáo chính xác!</i>"
        ),
        "image": "media/images/tai_khoan.jpg"
    },
    4: {
        "title": "🏷️ HƯỚNG DẪN SỬ DỤNG WEB APP (5/10)",
        "content": (
            "<b>🏷️ BƯỚC 5: THIẾT LẬP DANH MỤC</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Vào tab <b>Danh mục</b> để tùy chỉnh các nhóm thu chi:\n\n"
            "<b>Danh mục Chi phổ biến:</b>\n"
            "🍜 Ăn uống · 🚗 Đi lại · 🏠 Nhà ở · 💊 Sức khỏe · 🎮 Giải trí\n\n"
            "<b>Danh mục Thu phổ biến:</b>\n"
            "💼 Lương · 💹 Đầu tư · 🎁 Thưởng · 💸 Thu nhập phụ\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<i>💡 Có thể thêm danh mục tùy chỉnh theo thói quen chi tiêu của bạn</i>"
        ),
        "image": "media/images/danh_muc.jpg"
    },
    5: {
        "title": "🪣 HƯỚNG DẪN SỬ DỤNG WEB APP (6/10)",
        "content": (
            "<b>🪣 BƯỚC 6: HŨ TIỀN — THEO DÕI & PHÂN BỔ</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Vào tab <b>Hũ tiền</b> để xem số dư thực tế từng hũ và tiến độ so với kế hoạch.\n\n"
            "Mỗi lần ghi thu chi từ Telegram, bot tự động cập nhật số dư vào đúng hũ tương ứng.\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<b>⚙️ Tùy chỉnh Hũ tiền:</b>\n"
            "Nhấn nút <b>Cài đặt hũ tiền</b> để:\n"
            "• 🎨 Đổi màu sắc từng hũ theo ý thích\n"
            "• 📊 Thay đổi tỷ lệ % phân bổ\n"
            "• ✏️ Đổi tên hũ cho phù hợp\n"
            "• ➕ Thêm / bớt hũ tiền\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<i>💡 Điều chỉnh % theo thu nhập thực tế — không cần theo đúng công thức cứng nhắc</i>"
        ),
        "image": "media/images/hu_tien.jpg"
    },
    6: {
        "title": "🏠 HƯỚNG DẪN SỬ DỤNG WEB APP (7/10)",
        "content": (
            "<b>🏠 BƯỚC 7: THEO DÕI TÀI SẢN</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Vào tab <b>Tài sản</b> để theo dõi tổng tài sản ròng:\n\n"
            "• 🏠 Bất động sản\n"
            "• 🚗 Xe cộ, phương tiện\n"
            "• 📱 Thiết bị điện tử có giá trị\n"
            "• 💍 Trang sức, vàng\n"
            "• 📈 Cổ phiếu, quỹ đầu tư\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<i>💡 Cập nhật định kỳ để theo dõi sự tăng trưởng tài sản theo thời gian</i>"
        ),
        "image": "media/images/tai_san.jpg"
    },
    7: {
        "title": "💳 HƯỚNG DẪN SỬ DỤNG WEB APP (8/10)",
        "content": (
            "<b>💳 BƯỚC 8: QUẢN LÝ KHOẢN NỢ</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Vào tab <b>Khoản nợ</b> để theo dõi nợ vay và cho vay:\n\n"
            "• 🏦 <b>Nợ ngân hàng</b> — vay mua nhà, xe, tiêu dùng\n"
            "• 👥 <b>Nợ cá nhân</b> — mượn bạn bè, gia đình\n"
            "• 📅 <b>Hạn thanh toán</b> — nhắc nhở trả đúng hạn\n"
            "• 📊 <b>Tiến độ trả nợ</b> — % đã trả được\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<i>💡 Biết rõ tổng nợ giúp bạn lên kế hoạch trả nợ hiệu quả hơn</i>"
        ),
        "image": "media/images/khoan_no.jpg"
    },
    8: {
        "title": "📈 HƯỚNG DẪN SỬ DỤNG WEB APP (9/10)",
        "content": (
            "<b>📈 BƯỚC 9: THEO DÕI ĐẦU TƯ</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Vào tab <b>Đầu tư</b> để theo dõi danh mục đầu tư:\n\n"
            "• 📊 <b>Cổ phiếu</b> — VN-Index, cổ phiếu riêng lẻ\n"
            "• 🏦 <b>Tiết kiệm có kỳ hạn</b>\n"
            "• 🏠 <b>Bất động sản</b> cho thuê\n"
            "• 💰 <b>Vàng, ngoại tệ</b>\n"
            "• 🌐 <b>Crypto</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<i>💡 Theo dõi lợi nhuận/lỗ để đưa ra quyết định đầu tư đúng đắn</i>"
        ),
        "image": "media/images/dau_tu.jpg"
    },
    9: {
        "title": "🎉 HƯỚNG DẪN SỬ DỤNG WEB APP (10/10)",
        "content": (
            "<b>🎉 HƯỚNG DẪN NHANH — HOÀN THÀNH LỘ TRÌNH!</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "Chúc mừng bạn đã hoàn thành lộ trình hướng dẫn sử dụng Web App! 🏆\n\n"
            "<b>FreedomWalletBot</b> sẽ đồng hành và hỗ trợ bạn trong suốt hành trình tự do tài chính.\n"
            "Trân trọng biết ơn bạn đã tin tưởng và đồng hành 🙏\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<b>📲 Kết nối FreedomWalletBot để:</b>\n"
            "• ✍️ Ghi thu chi nhanh qua Telegram\n"
            "• 📊 Xem báo cáo tài chính tức thì\n"
            "• ⏰ Nhận nhắc nhở chi tiêu thông minh\n\n"
            "<b>🌐 Tham gia Cộng đồng Freedom Wallet:</b>\n"
            "👉 <a href=\"https://t.me/freedomwalletapp\">t.me/freedomwalletapp</a> — kiến tạo cộng đồng Tự do tài chính\n\n"
            "<b>💎 Tham gia cộng đồng Giàu Toàn Diện:</b>\n"
            "👉 <a href=\"https://t.me/giautoandien\">t.me/giautoandien</a>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "<b>⚡ THÊM VÀO HOME SCREEN:</b>\n"
            "📱 <b>iOS:</b> Safari → Chia sẻ → <b>Add to Home Screen</b>\n"
            "🤖 <b>Android:</b> Chrome → Menu → <b>Add to Home screen</b>\n"
            "💻 <b>Máy tính:</b> <b>Ctrl+D</b> để bookmark\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "🎉 <b>Bạn đã sẵn sàng sử dụng Freedom Wallet!</b>\n"
            "<i>Cần hỗ trợ? Liên hệ @tuanai_mentor</i>"
        ),
        "image": "media/images/cai_dat.png"
    }
}


async def send_webapp_usage_step(update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
    """Send a usage guide step with navigation"""
    total = len(WEBAPP_USAGE_STEPS)
    if step not in WEBAPP_USAGE_STEPS:
        if update.callback_query:
            await update.callback_query.answer("❌ Bước không hợp lệ!")
        return

    step_data = WEBAPP_USAGE_STEPS[step]

    # Fetch user's saved URLs for quick-open buttons
    user_id = update.effective_user.id
    web_app_url = None
    sheets_url = None
    try:
        urls = await run_sync(_get_user_urls_sync, user_id)
        if urls:
            web_app_url = urls['web_app_url']
            sheets_url = urls['google_sheets_url']
    except Exception:
        pass

    # Build buttons
    buttons = []

    # Row 1: quick-open links (only if user has them)
    link_row = []
    if web_app_url:
        link_row.append(InlineKeyboardButton("🌐 Mở Web App", url=web_app_url))
    if sheets_url:
        link_row.append(InlineKeyboardButton("📋 Mở Google Sheets", url=sheets_url))
    if link_row:
        buttons.append(link_row)

    is_last_step = (step == total - 1)

    if is_last_step:
        # Last step: action buttons + back + guide menu
        buttons.append([
            InlineKeyboardButton("✍️ Ghi thu chi", callback_data="webapp_record_guide"),
            InlineKeyboardButton("📊 Xem báo cáo", callback_data="reminder_view_report")
        ])
        buttons.append([
            InlineKeyboardButton("⬅️ Quay lại", callback_data=f"webapp_usage_step_{step-1}"),
            InlineKeyboardButton("📘 Hướng dẫn", callback_data="show_guide_menu")
        ])
    else:
        # Row 2: navigation
        nav = []
        if step > 0:
            nav.append(InlineKeyboardButton("⬅️ Quay lại", callback_data=f"webapp_usage_step_{step-1}"))
        if step < total - 1:
            nav.append(InlineKeyboardButton("Tiếp theo ➡️", callback_data=f"webapp_usage_step_{step+1}"))
        if nav:
            buttons.append(nav)

        # Row 3: menu (always shown)
        buttons.append([InlineKeyboardButton("📱 Menu chính", callback_data="show_main_menu")])

    keyboard = InlineKeyboardMarkup(buttons) if buttons else None
    
    title = step_data["title"]
    content = step_data["content"]
    message_text = f"{title}\n\n{content}"
    image_path = step_data.get("image")
    
    try:
        if update.callback_query:
            await update.callback_query.answer()
            if image_path and os.path.exists(image_path):
                await update.callback_query.message.delete()
                with open(image_path, "rb") as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=message_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
            else:
                if update.callback_query.message.photo:
                    await update.callback_query.message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                else:
                    await update.callback_query.edit_message_text(
                        text=message_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
        else:
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=message_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
            else:
                await update.message.reply_text(
                    message_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        logger.info(f"Sent webapp usage step {step} to user {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error sending usage step {step}: {e}")


# Web App Setup Guide Content - 6 Steps (0-5)
WEBAPP_SETUP_STEPS = {
    0: {
        "title": "🚀 TẠO WEB APP (TÙY CHỌN)",
        "content": """
👋 <b>Hướng dẫn tạo Web App - Data ownership layer</b>

━━━━━━━━━━━━━━━━━━━━━

<b>💡 WEB APP LÀ GÌ?</b>

Web App là OPTIONAL (tùy chọn) - chỉ cần nếu bạn muốn:
✅ Sở hữu 100% dữ liệu trong Google Drive riêng
✅ Xem dashboard trực quan
✅ Xuất Excel bất kỳ lúc nào

<b>❌ KHÔNG CẦN WEB APP để:</b>
• Ghi giao dịch (dùng Telegram bot)
• Xem số dư &amp; streak (dùng Telegram)
• Nhận insight &amp; reminder (dùng Telegram)

━━━━━━━━━━━━━━━━━━━━━

<b>🎯 HƯỚNG DẪN TẠO WEB APP</b>

Nếu bạn muốn data ownership layer:
1️⃣ Tạo bản sao Google Sheets Template
2️⃣ Mở Extensions → App Script
3️⃣ Deploy Web App của riêng bạn
4️⃣ Mở &amp; Authorize lần đầu

━━━━━━━━━━━━━━━━━━━━━

<b>✅ SAU KHI HOÀN THÀNH:</b>
• Web App cá nhân (data trong Drive của bạn)
• Telegram tự động đồng bộ
• Dashboard trực quan mọi lúc

━━━━━━━━━━━━━━━━━━━━━

<b>⏱ THỜI GIAN</b>: 10-15 phút
<b>📱 THIẾT BỊ</b>: Desktop/Laptop (khuyến nghị)
<b>🔗 CẦN</b>: Tài khoản Google

💡 <i>Telegram bot hoạt động hoàn hảo không cần Web App!</i>
""",
        "image": None
    },
    
    1: {
        "title": "📋 BƯỚC 1: TẠO BẢN SAO TEMPLATE",
        "content": """
<b>📋 CÁCH LÀM:</b>

1️⃣ Click <b>"📑 Copy Template"</b> bên dưới

2️⃣ Popup "Make a copy" hiện ra

3️⃣ Đổi tên (hoặc giữ nguyên) → Click <b>"Make a copy"</b>

━━━━━━━━━━━━━━━

<b>✅ KẾT QUẢ:</b>
• Bản sao riêng trong Google Drive
• File thuộc về BẠN (100% riêng tư)

━━━━━━━━━━━━━━━

<b>❓ LỖI:</b>
• "You need access" → Đăng nhập Google
• Không copy được → Thử Chrome
• Cần trợ giúp → @tuanai_mentor

💡 <b>Sau khi copy xong, không đóng tab! Chuyển sang Bước 2 ngay.</b>
""",
        "image": "docs/make-copy.png"
    },
    
    2: {
        "title": "⚙️ BƯỚC 2: MỞ APP SCRIPT",
        "content": """
<b>📋 CÁCH LÀM:</b>

1️⃣ Trong file Sheets vừa copy → Menu trên cùng

2️⃣ Click <b>"Extensions"</b> (Tiện ích mở rộng)

3️⃣ Chọn <b>"Apps Script"</b>

4️⃣ Tab mới mở → Code Editor
   • Thấy file <code>Code.gs</code> với nhiều code
   • <b>KHÔNG CẦN ĐỌC/SỬA GÌ!</b>

━━━━━━━━━━━━━━━

<b>✅ KẾT QUẢ:</b>
• Đang ở Apps Script Editor
• URL dạng: <code>script.google.com/...</code>
• Sẵn sàng Deploy (Bước 3)

━━━━━━━━━━━━━━━

<b>❓ Không thấy Extensions?</b>
• Refresh trang
• Hoặc nhấn <code>Alt + /</code> → gõ "Apps Script"

💡 <b>Đừng sợ code! Bạn không cần động vào gì cả.</b>
""",
        "image": "docs/app-script.png"
    },
    
    3: {
        "title": "🚀 BƯỚC 3: DEPLOY WEB APP",
        "content": """
<b>📋 CÁCH LÀM:</b>

1️⃣ Apps Script Editor → Click <b>"Deploy"</b> (góc phải) → <b>"New deployment"</b>

2️⃣ Click ⚙️ → Chọn <b>"Web app"</b>

3️⃣ Cấu hình:
• <b>Execute as</b>: <b>"Me"</b>
• <b>Who has access</b>: <b>"Anyone"</b>

4️⃣ Click <b>"Deploy"</b>

5️⃣ Copy <b>Web App URL</b> → <b>LƯU LẠI!</b>

━━━━━━━━━━━━━━━

<b>✅ KẾT QUẢ:</b>
• Có Web App URL riêng
• Sẵn sàng mở lần đầu

━━━━━━━━━━━━━━━

<b>💡 Lưu URL này để sử dụng sau!</b>
""",
        "image": "docs/deploy-app.png"
    },
    
    4: {
        "title": "🔐 BƯỚC 4: MỞ WEB APP & ĐĂNG NHẬP",
        "content": """
<b>📋 CÁCH LÀM:</b>

1️⃣ Mở <b>Web App URL</b> (vừa copy ở Bước 3)

2️⃣ <b>Authorize lần đầu:</b>

→ Popup "Authorization required"
→ Click <b>"Authorize access"</b>
→ Chọn tài khoản Google
→ Thấy "Google hasn't verified this app"
→ Click <b>"Advanced"</b> (Nâng cao)
→ Click <b>"Go to [Project name] (unsafe)"</b>
→ Click <b>"Allow"</b> (Cho phép)

━━━━━━━━━━━━━━━

<b>✅ KẾT QUẢ:</b>
• Web App mở thành công
• Đã có quyền truy cập Google Sheets
• Sẵn sàng sử dụng!

━━━━━━━━━━━━━━━

<b>❓ TẠI SAO "UNSAFE"?</b>

Không sao! Đây là app CỦA BẠN:
• Bạn tự tạo
• Dữ liệu trong Drive của bạn
• Google chỉ cảnh báo vì chưa verify
• 100% an toàn!

━━━━━━━━━━━━━━━

<b>💡 Sau lần đầu → không cần authorize lại!</b>
""",
        "image": "docs/use-deploy-app.png"
    },
    
    5: {
        "title": "✅ HOÀN THÀNH: TẠO WEB APP!",
        "content": """
🎉 <b>XUẤT SẮC! Đã tạo xong Freedom Wallet Web App!</b>

━━━━━━━━━━━━━━━

<b>✅ HOÀN THÀNH:</b>
• Google Sheets Template riêng
• Web App cá nhân đã authorize
• URL truy cập mọi lúc

━━━━━━━━━━━━━━━

<b>💡 MẸO:</b>

📱 <b>Điện thoại:</b> Thêm vào Home Screen
• iOS: Safari → Share → Add to Home Screen
• Android: Chrome → Menu → Add to Home screen

💻 <b>Máy tính:</b> Bookmark (Ctrl+D)

━━━━━━━━━━━━━━━

<b>🚀 TIẾP THEO: KẾT NỐI VỚI BOT</b>

💡 Ghi nhanh thu chi từ Telegram!

👉 <b>Nhấn "Tiếp theo" để xem!</b>
""",
        "image": None
    },
    
    6: {
        "title": "🤖 KẾT NỐI API VỚI TELEGRAM BOT",
        "content": """
💰 <b>SIÊU TIỆN LỢI: GHI NHANH TỪ TELEGRAM!</b>

Sau khi kết nối, bạn có thể:

✅ <b>Ghi thu/chi trong 10 giây:</b>
• Không cần mở Google Sheets
• Không cần mở Web App
• Chat với bot là xong!

✅ <b>Xem báo cáo nhanh:</b>
• Số dư các tài khoản
• Thu chi hôm nay/tháng
• Ngay trong Telegram!

✅ <b>Sử dụng menu nhanh:</b>
• Keyboard menu tiện lợi
• 1 phím là ghi ngay

━━━━━━━━━━━━━━━

<b>📋 CÁCH KẾT NỐI:</b>

1️⃣ Copy <b>Web App URL</b> (từ Bước 3)

2️⃣ Bấm nút <b>"📱 Kết nối ngay"</b> bên dưới

3️⃣ Paste URL vào chat → Gửi

4️⃣ Xong! Bot tự động kết nối!

━━━━━━━━━━━━━━━

<b>🔒 AN TOÀN:</b>
• URL chỉ bạn có
• Chỉ bạn truy cập được
• Không ai thấy dữ liệu của bạn

━━━━━━━━━━━━━━━

<b>💡 Chưa muốn kết nối ngay?</b>

→ Bấm "Bỏ qua" để học cách dùng trước
→ Kết nối sau tại Menu → ⚙️ Cài đặt
""",
        "image": None
    }
}


def get_webapp_setup_keyboard(current_step: int) -> InlineKeyboardMarkup:
    """Generate navigation keyboard for webapp setup guide"""
    buttons = []
    
    # Special handling for step 1 - add Copy Template button
    if current_step == 1:
        buttons.append([
            InlineKeyboardButton(
                "📑 Copy Template", 
                url=f"https://docs.google.com/spreadsheets/d/{os.getenv('TEMPLATE_SPREADSHEET_ID', '1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI')}/copy"
            )
        ])
    
    # Navigation row
    nav_row = []
    if current_step > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Quay lại", callback_data=f"webapp_step_{current_step-1}"))
    
    if current_step < 6:
        nav_row.append(InlineKeyboardButton("Tiếp theo ➡️", callback_data=f"webapp_step_{current_step+1}"))
    
    if nav_row:
        buttons.append(nav_row)
    
    # Menu row
    menu_row = []
    if current_step != 0:
        menu_row.append(InlineKeyboardButton("📱 Menu", callback_data="webapp_step_0"))
    
    # Step 6 (API connection) - add special buttons
    if current_step == 6:
        buttons.append([
            InlineKeyboardButton("📱 Kết nối ngay", callback_data="connect_webapp_start")
        ])
        buttons.append([
            InlineKeyboardButton("⏭ Bỏ qua, học cách dùng", callback_data="webapp_usage_step_0")
        ])
        buttons.append([
            InlineKeyboardButton("💬 Cần trợ giúp?", url="https://t.me/tuanai_mentor")
        ])
    # Step 5 (completion) - continue button
    elif current_step == 5:
        buttons.append([
            InlineKeyboardButton("💬 Cần trợ giúp?", url="https://t.me/tuanai_mentor")
        ])
    else:
        # Help row (for steps 0-4)
        if menu_row:
            buttons.append(menu_row)
        buttons.append([
            InlineKeyboardButton("💬 Cần trợ giúp?", url="https://t.me/tuanai_mentor")
        ])
    
    return InlineKeyboardMarkup(buttons)


async def send_webapp_setup_step(update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
    """Send a specific webapp setup step"""
    try:
        if step not in WEBAPP_SETUP_STEPS:
            await update.callback_query.answer("❌ Bước không hợp lệ!")
            return
        
        step_data = WEBAPP_SETUP_STEPS[step]
        keyboard = get_webapp_setup_keyboard(step)
        
        message_text = f"{step_data['title']}\n\n{step_data['content']}"
        
        # Handle image + text combination
        if step_data.get('image'):
            # If there's an image, we need to delete old message and send new photo message
            if update.callback_query:
                # Delete the old message
                await update.callback_query.message.delete()
                
                # Send new photo message
                with open(step_data['image'], 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=message_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
                await update.callback_query.answer()
            else:
                # Command: send photo directly
                with open(step_data['image'], 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=message_text,
                        parse_mode="HTML",
                        reply_markup=keyboard
                    )
        else:
            # No image, just text
            if update.callback_query:
                # Check if previous message was a photo
                if update.callback_query.message.photo:
                    # Previous was photo, need to delete and send new text message
                    await update.callback_query.message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message_text,
                        parse_mode="HTML",
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
                    await update.callback_query.answer()
                else:
                    # Previous was text, can edit
                    await update.callback_query.edit_message_text(
                        text=message_text,
                        parse_mode="HTML",
                        reply_markup=keyboard,
                        disable_web_page_preview=True
                    )
                    await update.callback_query.answer()
            else:
                await update.message.reply_text(
                    text=message_text,
                    parse_mode="HTML",
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
        
        logger.info(f"Sent webapp setup step {step} to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending webapp setup step {step}: {e}")
        if update.callback_query:
            await update.callback_query.answer("❌ Có lỗi xảy ra!")


async def taoweb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /taoweb command"""
    await send_webapp_setup_step(update, context, step=0)


async def webapp_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle webapp setup navigation callbacks"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        if callback_data.startswith("webapp_usage_step_"):
            step = int(callback_data.split("_")[-1])
            await send_webapp_usage_step(update, context, step)
        
        elif callback_data == "show_main_menu":
            await query.answer()
            from bot.core.keyboard import get_main_keyboard
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="📱 <b>MENU CHÍNH</b>\n\nDùng keyboard bên dưới để truy cập nhanh:",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )

        elif callback_data == "webapp_record_guide":
            await query.answer()
            text = (
                "✍️ <b>GHI THU CHI NHANH QUA FREEDOMWALLETBOT</b>\n\n"
                "━━━━━━━━━━━━━━━\n\n"
                "<b>Cách 1 — Nhắn tin tự nhiên:</b>\n"
                "Chỉ cần gõ vào chat bot, ví dụ:\n"
                "• <code>cà phê 35k</code>\n"
                "• <code>ăn sáng 50k ăn uống</code>\n"
                "• <code>lương tháng 15tr thu nhập</code>\n"
                "• <code>+500k tiền lãi</code>\n\n"
                "Bot tự nhận diện số tiền, danh mục, hũ tiền → đồng bộ sang Google Sheets ngay lập tức.\n\n"
                "━━━━━━━━━━━━━━━\n\n"
                "<b>Cách 2 — Dùng nút 💰 Ghi thu chi trên menu:</b>\n"
                "Nhấn nút <b>💰 Ghi thu chi</b> ở bàn phím bên dưới → chọn loại → nhập số tiền.\n\n"
                "━━━━━━━━━━━━━━━\n\n"
                "<i>💡 Mẹo: Ghi ngay khi vừa chi để không quên!</i>"
            )
            back_keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Quay lại", callback_data="webapp_usage_step_9")
            ]])
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                parse_mode="HTML",
                reply_markup=back_keyboard
            )

        elif callback_data == "show_guide_menu":
            await query.answer()
            guide_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🏗️ Tạo Web App", callback_data="webapp_step_0")],
                [InlineKeyboardButton("🤖 Kết nối Telegram Bot", callback_data="connect_webapp_start")],
                [InlineKeyboardButton("📖 Sử dụng Web App", callback_data="webapp_usage_step_0")],
                [InlineKeyboardButton("⬅️ Quay lại", callback_data="webapp_usage_step_9")]
            ])
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="📘 <b>HƯỚNG DẪN</b>\n\nChọn phần bạn muốn xem:",
                parse_mode="HTML",
                reply_markup=guide_keyboard
            )

        elif callback_data.startswith("webapp_step_"):
            step = int(callback_data.split("_")[-1])
            await send_webapp_setup_step(update, context, step)
        
        elif callback_data == "connect_webapp_start":
            # User clicked "Kết nối ngay"
            await query.answer()
            await query.message.delete()
            
            # Set state to waiting for URL
            context.user_data['waiting_for_webapp_url'] = True
            
            message = """
🔗 <b>PASTE WEB APP URL CỦA BẠN</b>

━━━━━━━━━━━━━━━

<b>📋 CÁCH LẤY URL:</b>

1️⃣ Quay lại <b>Bước 3</b> trong hướng dẫn
2️⃣ Trong Apps Script, bấm <b>"Deploy"</b>
3️⃣ Bấm <b>"Manage deployments"</b>
4️⃣ Copy <b>Web App URL</b>

━━━━━━━━━━━━━━━

<b>📌 URL SẼ CÓ DẠNG:</b>

<code>https://script.google.com/macros/s/ABC...XYZ/exec</code>

━━━━━━━━━━━━━━━

👉 <b>Paste URL vào đây và gửi!</b>

<i>Hoặc gõ /cancel để hủy</i>
"""
            
            # Add back button
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("🔙 Quay lại bước trước", callback_data="webapp_step_3")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send illustration image
            from pathlib import Path
            image_path = Path("media/images/buoc-4-completed.jpg")
            
            try:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(image_path, "rb"),
                    caption=message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error sending illustration image: {e}")
                # Fallback: send text only
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            
            logger.info(f"User {update.effective_user.id} started webapp URL connection")
        
    except Exception as e:
        logger.error(f"Error in webapp callback handler: {e}")
        await query.answer("❌ Có lỗi xảy ra!")


async def handle_webapp_url_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user sending Web App URL or Google Sheets URL (dispatcher for group=-1)"""
    
    # If waiting for Sheets URL, delegate to sheets handler
    if context.user_data.get('waiting_for_sheets_url'):
        return await handle_sheets_url_message(update, context)
    
    url = update.message.text.strip()
    url_pattern = r'^https://script\.google\.com/macros/s/[\w-]+/exec$'
    is_webapp_url = bool(re.match(url_pattern, url))
    sheets_pattern = r'^https://docs\.google\.com/spreadsheets/d/'
    is_sheets_url = bool(re.match(sheets_pattern, url))

    # Auto-detect: if user sends a webapp/sheets URL without prior state (e.g. after bot restart)
    if not context.user_data.get('waiting_for_webapp_url'):
        if is_webapp_url:
            # Treat as if they were waiting for webapp URL
            context.user_data['waiting_for_webapp_url'] = True
        elif is_sheets_url:
            context.user_data['waiting_for_sheets_url'] = True
            return await handle_sheets_url_message(update, context)
        else:
            return  # Not a URL, let other handlers process it
    
    user_id = update.effective_user.id
    
    if not re.match(url_pattern, url):
        await update.message.reply_text(
            "❌ <b>URL không đúng định dạng!</b>\n\n"
            "URL phải có dạng:\n"
            "<code>https://script.google.com/macros/s/ABC...XYZ/exec</code>\n\n"
            "Vui lòng kiểm tra lại và gửi lại URL!",
            parse_mode="HTML"
        )
        logger.warning(f"User {user_id} sent invalid webapp URL: {url[:100]}")
        raise ApplicationHandlerStop  # Stop other handlers
    
    # Save URL to database
    try:
        user_found = await run_sync(_save_webapp_url_sync_ws, user_id, url)
        
        if user_found:
            # Clear Web App URL waiting state
            context.user_data['waiting_for_webapp_url'] = False
            
            # Ask for Google Sheets URL next
            context.user_data['waiting_for_sheets_url'] = True
            
            await update.message.reply_text(
                "✅ <b>ĐÃ CẬP NHẬT WEB APP URL!</b>\n\n"
                "━━━━━━━━━━━━━━━\n\n"
                "📑 <b>BƯỚC 2: KẾT NỐI GOOGLE SHEETS</b>\n\n"
                "<b>🌟 LỢI ÍCH:</b>\n\n"
                "• 🔁 <b>Cập nhật tức thì:</b> Giao dịch từ Telegram → Google Sheets ngay lập tức\n"
                "• 📱 <b>Xem mọi lúc, mọi nơi:</b> Mở Sheets trên điện thoại hoặc máy tính bất kỳ lúc nào\n"
                "• 🔒 <b>Mở Google Sheet:</b> nhanh chóng ngay trong Bot\n\n"
                "━━━━━━━━━━━━━━━\n\n"
                "<b>📝 CÁCH LẤY LINK GOOGLE SHEETS:</b>\n\n"
                "1️⃣ Mở file Google Sheets bạn đã tạo khi làm Web App\n"
                "2️⃣ Copy link trên thanh địa chỉ trình duyệt\n\n"
                "<i>💡 Link có dạng: https://docs.google.com/spreadsheets/d/...</i>\n\n"
                "━━━━━━━━━━━━━━━\n\n"
                "👉 <b>Gửi link Google Sheets của bạn ngay bây giờ!</b>\n\n"
                "<i>Hoặc nhấn /cancel để bỏ qua bước này</i>",
                parse_mode="HTML"
            )
            
            logger.info(f"✅ Saved webapp URL for user {user_id}, asking for Sheets URL")
        else:
            await update.message.reply_text(
                "❌ Không tìm thấy tài khoản. Vui lòng /start lại!"
            )
            context.user_data['waiting_for_webapp_url'] = False
            
    except Exception as e:
        logger.error(f"Error saving webapp URL for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ Có lỗi khi lưu URL. Vui lòng thử lại!"
        )
        context.user_data['waiting_for_webapp_url'] = False
    
    # CRITICAL: Stop propagation to prevent message handler from processing URL as transaction
    raise ApplicationHandlerStop


async def handle_sheets_url_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user sending Google Sheets URL"""
    
    user_id = update.effective_user.id
    url = update.message.text.strip() if update.message and update.message.text else ""
    
    # Validate URL format - Google Sheets URL
    sheets_pattern = r'^https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
    is_sheets_url = bool(re.match(sheets_pattern, url))
    
    # Check if we're waiting for Sheets URL from this user
    # Also handle case where bot restarted and context state was lost — if user sends a
    # Sheets URL we should process it rather than letting it fall through to transaction handler
    if not context.user_data.get('waiting_for_sheets_url') and not is_sheets_url:
        return
    
    # If this looks like a sheets URL but state was lost, recover gracefully
    if not context.user_data.get('waiting_for_sheets_url') and is_sheets_url:
        # Check if user already has a sheets URL connected
        already_connected = await run_sync(_check_sheets_already_connected_sync, user_id)
        if already_connected:
            # Already connected — this was probably an accidental resend, ignore
            raise ApplicationHandlerStop
        # Otherwise treat as if they're setting it up
    match = re.match(sheets_pattern, url)
    
    if not match:
        await update.message.reply_text(
            "❌ <b>URL không đúng định dạng!</b>\n\n"
            "URL phải có dạng:\n"
            "<code>https://docs.google.com/spreadsheets/d/ABC.../edit</code>\n\n"
            "Vui lòng kiểm tra lại và gửi lại URL!",
            parse_mode="HTML"
        )
        logger.warning(f"User {user_id} sent invalid sheets URL: {url[:100]}")
        raise ApplicationHandlerStop
    
    # Extract spreadsheet ID
    spreadsheet_id = match.group(1)
    
    # Save URL to database
    try:
        user_found = await run_sync(_save_sheets_url_sync_ws, user_id, url, spreadsheet_id)
        
        if user_found:
            # Clear waiting state
            context.user_data['waiting_for_sheets_url'] = False
            
            # Show success message with quick menu keyboard AND guide
            await show_quick_menu_keyboard(update, context, first_time=True, sheets_connected=True)
            
            logger.info(f"✅ Saved Google Sheets URL for user {user_id} (ID: {spreadsheet_id})")
        else:
            await update.message.reply_text(
                "❌ Không tìm thấy tài khoản. Vui lòng /start lại!"
            )
            context.user_data['waiting_for_sheets_url'] = False
            
    except Exception as e:
        logger.error(f"Error saving Sheets URL for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ Có lỗi khi lưu URL. Vui lòng thử lại!"
        )
        context.user_data['waiting_for_sheets_url'] = False
    
    # CRITICAL: Stop propagation
    raise ApplicationHandlerStop

async def show_quick_menu_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, first_time: bool = False, sheets_connected: bool = False):
    """Show quick access keyboard menu"""
    
    # Use the canonical unified keyboard (same as all other entry points)
    from bot.core.keyboard import get_main_keyboard
    reply_markup = get_main_keyboard()
    
    if sheets_connected:
        # Special message after connecting Google Sheets
        message = (
            "🎊 <b>CHÚC MỪNG! HOÀN TẤT KẾT NỐI!</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "✅ Web App URL đã kết nối\n"
            "✅ Google Sheets đã kết nối\n"
            "✅ Hệ thống sẵn sàng 100%\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "⚠️ <b>TRƯỚC KHI SỬ DỤNG — LÀM SẠCH DỮ LIỆU MẪU</b>\n\n"
            "Khi bạn tạo Web App từ template, Google Sheets của bạn có sẵn <b>dữ liệu mẫu</b> "
            "(giao dịch, số dư giả) để minh họa cách hoạt động.\n\n"
            "Nếu không xóa, các con số này sẽ <b>lẫn vào dữ liệu thật</b> của bạn "
            "→ báo cáo sai, số dư không chính xác.\n\n"
            "👉 Bước đầu tiên: <b>Đăng nhập Web App → Xóa dữ liệu mẫu → Nhập số dư thực tế</b>\n\n"
            "━━━━━━━━━━━━━━━\n\n"
            "📖 Nhấn nút bên dưới để xem hướng dẫn từng bước 👇"
        )

        # Inline menu: ONLY 1 button
        inline_keyboard = [
            [InlineKeyboardButton("📖 Xem Hướng dẫn sử dụng Web App ngay", callback_data="webapp_usage_step_0")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

        await update.message.reply_text(
            "👇 <b>Xem Hướng dẫn sử dụng Web App ngay:</b>",
            parse_mode="HTML",
            reply_markup=inline_markup
        )

        logger.info(f"Showed post-connection guide to user {update.effective_user.id}")
        return
    
    if first_time:
        message = """
🎉 <b>KẾT NỐI THÀNH CÔNG!</b>

━━━━━━━━━━━━━━━

✅ Đã lưu Web App URL
✅ Sẵn sàng ghi nhanh thu chi
✅ Sẵn sàng kết nối Google Sheets

━━━━━━━━━━━━━━━

<b>🚀 BẮT ĐẦU SỬ DỤNG:</b>

• <b>💰 Ghi thu chi:</b> 1 phím → 10 giây xong
• <b>🌐 Mở Web Apps:</b> Giao diện đầy đủ
• <b>📋 Mở Sheets:</b> Kết nối Google Sheets
• <b>📈 Báo cáo:</b> Phân tích thu chi

━━━━━━━━━━━━━━━

<b>💡 MẸO:</b> Dùng keyboard bên dưới để truy cập nhanh!
"""
        
        # Add inline menu for first-time setup
        inline_keyboard = [
            [InlineKeyboardButton("📖 Hướng dẫn tạo Web App", callback_data="webapp_step_0")],
            [InlineKeyboardButton("🔗 Hướng dẫn kết nối Google Sheets", callback_data="webapp_step_0")],
            [InlineKeyboardButton("🎯 Hướng dẫn sử dụng Web Apps", url="https://t.me/tuanai_mentor")]
        ]
        inline_markup = InlineKeyboardMarkup(inline_keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        await update.message.reply_text(
            "📚 <b>HƯỚNG DẪN SỬ DỤNG</b>\n\n"
            "Chọn hướng dẫn bạn cần:",
            parse_mode="HTML",
            reply_markup=inline_markup
        )
        
        logger.info(f"Showed quick menu keyboard to user {update.effective_user.id}")
        return
    else:
        message = """
📱 <b>MENU NHANH</b>

Sử dụng keyboard bên dưới để:

💰 Ghi thu/chi nhanh
📊 Xem số dư & báo cáo
📋 Mở Google Sheets
⚙️ Cài đặt tài khoản
"""
    
    await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    
    logger.info(f"Showed quick menu keyboard to user {update.effective_user.id}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any ongoing operation"""
    if context.user_data.get('waiting_for_webapp_url'):
        context.user_data['waiting_for_webapp_url'] = False
        await update.message.reply_text(
            "✅ Đã hủy kết nối Web App.\n\n"
            "Bạn có thể kết nối sau tại:\n"
            "Gõ /taoweb"
        )
        logger.info(f"User {update.effective_user.id} cancelled webapp URL connection")
    elif context.user_data.get('waiting_for_sheets_url'):
        context.user_data['waiting_for_sheets_url'] = False
        await update.message.reply_text(
            "✅ Đã bỏ qua kết nối Google Sheets.\n\n"
            "Bạn vẫn có thể sử dụng bot bình thường.\n"
            "Muốn kết nối sau, gõ /taoweb"
        )
        # Show keyboard menu anyway
        await show_quick_menu_keyboard(update, context, first_time=False)
        logger.info(f"User {update.effective_user.id} skipped sheets URL connection")
    elif context.user_data.get('awaiting_settings'):
        context.user_data.pop('awaiting_settings', None)
        await update.message.reply_text("❌ Đã huỷ.")
    else:
        await update.message.reply_text("Không có thao tác nào để hủy.")


async def handle_keyboard_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Pure router for OLD keyboard buttons.
    All business logic lives in transaction.py — change only ONE place!

    Old keyboard routing:
      💰 Ghi thu chi    → falls through → handle_quick_transaction (group=0)
      🌐 Mở Web Apps   → handle_open_webapp
      📋 Mở Google Sheets → handle_open_sheets
      📈 Báo cáo       → handle_report_menu
      � Chia sẻ       → falls through → handle_share (group=0)
      💝 Đóng góp      → handle_donate
      📘 Hướng dẫn     → handle_guide_menu
      💬 Trợ giúp      → handle_help
    """
    from bot.handlers.transaction import (
        handle_record_button,
        handle_open_webapp, handle_open_sheets, handle_report_menu,
        handle_donate, handle_guide_menu, handle_help,
    )

    text = update.message.text.strip()

    # Old button text → centralized handler in transaction.py
    # "🔗 Chia sẻ" (corrupted old emoji) not listed → falls through to handle_share (group=0)
    OLD_BUTTON_HANDLERS = {
        "💰 Ghi thu chi":       handle_record_button,   # ← FIX: was falling to quick_transaction
        "🌐 Mở Web Apps":       handle_open_webapp,
        "📋 Mở Google Sheets":  handle_open_sheets,
        "📈 Báo cáo":           handle_report_menu,
        "💝 Đóng góp":          handle_donate,
        "📘 Hướng dẫn":         handle_guide_menu,
        "💬 Trợ giúp":          handle_help,
    }

    handler = OLD_BUTTON_HANDLERS.get(text)
    if handler is None:
        return  # not our button, or chia sẻ (falls through to handle_share group=0)

    await handler(update, context)
    raise ApplicationHandlerStop  # belt-and-suspenders (handlers raise internally too)



def register_webapp_setup_handlers(application):
    """Register all webapp setup handlers"""
    application.add_handler(CommandHandler("taoweb", taoweb_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    application.add_handler(CallbackQueryHandler(webapp_callback_handler, pattern="^webapp_|^connect_webapp|^show_main_menu$|^show_guide_menu$"))
    
    # Handler for keyboard menu buttons - HIGHEST PRIORITY
    # Must run BEFORE webapp URL handler and quick_record
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_keyboard_menu
        ),
        group=-2  # Highest priority
    )
    
    # Handler for receiving webapp URL - MUST run BEFORE quick_record (group=0)
    # Use group=-1 to ensure it checks when waiting_for_webapp_url is True
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_webapp_url_message
        ),
        group=-1  # Higher priority than quick_record (group=0)
    )
    
    # Handler for receiving Google Sheets URL - Same priority as webapp URL
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_sheets_url_message
        ),
        group=-1  # Higher priority than quick_record (group=0)
    )
    
    logger.info("✅ Web App setup handlers registered")

