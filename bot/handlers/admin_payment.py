"""
Admin Payment Commands - Manage payment verifications
Commands available for admin users only
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
import html
from config.settings import settings
from bot.utils.database import get_db, PaymentVerification, User, SessionLocal, run_sync
from sqlalchemy import func


def _get_pending_payments_sync():
    """Return {'total': int, 'items': list[dict]} for pending payment verifications."""
    db = SessionLocal()
    try:
        pending = db.query(PaymentVerification).filter(
            PaymentVerification.status == "PENDING"
        ).order_by(PaymentVerification.created_at.desc()).all()
        total = len(pending)
        items = []
        for v in pending[:10]:
            user = db.query(User).filter(User.id == v.user_id).first()
            time_ago = (datetime.utcnow() - v.created_at).total_seconds() / 60
            tx_preview = v.transaction_info[:150].replace('\n', ' ').replace('\r', ' ')
            items.append({
                'id': v.id,
                'user_id': v.user_id,
                'amount': v.amount,
                'time_ago': time_ago,
                'username': user.username if user else 'Unknown',
                'full_name': user.full_name if user and user.full_name else 'N/A',
                'transaction_preview': tx_preview,
            })
        return {'total': total, 'items': items}
    finally:
        db.close()


def _get_approval_details_sync(verification_id: str):
    """Return dict with user/ver details for approve flow, or None if not found."""
    db = SessionLocal()
    try:
        ver_id = int(verification_id.replace("VER", ""))
        ver = db.query(PaymentVerification).filter(PaymentVerification.id == ver_id).first()
        if not ver:
            return None
        user = db.query(User).filter(User.id == ver.user_id).first()
        return {
            'user_id': ver.user_id,
            'amount': ver.amount,
            'username': user.username if user else 'Unknown',
            'full_name': user.full_name if user else 'N/A',
            'premium_expires_str': user.premium_expires_at.strftime('%d/%m/%Y') if user and user.premium_expires_at else None,
        }
    finally:
        db.close()


def _get_rejection_data_sync(ver_int_id: int):
    """Return {'user_id', 'amount', 'status'} or None."""
    db = SessionLocal()
    try:
        ver = db.query(PaymentVerification).filter(PaymentVerification.id == ver_int_id).first()
        if not ver:
            return None
        return {'user_id': ver.user_id, 'amount': ver.amount, 'status': ver.status}
    finally:
        db.close()


def _do_reject_payment_sync(ver_int_id: int, approved_by: int, reason: str) -> None:
    """Write REJECTED status to payment verification."""
    db = SessionLocal()
    try:
        ver = db.query(PaymentVerification).filter(PaymentVerification.id == ver_int_id).first()
        if ver:
            ver.status = "REJECTED"
            ver.approved_by = approved_by
            ver.approved_at = datetime.utcnow()
            ver.notes = reason
            db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _get_payment_stats_sync():
    """Return aggregated payment statistics dict."""
    db = SessionLocal()
    try:
        pending = db.query(PaymentVerification).filter(PaymentVerification.status == "PENDING").count()
        approved = db.query(PaymentVerification).filter(PaymentVerification.status == "APPROVED").count()
        rejected = db.query(PaymentVerification).filter(PaymentVerification.status == "REJECTED").count()
        revenue = db.query(func.sum(PaymentVerification.amount)).filter(
            PaymentVerification.status == "APPROVED"
        ).scalar() or 0
        premium_count = db.query(User).filter(User.subscription_tier == 'PREMIUM').count()
        return {
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'revenue': revenue,
            'premium_count': premium_count,
        }
    finally:
        db.close()
from bot.services.payment_service import PaymentVerificationService
from bot.core.subscription import SubscriptionManager
from datetime import datetime


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == settings.ADMIN_USER_ID


async def payment_pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /payment_pending - Show all pending payment verifications
    Admin only command
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    try:
        result = await run_sync(_get_pending_payments_sync)
        total = result['total']
        pending_items = result['items']
        
        if not pending_items:
            await update.message.reply_text("✅ Không có yêu cầu xác nhận thanh toán nào.")
            return
        
        # Send header
        await update.message.reply_text(
            f"<b>🔍 YÊU CẦU XÁC NHẬN THANH TOÁN</b>\n\nTìm thấy {total} yêu cầu đang chờ:\n",
            parse_mode="HTML"
        )
        
        # Send each verification as separate message with buttons
        for item in pending_items:
            safe_username = html.escape(item['username'])
            full_name = html.escape(item['full_name'])
            safe_transaction_info = html.escape(item['transaction_preview'])
            
            message = f"""━━━━━━━━━━━━━━━━━━━━━
