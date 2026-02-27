"""
ErrorTracker — Tự động theo dõi, gom nhóm lỗi và auto-recover lỗi đã biết.

Cách hoạt động:
  1. error_handler trong main.py gọi tracker.record(error) mỗi khi có exception
  2. Tracker gom nhóm theo error type + message (bỏ qua stacktrace cụ thể)
  3. Khi cùng 1 lỗi xảy ra >= ALERT_THRESHOLD lần trong cửa sổ thời gian → gửi alert admin
  4. Một số lỗi đã biết có auto-recovery handler

Auto-recovery đã có:
  - httpx.RemoteProtocolError / ConnectionResetError → bỏ qua (Telegram glitch)
  - telegram.error.TimedOut → bỏ qua (network)
  - telegram.error.NetworkError → bỏ qua
  - sqlite3.OperationalError: database is locked → retry sau 1s (DB lock)
"""

import asyncio
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Lỗi nhẹ — bỏ qua hoàn toàn, không alert
IGNORABLE_ERRORS = {
    "telegram.error.TimedOut",
    "telegram.error.NetworkError",
    "httpx.RemoteProtocolError",
    "httpx.ConnectTimeout",
    "ConnectionResetError",
    "asyncio.TimeoutError",
    "telegram.error.BadRequest: Message is not modified",
    "telegram.error.BadRequest: Query is too old",
    "telegram.error.BadRequest: MESSAGE_ID_INVALID",
}

# Lỗi có thể tự recover — (error_pattern, recovery_description)
AUTO_RECOVERABLE = {
    "database is locked": "DB lock — auto-retry in 1s",
    "SSL: CERTIFICATE_VERIFY_FAILED": "SSL glitch — reconnect on next request",
    "Connection reset by peer": "Network reset — ignore, next poll OK",
    "Event loop is closed": "Event loop — restart needed",
}

ALERT_THRESHOLD = 5       # Số lần lỗi trong cửa sổ trước khi alert
ALERT_WINDOW_MINUTES = 10 # Cửa sổ thời gian (phút)
COOLDOWN_MINUTES = 30     # Không alert lại cùng lỗi trong 30 phút


