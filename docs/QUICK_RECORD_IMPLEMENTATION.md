# 🎯 QUICK RECORD - Ghi chi tiêu tự nhiên qua chat

## Tổng quan

**Quick Record** là tính năng Premium cho phép user gõ chat tự nhiên để ghi chi tiêu ngay lập tức:

```
User: chi 50k tiền ăn
Bot: ✅ Đã ghi thành công! Chi: 50,000 VNĐ - Ăn uống
```

---

## 2 PHƯƠNG ÁN TRIỂN KHAI

### **Option 1: Service Account với quyền EDITOR** ✏️

**Kiến trúc:**
```
Bot → Google Sheets API → Ghi trực tiếp vào Sheets
     (READ + WRITE)         (append row)
```

**Ưu điểm:**
- ✅ Đơn giản, reliable
- ✅ Không cần setup Apps Script
- ✅ Bot kiểm soát 100% quá trình ghi

**Nhược điểm:**
- ⚠️ User lo ngại bảo mật (bot có quyền XÓA data)
- ⚠️ Rủi ro nếu credentials bị lộ
- ⚠️ User phải share quyền Editor (cao hơn cần thiết)

**Setup User:**
1. Copy Google Sheets template
2. Share quyền **Editor** cho service account
3. Gửi Spreadsheet ID cho bot: `/setsheet ID`
4. Xong! Bắt đầu gõ: `chi 50k tiền ăn`

**Implementation:**
- File: `bot/services/sheets_writer.py` (270 lines)
- File: `bot/handlers/quick_record_direct.py` (200 lines)
- Scopes: `spreadsheets` (full read/write)
- Method: `append()` API call

---

### **Option 2: Google Apps Script Webhook** 🎯 **(KHUYẾN NGHỊ)**

**Kiến trúc:**
```
Bot → POST request → Apps Script → Ghi vào Sheets
     (webhook)         (user's code)   (user's permission)
```

**Ưu điểm:**
- ✅ **BẢO MẬT hơn:** Bot KHÔNG có quyền ghi, chỉ gửi request
- ✅ User vẫn 100% control
- ✅ Apps Script chạy dưới quyền USER (không phải bot)
- ✅ Có thể validate/transform data trước khi ghi
- ✅ User chỉ share quyền **Viewer** cho bot
- ✅ Dễ audit (xem Apps Script logs)

**Nhược điểm:**
- ⚠️ Setup phức tạp hơn (cần copy code Apps Script)
- ⚠️ Phụ thuộc vào Apps Script uptime
- ⚠️ User phải deploy Web App

**Setup User:**
1. Copy Google Sheets template
2. Share quyền **Viewer** cho service account (READ only)
3. Vào Extensions → Apps Script
4. Copy code webhook (cung cấp sẵn)
5. Deploy as Web App
6. Gửi webhook URL cho bot: `/setwebhook URL`
7. Xong! Bắt đầu gõ: `chi 50k tiền ăn`

**Implementation:**
- File: `bot/handlers/quick_record_webhook.py` (450 lines)
- Method: HTTP POST với aiohttp
- Apps Script: `doPost(e)` function
- Payload: JSON với date, category, amount, jar, note

---

## SO SÁNH CHI TIẾT

| Tiêu chí | Option 1: Direct Write | Option 2: Webhook (✅) |
|---------|------------------------|----------------------|
| **Bảo mật** | ⚠️ Bot có quyền Editor | ✅ Bot chỉ gửi request |
| **User control** | ⚠️ Bot có thể xóa data | ✅ User 100% control |
| **Setup complexity** | ✅ Đơn giản (3 bước) | ⚠️ Phức tạp (6 bước) |
| **Reliability** | ✅ Trực tiếp API | ⚠️ Phụ thuộc Apps Script |
| **Performance** | ✅ Nhanh (1 API call) | ⚠️ HTTP overhead |
| **Data validation** | ⚠️ Bot validate only | ✅ Apps Script validate |
| **Audit log** | ⚠️ Bot logs only | ✅ Apps Script logs |
| **User permission** | ⚠️ Editor required | ✅ Viewer sufficient |
| **Risk if leaked** | ⚠️ High (can delete) | ✅ Low (read only) |

---

## KHUYẾN NGHỊ: OPTION 2 (Webhook) 🎯

**Lý do:**

