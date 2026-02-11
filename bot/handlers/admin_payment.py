"""
Admin Payment Commands - Manage payment verifications
Commands available for admin users only
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
import html
from config.settings import settings
from bot.utils.database import get_db, PaymentVerification, User
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
    
    db = next(get_db())
    try:
        # Get all pending verifications
        pending = db.query(PaymentVerification).filter(
            PaymentVerification.status == "PENDING"
        ).order_by(PaymentVerification.created_at.desc()).all()
        
        if not pending:
            await update.message.reply_text("✅ Không có yêu cầu xác nhận thanh toán nào.")
            return
        
        # Send header
        await update.message.reply_text(
            f"<b>🔍 YÊU CẦU XÁC NHẬN THANH TOÁN</b>\n\nTìm thấy {len(pending)} yêu cầu đang chờ:\n",
            parse_mode="HTML"
        )
        
        # Send each verification as separate message with buttons
        for verification in pending[:10]:  # Show max 10
            user = db.query(User).filter(User.id == verification.user_id).first()
            username = user.username if user else "Unknown"
            safe_username = html.escape(username)
            full_name = html.escape(user.full_name if user and user.full_name else "N/A")
            
            time_ago = (datetime.utcnow() - verification.created_at).total_seconds() / 60
            
            # Escape transaction info and replace newlines with spaces
            transaction_preview = verification.transaction_info[:150].replace('\n', ' ').replace('\r', ' ')
            safe_transaction_info = html.escape(transaction_preview)
            
            message = f"""━━━━━━━━━━━━━━━━━━━━━
<b>VER{verification.id}</b>

👤 User: {full_name} (@{safe_username})
🆔 ID: {verification.user_id}
💰 Số tiền: <b>{verification.amount:,.0f} VNĐ</b>
⏱️ {time_ago:.0f} phút trước

📝 Thông tin:
{safe_transaction_info}...
"""
            
            # Inline buttons for this verification
            keyboard = [
                [
                    InlineKeyboardButton("✅ Duyệt", callback_data=f"admin_approve_VER{verification.id}"),
                    InlineKeyboardButton("❌ Từ chối", callback_data=f"admin_reject_VER{verification.id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        
        if len(pending) > 10:
            await update.message.reply_text(f"\n... và {len(pending) - 10} yêu cầu khác", parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error getting pending payments: {e}")
        safe_error = html.escape(str(e))
        await update.message.reply_text(f"❌ Lỗi: {safe_error}", parse_mode="HTML")
    finally:
        db.close()


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
        db = next(get_db())
        try:
            # Get verification details
            ver_id = int(verification_id.replace("VER", ""))
            verification = db.query(PaymentVerification).filter(
                PaymentVerification.id == ver_id
            ).first()
            
            if verification:
                # Get user
                payment_user = db.query(User).filter(
                    User.id == verification.user_id
                ).first()
                
                # Notify user
                try:
                    await context.bot.send_message(
                        chat_id=verification.user_id,
                        text=f"""
🎉 <b>CHÚC MỪNG! PREMIUM Đã Kích Hoạt</b>

━━━━━━━━━━━━━━━━━━━━━
✅ <b>THANH TOÁN ĐÃ XÁC NHẬN:</b>
━━━━━━━━━━━━━━━━━━━━━

💰 Số tiền: {verification.amount:,.0f} VNĐ
⏱️ Thời gian: {datetime.now().strftime('%H:%M %d/%m/%Y')}

━━━━━━━━━━━━━━━━━━━━━
💎 <b>TÀI KHOẢN PREMIUM:</b>
━━━━━━━━━━━━━━━━━━━━━

