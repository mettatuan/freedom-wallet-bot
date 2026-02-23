"""
Daily Reminder System - Nhắc nhở ghi chép hàng ngày
Giúp user tạo thói quen tracking tài chính 
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from loguru import logger
from datetime import datetime, timedelta
import aiohttp
from bot.utils.database import SessionLocal, User, run_sync


# Morning Reminder Content (8:00 AM)
MORNING_REMINDER_TEMPLATE = """
🌅 **Chào buổi sáng {name}!**

💪 **Hôm nay là ngày thứ {streak} ghi chép của bạn!**

━━━━━━━━━━━━━━━━━━━━━

🎯 **Mục tiêu hôm nay:**
• Ghi ít nhất 3 giao dịch
• Nhớ phân loại đúng hũ tiền
• Review tổng chi tiêu

{streak_message}

━━━━━━━━━━━━━━━━━━━━━

💡 **Tip:** Ghi chép ngay khi chi tiêu → không bao giờ quên!
"""

# Evening Reminder Content (8:00 PM)
EVENING_REMINDER_TEMPLATE = """
🌙 **Trước khi ngủ... {name}**

❓ **Hôm nay bạn đã ghi chép chưa?**

━━━━━━━━━━━━━━━━━━━━━

{streak_status}

━━━━━━━━━━━━━━━━━━━━━

💤 **Ghi ngay trước khi quên:**
• Bữa ăn hôm nay
• Di chuyển (xăng, grab...)
• Cafe, giải trí
• Mua sắm

💡 *Chỉ mất 30 giây thôi!*
"""

# Skip Alert (nếu không ghi 2 ngày liên tiếp)
SKIP_ALERT_TEMPLATE = """
😢 **Uhm... {name}, bạn ổn chứ?**

Mình thấy bạn đã không ghi chép {skip_days} ngày rồi.

━━━━━━━━━━━━━━━━━━━━━

💡 **Gặp khó khăn gì không?**
• Quên mất?
• App gặp lỗi?
• Chưa rõ cách ghi?

━━━━━━━━━━━━━━━━━━━━━

Mình ở đây giúp bạn! Nhắn cho mình nhé 💬

*"Thành công không đến từ động lực - mà đến từ hành động!"*
"""


def get_streak_message(streak: int) -> str:
    """Generate encouraging message based on streak"""
    if streak == 1:
        return "🌱 **Streak mới bắt đầu!** Hãy tiếp tục nhé!"
    elif streak < 3:
        return f"🔥 **Streak: {streak} ngày!** Cố gắng thêm một chút nữa!"
    elif streak < 7:
        return f"🔥 **Streak: {streak} ngày!** Tuyệt vời! Còn {7-streak} ngày nữa đạt 7 ngày!"
    elif streak == 7:
        return "🎉 **CHÚC MỪNG! 7 NGÀY LIÊN TỤC!** Hôm nay bạn sẽ nhận quà đặc biệt!"
    elif streak < 21:
        return f"🔥 **Streak: {streak} ngày!** Amazing! Đang trên đường hình thành thói quen!"
    elif streak < 30:
        return f"🔥 **Streak: {streak} ngày!** Xuất sắc! Còn {30-streak} ngày nữa đạt 30 ngày!"
    elif streak == 30:
        return "🏆 **CHÚC MỪNG! 30 NGÀY LIÊN TỤC!** Bạn sẽ nhận huy chương danh dự!"
    elif streak < 90:
        return f"🔥 **Streak: {streak} ngày!** Legendary! Bạn là master rồi!"
    else:
        return f"👑 **Streak: {streak} ngày!** BẠN LÀ HUYỀN THOẠI!"

def _get_reminder_user_sync(user_id: int):
    """Returns dict of user data needed for reminder, or None if not found/reminders disabled."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.reminder_enabled:
            return None
        return {
            "name": user.full_name or user.first_name or "bạn",
            "streak": user.streak_count or 0,
            "last_transaction_date": user.last_transaction_date,
            "reminder_enabled": user.reminder_enabled,
        }
    finally:
        db.close()


def _update_last_reminder_sync(user_id: int) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_reminder_sent = datetime.utcnow()
            db.commit()
    finally:
        db.close()


def _disable_reminder_sync(user_id: int) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.reminder_enabled = False
            db.commit()
    finally:
        db.close()


