"""
Admin Menu — Interactive dashboard cho admin.
/admin → Stats thực tế + action buttons.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.error import BadRequest
from config.settings import settings

logger = logging.getLogger(__name__)


# ─── Auth ─────────────────────────────────────────────────────────────────────
def _is_admin(user_id: int) -> bool:
    return bool(settings.ADMIN_USER_ID and user_id == int(settings.ADMIN_USER_ID))


def _get_excluded_ids() -> list:
    """IDs của admin/test accounts — loại khỏi stats thực tế."""
    ids = []
    try:
        for raw in settings.ADMIN_TEST_USER_IDS.split(","):
            raw = raw.strip()
            if raw.isdigit():
                ids.append(int(raw))
    except Exception:
        pass
    if settings.ADMIN_USER_ID and settings.ADMIN_USER_ID not in ids:
        ids.append(int(settings.ADMIN_USER_ID))
    return ids


# ─── Stats từ DB (loại test accounts) ────────────────────────────────────────
def _get_stats() -> dict:
    try:
        from bot.utils.database import SessionLocal, User, PaymentVerification
        from sqlalchemy import not_, func
        db = SessionLocal()
        excluded = _get_excluded_ids()

        def base_q():
            q = db.query(User)
            if excluded:
                q = q.filter(not_(User.id.in_(excluded)))
            return q

        total = base_q().count()
        registered = base_q().filter(User.is_registered == True).count()  # noqa
        with_webapp = (
            base_q()
            .filter(User.is_registered == True)  # noqa
            .filter(User.web_app_url.isnot(None))
            .filter(User.web_app_url != "")
            .filter(User.web_app_url != "pending")
            .count()
        )

        # Status counts
        sc = {}
        for st in ["PENDING", "WEBAPP_SETUP", "ACTIVE", "INACTIVE", "CHURNED"]:
            sc[st] = base_q().filter(User.user_status == st).count()

        # Activity
        today    = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_today = base_q().filter(User.last_active >= today).count()
        active_7d    = base_q().filter(User.last_active >= week_ago).count()

        # Source breakdown (BOT vs LANDING_PAGE)
        bot_users = base_q().filter(User.activation_source == "BOT").count()
        landing_users = base_q().filter(User.activation_source == "LANDING_PAGE").count()

        # User segments (Đăng ký / Kết nối / Giao dịch)
        dang_ky = base_q().filter(
            (User.spreadsheet_id.is_(None)) & 
            ((User.total_transactions.is_(None)) | (User.total_transactions == 0))
        ).count()
        ket_noi = base_q().filter(
            User.spreadsheet_id.isnot(None),
            (User.total_transactions.is_(None)) | (User.total_transactions == 0)
        ).count()
        giao_dich = base_q().filter(
            User.total_transactions.isnot(None),
            User.total_transactions > 0
        ).count()

        # Payment stats
        pending_payments = db.query(PaymentVerification).filter(
            PaymentVerification.status == "PENDING"
        ).count()
        revenue = db.query(func.sum(PaymentVerification.amount)).filter(
            PaymentVerification.status == "APPROVED"
        ).scalar() or 0

        db.close()
        return {
            "total": total,
            "registered": registered,
            "with_webapp": with_webapp,
            "without_webapp": max(0, registered - with_webapp),
            "status": sc,
            "active_today": active_today,
            "active_7d": active_7d,
            "bot_users": bot_users,
            "landing_users": landing_users,
            "dang_ky": dang_ky,
            "ket_noi": ket_noi,
            "giao_dich": giao_dich,
            "pending_payments": pending_payments,
            "revenue": revenue,
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "total": 0, "registered": 0, "with_webapp": 0, "without_webapp": 0,
            "status": {}, "active_today": 0, "active_7d": 0,
            "bot_users": 0, "landing_users": 0,
            "dang_ky": 0, "ket_noi": 0, "giao_dich": 0,
            "pending_payments": 0, "revenue": 0,
        }


# ─── Dashboard UI ─────────────────────────────────────────────────────────────
def _dashboard_text(s: dict) -> str:
    from datetime import timezone, timedelta
    pct = round(s["with_webapp"] / s["registered"] * 100) if s["registered"] else 0
    bar = "█" * round(pct / 10) + "░" * (10 - round(pct / 10))
    sc  = s.get("status", {})
    # Timezone VN = UTC+7
    now_vn = datetime.now(timezone(timedelta(hours=7))).strftime("%H:%M")
    
    # Format revenue
    revenue_str = f"{s['revenue']/1000000:.1f}M" if s['revenue'] >= 1000000 else f"{s['revenue']/1000:.0f}K" if s['revenue'] >= 1000 else str(int(s['revenue']))
    
    return (
        f"🛡️ <b>ADMIN PANEL</b>   <i>cập nhật {now_vn} VN</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Total: <b>{s['total']}</b>   📋 Đăng ký: <b>{s['registered']}</b>   💳 Pending: <b>{s['pending_payments']}</b>\n"
        f"🤖 BOT: <b>{s['bot_users']}</b>   🌐 Landing: <b>{s['landing_users']}</b>\n"
        f"🔗 Kết nối: <b>{s['with_webapp']}</b> ({pct}%)   📝 Giao dịch: <b>{s['giao_dich']}</b>\n"
        f"<code>[{bar}]</code> {pct}%\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Đăng ký: <b>{s['dang_ky']}</b> | Kết nối: <b>{s['ket_noi']}</b> | Giao dịch: <b>{s['giao_dich']}</b>\n"
        f"📅 Hôm nay: <b>{s['active_today']}</b>   7 ngày: <b>{s['active_7d']}</b>\n"
        f"💰 Doanh thu: <b>{revenue_str} VNĐ</b>"
    )


def _dashboard_keyboard(s: dict) -> InlineKeyboardMarkup:
    sc = s.get("status", {})
    return InlineKeyboardMarkup([
        # Row 1: User Management
        [
            InlineKeyboardButton("👥 Users", callback_data="adm:users_all"),
            InlineKeyboardButton("📊 Segments", callback_data="adm:segments"),
            InlineKeyboardButton("📈 Analytics", callback_data="adm:analytics"),
        ],
        # Row 2: Actions
        [
            InlineKeyboardButton("📣 Broadcast", callback_data="adm:broadcast_menu"),
            InlineKeyboardButton(f"💳 Payments ({s['pending_payments']})", callback_data="adm:payments"),
            InlineKeyboardButton("🔍 Search", callback_data="adm:search"),
        ],
        # Row 3: Data Sync
        [
            InlineKeyboardButton("🔄 Sync Jobs", callback_data="adm:sync_jobs"),
            InlineKeyboardButton("📊 Sheet", callback_data="adm:open_sheet"),
            InlineKeyboardButton("📧 Email", callback_data="adm:email_preview"),
        ],
        # Row 4: System
        [
            InlineKeyboardButton("🏥 Health", callback_data="adm:healthcheck"),
            InlineKeyboardButton("⚠️ Errors", callback_data="adm:errors"),
            InlineKeyboardButton("🔧 Tools", callback_data="adm:tools"),
        ],
        # Row 5: Navigation
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="adm:refresh"),
            InlineKeyboardButton("✖️ Close", callback_data="adm:close"),
        ],
    ])


# ─── Compact user list (không phải bảng dài) ─────────────────────────────────
def _quick_user_text(filter_type: str, limit: int = 15) -> str:
    from bot.utils.database import SessionLocal, User
    from sqlalchemy import not_
    excluded = _get_excluded_ids()
    db = SessionLocal()
    try:
        q = db.query(User)
        if excluded:
            q = q.filter(not_(User.id.in_(excluded)))

        if filter_type == "setup":
            q = q.filter(User.user_status == "WEBAPP_SETUP")
        elif filter_type == "inactive":
            q = q.filter(User.user_status.in_(["INACTIVE", "CHURNED"]))
        elif filter_type == "active":
            q = q.filter(User.user_status == "ACTIVE")
        elif filter_type == "pending":
            q = q.filter(User.user_status == "PENDING")
        # elif filter_type == "all": pass (no filter — show all)

        total = q.count()
        users = q.order_by(User.last_active.desc()).limit(limit).all()

        if not users:
            return f"<i>Không có users (filter: {filter_type})</i>"

        em_map = {"PENDING": "⏳", "WEBAPP_SETUP": "⚙️", "ACTIVE": "✅", "INACTIVE": "😴", "CHURNED": "❌"}
        label_map = {
            "setup": "CHƯA SETUP WEB APP", 
            "inactive": "INACTIVE / CHURNED", 
            "active": "ACTIVE", 
            "pending": "PENDING",
            "all": "TẤT CẢ USERS"
        }
        lines = [f"<b>{label_map.get(filter_type, filter_type.upper())}</b> — {total} users\n"]

        for u in users:
            em   = em_map.get(u.user_status or "", "❓")
            name = (u.first_name or u.username or "?")[:18]
            tag  = f" · <i>{u.admin_tag[:20]}</i>" if u.admin_tag else ""
            wb   = "🌐" if u.web_app_url and u.web_app_url not in ["", "pending"] else "  "
            la   = ""
            if u.last_active:
                d = datetime.utcnow() - u.last_active
                la = f"{d.days}d" if d.days else f"{d.seconds//3600}h" if d.seconds > 3600 else "now"
            lines.append(f"{em}{wb}<code>{u.id}</code> {name}{tag}  {la}")

        if total > limit:
            lines.append(f"\n<i>... và {total - limit} users nữa. Dùng /admin_users {filter_type}</i>")
        return "\n".join(lines)
    finally:
        db.close()


# ─── Handlers ─────────────────────────────────────────────────────────────────
async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/admin — Dashboard compact"""
    user = update.effective_user
    if not user or not _is_admin(user.id):
        await update.message.reply_text("⛔ Chỉ admin.")
        return
    s = _get_stats()
    await update.message.reply_text(
        _dashboard_text(s), parse_mode="HTML", reply_markup=_dashboard_keyboard(s)
    )


