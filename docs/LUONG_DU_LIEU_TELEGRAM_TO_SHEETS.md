# Luồng Xử Lý Dữ Liệu: Telegram Bot → Apps Script → Google Sheets

## 📊 Sơ Đồ Kiến Trúc

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                             │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                    "chi 50k ăn sáng" hoặc "đầu tư SP500 27tr"
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  TELEGRAM BOT (FreedomWalletBot)                                     │
│  📂 bot/handlers/quick_record_template.py                            │
│                                                                       │
│  ✅ STEP 1: Smart Parsing (lines 197-280)                           │
│     - Detect type: Chi / Thu / Đầu tư                               │
│     - Extract amount: 50k → 50,000 | 1.5tr → 1,500,000             │
│     - Filter SP500 bug (không parse "500" từ "SP500")              │
│     - Generate note: "ăn sáng" | "đầu tư SP500"                    │
│                                                                       │
│  ✅ STEP 2: Category Matching (lines 82-177)                        │
│     - Lấy categories từ API: /getCategories                         │
│     - Match: Exact → Partial → Keywords                             │
│     - Investment keywords: sp500, btc, vn30, etc. (20+)            │
│                                                                       │
│  ✅ STEP 3: Get User Data (lines 611-620)                           │
│     from bot.utils.database import User                             │
│     user = db.query(User).filter(User.id == user_id).first()       │
│     spreadsheet_id = user.spreadsheet_id  ← LƯU Ở DATABASE         │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                    user.spreadsheet_id (44 chars)
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SHEETS API CLIENT                                                   │
│  📂 bot/services/sheets_api_client.py                                │
│                                                                       │
│  ✅ Initialize (line 22):                                            │
│     client = SheetsAPIClient(user.spreadsheet_id)                   │
│                                                                       │
│  ✅ Build Payload (lines 33-45):                                     │
│     {                                                                │
│       "action": "addTransaction",                                    │
│       "spreadsheet_id": user.spreadsheet_id,                        │
│       "data": {                                                      │
│         "type": "Chi",          // hoặc "Thu", "Đầu tư"            │
│         "amount": 50000,                                             │
│         "category": "Ăn uống",                                       │
│         "note": "ăn sáng",                                           │
│         "fromJar": "NEC",       // auto-select based on category    │
│         "fromAccount": "Cash",                                       │
│         "date": "2026-02-09"    // ISO format                       │
│       }                                                              │
│     }                                                                │
│                                                                       │
│  ✅ API Call (lines 49-75):                                          │
│     POST to SHEETS_API_URL (line 13)                                │
│     URL: https://script.google.com/macros/s/                        │
│          AKfycbwzT4WokC13aouSr8f3X_2gxiAORid_gzObwFS187.../exec     │
│     Timeout: 30 seconds                                              │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                        HTTP POST (JSON)
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GOOGLE APPS SCRIPT API                                              │
│  📂 bot-api-handler-vietnamese.gs                                    │
│                                                                       │
│  ✅ doPost() Entry Point (lines 6-62):                               │
│     - Parse JSON body                                                │
│     - Extract: action, spreadsheet_id, data                         │
│     - Route to handler function                                      │
│                                                                       │
│  ✅ handleAddTransaction() (lines 163-207):                          │
│     - Open spreadsheet by ID:                                        │
│       ss = SpreadsheetApp.openById(spreadsheet_id)                  │
│                                                                       │
│     - Find sheet "Giao dịch" or "Transactions"                      │
│                                                                       │
│     - Generate Transaction ID (lines 172-174):                       │
│       transactionId = Utilities.formatDate(                          │
│         now, timezone, 'yyyyMMdd_HHmmss'                            │
│       )  // 20260209_143052                                         │
│                                                                       │
│     - Format Date to dd/MM/yyyy (lines 178-183):                     │
│       ISO "2026-02-09" → "09/02/2026"                               │
│                                                                       │
│     - Smart Category Matching (lines 80-148):                        │
│       findOrCreateCategory(ss, note, type)                          │
│       → Exact match → Partial match → Create new                    │
│                                                                       │
│     - Build Row (lines 187-195):                                     │
│       [transactionId, date, type, jarId, category,                  │
│        amount, fromAccount, toAccount, note]                        │
│                                                                       │
│     - Append to Sheet:                                               │
│       transactionsSheet.appendRow(row)                              │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                    Write to Google Sheets
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  GOOGLE SHEETS (User's Spreadsheet)                                  │
│                                                                       │
│  Sheet: "Giao dịch" (or "Transactions")                             │
│                                                                       │
│  Row Structure:                                                      │
│  ┌─────┬────────────┬──────┬──────┬──────────┬─────────┬─────┐    │
│  │  A  │     B      │  C   │  D   │    E     │    F    │ ... │    │
│  ├─────┼────────────┼──────┼──────┼──────────┼─────────┼─────┤    │
│  │ ID  │   Ngày     │ Loại │ Jar  │ Danh mục │ Số tiền │ ... │    │
│  ├─────┼────────────┼──────┼──────┼──────────┼─────────┼─────┤    │
│  │20260│ 09/02/2026 │ Chi  │ NEC  │ Ăn uống  │ 50,000  │ ... │    │
│  │209_ │            │      │      │          │         │     │    │
│  │1430 │            │      │      │          │         │     │    │
│  │52   │            │      │      │          │         │     │    │
│  └─────┴────────────┴──────┴──────┴──────────┴─────────┴─────┘    │
│                                                                       │
│  ✅ All formulas in sheet continue working:                          │
│     - SUM(), SUMIF(), VLOOKUP(), etc.                               │
│     - Dashboard charts auto-update                                   │
│     - Jar balances recalculate                                       │
└──────────────────────────────┬──────────────────────────────────────┘
                                │
                     Data synchronized ✅
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  BIDIRECTIONAL SYNC                                                  │
│                                                                       │
│  Bot → Sheets ✅                    Sheets → Web App ✅             │
│  (via Apps Script API)              (direct read/write)              │
│                                                                       │
│  Google Sheets = SINGLE SOURCE OF TRUTH                              │
│  No local database for transactions                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Các File Quan Trọng

### 1. Handler - Parse User Input
**File:** `bot/handlers/quick_record_template.py` (1011 lines)

**Line 197-280: Smart Parsing Function**
```python
def parse_quick_record_message(text: str) -> tuple[str, float, str]:
    # Step 1: Detect type (Chi/Thu/Đầu tư)
    # Step 2: Extract amount (with SP500 bug fix)
    # Step 3: Remove keywords and get note
    # Step 4: Smart defaulting
```

**Line 965-1011: Handler Registration**
```python
def register_quick_record_handlers(application):
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Regex(
                r'\d+(?:[,.\d]*)?(?:\s*(?:k|tr|triệu|nghìn|nghin)\b|(?:,\d{3})+)'
            ),  # Match ALL amount patterns
            handle_quick_record
        ),
        group=0  # HIGH PRIORITY - process before AI
    )
```

**Line 611-620: Get User Spreadsheet ID**
```python
db = next(get_db())
user = db.query(User).filter(User.id == user_id).first()
if not user or not user.spreadsheet_id:
    await query.edit_message_text("⚠️ Không tìm thấy spreadsheet ID")
```

### 2. API Client - Connect to Apps Script
**File:** `bot/services/sheets_api_client.py` (259 lines)

**Line 13: API URL**
```python
SHEETS_API_URL = "https://script.google.com/macros/s/AKfycbwzT4WokC13aouSr8f3X_2gxiAORid_gzObwFS187o8nw4_aI_DpLq6Mx38QRP_q2cc/exec"
```

**Line 101-150: Add Transaction Method**
```python
async def add_transaction(
    self, amount: float, category: str, note: str,
    from_jar: str = "NEC", from_account: str = "Cash",
    to_account: str = ""
) -> Dict[str, Any]:
    # Build transaction data
    transaction_data = {
        "date": datetime.now().strftime('%Y-%m-%d'),  # ISO format
        "type": self._detect_type(note),  # Chi/Thu/Đầu tư
        "amount": amount,
        "category": category,
        "note": note,
        "fromJar": from_jar,
        "fromAccount": from_account,
        "toAccount": to_account
    }
    
    # Call API
    return await self._call_api("addTransaction", {"data": transaction_data})
```

### 3. Apps Script Handler
**File:** `bot-api-handler-vietnamese.gs` (459 lines)

**Line 6-62: Entry Point**
```javascript
function doPost(e) {
  const params = JSON.parse(e.postData.contents);
  const action = params.action;  // "addTransaction"
  const spreadsheet_id = params.spreadsheet_id;
  const data = params.data;
  
  switch (action) {
    case 'addTransaction':
      result = handleAddTransaction(spreadsheet_id, data);
      break;
  }
  
  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}
```

**Line 163-207: Write to Sheet**
```javascript
function handleAddTransaction(spreadsheetId, transaction) {
  // Open user's spreadsheet
  const ss = SpreadsheetApp.openById(spreadsheetId);
  
  // Generate ID from date+time
  const transactionId = Utilities.formatDate(
    now, timezone, 'yyyyMMdd_HHmmss'
  );
  
  // Format date to dd/MM/yyyy
  const dateParts = transaction.date.split('-');  // [2026, 02, 09]
  formattedDate = `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}`;
  
  // Smart category matching
  const category = findOrCreateCategory(ss, transaction.note, transaction.type);
  
  // Build row
  const row = [
    transactionId,           // A: 20260209_143052
    formattedDate,           // B: 09/02/2026
    transaction.type,        // C: Chi/Thu/Đầu tư
    transaction.fromJar,     // D: NEC/FFA/PLAY
    category,                // E: Ăn uống
    transaction.amount,      // F: 50000
    transaction.fromAccount, // G: Cash
    transaction.toAccount,   // H: (empty)
    transaction.note         // I: ăn sáng
  ];
  
  // Append to sheet
  transactionsSheet.appendRow(row);
  
  return { success: true, transactionId, category };
}
```

