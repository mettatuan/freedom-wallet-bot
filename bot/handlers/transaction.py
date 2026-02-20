"""
Transaction Handler - Quick Record Flow
Handle natural language transaction input and keyboard actions
"""
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from sqlalchemy.orm import Session
from loguru import logger

from bot.core.nlp import parse_natural_language_transaction
from bot.core.keyboard import (
    get_main_keyboard,
    BTN_OVERVIEW, BTN_RECORD, BTN_WEEKLY, BTN_INSIGHT,
    BTN_DRIVE, BTN_WEBAPP, BTN_REFERRAL, BTN_SETTINGS
)
from bot.utils.database import Transaction, User, get_db
from datetime import datetime


async def handle_quick_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle quick transaction input.
    
    Flow:
    1. User types: "Cà phê 35k"
    2. Parse natural language → extract amount, category, type
    3. Save to database
    4. Show confirmation with balance update
    
    Example inputs:
    - "Cà phê 35k" → Expense: -35,000đ (Ăn uống)
    - "Lương 15tr" → Income: +15,000,000đ (Lương)
    - "Grab 50k" → Expense: -50,000đ (Di chuyển)
    """
    message_text = update.message.text
    user_id = update.effective_user.id
    
    # Skip if it's a keyboard button press
    if message_text in [BTN_OVERVIEW, BTN_RECORD, BTN_WEEKLY, BTN_INSIGHT,
                        BTN_DRIVE, BTN_WEBAPP, BTN_REFERRAL, BTN_SETTINGS]:
        return
    
    # Parse transaction
    parsed = parse_natural_language_transaction(message_text)
    
    # Check for errors
    if "error" in parsed:
        await update.message.reply_text(
            f"❌ {parsed['error']}\n\n"
            f"💡 Thử lại: 'Cà phê 35k' hoặc 'Lương 15tr'",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Save to database
    db: Session = next(get_db())
    try:
        # Create transaction record
        transaction = Transaction(
            user_id=user_id,
            amount=parsed['amount'],
            category=parsed['category'],
            description=parsed['description'],
            transaction_type=parsed['type'],
            created_at=datetime.utcnow()
        )
        db.add(transaction)
        
        # Update user's first_transaction_at if needed
        user = db.query(User).filter(User.telegram_id == user_id).first()
        if user and not user.first_transaction_at:
            user.first_transaction_at = datetime.utcnow()
        
        db.commit()
        
        # Auto-sync to Google Sheets (if configured)
        from bot.core.sheets_sync import sync_transaction_to_sheets
        try:
            await sync_transaction_to_sheets(transaction.id, user_id, db)
        except Exception as e:
            # Don't fail the transaction if sync fails
            logger.warning(f"Sheets sync failed for transaction {transaction.id}: {e}")
        
        # Calculate new balance
        total_income = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'income'
        ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        
        total_expense = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'expense'
        ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        
        balance = total_income + total_expense  # Expenses are negative
        
        # Format confirmation message
        from bot.core.nlp import format_vnd
        
        amount_display = format_vnd(parsed['amount'])
        balance_display = format_vnd(balance)
        
        emoji = "💸" if parsed['type'] == "expense" else "💰"
        type_label = "Chi" if parsed['type'] == "expense" else "Thu"
        
        confirmation = (
            f"✅ Đã ghi nhận!\n\n"
            f"{emoji} {type_label}: {amount_display}\n"
            f"📁 {parsed['category']}\n"
            f"📝 {parsed['description']}\n\n"
            f"💰 Số dư hiện tại: {balance_display}"
        )
        
        await update.message.reply_text(
            confirmation,
            reply_markup=get_main_keyboard()
        )
        
    except Exception as e:
        db.rollback()
        await update.message.reply_text(
            f"❌ Lỗi khi lưu giao dịch: {str(e)}\n\n"
            f"Vui lòng thử lại sau.",
            reply_markup=get_main_keyboard()
        )
    finally:
        db.close()


async def handle_overview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 📊 Tổng quan button - Show balance and quick stats"""
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    try:
        # Get awareness snapshot
        from bot.core.awareness import get_awareness_snapshot, format_awareness_message
        
        snapshot = get_awareness_snapshot(user_id, db)
        message = format_awareness_message(snapshot)
        
        message += f"\n💡 Gõ nhanh: 'Cà phê 35k' để ghi ngay!"
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        
    finally:
        db.close()


