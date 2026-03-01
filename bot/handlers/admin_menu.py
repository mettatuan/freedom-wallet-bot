"""
Admin Menu — Interactive dashboard cho admin.

/admin → Hiện live stats + action buttons trực tiếp.
Bấm nút là có kết quả, không cần nhớ lệnh.
"""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest
from config.settings import settings

logger = logging.getLogger(__name__)

# ─── Auth ──────────────────────────────────────────────────────────────────────
def _is_admin(user_id: int) -> bool:
    return bool(settings.ADMIN_USER_ID and user_id == int(settings.ADMIN_USER_ID))


# ─── Live stats từ DB ────────────────────────────────────────────────────────
def _get_stats() -> dict:
    try:
        from bot.utils.database import SessionLocal, User
        db = SessionLocal()
        total = db.query(User).count()
        registered = db.query(User).filter(User.is_registered == True).count()  # noqa
        with_webapp = (
            db.query(User)
            .filter(User.is_registered == True)  # noqa
            .filter(User.web_app_url != None)  # noqa
            .filter(User.web_app_url != "")
            .filter(User.web_app_url != "pending")
            .count()
        )
        
        # Status breakdown
        status_counts = {}
        for status in ["PENDING", "WEBAPP_SETUP", "ACTIVE", "INACTIVE", "CHURNED"]:
            count = db.query(User).filter(User.user_status == status).count()
            status_counts[status] = count
        
        # Tagged users
        tagged = db.query(User).filter(User.admin_tag != None).filter(User.admin_tag != "").count()
        
        db.close()
        return {
            "total": total, 
            "registered": registered,
            "with_webapp": with_webapp, 
            "without_webapp": registered - with_webapp,
            "status": status_counts,
            "tagged": tagged
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "total": 0, "registered": 0, "with_webapp": 0, "without_webapp": 0,
            "status": {}, "tagged": 0
        }


# ─── Dashboard text + keyboard ────────────────────────────────────────────────
def _dashboard_text(s: dict) -> str:
    pct = round(s["with_webapp"] / s["registered"] * 100) if s["registered"] else 0
    bar = "█" * round(pct / 10) + "░" * (10 - round(pct / 10))
    
    # Status breakdown
    status = s.get("status", {})
    status_text = f"""📊 <b>THEO TRẠNG THÁI:</b>
⏳ Pending: {status.get('PENDING', 0)} • ⚙️ Setup: {status.get('WEBAPP_SETUP', 0)}
✅ Active: {status.get('ACTIVE', 0)} • 😴 Inactive: {status.get('INACTIVE', 0)} • ❌ Churned: {status.get('CHURNED', 0)}
🏷️ Có tag: {s.get('tagged', 0)} users"""
    
    return (
        "🛡️ <b>FREEDOM WALLET — ADMIN PANEL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Tổng users:   <b>{s['total']}</b>\n"
        f"✅ Đã đăng ký:  <b>{s['registered']}</b>\n"
        f"🌐 Có Web App:  <b>{s['with_webapp']}</b>  •  ⚠️ Chưa setup: <b>{s['without_webapp']}</b>\n\n"
        f"<code>[{bar}] {pct}%</code> đã setup Web App\n\n"
        f"{status_text}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Chọn hành động:"
    )


def _dashboard_keyboard(s: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"🎯 GỬI EVENT ZOOM 19H ({s['registered']} users)",
            callback_data="adm:event_preview"
        )],
        [
            InlineKeyboardButton(
                f"👥 All Users ({s['total']})", 
                callback_data="adm:list_all"
            ),
            InlineKeyboardButton(
                f"⚙️ Setup ({s.get('status', {}).get('WEBAPP_SETUP', 0)})", 
                callback_data="adm:list_setup"
            ),
        ],
        [
            InlineKeyboardButton(
                f"✅ Active ({s.get('status', {}).get('ACTIVE', 0)})", 
                callback_data="adm:list_active"
            ),
            InlineKeyboardButton(
                f"😴 Inactive ({s.get('status', {}).get('INACTIVE', 0)})", 
                callback_data="adm:list_inactive"
            ),
        ],
        [InlineKeyboardButton(
            f"📤 Gửi video setup  ({s['without_webapp']} chưa setup)",
            callback_data="adm:broadcast_preview"
        )],
        [InlineKeyboardButton(
            f"� Gửi email  ({s['without_webapp']} chưa setup)",
            callback_data="adm:email_preview"
        )],
        [InlineKeyboardButton(
            f"�📢 Broadcast tất cả  ({s['registered']} users)",
            callback_data="adm:broadcast_all_preview"
        )],
        [
            InlineKeyboardButton("🏥 Health check", callback_data="adm:healthcheck"),
            InlineKeyboardButton("⚠️ Xem lỗi", callback_data="adm:errors"),
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="adm:refresh"),
            InlineKeyboardButton("❌ Đóng", callback_data="adm:close"),
        ],
    ])


