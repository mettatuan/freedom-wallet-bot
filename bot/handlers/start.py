"""
Start Command Handler
Unified 3-state routing based on Telegram ID (single source of truth):

  STATE 1 – VISITOR  : is_registered=False           → promo screen
  STATE 2 – SETUP    : is_registered=True, no web_app → setup guide
  STATE 3 – ACTIVE   : is_registered=True, web_app set → main menu

Entry points (all converge to the same state check):
  /start            → plain start (new or returning user)
  /start WEB_<hash> → from freedomwallet.app landing page
  /start REF<code>  → referral link
"""
import asyncio
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from bot.core.keyboard import get_main_keyboard
from bot.core.state_machine import StateManager
from bot.handlers.referral import handle_referral_start
from bot.utils.database import (
    SessionLocal, get_user_by_id, save_user_to_db, update_user_registration,
    run_sync, User,
)
from bot.utils.sheets import sync_web_registration
from config.settings import settings


def _esc(text: str) -> str:
    """Escape Markdown v1 special characters in user-supplied strings."""
    for ch in ('_', '*', '[', '`'):
        text = text.replace(ch, f'\\{ch}')
    return text


# ---------------------------------------------------------------------------
# Screen helpers
# ---------------------------------------------------------------------------

async def _show_visitor_screen(update: Update, user):
    """STATE 1: unregistered user → promo + "Đăng ký ngay"."""
    text = (
        f"Chào {user.first_name}, tôi là Trợ lý tài chính của bạn 👋\n\n"
        f"Freedom Wallet *không phải* một app để bạn tải về.\n"
        f"Đây là *hệ thống* quản lý tự do tài chính bạn *tự sở hữu 100%*.\n\n"
        f"Mỗi người dùng có:\n"
        f"• Google Sheet riêng trên Drive của bạn\n"
        f"• Apps Script riêng do bạn deploy\n"
        f"• Web App riêng chạy trên tài khoản Google của bạn\n\n"
        f"Dữ liệu nằm trên Drive của bạn.\n"
        f"Không phụ thuộc vào ai.\n\n"
        f"Nếu bạn muốn đăng ký sở hữu hệ thống này,\n"
        f"mình sẽ hướng dẫn từng bước, rất rõ ràng. 👇"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Đăng ký ngay", callback_data="start_free_registration")],
        [InlineKeyboardButton("🔍 Tôi đã đăng ký trên web", callback_data="web_already_registered")],
        [InlineKeyboardButton("ℹ️ Tìm hiểu thêm", callback_data="learn_more")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    image_path = Path("media/images/web_apps.jpg")
    try:
        await update.message.reply_photo(
            photo=open(image_path, "rb"),
            caption=text,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    except Exception:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def _show_setup_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, user, db_user):
    """STATE 2: registered but hasn't set up Web App yet → launch guide step-by-step directly."""
    from bot.handlers.webapp_setup import send_webapp_setup_step
    await send_webapp_setup_step(update, context, step=0)


async def _show_active_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user, db_user):
    """STATE 3: fully set up → show main keyboard + inline quick actions."""
    user_name = (
        getattr(db_user, "full_name", None)
        or getattr(db_user, "first_name", None)
        or user.first_name
        or "bạn"
    )

    # Build affiliate link
    try:
        from bot.utils.database import generate_referral_code
        referral_code = generate_referral_code(user.id)
        bot_username = (await context.bot.get_me()).username
        affiliate_link = f"https://t.me/{bot_username}?start=REF{referral_code}"
    except Exception:
        affiliate_link = None

    web_app_url = getattr(db_user, "web_app_url", None)
    sheets_url = getattr(db_user, "google_sheets_url", None)

    text = (
        f"👋 Chào mừng trở lại, *{_esc(user_name)}*!\n\n"
        f"Chọn thao tác bên dưới hoặc dùng menu phím bên dưới màn hình."
    )

    inline_rows = []
    row1 = []
    if web_app_url:
        row1.append(InlineKeyboardButton("🌐 Mở Web App", url=web_app_url))
    if sheets_url:
        row1.append(InlineKeyboardButton("📂 Google Sheet", url=sheets_url))
    if row1:
        inline_rows.append(row1)

    row2 = [
        InlineKeyboardButton("✍️ Ghi giao dịch", callback_data="webapp_record_guide"),
        InlineKeyboardButton("📊 Báo cáo", callback_data="reminder_view_report"),
    ]
    inline_rows.append(row2)

    row3 = [InlineKeyboardButton("📖 Hướng dẫn", callback_data="show_guide_menu")]
    if affiliate_link:
        row3.append(InlineKeyboardButton("🔗 Link giới thiệu", url=affiliate_link))
    inline_rows.append(row3)

    inline_rows.append([InlineKeyboardButton("💝 Đóng góp tùy tâm", callback_data="payment_info")])

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_rows),
    )
    # Also send the persistent reply keyboard
    await update.message.reply_text(
        "Menu nhanh 👇",
        reply_markup=get_main_keyboard(),
    )