def _get_user_web_app_url_sync(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user.web_app_url if user else None
    finally:
        db.close()

async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send morning motivation reminder"""
    try:
        user_data = await run_sync(_get_reminder_user_sync, user_id)
        if not user_data:
            return
        
        name = user_data['name']
        streak = user_data['streak']
        
        # Generate message
        streak_message = get_streak_message(streak)
        message = MORNING_REMINDER_TEMPLATE.format(
            name=name,
            streak=streak if streak > 0 else 1,
            streak_message=streak_message
        )
        
        # Keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Mở App ngay", callback_data="reminder_open_app")],
            [InlineKeyboardButton("⏰ Nhắc tôi tối nay", callback_data="reminder_snooze_evening")],
            [InlineKeyboardButton("🔕 Tắt nhắc nhở hôm nay", callback_data="reminder_disable_today")]
        ])
        
        # Send message
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        # Update last reminder sent
        await run_sync(_update_last_reminder_sync, user_id)
        
        logger.info(f"Sent morning reminder to user {user_id} (streak: {streak})")
        
    except Exception as e:
        logger.error(f"Error sending morning reminder to {user_id}: {e}")


async def send_evening_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Send evening reminder to record transactions"""
    try:
        user_data = await run_sync(_get_reminder_user_sync, user_id)
        if not user_data:
            return
        
        name = user_data['name']
        streak = user_data['streak']
        
        # Check if user recorded transaction today
        today = datetime.utcnow().date()
        last_transaction = user_data['last_transaction_date']
        recorded_today = last_transaction and last_transaction.date() == today
        
        if recorded_today:
            streak_status = f"✅ **Tuyệt vời!** Bạn đã ghi chép hôm nay!\n\n🔥 **Streak: {streak} ngày liên tục!**"
        else:
            streak_status = "⚠️ **Chưa ghi chép hôm nay!**\n\nGhi ngay để giữ streak nhé!"
        
        # Generate message
        message = EVENING_REMINDER_TEMPLATE.format(
            name=name,
            streak_status=streak_status
        )
        
        # Keyboard
        if recorded_today:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Xem báo cáo", callback_data="reminder_view_report")],
                [InlineKeyboardButton("📝 Ghi thêm", callback_data="reminder_open_app")]
            ])
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Ghi ngay", callback_data="reminder_open_app")],
                [InlineKeyboardButton("✅ Đã ghi xong", callback_data="reminder_done")],
                [InlineKeyboardButton("⏰ Nhắc tôi sau 1h", callback_data="reminder_snooze_1h")]
            ])
        
        # Send message
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        # Update last reminder sent
        await run_sync(_update_last_reminder_sync, user_id)
        
        logger.info(f"Sent evening reminder to user {user_id} (recorded_today: {recorded_today})")
        
    except Exception as e:
        logger.error(f"Error sending evening reminder to {user_id}: {e}")


async def send_skip_alert(context: ContextTypes.DEFAULT_TYPE, user_id: int, skip_days: int):
    """Send alert when user skips recording for 2+ days"""
    try:
        user_data = await run_sync(_get_reminder_user_sync, user_id)
        if not user_data:
            return
        
        name = user_data['name']
        
        # Generate message
        message = SKIP_ALERT_TEMPLATE.format(
            name=name,
            skip_days=skip_days
        )
        
        # Keyboard
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Ghi bù ngay", callback_data="reminder_catch_up")],
            [InlineKeyboardButton("💬 Cần hỗ trợ", url="https://t.me/freedomwalletapp")],
            [InlineKeyboardButton("⏰ Nhắc tôi sáng mai", callback_data="reminder_snooze_tomorrow")]
        ])
        
        # Send message
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        
        logger.info(f"Sent skip alert to user {user_id} (skip_days: {skip_days})")
        
    except Exception as e:
        logger.error(f"Error sending skip alert to {user_id}: {e}")


