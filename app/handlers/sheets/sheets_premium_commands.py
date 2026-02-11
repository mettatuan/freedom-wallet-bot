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
            "âš ï¸ Báº¡n chÆ°a káº¿t ná»‘i Google Sheets!\n\n"
            "DÃ¹ng /connectsheets Ä‘á»ƒ káº¿t ná»‘i trÆ°á»›c nhÃ©. ðŸ˜Š"
        )
        return
    
    # Get balance from Sheets
    await update.message.reply_text("ðŸ”„ Äang láº¥y sá»‘ dÆ°...\nâ³ Vui lÃ²ng Ä‘á»£i...")
    
    try:
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        result = await client.get_balance()
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            await update.message.reply_text(
                f"âŒ **KhÃ´ng láº¥y Ä‘Æ°á»£c sá»‘ dÆ°**\n\n"
                f"Lá»—i: {error_msg}\n\n"
                f"Vui lÃ²ng thá»­ láº¡i hoáº·c liÃªn há»‡ admin. ðŸ˜¢",
                parse_mode="Markdown"
            )
            return
        
        # Format balance message
        jars = result.get("jars", [])
        total_balance = result.get("totalBalance", 0)
        
        message = "ðŸ’° **Sá» DÆ¯ CÃC HÅ¨**\n\n"
        
        for jar in jars:
            icon = jar.get("icon", "ðŸº")
            name = jar.get("name", "Unknown")
            balance = jar.get("balance", 0)
            percentage = jar.get("percentage", 0)
            
            message += f"{icon} **{name}** ({percentage}%)\n"
            message += f"   â”” {balance:,.0f} â‚«\n\n"
        
        message += f"â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”\n"
        message += f"ðŸ’Ž **Tá»•ng cá»™ng: {total_balance:,.0f} â‚«**\n\n"
        message += f"ðŸ“Š DÃ¹ng /spending Ä‘á»ƒ xem chi tiÃªu thÃ¡ng nÃ y nhÃ©!"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"âœ… User {user_id} checked balance: {total_balance:,.0f}")
    
    except Exception as e:
        logger.error(f"âŒ Error getting balance: {e}")
        await update.message.reply_text(
            f"âŒ **CÃ³ lá»—i xáº£y ra**\n\n"
            f"Lá»—i: {str(e)}\n\n"
            f"Vui lÃ²ng thá»­ láº¡i sau. ðŸ˜¢",
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
            "âš ï¸ Báº¡n chÆ°a káº¿t ná»‘i Google Sheets!\n\n"
            "DÃ¹ng /connectsheets Ä‘á»ƒ káº¿t ná»‘i trÆ°á»›c nhÃ©. ðŸ˜Š"
        )
        return
    
    # Get recent transactions
    await update.message.reply_text("ðŸ”„ Äang phÃ¢n tÃ­ch chi tiÃªu...\nâ³ Vui lÃ²ng Ä‘á»£i...")
    
    try:
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        result = await client.get_recent_transactions(limit=10)
        
        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            await update.message.reply_text(
                f"âŒ **KhÃ´ng láº¥y Ä‘Æ°á»£c dá»¯ liá»‡u**\n\n"
                f"Lá»—i: {error_msg}\n\n"
                f"Vui lÃ²ng thá»­ láº¡i. ðŸ˜¢",
                parse_mode="Markdown"
            )
            return
        
        transactions = result.get("transactions", [])
        count = result.get("count", 0)
        
        if count == 0:
            await update.message.reply_text(
                "ðŸ“Š **PHÃ‚N TÃCH CHI TIÃŠU**\n\n"
                "ChÆ°a cÃ³ giao dá»‹ch nÃ o!\n\n"
                "HÃ£y thá»­ ghi má»™t chi tiÃªu:\n"
                "`chi 50k tiá»n Äƒn`",
                parse_mode="Markdown"
            )
            return
        
        # Format transactions
        message = f"ðŸ“Š **{count} GIAO Dá»ŠCH Gáº¦N ÄÃ‚Y**\n\n"
        
        for i, tx in enumerate(transactions[:10], 1):
            date = tx.get("date", "N/A")
            tx_type = tx.get("type", "Chi")
            amount = tx.get("amount", 0)
            note = tx.get("note", "")
            
            emoji = "ðŸ’¸" if tx_type == "Chi" else "ðŸ’°"
            message += f"{i}. {emoji} {date}\n"
            message += f"   â”” {amount:,.0f} â‚« - {note}\n\n"
        
        message += f"ðŸ’¡ DÃ¹ng /balance Ä‘á»ƒ xem sá»‘ dÆ° nhÃ©!"
        
        await update.message.reply_text(message, parse_mode="Markdown")
        logger.info(f"âœ… User {user_id} checked spending: {count} transactions")
    
    except Exception as e:
        logger.error(f"âŒ Error getting spending: {e}")
        await update.message.reply_text(
            f"âŒ **CÃ³ lá»—i xáº£y ra**\n\n"
            f"Lá»—i: {str(e)}\n\n"
            f"Vui lÃ²ng thá»­ láº¡i sau. ðŸ˜¢",
            parse_mode="Markdown"
        )


def register_sheets_premium_commands(application):
    """Register premium commands for Sheets-connected users"""
    
    application.add_handler(CommandHandler("balance", handle_balance))
    application.add_handler(CommandHandler("spending", handle_spending))
    
    logger.info("âœ… Sheets premium commands registered (/balance, /spending)")