async def handle_record_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ➕ Ghi giao dịch button - Show quick record guide"""
    message = (
        f"➕ <b>Ghi giao dịch nhanh</b>\n\n"
        f"Chỉ cần gõ vào ô chat, ví dụ:\n\n"
        f"• Cà phê 35k\n"
        f"• Ăn trưa 50k\n"
        f"• Grab 40k\n"
        f"• Lương 15tr\n\n"
        f"Bot sẽ tự động:\n"
        f"✅ Phân loại (Ăn uống, Di chuyển...)\n"
        f"✅ Tính số dư\n"
        f"✅ Đồng bộ Google Sheets\n\n"
        f"Gõ ngay để thử! 💬"
    )
    
    await update.message.reply_text(
        message,
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )


async def handle_weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 📈 Báo cáo tuần button - Show weekly insight"""
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    try:
        from bot.core.reflection import generate_weekly_insight, format_weekly_insight_message
        
        # Generate insight
        insight = generate_weekly_insight(user_id, db)
        message = format_weekly_insight_message(insight)
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    finally:
        db.close()


async def handle_insight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 💡 Insight button - Show behavioral analysis"""
    user_id = update.effective_user.id
    
    db: Session = next(get_db())
    try:
        from bot.core.behavioral import get_behavioral_snapshot, format_behavioral_message
        
        # Get behavioral snapshot
        snapshot = get_behavioral_snapshot(user_id, db)
        message = format_behavioral_message(snapshot)
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    finally:
        db.close()


def register_transaction_handlers(application):
    """Register all transaction-related handlers"""
    
    # Keyboard button handlers (exact match)
    from bot.core.keyboard import (
        BTN_OVERVIEW, BTN_RECORD, BTN_WEEKLY, BTN_INSIGHT,
        BTN_DRIVE, BTN_WEBAPP, BTN_REFERRAL, BTN_SETTINGS
    )
    
    application.add_handler(MessageHandler(
        filters.Text([BTN_OVERVIEW]),
        handle_overview
    ))
    
    application.add_handler(MessageHandler(
        filters.Text([BTN_RECORD]),
        handle_record_button
    ))
    
    application.add_handler(MessageHandler(
        filters.Text([BTN_WEEKLY]),
        handle_weekly_report
    ))
    
    application.add_handler(MessageHandler(
        filters.Text([BTN_INSIGHT]),
        handle_insight
    ))
    
    # Wire up existing handlers to keyboard buttons
    # 🔗 Kết nối Drive → sheets_setup
    from bot.handlers.sheets_setup import handle_connect_sheets_wizard
    application.add_handler(MessageHandler(
        filters.Text([BTN_DRIVE]),
        handle_connect_sheets_wizard
    ))
    
    # 🌐 Mở Web App → webapp_setup (step 1)
    from bot.handlers.webapp_setup import send_webapp_setup_step
    async def handle_open_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await send_webapp_setup_step(update, context, step=1)
    
    application.add_handler(MessageHandler(
        filters.Text([BTN_WEBAPP]),
        handle_open_webapp
    ))
    
    # 🎁 Giới thiệu → referral handler
    from bot.handlers.referral import referral_command
    application.add_handler(MessageHandler(
        filters.Text([BTN_REFERRAL]),
        referral_command
    ))
    
    # ⚙️ Cài đặt → settings menu
    application.add_handler(MessageHandler(
        filters.Text([BTN_SETTINGS]),
        handle_settings_menu
    ))
    
    # Natural language transaction handler (catch-all for non-button text)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_quick_transaction
    ))


async def handle_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle ⚙️ Cài đặt button - Show settings menu"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🔔 Nhắc nhở hàng ngày", callback_data="settings_reminder")],
        [InlineKeyboardButton("📊 Xuất dữ liệu CSV", callback_data="settings_export")],
        [InlineKeyboardButton("🗑️ Xóa tất cả giao dịch", callback_data="settings_delete_all")],
        [InlineKeyboardButton("ℹ️ Thông tin tài khoản", callback_data="settings_account")]
    ]
    
    await update.message.reply_text(
        "⚙️ <b>Cài đặt</b>\n\n"
        "Chọn mục bạn muốn thay đổi:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
