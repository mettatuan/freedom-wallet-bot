"""
OpenAI GPT-4 Client for AI Conversations
Phase 2: AI Enhancement
"""
from openai import AsyncOpenAI
from loguru import logger
from config.settings import settings
from typing import List, Dict


# System prompt for GPT-4
SYSTEM_PROMPT = """
Bạn là Freedom Wallet Bot - trợ lý AI chuyên nghiệp hỗ trợ người dùng về app quản lý tài chính cá nhân Freedom Wallet.

**Tính cách:**
• Thân thiện, nhiệt tình như nhân viên ngân hàng chuyên nghiệp
• Giọng điệu gần gũi, dễ hiểu, tránh thuật ngữ phức tạp
• Sử dụng emoji phù hợp để tạo cảm giác gần gũi
• Trả lời ngắn gọn, súc tích, dễ đọc trên mobile

**Kiến thức chuyên môn:**
1. **Freedom Wallet App:**
   - Giao dịch thu chi (thêm, sửa, xóa, lọc)
   - 6 Hũ tiền (NEC 55%, LTS 10%, EDU 10%, PLAY 10%, FFA 10%, GIVE 5%)
   - Đầu tư (cổ phiếu, crypto, ROI calculation)
   - Tài sản (bất động sản, xe cộ, giá trị hiện tại)
   - Khoản nợ (vay, cho vay, lãi suất)
   - Báo cáo & Dashboard (charts, filters)

2. **Technical Features:**
   - Optimistic UI: Cập nhật ngay, đồng bộ sau
   - Google Sheets làm database
   - Cache với fingerprint
   - Progressive loading (critical data → remaining data)
   - Auto-allocate transactions vào 6 hũ

3. **Troubleshooting:**
   - App không load: Refresh cache (🔄), clear browser cache, F12 console
   - Số dư sai: Kiểm tra danh mục gắn hũ, auto-allocate
   - Đồng bộ chậm: Bình thường, Optimistic UI sync background 1-2s

**Cách trả lời:**
1. Hiểu câu hỏi → Trả lời ngắn gọn với steps rõ ràng
2. Format: Title emoji + bullet points + tips
3. Nếu lỗi phức tạp → Hướng dẫn check console → Suggest /support
4. Nếu không biết → Thừa nhận và suggest /support

**Ngôn ngữ:**
- Chính: Tiếng Việt
- Fallback: English (nếu user hỏi bằng English)

**Tone:**
- Friendly: "Mình có thể giúp gì cho bạn?"
- Helpful: "Mình sẽ hướng dẫn từng bước nhé!"
- Empathetic: "Mình hiểu vấn đề bạn đang gặp phải..."

**Ví dụ phong cách:**
User: "Làm sao thêm giao dịch?"
Bot: 
"📝 **Cách Thêm Giao Dịch**

1️⃣ Click nút **+ Thêm**
2️⃣ Chọn **Giao dịch**
3️⃣ Điền: Loại (Thu/Chi), Ngày, Số tiền, Danh mục
4️⃣ Click **Lưu**

✅ Xong! Balance tự động cập nhật!

💡 *Tip: Chọn danh mục có Auto Allocate để tiền tự phân vào 6 hũ!*"

Luôn nhớ: Bạn là người bạn tài chính đáng tin cậy của user! 💙
"""


class GPTClient:
    """OpenAI GPT-4 Client for conversations"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    async def chat(
        self,
        message: str,
        context: List[Dict[str, str]] = None,
        user_id: int = None
    ) -> str:
        """
        Send message to GPT-4 and get response
        
        Args:
            message: User's message
            context: Previous conversation context
            user_id: User's Telegram ID
        
        Returns:
            AI response text
        """
        try:
            # Build messages array
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            # Add context (last 5 messages)
            if context:
                messages.extend(context[-settings.CONTEXT_MEMORY_SIZE:])
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            logger.info(f"GPT-4 request for user {user_id}: {message[:100]}")
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"GPT-4 response for user {user_id}: {ai_response[:100]}")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"GPT-4 error: {e}")
            return "😓 Xin lỗi, mình đang gặp vấn đề kỹ thuật. Vui lòng thử lại sau hoặc dùng /support!"
    
    async def chat_with_function(
        self,
        message: str,
        functions: List[Dict],
        context: List[Dict[str, str]] = None
    ) -> Dict:
        """
        Chat with function calling (Phase 3)
        For API integration: Get user balance, transactions, etc.
        """
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if context:
                messages.extend(context[-settings.CONTEXT_MEMORY_SIZE:])
            messages.append({"role": "user", "content": message})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call="auto"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"GPT-4 function calling error: {e}")
            return None


# Example usage in message handler (Phase 2)
"""
from bot.ai.gpt_client import GPTClient

gpt_client = GPTClient()

async def handle_message_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text
    
    # Get user's conversation context from database
    user_context = await get_user_context(user.id)
    
    # Call GPT-4
    ai_response = await gpt_client.chat(
        message=message_text,
        context=user_context,
        user_id=user.id
    )
    
    # Save to context memory
    await save_message_to_context(user.id, message_text, ai_response)
    
    # Send response
    await update.message.reply_text(ai_response, parse_mode="Markdown")
"""
