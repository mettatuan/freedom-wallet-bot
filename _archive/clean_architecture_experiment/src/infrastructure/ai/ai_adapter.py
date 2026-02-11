"""OpenAI/AI service adapter for natural language processing."""

from typing import Optional, List, Dict, Any
import openai
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class AIServiceAdapter:
    """Adapter for OpenAI API (AI services)."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize AI service adapter.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4)
        """
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Optional[str]:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text or None if failed
        """
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to generate completion: {e}")
            return None
    
    async def parse_transaction(
        self,
        message: str,
        categories: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Parse transaction from natural language message.
        
        Args:
            message: User message (e.g., "chi 50k ăn sáng")
            categories: List of valid categories
            
        Returns:
            Parsed transaction dict with amount, category, note, or None
        """
        system_message = f"""Bạn là trợ lý phân tích giao dịch tài chính tiếng Việt.
Phân tích tin nhắn và trích xuất:
- amount: số tiền (dương = thu nhập, âm = chi tiêu)
- category: danh mục (chọn từ: {', '.join(categories)})
- note: ghi chú (tùy chọn)

Trả lời JSON format:
{{"amount": 50000, "category": "Ăn uống", "note": "Ăn sáng"}}"""
        
        try:
            response = await self.generate_completion(
                prompt=message,
                system_message=system_message,
                temperature=0.3,
                max_tokens=150
            )
            
            if not response:
                return None
            
            # Parse JSON response
            import json
            result = json.loads(response)
            
            return {
                "amount": float(result.get("amount", 0)),
                "category": result.get("category", "Khác"),
                "note": result.get("note", "")
            }
        except Exception as e:
            logger.error(f"Failed to parse transaction: {e}")
            return None
    
    async def categorize_transaction(
        self,
        description: str,
        categories: List[str]
    ) -> Optional[str]:
        """
        Suggest category for transaction description.
        
        Args:
            description: Transaction description
            categories: Available categories
            
        Returns:
            Suggested category or None
        """
        system_message = f"""Bạn là trợ lý phân loại giao dịch tài chính.
Dựa vào mô tả, chọn danh mục phù hợp nhất từ: {', '.join(categories)}
Chỉ trả lời tên danh mục, không giải thích."""
        
        try:
            response = await self.generate_completion(
                prompt=description,
                system_message=system_message,
                temperature=0.2,
                max_tokens=50
            )
            
            if response and response.strip() in categories:
                return response.strip()
            
            return None
        except Exception as e:
            logger.error(f"Failed to categorize transaction: {e}")
            return None
    
    async def generate_financial_insight(
        self,
        transactions: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate financial insights from transaction data.
        
        Args:
            transactions: List of transaction dictionaries
            context: Optional context (e.g., "monthly summary", "spending habits")
            
        Returns:
            Generated insight text or None
        """
        system_message = """Bạn là chuyên gia tư vấn tài chính.
Phân tích dữ liệu giao dịch và đưa ra insights ngắn gọn, hữu ích.
Trả lời bằng tiếng Việt, tối đa 3-4 câu."""
        
        # Summarize transactions
        total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
        total_expense = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
        balance = total_income - total_expense
        
        prompt = f"""Dữ liệu giao dịch:
- Tổng thu nhập: {total_income:,.0f} VNĐ
- Tổng chi tiêu: {total_expense:,.0f} VNĐ
- Số dư: {balance:,.0f} VNĐ
- Số giao dịch: {len(transactions)}

{f'Context: {context}' if context else ''}

Đưa ra nhận xét và lời khuyên ngắn gọn."""
        
        try:
            return await self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.7,
                max_tokens=300
            )
        except Exception as e:
            logger.error(f"Failed to generate insight: {e}")
            return None
    
    async def answer_question(
        self,
        question: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Answer user question about finances.
        
        Args:
            question: User question
            context: Optional context (user data, transaction history)
            
        Returns:
            Answer text or None
        """
        system_message = """Bạn là trợ lý tài chính thông minh của FreedomWallet.
Trả lời câu hỏi người dùng một cách thân thiện, chính xác, ngắn gọn.
Sử dụng tiếng Việt."""
        
        prompt = question
        if context:
            prompt = f"Context:\n{context}\n\nCâu hỏi: {question}"
        
        try:
            return await self.generate_completion(
                prompt=prompt,
                system_message=system_message,
                temperature=0.7,
                max_tokens=400
            )
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return None
    
    async def detect_intent(
        self,
        message: str,
        intents: List[str]
    ) -> Optional[str]:
        """
        Detect user intent from message.
        
        Args:
            message: User message
            intents: List of possible intents
            
        Returns:
            Detected intent or None
        """
        system_message = f"""Phân loại ý định của tin nhắn vào một trong các loại:
{', '.join(intents)}

Chỉ trả lời tên ý định, không giải thích."""
        
        try:
            response = await self.generate_completion(
                prompt=message,
                system_message=system_message,
                temperature=0.2,
                max_tokens=30
            )
            
            if response and response.strip() in intents:
                return response.strip()
            
            return None
        except Exception as e:
            logger.error(f"Failed to detect intent: {e}")
            return None