async def handle_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    label = "✅ Admin" if _is_admin(user.id) else "❌ Không phải admin"
    await update.message.reply_text(f"ID: <code>{user.id}</code>  {label}", parse_mode="HTML")


async def handle_admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not _is_admin(query.from_user.id):
        await query.answer("⛔", show_alert=True)
        return
    await query.answer()
    data = query.data

    _back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Dashboard", callback_data="adm:refresh")]])

    # ── Close / Refresh ──────────────────────────────────────────────────────
    if data == "adm:close":
        try:
            await query.message.delete()
        except Exception:
            await query.edit_message_text("✅ Đóng.")

    elif data in ("adm:refresh", "adm:main"):
        try:
            s = _get_stats()
            await query.edit_message_text(
                _dashboard_text(s), parse_mode="HTML", reply_markup=_dashboard_keyboard(s)
            )
        except BadRequest as e:
            if "not modified" in str(e).lower():
                await query.answer("Không có thay đổi.", show_alert=False)
            else:
                await query.answer(f"Lỗi: {e}", show_alert=True)

    # ── User lists (compact inline) ──────────────────────────────────────────
    elif data == "adm:users_setup":
        text = _quick_user_text("setup")
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📤 Gửi setup guide", callback_data="adm:broadcast_confirm")],
                [InlineKeyboardButton("◀️ Dashboard", callback_data="adm:refresh")],
            ])
        )

    elif data == "adm:users_inactive":
        text = _quick_user_text("inactive")
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=_back_btn)

    elif data == "adm:users_all":
        text = _quick_user_text("all")
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=_back_btn)

    # ── NEW: Segments View ────────────────────────────────────────────────────
    elif data == "adm:segments":
        s = _get_stats()
        await query.edit_message_text(
            f"📊 <b>USER SEGMENTS</b>\n\n"
            f"📍 <b>Đăng ký</b>: {s['dang_ky']} users ({s['dang_ky']/s['total']*100:.1f}%)\n"
            f"   Chỉ mới đăng ký, chưa kết nối spreadsheet\n\n"
            f"📍 <b>Đã kết nối Bot</b>: {s['ket_noi']} users ({s['ket_noi']/s['total']*100:.1f}%)\n"
            f"   Có spreadsheet nhưng chưa ghi giao dịch\n\n"
            f"📍 <b>Ghi giao dịch</b>: {s['giao_dich']} users ({s['giao_dich']/s['total']*100:.1f}%)\n"
            f"   Đã có giao dịch trong hệ thống\n",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"📤 Broadcast Đăng ký ({s['dang_ky']})", callback_data="adm:broadcast_dang_ky")],
                [InlineKeyboardButton(f"📤 Broadcast Giao dịch ({s['giao_dich']})", callback_data="adm:broadcast_giao_dich")],
                [InlineKeyboardButton("◀️ Dashboard", callback_data="adm:refresh")],
            ])
        )

    # ── NEW: Analytics ─────────────────────────────────────────────────────────
    elif data == "adm:analytics":
        s = _get_stats()
        conversion_rate = (s['with_webapp'] / s['total'] * 100) if s['total'] > 0 else 0
        active_rate = (s['giao_dich'] / s['total'] * 100) if s['total'] > 0 else 0
        await query.edit_message_text(
            f"📈 <b>ANALYTICS</b>\n\n"
            f"<b>Conversion Funnel:</b>\n"
            f"Total Users → {s['total']}\n"
            f"├─ Đăng ký → {s['dang_ky']} ({s['dang_ky']/s['total']*100:.1f}%)\n"
            f"├─ Kết nối → {s['ket_noi']} ({s['ket_noi']/s['total']*100:.1f}%)\n"
            f"└─ Giao dịch → {s['giao_dich']} ({s['giao_dich']/s['total']*100:.1f}%)\n\n"
            f"<b>Activation Rate:</b> {conversion_rate:.1f}%\n"
            f"<b>Active Rate:</b> {active_rate:.1f}%\n\n"
            f"<b>By Source:</b>\n"
            f"🤖 BOT: {s['bot_users']} users\n"
            f"🌐 Landing Page: {s['landing_users']} users\n\n"
            f"<b>Payment:</b>\n"
            f"💰 Revenue: {s['revenue']/1000:.0f}K VNĐ\n"
            f"💳 Pending: {s['pending_payments']} verifications",
            parse_mode="HTML",
            reply_markup=_back_btn
        )

    # ── NEW: Broadcast Menu ────────────────────────────────────────────────────
    elif data == "adm:broadcast_menu":
        s = _get_stats()
        await query.edit_message_text(
            f"📣 <b>BROADCAST MENU</b>\n\n"
            f"Chọn segment để gửi:\n\n"
            f"📤 <b>Đăng ký</b>: {s['dang_ky']} users\n"
            f"   → Onboarding message\n\n"
            f"📤 <b>Đã kết nối</b>: {s['ket_noi']} users\n"
            f"   → Khuyến khích giao dịch đầu tiên\n\n"
            f"📤 <b>Giao dịch</b>: {s['giao_dich']} users\n"
            f"   → Feedback & Premium offer\n\n"
            f"📤 <b>Setup Chưa xong</b>: {s['without_webapp']} users\n"
            f"   → Setup guide",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Đăng ký ({s['dang_ky']})", callback_data="adm:broadcast_dang_ky")],
                [InlineKeyboardButton(f"Đã kết nối ({s['ket_noi']})", callback_data="adm:broadcast_ket_noi")],
                [InlineKeyboardButton(f"Giao dịch ({s['giao_dich']})", callback_data="adm:broadcast_giao_dich")],
                [InlineKeyboardButton(f"Setup msg ({s['without_webapp']})", callback_data="adm:broadcast_preview")],
                [InlineKeyboardButton("◀️ Back", callback_data="adm:refresh")],
            ])
        )

    elif data == "adm:broadcast_dang_ky":
        await query.answer("⚠️ Feature coming soon! Use broadcast_segments.py script", show_alert=True)

    elif data == "adm:broadcast_ket_noi":
        await query.answer("⚠️ Feature coming soon! Use broadcast_segments.py script", show_alert=True)

    elif data == "adm:broadcast_giao_dich":
        await query.answer("⚠️ Feature coming soon! Use broadcast_segments.py script", show_alert=True)

    # ── NEW: Payments ──────────────────────────────────────────────────────────
    elif data == "adm:payments":
        s = _get_stats()
        await query.edit_message_text(
            f"💳 <b>PAYMENT VERIFICATIONS</b>\n\n"
            f"Pending: <b>{s['pending_payments']}</b> verifications\n"
            f"Revenue: <b>{s['revenue']/1000:.0f}K VNĐ</b>\n\n"
            f"Use commands:\n"
            f"/payment_list - View pending\n"
            f"/payment_stats - Statistics",
            parse_mode="HTML",
            reply_markup=_back_btn
        )

    # ── NEW: Search ────────────────────────────────────────────────────────────
    elif data == "adm:search":
        await query.edit_message_text(
            f"🔍 <b>SEARCH USER</b>\n\n"
            f"Send:\n"
            f"<code>/admin_find [user_id or email]</code>\n\n"
            f"Example:\n"
            f"<code>/admin_find 6588506476</code>\n"
            f"<code>/admin_find mettatuan@gmail.com</code>",
            parse_mode="HTML",
            reply_markup=_back_btn
        )

    # ── NEW: Sync Jobs ─────────────────────────────────────────────────────────
    elif data == "adm:sync_jobs":
        await query.edit_message_text(
            f"🔄 <b>SYNC JOBS</b>\n\n"
            f"<b>Auto Sync Schedule:</b>\n"
            f"• Landing Page → DB: Every 30 min\n"
            f"• DB → Sheet: Manual only\n\n"
            f"<b>Manual Triggers:</b>\n"
            f"Use VPS PowerShell:\n"
            f"<code>cd C:\\FreedomWalletBot</code>\n"
            f"<code>python bot/utils/sync_landing_page.py</code>\n"
            f"<code>python bot/utils/sync_db_to_sheet.py</code>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Open Google Sheet", callback_data="adm:open_sheet")],
                [InlineKeyboardButton("◀️ Back", callback_data="adm:refresh")],
            ])
        )

    # ── NEW: Open Sheet ────────────────────────────────────────────────────────
    elif data == "adm:open_sheet":
        sheet_url = "https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit"
        await query.edit_message_text(
            f"📊 <b>GOOGLE SHEET</b>\n\n"
            f"Click button below to open:\n"
            f"• 32 users synced\n"
            f"• Auto-updates every 30 min\n"
            f"• Includes status & source",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Open Sheet", url=sheet_url)],
                [InlineKeyboardButton("◀️ Back", callback_data="adm:refresh")],
            ])
        )

    # ── NEW: Tools Menu ────────────────────────────────────────────────────────
    elif data == "adm:tools":
        await query.edit_message_text(
            f"🔧 <b>ADMIN TOOLS</b>\n\n"
            f"<b>Available Commands:</b>\n"
            f"/broadcast_all [msg] - Send to all\n"
            f"/admin_users [filter] - List users\n"
            f"/admin_find [id/email] - Search user\n"
            f"/payment_list - Pending payments\n"
            f"/health - System status\n\n"
            f"<b>VPS Scripts:</b>\n"
            f"• broadcast_segments.py - Segment broadcast\n"
            f"• check_bot_status.ps1 - Bot status\n"
            f"• C:\\nssm\\nssm.exe restart FreedomWalletBot",
            parse_mode="HTML",
            reply_markup=_back_btn
        )

    # ── Event Broadcast (Keep existing) ───────────────────────────────────────
    elif data == "adm:event_preview":
        s = _get_stats()
        await query.edit_message_text(
            f"🎯 <b>EVENT ZOOM — XÁC NHẬN GỬI</b>\n"
            f"Gửi tới: <b>{s['registered']} users</b> đã đăng ký\n\n"
            f"🔔 <b>TỐI NAY – 19H00 - Tuấn trực tiếp</b>\n"
            f"HƯỚNG DẪN TẠO WEB APP TỪ A → Z\n"
            f"Kèm: Zalo group  ·  Telegram group  ·  Start Bot",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Gửi ngay", callback_data="adm:event_confirm")],
                [InlineKeyboardButton("◀️ Hủy", callback_data="adm:refresh")],
            ])
        )

    elif data == "adm:event_confirm":
        await query.edit_message_text("⏳ <b>Đang gửi event...</b>", parse_mode="HTML")
        context.application.create_task(_run_event_broadcast(query, context))

    # ── Setup Broadcast ──────────────────────────────────────────────────────
    elif data == "adm:broadcast_preview":
        s = _get_stats()
        await query.edit_message_text(
            f"📤 <b>GỬI VIDEO SETUP — XÁC NHẬN</b>\n"
            f"Gửi tới: <b>{s['without_webapp']} users</b> chưa setup\n"
            f"Nội dung: Video 5 phút + link hướng dẫn",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Gửi ngay", callback_data="adm:broadcast_confirm")],
                [InlineKeyboardButton("◀️ Hủy", callback_data="adm:refresh")],
            ])
        )

    elif data == "adm:broadcast_confirm":
        await query.edit_message_text("⏳ <b>Đang gửi...</b>", parse_mode="HTML")
        context.application.create_task(_run_broadcast(query, context))

    # ── Broadcast All ─────────────────────────────────────────────────────────
    elif data == "adm:broadcast_all_preview":
        s = _get_stats()
        await query.edit_message_text(
            f"📢 <b>BROADCAST TẤT CẢ</b>\n"
            f"Gửi tới: <b>{s['registered']} users</b>\n\n"
            f"Dùng lệnh tùy chỉnh:\n"
            f"<code>/broadcast_all confirm [nội dung]</code>",
            parse_mode="HTML",
            reply_markup=_back_btn
        )

    # ── Email ─────────────────────────────────────────────────────────────────
    elif data == "adm:email_preview":
        await _handle_email_preview(query)

    elif data == "adm:email_confirm":
        await query.edit_message_text("⏳ <b>Đang gửi email...</b>", parse_mode="HTML")
        context.application.create_task(_run_email_broadcast(query, context))

    elif data == "adm:email_test":
        await _handle_email_test(query)

    # ── Health / Errors ───────────────────────────────────────────────────────
    elif data == "adm:healthcheck":
        try:
            text = await _get_health_text()
            await query.edit_message_text(
                text, parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔄", callback_data="adm:healthcheck"),
                    InlineKeyboardButton("◀️", callback_data="adm:refresh"),
                ]])
            )
        except BadRequest as e:
            if "not modified" in str(e).lower():
                await query.answer("Không thay đổi.")
            else:
                await query.answer(f"Lỗi: {e}", show_alert=True)

    elif data == "adm:errors":
        await query.edit_message_text(
            _get_errors_text()[:4000], parse_mode="HTML", reply_markup=_back_btn
        )

    else:
        await query.answer("Unknown.", show_alert=True)


