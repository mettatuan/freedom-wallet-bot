"""Transaction recording handler using Clean Architecture."""

from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from decimal import Decimal
import re
from datetime import datetime

from ...infrastructure.di_container import get_container
from ...application.dtos import RecordTransactionInput


# Transaction parsing patterns
TRANSACTION_PATTERNS = [
    # chi 50k ăn sáng
    r'^(chi|spend|expense)\s+(\d+[km]?)\s+(.+)$',
    # thu 5tr lương
    r'^(thu|income|earn|salary)\s+(\d+[km]?|tr)\s+(.+)$',
    # -50k or +2000000
    r'^([-+])(\d+[km]?)\s+(.+)$',
]


def parse_amount(amount_str: str) -> Decimal:
    """
    Parse Vietnamese amount string to Decimal.
    
    Examples:
        50k -> 50000
        2tr -> 2000000
        1.5m -> 1500000
        100 -> 100
    """
    amount_str = amount_str.lower().strip()
    
    # Handle 'k' (nghìn = thousand)
    if 'k' in amount_str:
        base = float(amount_str.replace('k', ''))
        return Decimal(str(int(base * 1000)))
    
    # Handle 'tr' or 'm' (triệu = million)
    if 'tr' in amount_str or 'm' in amount_str:
        base = float(amount_str.replace('tr', '').replace('m', ''))
        return Decimal(str(int(base * 1000000)))
    
    # Plain number
    return Decimal(amount_str)


async def quick_record_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle quick transaction recording.
    
    Supported formats:
    - chi 50k ăn sáng
    - thu 5tr lương tháng 1
    - -100000 mua sách
    - +2000000 thưởng
    """
    # Skip if user is in a conversation (e.g., registration, setup)
    # ConversationHandler will handle the message instead
    if context.user_data:
        # User is likely in a conversation, let ConversationHandler process it
        # Don't process as transaction
        return None
    
    user = update.effective_user
    message_text = update.message.text.strip().lower()
    
    logger.info(f"User {user.id} sent transaction message: {message_text}")
    
    # Try to parse transaction
    transaction_type = None
    amount_str = None
    note = None
    
    for pattern in TRANSACTION_PATTERNS:
        match = re.match(pattern, message_text)
        if match:
            groups = match.groups()
            
            if len(groups) == 3:
                transaction_type = groups[0]
                amount_str = groups[1]
                note = groups[2].strip()
                break
    
    if not transaction_type or not amount_str:
        # Not a transaction command, ignore or handle as regular message
        return
    
    try:
        # Parse amount
        amount = parse_amount(amount_str)
        
        # Determine if income or expense
        if transaction_type in ['chi', 'spend', 'expense', '-']:
            amount = -abs(amount)  # Expense is negative
            category = "Chi tiêu"
        else:
            amount =abs(amount)  # Income is positive
            category = "Thu nhập"
        
        logger.info(f"Parsed transaction: amount={amount}, category={category}, note={note}")
        
        # Show processing message
        processing_msg = await update.message.reply_text("⏳ Đang kiểm tra...")
        
        # Execute use case
        container = get_container()
        session = container.get_db_session()
        
        try:
            # First, check if user has completed setup
            user_repository = container.get_user_repository(session)
            user_entity = await user_repository.get_by_id(user.id)
            
            if not user_entity or not user_entity.sheet_url or not user_entity.webapp_url:
                await processing_msg.edit_text(
                    "⚠️ **Chưa setup Sheet!**\n\n"
                    "Bạn cần hoàn tất setup trước khi ghi giao dịch.\n\n"
                    "📝 Sử dụng lệnh /setup để bắt đầu."
                )
                return
            
            # Update message
            await processing_msg.edit_text("⏳ Đang ghi vào Sheet...")
            
            # Execute transaction recording
            record_use_case = container.get_record_transaction_use_case(session)
            
            result = await record_use_case.execute(RecordTransactionInput(
                user_id=user.id,
                amount=amount,
                category=category,
                note=note or "",
                date=datetime.utcnow()
            ))
            
            if result.is_failure():
                logger.error(f"Failed to record transaction: {result.error_message}")
                await processing_msg.edit_text(
                    f"❌ Ghi thất bại: {result.error_message}"
                )
                return
            
            # Success!
            transaction_dto = result.data.transaction
            balance = result.data.balance
            
            # Format amount for display
            formatted_amount = f"{abs(float(amount)):,.0f}đ".replace(',', '.')
            
            # Emoji based on type
            emoji = "📉" if amount < 0 else "📈"
            
            success_message = (
                f"{emoji} **GHI THÀNH CÔNG!**\n\n"
                f"💰 Số tiền: {formatted_amount}\n"
                f"📂 Danh mục: {category}\n"
                f"📝 Ghi chú: {note or '(không có)'}\n\n"
                f"💳 **Số dư hiện tại:** {balance:,.0f}đ".replace(',', '.')
            )
            
            await processing_msg.edit_text(
                success_message,
                parse_mode="Markdown"
            )
            
            logger.info(f"✅ Transaction recorded for user {user.id}: {formatted_amount}")
            
        finally:
            session.close()
    
    except ValueError as e:
        logger.error(f"Invalid amount format: {amount_str}")
        await update.message.reply_text(
            f"❌ Số tiền không hợp lệ: {amount_str}\n\n"
            f"Ví dụ: chi 50k ăn sáng, thu 2tr lương"
        )
    except Exception as e:
        logger.exception(f"Error recording transaction for user {user.id}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra khi ghi giao dịch.\n"
            "Vui lòng thử lại sau."
        )


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current balance using CalculateBalanceUseCase."""
    user = update.effective_user
    logger.info(f"User {user.id} requested balance")
    
    try:
        container = get_container()
        session = container.get_db_session()
        
        try:
            calculate_balance_use_case = container.get_calculate_balance_use_case(session)
            
            result = await calculate_balance_use_case.execute(user.id)
            
            if result.is_failure():
                await update.message.reply_text(
                    f"❌ Không thể tính số dư: {result.error_message}"
                )
                return
            
            # Get balance data
            balance_data = result.data
            total_income = balance_data.total_income
            total_expense = balance_data.total_expense
            balance = balance_data.balance
            transaction_count = balance_data.transaction_count
            
            # Format message
            balance_message = (
                "💰 **SỐ DƯ CỦA BẠN**\n\n"
                f"📈 Tổng thu: {total_income:,.0f}đ\n"
                f"📉 Tổng chi: {total_expense:,.0f}đ\n"
                f"━━━━━━━━━━━━━━━\n"
                f"💳 **Số dư:** {balance:,.0f}đ\n\n"
                f"📊 Tổng {transaction_count} giao dịch"
            ).replace(',', '.')
            
            await update.message.reply_text(
                balance_message,
                parse_mode="Markdown"
            )
            
        finally:
            session.close()
    
    except Exception as e:
        logger.exception(f"Error getting balance for user {user.id}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra khi tính số dư."
        )