# ---------------------------------------------------------------------------
# Main /start handler
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — unified entry point for all channels.

    Identification: Telegram user.id (primary key in DB).
    Routing based purely on DB state — no day-based scheduling.
    """
    user = update.effective_user
    logger.info(f"/start: user {user.id} (@{user.username})")

    # 1. Ensure user row exists
    db_user = await save_user_to_db(user)

    # 2. VIP activity ping
    try:
        with StateManager() as sm:
            sm.update_super_vip_activity(user.id)
    except Exception:
        pass

    # 3. Entry-point pre-processing (no messages here, only DB updates)
    if context.args:
        code = context.args[0]
        logger.info(f"  start code: {code}")

        if code.startswith("WEB_"):
            # ── from freedomwallet.app ──────────────────────────────────
            # Mark registered instantly using Telegram profile (no sheet lookup needed)
            email_hash = code[4:]
            logger.info(f"  WEB_ deep link: hash={email_hash}, user_id={user.id}")
            await update_user_registration(
                user_id=user.id,
                email="",
                phone="",
                full_name=db_user.first_name or user.first_name or "",
                source="WEB",
                referral_count=0,
            )
            logger.info(f"  WEB_ user {user.id} marked registered instantly")

            # Show congratulations then go straight to setup guide
            user_name = user.first_name or "bạn"
            await update.message.reply_text(
                f"🎉 <b>Chúc mừng {user_name} đã đăng ký thành công!</b>\n\n"
                f"Bước tiếp theo: tạo Web App cá nhân của bạn.\n"
                f"Mình sẽ hướng dẫn từng bước, rất đơn giản 👇",
                parse_mode="HTML",
            )
            from bot.handlers.webapp_setup import send_webapp_setup_step
            await send_webapp_setup_step(update, context, step=0)
            return
        else:
            # ── referral link (REFxxx) ──────────────────────────────────
            referred = await handle_referral_start(update, context, code)
            if referred:
                await asyncio.sleep(1)

    # 4. Reload fresh state from DB
    db_user = await get_user_by_id(user.id) or db_user

    # 5. Enable reminders for registered users
    if db_user and db_user.is_registered:
        try:
            def _enable_reminders_sync(uid: int):
                _db = SessionLocal()
                try:
                    _u = _db.query(User).filter(User.id == uid).first()
                    if _u:
                        _u.reminder_enabled = True
                        _db.commit()
                finally:
                    _db.close()
            await run_sync(_enable_reminders_sync, db_user.id)
        except Exception as e:
            logger.error(f"Enable reminders: {e}")

    # 6. ── 3-STATE ROUTING ──────────────────────────────────────────────
    is_registered = bool(db_user and db_user.is_registered)
    has_web_app   = bool(db_user and getattr(db_user, "web_app_url", None))

    if not is_registered:
        # STATE 1: VISITOR
        logger.info(f"  → VISITOR screen for {user.id}")
        await _show_visitor_screen(update, user)

    elif not has_web_app:
        # STATE 2: SETUP (registered, no web app yet)
        logger.info(f"  → SETUP screen for {user.id}")
        await _show_setup_screen(update, context, user, db_user)

    else:
        # STATE 3: ACTIVE (registered + web app set)
        logger.info(f"  → ACTIVE menu for {user.id}")
        await _show_active_menu(update, context, user, db_user)


def _credit_referral_on_web_registration(user_id: int, web_data: dict):
    """Promote referral PENDING → VERIFIED when WEB user is confirmed."""
    try:
        from bot.utils.database import SessionLocal, User as UserModel, Referral
        _db = SessionLocal()
        try:
            referred_by = web_data.get("referred_by")
            if not referred_by:
                return
            referral = (
                _db.query(Referral)
                .filter(Referral.referred_user_id == user_id, Referral.status == "PENDING")
                .first()
            )
            if referral:
                referral.status = "VERIFIED"
                referrer = _db.query(UserModel).filter(UserModel.id == referral.referrer_id).first()
                if referrer:
                    referrer.referral_count = (referrer.referral_count or 0) + 1
                _db.commit()
                logger.info(f"✅ Referral VERIFIED: user {user_id} referred by {referral.referrer_id}")
        finally:
            _db.close()
    except Exception as e:
        logger.error(f"Credit referral WEB: {e}")


async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📋 *Danh Sách Lệnh*\n\n"
        "*/start* – Hiện menu chính\n"
        "*/help* – Hiện menu này\n"
        "*/support* – Liên hệ support\n\n"
        "💬 *Hoặc chat trực tiếp với mình:*\n"
        "Gõ câu hỏi bằng tiếng Việt hoặc English!\n\n"
        "📚 *Ví dụ câu hỏi:*\n"
        "• Làm sao thêm giao dịch?\n"
        "• 6 hũ tiền là gì?\n"
        "• App không load được dữ liệu\n\n"
        "🤖 Mình sẽ trả lời ngay lập tức!"
    )
    keyboard = [[InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]]
    await update.message.reply_text(
        help_text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
