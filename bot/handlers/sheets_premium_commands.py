"""
Sheets Premium Commands Handler
Commands for users who connected Google Sheets: /balance, /spending
"""
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.utils.database import get_db, User
from bot.services.sheets_api_client import SheetsAPIClient
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
                f"Lỗi: {error_msg}\n\n"
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
            message += f"   └ {balance:,.0f} ₫\n\n"
        
        message += f"━━━━━━━━━━━━━━━\n"
        message += f"💎 **Tổng cộng: {total_balance:,.0f} ₫**\n\n"
        message += f"📊 Dùng /spending để xem chi tiêu tháng này nhé!"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"✅ User {user_id} checked balance: {total_balance:,.0f}")
    
    except Exception as e:
        logger.error(f"❌ Error getting balance: {e}")
        await update.message.reply_text(
            f"❌ **Có lỗi xảy ra**\n\n"
            f"Lỗi: {str(e)}\n\n"
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
    
    # Get recent transactions
    await update.message.reply_text("🔄 Đang phân tích chi tiêu...\n⏳ Vui lòng đợi...")
    
    try:
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        result = await client.get_recent_transactions(limit=10)
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            await update.message.reply_text(
                f"❌ **Không lấy được dữ liệu**\n\n"
                f"Lỗi: {error_msg}\n\n"
                f"Vui lòng thử lại. 😢",
                parse_mode="Markdown"
            )
            return
        
        transactions = result.get("transactions", [])
        count = result.get("count", 0)
        
        if count == 0:
            await update.message.reply_text(
                "📊 **PHÂN TÍCH CHI TIÊU**\n\n"
                "Chưa có giao dịch nào!\n\n"
                "Hãy thử ghi một chi tiêu:\n"
                "`chi 50k tiền ăn`",
                parse_mode="Markdown"
            )
            return
        
        # Format transactions
        message = f"📊 **{count} GIAO DỊCH GẦN ĐÂY**\n\n"
        
        for i, tx in enumerate(transactions[:10], 1):
            date = tx.get("date", "N/A")
            tx_type = tx.get("type", "Chi")
            amount = tx.get("amount", 0)
            note = tx.get("note", "")
            
            emoji = "💸" if tx_type == "Chi" else "💰"
            message += f"{i}. {emoji} {date}\n"
            message += f"   └ {amount:,.0f} ₫ - {note}\n\n"
        
        message += f"💡 Dùng /balance để xem số dư nhé!"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"✅ User {user_id} checked spending: {count} transactions")
    
    except Exception as e:
        logger.error(f"❌ Error getting spending: {e}")
        await update.message.reply_text(
            f"❌ **Có lỗi xảy ra**\n\n"
            f"Lỗi: {str(e)}\n\n"
            f"Vui lòng thử lại sau. 😢",
            parse_mode="Markdown"
        )


def register_sheets_premium_commands(application):
    """Register premium commands for Sheets-connected users"""
    
    application.add_handler(CommandHandler("balance", handle_balance))
    application.add_handler(CommandHandler("spending", handle_spending))
    
    logger.info("✅ Sheets premium commands registered (/balance, /spending)")