✅ Kích hoạt: Ngay bây giờ
📅 Hết hạn: {payment_user.premium_expires_at.strftime('%d/%m/%Y') if payment_user.premium_expires_at else '365 ngày'}

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
                    logger.error(f"Error notifying user {verification.user_id}: {e}")
                
                # Confirm to admin
                safe_username = html.escape(payment_user.username if payment_user else 'Unknown')
                await update.message.reply_text(
                    f"✅ Đã phê duyệt {verification_id}\n"
                    f"👤 User: {safe_username} (ID: {verification.user_id})\n"
                    f"💰 Số tiền: {verification.amount:,.0f} VNĐ\n"
                    f"📅 Premium đến: {payment_user.premium_expires_at.strftime('%d/%m/%Y') if payment_user and payment_user.premium_expires_at else 'N/A'}\n"
                    f"✅ Đã gửi thông báo cho user",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(f"✅ Đã phê duyệt {verification_id}")
                
        finally:
            db.close()
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
    
    db = next(get_db())
    try:
        # Get verification request
        ver_id = int(verification_id.replace("VER", ""))
        verification = db.query(PaymentVerification).filter(
            PaymentVerification.id == ver_id
        ).first()
        
        if not verification:
            await update.message.reply_text(f"❌ Không tìm thấy {verification_id}")
            return
        
        if verification.status != "PENDING":
            await update.message.reply_text(
                f"❌ {verification_id} đã được xử lý: {verification.status}"
            )
            return
        
        # Update status
        verification.status = "REJECTED"
        verification.approved_by = user_id
        verification.approved_at = datetime.utcnow()
        verification.notes = reason
        db.commit()
        
        # Notify user
        safe_reason = html.escape(reason)
        try:
            await context.bot.send_message(
                chat_id=verification.user_id,
                text=f"""
❌ <b>YÊU CẦU XÁC NHẬN BỊ TỪ CHỐI</b>

━━━━━━━━━━━━━━━━━━━━━
📋 <b>THÔNG TIN:</b>
━━━━━━━━━━━━━━━━━━━━━

Mã: {verification_id}
💰 Số tiền: {verification.amount:,.0f} VNĐ

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
            logger.error(f"Error notifying user {verification.user_id}: {e}")
        
        # Confirm to admin
        safe_reason_admin = html.escape(reason)
        await update.message.reply_text(
            f"✅ Đã từ chối {verification_id}\n"
            f"👤 User ID: {verification.user_id}\n"
            f"📝 Lý do: {safe_reason_admin}\n"
            f"✅ Đã gửi thông báo cho user",
            parse_mode="HTML"
        )
        
        logger.info(f"Payment {verification_id} rejected by admin {user_id}: {reason}")
        
    except Exception as e:
        logger.error(f"Error rejecting payment {verification_id}: {e}")
        await update.message.reply_text(f"❌ Lỗi: {e}")
        db.rollback()
    finally:
        db.close()


async def payment_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /payment_stats - Show payment statistics
    Admin only command
    """
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    
    db = next(get_db())
    try:
        # Get statistics
        total_pending = db.query(PaymentVerification).filter(
            PaymentVerification.status == "PENDING"
        ).count()
        
        total_approved = db.query(PaymentVerification).filter(
            PaymentVerification.status == "APPROVED"
        ).count()
        
        total_rejected = db.query(PaymentVerification).filter(
            PaymentVerification.status == "REJECTED"
        ).count()
        
        # Get total revenue (approved only)
        from sqlalchemy import func
        total_revenue = db.query(
            func.sum(PaymentVerification.amount)
        ).filter(
            PaymentVerification.status == "APPROVED"
        ).scalar() or 0
        
        message = f"""
📊 <b>THỐNG KÊ THANH TOÁN</b>

━━━━━━━━━━━━━━━━━━━━━
📋 <b>YÊU CẦU:</b>
━━━━━━━━━━━━━━━━━━━━━

⏳ Đang chờ: {total_pending}
✅ Đã duyệt: {total_approved}
❌ Đã từ chối: {total_rejected}

━━━━━━━━━━━━━━━━━━━━━
💰 <b>DOANH THU:</b>
━━━━━━━━━━━━━━━━━━━━━

Tổng: {total_revenue:,.0f} VNĐ
Trung bình: {total_revenue/total_approved if total_approved > 0 else 0:,.0f} VNĐ/giao dịch

━━━━━━━━━━━━━━━━━━━━━
💎 <b>PREMIUM USERS:</b>
━━━━━━━━━━━━━━━━━━━━━

Tổng: {db.query(User).filter(User.subscription_tier == 'PREMIUM').count()} users
"""
        
        await update.message.reply_text(message, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error getting payment stats: {e}")
        await update.message.reply_text(f"❌ Lỗi: {e}")
    finally:
        db.close()
