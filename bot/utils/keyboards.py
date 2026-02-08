from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Tính năng", callback_data='features'), InlineKeyboardButton("🎬 Tutorial", callback_data='tutorial')],
        [InlineKeyboardButton("💬 Hỏi đáp", callback_data='faq'), InlineKeyboardButton("🆘 Hỗ trợ", callback_data='support')]
    ]
    return InlineKeyboardMarkup(keyboard)
