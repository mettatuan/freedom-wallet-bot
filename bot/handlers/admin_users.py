"""
Admin User Management Commands
/admin_users [filter] - List users with detailed info
/tag <user_id> <tag> - Set admin tag for user
/user_detail <user_id> - Get detailed info about specific user
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from config.settings import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return bool(settings.ADMIN_USER_ID and user_id == int(settings.ADMIN_USER_ID))


async def handle_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /admin_users [filter]
    Filters: all, pending, webapp_setup, active, inactive, notag
    """
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only")
        return
    
    from bot.utils.database import SessionLocal, User
    
    filter_type = context.args[0].lower() if context.args else "all"
    
    db = SessionLocal()
    try:
        query = db.query(User)
        
        # Apply filters
        if filter_type == "pending":
            query = query.filter(User.user_status == "PENDING")
        elif filter_type == "webapp_setup":
            query = query.filter(User.user_status == "WEBAPP_SETUP")
        elif filter_type == "active":
            query = query.filter(User.user_status == "ACTIVE")
        elif filter_type == "inactive":
            query = query.filter(User.user_status == "INACTIVE")
        elif filter_type == "churned":
            query = query.filter(User.user_status == "CHURNED")
        elif filter_type == "notag":
            query = query.filter((User.admin_tag == None) | (User.admin_tag == ""))
        elif filter_type == "registered":
            query = query.filter(User.is_registered == True)
        elif filter_type == "inactive_7d":
            # Users inactive for 7+ days
            cutoff = datetime.utcnow() - timedelta(days=7)
            query = query.filter(User.last_active < cutoff)
        
        # Order by last active
        query = query.order_by(User.last_active.desc())
        
        users = query.limit(50).all()  # Limit to 50 for readability
        
        if not users:
            await update.message.reply_text(
                f"📊 Không có users với filter: <b>{filter_type}</b>", 
                parse_mode="HTML"
            )
            return
        
        # Build report
        lines = [
            f"📊 <b>DANH SÁCH USERS ({filter_type.upper()})</b>",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"Tổng: <b>{len(users)}</b> users\n"
        ]
        
        for u in users:
            status_emoji = {
                "PENDING": "⏳",
                "WEBAPP_SETUP": "⚙️",
                "ACTIVE": "✅",
                "INACTIVE": "😴",
                "CHURNED": "❌"
            }.get(u.user_status, "❓")
            
            # Format last active
            if u.last_active:
                delta = datetime.utcnow() - u.last_active
                if delta.days > 30:
                    last_active = f"{delta.days}d ago"
                elif delta.days > 0:
                    last_active = f"{delta.days}d"
                elif delta.seconds > 3600:
                    last_active = f"{delta.seconds // 3600}h"
                else:
                    last_active = "now"
            else:
                last_active = "never"
            
            # User line
            name = u.first_name or u.username or "Unknown"
            tag_str = f" 🏷️<i>{u.admin_tag}</i>" if u.admin_tag else ""
            webapp_icon = "🌐" if u.web_app_url and u.web_app_url not in ["", "pending"] else ""
            
            lines.append(
                f"{status_emoji} <code>{u.id}</code> {webapp_icon} {name}"
                f"{tag_str}"
                f"\n   ⏱️ {last_active} • 💬 {u.total_interactions or 0}x"
            )
        
        lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(
            f"Filters: all, pending, webapp_setup, active, inactive, churned, notag, registered, inactive_7d"
        )
        
        text = "\n".join(lines)
        
        # Split if too long
        if len(text) > 4000:
            text = text[:3900] + "\n\n⚠️ Danh sách quá dài, chỉ hiển thị 50 users đầu"
        
        await update.message.reply_text(text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in admin_users: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Lỗi: {e}")
    finally:
        db.close()


async def handle_tag_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /tag <user_id> <tag_text>
    Set admin tag for user
    """
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Sử dụng: <code>/tag [user_id] [tag text]</code>\n"
            "Ví dụ: <code>/tag 12345678 VIP member - follow up weekly</code>",
            parse_mode="HTML"
        )
        return
    
    try:
        user_id = int(context.args[0])
        tag = " ".join(context.args[1:])
        
        from bot.utils.database import SessionLocal, User
        db = SessionLocal()
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await update.message.reply_text(f"❌ User {user_id} không tồn tại")
            db.close()
            return
        
        user.admin_tag = tag
        db.commit()
        
        await update.message.reply_text(
            f"✅ Đã set tag cho user <code>{user_id}</code> ({user.first_name or user.username})\n"
            f"🏷️ Tag: <i>{tag}</i>",
            parse_mode="HTML"
        )
        
        db.close()
        
    except ValueError:
        await update.message.reply_text("❌ User ID phải là số")
    except Exception as e:
        logger.error(f"Error in tag_user: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Lỗi: {e}")


async def handle_user_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /user_detail <user_id>
    Get detailed info about specific user
    """
    if not _is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Admin only")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ Sử dụng: <code>/user_detail [user_id]</code>",
            parse_mode="HTML"
        )
        return
    
    try:
        user_id = int(context.args[0])
        
        from bot.utils.database import SessionLocal, User
        db = SessionLocal()
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await update.message.reply_text(f"❌ User {user_id} không tồn tại")
            db.close()
            return
        
        # Build detailed report
        status_emoji = {
            "PENDING": "⏳ PENDING",
            "WEBAPP_SETUP": "⚙️ WEBAPP_SETUP",
            "ACTIVE": "✅ ACTIVE",
            "INACTIVE": "😴 INACTIVE",
            "CHURNED": "❌ CHURNED"
        }.get(user.user_status, "❓ UNKNOWN")
        
        lines = [
            f"👤 <b>USER DETAIL</b>",
            f"━━━━━━━━━━━━━━━━━━━━━━",
            f"<b>ID:</b> <code>{user.id}</code>",
            f"<b>Name:</b> {user.first_name or 'N/A'} {user.last_name or ''}",
            f"<b>Username:</b> @{user.username}" if user.username else "",
            f"<b>Status:</b> {status_emoji}",
            f"<b>Tag:</b> <i>{user.admin_tag}</i>" if user.admin_tag else "",
            "",
            f"📊 <b>STATS</b>",
            f"• Registered: {'✅' if user.is_registered else '❌'}",
            f"• Email: {user.email or 'N/A'}",
            f"• Phone: {user.phone or 'N/A'}",
            f"• Web App: {'✅' if user.web_app_url and user.web_app_url not in ['', 'pending'] else '❌'}",
            f"• Total Interactions: <b>{user.total_interactions or 0}</b>",
            f"• Active Days: <b>{user.daily_active_days or 0}</b>",
            f"• Last Command: <code>{user.last_command or 'N/A'}</code>",
            "",
            f"📅 <b>TIMELINE</b>",
            f"• Created: {user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A'}",
            f"• First Seen: {user.first_seen_at.strftime('%Y-%m-%d %H:%M') if user.first_seen_at else 'N/A'}",
            f"• Last Active: {user.last_active.strftime('%Y-%m-%d %H:%M') if user.last_active else 'N/A'}",
            f"• Last Command: {user.last_command_at.strftime('%Y-%m-%d %H:%M') if user.last_command_at else 'N/A'}",
            "",
            f"🎯 <b>ENGAGEMENT</b>",
            f"• Referral Code: <code>{user.referral_code}</code>",
            f"• Referred By: {user.referred_by or 'Direct'}",
            f"• Referral Count: <b>{user.referral_count}</b>",
            f"• Source: {user.activation_source or 'BOT'}",
            f"• Subscription: {user.subscription_tier}",
            f"• VIP Tier: {user.vip_tier or 'None'}",
        ]
        
        text = "\n".join([line for line in lines if line is not None])
        
        # Keyboard with actions
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🏷️ Set Tag", callback_data=f"admin_set_tag:{user_id}"),
                InlineKeyboardButton("📊 Change Status", callback_data=f"admin_set_status:{user_id}"),
            ],
            [
                InlineKeyboardButton("📤 Message User", url=f"tg://user?id={user_id}"),
            ],
        ])
        
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
        
        db.close()
        
    except ValueError:
        await update.message.reply_text("❌ User ID phải là số")
    except Exception as e:
        logger.error(f"Error in user_detail: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Lỗi: {e}")


def register_admin_user_handlers(application, group: int = -10):
    """Register admin user management handlers"""
    application.add_handler(CommandHandler("admin_users", handle_admin_users), group=group)
    application.add_handler(CommandHandler("tag", handle_tag_user), group=group)
    application.add_handler(CommandHandler("user_detail", handle_user_detail), group=group)
    logger.info(f"✅ Admin user management handlers registered (group={group})")