### 4. User Database Model
**File:** `bot/utils/database.py` (474 lines)

**Line 100: Spreadsheet ID Field**
```python
class User(Base):
    spreadsheet_id = Column(String(100), nullable=True)  # 44 chars Google Sheets ID
    sheets_connected_at = Column(DateTime, nullable=True)
    sheets_last_sync = Column(DateTime, nullable=True)
    webhook_url = Column(String(500), nullable=True)
    web_app_url = Column(String(500), nullable=True)
```

---

## ✅ Trạng Thái Hiện Tại

### Đã Có Sẵn ✅
- ✅ Smart parsing với flexible word order (20 patterns)
- ✅ Investment transaction support (Đầu tư type)
- ✅ SP500 bug fix (filter product code numbers)
- ✅ Handler registration (group=0 priority)
- ✅ Sheets API client với URL mới nhất
- ✅ Apps Script với date formatting dd/MM/yyyy
- ✅ Database schema với spreadsheet_id
- ✅ Category smart matching (exact → partial → keywords)
- ✅ Bidirectional sync architecture

### Cần User Làm ⚠️
1. **Connect Spreadsheet** (one-time setup per user):
   ```
   User: /connectsheets
   Bot: "Nhập link Google Sheets của bạn"
   User: [paste link]
   Bot: ✅ Lưu spreadsheet_id vào database
   ```