<b>VER{item['id']}</b>

👤 User: {full_name} (@{safe_username})
🆔 ID: {item['user_id']}
💰 Số tiền: <b>{item['amount']:,.0f} VNĐ</b>
⏱️ {item['time_ago']:.0f} phút trước

📝 Thông tin:
{safe_transaction_info}...
"""
            
            # Inline buttons for this verification
            keyboard = [
                [
                    InlineKeyboardButton("✅ Duyệt", callback_data=f"admin_approve_VER{item['id']}"),
                    InlineKeyboardButton("❌ Từ chối", callback_data=f"admin_reject_VER{item['id']}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
        if total > 10:
            await update.message.reply_text(f"\n... và {total - 10} yêu cầu khác", parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error getting pending payments: {e}")
        safe_error = html.escape(str(e))
        await update.message.reply_text(f"❌ Lỗi: {safe_error}", parse_mode="HTML")


async def payment_approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /payment_approve VER123 - Approve payment verification
    Admin only command
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    # Get verification ID from command args
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Sử dụng: <code>/payment_approve VER123</code>",
            parse_mode="HTML"
        )
        return
    
    verification_id = context.args[0]
    
    # Approve payment
    success = await PaymentVerificationService.approve_payment(
        verification_id=verification_id,
        approved_by=user_id
    )
    
    if success:
        try:
            approval_data = await run_sync(_get_approval_details_sync, verification_id)
            
            if approval_data:
                expire_str = approval_data['premium_expires_str'] or '365 ngày'
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=approval_data['user_id'],
                        text=f"""
🎉 <b>CHÚC MỪNG! PREMIUM Đã Kích Hoạt</b>

━━━━━━━━━━━━━━━━━━━━━
✅ <b>THANH TOÁN ĐÃ XÁC NHẬN:</b>
━━━━━━━━━━━━━━━━━━━━━

💰 Số tiền: {approval_data['amount']:,.0f} VNĐ
⏱️ Thời gian: {datetime.now().strftime('%H:%M %d/%m/%Y')}

━━━━━━━━━━━━━━━━━━━━━
💎 <b>TÀI KHOẢN PREMIUM:</b>
━━━━━━━━━━━━━━━━━━━━━

✅ Kích hoạt: Ngay bây giờ
📅 Hết hạn: {expire_str}

━━━━━━━━━━━━━━━━━━━━━
🎁 <b>BẮT ĐẦU SỬ DỤNG:</b>
━━━━━━━━━━━━━━━━━━━━━

• Gửi tin nhắn không giới hạn
• Sử dụng tất cả tính năng Premium
• Hỗ trợ ưu tiên từ Admin

📞 Cần hỗ trợ? Gửi tin nhắn trực tiếp cho mình!

