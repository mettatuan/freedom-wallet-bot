"""Telegram Bot adapter for external communication."""

from typing import Optional, Dict, Any, List
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError
import logging

logger = logging.getLogger(__name__)


class TelegramAdapter:
    """Adapter for Telegram Bot API."""
    
    def __init__(self, bot: Bot):
        """
        Initialize Telegram adapter.
        
        Args:
            bot: Telegram Bot instance
        """
        self.bot = bot
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Send text message to user.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            reply_markup: Optional inline keyboard
            parse_mode: Parse mode (HTML, Markdown)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False
    
    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Edit existing message.
        
        Args:
            chat_id: Telegram chat ID
            message_id: Message ID to edit
            text: New message text
            reply_markup: Optional inline keyboard
            parse_mode: Parse mode
            
        Returns:
            True if edited successfully, False otherwise
        """
        try:
            await self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to edit message {message_id} in {chat_id}: {e}")
            return False
    
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False
    ) -> bool:
        """
        Answer callback query from inline keyboard.
        
        Args:
            callback_query_id: Callback query ID
            text: Optional notification text
            show_alert: Show as alert instead of notification
            
        Returns:
            True if answered successfully, False otherwise
        """
        try:
            await self.bot.answer_callback_query(
                callback_query_id=callback_query_id,
                text=text,
                show_alert=show_alert
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to answer callback query: {e}")
            return False
    
    async def send_photo(
        self,
        chat_id: int,
        photo_url: str,
        caption: Optional[str] = None
    ) -> bool:
        """
        Send photo to user.
        
        Args:
            chat_id: Telegram chat ID
            photo_url: Photo URL or file_id
            caption: Optional caption
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to send photo to {chat_id}: {e}")
            return False
    
    async def get_chat_member(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get chat member information.
        
        Args:
            chat_id: Chat ID
            user_id: User ID
            
        Returns:
            Chat member info or None
        """
        try:
            member = await self.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            return {
                "status": member.status,
                "user": {
                    "id": member.user.id,
                    "username": member.user.username,
                    "first_name": member.user.first_name,
                    "last_name": member.user.last_name
                }
            }
        except TelegramError as e:
            logger.error(f"Failed to get chat member {user_id} in {chat_id}: {e}")
            return None
    
    @staticmethod
    def create_inline_keyboard(buttons: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
        """
        Create inline keyboard markup.
        
        Args:
            buttons: List of button rows, each row is list of {"text": "...", "callback_data": "..."}
            
        Returns:
            InlineKeyboardMarkup instance
        """
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append(
                    InlineKeyboardButton(
                        text=button.get("text", ""),
                        callback_data=button.get("callback_data"),
                        url=button.get("url"),
                        web_app=button.get("web_app")
                    )
                )
            keyboard.append(keyboard_row)
        
        return InlineKeyboardMarkup(keyboard)
    
    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """
        Delete message.
        
        Args:
            chat_id: Chat ID
            message_id: Message ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            await self.bot.delete_message(chat_id=chat_id, message_id=message_id)
            return True
        except TelegramError as e:
            logger.error(f"Failed to delete message {message_id} in {chat_id}: {e}")
            return False
