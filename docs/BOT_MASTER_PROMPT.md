# 🤖 Freedom Wallet Bot - Master Prompt

**Version:** 1.0.0  
**Bot Name:** @FreedomWalletBot  
**Purpose:** AI-powered customer support assistant for Freedom Wallet app users

---

## 📋 Bot Overview

Create a professional Telegram bot that provides 24/7 intelligent customer support for Freedom Wallet - a personal finance management web application. The bot should act as a knowledgeable, friendly Vietnamese customer service representative who can:

1. Answer questions about app features
2. Guide users through common tasks
3. Troubleshoot issues
4. Provide financial tips using the 6 Jars method
5. Escalate complex issues to human support

---

## 🎯 Core Requirements

### 1. **Language & Tone**
- **Primary Language:** Vietnamese (friendly, professional)
- **Fallback:** English support
- **Tone:** Warm, helpful, empathetic like a banking advisor
- **Style:** Use emojis appropriately (💰, 📊, ✅, ❌, 💡)

### 2. **Key Capabilities**

#### A. Feature Explanation
Bot must explain:
- **6 Jars Money Management:** NEC (55%), LTS (10%), EDU (10%), PLAY (10%), FFA (10%), GIVE (5%)
- **Transactions:** Add income/expense with jar auto-allocation
- **Investments:** Track ROI, profit, buy/sell operations
- **Assets:** Real estate, vehicles with image upload
- **Debts:** Loan tracking with interest calculation
- **Accounts:** Multiple accounts (cash, bank, e-wallet)
- **Reports:** Charts, dashboards, financial journey

#### B. Common User Tasks
Guide users step-by-step:
1. "How to add a transaction?"
2. "How to transfer money between jars?"
3. "How to track investments?"
4. "How to add an asset?"
5. "How to view reports?"
6. "How to manage debts?"

#### C. Troubleshooting
Help with:
- Login issues
- Data not loading
- Jar balances incorrect
- Investment calculations wrong
- Images not uploading
- Sync problems between sheets

#### D. Financial Education
Provide tips on:
- 6 Jars method philosophy
- Budgeting best practices
- Investment basics
- Debt management strategies
- Saving goals

### 3. **Technical Integration**

#### A. Must Support
- `/start` - Welcome message + quick action buttons
- `/help` - Main menu with categories
- `/tutorial` - Interactive walkthrough video/GIF links
- `/support` - Contact human support (save request to Google Sheets)
- `/tips` - Daily financial tip
- `/status` - Check app status & announce maintenance

#### B. Smart Features
- **Context Memory:** Remember conversation history (last 5 messages)
- **Intent Recognition:** Understand variations:
  - "Làm sao thêm giao dịch?" = "How to add transaction?"
  - "Chuyển tiền giữa hũ" = "Transfer between jars"
  - "Sao số dư sai?" = "Balance incorrect"
- **Quick Replies:** Inline keyboard buttons for common actions
- **Rich Media:** Send screenshots, GIFs, tutorial videos
- **Multilingual:** Auto-detect language (vi/en)

### 4. **Data Sources**

#### A. Knowledge Base (Vector DB recommended)
- Freedom Wallet documentation
- FAQ from real user questions
- Tutorial scripts
- Error message catalog

#### B. Real-time Data (Optional Phase 2)
- Integrate with Freedom Wallet API
- Check user's last login
- View user's jar balances (with authentication)
- Send transaction reminders

---

## 🏗️ Technical Architecture

### Stack Recommendation

```
Bot Framework: python-telegram-bot (Python) or telegraf (Node.js)
AI/NLP: OpenAI GPT-4 or Claude API
Database: 
  - SQLite / PostgreSQL (user sessions)
  - Google Sheets (support tickets)
Vector DB: Pinecone / ChromaDB (knowledge base)
Hosting: Railway / Render / Google Cloud Run
```

### Folder Structure

