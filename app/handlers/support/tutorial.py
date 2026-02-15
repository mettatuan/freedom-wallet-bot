from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def tutorial_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with links to tutorials."""
    
    text = """
📚 **Hướng Dẫn Sử Dụng**

🎬 **Video Tutorials:**
Coming soon...

📖 **Tài liệu:**
• [Hướng dẫn bắt đầu](https://freedomwallet.com/docs/start)
• [6 Hũ tiền chi tiết](https://freedomwallet.com/docs/jars)
• [Đầu tư & ROI](https://freedomwallet.com/docs/investment)

💡 Hoặc hỏi mình trực tiếp: "Làm sao thêm giao dịch?"
"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

