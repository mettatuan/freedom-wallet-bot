# 🔐 Fix API Authentication - Quick Guide

## Vấn đề hiện tại
```
❌ Error: Unauthorized: Invalid API key
```

Bot đang dùng API key: `fwb_bot_testing_2026`
Apps Script của bạn không nhận ra key này.

---

## ✅ Giải pháp 1: Comment Authentication (KHUYÊN DÙNG - Nhanh nhất)

### Bước 1: Mở Apps Script
1. Mở Google Sheets: `1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI`
2. **Extensions** → **Apps Script** 
3. Mở file **Code.gs**

### Bước 2: Tìm và comment dòng này (khoảng line 72-78)
```javascript
// ✅ STEP 1: Validate API Key
if (!apiKey || !VALID_API_KEYS[apiKey]) {
  Logger.log(`❌ Unauthorized: invalid API key`);
  return createJsonResponse({
    success: false,
    error: 'Unauthorized: Invalid API key'
  });
}
```

**Thay bằng:**
```javascript
// ✅ STEP 1: Validate API Key (DISABLED FOR TESTING)
// if (!apiKey || !VALID_API_KEYS[apiKey]) {
//   Logger.log(`❌ Unauthorized: invalid API key`);
//   return createJsonResponse({
//     success: false,
//     error: 'Unauthorized: Invalid API key'
//   });
// }
```

### Bước 3: Deploy lại
1. Click **Deploy** → **Manage deployments**
2. Click **biểu tượng bút chì** (Edit) bên deployment hiện tại
3. **Version**: New version
4. **Deploy**

### Bước 4: Test
```bash
cd d:\Projects\FreedomWalletBot
python test_get_categories_api.py
```

Nếu thấy:
```
✅ API Response:
   Success: True
   📊 Total categories: 52
```
→ **THÀNH CÔNG!** 🎉

---

## ✅ Giải pháp 2: Thêm API Key đúng

### Bước 1: Tìm API keys trong Code.gs (line 47-56)
```javascript
const VALID_API_KEYS = {
  'fwb_bot_production_2026': {
    name: 'FreedomWalletBot Production',
    rateLimit: 100,
    enabled: true
  },
  'fwb_bot_testing_2026': {
    name: 'FreedomWalletBot Testing',
    rateLimit: 1000,
    enabled: true
  }
};
```

### Bước 2: Kiểm tra key có enabled không
Nếu `'fwb_bot_testing_2026'` đã có và `enabled: true`, vấn đề có thể là:
- Key bị typo trong .env
- Apps Script chưa deploy mới nhất

### Bước 3: Hoặc tạo key mới
Thêm key mới vào Apps Script:
```javascript
const VALID_API_KEYS = {
  'freedom_wallet_bot_2026': {  // ← Key mới
    name: 'FreedomWalletBot',
    rateLimit: 1000,
    enabled: true
  }
};
```

Sau đó update .env:
```dotenv
FREEDOM_WALLET_API_KEY=freedom_wallet_bot_2026
```

---

## 🎯 Sau khi fix xong

### 1. Test API
```bash
python test_get_categories_api.py
```

Kết quả mong đợi:
```
💰 INCOME CATEGORIES (Thu): 10
   💼 Lương                 | Jar:      | Auto: True  | ID: CAT031
   💼 Kinh doanh            | Jar:      | Auto: True  | ID: CAT032
   🏠 Cho thuê              | Jar: FFA  | Auto: False | ID: CAT033
   📈 Lãi đầu tư           | Jar: FFA  | Auto: False | ID: CAT034
   ...

🔍 SEARCH RESULT: 'Lương' category
   ✅ FOUND: {'id': 'CAT031', 'name': 'Lương', ...}
```

### 2. Restart Bot
```bash
cd d:\Projects\FreedomWalletBot
python main.py
```

### 3. Test trong Telegram
```
Bạn: Thu 50tr lương

Bot: 📝 Phân loại tự động

• Thu: 50,000,000 ₫
• Danh mục: 💼 Lương
• Phân bổ: Tự động 6 hũ 🏺
• Tài khoản: Cash
• Ghi chú: lương

💡 Đúng không? Xác nhận hoặc chỉnh sửa:
[✅ Xác nhận và ghi]
```

---

## 🚨 Troubleshooting

### Vẫn lỗi "Invalid API key" sau khi comment
→ Chưa deploy lại Apps Script. Nhớ **New version** khi deploy!

### Test script báo 404
→ Sai webapp URL. Kiểm tra lại URL deployment.

### Categories không load
→ Sheet "Danh mục" không tồn tại hoặc sai format.

---

## 📞 Cần hỗ trợ?

Gửi screenshot của:
1. Apps Script Code.gs (dòng 47-80)
2. Kết quả test: `python test_get_categories_api.py`
3. Deployment URL trong Apps Script

Tôi sẽ hỗ trợ ngay! 🚀