```
freedom-wallet-bot/
├── bot/
│   ├── handlers/          # Command & message handlers
│   │   ├── start.py
│   │   ├── help.py
│   │   ├── support.py
│   │   └── tutorial.py
│   ├── ai/
│   │   ├── gpt_client.py  # OpenAI/Claude integration
│   │   ├── prompts.py     # System prompts
│   │   └── context.py     # Conversation memory
│   ├── knowledge/
│   │   ├── faq.json       # Structured FAQ
│   │   ├── docs/          # Freedom Wallet docs
│   │   └── embeddings.py  # Vector search
│   └── utils/
│       ├── keyboards.py   # Inline keyboards
│       ├── formatters.py  # Message formatting
│       └── validators.py  # Input validation
├── data/
│   ├── users.db           # SQLite database
│   └── support_tickets/   # Sheets integration
├── media/
│   ├── screenshots/       # Tutorial images
│   ├── gifs/              # Step-by-step GIFs
│   └── videos/            # Tutorial videos
├── config/
│   ├── .env               # API keys, tokens
│   └── settings.py        # Bot configuration
├── tests/
│   └── test_bot.py
├── requirements.txt
├── README.md
└── main.py               # Bot entry point
```

---

## 🎨 Conversation Flow Examples

### Example 1: Feature Question

```
User: Làm sao để thêm giao dịch?

Bot: 
📝 **Thêm Giao Dịch - Hướng Dẫn Chi Tiết**

Để thêm giao dịch mới, bạn làm theo các bước sau:

1️⃣ Mở Freedom Wallet
2️⃣ Click nút **"+ Thêm"** ở góc dưới bên phải
3️⃣ Chọn **"Giao dịch"**
4️⃣ Điền thông tin:
   • 💵 Loại: Thu / Chi
   • 📅 Ngày: Chọn ngày thực hiện
   • 💰 Số tiền: VD: 200,000
   • 🏷️ Danh mục: Ăn uống, Di chuyển, ...
   • 🏦 Tài khoản: Chọn tài khoản nguồn
   • 💼 Hũ tiền: (Tự động hoặc chọn thủ công)
   • 📝 Ghi chú: (Tùy chọn)
5️⃣ Click **"Lưu"**

✅ Giao dịch sẽ được lưu ngay lập tức và tính vào hũ tiền!

[Xem Video Hướng Dẫn 📹] [Câu hỏi khác? 💬]
```

### Example 2: Troubleshooting

```
User: Sao số dư hũ tôi sai sai?

Bot:
🔍 **Kiểm Tra Số Dư Hũ Tiền**

Mình sẽ giúp bạn kiểm tra nhé! Có 3 nguyên nhân phổ biến:

1️⃣ **Cache chưa refresh**
   ➡️ Thử click nút 🔄 ở góc trên để reload

2️⃣ **Giao dịch chưa phân bổ đúng hũ**
   ➡️ Kiểm tra lại "Danh mục" có gắn đúng hũ chưa

3️⃣ **Chuyển khoản giữa hũ chưa đồng bộ**
   ➡️ Đợi 2-3 giây để hệ thống đồng bộ

Bạn muốn mình:
[✅ Check chi tiết] [🔄 Hướng dẫn refresh] [👤 Liên hệ hỗ trợ]
```

### Example 3: Financial Tip

```
User: /tips

Bot:
💡 **Tip Tài Chính Hôm Nay** (#127)

📊 **Quy Tắc 50/30/20 kết hợp 6 Hũ**

Thay vì dùng 50/30/20 truyền thống, hãy dùng 6 Hũ của Freedom Wallet:
• 55% NEC: Chi tiêu thiết yếu (= 50%)
• 10% LTS: Tiết kiệm dài hạn (= 20% save)
• 10% EDU: Đầu tư bản thân
• 10% PLAY: Giải trí (gộp vào 30% flexible)
• 10% FFA: Tự do tài chính (đầu tư sinh lời)
• 5% GIVE: Từ thiện

✨ Lợi ích: Cân bằng giữa sống tốt hôm nay và tương lai!

[Xem thêm tips 📚] [Áp dụng ngay ⚡]
```

