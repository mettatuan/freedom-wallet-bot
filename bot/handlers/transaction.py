"""
Transaction Handler - Confirm Before Save Flow
Parse → Show preview (danh mục, hũ, tài khoản) → User confirms → Save to DB + Sheets
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters, ApplicationHandlerStop
from sqlalchemy.orm import Session
from loguru import logger
import aiohttp

import asyncio
from bot.core.nlp import parse_natural_language_transaction, ai_parse_transaction, format_vnd
from bot.core.categories import get_all_categories
from bot.core.keyboard import (
    get_main_keyboard,
    BTN_RECORD, BTN_REPORT, BTN_SHEETS, BTN_WEBAPP,
    BTN_SHARE, BTN_DONATE, BTN_GUIDE, BTN_SETTINGS,
    # legacy aliases
    BTN_OVERVIEW, BTN_WEEKLY, BTN_INSIGHT, BTN_DRIVE, BTN_REFERRAL,
)
from bot.utils.database import Transaction, User, get_db, run_sync
from datetime import datetime, timezone


# --- Categories that auto-distribute income across all 6 jars ---
AUTO_DISTRIBUTE_CATEGORIES = {
    "Lương", "Kinh doanh", "Bán hàng", "Thu tiền nợ",
}

# --- Jar mapping (category → hũ mặc định) ---
CATEGORY_TO_JAR = {
    # Chi — Thiết yếu (NEC)
    "Ăn uống":                        "Thiết yếu",
    "Di chuyển":                      "Thiết yếu",
    "Nhà ở":                          "Thiết yếu",
    "Sức khỏe":                       "Thiết yếu",
    "Điện nước":                      "Thiết yếu",
    "Xăng xe":                        "Thiết yếu",
    "Chi phí khác":                   "Thiết yếu",
    "Công cụ làm việc":               "Thiết yếu",
    "Khác":                           "Thiết yếu",
    # Chi — Vui chơi (PLAY)
    "Mua sắm":                        "Vui chơi",
    "Giải trí":                       "Vui chơi",
    # Chi — Giáo dục (EDU)
    "Học tập":                        "Giáo dục",
    "Giáo dục":                       "Giáo dục",
    "Khóa học":                       "Giáo dục",
    # Chi — Cho đi (GIVE)
    "Quà tặng":                       "Cho đi",
    "Từ thiện":                       "Cho đi",
    # Chi — Tiết kiệm (LTSS)
    "Bảo hiểm":                       "Tiết kiệm",
    # Chi — Tự do TC (FFA)
    "Cho thuê":                       "Tự do TC",
    "Phí giao dịch & quản lý tài sản": "Tự do TC",
    # Thu — Tự do TC
    "Đầu tư":                         "Tự do TC",
    "Thu đầu tư":                     "Tự do TC",
    "Lãi đầu tư":                     "Tự do TC",
    # Thu — Tiết kiệm
    "Lãi ngân hàng":                  "Tiết kiệm",
    # Thu — Tự động phân bổ (set "" so logic uses AUTO_DISTRIBUTE_CATEGORIES)
    "Lương":                          "",
    "Kinh doanh":                     "",
    "Bán hàng":                       "",
    "Thu tiền nợ":                    "",
}

JARS = ["Thiết yếu", "Giáo dục", "Tiết kiệm", "Vui chơi", "Cho đi", "Tự do TC"]
ACCOUNTS = ["Tiền mặt", "Ngân hàng", "Ví điện tử"]

# Map Vietnamese display names → GAS account IDs
_ACCOUNT_DISPLAY_TO_ID: dict[str, str] = {
    "Tiền mặt": "Cash",
    "Ngân hàng": "OCB",
    "Ví điện tử": "ZALO",
}


def _resolve_account_id(display_or_id: str) -> str:
    """Return GAS account ID for a display name; pass through if already an ID."""
    return _ACCOUNT_DISPLAY_TO_ID.get(display_or_id, display_or_id)


def _make_preview(pending: dict) -> tuple:
    amount_display = format_vnd(abs(pending["amount"]))
    tx_type  = pending["type"]
    category = pending["category"]
    jar      = pending.get("jar", CATEGORY_TO_JAR.get(category, "Thiết yếu"))
    account  = pending.get("account", "Cash")
    desc     = pending["description"]

    type_label = "💰 Thu" if tx_type == "income" else "💸 Chi"

    # Determine jar display
    if category in AUTO_DISTRIBUTE_CATEGORIES and not jar:
        jar_line = "\n🪣 Hũ tiền: <b>Tự động phân bổ 6 hũ</b> ✨"
    elif jar:
        jar_line = f"\n🪣 Hũ tiền: <b>{jar}</b>"
    else:
        jar_line = "\n🪣 Hũ tiền: <b>Thiết yếu</b>"

    # Show USD→VND conversion hint if original text contained $
    import re as _re
    orig = pending.get("original_text", "")
    usd_match = _re.search(r'[+\-]?(\d+(?:[.,]\d+)?)\s*\$|[+\-]?\$\s*(\d+(?:[.,]\d+)?)|(\d+(?:[.,]\d+)?)\s*(?:usd|dollar|đô)', orig, _re.IGNORECASE)
    usd_note = ""
    if usd_match:
        raw_usd = usd_match.group(1) or usd_match.group(2) or usd_match.group(3)
        if raw_usd:
            usd_note = f"\n💱 <i>≈ {raw_usd}$ × 26,236đ/USD</i>"

    text = (
        f"📋 <b>Xác nhận giao dịch?</b>\n\n"
        f"💬 <i>{desc}</i>\n"
        f"─────────────────\n"
        f"{type_label}: <b>{amount_display}</b>{usd_note}\n"
        f"📁 Danh mục: <b>{category}</b>"
        f"{jar_line}\n"
        f"🏦 Tài khoản: <b>{account}</b>\n"
        f"─────────────────\n"
        f"Thông tin đúng chưa? Nhấn <b>Xác nhận</b> để ghi vào Sheets."
    )

    toggle_label = "💰 Đổi → Thu" if tx_type == "expense" else "💸 Đổi → Chi"
    keyboard = [
        [InlineKeyboardButton("✅ Xác nhận ghi", callback_data="txn_confirm")],
        [
            InlineKeyboardButton(toggle_label,       callback_data="txn_toggle_type"),
            InlineKeyboardButton("📁 Danh mục",      callback_data="txn_cat_menu"),
        ],
        [
            InlineKeyboardButton("🪣 Hũ tiền",       callback_data="txn_jar_menu"),
            InlineKeyboardButton("🏦 Tài khoản",     callback_data="txn_acct_menu"),
        ],
        [InlineKeyboardButton("❌ Huỷ", callback_data="txn_cancel")],
    ]
    return text, InlineKeyboardMarkup(keyboard)


async def handle_quick_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    user_id = update.effective_user.id

    if message_text in [BTN_OVERVIEW, BTN_RECORD, BTN_WEEKLY, BTN_INSIGHT,
                        BTN_DRIVE, BTN_WEBAPP, BTN_REFERRAL, BTN_SETTINGS]:
        return

    parsed = parse_natural_language_transaction(message_text)

    # ── AI fallback khi standard parser không nhận được số tiền ──────────────
    if "error" in parsed:
        from config.settings import settings
        if settings.OPENAI_API_KEY:
            parsed = await ai_parse_transaction(message_text, settings.OPENAI_API_KEY)

    if "error" in parsed:
        await update.message.reply_text(
            f"❌ {parsed['error']}",
            reply_markup=get_main_keyboard()
        )
        raise ApplicationHandlerStop

    parsed["jar"]     = CATEGORY_TO_JAR.get(parsed["category"], "Thiết yếu")
    parsed["account"] = "Cash"  # default account ID
    context.user_data["pending_tx"] = parsed

    text, keyboard = _make_preview(parsed)
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    raise ApplicationHandlerStop


_GAS_API_KEY = "fwb_bot_production_2026"

# Map jar name → jar ID for GAS
_JAR_NAME_TO_ID = {
    "Thiết yếu":  "NEC",
    "Vui chơi":   "PLAY",
    "Giáo dục":   "EDU",
    "Tiết kiệm":  "LTSS",
    "Cho đi":     "GIVE",
    "Tự do TC":   "FFA",
}


def _save_transaction_sync(user_id: int, pending: dict):
    """Sync DB work — must only return primitive values, never SQLAlchemy objects."""
    db: Session = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        transaction = Transaction(
            user_id=user_id,
            amount=pending["amount"],
            category=pending["category"],
            description=pending["description"],
            transaction_type=pending["type"],
            created_at=datetime.utcnow()
        )
        db.add(transaction)
        if user and not user.first_transaction_at:
            user.first_transaction_at = datetime.utcnow()
        db.commit()
        db.refresh(transaction)
        # Extract primitives BEFORE closing session — never leak ORM objects
        tx_id = transaction.id
        web_app_url = str(user.web_app_url) if user and user.web_app_url else None
        return True, "", web_app_url, tx_id
    except Exception as e:
        db.rollback()
        return False, str(e), None, None
    finally:
        db.close()


async def _save_transaction(user_id: int, pending: dict):
    """Save transaction to local DB. Returns (success, error_msg, web_app_url, transaction_id)."""
    return await run_sync(_save_transaction_sync, user_id, pending)


async def _sync_to_gas(transaction_id: int, user_id: int, pending: dict, web_app_url: str):
    """Fire-and-forget GAS sync running in background."""
    jar_name = pending.get("jar", "")
    category = pending.get("category", "")
    # Auto-distribute income → send empty jarId so GAS distributes across all 6 jars
    # (GAS treats Thu transaction with empty jarId as auto-allocation)
    if not jar_name and category in AUTO_DISTRIBUTE_CATEGORIES:
        jar_id = ""
    else:
        jar_id = _JAR_NAME_TO_ID.get(jar_name, jar_name) if jar_name else "NEC"
    tx_type  = "Thu" if pending["type"] == "income" else "Chi"
    account  = _resolve_account_id(pending.get("account", "Cash"))
    # Both Thu and Chi use sourceAccount (column G) — matching existing sheet data convention.
    # destinationAccount is only used for transfer transactions.
    src_acc  = account
    dst_acc  = ""

    payload = {
        "action":  "addTransaction",
        "api_key": _GAS_API_KEY,
        "data": {
            "date":               datetime.utcnow().strftime("%d/%m/%Y"),
            "type":               tx_type,
            "jarId":              jar_id,
            "category":           pending["category"],
            "amount":             abs(pending["amount"]),
            "sourceAccount":      src_acc,
            "destinationAccount": dst_acc,
            "note":               pending["description"],
        }
    }
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            resp = await session.post(web_app_url, json=payload)
            raw_text = await resp.text()
        try:
            import json as _json
            result = _json.loads(raw_text)
        except Exception:
            logger.warning(f"⚠️ GAS non-JSON response (HTTP {resp.status}): {raw_text[:300]}")
            return
        if result.get("success"):
            # Update sync flag in DB via thread to avoid blocking event loop
            def _mark_synced_sync(tx_id: int):
                db: Session = next(get_db())
                try:
                    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
                    if tx:
                        tx.synced_to_sheets = True
                        tx.synced_at = datetime.utcnow()
                        db.commit()
                finally:
                    db.close()
            await run_sync(_mark_synced_sync, transaction_id)
            logger.info(f"✅ GAS sync OK: txId={result.get('transactionId')} user={user_id}")
        else:
            logger.warning(f"⚠️ GAS addTransaction failed: {result}")
    except Exception as e:
        logger.warning(f"⚠️ GAS sync exception [{type(e).__name__}]: {e}")


async def handle_txn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data    = query.data
    user_id = update.effective_user.id

    pending = context.user_data.get("pending_tx")
    if not pending:
        await query.edit_message_text("⚠️ Phiên giao dịch đã hết hạn. Vui lòng nhập lại.")
        return

    if data == "txn_confirm":
        success, err, web_app_url, tx_id = await _save_transaction(user_id, pending)
        context.user_data.pop("pending_tx", None)
        if not success:
            await query.edit_message_text(f"❌ Lỗi khi lưu: {err}\n\nVui lòng thử lại.")
            return

        # ── Show ✅ IMMEDIATELY — don't wait for GAS ──────────────────
        amount_display = format_vnd(abs(pending["amount"]))
        type_label = "Thu" if pending["type"] == "income" else "Chi"
        emoji = "💰" if pending["type"] == "income" else "💸"
        cat = pending.get("category", "")
        jar_val = pending.get("jar", "")
        if cat in AUTO_DISTRIBUTE_CATEGORIES and not jar_val:
            jar_line = "\n🪣 Tự động phân bổ 6 hũ ✨"
        elif jar_val:
            jar_line = f"\n🪣 Hũ: {jar_val}"
        else:
            jar_line = "\n🪣 Hũ: Thiết yếu"
        done_text = (
            f"✅ <b>Đã ghi thành công!</b>\n\n"
            f"{emoji} {type_label}: <b>{amount_display}</b>\n"
            f"📁 {pending['category']}{jar_line}\n"
            f"🏦 {pending.get('account', 'Cash')}\n\n"
            f"<i>⏳ Đang đồng bộ Google Sheets...</i>"
        )
        btns = InlineKeyboardMarkup([[
            InlineKeyboardButton("🪣 Xem số dư hũ",      callback_data="reminder_view_report"),
            InlineKeyboardButton("📊 Báo cáo",            callback_data="rpt_menu"),
        ]])
        await query.edit_message_text(done_text, parse_mode="HTML", reply_markup=btns)

        # ── Fire GAS sync in background ───────────────────────────────
        if web_app_url and tx_id:
            import asyncio
            asyncio.create_task(_sync_to_gas(tx_id, user_id, pending, web_app_url))
        return

    if data == "txn_cancel":
        context.user_data.pop("pending_tx", None)
        await query.edit_message_text("❌ Đã huỷ giao dịch.")
        return

    if data == "txn_toggle_type":
        pending["type"] = "income" if pending["type"] == "expense" else "expense"
        from bot.core.categories import detect_category
        pending["category"] = detect_category(pending["description"], pending["type"])
        pending["jar"] = CATEGORY_TO_JAR.get(pending["category"], "")
        context.user_data["pending_tx"] = pending
        text, keyboard = _make_preview(pending)
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
        return

    if data == "txn_cat_menu":
        cats = get_all_categories(pending["type"])
        rows = []
        for i in range(0, len(cats), 3):
            row = [InlineKeyboardButton(c, callback_data=f"txn_cat_{c}") for c in cats[i:i+3]]
            rows.append(row)
        rows.append([InlineKeyboardButton("« Quay lại", callback_data="txn_back")])
        await query.edit_message_text(
            "📁 <b>Chọn danh mục:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("txn_cat_"):
        cat = data[len("txn_cat_"):]
        pending["category"] = cat
        pending["jar"] = CATEGORY_TO_JAR.get(cat, "Thiết yếu")
        context.user_data["pending_tx"] = pending
        text, keyboard = _make_preview(pending)
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
        return

    if data == "txn_jar_menu":
        rows = [[InlineKeyboardButton(j, callback_data=f"txn_jar_{j}")] for j in JARS]
        rows.append([InlineKeyboardButton("« Quay lại", callback_data="txn_back")])
        await query.edit_message_text(
            "🪣 <b>Chọn hũ tiền:</b>\n\n"
            "• <b>Thiết yếu</b> (55%) — ăn uống, nhà ở, đi lại\n"
            "• <b>Giáo dục</b> (10%) — học tập, sách, khóa học\n"
            "• <b>Tiết kiệm</b> (10%) — tiết kiệm dài hạn\n"
            "• <b>Vui chơi</b> (10%) — giải trí, mua sắm\n"
            "• <b>Cho đi</b> (5%) — quà tặng, từ thiện\n"
            "• <b>Tự do TC</b> (10%) — đầu tư, tài chính tự do",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("txn_jar_"):
        jar = data[len("txn_jar_"):]
        pending["jar"] = jar
        context.user_data["pending_tx"] = pending
        text, keyboard = _make_preview(pending)
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
        return

    if data == "txn_acct_menu":
        rows = [[InlineKeyboardButton(a, callback_data=f"txn_acct_{a}")] for a in ACCOUNTS]
        rows.append([InlineKeyboardButton("« Quay lại", callback_data="txn_back")])
        await query.edit_message_text(
            "🏦 <b>Chọn tài khoản:</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(rows)
        )
        return

    if data.startswith("txn_acct_"):
        acct = data[len("txn_acct_"):]
        pending["account"] = _resolve_account_id(acct)  # store GAS account ID
        context.user_data["pending_tx"] = pending
        text, keyboard = _make_preview(pending)
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
        return

    if data == "txn_back":
        text, keyboard = _make_preview(pending)
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=keyboard)
        return


async def handle_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    def _overview_sync(uid: int) -> str:
        from bot.core.awareness import get_awareness_snapshot, format_awareness_message
        db: Session = next(get_db())
        try:
            snapshot = get_awareness_snapshot(uid, db)
            return format_awareness_message(snapshot)
        finally:
            db.close()

    message = await run_sync(_overview_sync, user_id)
    message += "\n💡 Gõ nhanh: 'Cà phê 35k' để ghi ngay!"
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=get_main_keyboard())


async def handle_record_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        f"➕ <b>Ghi giao dịch nhanh</b>\n\n"
        f"Chỉ cần gõ vào ô chat, ví dụ:\n\n"
        f"• <code>Cà phê 35k</code>\n"
        f"• <code>Ăn trưa 50k</code>\n"
        f"• <code>Grab 40k</code>\n"
        f"• <code>Lương 15tr</code>\n\n"
        f"Bot sẽ phân tích và đề xuất:\n"
        f"✅ Loại: Thu / Chi\n"
        f"✅ Danh mục (Ăn uống, Di chuyển...)\n"
        f"✅ Hũ tiền (Thiết yếu, Vui chơi...)\n"
        f"✅ Tài khoản (Tiền mặt, Ngân hàng...)\n\n"
        f"Bạn xác nhận rồi mới ghi vào Sheets! 💬"
    )
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=get_main_keyboard())
    raise ApplicationHandlerStop


async def handle_weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    def _weekly_sync(uid: int) -> str:
        from bot.core.reflection import generate_weekly_insight, format_weekly_insight_message
        db: Session = next(get_db())
        try:
            insight = generate_weekly_insight(uid, db)
            return format_weekly_insight_message(insight)
        finally:
            db.close()

    message = await run_sync(_weekly_sync, user_id)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=get_main_keyboard())


async def handle_insight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    def _insight_sync(uid: int) -> str:
        from bot.core.behavioral import get_behavioral_snapshot, format_behavioral_message
        db: Session = next(get_db())
        try:
            snapshot = get_behavioral_snapshot(uid, db)
            return format_behavioral_message(snapshot)
        finally:
            db.close()

    message = await run_sync(_insight_sync, user_id)
    await update.message.reply_text(message, parse_mode='HTML', reply_markup=get_main_keyboard())


# ─────────────────────────────────────────────
# ⚙️ Cài đặt — helpers
# ─────────────────────────────────────────────
def _settings_keyboard(r_enabled, r_hour, w_enabled, m_enabled):
    remind_icon   = "🔔" if r_enabled  else "🔕"
    remind_status = "✅ Bật" if r_enabled  else "❌ Tắt"
    weekly_status = "✅ Bật" if w_enabled  else "❌ Tắt"
    monthly_status = "✅ Bật" if m_enabled else "❌ Tắt"
    return InlineKeyboardMarkup([
        # ── Section header ───────────────────
        [InlineKeyboardButton("⏰  NHẮC NHỞ", callback_data="settings_noop")],
        [InlineKeyboardButton(f"{remind_icon} Nhắc ghi chi tiêu: {remind_status}",
                              callback_data="settings_toggle_reminder")],
        [InlineKeyboardButton(f"🕘 Giờ nhắc: {r_hour:02d}:00",
                              callback_data="settings_pick_hour")],
        [InlineKeyboardButton(f"📆 Tổng kết tuần: {weekly_status}",
                              callback_data="settings_toggle_weekly")],
        [InlineKeyboardButton(f"📊 Báo cáo tháng: {monthly_status}",
                              callback_data="settings_toggle_monthly")],
        # ── Divider ──────────────────────────
        [InlineKeyboardButton("──────────────────────────", callback_data="settings_noop")],
        # ── Section header ───────────────────
        [InlineKeyboardButton("🔗  KẾT NỐI", callback_data="settings_noop")],
        [InlineKeyboardButton("📋 Thay Google Sheet", callback_data="settings_change_sheet")],
        [InlineKeyboardButton("🔄 Thay Web App URL",  callback_data="settings_change_webapp")],
    ])


def _get_user_settings(user_id):
    """Return (r_enabled, r_hour, w_enabled, m_enabled) from DB."""
    _db = next(get_db())
    try:
        _u = _db.query(User).filter(User.id == user_id).first()
        if not _u:
            return True, 8, True, True
        return (
            bool(_u.reminder_enabled),
            int(getattr(_u, "reminder_hour", 8) or 8),
            bool(getattr(_u, "weekly_reminder_enabled", True)),
            bool(getattr(_u, "monthly_reminder_enabled", True)),
        )
    finally:
        _db.close()


async def handle_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    r_en, r_hr, w_en, m_en = await run_sync(_get_user_settings, user_id)
    await update.message.reply_text(
        "⚙️ <b>Cài đặt</b>\n\nTuỳ chỉnh nhắc nhở và kết nối của bạn:",
        parse_mode="HTML",
        reply_markup=_settings_keyboard(r_en, r_hr, w_en, m_en),
    )
    raise ApplicationHandlerStop


# ─────────────────────────────────────────────
# ⚙️ Cài đặt — callbacks
# ─────────────────────────────────────────────
async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    data    = query.data
    user_id = update.effective_user.id

    # ── No-op (section headers / dividers) ──────────────────────────
    if data == "settings_noop":
        await query.answer()
        return

    # ── Hour picker sub-keyboard ─────────────────────────────────────
    if data == "settings_pick_hour":
        await query.answer()
        hour_rows = []
        row = []
        for h in range(5, 23):
            row.append(InlineKeyboardButton(f"{h:02d}:00", callback_data=f"settings_hour_{h}"))
            if len(row) == 6:
                hour_rows.append(row)
                row = []
        if row:
            hour_rows.append(row)
        hour_rows.append([InlineKeyboardButton("⬅️ Quay lại", callback_data="settings_back")])
        await query.edit_message_text(
            "🕘 <b>Chọn giờ nhắc</b>\n\nGiờ nào bạn muốn nhận nhắc ghi chi tiêu?",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(hour_rows),
        )
        return

    # ── Set hour ─────────────────────────────────────────────────────
    if data.startswith("settings_hour_"):
        hour = int(data.split("_")[-1])
        def _set_hour(_uid, _h):
            _db = next(get_db())
            try:
                _u = _db.query(User).filter(User.id == _uid).first()
                if _u:
                    _u.reminder_hour = _h
                    _db.commit()
            finally:
                _db.close()
        await run_sync(_set_hour, user_id, hour)
        await query.answer(f"✅ Đã đặt nhắc lúc {hour:02d}:00")
        r_en, r_hr, w_en, m_en = await run_sync(_get_user_settings, user_id)
        await query.edit_message_text(
            "⚙️ <b>Cài đặt</b>\n\nTuỳ chỉnh nhắc nhở và kết nối của bạn:",
            parse_mode="HTML",
            reply_markup=_settings_keyboard(r_en, r_hr, w_en, m_en),
        )
        return

    # ── Back (from hour picker) ──────────────────────────────────────
    if data == "settings_back":
        await query.answer()
        r_en, r_hr, w_en, m_en = await run_sync(_get_user_settings, user_id)
        await query.edit_message_text(
            "⚙️ <b>Cài đặt</b>\n\nTuỳ chỉnh nhắc nhở và kết nối của bạn:",
            parse_mode="HTML",
            reply_markup=_settings_keyboard(r_en, r_hr, w_en, m_en),
        )
        return

    # ── Toggle reminder_enabled ──────────────────────────────────────
    if data == "settings_toggle_reminder":
        def _toggle_reminder(_uid):
            _db = next(get_db())
            try:
                _u = _db.query(User).filter(User.id == _uid).first()
                if _u:
                    _u.reminder_enabled = not bool(_u.reminder_enabled)
                    _db.commit()
            finally:
                _db.close()
        await run_sync(_toggle_reminder, user_id)
        r_en, r_hr, w_en, m_en = await run_sync(_get_user_settings, user_id)
        await query.answer("🔔 Đã bật nhắc nhở!" if r_en else "🔕 Đã tắt nhắc nhở!")
        await query.edit_message_reply_markup(
            reply_markup=_settings_keyboard(r_en, r_hr, w_en, m_en)
        )
        return

    # ── Toggle weekly_reminder_enabled ───────────────────────────────
    if data == "settings_toggle_weekly":
        def _toggle_weekly(_uid):
            _db = next(get_db())
            try:
                _u = _db.query(User).filter(User.id == _uid).first()
                if _u:
                    _u.weekly_reminder_enabled = not bool(getattr(_u, "weekly_reminder_enabled", True))
                    _db.commit()
            finally:
                _db.close()
        await run_sync(_toggle_weekly, user_id)
        r_en, r_hr, w_en, m_en = await run_sync(_get_user_settings, user_id)
        await query.answer("📆 Đã bật tổng kết tuần!" if w_en else "📆 Đã tắt tổng kết tuần!")
        await query.edit_message_reply_markup(
            reply_markup=_settings_keyboard(r_en, r_hr, w_en, m_en)
        )
        return

    # ── Toggle monthly_reminder_enabled ──────────────────────────────
    if data == "settings_toggle_monthly":
        def _toggle_monthly(_uid):
            _db = next(get_db())
            try:
                _u = _db.query(User).filter(User.id == _uid).first()
                if _u:
                    _u.monthly_reminder_enabled = not bool(getattr(_u, "monthly_reminder_enabled", True))
                    _db.commit()
            finally:
                _db.close()
        await run_sync(_toggle_monthly, user_id)
        r_en, r_hr, w_en, m_en = await run_sync(_get_user_settings, user_id)
        await query.answer("📊 Đã bật báo cáo tháng!" if m_en else "📊 Đã tắt báo cáo tháng!")
        await query.edit_message_reply_markup(
            reply_markup=_settings_keyboard(r_en, r_hr, w_en, m_en)
        )
        return

    # ── Change Google Sheet ──────────────────────────────────────────
    if data == "settings_change_sheet":
        await query.answer()
        context.user_data["awaiting_settings"] = "sheet"
        await query.edit_message_text(
            "📋 <b>Thay Google Sheet</b>\n\n"
            "Gửi <b>Webhook URL</b> mới của Google Apps Script cho mình nhé.\n\n"
            "<i>Ví dụ: https://script.google.com/macros/s/.../exec</i>\n\n"
            "Nhấn /cancel để huỷ.",
            parse_mode="HTML",
        )
        return

    # ── Change Web App URL ───────────────────────────────────────────
    if data == "settings_change_webapp":
        await query.answer()
        context.user_data["awaiting_settings"] = "webapp"
        await query.edit_message_text(
            "🔄 <b>Thay Web App URL</b>\n\n"
            "Gửi <b>Web App URL</b> mới của bạn nhé.\n\n"
            "<i>Ví dụ: https://script.google.com/macros/s/.../exec</i>\n\n"
            "Nhấn /cancel để huỷ.",
            parse_mode="HTML",
        )
        return

    await query.answer()


# ─────────────────────────────────────────────
# ⚙️ Cài đặt — URL input handler
# ─────────────────────────────────────────────
async def handle_settings_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catch URL text when user is updating sheet/webapp via settings."""
    awaiting = context.user_data.get("awaiting_settings")
    if not awaiting:
        return  # not our turn

    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text(
            "⚠️ URL không hợp lệ. Vui lòng gửi link bắt đầu bằng https://...\nHoặc /cancel để huỷ."
        )
        raise ApplicationHandlerStop

    user_id = update.effective_user.id

    def _save_url_sync(_uid, _field, _url):
        _db = next(get_db())
        try:
            _u = _db.query(User).filter(User.id == _uid).first()
            if _u:
                setattr(_u, _field, _url)
                _db.commit()
        finally:
            _db.close()

    if awaiting == "sheet":
        await run_sync(_save_url_sync, user_id, "webhook_url", url)
        context.user_data.pop("awaiting_settings", None)
        display = f"<code>{url[:80]}...</code>" if len(url) > 80 else f"<code>{url}</code>"
        await update.message.reply_text(
            f"✅ <b>Đã cập nhật Google Sheet Webhook!</b>\n\n{display}",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
    elif awaiting == "webapp":
        await run_sync(_save_url_sync, user_id, "web_app_url", url)
        context.user_data.pop("awaiting_settings", None)
        display = f"<code>{url[:80]}...</code>" if len(url) > 80 else f"<code>{url}</code>"
        await update.message.reply_text(
            f"✅ <b>Đã cập nhật Web App URL!</b>\n\n{display}",
            parse_mode="HTML",
            reply_markup=get_main_keyboard(),
        )
    raise ApplicationHandlerStop


# ─────────────────────────────────────────────
# 📊 Báo cáo menu
# ─────────────────────────────────────────────
async def handle_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show report type/period selection inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📈 Thu chi",    callback_data="rpt_thu_chi"),
            InlineKeyboardButton("💳 Tài khoản",  callback_data="rpt_tai_khoan"),
            InlineKeyboardButton("🪣 Hũ tiền",    callback_data="rpt_hu_tien"),
        ],
        [
            InlineKeyboardButton("📅 Hôm nay",    callback_data="rpt_today"),
            InlineKeyboardButton("📆 Tuần này",   callback_data="rpt_week"),
            InlineKeyboardButton("🗓 Tháng này",  callback_data="rpt_month"),
        ],
    ]
    await update.message.reply_text(
        "📊 <b>Báo cáo tài chính</b>\n\n"
        "Chọn loại báo cáo hoặc khoảng thời gian:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    raise ApplicationHandlerStop


async def handle_report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rpt_ callbacks — fetch from Sheets and filter/display."""
    query = update.callback_query
    await query.answer()
    data    = query.data
    user_id = update.effective_user.id

    # Map to display labels
    TYPE_LABELS  = {"rpt_thu_chi": "Thu chi", "rpt_tai_khoan": "Tài khoản", "rpt_hu_tien": "Hũ tiền"}
    PERIOD_LABELS = {"rpt_today": "hôm nay", "rpt_week": "tuần này", "rpt_month": "tháng này"}

    if data in TYPE_LABELS:
        label = TYPE_LABELS[data]
        context.user_data["rpt_type"] = data
        keyboard = [[
            InlineKeyboardButton("📅 Hôm nay",  callback_data="rpt_today"),
            InlineKeyboardButton("📆 Tuần này", callback_data="rpt_week"),
            InlineKeyboardButton("🗓 Tháng này", callback_data="rpt_month"),
        ]]
        await query.edit_message_text(
            f"📊 <b>{label}</b> — Chọn khoảng thời gian:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data in PERIOD_LABELS:
        rpt_type = context.user_data.get("rpt_type", "rpt_thu_chi")
        type_label   = TYPE_LABELS.get(rpt_type, "Thu chi")
        period_label = PERIOD_LABELS[data]

        # Fetch web_app_url via thread to avoid blocking event loop
        def _get_webapp_url(_uid):
            from bot.utils.database import get_db, User
            _db = next(get_db())
            try:
                _u = _db.query(User).filter(User.id == _uid).first()
                return str(_u.web_app_url) if _u and _u.web_app_url else None
            finally:
                _db.close()
        web_app_url = await run_sync(_get_webapp_url, user_id)

        if not web_app_url:
            await query.edit_message_text(
                "⚠️ Bạn chưa kết nối Web App.\n\n"
                "Vào <b>📂 Mở Google Sheet</b> → cài đặt kết nối để xem báo cáo!",
                parse_mode="HTML"
            )
            return

        await query.edit_message_text("🔄 Đang lấy dữ liệu từ Sheets...")
        _KEY = "fwb_bot_production_2026"
        try:
            timeout = aiohttp.ClientTimeout(total=20)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async def _fetch_balance():
                    r = await session.post(web_app_url, json={"action": "getBalance", "api_key": _KEY})
                    return await r.json(content_type=None)

                async def _fetch_transactions():
                    r = await session.post(web_app_url, json={"action": "getTransactions", "data": {"limit": 20}, "api_key": _KEY})
                    return await r.json(content_type=None)

                bal_data, tx_data = await asyncio.gather(_fetch_balance(), _fetch_transactions())

            lines = [f"<b>📊 {type_label} — {period_label.capitalize()}</b>\n"]

            if rpt_type == "rpt_hu_tien" and bal_data.get("success"):
                jars  = bal_data.get("jars", [])
                total = bal_data.get("totalBalance", 0)
                lines.append("━━━━━━━━━━━━━━━")
                for j in jars:
                    raw_icon = j.get("icon", "")
                    icon = raw_icon if (raw_icon and not raw_icon.startswith("http")) else "🪣"
                    name = j.get("name", "?")
                    bal  = j.get("balance", 0)
                    pct  = j.get("percentage", 0)
                    lines.append(f"{icon} {name} ({pct}%): <b>{bal:,.0f}đ</b>")
                lines.append(f"\n💰 Tổng: <b>{total:,.0f}đ</b>")

            elif rpt_type == "rpt_tai_khoan" and bal_data.get("success"):
                accounts = bal_data.get("accounts", [])
                lines.append("━━━━━━━━━━━━━━━")
                for a in accounts:
                    raw_icon = a.get("icon", "")
                    icon = raw_icon if (raw_icon and not raw_icon.startswith("http")) else "💳"
                    name = a.get("name", "?")
                    bal  = a.get("balance", 0)
                    lines.append(f"{icon} {name}: <b>{bal:,.0f}đ</b>")

            elif rpt_type == "rpt_thu_chi" and tx_data.get("success"):
                from datetime import datetime, timedelta
                now = datetime.now()
                if data == "rpt_today":
                    since = now.replace(hour=0, minute=0, second=0, microsecond=0)
                elif data == "rpt_week":
                    since = now - timedelta(days=now.weekday())
                    since = since.replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

                txs = tx_data.get("transactions", [])
                income = sum(t.get("amount", 0) for t in txs if t.get("type") in ("income", "Thu"))
                expense = sum(t.get("amount", 0) for t in txs if t.get("type") in ("expense", "Chi"))
                lines.append("━━━━━━━━━━━━━━━")
                lines.append(f"💰 Thu: <b>{income:,.0f}đ</b>")
                lines.append(f"💸 Chi: <b>{expense:,.0f}đ</b>")
                lines.append(f"📊 Chênh lệch: <b>{income - expense:,.0f}đ</b>")

            back_btn = InlineKeyboardMarkup([[
                InlineKeyboardButton("📊 Xem chi tiết Sheets", callback_data="reminder_view_report"),
                InlineKeyboardButton("🔄 Báo cáo khác", callback_data="rpt_menu"),
            ]])
            await query.edit_message_text("\n".join(lines), parse_mode="HTML", reply_markup=back_btn)

        except Exception as e:
            await query.edit_message_text(f"❌ Lỗi kết nối: {str(e)[:120]}")
        return

    if data == "rpt_menu":
        keyboard = [
            [
                InlineKeyboardButton("📈 Thu chi",   callback_data="rpt_thu_chi"),
                InlineKeyboardButton("💳 Tài khoản", callback_data="rpt_tai_khoan"),
                InlineKeyboardButton("🪣 Hũ tiền",   callback_data="rpt_hu_tien"),
            ],
            [
                InlineKeyboardButton("📅 Hôm nay",   callback_data="rpt_today"),
                InlineKeyboardButton("📆 Tuần này",  callback_data="rpt_week"),
                InlineKeyboardButton("🗓 Tháng này", callback_data="rpt_month"),
            ],
            [InlineKeyboardButton("📊 Xem tất cả (Sheets)", callback_data="reminder_view_report")],
        ]
        await query.edit_message_text(
            "📊 <b>Báo cáo tài chính</b>\n\nChọn loại báo cáo hoặc khoảng thời gian:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


# ─────────────────────────────────────────────
# 📂 Mở Google Sheet
# ─────────────────────────────────────────────
async def handle_open_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open user's Google Sheet directly."""
    user_id = update.effective_user.id

    def _get_sheets_url(_uid):
        _db: Session = next(get_db())
        try:
            _u = _db.query(User).filter(User.id == _uid).first()
            return str(_u.google_sheets_url) if _u and _u.google_sheets_url else None
        finally:
            _db.close()

    sheets_url = await run_sync(_get_sheets_url, user_id)

    if sheets_url:
        await update.message.reply_text(
            "📂 <b>Google Sheet của bạn</b>\n\nNhấn để mở:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📂 Mở Google Sheet", url=sheets_url)
            ]])
        )
    else:
        await update.message.reply_text(
            "⚠️ <b>Chưa có link Google Sheet</b>\n\n"
            "Bạn cần kết nối Google Sheet trước.\n\n"
            "📖 Nhấn <b>Hướng dẫn</b> → <i>Tạo Web App</i> để bắt đầu.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    raise ApplicationHandlerStop


# ─────────────────────────────────────────────
# 🔗 Chia sẻ
# ─────────────────────────────────────────────
async def handle_share(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Share bot with personal affiliate link + referral stats."""
    import urllib.parse
    user_id      = update.effective_user.id
    bot_username = context.bot.username

    # ── Fetch or create referral code (via thread) ─────────────────
    def _get_ref_sync(_uid):
        from bot.utils.database import generate_referral_code
        _db = next(get_db())
        try:
            _u = _db.query(User).filter(User.id == _uid).first()
            code  = str(_u.referral_code) if _u and _u.referral_code else None
            count = int(_u.referral_count or 0) if _u else 0
            if not code:
                code = generate_referral_code(_uid)
                if _u:
                    _u.referral_code = code
                    _db.commit()
            return code, count
        finally:
            _db.close()
    ref_code, ref_count = await run_sync(_get_ref_sync, user_id)

    # ── Personal affiliate link ─────────────────────────────────────
    ref_url  = f"https://t.me/{bot_username}?start={ref_code}"
    share_msg = urllib.parse.quote(
        "🪙 Mình đang dùng Freedom Wallet Bot để quản lý tài chính theo phương pháp 6 Hũ Tiền!\n"
        "✅ Ghi giao dịch bằng ngôn ngữ tự nhiên\n"
        "✅ Tự động phân bổ vào 6 hũ\n"
        "✅ Đồng bộ Google Sheets\n"
        "✅ Hoàn toàn miễn phí 🎁\n\n"
        f"👉 Đăng ký ngay: {ref_url}"
    )
    tele_url = f"https://t.me/share/url?url={urllib.parse.quote(ref_url)}&text={share_msg}"
    fb_url   = f"https://www.facebook.com/sharer/sharer.php?u={urllib.parse.quote(ref_url)}"
    zalo_url = f"https://zalo.me/share/url?{urllib.parse.quote(ref_url)}"
    tw_url   = f"https://twitter.com/intent/tweet?text={share_msg}"

    # ── Stats text ──────────────────────────────────────────────────
    stats_line = f"👥 Bạn đã giới thiệu: <b>{ref_count} người</b>\n\n" if ref_count else ""

    text = (
        "🌍 <b>LAN TỎA FREEDOM WALLET</b>\n\n"
        f"{stats_line}"
        "🔗 <b>Link affiliate của bạn:</b>\n"
        f"<code>{ref_url}</code>\n\n"
        "Mỗi người bạn giới thiệu đều được ghi nhận. "
        "Chia sẻ để giúp cộng đồng cùng tiến tới tự do tài chính 💚\n\n"
        "Chọn nền tảng:"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✈️ Telegram", url=tele_url),
            InlineKeyboardButton("📘 Facebook", url=fb_url),
        ],
        [
            InlineKeyboardButton("💬 Zalo",    url=zalo_url),
            InlineKeyboardButton("🐦 Twitter", url=tw_url),
        ],
        [InlineKeyboardButton("📋 Copy link", callback_data=f"share_copy_{ref_url}")],
    ])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    raise ApplicationHandlerStop


# ─────────────────────────────────────────────
# 💝 Đóng góp
# ─────────────────────────────────────────────
async def handle_donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show donation QR + bank info (reads from settings/env)."""
    import os, urllib.parse
    from config.settings import settings

    bank = settings.PAYMENT_BANK_NAME
    name = settings.PAYMENT_ACCOUNT_NAME
    stk  = settings.PAYMENT_ACCOUNT_NUMBER

    # VietQR – no fixed amount (tùy tâm)
    bank_codes = {
        "OCB": "970448", "VIETCOMBANK": "970436", "TECHCOMBANK": "970407",
        "MBBANK": "970422", "AGRIBANK": "970405", "BIDV": "970418",
        "VPBANK": "970432", "SACOMBANK": "970403", "ACB": "970416",
        "VIETINBANK": "970415",
    }
    bank_code = bank_codes.get(bank.upper(), "970448")
    qr_url = (
        f"https://img.vietqr.io/image/{bank_code}-{stk}-compact.jpg?"
        + urllib.parse.urlencode({"accountName": name, "addInfo": "Freedom Wallet"})
    )

    caption = (
        "💝 <b>Đóng góp — Tự do Tài chính cùng nhau</b>\n\n"
        "Freedom Wallet Bot được phát triển <b>miễn phí</b> với tâm huyết giúp "
        "cộng đồng thực hành tài chính lành mạnh theo phương pháp 6 hũ.\n\n"
        "Mọi đóng góp <i>tùy tâm</i> đều giúp:\n"
        "🖥 Duy trì server & chi phí vận hành\n"
        "🚀 Phát triển tính năng mới\n"
        "📚 Xây dựng cộng đồng Tự do Tài chính\n\n"
        "<b>Quét mã QR hoặc chuyển khoản:</b>\n"
        f"🏦 Ngân hàng: <code>{bank}</code>\n"
        f"👤 Chủ TK: <code>{name}</code>\n"
        f"💳 Số TK: <code>{stk}</code>\n\n"
        "<i>Cảm ơn bạn đã đồng hành và tin tưởng! 🙏</i>"
    )

    try:
        await update.message.reply_photo(
            photo=qr_url,
            caption=caption,
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    except Exception:
        # Fallback: local QR file
        qr_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "media", "images", "QR_code.jpg"
        )
        if os.path.exists(qr_path):
            with open(qr_path, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=caption,
                    parse_mode="HTML", reply_markup=get_main_keyboard()
                )
        else:
            await update.message.reply_text(caption, parse_mode="HTML", reply_markup=get_main_keyboard())
    raise ApplicationHandlerStop


# ─────────────────────────────────────────────
# 📖 Hướng dẫn
# ─────────────────────────────────────────────
async def handle_guide_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show guide submenu: Tạo Web App / Kết nối Bot / Sử dụng Web App."""
    keyboard = [
        [InlineKeyboardButton("🛠 Tạo Web App",                callback_data="webapp_step_0")],
        [InlineKeyboardButton("🔗 Cập nhật link & Kết nối Bot", callback_data="connect_webapp_start")],
        [InlineKeyboardButton("📱 Sử dụng Web App",            callback_data="webapp_usage_step_1")],
    ]
    await update.message.reply_text(
        "📖 <b>Hướng dẫn sử dụng Freedom Wallet</b>\n\n"
        "Chọn chủ đề bạn cần hỗ trợ:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    raise ApplicationHandlerStop


# ─────────────────────────────────────────────
# 🌐 Mở Web App
# ─────────────────────────────────────────────
async def handle_open_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open user's Web App directly if set, else guide to setup."""
    uid = update.effective_user.id

    def _get_wa_url(_uid):
        _db = next(get_db())
        try:
            _user = _db.query(User).filter(User.id == _uid).first()
            return str(_user.web_app_url) if _user and _user.web_app_url else None
        finally:
            _db.close()

    wa_url = await run_sync(_get_wa_url, uid)
    if wa_url:
        await update.message.reply_text(
            "🌐 <b>Web App của bạn</b>\n\nNhấn để mở Freedom Wallet Web:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🌐 Mở Web App", url=wa_url)
            ]])
        )
    else:
        await update.message.reply_text(
            "⚠️ <b>Chưa có link Web App</b>\n\n"
            "Bạn chưa kết nối Freedom Wallet Web App.\n"
            "📖 Nhấn <b>Hướng dẫn</b> → <i>Tạo Web App</i> để thiết lập "
            "hoặc gửi link Web App của bạn để cập nhật.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    raise ApplicationHandlerStop


# ─────────────────────────────────────────────
# 💬 Trợ giúp
# ─────────────────────────────────────────────
async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show support links and community info."""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Cộng đồng Freedom Wallet", url="https://t.me/freedomwalletapp")],
        [InlineKeyboardButton("💬 Hỗ trợ nhanh", url="https://t.me/tuanai_mentor")],
    ])
    await update.message.reply_text(
        "💬 <b>Trợ giúp & Cộng đồng</b>\n\n"
        "🆘 <b>Cần hỗ trợ?</b>\n"
        "• Chat trực tiếp: @tuanai_mentor\n"
        "• Cộng đồng: Hỏi đáp, chia sẻ kinh nghiệm\n"
        "• Phản hồi nhanh trong 24h\n\n"
        "📚 <b>Tài liệu:</b>\n"
        "• Video hướng dẫn tại group\n"
        "• Tips & Tricks tài chính\n\n"
        "Chọn kênh hỗ trợ bên dưới:",
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    raise ApplicationHandlerStop


def register_transaction_handlers(application):
    from bot.core.keyboard import (
        BTN_RECORD, BTN_REPORT, BTN_SHEETS, BTN_WEBAPP,
        BTN_SHARE, BTN_DONATE, BTN_GUIDE, BTN_SETTINGS,
    )

    # txn_ callback (confirm/edit flow) — register FIRST
    application.add_handler(CallbackQueryHandler(handle_txn_callback, pattern=r"^txn_"))
    # Report submenu callbacks
    application.add_handler(CallbackQueryHandler(handle_report_callback, pattern=r"^rpt_"))
    # Settings callbacks (toggles, hour picker, URL change)
    application.add_handler(CallbackQueryHandler(handle_settings_callback, pattern=r"^settings_"))
    # Share copy-link callback — data: "share_copy_{ref_url}"
    async def _share_copy_link(update, context):
        data = update.callback_query.data
        link = data[len("share_copy_"):]
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            "🔗 <b>Link affiliate của bạn:</b>\n\n"
            f"<code>{link}</code>\n\n"
            "👆 Nhấn vào link để copy, sau đó paste chia sẻ với bạn bè!",
            parse_mode="HTML",
        )
    application.add_handler(CallbackQueryHandler(_share_copy_link, pattern=r"^share_copy_"))

    application.add_handler(MessageHandler(filters.Text([BTN_RECORD]),   handle_record_button))
    application.add_handler(MessageHandler(filters.Text([BTN_REPORT]),   handle_report_menu))
    application.add_handler(MessageHandler(filters.Text([BTN_SHEETS]),   handle_open_sheets))
    application.add_handler(MessageHandler(filters.Text([BTN_SHARE]),    handle_share))
    application.add_handler(MessageHandler(filters.Text([BTN_DONATE]),   handle_donate))
    application.add_handler(MessageHandler(filters.Text([BTN_GUIDE]),    handle_guide_menu))
    application.add_handler(MessageHandler(filters.Text([BTN_SETTINGS]), handle_settings_menu))

    application.add_handler(MessageHandler(filters.Text([BTN_WEBAPP]), handle_open_webapp))

    # Settings URL input — group=-1 so it fires before the quick_transaction catch-all (group=0)
    # Returns immediately (no stop) if not in awaiting state; raises stop if it processes the URL
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_settings_url_input,
    ), group=-1)

    # Natural language catch-all (must be last)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_quick_transaction
    ))