1. **Bảo mật tối ưu:**
   - Bot chỉ có quyền ĐỌC (Viewer)
   - Apps Script chạy dưới quyền USER
   - Nếu bot credentials bị lộ → Hacker chỉ ĐỌC được, KHÔNG xóa

2. **User trust:**
   - User thấy rõ Apps Script code (transparent)
   - User deploy Web App của chính họ
   - User có thể tắt webhook bất cứ lúc nào

3. **Flexibility:**
   - Apps Script có thể validate (VD: max 10 triệu/transaction)
   - Có thể transform data (VD: auto-categorize)
   - Có thể gửi email confirmation

4. **Consistent với kiến trúc hiện tại:**
   - Bot đã ĐỌC data qua READ-ONLY API
   - GHI cũng nên qua một layer riêng (Apps Script)

---

## FLOW NGƯỜI DÙNG

### **Option 2 - Webhook Flow:**

```
┌─────────────────────────────────────────────────┐
│ USER                                            │
├─────────────────────────────────────────────────┤
│ 1. Gõ: /setupwebhook                           │
│    → Bot hiện hướng dẫn chi tiết               │
│                                                 │
│ 2. Mở Google Sheets                            │
│    → Extensions → Apps Script                  │
│    → Copy code từ bot                          │
│    → Deploy as Web App                         │
│                                                 │
│ 3. Copy Webhook URL                            │
│    → Gõ: /setwebhook [URL]                    │
│    → Bot test connection                       │
│    → ✅ Kết nối thành công!                    │
│                                                 │
│ 4. Bắt đầu ghi:                                │
│    → "chi 50k tiền ăn"                         │
│    → Bot parse → POST to webhook               │
│    → Apps Script ghi vào Sheets                │
│    → ✅ Đã ghi!                                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ TECHNICAL FLOW                                  │
├─────────────────────────────────────────────────┤
│                                                 │
│ User: "chi 50k tiền ăn"                        │
│   ↓                                             │
│ Bot: parse_expense_message()                    │
│   → {amount: 50000, category: "Ăn uống"}      │
│   ↓                                             │
│ Bot: send_transaction_to_webhook()              │
│   → POST https://script.google.com/...         │
│   → Payload: {date, category, amount...}       │
│   ↓                                             │
│ Apps Script: doPost(e)                          │
│   → Parse JSON                                  │
│   → sheet.appendRow([...])                     │
│   → Return {success: true}                     │
│   ↓                                             │
│ Bot: Show confirmation                          │
│   → ✅ Đã ghi thành công!                      │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## CODE CHÍNH CẦN TÍCH HỢP

### 1. Database Schema Update ✅ (ĐÃ XỨ LÝ)

```python
# bot/utils/database.py - User model
spreadsheet_id = Column(String(100), nullable=True)
sheets_connected_at = Column(DateTime, nullable=True)
sheets_last_sync = Column(DateTime, nullable=True)
webhook_url = Column(String(500), nullable=True)  # NEW!
```

### 2. Register Handlers

```python
# bot/main.py
from bot.handlers.quick_record_webhook import register_quick_record_webhook_handlers

# After existing handlers:
register_quick_record_webhook_handlers(application)
```

### 3. Google Apps Script Code (User sẽ copy)

```javascript
// User sẽ paste vào Apps Script editor
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('Transactions');
    
    if (!sheet) {
      return ContentService.createTextOutput(
        JSON.stringify({success: false, error: 'Sheet not found'})
      ).setMimeType(ContentService.MimeType.JSON);
    }
    
    // Append row: Date | Category | Amount | Jar | Note | Method
    sheet.appendRow([
      data.date,
      data.category,
      data.amount,
      data.jar,
      data.note,
      data.method
    ]);
    
    return ContentService.createTextOutput(
      JSON.stringify({success: true, message: 'Transaction recorded'})
    ).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(
      JSON.stringify({success: false, error: error.toString()})
    ).setMimeType(ContentService.MimeType.JSON);
  }
}
```

---

## TESTING CHECKLIST

### Option 2 - Webhook Testing:

- [ ] User setup Apps Script theo hướng dẫn
- [ ] User deploy Web App successfully
- [ ] Bot nhận webhook URL từ `/setwebhook`
- [ ] Bot test connection thành công
- [ ] User gõ "chi 50k tiền ăn"
- [ ] Bot parse đúng: 50,000 VNĐ - Ăn uống
- [ ] Webhook POST request thành công (200 OK)
- [ ] Apps Script ghi row vào Transactions sheet
- [ ] Bot hiện confirmation: ✅ Đã ghi!
- [ ] User check Google Sheets → Row mới xuất hiện
- [ ] Analytics track: quick_record_success

### Error Cases Testing:

- [ ] Wrong webhook URL → "URL không hợp lệ"
- [ ] Apps Script chưa deploy → Timeout error
- [ ] Wrong format message → "Không hiểu format"
- [ ] Not Premium tier → "Tính năng Premium"
- [ ] Webhook not configured → Guide to /setupwebhook

---

## DEPENDENCIES

### Python Packages:

```bash
pip install aiohttp  # For HTTP POST requests
```

### Google Apps Script:
- No additional dependencies
- Uses built-in SpreadsheetApp

---

## EXAMPLE CONVERSATIONS

### Setup Conversation:

```
User: /setupwebhook