---

## 🔑 System Prompts (for AI)

### Main System Prompt

```
You are Freedom Wallet Bot, a friendly and professional Vietnamese customer support assistant for Freedom Wallet - a personal finance management app.

Your role:
- Answer questions about app features (6 Jars method, transactions, investments, assets, debts, reports)
- Guide users step-by-step through tasks
- Troubleshoot technical issues
- Provide financial education using the 6 Jars philosophy
- Escalate complex issues to human support

Communication style:
- Use Vietnamese as primary language (friendly, warm tone)
- Use appropriate emojis (💰, 📊, ✅, ❌, 💡)
- Be concise but thorough
- Use bullet points and numbered lists
- Include inline buttons for common actions
- End with helpful follow-up suggestions

Knowledge base:
- Freedom Wallet documentation
- 6 Jars Money Management method
- Vietnamese personal finance best practices

When uncertain:
- Say "Để mình kiểm tra kỹ hơn nhé!" and offer to escalate
- Never make up features or capabilities
- Always provide /support option for complex issues
```

### Troubleshooting Prompt

```
User is experiencing a technical issue with Freedom Wallet. 

Your approach:
1. Ask clarifying questions (1-2 max)
2. Provide 3 most likely solutions ranked by probability
3. Include step-by-step instructions with emojis
4. Offer screenshot/video tutorials
5. If unresolved after 3 attempts, escalate to /support

Common issues database:
- Login problems → Check email/password, clear cache
- Data not loading → Refresh, check internet, force reload with 🔄
- Jar balances wrong → Check jar allocation in categories, wait for sync
- Investment calculations → Verify buy price, current value, check ROI formula
- Images not uploading → Check file size (<5MB), format (JPG/PNG), internet speed

Always end with: "Đã giải quyết chưa bạn? [✅ Xong] [❌ Vẫn lỗi]"
```

---

## 📊 Analytics & Monitoring

### Track Metrics
- Total users
- Active daily/monthly users
- Most asked questions
- Support ticket volume
- Average resolution time
- User satisfaction (thumbs up/down)

### Logging
```python
# Log format
{
  "timestamp": "2026-02-06T10:30:00",
  "user_id": 123456789,
  "username": "@user",
  "message": "Làm sao thêm giao dịch?",
  "intent": "feature_question",
  "category": "transactions",
  "resolved": true,
  "satisfaction": "positive"
}
```

---

## 🚀 Implementation Phases

### Phase 1: MVP (Week 1-2)
- ✅ Basic bot setup (telegram-python-bot)
- ✅ /start, /help, /support commands
- ✅ FAQ handler (JSON-based)
- ✅ Simple keyword matching
- ✅ Google Sheets support ticket integration

### Phase 2: AI Enhancement (Week 3-4)
- 🤖 Integrate OpenAI GPT-4 API
- 🧠 Context memory (conversation history)
- 🔍 Vector search for knowledge base
- 📊 Intent classification
- 🎨 Rich media responses (images, GIFs)

### Phase 3: Advanced Features (Week 5-6)
- 🔗 API integration with Freedom Wallet (read-only)
- 📱 User authentication (verify app users)
- 🔔 Proactive notifications (transaction reminders)
- 📈 Personalized financial insights
- 🌐 Multilingual support (EN/VI)

### Phase 4: Scale & Optimize (Week 7-8)
- ⚡ Response caching
- 📊 Advanced analytics dashboard
- 🧪 A/B testing for prompts
- 🛡️ Rate limiting & abuse prevention
- 🎓 Machine learning from conversation data

---

## 🧪 Testing Checklist

### Functional Tests
- [ ] Bot responds to /start
- [ ] /help shows proper menu
- [ ] /support saves to Google Sheets
- [ ] FAQ answers are accurate
- [ ] Inline buttons work correctly
- [ ] Images/GIFs display properly