# ─── Broadcast setup preview ──────────────────────────────────────────────────
SETUP_MESSAGE_PREVIEW = (
    "📤 <b>PREVIEW — Tin gửi tới user chưa setup Web App</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "👋 <b>Bạn đã đăng ký Freedom Wallet rồi!</b>\n\n"
    "Bước tiếp theo là tạo <b>Web App cá nhân</b> để:\n"
    "✅ Lưu 100% dữ liệu trong Google Drive của bạn\n"
    "✅ Ghi thu chi bằng giọng nói và text siêu nhanh\n"
    "✅ Xem báo cáo tài chính trực quan\n\n"
    "🎬 <b>Video hướng dẫn từng bước (5 phút):</b>\n"
    "https://youtu.be/xVoASsuWfto\n\n"
    "Chỉ mất 5 phút — làm ngay hôm nay nhé! 🚀\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ Bấm <b>✅ Gửi ngay</b> để gửi tới tất cả user chưa setup."
)

EVENT_MESSAGE_PREVIEW = (
    "📢 <b>PREVIEW — ZOOM TRAINING EVENT TỐI NAY</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🔔 <b>TỐI NAY – 19H00 - Tuấn trực tiếp</b>\n"
    "<b>HƯỚNG DẪN TẠO WEB APP & SỬ DỤNG FREEDOM WALLET TỪ A → Z</b>\n\n"
    "📍 <b>NỘI DUNG:</b>\n"
    "   1️⃣ Tạo Web App - Từng bước chi tiết\n"
    "   2️⃣ Kết nối Bot Telegram\n"
    "   3️⃣ Hướng dẫn sử dụng Web App\n"
    "   4️⃣ Ghi giao dịch A→Z\n"
    "   5️⃣ Q&A giải đáp mọi thắc mắc\n\n"
    "✅ <b>YÊU CẦU:</b>\n"
    "   🖥️ Laptop để làm theo\n"
    "   👥 Tham gia nhóm nhận link Zoom\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ Bấm <b>✅ Gửi ngay</b> để gửi tới tất cả {registered} users."
)

EVENT_MESSAGE_PREVIEW = (
    "📢 <b>PREVIEW — ZOOM TRAINING EVENT TỐI NAY</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🔔 <b>TỐI NAY – 19H00 - Tuấn trực tiếp</b>\n"
    "<b>HƯỚNG DẪN TẠO WEB APP & SỬ DỤNG FREEDOM WALLET TỪ A → Z</b>\n\n"
    "📌 <b>NỘI DUNG:</b>\n"
    "   1️⃣ Tạo Web App - Từng bước chi tiết\n"
    "   2️⃣ Kết nối Bot Telegram\n"
    "   3️⃣ Hướng dẫn sử dụng Web App\n"
    "   4️⃣ Ghi giao dịch A→Z\n"
    "   5️⃣ Q&A giải đáp mọi thắc mắc\n\n"
    "✅ <b>YÊU CẦU:</b>\n"
    "   🖥️ Laptop để làm theo\n"
    "   👥 Tham gia nhóm nhận link Zoom\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚠️ Bấm <b>✅ Gửi ngay</b> để gửi tới tất cả {registered} users."
)


def _broadcast_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Gửi ngay", callback_data="adm:broadcast_confirm")],
        [InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")],
    ])