2. **Share Spreadsheet with Service Account**:
   - User copy Freedom Wallet template
   - Share với service account email: `...@...iam.gserviceaccount.com`
   - Permission: Editor (to write transactions)

3. **Test Quick Record**:
   ```
   User: "chi 50k ăn sáng"
   Bot: [Parse] → [Match category] → [Call API] → [Write to sheet] → ✅ Success
   ```

---

## 🔄 Luồng Xử Lý Chi Tiết

### Input: "đầu tư SP500 27tr"

**STEP 1: Parse (quick_record_template.py)**
```python
text = "đầu tư SP500 27tr"

# Detect type
"đầu tư" in INVESTMENT_KEYWORDS → type = "Đầu tư"

# Extract amount (with SP500 fix)
all_matches = ["500", "27tr"]  # regex tìm được 2 số
filter: "500" có "P" ngay phía trước → bỏ qua
valid_matches = ["27tr"]
amount = parse_amount("27tr") → 27,000,000

# Remove keywords
note = "đầu tư SP500"  # Keep "đầu tư" (semantic), remove nothing

Result: ("Đầu tư", 27000000, "đầu tư SP500")
```

**STEP 2: Category Matching (quick_record_template.py)**
```python
categories = await client.get_categories()  # 53 categories including 12 investment

# Try exact match
"đầu tư SP500" == "Chứng khoán" ❌

# Try partial match
"đầu tư SP500" contains "chứng khoán" ❌

# Try keywords
"sp500" in note_lower → keywords['sp500'] = 'Chứng khoán' ✅

matched_category = {
  "name": "Chứng khoán",
  "icon": "📈",
  "jarId": "FFA",
  "type": "Đầu tư"
}
```

