from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def tutorial_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with links to tutorials."""
    
    text = """
ðŸ“š **HÆ°á»›ng Dáº«n Sá»­ Dá»¥ng**

ðŸŽ¬ **Video Tutorials:**
Coming soon...

ðŸ“– **TÃ i liá»‡u:**
â€¢ [HÆ°á»›ng dáº«n báº¯t Ä‘áº§u](https://freedomwallet.com/docs/start)
â€¢ [6 HÅ© tiá»n chi tiáº¿t](https://freedomwallet.com/docs/jars)
â€¢ [Äáº§u tÆ° & ROI](https://freedomwallet.com/docs/investment)

ðŸ’¡ Hoáº·c há»i mÃ¬nh trá»±c tiáº¿p: "LÃ m sao thÃªm giao dá»‹ch?"
"""
    
    keyboard = [
        [InlineKeyboardButton("ðŸ  Vá» trang chá»§", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