Bot: 📱 CÀI ĐẶT QUICK RECORD QUA WEBHOOK
     
     Bước 1: Mở Google Sheets...
     [Full guide]

User: [Follows steps, deploys Apps Script]

User: /setwebhook https://script.google.com/macros/s/ABC123.../exec

Bot: 🔄 Đang test webhook...
     ✅ Kết nối thành công!
     
     Thử ngay:
     • "chi 50k tiền ăn"
```

### Usage Conversation:

```
User: chi 50k tiền ăn

Bot: 📝 Xác nhận ghi:
     💸 Số tiền: 50,000 VNĐ
     📂 Danh mục: Ăn uống
     🔄 Đang gửi tới Google Sheets...

Bot: ✅ Đã ghi thành công!
     💸 Chi: 50,000 VNĐ
     📂 Ăn uống
     
     📊 Xem số dư: /balance
```

---

## SECURITY NOTES

### Option 2 Security Model:

1. **Bot Credentials:**
   - Bot chỉ có quyền READ (spreadsheets.readonly)
   - Nếu credentials bị lộ → Chỉ ĐỌC, không GHI/XÓA

2. **User Control:**
   - User deploy Apps Script trên account của họ
   - User có thể DISABLE Web App bất cứ lúc nào
   - User có thể thay đổi code để validate thêm

3. **Data Flow:**
   - Bot → HTTPS POST → Apps Script (encrypted)
   - Apps Script → SpreadsheetApp → Sheets (Google internal)
   - No intermediate storage on bot server

4. **Audit:**
   - Bot logs: Analytics event tracking
   - Apps Script logs: View in GCP Logs Explorer
   - Sheets history: File → Version history

---

## ROLLOUT PLAN

### Phase 1: Testing (3 days)
- Deploy to staging bot
- Internal testing with 2-3 users
- Fix bugs and optimize UX

### Phase 2: Premium Beta (1 week)
- Enable for 10-20 Premium users
- Monitor analytics + error rates
- Collect user feedback

### Phase 3: Full Launch (Week 2)
- Enable for all Premium/Trial users
- Add to /start menu: "🎯 Quick Record"
- Tutorial video/gif

---

## FUTURE ENHANCEMENTS

1. **Voice Input:**
   - User gửi voice message: "Chi năm mươi nghìn tiền ăn"
   - Bot STT (Speech-to-Text) → Parse → Write

2. **Photo Input:**
   - User chụp hóa đơn
   - Bot OCR → Extract amount + category → Write

3. **Smart Categorization:**
   - GPT-4 analyze note → Auto-suggest category
   - "Mua iphone 15" → Category: "Công nghệ" (not "Mua sắm")

4. **Budget Alerts:**
   - If (monthly spending > budget):
     - Apps Script return warning
     - Bot show alert to user

5. **Multi-account:**
   - Support multiple Sheets (personal + business)
   - User switch: `/switch personal` or `/switch business`

---

## RECOMMENDATION: IMPLEMENT OPTION 2 ✅

**Tóm tắt:**
- ✅ Bảo mật tốt nhất (bot chỉ READ)
- ✅ User trust cao hơn (transparent)
- ✅ Flexibility cho sau này
- ✅ Consistent với kiến trúc READ-ONLY

**Next Steps:**
1. Add aiohttp to requirements.txt
2. Register handlers in main.py
3. Test full flow với 1 user
4. Write user documentation
5. Launch to Premium users! 🚀
