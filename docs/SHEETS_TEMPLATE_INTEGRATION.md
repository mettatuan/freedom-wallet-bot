# 🚀 FREEDOM WALLET BOT INTEGRATION - OPTION 3 (TỐI ƯU NHẤT)

## Tổng quan

Thay vì user phải deploy Apps Script riêng, **sử dụng Apps Script CÓ SẴN** trong Freedom Wallet template.

---

## Kiến trúc

```
┌─────────────────────────────────────────────────────────────┐
│ FREEDOM WALLET TEMPLATE (Google Sheets)                    │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐  │
│ │ Apps Script (ĐÃ CÓ SẴN)                            │  │
│ │                                                       │  │
│ │ - doGet() → Return HTML interface                    │  │
│ │ - doPost() → Handle bot API requests (NEW)          │  │
│ │ - addTransactionsBatch() → Có sẵn                   │  │
│ │ - getAllData() → Có sẵn                             │  │
│ │                                                       │  │
│ │ ✅ Deploy as Web App (user CHỈ LÀM 1 LẦN)           │  │
│ └─────────────────────────────────────────────────────┘  │
│                                                             │
│ Sheets: Dashboard | Transactions | Accounts | ...          │
└─────────────────────────────────────────────────────────────┘
                          ↑↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│ TELEGRAM BOT                                                │
│                                                             │
│ User: "chi 50k tiền ăn"                                    │
│   ↓                                                          │
│ Bot parse → POST request                                    │
│   ↓                                                          │
│ POST https://script.google.com/.../exec                     │
│ Body: {action: "addTransaction", data: {...}}              │
│   ↓                                                          │
│ Apps Script → addTransactionsBatch()                        │
│   ↓                                                          │
│ ✅ Ghi vào Transactions sheet                              │
└─────────────────────────────────────────────────────────────┘
```

---

## So sánh 3 Options

| Tiêu chí | Option 1: Direct Write | Option 2: Custom Webhook | **Option 3: Template** ✅ |
|---------|------------------------|--------------------------|--------------------------|
| User setup | Share Editor | Copy code + Deploy | **Copy template only** |
| Bảo mật | ⚠️ Bot có Editor | ✅ Read-only | ✅ Read-only |
| Độ phức tạp | Đơn giản | Phức tạp (6 bước) | **Rất đơn giản (2 bước)** |
| Apps Script | Không cần | User tự deploy | **Có sẵn trong template** |
| Maintenance | Bot maintain | User maintain | **Template maintain** |
| Scale | ✅ Tốt | ⚠️ Mỗi user 1 script | ✅ **Tốt nhất** |
| Trust | ⚠️ Thấp | ✅ Cao | ✅ **Cao nhất** |

---

## Quy trình User

### **Option 3 - Template Integration:**

```
1. User: Click "Bắt đầu Premium" trong bot
   ↓
2. Bot: "Bạn đã có Freedom Wallet chưa?"
   [Đã có] | [Chưa có, tạo mới]
   ↓
3. Nếu chưa có:
   Bot: "Click link này để copy template"
   → https://docs.google.com/spreadsheets/.../copy
   ✅ Template tự động copy với Apps Script có sẵn
   ↓
4. Bot: "Gửi link Google Sheets của bạn"
   User paste: https://docs.google.com/spreadsheets/d/ABC123.../
   ↓
5. Bot extract Spreadsheet ID: ABC123...
   Bot: "🔄 Đang test kết nối..."
   ↓
6. Bot call:
   GET https://script.google.com/macros/s/DEPLOY_ID/exec?action=ping
   ↓
7. ✅ "Kết nối thành công! Giờ bạn có thể gõ: chi 50k tiền ăn"
```

---

## Thay đổi cần thiết

### 1. **Thêm doPost() vào Freedom Wallet Apps Script**

File: `FreedomWallet/Code-Refactored.gs`

