"""
Sheets Premium Commands Handler
Commands for users who connected Google Sheets: /balance, /spending
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.utils.database import get_db, User
from app.services.sheets_api_client import SheetsAPIClient
import logging

logger = logging.getLogger(__name__)


async def handle_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for /balance command
    Show balance of all jars
    """
    user_id = update.effective_user.id
    
    # Check if user has connected Sheets
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.spreadsheet_id:
        await update.message.reply_text(
            "⚠️ Bạn chưa kết nối Google Sheets!\n\n"
            "Dùng /connectsheets để kết nối trước nhé. 😊"
        )
        return
    
    # Get balance from Sheets
    await update.message.reply_text("🔄 Đang lấy số dư...\n⏳ Vui lòng đợi...")
    
    try:
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        result = await client.get_balance()
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            await update.message.reply_text(
                f"❌ **Không lấy được số dư**\n\n"
                f"Lá»—i: {error_msg}\n\n"
                f"Vui lòng thử lại hoặc liên hệ admin. 😢",
                parse_mode="Markdown"
            )
            return
        
        # Format balance message
        jars = result.get("jars", [])
        total_balance = result.get("totalBalance", 0)
        
        message = "💰 **SỐ DƯ CÁC HŨ**\n\n"
        
        for jar in jars:
            icon = jar.get("icon", "🏺")
            name = jar.get("name", "Unknown")
            balance = jar.get("balance", 0)
            percentage = jar.get("percentage", 0)
            
            message += f"{icon} **{name}** ({percentage}%)\n"
            message += f"   â"" {balance:,.0f} â'«\n\n"
        
        message += f"━━━━━━━━━━━━━━━\n"
        message += f"💎 **Tổng cộng: {total_balance:,.0f} ₫**\n\n"
        message += f"📊 Dùng /spending để xem chi tiêu tháng này nhé!"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"✅ User {user_id} checked balance: {total_balance:,.0f}")
    
    except Exception as e:
        logger.error(f"❌ Error getting balance: {e}")
        await update.message.reply_text(
            f"❌ **Có lỗi xảy ra**\n\n"
            f"Lá»—i: {str(e)}\n\n"
            f"Vui lòng thử lại sau. 😢",
            parse_mode="Markdown"
        )


async def handle_spending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for /spending command
    Show spending analysis (placeholder)
    """
    user_id = update.effective_user.id
    
    # Check if user has connected Sheets
    db = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.spreadsheet_id:
        await update.message.reply_text(
            "⚠️ Bạn chưa kết nối Google Sheets!\n\n"
            "Dùng /connectsheets để kết nối trước nhé. 😊"
        )
        return
    
    # Get recent transactions (limit 200 to get all monthly transactions)
    await update.message.reply_text("🔄 Đang phân tích chi tiêu tháng này...\n⏳ Vui lòng đợi...")
    
    try:
        from datetime import datetime
        
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        result = await client.get_recent_transactions(limit=200)
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            await update.message.reply_text(
                f"❌ **Không lấy được dữ liệu**\n\n"
                f"Lỗi: {error_msg}\n\n"
                f"Vui lòng thử lại. 😢",
                parse_mode="Markdown"
            )
            return
        
        # Filter transactions for current month
        all_transactions = result.get("transactions", [])
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_expenses = []
        total_expense = 0
        
        for txn in all_transactions:
            # Parse transaction date
            txn_date_str = txn.get('date', '')
            try:
                # Try different date formats
                if '/' in txn_date_str:
                    parts = txn_date_str.split('/')
                    if len(parts) == 3:
                        txn_day, txn_month, txn_year = int(parts[0]), int(parts[1]), int(parts[2])
                elif '-' in txn_date_str:
                    txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d")
                    txn_month = txn_date.month
                    txn_year = txn_date.year
                else:
                    continue
                
                # Filter: only "Chi" transactions in current month
                if txn_month == current_month and txn_year == current_year:
                    txn_type = txn.get('type', '').strip()
                    if txn_type == 'Chi':
                        txn_amount = abs(float(txn.get('amount', 0)))
                        total_expense += txn_amount
                        monthly_expenses.append(txn)
                        
            except (ValueError, IndexError):
                continue
        
        if len(monthly_expenses) == 0:
            await update.message.reply_text(
                "📊 **PHÂN TÍCH CHI TIÊU THÁNG NÀY**\n\n"
                "Chưa có giao dịch chi tiêu nào trong tháng này!\n\n"
                "Hãy thử ghi một chi tiêu:\n"
                "`chi 50k tiền ăn`",
                parse_mode="Markdown"
            )
            return
        
        # Format recent expenses (last 10)
        month_name = datetime.now().strftime("%m/%Y")
        message = f"📊 **CHI TIÊU THÁNG {month_name}**\n\n"
        message += f"💸 **Tổng chi:** {total_expense:,.0f} ₫\n"
        message += f"📝 **Số giao dịch:** {len(monthly_expenses)}\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"**{min(10, len(monthly_expenses))} GIAO DỊCH GẦN NHẤT:**\n\n"
        
        for i, tx in enumerate(monthly_expenses[-10:][::-1], 1):
            date = tx.get("date", "N/A")
            amount = abs(float(tx.get("amount", 0)))
            note = tx.get("note", "")
            category = tx.get("category", "")
            
            message += f"{i}. 💸 {date}\n"
            message += f"   └ {amount:,.0f} ₫ - {category or note}\n\n"
        
        message += f"💡 Dùng /balance để xem số dư nhé!"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"✅ User {user_id} analyzed spending: {len(monthly_expenses)} expenses, total {total_expense:,.0f}")
    
    except Exception as e:
        logger.error(f"❌ Error getting spending: {e}")
        await update.message.reply_text(
            f"❌ **Có lỗi xảy ra**\n\n"
            f"Lá»—i: {str(e)}\n\n"
            f"Vui lòng thử lại sau. 😢",
            parse_mode="Markdown"
        )


def register_sheets_premium_commands(application):
    """Register premium commands for Sheets-connected users"""
    
    application.add_handler(CommandHandler("balance", handle_balance))
    application.add_handler(CommandHandler("spending", handle_spending))
    
    logger.info("✅ Sheets premium commands registered (/balance, /spending)")

