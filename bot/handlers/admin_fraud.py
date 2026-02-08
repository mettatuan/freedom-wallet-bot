"""
Admin Fraud Review Handler (Week 5)

Commands for manual review of flagged referrals:
- /fraud_queue - View pending reviews
- /fraud_review <id> - View referral details
- /fraud_approve <id> - Approve referral
- /fraud_reject <id> - Reject referral
- /fraud_stats - View fraud statistics

Only accessible to admin users
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from config.settings import settings
from bot.core.fraud_detector import FraudDetector
from bot.utils.database import SessionLocal, Referral, User
from datetime import datetime


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    admin_id = getattr(settings, 'ADMIN_USER_ID', None)
    return user_id == admin_id


async def fraud_queue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show queue of referrals pending manual review
    
    Usage: /fraud_queue
    """
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Only admin can access this command.")
        return
    
    try:
        with FraudDetector() as detector:
            pending = detector.get_pending_reviews(limit=20)
            
            if not pending:
                await update.message.reply_text(
                    "✅ **FRAUD REVIEW QUEUE**\n\n"
                    "No pending reviews! All clear. 🎉",
                    parse_mode="Markdown"
                )
                return
            
            # Build queue message
            message = "🛡️ **FRAUD REVIEW QUEUE**\n\n"
            message += f"**Total: {len(pending)} pending reviews**\n\n"
            
            for idx, item in enumerate(pending[:10], 1):  # Show first 10
                emoji = "🚨" if item['review_status'] == 'HIGH_RISK' else "⚠️"
                
                message += (
                    f"{emoji} **#{idx} - ID {item['referral_id']}**\n"
                    f"   Score: {item['fraud_score']}/100\n"
                    f"   Referrer: {item['referrer_name']} (#{item['referrer_id']})\n"
                    f"   Referred: {item['referred_name']} (#{item['referred_id']})\n"
                    f"   Date: {item['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
                    f"   `/fraud_review {item['referral_id']}`\n\n"
                )
            
            if len(pending) > 10:
                message += f"\n... and {len(pending) - 10} more"
            
            message += "\n━━━━━━━━━━━━━━━"
            
            await update.message.reply_text(message, parse_mode="Markdown")
    
    except Exception as e:
        logger.error(f"Failed to get fraud queue: {e}")
        await update.message.reply_text(
            f"❌ Error getting fraud queue: {str(e)}"
        )


