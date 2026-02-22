# 🚀 Quick Start: FreedomWallet Bot + Google Sheets Integration

## ✅ Trạng Thái Hiện Tại

**HỆ THỐNG ĐÃ SẴN SÀNG!** Tất cả code đã được implement:
- ✅ Smart parsing (flexible word order)
- ✅ Investment support (Đầu tư type)
- ✅ SP500 bug fix (không parse số từ product code)
- ✅ Apps Script deployed với date formatting dd/MM/yyyy
- ✅ Handler registration trong main.py
- ✅ Database schema với spreadsheet_id

## 📋 Checklist Cho User

### 1. One-Time Setup (mỗi user làm 1 lần)

#### Bước 1: Copy Freedom Wallet Template
```
1. Vào link template: https://docs.google.com/spreadsheets/d/YOUR_TEMPLATE_ID/copy
2. Click "Make a copy"
3. Đặt tên: "Freedom Wallet - [Tên bạn]"
4. Copy Spreadsheet ID (44 ký tự từ URL)
   Example URL: https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/edit
   ID: 1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg
```

#### Bước 2: Share với Service Account
```
1. Click "Share" button
2. Thêm email: [Service Account Email]
3. Permission: EDITOR
4. Click "Send"
```

#### Bước 3: Connect Bot với Sheet
```
User gõ trong Telegram:
  /connectsheets

Bot: "Nhập link Google Sheets của bạn"

User paste:
  https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/edit

Bot: ✅ Đã kết nối! Spreadsheet ID: 1dV-KAVxxtbrmp79...
```

### 2. Test Giao Dịch

#### Test 1: Chi tiêu đơn giản
```
User: chi 50k ăn sáng

Bot: 📝 Phân loại tự động
     • Chi: 50,000 ₫
     • Danh mục: 🍽️ Ăn uống
     • Hũ: NEC - 🏠 Nhu cầu thiết yếu
     • Tài khoản: Cash
     • Ghi chú: ăn sáng
     
     Đúng không? [Xác nhận] [Chỉnh sửa]
     
User click: [Xác nhận]

Bot: ✅ Đã ghi thành công!
```

#### Test 2: Mua sắm với số lẻ
```
User: mua sắm 1,5 triệu

Bot: 📝 Phân loại tự động
     • Chi: 1,500,000 ₫
     • Danh mục: 🛍️ Mua sắm
     • Hũ: PLAY - 🎉 Giải trí & Tận hưởng
     [Confirm flow...]

✅ Expected: Parse đúng 1.5 triệu (không phải 5 triệu)
```

#### Test 3: Đầu tư SP500 (CRITICAL TEST)
```
User: đầu tư SP500 27tr

Bot: 📝 Phân loại tự động
     • Đầu tư: 27,000,000 ₫
     • Danh mục: 📈 Chứng khoán
     • Hũ: FFA - 📈 Đầu tư & Tự do tài chính
     • Ghi chú: đầu tư SP500
     [Confirm flow...]

✅ Expected: Parse đúng 27tr (KHÔNG PHẢI 500₫ từ "SP500")
```

#### Test 4: Thu nhập
```
User: lương 15 triệu

Bot: 📝 Phân loại tự động
     • Thu: 15,000,000 ₫
     • Danh mục: 💰 Lương
     • Hũ: (auto-allocate theo % các hũ)
     [Confirm flow...]
```

#### Test 5: Flexible word order
```
User: 150k xem phim
User: xem phim 150k
User: chi xem phim 150k

✅ TẤT CẢ phải parse thành: Chi, 150000₫, "xem phim"
```

### 3. Verify Trong Google Sheets

#### Mở sheet "Giao dịch" và kiểm tra:
```
Row format:
┌────────────┬────────────┬──────┬─────┬──────────┬──────────┬────────┬──────┬──────────┐
│     A      │     B      │  C   │  D  │    E     │    F     │   G    │  H   │    I     │
├────────────┼────────────┼──────┼─────┼──────────┼──────────┼────────┼──────┼──────────┤
│ ID         │ Ngày       │ Loại │ Jar │ Danh mục │ Số tiền  │ Tài kh │ Đích │ Ghi chú  │
│ (datetime) │ (dd/MM/yy) │      │     │          │          │        │      │          │
├────────────┼────────────┼──────┼─────┼──────────┼──────────┼────────┼──────┼──────────┤
│ 20260209_  │ 09/02/2026 │ Chi  │ NEC │ Ăn uống  │ 50,000   │ Cash   │      │ ăn sáng  │
│ 143052     │            │      │     │          │          │        │      │          │
├────────────┼────────────┼──────┼─────┼──────────┼──────────┼────────┼──────┼──────────┤
│ 20260209_  │ 09/02/2026 │ Đầu  │ FFA │ Chứng    │27,000,000│ VCB    │      │ đầu tư   │
│ 143128     │            │ tư   │     │ khoán    │          │        │      │ SP500    │
└────────────┴────────────┴──────┴─────┴──────────┴──────────┴────────┴──────┴──────────┘

✅ Check items:
   - ID format: yyyyMMdd_HHmmss ✅
   - Date format: dd/MM/yyyy (09/02/2026) ✅
   - Type: Chi/Thu/Đầu tư ✅
   - Category matched correctly ✅
   - Amount correct (không phải 500₫) ✅
```

