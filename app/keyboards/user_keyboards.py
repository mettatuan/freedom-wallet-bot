from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("ðŸ“š TÃ­nh nÄƒng", callback_data='features'), InlineKeyboardButton("ðŸŽ¬ Tutorial", callback_data='tutorial')],
        [InlineKeyboardButton("ðŸ’¬ Há»i Ä‘Ã¡p", callback_data='faq'), InlineKeyboardButton("ðŸ†˜ Há»— trá»£", callback_data='support')]
    ]
    return InlineKeyboardMarkup(keyboard)

