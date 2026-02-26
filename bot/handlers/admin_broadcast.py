"""
Admin Broadcast — Gửi thông báo hàng loạt tới nhóm user cụ thể.

Commands (admin only):
  /broadcast_setup  — Gửi video hướng dẫn tạo Web App tới user chưa setup
  /broadcast_all    — Gửi tin tới TẤT CẢ user đã đăng ký (dùng cẩn thận)
  /broadcast_status — Xem số lượng từng nhóm user

Rate limit: 30 message/giây (Telegram limit).
"""

import asyncio
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram.error import Forbidden, BadRequest

from bot.utils.database import SessionLocal, User
from config.settings import settings

logger = logging.getLogger(__name__)

VIDEO_SETUP_URL = "https://youtu.be/xVoASsuWfto"

SETUP_MESSAGE = (
    "👋 <b>Bạn đã đăng ký Freedom Wallet rồi!</b>\n\n"
    "Bước tiếp theo là tạo <b>Web App cá nhân</b> để:\n"
    "✅ Lưu 100% dữ liệu trong Google Drive của bạn\n"
    "✅ Xem dashboard thu chi trực quan\n"
    "✅ Đồng bộ với Telegram bot tự động\n\n"
    "🎬 <b>Video hướng dẫn từng bước (5 phút):</b>\n"
    f"{VIDEO_SETUP_URL}\n\n"
    "Sau khi tạo xong, gửi link Web App vào đây để kích hoạt bot nhé! 👇"
)


def _is_admin(user_id: int) -> bool:
    return settings.ADMIN_USER_ID and user_id == settings.ADMIN_USER_ID


def _get_users_without_webapp() -> list[User]:
    """Query user đã đăng ký nhưng chưa có web_app_url."""
    db = SessionLocal()
    try:
        users = (
            db.query(User)
            .filter(User.is_registered == True)  # noqa
            .filter(
                (User.web_app_url == None) |  # noqa
                (User.web_app_url == "") |
                (User.web_app_url == "pending")
            )
            .all()
        )
        # Detach từ session để dùng ngoài
        result = []
        for u in users:
            result.append({
                "id": u.id,
                "first_name": u.first_name or "bạn",
                "username": u.username,
            })
        return result
    finally:
        db.close()


def _get_all_registered_users() -> list[dict]:
    """Query tất cả user đã đăng ký."""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.is_registered == True).all()  # noqa
        return [{"id": u.id, "first_name": u.first_name or "bạn", "username": u.username} for u in users]
    finally:
        db.close()


def _get_user_stats() -> dict:
    db = SessionLocal()
    try:
        total = db.query(User).count()
        registered = db.query(User).filter(User.is_registered == True).count()  # noqa
        with_webapp = (
            db.query(User)
            .filter(User.is_registered == True)  # noqa
            .filter(User.web_app_url != None)  # noqa
            .filter(User.web_app_url != "")
            .count()
        )
        without_webapp = registered - with_webapp
        return {
            "total": total,
            "registered": registered,
            "with_webapp": with_webapp,
            "without_webapp": without_webapp,
        }
    finally:
        db.close()


async def _send_broadcast(bot, users: list[dict], message: str, delay: float = 0.05) -> dict:
    """
    Gửi message tới danh sách user với rate limiting.
    Trả về dict: {sent, blocked, failed, total}
    """
    sent = blocked = failed = 0
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎬 Xem video hướng dẫn", url=VIDEO_SETUP_URL),
        InlineKeyboardButton("📋 Hướng dẫn từng bước", callback_data="webapp_setup_step_0"),
    ]])

    for i, user in enumerate(users):
        try:
            await bot.send_message(
                chat_id=user["id"],
                text=message,
                parse_mode="HTML",
                reply_markup=keyboard,
                disable_web_page_preview=False,
            )
            sent += 1
            logger.info(f"[BROADCAST] sent to {user['id']} ({user.get('username', '?')})")
        except Forbidden:
            # User đã block bot
            blocked += 1
            logger.info(f"[BROADCAST] blocked by {user['id']}")
        except BadRequest as e:
            failed += 1
            logger.warning(f"[BROADCAST] bad request for {user['id']}: {e}")
        except Exception as e:
            failed += 1
            logger.warning(f"[BROADCAST] failed for {user['id']}: {e}")

        # Rate limit: 30 msg/s → ~33ms giữa mỗi message
        await asyncio.sleep(delay)

        # Progress log mỗi 10 user
        if (i + 1) % 10 == 0:
            logger.info(f"[BROADCAST] progress: {i+1}/{len(users)} | sent={sent} blocked={blocked} failed={failed}")

    return {"sent": sent, "blocked": blocked, "failed": failed, "total": len(users)}


