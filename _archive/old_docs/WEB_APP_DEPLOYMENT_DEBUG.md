# 🔧 Web App Deployment Debug Guide

## Vấn đề: Bot hiển thị "✅ Đã ghi thành công!" nhưng sheet không có giao dịch

---

## ✅ CHECKLIST 1: Deployment Settings

### Bước 1.1: Mở Apps Script Editor
1. Mở spreadsheet: https://docs.google.com/spreadsheets/d/1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI/edit
2. Click **Extensions** → **Apps Script**

### Bước 1.2: Verify Files Exist
Các file này PHẢI có:
- [x] Code.gs (chứa doPost function)
- [x] backend/entities/Transactions.gs
- [x] backend/utils/DateHelper.gs
- [x] backend/DataManager.gs
- [x] backend/CacheManager.gs

### Bước 1.3: Deploy Web App
1. Trong Apps Script Editor, click **Deploy** → **Manage deployments**
2. Nếu chưa có deployment:
   - Click **New deployment**
   - Type: **Web app**
3. Nếu đã có deployment:
   - Click **Edit** (⚙️ icon)

### Bước 1.4: Configure Deployment (QUAN TRỌNG!)

```
Description: FreedomWallet Bot API
Execute as: Me (your-email@gmail.com)
Who has access: Anyone ← PHẢI LÀ "Anyone"
```

**⚠️ LƯU Ý:**
- **KHÔNG chọn** "Anyone with a Google account"
- **PHẢI chọn** "Anyone" (no Google account required)
- Nếu không, Bot sẽ không gọi được Web App

### Bước 1.5: Deploy & Copy URL
1. Click **Deploy**
2. Authorize nếu được yêu cầu:
   - Click **Authorize access**
   - Chọn Google account
   - Click **Advanced** → **Go to FreedomWallet (unsafe)**
   - Click **Allow**
3. Copy **Web App URL** (dạng: `https://script.google.com/macros/s/AKfycby.../exec`)
4. Lưu URL này vào Bot: `/setwebapp <URL>`

---

## ✅ CHECKLIST 2: Sheet Structure

### Bước 2.1: Kiểm tra Sheet Name
Code.gs tìm sheet có tên **CHÍNH XÁC** là: `Giao dịch`

```javascript
// Trong Transactions.gs
SHEET_NAME: 'Giao dịch',
```

**Cách kiểm tra:**
1. Mở spreadsheet
2. Xem các tab ở dưới cùng
3. Đảm bảo có tab tên: **Giao dịch** (không dấu ngoặc, không space thừa)

**Nếu không đúng tên:**
- Đổi tên sheet về "Giao dịch"
- HOẶC sửa Code.gs line 9 trong Transactions.gs:
  ```javascript
  SHEET_NAME: 'Tên sheet của bạn',
  ```

### Bước 2.2: Kiểm tra Header Row
Sheet "Giao dịch" phải có header row (dòng 1) với các cột:

| A | B | C | D | E | F | G | H | I | J | K | L | M |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ID | Ngày | Loại | Jar ID | Danh mục | Số tiền | Tài khoản nguồn | Tài khoản đích | Ghi chú | Investment ID | Số lượng | Đơn giá | Phí GD |

**Cách kiểm tra:**
1. Mở sheet "Giao dịch"
2. Dòng 1 phải có các header này
3. Nếu thiếu → Thêm header row

---

## ✅ CHECKLIST 3: Test Web App Directly

### Bước 3.1: Test Ping
Mở Terminal/PowerShell:

```powershell
cd D:\Projects\FreedomWalletBot
python test_webapp_direct.py
```

**Kết quả mong đợi:**
```
✅ TEST 1: PING TEST
✅ Status Code: 200
✅ JSON Response: {
  "success": true,
  "message": "Pong from Freedom Wallet!",
  ...
}
```

**Nếu lỗi:**
- Status 403 → Web App chưa deploy với "Anyone" access
- Status 404 → URL sai hoặc deployment bị xóa
- Connection timeout → Firewall/network issue

### Bước 3.2: Test Add Transaction
Nếu ping OK, script sẽ tự động test thêm giao dịch.

**Kết quả mong đợi:**
```
✅ TEST 2: ADD TRANSACTION
✅ Status Code: 200
✅ JSON Response: {
  "success": true,
  "transactionId": "TX_TEST_1770638000",
  ...
}
🎉 SUCCESS! Transaction ID: TX_TEST_1770638000
📊 Check spreadsheet: ...
```

**Sau test, kiểm tra spreadsheet:**
1. Mở: https://docs.google.com/spreadsheets/d/1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI/edit
2. Vào tab "Giao dịch"
3. Tìm transaction với note: "TEST từ Code.gs deployment check"

---

## ✅ CHECKLIST 4: Debug Logs

### Bước 4.1: Check Apps Script Logs
1. Trong Apps Script Editor
2. Click **View** → **Executions**
3. Xem các executions gần đây:
   - ✅ Status "Completed" → Web App chạy OK
   - ❌ Status "Failed" → Click vào xem error details

