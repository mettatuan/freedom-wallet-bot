"""Start command handler using Clean Architecture."""

from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from ...infrastructure.di_container import get_container
from ...application.dtos import RegisterUserInput


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command using Clean Architecture.
    
    Workflow:
    1. Get DI container
    2. Call RegisterUserUseCase
    3. Show welcome message with tier-appropriate menu
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started bot (Clean Architecture)")
    
    try:
        # Get DI container
        container = get_container()
        session = container.get_db_session()
        
        try:
            # Register user (idempotent - returns existing user if already registered)
            register_use_case = container.get_register_user_use_case(session)
            
            result = await register_use_case.execute(RegisterUserInput(
                telegram_user_id=user.id,
                telegram_username=user.username,
                email=None,  # Will be collected during registration flow
                phone=None
            ))
            
            if result.is_failure():
                logger.error(f"Failed to register user {user.id}: {result.error_message}")
                await update.message.reply_text(
                    "❌ Có lỗi xảy ra khi khởi tạo tài khoản.\n"
                    "Vui lòng thử lại sau."
                )
                return
            
            # Defensive: Check if data exists before accessing attributes
            if not result.data:
                logger.error(f"No data returned for user {user.id}")
                await update.message.reply_text("❌ Lỗi hệ thống. Vui lòng thử lại.")
                return
            
            user_dto = result.data.user
            subscription_dto = result.data.subscription
            is_new_user = result.data.is_new_user
            
            # Defensive: Check if subscription exists
            if not subscription_dto:
                logger.error(f"No subscription found for user {user.id}")
                await update.message.reply_text("❌ Lỗi hệ thống: Không tìm thấy gói dịch vụ. Vui lòng liên hệ admin.")
                return
            
            # Log registration result
            if is_new_user:
                logger.info(f"✅ New user {user.id} registered with {subscription_dto.tier} tier")
            else:
                logger.info(f"♻️ Existing user {user.id} ({subscription_dto.tier} tier) restarted bot")
            
            # Build welcome message based on tier
            if subscription_dto.tier == "FREE":
                # Use original legacy welcome message
                welcome_text = f"""Chào {user.first_name},

Freedom Wallet không phải một app để bạn tải về.
Đây là một hệ thống bạn tự sở hữu.

Mỗi người dùng có:
• Google Sheet riêng
• Apps Script riêng
• Web App riêng

Dữ liệu nằm trên Drive của bạn.
Không phụ thuộc vào ai.

Nếu bạn muốn đăng ký sở hữu hệ thống web app này,
mình sẽ hướng dẫn từng bước, rất rõ ràng."""
                
                keyboard = [
                    [InlineKeyboardButton("📝 Đăng ký ngay", callback_data="start_free_registration")],
                    [InlineKeyboardButton("📖 Tìm hiểu thêm", callback_data="learn_more")],
                ]
                
            elif subscription_dto.tier == "UNLOCK":
                welcome_text = (
                    f"👋 Xin chào lại {user.first_name}!\n\n"
                    f"🔓 **Tài khoản UNLOCK** của bạn đang hoạt động.\n\n"
                    f"⚡ **Bạn có thể:**\n"
                    f"• Ghi chi tiêu siêu nhanh: `chi 50k ăn sáng`\n"
                    f"• Xem số dư: /balance\n"
                    f"• Xem giao dịch gần đây: /recent\n\n"
                    f"Thử ghi khoản chi tiêu ngay nhé!"
                )
                
                keyboard = [
                    [InlineKeyboardButton("💰 Xem số dư", callback_data="balance")],
                    [InlineKeyboardButton("📊 Giao dịch gần đây", callback_data="recent")],
                    [InlineKeyboardButton("⚙️ Cài đặt", callback_data="settings")],
                ]
                
            elif subscription_dto.tier == "PREMIUM":
                welcome_text = (
                    f"👋 Xin chào lại {user.first_name}!\n\n"
                    f"💎 **Tài khoản PREMIUM** của bạn đang hoạt động.\n\n"
                    f"🚀 **Bạn có thể:**\n"
                    f"• Ghi chi tiêu siêu nhanh: `chi 50k ăn sáng`\n"
                    f"• Phân tích AI: /insights\n"
                    f"• Xem báo cáo: /report\n"
                    f"• Đặt mục tiêu: /goals\n\n"
                    f"Hãy tận dụng tối đa các tính năng Premium!"
                )
                
                keyboard = [
                    [InlineKeyboardButton("💰 Xem số dư", callback_data="balance"),
                     InlineKeyboardButton("🤖 AI Insights", callback_data="ai_insights")],
                    [InlineKeyboardButton("📊 Báo cáo", callback_data="report"),
                     InlineKeyboardButton("🎯 Mục tiêu", callback_data="goals")],
                    [InlineKeyboardButton("⚙️ Cài đặt", callback_data="settings")],
                ]
            
            else:
                welcome_text = f"👋 Xin chào {user.first_name}!\n\nChào mừng đến với FreedomWallet Bot!"
                keyboard = [[InlineKeyboardButton("❓ Trợ giúp", callback_data="help")]]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # For FREE tier, send image with caption (like legacy)
            if subscription_dto.tier == "FREE":
                image_path = Path("media/images/web_apps.jpg")
                try:
                    await update.message.reply_photo(
                        photo=open(image_path, 'rb'),
                        caption=welcome_text,
                        parse_mode="Markdown",
                        reply_markup=reply_markup
                    )
                except Exception as e:
                    logger.error(f"Error sending photo: {e}")
                    # Fallback to text only
                    await update.message.reply_text(
                        welcome_text,
                        reply_markup=reply_markup,
                        parse_mode="Markdown"
                    )
            else:
                # Other tiers: text only
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            
        finally:
            session.close()
    
    except Exception as e:
        logger.exception(f"Error in start_command for user {user.id}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại sau."
        )