Cảm ơn bạn đã tin tưởng Freedom Wallet! 💖
""",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Error notifying user {approval_data['user_id']}: {e}")
                
                # Confirm to admin
                safe_username = html.escape(approval_data['username'])
                await update.message.reply_text(
                    f"✅ Đã phê duyệt {verification_id}\n"
                    f"👤 User: {safe_username} (ID: {approval_data['user_id']})\n"
                    f"💰 Số tiền: {approval_data['amount']:,.0f} VNĐ\n"
                    f"📅 Premium đến: {expire_str}\n"
                    f"✅ Đã gửi thông báo cho user",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(f"✅ Đã phê duyệt {verification_id}")
                
        except Exception as e:
            logger.error(f"Error in payment_approve_command post-approval: {e}")
    else:
        await update.message.reply_text(
            f"❌ Không thể phê duyệt {verification_id}. Kiểm tra lại ID hoặc log.",
            parse_mode="HTML"
        )


async def payment_reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /payment_reject VER123 [reason] - Reject payment verification
    Admin only command
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    # Get verification ID from command args
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Sử dụng: <code>/payment_reject VER123 [lý do]</code>",
            parse_mode="HTML"
        )
        return
    
    verification_id = context.args[0]
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Không rõ lý do"
    
    ver_id = int(verification_id.replace("VER", ""))
    
    try:
        ver_data = await run_sync(_get_rejection_data_sync, ver_id)
        
        if not ver_data:
            await update.message.reply_text(f"❌ Không tìm thấy {verification_id}")
            return
        
        if ver_data['status'] != "PENDING":
            await update.message.reply_text(
                f"❌ {verification_id} đã được xử lý: {ver_data['status']}"
            )
            return
        
        # Update status
        await run_sync(_do_reject_payment_sync, ver_id, user_id, reason)
        
        # Notify user
        safe_reason = html.escape(reason)
        try:
            await context.bot.send_message(
                chat_id=ver_data['user_id'],
                text=f"""
❌ <b>YÊU CẦU XÁC NHẬN BỊ TỪ CHỐI</b>

━━━━━━━━━━━━━━━━━━━━━
📋 <b>THÔNG TIN:</b>
━━━━━━━━━━━━━━━━━━━━━

Mã: {verification_id}
💰 Số tiền: {ver_data['amount']:,.0f} VNĐ

━━━━━━━━━━━━━━━━━━━━━
📝 <b>LÝ DO:</b>
━━━━━━━━━━━━━━━━━━━━━

{safe_reason}

━━━━━━━━━━━━━━━━━━━━━
💡 <b>TIẾP THEO:</b>
━━━━━━━━━━━━━━━━━━━━━

Vui lòng kiểm tra lại thông tin thanh toán và liên hệ Admin để được hỗ trợ.

💬 Liên hệ: Gửi tin nhắn trực tiếp trong bot
""",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")
                ]])
            )
        except Exception as e:
            logger.error(f"Error notifying user {ver_data['user_id']}: {e}")
        
        # Confirm to admin
        safe_reason_admin = html.escape(reason)
        await update.message.reply_text(
            f"✅ Đã từ chối {verification_id}\n"
            f"👤 User ID: {ver_data['user_id']}\n"
            f"📝 Lý do: {safe_reason_admin}\n"
            f"✅ Đã gửi thông báo cho user",
            parse_mode="HTML"
        )
        
        logger.info(f"Payment {verification_id} rejected by admin {user_id}: {reason}")
        
    except Exception as e:
        logger.error(f"Error rejecting payment {verification_id}: {e}")
        await update.message.reply_text(f"❌ Lỗi: {e}")


async def payment_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /payment_stats - Show payment statistics
    Admin only command
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    try:
        stats = await run_sync(_get_payment_stats_sync)
        
        message = f"""
📊 <b>THỐNG KÊ THANH TOÁN</b>

━━━━━━━━━━━━━━━━━━━━━
📋 <b>YÊU CẦU:</b>
━━━━━━━━━━━━━━━━━━━━━

⏳ Đang chờ: {stats['pending']}
✅ Đã duyệt: {stats['approved']}
❌ Đã từ chối: {stats['rejected']}

━━━━━━━━━━━━━━━━━━━━━
💰 <b>DOANH THU:</b>
━━━━━━━━━━━━━━━━━━━━━

Tổng: {stats['revenue']:,.0f} VNĐ
Trung bình: {stats['revenue']/stats['approved'] if stats['approved'] > 0 else 0:,.0f} VNĐ/giao dịch

━━━━━━━━━━━━━━━━━━━━━
💎 <b>PREMIUM USERS:</b>
━━━━━━━━━━━━━━━━━━━━━

Tổng: {stats['premium_count']} users
"""
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error getting payment stats: {e}")
        await update.message.reply_text(f"❌ Lỗi: {e}")