# ─── Background tasks ─────────────────────────────────────────────────────────
async def _run_event_broadcast(query, context):
    _back = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Dashboard", callback_data="adm:refresh")]])
    try:
        from bot.handlers.admin_broadcast import _get_all_registered_users, _send_broadcast, EVENT_MESSAGE
        users = _get_all_registered_users()
        if not users:
            await query.edit_message_text("⚠️ Không có users.", reply_markup=_back)
            return
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Zalo Group", url="https://zalo.me/g/ivdfur126")],
            [InlineKeyboardButton("💬 Telegram Group", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("🤖 Start Bot", url="https://t.me/FreedomWalletbot")],
        ])
        result = await _send_broadcast(context.bot, users, EVENT_MESSAGE, delay=0.05, keyboard=kb)
        await query.edit_message_text(
            f"✅ <b>Gửi event xong!</b>\n📤 {result['sent']} · 🚫 {result['blocked']} · ❌ {result['failed']} / {result['total']}",
            parse_mode="HTML", reply_markup=_back
        )
    except Exception as e:
        logger.error(f"Event broadcast error: {e}", exc_info=True)
        await query.edit_message_text(f"❌ {e}", reply_markup=_back)


async def _run_broadcast(query, context):
    _back = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Dashboard", callback_data="adm:refresh")]])
    try:
        from bot.handlers.admin_broadcast import _get_users_without_webapp, _send_broadcast, SETUP_MESSAGE
        users = _get_users_without_webapp()
        if not users:
            await query.edit_message_text("✅ Tất cả đã setup.", reply_markup=_back)
            return
        result = await _send_broadcast(context.bot, users, SETUP_MESSAGE)
        await query.edit_message_text(
            f"✅ <b>Gửi xong!</b>\n📤 {result['sent']} · 🚫 {result['blocked']} · ❌ {result['failed']} / {result['total']}",
            parse_mode="HTML", reply_markup=_back
        )
    except Exception as e:
        logger.error(f"Broadcast error: {e}", exc_info=True)
        await query.edit_message_text(f"❌ {e}", reply_markup=_back)