---

## 🧪 Run Test Script

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run comprehensive test
python test_telegram_to_sheets_flow.py
```

**Expected output:**
```
🧪 TEST LUỒNG DỮ LIỆU: Telegram Bot → Apps Script → Sheets
======================================================================

📝 STEP 1: Smart Parsing
  Input:  'chi 50k ăn sáng'
  Output: Type=Chi, Amount=50,000₫, Note='ăn sáng'
  
  Input:  'đầu tư SP500 27tr'
  Output: Type=Đầu tư, Amount=27,000,000₫, Note='đầu tư SP500'
  
🔌 STEP 2: API Connection Test
  ✅ PING: Pong from Bot API!
  
📂 STEP 3: Get Categories
  ✅ Categories loaded: 53 total
  📈 Investment categories: 12
  
💸 STEP 4: Add Transaction - Chi (Expense)
  ✅ SUCCESS
  
📈 STEP 5: Add Transaction - Đầu tư (Investment)
  ✅ SUCCESS
  
💰 STEP 6: Get Balance
  ✅ Total Balance: 10,000,000 ₫
  
🎉 TẤT CẢ TESTS PASSED! Hệ thống sẵn sàng hoạt động.
```

---

## 🔍 Troubleshooting

### Issue 1: "Không tìm thấy spreadsheet ID"
**Cause:** User chưa /connectsheets
**Fix:** 
```
User: /connectsheets
Bot: Nhập link...
User: [paste link]
```

### Issue 2: "Permission denied"
**Cause:** Sheet chưa share với service account
**Fix:** 
```
1. Open Google Sheet
2. Click "Share"
3. Add service account email
4. Permission: EDITOR
```

### Issue 3: Bot không respond
**Cause:** Handler chưa register hoặc bot chưa start
**Fix:**
```powershell
# Check bot is running
python main.py

# Check handler registration in main.py (line 147)
from bot.handlers.quick_record_template import register_quick_record_handlers
register_quick_record_handlers(application)
```

### Issue 4: Parse sai số tiền
**Cause:** Regex không match format
**Fix:** Check test_smart_parsing.py để verify patterns

### Issue 5: Ghi vào sheet sai định dạng ngày
**Cause:** Apps Script chưa deploy version mới
**Fix:**
```
1. Open bot-api-handler-vietnamese.gs
2. Deploy → New deployment
3. Copy URL mới
4. Update bot/services/sheets_api_client.py line 13
```

---

## 📚 Documentation Files

1. **LUONG_DU_LIEU_TELEGRAM_TO_SHEETS.md** - Complete architecture diagram
2. **test_telegram_to_sheets_flow.py** - Integration test script
3. **bot/handlers/quick_record_template.py** - Handler implementation
4. **bot/services/sheets_api_client.py** - API client
5. **bot-api-handler-vietnamese.gs** - Apps Script backend

---

## 🎯 Success Criteria

- ✅ User gõ "chi 50k ăn sáng" → Ghi vào sheet trong <2s
- ✅ Date format: dd/MM/yyyy (09/02/2026)
- ✅ Transaction ID: yyyyMMdd_HHmmss (20260209_143052)
- ✅ Smart category matching hoạt động
- ✅ Investment transactions (Đầu tư) hoạt động
- ✅ SP500 bug fix hoạt động (parse 27tr không phải 500)
- ✅ Flexible word order hoạt động
- ✅ All formulas trong sheet vẫn hoạt động

---

## 🚨 Known Limitations

1. **Spreadsheet ID required:** User PHẢI /connectsheets trước khi dùng quick record
2. **Permission required:** Service account PHẢI có EDITOR access
3. **Network latency:** API call có thể mất 1-2 giây
4. **Apps Script quota:** 
   - Free tier: 20,000 URL Fetch calls/day
   - Mỗi transaction = 2 calls (getCategories + addTransaction)
   - Max ~10,000 transactions/day

---

## 📞 Support

Nếu có vấn đề:
1. Check logs: `data/logs/bot.log`
2. Run test script: `python test_telegram_to_sheets_flow.py`
3. Verify Apps Script deployment URL trong `sheets_api_client.py`
4. Check database: `user.spreadsheet_id` có giá trị chưa

---

## 🎉 Ready to Go!

Hệ thống sẵn sàng 100%. Chỉ cần user:
1. Connect spreadsheet (one-time)
2. Test với vài giao dịch
3. Verify trong Google Sheets

**Happy tracking! 💰📊**
