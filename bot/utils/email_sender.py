"""
Email Sender — Gửi email tới users qua SMTP.

Dùng Gmail + App Password (không cần SMTP server riêng).
Setup: https://myaccount.google.com/apppasswords
"""

import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from config.settings import settings

logger = logging.getLogger(__name__)


# ─── Email templates ──────────────────────────────────────────────────────────
def _html_setup_email(first_name: str) -> str:
    """Template email hướng dẫn setup Web App."""
    name = first_name or "bạn"
    return f"""
<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">

  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 24px;">
    <h1 style="color: white; margin: 0; font-size: 24px;">💎 Freedom Wallet</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0;">Quản lý tài chính thông minh</p>
  </div>

  <p style="font-size: 16px;">Chào <strong>{name}</strong>! 👋</p>

  <p>Bạn đã đăng ký <strong>Freedom Wallet</strong> rồi nhưng chưa hoàn tất bước tạo <strong>Web App cá nhân</strong>.</p>

  <p>Web App giúp bạn:</p>
  <ul style="line-height: 1.8;">
    <li>✅ Lưu 100% dữ liệu trong <strong>Google Drive</strong> của bạn (không ai đọc được)</li>
    <li>✅ Ghi thu chi bằng <strong>giọng nói và text</strong> siêu nhanh</li>
    <li>✅ Xem báo cáo tài chính <strong>trực quan</strong> theo ngày/tháng</li>
  </ul>

  <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 16px; border-radius: 4px; margin: 24px 0;">
    <p style="margin: 0; font-size: 15px;">🎬 <strong>Video hướng dẫn từng bước (chỉ 5 phút):</strong></p>
    <a href="https://youtu.be/xVoASsuWfto"
       style="display: inline-block; margin-top: 10px; background: #ff0000; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold;">
      ▶ Xem video hướng dẫn
    </a>
  </div>

  <p>Sau khi xem video, quay lại bot Telegram và nhắn <strong>/start</strong> để tiếp tục nhé!</p>

  <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #eee; text-align: center; color: #888; font-size: 13px;">
    <p>Freedom Wallet Bot — <a href="https://t.me/FreedomWalletBot">@FreedomWalletBot</a></p>
    <p>Nếu bạn không muốn nhận email này, hãy nhắn <code>/unsubscribe</code> cho bot.</p>
  </div>

</body>
</html>
"""


def _text_setup_email(first_name: str) -> str:
    """Plain text fallback."""
    name = first_name or "bạn"
    return f"""Chào {name}!

Bạn đã đăng ký Freedom Wallet nhưng chưa hoàn tất bước tạo Web App cá nhân.

Video hướng dẫn từng bước (5 phút):
https://youtu.be/xVoASsuWfto

Sau khi xem, quay lại bot: https://t.me/FreedomWalletBot

Trân trọng,
Freedom Wallet Team
"""


# ─── Core sender ──────────────────────────────────────────────────────────────
def _send_email_sync(to_email: str, to_name: str, subject: str, html_body: str, text_body: str) -> bool:
    """Gửi 1 email đồng bộ qua SMTP. Trả về True nếu thành công."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = f"{to_name} <{to_email}>" if to_name else to_email

        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

        return True
    except smtplib.SMTPRecipientsRefused:
        logger.warning(f"Email rejected: {to_email}")
        return False
    except Exception as e:
        logger.warning(f"Email error to {to_email}: {e}")
        return False


async def send_setup_email(to_email: str, to_name: str = "") -> bool:
    """Gửi email hướng dẫn setup Web App (async wrapper)."""
    subject = "🚀 Hoàn tất setup Freedom Wallet của bạn (5 phút)"
    html = _html_setup_email(to_name)
    text = _text_setup_email(to_name)
    return await asyncio.to_thread(_send_email_sync, to_email, to_name, subject, html, text)


async def send_custom_email(to_email: str, to_name: str, subject: str, html_body: str, text_body: str = "") -> bool:
    """Gửi email tùy chỉnh."""
    if not text_body:
        # Strip HTML tags thô sơ làm fallback
        import re
        text_body = re.sub(r"<[^>]+>", "", html_body)
    return await asyncio.to_thread(_send_email_sync, to_email, to_name, subject, html_body, text_body)


# ─── Batch sender ─────────────────────────────────────────────────────────────
async def send_setup_emails_to_list(users: list[dict], delay: float = 0.5) -> dict:
    """
    Gửi email setup tới danh sách users.
    users: list of {"id", "first_name", "email"}
    Trả về {sent, skipped_no_email, failed, total}
    """
    sent = skipped = failed = 0
    for user in users:
        email = user.get("email", "").strip()
        if not email or "@" not in email:
            skipped += 1
            continue
        ok = await send_setup_email(email, user.get("first_name", ""))
        if ok:
            sent += 1
        else:
            failed += 1
        await asyncio.sleep(delay)  # Rate limit: 2 emails/sec tránh bị spam filter

    return {"sent": sent, "skipped_no_email": skipped, "failed": failed, "total": len(users)}


def test_smtp_connection() -> tuple[bool, str]:
    """Kiểm tra SMTP config có hoạt động không. Trả về (ok, message)."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        return False, "Chưa cấu hình SMTP_USER / SMTP_PASSWORD trong .env"
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as s:
            s.ehlo()
            s.starttls()
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        return True, f"✅ Kết nối thành công: {settings.SMTP_USER}"
    except Exception as e:
        return False, f"❌ Lỗi: {e}"