# ─── Helpers ──────────────────────────────────────────────────────────────────
async def _get_health_text() -> str:
    try:
        from bot.core.error_tracker import get_tracker
        t = get_tracker()
        recent = t.get_recent_errors(minutes=60)
        real = t.total_errors - t.ignorable_count
        status = "🟢 Ổn định" if real < 5 else ("🟡 Theo dõi" if real < 15 else "🔴 Kiểm tra ngay!")
        return f"🏥 <b>HEALTH: {status}</b>\nLỗi 1h: <b>{recent}</b>  Tổng: {t.total_errors}"
    except Exception as e:
        return f"🏥 Bot đang chạy\n⚠️ Lỗi tracker: {e}"


def _get_errors_text() -> str:
    try:
        from bot.core.error_tracker import get_tracker
        return f"⚠️ <b>LỖI GẦN ĐÂY</b>\n{get_tracker().get_report()}"
    except Exception as e:
        return f"Không đọc được: {e}"


async def _handle_email_preview(query):
    from config.settings import settings
    from bot.utils.email_sender import test_smtp_connection
    from sqlalchemy import not_
    smtp_ok, smtp_msg = await asyncio.to_thread(test_smtp_connection)
    smtp_status = f"✅ SMTP: {getattr(settings, 'SMTP_USER', '?')}" if smtp_ok else "⚠️ SMTP chưa cấu hình"
    try:
        from bot.utils.database import SessionLocal, User
        excluded = _get_excluded_ids()
        db = SessionLocal()
        q = (db.query(User).filter(User.is_registered == True)  # noqa
             .filter(not_(User.id.in_(excluded)) if excluded else User.id.isnot(None))
             .filter((User.web_app_url.is_(None)) | (User.web_app_url == "") | (User.web_app_url == "pending"))
             .filter(User.email.isnot(None)).filter(User.email != ""))
        cnt = q.count()
        db.close()
    except Exception:
        cnt = 0
    await query.edit_message_text(
        f"📧 <b>EMAIL BROADCAST</b>\n{smtp_status}\n\nGửi tới: <b>{cnt} users</b> có email, chưa setup",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ Gửi ({cnt})", callback_data="adm:email_confirm")],
            [InlineKeyboardButton("🔌 Test SMTP", callback_data="adm:email_test")],
            [InlineKeyboardButton("◀️", callback_data="adm:refresh")],
        ])
    )