async def fraud_review_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    View detailed information about a flagged referral
    
    Usage: /fraud_review <referral_id>
    """
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Only admin can access this command.")
        return
    
    # Parse referral_id from args
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Usage: `/fraud_review <referral_id>`\n\n"
            "Example: `/fraud_review 123`",
            parse_mode="Markdown"
        )
        return
    
    try:
        referral_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid referral ID. Must be a number.")
        return
    
    try:
        session = SessionLocal()
        
        # Get referral
        referral = session.query(Referral).filter(Referral.id == referral_id).first()
        
        if not referral:
            await update.message.reply_text(f"❌ Referral {referral_id} not found.")
            session.close()
            return
        
        # Get user details
        referrer = session.query(User).filter(User.id == referral.referrer_id).first()
        referred = session.query(User).filter(User.id == referral.referred_id).first()
        
        referrer_name = referrer.username or referrer.full_name if referrer else 'Unknown'
        referred_name = referred.username or referred.full_name if referred else 'Unknown'
        
        # Get referrer's total referrals
        total_refs = session.query(Referral).filter(
            Referral.referrer_id == referral.referrer_id
        ).count()
        
        verified_refs = session.query(Referral).filter(
            Referral.referrer_id == referral.referrer_id,
            Referral.status == "VERIFIED"
        ).count()
        
        pending_refs = session.query(Referral).filter(
            Referral.referrer_id == referral.referrer_id,
            Referral.review_status.in_(['PENDING_REVIEW', 'HIGH_RISK'])
        ).count()
        
        session.close()
        
        # Build detailed message
        emoji = "🚨" if referral.review_status == 'HIGH_RISK' else "⚠️"
        
        message = (
            f"{emoji} **FRAUD REVIEW - #{referral_id}**\n\n"
            f"**Fraud Score:** {referral.velocity_score}/100\n"
            f"**Status:** {referral.review_status}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"**REFERRER INFO:**\n"
            f"• Name: {referrer_name}\n"
            f"• ID: {referral.referrer_id}\n"
            f"• Total refs: {total_refs}\n"
            f"• Verified: {verified_refs}\n"
            f"• Pending review: {pending_refs}\n\n"
            f"**REFERRED USER:**\n"
            f"• Name: {referred_name}\n"
            f"• ID: {referral.referred_id}\n\n"
            f"**TECHNICAL DATA:**\n"
            f"• IP: {referral.ip_address or 'N/A'}\n"
            f"• User-Agent: {referral.user_agent[:50] + '...' if referral.user_agent and len(referral.user_agent) > 50 else referral.user_agent or 'N/A'}\n"
            f"• Device FP: {referral.device_fingerprint[:16] + '...' if referral.device_fingerprint else 'N/A'}\n"
            f"• Created: {referral.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"**ACTIONS:**\n"
            f"• `/fraud_approve {referral_id}` - Approve\n"
            f"• `/fraud_reject {referral_id}` - Reject\n"
        )
        
        await update.message.reply_text(message, parse_mode="Markdown")
    
    except Exception as e:
        logger.error(f"Failed to review referral {referral_id}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def fraud_approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manually approve a flagged referral
    
    Usage: /fraud_approve <referral_id>
    """
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Only admin can access this command.")
        return
    
    # Parse referral_id from args
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Usage: `/fraud_approve <referral_id>`\n\n"
            "Example: `/fraud_approve 123`",
            parse_mode="Markdown"
        )
        return
    
    try:
        referral_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid referral ID. Must be a number.")
        return
    
    try:
        with FraudDetector() as detector:
            success = detector.approve_referral(referral_id, user.id, reason="Manual admin review")
            
            if success:
                await update.message.reply_text(
                    f"✅ **Referral #{referral_id} APPROVED**\n\n"
                    f"Referral has been verified and counted.\n"
                    f"Referrer will be notified if they reach VIP tier.",
                    parse_mode="Markdown"
                )
                
                logger.info(f"✅ Admin {user.id} approved referral {referral_id}")
            else:
                await update.message.reply_text(
                    f"❌ Failed to approve referral #{referral_id}.\n"
                    f"It may not exist or already be processed."
                )
    
    except Exception as e:
        logger.error(f"Failed to approve referral {referral_id}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def fraud_reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manually reject a flagged referral
    
    Usage: /fraud_reject <referral_id>
    """
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Only admin can access this command.")
        return
    
    # Parse referral_id from args
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Usage: `/fraud_reject <referral_id>`\n\n"
            "Example: `/fraud_reject 123`",
            parse_mode="Markdown"
        )
        return
    
    try:
        referral_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid referral ID. Must be a number.")
        return
    
    try:
        with FraudDetector() as detector:
            success = detector.reject_referral(referral_id, user.id, reason="Manual admin review")
            
            if success:
                await update.message.reply_text(
                    f"⛔ **Referral #{referral_id} REJECTED**\n\n"
                    f"Referral has been marked as fraudulent.\n"
                    f"It will not count toward referrer's progress.",
                    parse_mode="Markdown"
                )
                
                logger.info(f"⛔ Admin {user.id} rejected referral {referral_id}")
            else:
                await update.message.reply_text(
                    f"❌ Failed to reject referral #{referral_id}.\n"
                    f"It may not exist or already be processed."
                )
    
    except Exception as e:
        logger.error(f"Failed to reject referral {referral_id}: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def fraud_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show overall fraud detection statistics
    
    Usage: /fraud_stats
    """
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ Only admin can access this command.")
        return
    
    try:
        with FraudDetector() as detector:
            stats = detector.get_fraud_stats()
            
            message = (
                "📊 **FRAUD DETECTION STATISTICS**\n\n"
                f"**Total Referrals:** {stats['total_referrals']}\n\n"
                f"✅ Auto-approved: {stats['auto_approved']} "
                f"({stats['auto_approved'] / stats['total_referrals'] * 100:.1f}%)\n"
                f"⚠️ Pending review: {stats['pending_review']}\n"
                f"🚨 High risk: {stats['high_risk']}\n"
                f"⛔ Rejected: {stats['rejected']}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"**Approval Rate:** {stats['approval_rate']}%\n\n"
                f"💡 Use `/fraud_queue` to review pending cases"
            )
            
            await update.message.reply_text(message, parse_mode="Markdown")
    
    except Exception as e:
        logger.error(f"Failed to get fraud stats: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