async def recent_transactions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent transactions."""
    user = update.effective_user
    logger.info(f"User {user.id} requested recent transactions")
    
    try:
        container = get_container()
        session = container.get_db_session()
        
        try:
            transaction_repo = container.get_transaction_repository(session)
            
            # Get recent transactions (last 10)
            transactions = await transaction_repo.get_recent(user.id, limit=10)
            
            if not transactions:
                await update.message.reply_text(
                    "📭 Chưa có giao dịch nào.\n\n"
                    "Thử ghi khoản đầu tiên: `chi 50k ăn sáng`",
                    parse_mode="Markdown"
                )
                return
            
            # Build message
            message_lines = ["📊 **GIAO DỊCH GẦN ĐÂY**\n"]
            
            for i, txn in enumerate(transactions, 1):
                amount = float(txn.amount)
                formatted_amount = f"{abs(amount):,.0f}đ".replace(',', '.')
                emoji = "📉" if amount < 0 else "📈"
                sign = "-" if amount < 0 else "+"
                
                date_str = txn.date.strftime("%d/%m")
                
                message_lines.append(
                    f"{i}. {emoji} {sign}{formatted_amount}\n"
                    f"   {txn.category} • {txn.note or '(không có ghi chú)'}\n"
                    f"   {date_str}\n"
                )
            
            message_lines.append("\n💡 Dùng /balance để xem tổng số dư")
            
            await update.message.reply_text(
                "\n".join(message_lines),
                parse_mode="Markdown"
            )
            
        finally:
            session.close()
    
    except Exception as e:
        logger.exception(f"Error getting recent transactions for user {user.id}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra khi lấy giao dịch."
        )