```javascript
/**
 * doPost - Handle API requests from Telegram Bot
 * @param {Object} e - Event object with postData
 * @returns {Object} - JSON response
 */
function doPost(e) {
  try {
    // Parse request
    const params = JSON.parse(e.postData.contents);
    const action = params.action;
    const data = params.data;
    const apiKey = params.apiKey; // Verify bot
    
    // Check API key (optional security layer)
    const validApiKey = PropertiesService.getScriptProperties().getProperty('BOT_API_KEY');
    if (apiKey && apiKey !== validApiKey) {
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        error: 'Invalid API key'
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // Route actions
    let result;
    switch (action) {
      case 'ping':
        result = { success: true, message: 'Pong!' };
        break;
        
      case 'addTransaction':
        // Add single transaction
        result = addTransactionsBatch([data]);
        break;
        
      case 'addTransactions':
        // Add multiple transactions
        result = addTransactionsBatch(data);
        break;
        
      case 'getBalance':
        // Get jar balances
        const criticalData = getCriticalData(false);
        result = {
          success: criticalData.success,
          jars: criticalData.jars,
          accounts: criticalData.accounts
        };
        break;
        
      case 'getTransactions':
        // Get recent transactions
        const limit = data.limit || 10;
        const allData = getAllData(false);
        result = {
          success: allData.success,
          transactions: allData.transactions.slice(0, limit)
        };
        break;
        
      default:
        result = {
          success: false,
          error: `Unknown action: ${action}`
        };
    }
    
    return ContentService.createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    Logger.log(`❌ doPost error: ${error.toString()}`);
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * doGet - Handle GET requests (for testing & ping)
 * @param {Object} e - Event object with parameters
 * @returns {Object} - HTML or JSON response
 */
function doGet(e) {
  // If has action parameter, handle as API request
  if (e && e.parameter && e.parameter.action) {
    const action = e.parameter.action;
    
    if (action === 'ping') {
      return ContentService.createTextOutput(JSON.stringify({
        success: true,
        message: 'Freedom Wallet API is alive!',
        timestamp: new Date().toISOString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    if (action === 'getBalance') {
      const data = getCriticalData(false);
      return ContentService.createTextOutput(JSON.stringify({
        success: data.success,
        jars: data.jars
      })).setMimeType(ContentService.MimeType.JSON);
    }
  }
  
  // Default: Return HTML interface
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('Quản Lý Tài Chính Cá Nhân')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .setFaviconUrl('https://cdn-icons-png.flaticon.com/512/2331/2331717.png');
}
```

### 2. **Deploy Web App (CHẠY 1 LẦN DUY NHẤT)**

Sau khi thêm doPost():1. Click **Deploy → New deployment**
2. Type: **Web app**
3. Execute as: **Me**
4. Who has access: **Anyone**
5. Click **Deploy**
6. Copy **Web App URL**: `https://script.google.com/macros/s/DEPLOY_ID/exec`

**LƯU Ý:** URL này KHÔNG ĐỔI! Template có thể share với URL này.

### 3. **Bot Integration - NEW Approach**

File: `bot/handlers/sheets_template_integration.py` (NEW)

```python
"""
Freedom Wallet Template Integration
User chỉ cần share Spreadsheet ID
Bot tự động kết nối qua Apps Script có sẵn
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from bot.core.subscription import SubscriptionManager, SubscriptionTier
from bot.utils.database import get_user_by_id, SessionLocal
from bot.services.analytics import Analytics
import aiohttp
import re
from datetime import datetime

# Template URL (public, anyone can copy)
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/TEMPLATE_ID/copy"

# Apps Script Web App URL (deployed once, stable)
APPS_SCRIPT_URL = "https://script.google.com/macros/s/DEPLOY_ID/exec"


async def handle_start_premium_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start Premium setup flow
    Guide user to copy template or connect existing Sheets
    """
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    tier = SubscriptionManager.get_user_tier(user)
    
    if tier not in [SubscriptionTier.PREMIUM, SubscriptionTier.TRIAL]:
        await update.message.reply_text(
            "🔒 **Tính năng Premium**\n\n"
            "Vui lòng nâng cấp: /start"
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("✅ Đã có Freedom Wallet", callback_data="sheets_have_existing")],
        [InlineKeyboardButton("🆕 Tạo mới từ Template", callback_data="sheets_create_new")],
        [InlineKeyboardButton("❓ Freedom Wallet là gì?", callback_data="sheets_what_is")]
    ]
    
    await update.message.reply_text(
        "🎯 **CÀI ĐẶT PREMIUM**\n\n"
        "Để sử dụng tính năng Premium (AI phân tích, Quick Record):\n\n"
        "Bạn cần Freedom Wallet (Google Sheets) để lưu dữ liệu.\n\n"
        "**Bạn đã có Freedom Wallet chưa?**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    Analytics.track_event(user_id, 'premium_setup_started')


async def handle_create_new_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Guide user to copy Freedom Wallet template
    """
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy Template", url=TEMPLATE_URL)],
        [InlineKeyboardButton("✅ Đã copy, kết nối ngay", callback_data="sheets_connect")]
    ]
    
    await query.edit_message_text(
        "🆕 **TẠO FREEDOM WALLET MỚI**\n\n"
        "**Bước 1:** Click nút bên dưới để copy template\n"
        "→ Template sẽ tự động copy vào Google Drive của bạn\n"
        "→ Apps Script đã có sẵn, không cần setup gì!\n\n"
        "**Bước 2:** Sau khi copy xong, click \"Đã copy\"\n\n"
        "💡 **Template bao gồm:**\n"
        "• Hệ thống 6 Jars\n"
        "• Tracking giao dịch tự động\n"
        "• Dashboard phân tích\n"
        "• API tích hợp sẵn với bot\n\n"
        "🔒 **Bảo mật:** Dữ liệu 100% của bạn trên Google Drive",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    Analytics.track_event(update.effective_user.id, 'sheets_template_guide_viewed')


async def handle_connect_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request Spreadsheet URL/ID from user
    """
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔗 **KẾT NỐI GOOGLE SHEETS**\n\n"
        "**Cách 1:** Gửi link Google Sheets\n"
        "Ví dụ: `https://docs.google.com/spreadsheets/d/ABC123.../edit`\n\n"
        "**Cách 2:** Chỉ gửi Spreadsheet ID\n"
        "Ví dụ: `ABC123...` (44 ký tự)\n\n"
        "Gõ hoặc paste link/ID để kết nối:",
        parse_mode='Markdown'
    )
    
    # Store state: waiting for Spreadsheet ID
    context.user_data['waiting_for_sheets_id'] = True
    
    Analytics.track_event(update.effective_user.id, 'sheets_connect_requested')