# ─── Handlers ─────────────────────────────────────────────────────────────────
async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/admin — Dashboard với live stats"""
    user = update.effective_user
    if not user or not _is_admin(user.id):
        await update.message.reply_text("⛔ Chỉ admin mới dùng được lệnh này.")
        return
    s = _get_stats()
    await update.message.reply_text(
        _dashboard_text(s), parse_mode="HTML", reply_markup=_dashboard_keyboard(s)
    )


async def handle_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/myid — Xem Telegram user ID"""
    user = update.effective_user
    is_admin = _is_admin(user.id)
    status = "✅ <b>Đây là Admin ID</b>" if is_admin else f"❌ Không phải admin (admin ID: <code>{settings.ADMIN_USER_ID}</code>)"
    await update.message.reply_text(
        f"👤 Your Telegram ID: <code>{user.id}</code>\n{status}", parse_mode="HTML"
    )


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tất cả nút inline trong admin panel."""
    query = update.callback_query
    if not _is_admin(query.from_user.id):
        await query.answer("⛔ Không có quyền.", show_alert=True)
        return
    await query.answer()
    data = query.data

    if data == "adm:close":
        await query.edit_message_text("✅ Admin panel đã đóng.")

    elif data in ("adm:refresh", "adm:main"):
        try:
            s = _get_stats()
            await query.edit_message_text(
                _dashboard_text(s), parse_mode="HTML", reply_markup=_dashboard_keyboard(s)
            )
        except BadRequest as e:
            # "Message is not modified" — stats haven't changed, just show toast
            if "not modified" in str(e).lower() or "Message is not modified" in str(e):
                await query.answer("✅ Dữ liệu không thay đổi.", show_alert=False)
            else:
                logger.error(f"BadRequest in refresh: {e}")
                await query.answer(f"❌ Lỗi: {e}", show_alert=True)

    elif data == "adm:email_preview":
        await _handle_email_preview(query)

    elif data == "adm:event_preview":
        s = _get_stats()
        await query.edit_message_text(
            EVENT_MESSAGE_PREVIEW.format(registered=s['registered']),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Gửi ngay", callback_data="adm:event_confirm")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")],
            ])
        )

    elif data == "adm:event_confirm":
        await query.edit_message_text(
            "⏳ <b>Đang gửi event tới tất cả users...</b> Vui lòng chờ.", parse_mode="HTML"
        )
        context.application.create_task(_run_event_broadcast(query, context))

    elif data == "adm:email_confirm":
        await query.edit_message_text(
            "⏳ <b>Đang gửi email...</b> Vui lòng chờ.", parse_mode="HTML"
        )
        context.application.create_task(_run_email_broadcast(query, context))

    elif data == "adm:email_test":
        await _handle_email_test(query)

    elif data == "adm:event_preview":
        s = _get_stats()
        await query.edit_message_text(
            EVENT_MESSAGE_PREVIEW.format(registered=s['registered']),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Gửi ngay", callback_data="adm:event_confirm")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")],
            ])
        )

    elif data == "adm:event_confirm":
        await query.edit_message_text(
            "⏳ <b>Đang gửi event tới tất cả users...</b> Vui lòng chờ.", parse_mode="HTML"
        )
        context.application.create_task(_run_event_broadcast(query, context))

    elif data == "adm:list_all":
        await _show_user_list(query, "all")
    
    elif data == "adm:list_setup":
        await _show_user_list(query, "webapp_setup")
    
    elif data == "adm:list_active":
        await _show_user_list(query, "active")
    
    elif data == "adm:list_inactive":
        await _show_user_list(query, "inactive")

    elif data == "adm:broadcast_preview":
        await query.edit_message_text(
            SETUP_MESSAGE_PREVIEW, parse_mode="HTML",
            reply_markup=_broadcast_preview_keyboard()
        )

    elif data == "adm:broadcast_all_preview":
        s = _get_stats()
        await query.edit_message_text(
            f"📢 <b>BROADCAST ALL</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Sẽ gửi tới <b>{s['registered']} users</b> đã đăng ký.\n\n"
            f"Dùng lệnh để gửi với nội dung tùy chỉnh:\n"
            f"<code>/broadcast_all confirm [nội dung]</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
            ]])
        )

    elif data == "adm:broadcast_confirm":
        await query.edit_message_text(
            "⏳ <b>Đang gửi...</b> Vui lòng chờ.", parse_mode="HTML"
        )
        context.application.create_task(_run_broadcast(query, context))

    elif data == "adm:healthcheck":
        try:
            text = await _get_health_text()
            await query.edit_message_text(
                text, parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄 Refresh", callback_data="adm:healthcheck"),
                    InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh"),
                ]])
            )
        except BadRequest as e:
            if "not modified" in str(e).lower():
                await query.answer("✅ Dữ liệu không thay đổi.", show_alert=False)
            else:
                logger.error(f"Error in healthcheck: {e}")
                await query.answer(f"❌ Lỗi: {e}", show_alert=True)

    elif data == "adm:errors":
        text = _get_errors_text()
        await query.edit_message_text(
            text[:4000], parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
            ]])
        )

    else:
        await query.answer("Không rõ lệnh.", show_alert=True)


# ─── Helper tasks ─────────────────────────────────────────────────────────────
async def _show_user_list(query, filter_type: str):
    """Show user list with filter"""
    from bot.utils.database import SessionLocal, User
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        users_query = db.query(User)
        
        # Apply filters
        if filter_type == "webapp_setup":
            users_query = users_query.filter(User.user_status == "WEBAPP_SETUP")
        elif filter_type == "active":
            users_query = users_query.filter(User.user_status == "ACTIVE")
        elif filter_type == "inactive":
            users_query = users_query.filter(User.user_status == "INACTIVE")
        
        users = users_query.order_by(User.last_active.desc()).limit(20).all()
        
        if not users:
            await query.edit_message_text(
                f"📊 Không có users với filter: <b>{filter_type}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
                ]])
            )
            return
        
        # Build report
        lines = [
            f"📊 <b>DANH SÁCH USERS ({filter_type.upper()})</b>",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"Tổng: <b>{len(users)}</b> users (20 gần nhất)\n"
        ]
        
        for u in users:
            status_emoji = {
                "PENDING": "⏳",
                "WEBAPP_SETUP": "⚙️",
                "ACTIVE": "✅",
                "INACTIVE": "😴",
                "CHURNED": "❌"
            }.get(u.user_status, "❓")
            
            # Format last active
            if u.last_active:
                delta = datetime.utcnow() - u.last_active
                if delta.days > 30:
                    last_active = f"{delta.days}d"
                elif delta.days > 0:
                    last_active = f"{delta.days}d"
                elif delta.seconds > 3600:
                    last_active = f"{delta.seconds // 3600}h"
                else:
                    last_active = "now"
            else:
                last_active = "never"
            
            # User line
            name = u.first_name or u.username or "Unknown"
            tag_str = f" 🏷️<i>{u.admin_tag[:20]}</i>" if u.admin_tag else ""
            webapp_icon = "🌐" if u.web_app_url and u.web_app_url not in ["", "pending"] else ""
            
            lines.append(
                f"{status_emoji} <code>{u.id}</code> {webapp_icon} {name}"
                f"{tag_str}"
                f"\n   ⏱️ {last_active} • 💬 {u.total_interactions or 0}x"
            )
        
        lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"Dùng /admin_users {filter_type} để xem đầy đủ")
        
        text = "\n".join(lines)
        
        if len(text) > 4000:
            text = text[:3900] + "\n\n⚠️ Danh sách quá dài"
        
        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
            ]])
        )
    except Exception as e:
        logger.error(f"Error in _show_user_list: {e}", exc_info=True)
        await query.edit_message_text(
            f"❌ Lỗi: {e}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
            ]])
        )
    finally:
        db.close()


async def _run_event_broadcast(query, context):
    """Gửi event Zoom training tới tất cả registered users"""
    try:
        from bot.handlers.admin_broadcast import (
            _get_all_registered_users, _send_broadcast, EVENT_MESSAGE
        )
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        users = _get_all_registered_users()
        if not users:
            await query.edit_message_text(
                "⚠️ Không có user nào đã đăng ký.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
                ]])
            )
            return
        
        # Keyboard cho event
        event_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Tham gia nhóm Zalo", url="https://zalo.me/g/ivdfur126")],
            [InlineKeyboardButton("💬 Tham gia nhóm Telegram", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("🤖 Bắt đầu với Bot", url="https://t.me/FreedomWalletbot")],
        ])
        
        result = await _send_broadcast(context.bot, users, EVENT_MESSAGE, delay=0.05, keyboard=event_keyboard)
        
        await query.edit_message_text(
            f"✅ <b>Event Broadcast hoàn tất!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📤 Đã gửi:  <b>{result['sent']}</b>\n"
            f"🚫 Bị chặn: {result['blocked']}\n"
            f"❌ Lỗi:     {result['failed']}\n"
            f"🎯 Tổng:   <b>{result['total']}</b> users",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Về Dashboard", callback_data="adm:refresh")
            ]])
        )
    except Exception as e:
        logger.error(f"Event broadcast error: {e}", exc_info=True)
        await query.edit_message_text(
            f"❌ Lỗi khi gửi event: {e}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
            ]])
        )


async def _run_broadcast(query, context):
    try:
        from bot.handlers.admin_broadcast import (
            _get_users_without_webapp, _send_broadcast, SETUP_MESSAGE
        )
        users = _get_users_without_webapp()
        if not users:
            await query.edit_message_text(
                "✅ Không có user nào cần gửi (tất cả đã setup Web App).",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
                ]])
            )
            return
        result = await _send_broadcast(context.bot, users, SETUP_MESSAGE)
        await query.edit_message_text(
            f"✅ <b>Broadcast hoàn tất!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📤 Đã gửi:  <b>{result['sent']}</b>\n"
            f"🚫 Bị chặn: {result['blocked']}\n"
            f"❌ Lỗi:     {result['failed']}\n"
            f"📊 Tổng:   {result['total']}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Về Dashboard", callback_data="adm:refresh")
            ]])
        )
    except Exception as e:
        logger.error(f"Broadcast error: {e}", exc_info=True)
        await query.edit_message_text(
            f"❌ Lỗi: {e}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
            ]])
        )


async def _get_health_text() -> str:
    try:
        from bot.core.error_tracker import get_tracker
        t = get_tracker()
        recent = t.get_recent_errors(minutes=60)
        real = t.total_errors - t.ignorable_count
        status = "🟢 Ổn định" if real < 5 else ("🟡 Cần theo dõi" if real < 15 else "🔴 Cần kiểm tra!")
        return (
            f"🏥 <b>HEALTH CHECK</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"✅ Bot đang chạy bình thường\n"
            f"Lỗi 1h qua: <b>{recent}</b>  •  Tổng: {t.total_errors}\n"
            f"Trạng thái: {status}"
        )
    except Exception as e:
        return f"🏥 Bot đang chạy\n⚠️ Không đọc được error tracker: {e}"


def _get_errors_text() -> str:
    try:
        from bot.core.error_tracker import get_tracker
        return f"⚠️ <b>LỖI GẦN ĐÂY</b>\n━━━━━━━━━━━━━━━━━━━━━━\n\n{get_tracker().get_report()}"
    except Exception as e:
        return f"Không đọc được error log: {e}"


async def _handle_email_preview(query):
    """Hiện preview email + trạng thái SMTP."""
    from config.settings import settings
    from bot.utils.email_sender import test_smtp_connection

    smtp_ok, smtp_msg = await asyncio.to_thread(test_smtp_connection)
    status_line = f"✅ SMTP: {settings.SMTP_USER}" if smtp_ok else f"⚠️ SMTP chưa cấu hình\n{smtp_msg}"

    s = _get_stats()
    # Count users có email
    try:
        from bot.utils.database import SessionLocal, User
        db = SessionLocal()
        users_with_email = (
            db.query(User)
            .filter(User.is_registered == True)  # noqa
            .filter(
                (User.web_app_url == None) |  # noqa
                (User.web_app_url == "") |
                (User.web_app_url == "pending")
            )
            .filter(User.email != None)  # noqa
            .filter(User.email != "")
            .count()
        )
        db.close()
    except Exception:
        users_with_email = 0

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"✅ Gửi email ngay ({users_with_email} users có email)",
            callback_data="adm:email_confirm"
        )],
        [InlineKeyboardButton("🔌 Test kết nối SMTP", callback_data="adm:email_test")],
        [InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")],
    ])

    await query.edit_message_text(
        f"📧 <b>PREVIEW — Email hướng dẫn setup Web App</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{status_line}\n\n"
        f"📊 Sẽ gửi tới: <b>{users_with_email} users</b> (đã đăng ký, chưa setup, có email)\n"
        f"⚠️ Users không có email: {s['without_webapp'] - users_with_email} (bỏ qua)\n\n"
        f"<b>Chủ đề:</b> 🚀 Hoàn tất setup Freedom Wallet của bạn (5 phút)\n\n"
        f"<b>Nội dung:</b>\n"
        f"• Lời chào cá nhân hóa theo tên\n"
        f"• Giải thích lợi ích Web App\n"
        f"• Nút bấm xem video: https://youtu.be/xVoASsuWfto\n"
        f"• Link quay lại bot",
        parse_mode="HTML",
        reply_markup=keyboard,
    )


async def _handle_email_test(query):
    """Test kết nối SMTP."""
    import asyncio
    from bot.utils.email_sender import test_smtp_connection
    ok, msg = await asyncio.to_thread(test_smtp_connection)
    icon = "✅" if ok else "❌"
    await query.edit_message_text(
        f"{icon} <b>Kết quả test SMTP</b>\n\n{msg}\n\n"
        f"Nếu chưa cấu hình, thêm vào <code>.env</code> trên VPS:\n"
        f"<code>SMTP_USER=your@gmail.com\nSMTP_PASSWORD=xxxx xxxx xxxx xxxx</code>\n\n"
        f"📖 Tạo App Password: myaccount.google.com/apppasswords",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Quay lại", callback_data="adm:email_preview")
        ]])
    )


async def _run_email_broadcast(query, context):
    """Chạy email broadcast trong background."""
    import asyncio
    try:
        from bot.utils.database import SessionLocal, User
        from bot.utils.email_sender import send_setup_emails_to_list

        db = SessionLocal()
        users_q = (
            db.query(User)
            .filter(User.is_registered == True)  # noqa
            .filter(
                (User.web_app_url == None) |  # noqa
                (User.web_app_url == "") |
                (User.web_app_url == "pending")
            )
            .filter(User.email != None)  # noqa
            .filter(User.email != "")
            .all()
        )
        users = [{"id": u.id, "first_name": u.first_name or "", "email": u.email} for u in users_q]
        db.close()

        if not users:
            await query.edit_message_text(
                "✅ Không có user nào cần gửi email (không có email hoặc đã setup).",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
                ]])
            )
            return

        result = await send_setup_emails_to_list(users)
        await query.edit_message_text(
            f"✅ <b>Gửi email hoàn tất!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📧 Đã gửi:          <b>{result['sent']}</b>\n"
            f"⚠️ Không có email: {result['skipped_no_email']}\n"
            f"❌ Lỗi:             {result['failed']}\n"
            f"📊 Tổng:           {result['total']}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Về Dashboard", callback_data="adm:refresh")
            ]])
        )
    except Exception as e:
        logger.error(f"Email broadcast error: {e}", exc_info=True)
        await query.edit_message_text(
            f"❌ Lỗi gửi email: {e}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Quay lại", callback_data="adm:refresh")
            ]])
        )


# ─── Register ─────────────────────────────────────────────────────────────────
def register_admin_menu_handlers(application):
    application.add_handler(CommandHandler("admin", handle_admin_menu), group=-10)
    application.add_handler(CommandHandler("myid", handle_myid), group=-10)
    application.add_handler(
        CallbackQueryHandler(handle_admin_callback, pattern=r"^adm:"),
        group=-10,
    )
    logger.info("✅ Admin menu handlers registered (group=-10)")