class ErrorTracker:
    """Singleton tracker — dùng error_tracker.get_tracker() để lấy instance."""

    def __init__(self):
        # {error_key: [timestamp, ...]}
        self._counts: dict[str, list[float]] = defaultdict(list)
        # {error_key: last_alert_time}
        self._last_alert: dict[str, float] = {}
        # {error_key: total count all time}
        self._total: dict[str, int] = defaultdict(int)
        self._ignorable_count: int = 0
        # Admin bot ref (set sau khi application khởi động)
        self._bot = None
        self._admin_id: Optional[int] = None

    def setup(self, bot, admin_id: int):
        self._bot = bot
        self._admin_id = admin_id

    def _make_key(self, error: Exception) -> str:
        """Tạo key ngắn gọn từ exception — bỏ qua line numbers cụ thể."""
        etype = type(error).__qualname__
        msg = str(error)[:120]
        # Xoá số cụ thể để gom nhóm (line 123 → line N)
        msg = re.sub(r'\b\d{4,}\b', 'N', msg)
        return f"{etype}: {msg}"

    def _is_ignorable(self, error: Exception) -> bool:
        etype = f"{type(error).__module__}.{type(error).__qualname__}"
        short = type(error).__qualname__
        msg = str(error)
        for pattern in IGNORABLE_ERRORS:
            if pattern in etype or pattern in short or pattern in msg:
                return True
        return False

    def _get_recovery_hint(self, error: Exception) -> Optional[str]:
        msg = str(error).lower()
        for pattern, hint in AUTO_RECOVERABLE.items():
            if pattern.lower() in msg:
                return hint
        return None

    def record(self, error: Exception) -> dict:
        """
        Ghi nhận lỗi. Trả về dict với:
          - ignorable: bool
          - recovery_hint: str | None
          - alert_needed: bool
          - count_in_window: int
        """
        if self._is_ignorable(error):
            self._ignorable_count += 1
            return {"ignorable": True, "recovery_hint": None, "alert_needed": False, "count_in_window": 0}

        key = self._make_key(error)
        now = time.time()
        window_start = now - ALERT_WINDOW_MINUTES * 60

        # Xoá timestamps cũ
        self._counts[key] = [t for t in self._counts[key] if t > window_start]
        self._counts[key].append(now)
        self._total[key] += 1

        count = len(self._counts[key])
        recovery_hint = self._get_recovery_hint(error)

        # Check alert
        last_alert = self._last_alert.get(key, 0)
        cooldown_ok = (now - last_alert) > COOLDOWN_MINUTES * 60
        alert_needed = count >= ALERT_THRESHOLD and cooldown_ok

        if alert_needed:
            self._last_alert[key] = now

        return {
            "ignorable": False,
            "recovery_hint": recovery_hint,
            "alert_needed": alert_needed,
            "count_in_window": count,
            "key": key,
            "total": self._total[key],
        }

    async def send_alert(self, error: Exception, context_info: str, result: dict):
        """Gửi alert tới admin khi lỗi vượt ngưỡng."""
        if not self._bot or not self._admin_id:
            return
        try:
            import html as _html
            key = result.get("key", str(type(error).__name__))
            count = result.get("count_in_window", 0)
            total = result.get("total", 0)
            hint = result.get("recovery_hint", "")
            hint_line = f"\n🔧 <b>Auto-recovery:</b> {hint}" if hint else ""

            msg = (
                f"🔴 <b>Lỗi lặp lại ({count}x/{ALERT_WINDOW_MINUTES}min)</b>\n\n"
                f"<code>{_html.escape(key[:200])}</code>\n"
                f"{context_info}"
                f"{hint_line}\n"
                f"📊 Tổng lỗi này: {total} lần\n"
                f"💡 /admin_errors để xem chi tiết"
            )
            await self._bot.send_message(
                chat_id=self._admin_id,
                text=msg,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning(f"ErrorTracker: failed to send alert: {e}")

    @property
    def total_errors(self) -> int:
        return sum(self._total.values())

    @property
    def ignorable_count(self) -> int:
        return self._ignorable_count

    def get_recent_errors(self, minutes: int = 60) -> int:
        """Tổng số lỗi thực tế (không tính ignorable) trong N phút gần nhất."""
        now = time.time()
        window_start = now - minutes * 60
        total = 0
        for timestamps in self._counts.values():
            total += sum(1 for t in timestamps if t > window_start)
        return total

    def get_report(self) -> str:
        """Tạo report text để hiển thị trong admin panel."""
        summary = self.get_summary()
        if not summary:
            return "✅ Không có lỗi nào trong cửa sổ thời gian hiện tại."
        lines = []
        for item in summary[:10]:  # top 10
            lines.append(
                f"• <b>{item['count_window']}x</b> lúc {item['last_seen']} (tổng: {item['total']}x)\n"
                f"  <code>{item['key'][:100]}</code>"
            )
        return "\n\n".join(lines)

    def get_summary(self) -> list[dict]:
        """Trả về danh sách lỗi đang có trong cửa sổ thời gian, sắp xếp theo count."""
        now = time.time()
        window_start = now - ALERT_WINDOW_MINUTES * 60
        result = []
        for key, timestamps in self._counts.items():
            recent = [t for t in timestamps if t > window_start]
            if recent:
                result.append({
                    "key": key,
                    "count_window": len(recent),
                    "total": self._total[key],
                    "last_seen": datetime.fromtimestamp(max(recent)).strftime("%H:%M:%S"),
                })
        return sorted(result, key=lambda x: x["count_window"], reverse=True)


# Singleton
_tracker: Optional[ErrorTracker] = None


def get_tracker() -> ErrorTracker:
    global _tracker
    if _tracker is None:
        _tracker = ErrorTracker()
    return _tracker
