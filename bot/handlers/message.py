"""
Message Handler - Process user messages with FAQ or AI
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
import json
from pathlib import Path


# Load FAQ data
FAQ_FILE = Path(__file__).parent.parent / "knowledge" / "faq.json"
with open(FAQ_FILE, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)


def search_faq(query: str) -> dict:
    """
    Search FAQ based on keywords matching
    Returns: {"found": bool, "answer": str, "category": str}
    """
    query_lower = query.lower()
    
    # Check default responses first
    default_responses = FAQ_DATA.get("default_responses", {})
    
    # Greeting
    if any(word in query_lower for word in default_responses.get("greeting", [])):
        return {
            "found": True,
            "answer": default_responses.get("greeting_response"),
            "category": "greeting"
        }
    
    # Thanks
    if any(word in query_lower for word in default_responses.get("thanks", [])):
        return {
            "found": True,
            "answer": default_responses.get("thanks_response"),
            "category": "thanks"
        }
    
    # Goodbye
    if any(word in query_lower for word in default_responses.get("goodbye", [])):
        return {
            "found": True,
            "answer": default_responses.get("goodbye_response"),
            "category": "goodbye"
        }
    
    # Search in FAQ categories
    for category in FAQ_DATA.get("categories", []):
        for question in category.get("questions", []):
            keywords = question.get("keywords", [])
            
            # Check if any keyword matches
            if any(keyword.lower() in query_lower for keyword in keywords):
                return {
                    "found": True,
                    "answer": question.get("answer"),
                    "category": category.get("name"),
                    "icon": category.get("icon")
                }
    
    # Not found
    return {
        "found": False,
        "answer": None,
        "category": None
    }


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages from users"""
    
    user = update.effective_user
    message_text = update.message.text
    logger.info(f"User {user.id} ({user.username}): {message_text}")
    
    # Phase 1: Simple FAQ keyword matching
    faq_result = search_faq(message_text)
    
    if faq_result["found"]:
        # Found answer in FAQ
        answer = faq_result["answer"]
        category = faq_result.get("category", "")
        icon = faq_result.get("icon", "💬")
        
        # Quick action buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Giải quyết", callback_data="feedback_solved"),
                InlineKeyboardButton("❌ Vẫn lỗi", callback_data="feedback_unsolved")
            ],
            [
                InlineKeyboardButton("💬 Hỏi thêm", callback_data="ask_more"),
                InlineKeyboardButton("🆘 Liên hệ support", callback_data="contact_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            answer,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    else:
        # Not found - fallback response
        fallback_text = """
🤔 **Xin lỗi, mình chưa hiểu câu hỏi của bạn.**

💡 **Gợi ý:**
• Hỏi bằng từ khóa đơn giản: "thêm giao dịch", "6 hũ", "tính ROI"
• Dùng /help để xem danh sách câu hỏi phổ biến
• Hoặc /support để liên hệ support team

🔍 **Ví dụ câu hỏi:**
• Làm sao thêm giao dịch?
• 6 hũ tiền là gì?
• Cách chuyển tiền giữa hũ?

💬 Thử hỏi lại nhé!
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📚 Xem FAQ", callback_data="help_faq"),
                InlineKeyboardButton("🆘 Liên hệ support", callback_data="contact_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            fallback_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


# Phase 2: Upgrade to AI-powered conversation
"""
from bot.ai.gpt_client import GPTClient

gpt_client = GPTClient()

async def handle_message_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Enhanced version with GPT-4
    
    # Try FAQ first (faster)
    faq_result = search_faq(message_text)
    if faq_result["found"]:
        # Send FAQ answer
        ...
        return
    
    # If not in FAQ, use GPT-4
    try:
        # Get conversation context
        user_context = await get_user_context(user.id)
        
        # Call GPT-4
        ai_response = await gpt_client.chat(
            message=message_text,
            context=user_context,
            user_id=user.id
        )
        
        # Save to context memory
        await save_message_to_context(user.id, message_text, ai_response)
        
        # Send AI response
        await update.message.reply_text(ai_response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"GPT-4 error: {e}")
        # Fallback to not found message
        ...
"""
