"""
Health Monitor — Job chạy ngầm mỗi 5 phút kiểm tra sức khoẻ bot.

Kiểm tra:
  1. Log file có ghi được không (disk space / permission)
  2. DB có query được không
  3. Số lỗi gần đây — gửi digest cho admin nếu vượt ngưỡng
  4. Uptime tracking

Admin command: /healthcheck — xem status ngay lập tức
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

_start_time = time.time()


def get_uptime_str() -> str:
    elapsed = int(time.time() - _start_time)
    h, m = divmod(elapsed // 60, 60)
    d, h = divmod(h, 24)
    if d:
        return f"{d}d {h}h {m}m"
    if h:
        return f"{h}h {m}m"
    return f"{m}m"


async def _check_db() -> tuple[bool, str]:
    """Kiểm tra DB có query được không."""
    try:
        from bot.utils.database import SessionLocal, User
        import asyncio as _asyncio

        def _ping():
            db = SessionLocal()
            try:
                db.query(User).limit(1).all()
                return True
            finally:
                db.close()

        await _asyncio.to_thread(_ping)
        return True, "OK"
    except Exception as e:
        return False, str(e)[:80]


async def _check_log_file() -> tuple[bool, str]:
    """Kiểm tra log file có writable không."""
    log_path = Path("data/logs/bot.log")
    try:
        if log_path.exists():
            size_mb = log_path.stat().st_size / 1024 / 1024
            if size_mb > 50:
                return False, f"Log quá lớn: {size_mb:.1f}MB (>50MB)"
            return True, f"{size_mb:.2f}MB"
        return True, "OK (no log yet)"
    except Exception as e:
        return False, str(e)[:80]


async def health_check_job(context: ContextTypes.DEFAULT_TYPE):
    """Chạy mỗi 5 phút, gửi digest nếu có vấn đề nghiêm trọng."""
    from bot.core.error_tracker import get_tracker
    from config.settings import settings

    tracker = get_tracker()
    summary = tracker.get_summary()

    # Chỉ alert nếu có lỗi nghiêm trọng lặp lại nhiều
    critical = [e for e in summary if e["count_window"] >= 10]
    if not critical:
        return  # Bot khoẻ mạnh, không cần báo

    if not settings.ADMIN_USER_ID:
        return

    import html as _html
    lines = []
    for e in critical[:5]:
        lines.append(
            f"• <code>{_html.escape(e['key'][:100])}</code>\n"
            f"  {e['count_window']}x/10min | tổng {e['total']}"
        )

    msg = (
        f"⚠️ <b>Health Monitor Alert</b>\n"
        f"⏱ Uptime: {get_uptime_str()}\n\n"
        f"<b>Lỗi lặp nhiều:</b>\n" + "\n".join(lines) +
        f"\n\n💡 Dùng /admin_errors để xem chi tiết"
    )
    try:
        await context.bot.send_message(
            chat_id=settings.ADMIN_USER_ID,
            text=msg,
            parse_mode="HTML",
        )
    except Exception as e:
        logger.warning(f"HealthMonitor: failed to send digest: {e}")


async def handle_healthcheck_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command /healthcheck — xem status ngay."""
    from config.settings import settings
    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return

    db_ok, db_msg = await _check_db()
    log_ok, log_msg = await _check_log_file()

    from bot.core.error_tracker import get_tracker
    tracker = get_tracker()
    summary = tracker.get_summary()

    db_icon = "✅" if db_ok else "❌"
    log_icon = "✅" if log_ok else "⚠️"

    error_lines = ""
    if summary:
        import html as _html
        lines = []
        for e in summary[:5]:
            lines.append(f"  • {e['count_window']}x — <code>{_html.escape(e['key'][:80])}</code>")
        error_lines = "\n<b>Lỗi gần đây:</b>\n" + "\n".join(lines)
    else:
        error_lines = "\n✅ Không có lỗi bất thường"

    msg = (
        f"🖥️ <b>Bot Health Check</b>\n"
        f"⏱ Uptime: <b>{get_uptime_str()}</b>\n\n"
        f"{db_icon} DB: {db_msg}\n"
        f"{log_icon} Log: {log_msg}\n"
        f"{error_lines}"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def handle_admin_errors_command(update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command /admin_errors — xem tất cả lỗi đang track."""
    from config.settings import settings
    import html as _html

    user_id = update.effective_user.id
    if user_id != settings.ADMIN_USER_ID:
        return

    from bot.core.error_tracker import get_tracker
    tracker = get_tracker()
    summary = tracker.get_summary()

    if not summary:
        await update.message.reply_text("✅ Không có lỗi nào trong 10 phút qua.")
        return

    lines = []
    for i, e in enumerate(summary[:10], 1):
        lines.append(
            f"{i}. <code>{_html.escape(e['key'][:100])}</code>\n"
            f"   📊 {e['count_window']}x/10min | tổng {e['total']} | lần cuối {e['last_seen']}"
        )

    msg = f"📋 <b>Lỗi đang theo dõi (10 phút qua)</b>\n\n" + "\n\n".join(lines)
    await update.message.reply_text(msg, parse_mode="HTML")


def register_health_handlers(application):
    from telegram.ext import CommandHandler
    application.add_handler(CommandHandler("healthcheck", handle_healthcheck_command))
    application.add_handler(CommandHandler("admin_errors", handle_admin_errors_command))
    logger.info("✅ Health monitor handlers registered")
