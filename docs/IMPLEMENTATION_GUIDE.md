# 🛠️ Implementation Guide - Freedom Wallet Bot

Step-by-step guide to build the bot from scratch.

---

## Phase 1: MVP Setup (Week 1-2)

### Step 1: Create Telegram Bot

```bash
# 1. Open Telegram and search for @BotFather
# 2. Send /newbot
# 3. Choose name: Freedom Wallet Bot
# 4. Choose username: @FreedomWalletBot (or similar)
# 5. Copy the bot token
```

### Step 2: Project Setup

```bash
# Create project directory
cd "D:/Projects"
mkdir "FreedomWalletBot"
cd "FreedomWalletBot"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup config
cp config/.env.example config/.env
# Edit .env with your tokens
```

### Step 3: Basic Bot Structure

Create these files:

**`config/settings.py`**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    OPENAI_API_KEY: str
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = "config/.env"

settings = Settings()
```

**`bot/handlers/start.py`**
```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    keyboard = [
        [InlineKeyboardButton("📚 Tính năng", callback_data="features")],
        [InlineKeyboardButton("🎬 Tutorial", callback_data="tutorial")],
        [InlineKeyboardButton("💬 Hỏi đáp", callback_data="faq")],
        [InlineKeyboardButton("🆘 Hỗ trợ", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 **Xin chào! Mình là Freedom Wallet Bot**\n\n"
        "Mình là trợ lý AI hỗ trợ 24/7 cho ứng dụng "
        "quản lý tài chính Freedom Wallet 💰\n\n"
        "🎯 **Mình có thể giúp bạn:**\n"
        "• 📖 Tìm hiểu tính năng ứng dụng\n"
        "• 🎓 Hướng dẫn sử dụng từng bước\n"
        "• 🔧 Khắc phục sự cố kỹ thuật\n"
        "• 💡 Chia sẻ tips tài chính hay\n"
        "• 🆘 Liên hệ hỗ trợ nếu cần\n\n"
        "**Hãy hỏi mình bất cứ điều gì!** 😊",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
```

### Step 4: FAQ System (Simple JSON)

**`bot/knowledge/faq.json`**
```json
{
  "categories": [
    {
      "id": "transactions",
      "name": "Giao dịch",
      "icon": "💰",
      "questions": [
        {
          "keywords": ["thêm giao dịch", "tạo giao dịch", "add transaction"],
          "answer": "📝 **Thêm Giao Dịch**\n\n1. Mở Freedom Wallet\n2. Click nút **+ Thêm**\n3. Chọn **Giao dịch**\n4. Điền thông tin:\n   • Loại: Thu/Chi\n   • Số tiền: VD 200000\n   • Danh mục: Chọn danh mục\n   • Tài khoản: Nguồn tiền\n5. Click **Lưu**\n\n✅ Xong!",
          "media": "screenshots/add-transaction.png"
        },
        {
          "keywords": ["xóa giao dịch", "delete transaction"],
          "answer": "🗑️ **Xóa Giao Dịch**\n\n1. Vào trang **Giao dịch**\n2. Click vào giao dịch muốn xóa\n3. Click biểu tượng 🗑️ **Xóa**\n4. Xác nhận xóa\n\n✅ Giao dịch đã bị xóa!"
        }
      ]
    },
    {
      "id": "jars",
      "name": "6 Hũ Tiền",
      "icon": "🏺",
      "questions": [
        {
          "keywords": ["6 hũ", "jars", "hũ tiền"],
          "answer": "🏺 **Phương pháp 6 Hũ Tiền**\n\nChia thu nhập thành 6 hũ:\n\n1. NEC (55%): Chi tiêu thiết yếu\n2. LTS (10%): Tiết kiệm dài hạn\n3. EDU (10%): Giáo dục, phát triển\n4. PLAY (10%): Giải trí\n5. FFA (10%): Tự do tài chính\n6. GIVE (5%): Cho đi, từ thiện\n\n💡 Giúp bạn cân bằng tài chính!"
        },
        {
          "keywords": ["chuyển hũ", "transfer jar", "chuyển tiền hũ"],
          "answer": "↔️ **Chuyển Tiền Giữa Hũ**\n\n1. Vào trang **6 Hũ**\n2. Click nút **Chuyển tiền**\n3. Chọn:\n   • Hũ nguồn: Hũ trừ tiền\n   • Hũ đích: Hũ nhận tiền\n   • Số tiền: VD 1000000\n4. Click **Chuyển**\n\n✅ Số dư cập nhật ngay!"
        }
      ]
    },
    {
      "id": "investments",
      "name": "Đầu tư",
      "icon": "📈",
      "questions": [
        {
          "keywords": ["thêm đầu tư", "add investment"],
          "answer": "📈 **Thêm Khoản Đầu Tư**\n\n1. Click **+ Thêm** → **Đầu tư**\n2. Điền thông tin:\n   • Tên: VD \"Cổ phiếu VNM\"\n   • Giá mua: 80000\n   • Số lượng: 100\n   • Vốn: 8000000\n   • Từ hũ: FFA\n3. Click **Lưu**\n\n✅ Hệ thống tự tính ROI!"
        }
      ]
    }
  ]
}
```

**`bot/handlers/message.py`** (Simple keyword matching)
```python
import json
from telegram import Update
from telegram.ext import ContextTypes

# Load FAQ
with open('bot/knowledge/faq.json', 'r', encoding='utf-8') as f:
    faq_data = json.load(f)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages with keyword matching"""
    user_message = update.message.text.lower()
    
    # Search FAQ
    for category in faq_data['categories']:
        for qa in category['questions']:
            for keyword in qa['keywords']:
                if keyword.lower() in user_message:
                    await update.message.reply_text(
                        qa['answer'],
                        parse_mode="Markdown"
                    )
                    return
    
    # Not found - suggest help
    await update.message.reply_text(
        "🤔 Xin lỗi, mình chưa hiểu câu hỏi!\n\n"
        "Bạn có thể:\n"
        "• Dùng /help để xem menu\n"
        "• Hỏi cụ thể hơn\n"
        "• Dùng /support để chat admin"
    )
```

### Step 5: Google Sheets Support Tickets

**`bot/handlers/support.py`**
```python
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

# Setup Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(
    'config/google-credentials.json', 
    scopes=SCOPES
)
gc = gspread.authorize(creds)
sheet = gc.open_by_key('YOUR_SHEET_ID').sheet1

async def support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support requests"""
    # Ask for issue description
    await update.message.reply_text(
        "🆘 **Hỗ trợ khách hàng**\n\n"
        "Vui lòng mô tả vấn đề của bạn, "
        "mình sẽ ghi nhận và phản hồi sớm!"
    )
    
    # Wait for next message
    context.user_data['waiting_for_support'] = True

async def support_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save support ticket to sheet"""
    if context.user_data.get('waiting_for_support'):
        user = update.effective_user
        message = update.message.text
        
        # Save to sheet
        sheet.append_row([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            user.id,
            user.username or 'N/A',
            user.full_name,
            message,
            'Pending'
        ])
        
        await update.message.reply_text(
            "✅ **Đã ghi nhận yêu cầu!**\n\n"
            "Support team sẽ phản hồi trong 24h.\n"
            "Ticket ID: #" + str(user.id)
        )
        
        context.user_data['waiting_for_support'] = False
```

### Step 6: Test MVP

```bash
# Run bot
python main.py

# Test in Telegram:
# 1. Search @FreedomWalletBot
# 2. /start
# 3. Ask: "Làm sao thêm giao dịch?"
# 4. Test /support
```

---

## Phase 2: AI Enhancement (Week 3-4)

### Step 1: OpenAI Integration

**`bot/ai/gpt_client.py`**
```python
import openai
from config.settings import settings

openai.api_key = settings.OPENAI_API_KEY

SYSTEM_PROMPT = """
You are Freedom Wallet Bot, a friendly Vietnamese customer support assistant.
Answer questions about Freedom Wallet app features, guide users step-by-step,
and provide financial tips using the 6 Jars method.
Use emojis appropriately and be concise.
"""

async def get_ai_response(user_message: str, conversation_history: list = None):
    """Get response from GPT-4"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if conversation_history:
        messages.extend(conversation_history[-5:])  # Last 5 messages
    
    messages.append({"role": "user", "content": user_message})
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content
```

### Step 2: Context Memory

**`bot/ai/context.py`**
```python
from typing import Dict, List

# In-memory storage (use Redis in production)
user_contexts: Dict[int, List[dict]] = {}

def add_message(user_id: int, role: str, content: str):
    """Add message to user context"""
    if user_id not in user_contexts:
        user_contexts[user_id] = []
    
    user_contexts[user_id].append({
        "role": role,
        "content": content
    })
    
    # Keep only last 10 messages
    if len(user_contexts[user_id]) > 10:
        user_contexts[user_id] = user_contexts[user_id][-10:]

def get_context(user_id: int) -> List[dict]:
    """Get user conversation context"""
    return user_contexts.get(user_id, [])

def clear_context(user_id: int):
    """Clear user context"""
    if user_id in user_contexts:
        del user_contexts[user_id]
```

### Step 3: Update Message Handler

**`bot/handlers/message.py` (with AI)**
```python
from bot.ai.gpt_client import get_ai_response
from bot.ai.context import add_message, get_context

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages with AI"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Add user message to context
    add_message(user_id, "user", user_message)
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    # Get AI response
    conversation_history = get_context(user_id)
    ai_response = await get_ai_response(user_message, conversation_history)
    
    # Add AI response to context
    add_message(user_id, "assistant", ai_response)
    
    # Send response
    await update.message.reply_text(ai_response, parse_mode="Markdown")
```

---

## Phase 3: Production Deployment

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set TELEGRAM_BOT_TOKEN=your_token
railway variables set OPENAI_API_KEY=your_key

# Deploy
railway up
```

### Create `Procfile`
```
worker: python main.py
```

### Create `railway.json`
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## 🎓 Next Steps

1. ✅ Complete MVP (Phase 1)
2. 🤖 Add AI capabilities (Phase 2)
3. 🚀 Deploy to production
4. 📊 Monitor usage & iterate
5. 🔗 Integrate with Freedom Wallet API (Phase 3)

---

**Happy Building! 🚀**