async def _handle_email_test(query):
    from bot.utils.email_sender import test_smtp_connection
    ok, msg = await asyncio.to_thread(test_smtp_connection)
    icon = "✅" if ok else "❌"
    await query.edit_message_text(
        f"{icon} SMTP: {msg}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️", callback_data="adm:email_preview")]])
    )


async def _run_email_broadcast(query, context):
    _back = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Dashboard", callback_data="adm:refresh")]])
    try:
        from bot.utils.database import SessionLocal, User
        from bot.utils.email_sender import send_setup_emails_to_list
        from sqlalchemy import not_
        excluded = _get_excluded_ids()
        db = SessionLocal()
        users_q = (
            db.query(User).filter(User.is_registered == True)  # noqa
            .filter(not_(User.id.in_(excluded)) if excluded else User.id.isnot(None))
            .filter((User.web_app_url.is_(None)) | (User.web_app_url == "") | (User.web_app_url == "pending"))
            .filter(User.email.isnot(None)).filter(User.email != "").all()
        )
        users = [{"id": u.id, "first_name": u.first_name or "", "email": u.email} for u in users_q]
        db.close()
        if not users:
            await query.edit_message_text("✅ Không có ai cần gửi.", reply_markup=_back)
            return
        result = await send_setup_emails_to_list(users)
        await query.edit_message_text(
            f"✅ Email xong!  📧{result['sent']} ⚠️{result.get('skipped_no_email',0)} ❌{result['failed']} / {result['total']}",
            reply_markup=_back
        )
    except Exception as e:
        logger.error(f"Email broadcast error: {e}", exc_info=True)
        await query.edit_message_text(f"❌ {e}", reply_markup=_back)


# ─── Register ─────────────────────────────────────────────────────────────────
def register_admin_menu_handlers(application):
    application.add_handler(CommandHandler("admin", handle_admin_menu), group=-10)
    application.add_handler(CommandHandler("myid", handle_myid), group=-10)
    application.add_handler(
        CallbackQueryHandler(handle_admin_callback, pattern=r"^adm:"),
        group=-10,
    )
    logger.info("✅ Admin menu handlers registered (group=-10)")