**STEP 3: API Call (sheets_api_client.py)**
```python
client = SheetsAPIClient(user.spreadsheet_id)

payload = {
  "action": "addTransaction",
  "spreadsheet_id": "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg",
  "data": {
    "date": "2026-02-09",
    "type": "Đầu tư",
    "amount": 27000000,
    "category": "Chứng khoán",
    "note": "đầu tư SP500",
    "fromJar": "FFA",
    "fromAccount": "VCB"
  }
}

POST to SHEETS_API_URL
```

**STEP 4: Apps Script Processing (bot-api-handler-vietnamese.gs)**
```javascript
// Generate ID
transactionId = "20260209_143052"

// Format date
"2026-02-09" → "09/02/2026"

// Build row
row = [
  "20260209_143052",    // A: ID
  "09/02/2026",         // B: Ngày
  "Đầu tư",             // C: Loại
  "FFA",                // D: Jar
  "Chứng khoán",        // E: Danh mục
  27000000,             // F: Số tiền
  "VCB",                // G: Tài khoản
  "",                   // H: Đích
  "đầu tư SP500"        // I: Ghi chú
]

// Write to sheet
transactionsSheet.appendRow(row)

// Return success
{
  "success": true,
  "transactionId": "20260209_143052",
  "category": "Chứng khoán",
  "timestamp": "2026-02-09T14:30:52.123Z"
}
```

**STEP 5: Bot Confirmation**
```
✅ Đã ghi thành công!

• Đầu tư: 27,000,000 ₫
• Danh mục: 📈 Chứng khoán
• Hũ: FFA - 📈 Đầu tư & Tự do tài chính
• Tài khoản: VCB
• Ghi chú: đầu tư SP500
• Thời gian: 2026-02-09T14:30:52.123Z

💡 Dùng /balance để xem số dư nhé!
```

---

## 🧪 Test Script

Để verify hệ thống hoạt động:

```python
# test_telegram_to_sheets_flow.py
import asyncio
from bot.services.sheets_api_client import SheetsAPIClient

async def test_flow():
    # STEP 1: Test API connectivity
    spreadsheet_id = "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg"
    client = SheetsAPIClient(spreadsheet_id)
    
    print("1️⃣ Testing API connection...")
    ping = await client.ping()
    print(f"   {'✅' if ping['success'] else '❌'} {ping}")
    
    # STEP 2: Get categories
    print("\n2️⃣ Getting categories...")
    cats = await client.get_categories()
    print(f"   ✅ {cats['count']} categories loaded")
    
    # STEP 3: Test transaction
    print("\n3️⃣ Testing add transaction...")
    result = await client.add_transaction(
        amount=50000,
        category="Ăn uống",
        note="test từ bot",
        from_jar="NEC",
        from_account="Cash"
    )
    print(f"   {'✅' if result['success'] else '❌'} {result}")

asyncio.run(test_flow())
```

---

## 📋 Checklist Deploy

- [x] ✅ Smart parsing code (quick_record_template.py)
- [x] ✅ SP500 bug fix (filter product codes)
- [x] ✅ Investment support (Đầu tư type)
- [x] ✅ API client với URL mới (sheets_api_client.py)
- [x] ✅ Apps Script deployed (bot-api-handler-vietnamese.gs)
- [x] ✅ Date formatting dd/MM/yyyy
- [x] ✅ Category matching với 20+ keywords
- [x] ✅ Handler registration (main.py)
- [x] ✅ Database schema (spreadsheet_id field)
- [ ] ⚠️ User test: /connectsheets
- [ ] ⚠️ User test: "chi 50k ăn sáng"
- [ ] ⚠️ User test: "đầu tư SP500 27tr"

---

## 🎯 Kết Luận

**Hệ thống ĐÃ SẴN SÀNG để xử lý luồng dữ liệu từ Telegram Bot → Apps Script → Google Sheets!**

Không cần fix gì thêm trong code FreedomWallet. Chỉ cần:
1. User connect spreadsheet (one-time)
2. Test với các lệnh thực tế
3. Verify data ghi vào sheet đúng format

Tất cả đã được implement với:
- Smart parsing ✅
- Investment support ✅  
- SP500 bug fix ✅
- Date formatting ✅
- Bidirectional sync ✅
