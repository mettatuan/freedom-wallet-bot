"""
User Feedback — /feedback command để user báo lỗi có context đầy đủ.

Khi user dùng /feedback hoặc gõ "báo lỗi" / "bị lỗi":
  1. Thu thập context: user_id, pending_tx, last messages, user_data keys
  2. Gửi ngay cho admin với đầy đủ thông tin
  3. Trả lời user thân thiện

Format báo cáo gửi admin:
  📣 Phản hồi từ user [tên] (id)
  💬 Nội dung: "..."
  📋 Context: pending_tx, cached_accounts, etc.
  ⏰ Thời gian: ...
"""

import html
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from config.settings import settings

logger = logging.getLogger(__name__)

AWAITING_FEEDBACK = "AWAITING_FEEDBACK"


async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu flow feedback — hỏi user muốn báo gì."""
    await update.message.reply_text(
        "📣 <b>Báo lỗi / Góp ý</b>\n\n"
        "Mô tả ngắn gọn vấn đề bạn gặp phải:\n"
        "<i>(Ví dụ: 'Bot không ghi được giao dịch', 'Bấm xác nhận không thấy phản hồi')</i>\n\n"
        "Hoặc /cancel để bỏ qua.",
        parse_mode="HTML",
    )
    return AWAITING_FEEDBACK


async def feedback_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhận nội dung feedback, gửi cho admin với đầy đủ context."""
    user = update.effective_user
    text = update.message.text

    # Thu thập context từ user_data
    ud = context.user_data or {}
    ctx_parts = []

    pending = ud.get("pending_tx")
    if pending:
        ctx_parts.append(f"pending_tx: {pending}")

    cached_accounts = ud.get("cached_accounts")
    if cached_accounts:
        ctx_parts.append(f"cached_accounts: {len(cached_accounts)} accounts")

    last_account = ud.get("last_account")
    if last_account:
        ctx_parts.append(f"last_account: {last_account}")

    # Các keys còn lại
    other_keys = [k for k in ud.keys() if k not in {"pending_tx", "cached_accounts", "last_account", "conversation_context"}]
    if other_keys:
        ctx_parts.append(f"other_data_keys: {other_keys}")

    context_block = "\n".join(ctx_parts) if ctx_parts else "None"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = f"@{user.username}" if user.username else f"id:{user.id}"

    # Gửi cho admin
    if settings.ADMIN_USER_ID:
        admin_msg = (
            f"📣 <b>Feedback từ user</b>\n\n"
            f"👤 {html.escape(user.full_name or '')} {html.escape(username)}\n"
            f"🆔 <code>{user.id}</code>\n"
            f"⏰ {timestamp}\n\n"
            f"💬 <b>Nội dung:</b>\n<i>{html.escape(text)}</i>\n\n"
            f"📋 <b>Context:</b>\n<code>{html.escape(context_block[:500])}</code>"
        )
        try:
            await context.bot.send_message(
                chat_id=settings.ADMIN_USER_ID,
                text=admin_msg,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Feedback: failed to notify admin: {e}")

    # Log locally
    logger.info(f"[FEEDBACK] user={user.id} | {text[:100]}")

    await update.message.reply_text(
        "✅ Cảm ơn bạn đã phản hồi!\n"
        "Admin sẽ xem xét và cải thiện trong thời gian sớm nhất. 🙏"
    )
    return ConversationHandler.END


async def feedback_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👌 Đã huỷ.")
    return ConversationHandler.END


def register_feedback_handler(application):
    handler = ConversationHandler(
        entry_points=[
            CommandHandler("feedback", feedback_start),
            MessageHandler(
                filters.TEXT & filters.Regex(r"(?i)(báo lỗi|bị lỗi|report bug|lỗi bot|bot lỗi)"),
                feedback_start
            ),
        ],
        states={
            AWAITING_FEEDBACK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_receive),
            ],
        },
        fallbacks=[CommandHandler("cancel", feedback_cancel)],
        per_user=True,
        per_chat=True,
        name="feedback_conversation",
    )
    application.add_handler(handler)
    logger.info("✅ Feedback handler registered")