### Conversation Tests
- [ ] Understands Vietnamese variations
- [ ] Maintains context across 5 messages
- [ ] Handles typos gracefully
- [ ] Escalates appropriately
- [ ] Doesn't hallucinate features

### Edge Cases
- [ ] Handles spam/abuse
- [ ] Rate limiting works
- [ ] Graceful degradation if API down
- [ ] Handles non-Vietnamese languages
- [ ] Empty/invalid inputs

---

## 📝 Sample Bot Messages

### Welcome Message (/start)
```
👋 **Xin chào! Mình là Freedom Wallet Bot**

Mình là trợ lý AI hỗ trợ 24/7 cho ứng dụng quản lý tài chính Freedom Wallet 💰

🎯 **Mình có thể giúp bạn:**
• 📖 Tìm hiểu tính năng ứng dụng
• 🎓 Hướng dẫn sử dụng từng bước
• 🔧 Khắc phục sự cố kỹ thuật
• 💡 Chia sẻ tips tài chính hay
• 🆘 Liên hệ hỗ trợ nếu cần

**Hãy hỏi mình bất cứ điều gì!** 😊
Hoặc chọn nhanh bên dưới ⬇️

[📚 Tính năng] [🎬 Tutorial] [💬 Hỏi đáp] [🆘 Hỗ trợ]
```

### Error Message
```
😅 **Xin lỗi, mình chưa hiểu rõ câu hỏi!**

Bạn có thể nói rõ hơn hoặc chọn một trong các câu hỏi phổ biến:

• "Làm sao để thêm giao dịch?"
• "Hũ tiền 6 Jars là gì?"
• "Cách theo dõi đầu tư?"
• "Tại sao số dư sai?"

Hoặc dùng:
[📚 Menu chính] [💬 Chat với admin] [🔍 Tìm kiếm]
```

---

## 🔐 Security & Privacy

### Data Protection
- Store only necessary user data (user_id, username)
- No access to user's financial data without explicit permission
- Encrypt API keys and tokens
- Auto-delete old conversation logs (30 days)

### User Authentication
- For sensitive operations, require app login
- Generate one-time tokens for verification
- Never ask for passwords in chat
- Use OAuth flow for API integration

### Rate Limiting
```python
# Per user limits
MAX_MESSAGES_PER_MINUTE = 10
MAX_SUPPORT_TICKETS_PER_DAY = 3
COOLDOWN_AFTER_SPAM = 60  # seconds
```

---

## 📚 Documentation Links

### Freedom Wallet Resources
- Main App: https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
- Documentation: See `/FreedomWallet/docs/`
- GitHub: `D:/Projects/FreedomWallet`

### Bot Development Resources
- python-telegram-bot docs: https://docs.python-telegram-bot.org/
- OpenAI API: https://platform.openai.com/docs
- Telegram Bot API: https://core.telegram.org/bots/api

---

## 💡 Tips for Implementation

1. **Start Simple:** Begin with keyword matching before adding AI
2. **Log Everything:** Understand what users actually ask
3. **Iterate Fast:** Deploy daily, improve based on real usage
4. **Monitor Costs:** OpenAI API can be expensive, use caching
5. **User Feedback:** Add thumbs up/down after each response
6. **Fallback Plan:** Always have /support option ready

---

## 🎯 Success Metrics

### Target KPIs (Month 1)
- 📈 100+ active users
- ⏱️ <5s average response time
- ✅ >80% self-service resolution rate
- 😊 >4.5/5 user satisfaction
- 🎫 <10 support tickets/day

### Long-term Goals
- 🚀 1,000+ active users
- 🤖 95% automated resolution
- 💰 50% reduction in support costs
- 🌟 Net Promoter Score >50

---

**Ready to build? Start with Phase 1 MVP!**

*Last updated: February 6, 2026*