# Callback handlers for reminder buttons
async def reminder_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle reminder button callbacks"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = update.effective_user.id
    
    try:
        if callback_data == "reminder_open_app":
            await query.edit_message_text(
                text="📱 **Hãy mở Web App của bạn để ghi chép!**\n\n"
                     "Link Web App nằm trong message Day 1 của bạn.\n\n"
                     "💡 *Tip: Pin message chứa Web App để truy cập nhanh!*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("👥 Group VIP", url="https://t.me/freedomwalletapp")
                ]])
            )
        
        elif callback_data == "reminder_done":
            await query.edit_message_text(
                text="✅ **Tuyệt vời! Cảm ơn bạn đã ghi chép!**\n\n"
                     "🔥 Streak của bạn được giữ nguyên!\n\n"
                     "Hẹn gặp lại bạn vào sáng mai! 😊",
                parse_mode="Markdown"
            )
        
        elif callback_data == "reminder_disable_today":
            await run_sync(_disable_reminder_sync, user_id)
            
            await query.edit_message_text(
                text="🔕 **Đã tắt nhắc nhở hôm nay.**\n\n"
                     "Bạn có thể bật lại bất cứ lúc nào bằng lệnh /reminder_on",
                parse_mode="Markdown"
            )
        
        elif callback_data in ["reminder_snooze_evening", "reminder_snooze_1h", "reminder_snooze_tomorrow"]:
            await query.edit_message_text(
                text="⏰ **Okay! Mình sẽ nhắc bạn sau!**\n\n"
                     "Đừng quên ghi chép nhé! 😊",
                parse_mode="Markdown"
            )
        
        elif callback_data == "reminder_view_report":
            # Fetch real balance + recent transactions from user's Web App
            web_app_url = await run_sync(_get_user_web_app_url_sync, user_id)

            if not web_app_url:
                await query.edit_message_text(
                    "⚠️ Bạn chưa kết nối Web App.\n"
                    "Vào menu → cài đặt kết nối để xem báo cáo ngay trong Telegram!"
                )
                return

            await query.edit_message_text("🔄 Đang lấy dữ liệu từ Sheets...")

            try:
                timeout = aiohttp.ClientTimeout(total=15)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    _KEY = "fwb_bot_production_2026"
                    # Fetch balance
                    bal_resp = await session.post(web_app_url, json={"action": "getBalance", "api_key": _KEY})
                    bal_data = await bal_resp.json(content_type=None)

                    # Fetch recent transactions
                    tx_resp = await session.post(web_app_url, json={"action": "getTransactions", "data": {"limit": 5}, "api_key": _KEY})
                    tx_data = await tx_resp.json(content_type=None)

                lines = ["<b>📊 BÁO CÁO NHANH TỪ SHEETS</b>\n"]

                # Balance section
                if bal_data.get("success"):
                    jars = bal_data.get("jars", [])
                    total = bal_data.get("totalBalance", 0)
                    lines.append("━━━━━━━━━━━━━━━")
                    lines.append("<b>🪣 Số dư các hũ tiền:</b>")
                    for jar in jars:
                        icon = jar.get("icon", "🪣")
                        name = jar.get("name", "?")
                        balance = jar.get("balance", 0)
                        pct = jar.get("percentage", 0)
                        lines.append(f"{icon} {name} ({pct}%): <b>{balance:,.0f}đ</b>")
                    lines.append(f"\n💰 <b>Tổng: {total:,.0f}đ</b>")
                else:
                    lines.append("⚠️ Không lấy được số dư hũ")

                # Transactions section
                if tx_data.get("success"):
                    txs = tx_data.get("transactions", [])
                    if txs:
                        lines.append("\n━━━━━━━━━━━━━━━")
                        lines.append("<b>📅 5 giao dịch gần nhất:</b>")
                        for tx in txs[:5]:
                            t = tx.get("type", "Chi")
                            amt = tx.get("amount", 0)
                            note = tx.get("note", "") or tx.get("category", "")
                            date = tx.get("date", "")[:10]
                            em = "💸" if t in ("Chi", "expense") else "💰"
                            lines.append(f"{em} {date} — {amt:,.0f}đ {note}")

                msg = "\n".join(lines)
                back_btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Menu chính", callback_data="show_main_menu")
                ]])
                await query.edit_message_text(msg, parse_mode="HTML", reply_markup=back_btn)

            except Exception as e:
                logger.error(f"Error fetching Sheets report: {e}")
                await query.edit_message_text(
                    f"❌ Lỗi kết nối Web App: {str(e)[:120]}\n\n"
                    "Kiểm tra Web App có đang hoạt động không."
                )
        
        elif callback_data == "reminder_catch_up":
            await query.edit_message_text(
                text="💪 **Tuyệt! Hãy ghi bù những giao dịch đã bỏ lỡ!**\n\n"
                     "📝 **Tips ghi bù:**\n"
                     "1. Mở Web App\n"
                     "2. Thêm giao dịch → Chọn ngày cũ\n"
                     "3. Ghi tất cả giao dịch đã nhớ ra\n\n"
                     "🎯 Sau khi ghi xong, streak sẽ được cập nhật!",
                parse_mode="Markdown"
            )
        
    except Exception as e:
        logger.error(f"Error in reminder callback handler: {e}")


def register_reminder_handlers(application):
    """Register reminder callback handlers"""
    application.add_handler(CallbackQueryHandler(reminder_callback_handler, pattern="^reminder_"))
    logger.info("✅ Daily reminder handlers registered")