async def handle_broadcast_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xem số lượng từng nhóm."""
    if not _is_admin(update.effective_user.id):
        return

    import asyncio as _asyncio
    stats = await _asyncio.to_thread(_get_user_stats)

    await update.message.reply_text(
        f"📊 <b>Thống kê User</b>\n\n"
        f"👥 Tổng user: <b>{stats['total']}</b>\n"
        f"✅ Đã đăng ký: <b>{stats['registered']}</b>\n"
        f"🌐 Có Web App: <b>{stats['with_webapp']}</b>\n"
        f"⏳ Chưa có Web App: <b>{stats['without_webapp']}</b>\n\n"
        f"Để gửi video hướng dẫn cho {stats['without_webapp']} user chưa setup:\n"
        f"👉 /broadcast_setup",
        parse_mode="HTML",
    )


async def handle_broadcast_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gửi video hướng dẫn tới user đã đăng ký nhưng chưa tạo Web App."""
    if not _is_admin(update.effective_user.id):
        return

    import asyncio as _asyncio

    # Lấy danh sách
    users = await _asyncio.to_thread(_get_users_without_webapp)

    if not users:
        await update.message.reply_text("✅ Không có user nào cần gửi (tất cả đã setup Web App).")
        return

    # Confirm trước khi gửi
    args = context.args
    if not args or args[0] != "confirm":
        await update.message.reply_text(
            f"📣 Chuẩn bị gửi video hướng dẫn tới <b>{len(users)} user</b> chưa tạo Web App.\n\n"
            f"Preview nội dung:\n{SETUP_MESSAGE[:300]}...\n\n"
            f"✅ Để xác nhận gửi:\n<code>/broadcast_setup confirm</code>",
            parse_mode="HTML",
        )
        return

    # Gửi thông báo bắt đầu
    progress_msg = await update.message.reply_text(
        f"⏳ Đang gửi tới {len(users)} user... (có thể mất vài phút)"
    )

    # Broadcast
    result = await _send_broadcast(context.bot, users, SETUP_MESSAGE)

    # Kết quả
    await progress_msg.edit_text(
        f"✅ <b>Broadcast hoàn thành!</b>\n\n"
        f"📤 Đã gửi: <b>{result['sent']}</b>\n"
        f"🚫 Bị block: <b>{result['blocked']}</b>\n"
        f"❌ Lỗi khác: <b>{result['failed']}</b>\n"
        f"📊 Tổng: {result['total']}\n\n"
        f"⏰ {datetime.now().strftime('%H:%M:%S')}",
        parse_mode="HTML",
    )

    logger.info(f"[BROADCAST] setup complete: {result}")


async def handle_broadcast_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gửi tin tới TẤT CẢ user đã đăng ký — yêu cầu confirm + nội dung."""
    if not _is_admin(update.effective_user.id):
        return

    args = context.args
    if not args or args[0] != "confirm":
        import asyncio as _asyncio
        stats = await _asyncio.to_thread(_get_user_stats)
        await update.message.reply_text(
            f"⚠️ Lệnh này gửi tới <b>TẤT CẢ {stats['registered']} user</b> đã đăng ký.\n\n"
            f"Để gửi, dùng:\n<code>/broadcast_all confirm [nội dung]</code>\n\n"
            f"Ví dụ:\n<code>/broadcast_all confirm 🎉 Freedom Wallet vừa ra tính năng mới!</code>",
            parse_mode="HTML",
        )
        return

    custom_msg = " ".join(args[1:]) if len(args) > 1 else None
    if not custom_msg:
        await update.message.reply_text("❌ Thiếu nội dung. Dùng: /broadcast_all confirm [nội dung]")
        return

    import asyncio as _asyncio
    users = await _asyncio.to_thread(_get_all_registered_users)

    progress_msg = await update.message.reply_text(
        f"⏳ Đang gửi tới {len(users)} user..."
    )

    result = await _send_broadcast(context.bot, users, custom_msg, delay=0.05)

    await progress_msg.edit_text(
        f"✅ <b>Broadcast hoàn thành!</b>\n\n"
        f"📤 Đã gửi: <b>{result['sent']}</b>\n"
        f"🚫 Bị block: <b>{result['blocked']}</b>\n"
        f"❌ Lỗi khác: <b>{result['failed']}</b>",
        parse_mode="HTML",
    )


def register_broadcast_handlers(application):
    application.add_handler(CommandHandler("broadcast_setup", handle_broadcast_setup))
    application.add_handler(CommandHandler("broadcast_all", handle_broadcast_all))
    application.add_handler(CommandHandler("broadcast_status", handle_broadcast_status))
    logger.info("✅ Broadcast handlers registered")