### Bước 4.2: Common Errors

**Error: "Exception: Cannot find sheet 'Giao dịch'"**
- **Nguyên nhân:** Sheet name không đúng
- **Giải pháp:** Đổi tên sheet về "Giao dịch" hoặc sửa SHEET_NAME trong code

**Error: "ReferenceError: TransactionsModule is not defined"**
- **Nguyên nhân:** Files chưa được deploy đúng thứ tự
- **Giải pháp:**
  1. Trong Apps Script Editor
  2. Đảm bảo các file được load theo thứ tự (Apps Script tự động load theo alphabet)
  3. Re-deploy Web App

**Error: "Exception: You do not have permission to call SpreadsheetApp.getActiveSpreadsheet"**
- **Nguyên nhân:** Deploy setting sai
- **Giải pháp:**
  1. Deploy → Manage deployments
  2. Edit deployment
  3. **Execute as:** Me (your email) ← Phải chọn "Me", không phải "User accessing the web app"

---

## ✅ CHECKLIST 5: Bot Configuration

### Bước 5.1: Verify Web App URL in Bot
```
/mywebapp
```

**Kết quả mong đợi:**
```
📱 Web App của bạn:
https://script.google.com/macros/s/AKfycbw.../exec
```

**Nếu URL khác hoặc không có:**
```
/setwebapp https://script.google.com/macros/s/AKfycbwloP0ItK9dnDRl8AW2V-1r9eZe1LRC-Y3yNx-7BNAd2r9uoKBmWLWq2bBQjLYZtY0pGQ/exec
```

### Bước 5.2: Test Transaction via Bot
```
chi 50k test deployment
```

**Kết quả mong đợi:**
```
✅ Đã ghi thành công!
• Chi: 50,000 ₫
• Danh mục: 🍽️ Ăn uống
• ID: TX_1770638123
```

**Sau đó kiểm tra spreadsheet:**
- Vào tab "Giao dịch"
- Tìm transaction ID: TX_1770638123

---

## 🔍 COMMON ISSUES & SOLUTIONS

### Issue 1: "Success" message but no data in sheet

**Possible Causes:**
1. ❌ Sheet name mismatch
2. ❌ Web App URL outdated (old deployment)
3. ❌ Bot saved wrong URL
4. ❌ Apps Script có lỗi runtime

**Solutions:**
1. Verify sheet name = "Giao dịch"
2. Re-deploy Web App → Get NEW URL → Update bot với `/setwebapp <NEW_URL>`
3. Run `python test_webapp_direct.py` để test trực tiếp
4. Check Apps Script Executions log

### Issue 2: Connection timeout

**Possible Causes:**
1. ❌ Apps Script đang chạy quá lâu
2. ❌ Network/firewall blocking
3. ❌ Spreadsheet quá lớn (>10MB)

**Solutions:**
1. Optimize Apps Script code (reduce SpreadsheetApp calls)
2. Check firewall settings
3. Archive old data to separate spreadsheet

### Issue 3: "Unauthorized" error

**Possible Causes:**
1. ❌ API key không đúng
2. ❌ Web App "Execute as" setting sai

**Solutions:**
1. Bot sử dụng API key: `fwb_bot_production_2026` (hardcoded trong Code.gs)
2. Verify trong Code.gs lines 43-52:
   ```javascript
   const VALID_API_KEYS = {
     'fwb_bot_production_2026': {
       name: 'FreedomWalletBot Production',
       ...
     }
   }
   ```

---

## 📊 FINAL VERIFICATION

Sau khi hoàn thành tất cả checklist:

1. ✅ Web App deployed với "Anyone" access
2. ✅ Sheet "Giao dịch" tồn tại với đúng structure
3. ✅ `python test_webapp_direct.py` passes ALL tests
4. ✅ Apps Script Executions log không có errors
5. ✅ Bot có đúng Web App URL (`/mywebapp`)
6. ✅ Test transaction qua bot → Data xuất hiện trong sheet

**Nếu tất cả đều ✅ nhưng vẫn không work:**
- Share spreadsheet ID & Web App URL
- Share screenshot Apps Script Executions log
- Share bot logs khi gọi `chi 50k test`

---

## 🆘 NEED HELP?

Nếu vẫn không work, cung cấp:

1. **Apps Script Execution Log:**
   - Apps Script Editor → View → Executions
   - Screenshot execution gần nhất (cả thành công và thất bại)

2. **Bot Log:**
   ```powershell
   Get-Content D:\Projects\FreedomWalletBot\data\logs\bot.log -Tail 50 | 
     Select-String "quick_record|addTransaction|webapp"
   ```

3. **Test Script Result:**
   ```powershell
   cd D:\Projects\FreedomWalletBot
   python test_webapp_direct.py > test_result.txt 2>&1
   cat test_result.txt
   ```

4. **Verify Deployment:**
   - Screenshot Deploy → Manage deployments settings
   - Confirm "Who has access" = "Anyone"