async def handle_sheets_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receive and validate Spreadsheet ID from user
    """
    # Check if waiting for input
    if not context.user_data.get('waiting_for_sheets_id'):
        return
    
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    # Extract Spreadsheet ID from URL or raw ID
    spreadsheet_id = extract_spreadsheet_id(text)
    
    if not spreadsheet_id:
        await update.message.reply_text(
            "❌ **ID không hợp lệ!**\n\n"
            "Spreadsheet ID phải có 44 ký tự.\n\n"
            "Thử lại với:\n"
            "• Link đầy đủ: https://docs.google.com/spreadsheets/d/ABC.../edit\n"
            "• Hoặc chỉ ID: ABC123..."
        )
        return
    
    await update.message.reply_text(
        f"🔄 **Đang test kết nối...**\n\n"
        f"Spreadsheet ID: `{spreadsheet_id[:10]}...`\n\n"
        f"Vui lòng đợi...",
        parse_mode='Markdown'
    )
    
    # Test connection
    success, message, data = await test_sheets_connection(spreadsheet_id)
    
    if success:
        # Save to database
        db = SessionLocal()
        user = await get_user_by_id(user_id)
        user = db.merge(user)
        user.spreadsheet_id = spreadsheet_id
        user.sheets_connected_at = datetime.utcnow()
        db.commit()
        db.close()
        
        # Clear state
        context.user_data['waiting_for_sheets_id'] = False
        
        await update.message.reply_text(
            f"✅ **Kết nối thành công!**\n\n"
            f"📊 **Dữ liệu hiện tại:**\n"
            f"• Tổng tài sản: {data.get('total_balance', 0):,.0f} VNĐ\n"
            f"• Số tài khoản: {data.get('accounts_count', 0)}\n"
            f"• Giao dịch gần đây: {data.get('transactions_count', 0)}\n\n"
            f"🎉 **Sẵn sàng sử dụng Premium!**\n\n"
            f"**Thử ngay:**\n"
            f"• `chi 50k tiền ăn` - Ghi chi tiêu\n"
            f"• `/balance` - Xem số dư 6 jars\n"
            f"• `/spending` - Phân tích chi tiêu\n"
            f"• `/analyze` - AI phân tích tài chính",
            parse_mode='Markdown'
        )
        
        Analytics.track_event(user_id, 'sheets_connected_success', {
            'spreadsheet_id': spreadsheet_id[:10],
            'total_balance': data.get('total_balance', 0)
        })
        
        logger.info(f"User {user_id} connected sheets: {spreadsheet_id[:10]}...")
        
    else:
        await update.message.reply_text(
            f"❌ **Kết nối thất bại!**\n\n"
            f"Lỗi: {message}\n\n"
            f"**Kiểm tra:**\n"
            f"• Bạn đã copy template chưa?\n"
            f"• Link có đúng không?\n"
            f"• Spreadsheet có tồn tại không?\n\n"
            f"Thử lại: /connectsheets"
        )
        
        Analytics.track_event(user_id, 'sheets_connection_failed', {
            'error': message
        })


async def test_sheets_connection(spreadsheet_id: str) -> tuple:
    """
    Test connection to Freedom Wallet Apps Script
    
    Returns:
        (success: bool, message: str, data: dict)
    """
    try:
        # Construct Web App URL with Spreadsheet ID
        url = f"{APPS_SCRIPT_URL}?action=ping&spreadsheet_id={spreadsheet_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get('success'):
                        # Get balance data
                        balance_url = f"{APPS_SCRIPT_URL}?action=getBalance&spreadsheet_id={spreadsheet_id}"
                        async with session.get(balance_url, timeout=aiohttp.ClientTimeout(total=10)) as balance_response:
                            if balance_response.status == 200:
                                balance_data = await balance_response.json()
                                jars = balance_data.get('jars', [])
                                total = sum(float(jar.get('balance', 0)) for jar in jars)
                                
                                return True, "Connected", {
                                    'total_balance': total,
                                    'accounts_count': len(balance_data.get('accounts', [])),
                                    'transactions_count': 0  # Can fetch later
                                }
                        
                        return True, "Connected", {}
                    else:
                        return False, result.get('error', 'Unknown error'), {}
                else:
                    return False, f"HTTP {response.status}", {}
                    
    except aiohttp.ClientTimeout:
        return False, "Timeout - Apps Script không phản hồi", {}
    except Exception as e:
        return False, str(e), {}


def extract_spreadsheet_id(text: str) -> str:
    """
    Extract Spreadsheet ID from URL or raw ID
    
    Examples:
    - https://docs.google.com/spreadsheets/d/ABC123.../edit → ABC123...
    - ABC123... → ABC123...
    """
    # Pattern 1: Full URL
    url_pattern = r'spreadsheets/d/([a-zA-Z0-9_-]{30,})'
    match = re.search(url_pattern, text)
    if match:
        return match.group(1)
    
    # Pattern 2: Raw ID
    if re.match(r'^[a-zA-Z0-9_-]{30,}$', text):
        return text
    
    return None


# Register handlers
def register_sheets_template_handlers(application):
    """Register Freedom Wallet Template integration handlers"""
    from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters
    
    application.add_handler(CommandHandler("connectsheets", handle_start_premium_setup))
    
    application.add_handler(CallbackQueryHandler(
        handle_create_new_sheets,
        pattern="^sheets_create_new$"
    ))
    
    application.add_handler(CallbackQueryHandler(
        handle_connect_sheets,
        pattern="^sheets_connect|sheets_have_existing$"
    ))
    
    # Message handler for Spreadsheet ID input
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_sheets_id_input,
        block=False  # Allow other handlers to process too
    ))
    
    logger.info("✅ Sheets Template integration handlers registered")
```

---

## Ưu điểm tột đỉnh

1. ✅ **User KHÔNG phải setup Apps Script** (đã có sẵn trong template)
2. ✅ **Chỉ 2 bước:** Copy template + Gửi link
3. ✅ **Bot maintain Apps Script code** (update 1 lần, apply cho tất cả)
4. ✅ **Bảo mật:** Bot chỉ call Web App URL, không cần quyền gì
5. ✅ **Scale tốt:** 1 deployment cho tất cả users
6. ✅ **Transparent:** User thấy rõ template
7. ✅ **Trusted:** Template chính thức từ Freedom Wallet

---

## Next Steps

1. **Implement doPost() trong Freedom Wallet** Code-Refactored.gs
2. **Deploy Web App** (1 lần duy nhất)
3. **Tạo template public** với deployment ID
4. **Update bot** với sheets_template_integration.py
5. **Test full flow** với 1 user

---

## Deployment Checklist

- [ ] Thêm doPost() vào Code-Refactored.gs
- [ ] Deploy as Web App, copy URL
- [ ] Tạo template public với deployment
- [ ] Update APPS_SCRIPT_URL trong bot
- [ ] Test ping endpoint
- [ ] Test addTransaction endpoint
- [ ] Test getBalance endpoint
- [ ] Full E2E test: Copy template → Connect → Quick Record
- [ ] Update documentation
- [ ] Launch! 🚀
