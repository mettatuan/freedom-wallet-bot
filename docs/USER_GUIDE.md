# 📖 HƯỚNG DẪN SỬ DỤNG FREEDOM WALLET BOT

## 🚀 Quick Start (3 Phút)

**Option 1: Dùng Quick Record (Khuyến nghị)** ← KHÔNG CẦN SERVICE ACCOUNT!

1. **Copy template về Drive:**
   - https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/copy

2. **Deploy Web App:**
   - Mở spreadsheet → **Extensions → Apps Script**
   - Click **Deploy → New deployment**
   - Type: **Web app**
   - Who has access: **Anyone**
   - Copy URL (dạng: `https://script.google.com/macros/s/.../exec`)

3. **Kết nối với bot:**
   ```
   /setwebapp https://script.google.com/macros/s/.../exec
   ```

4. **Thử ngay:**
   ```
   chi 50k cà phê
   thu 5tr lương
   ```

**✅ XONG! Không cần làm gì thêm.**

---

## 🎯 Bot có 2 chế độ kết nối Google Sheets:

### ✅ Chế độ 1: QUICK RECORD (Ghi nhanh giao dịch)
**Đây là chế độ BẠN NÊN DÙNG!**

**Commands:**
- `/setwebapp [URL]` - Lưu Web App URL
- `/mywebapp` - Xem URL hiện tại
- `/taoweb` - Hướng dẫn chi tiết

**Cách dùng:**
```
chi 50k cà phê
thu 5tr lương
đầu tư 1tr Bitcoin
chuyển 2tr ví Momo sang ví VCB
```

Bot sẽ tự động:
- Phân loại danh mục
- Chọn hũ tiền phù hợp
- Ghi vào Google Sheets qua Apps Script API

**⚠️ LƯU Ý:** Bạn PHẢI dùng Web App URL đầy đủ:
```
✅ ĐÚNG: https://script.google.com/macros/s/AKfycby.../exec
❌ SAI: AKfycby... (thiếu https://)
```

---

### 🔒 Chế độ 2: PREMIUM AI ANALYSIS (Đọc trực tiếp Sheets)
**Tính năng nâng cao, cần service account**

**Commands:**
- `/getsaemail` - Xem service account email để share
- `/setsheet [ID]` - Kết nối spreadsheet (sau khi đã share)

**Cách setup:**

**Bước 1: Lấy service account email**
```
/getsaemail
```

Bot sẽ trả về:
```
📧 Service Account Email:

eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com

🔑 Project: eliroxbot-calendar
```

**Bước 2: Share spreadsheet**
1. Copy template về Drive (nếu chưa)
2. Mở spreadsheet → Click **Share**
3. Paste email: `eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com`
4. Quyền: **Viewer** (chỉ đọc)
5. **Bỏ tick** "Notify people"
6. Click **Share**

**Bước 3: Kết nối với bot**
Lấy Spreadsheet ID từ URL:
```
https://docs.google.com/spreadsheets/d/[COPY_PHẦN_NÀY]/edit
```

Gửi bot:
```
/setsheet [ID_CỦA_BẠN]
```

**Tính năng:**
- AI phân tích chi tiêu tự động
- Dashboard thông minh
- Gợi ý tối ưu tài chính
- Chat với bot về số liệu của bạn

---

## ❓ Xử Lý Lỗi

### Lỗi 1: "Bạn đang dùng Template ID!"
```
⚠️ Bạn đang dùng Template ID!
```

**Nguyên nhân:** Bạn gửi `/setsheet 1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg` (Template ID gốc)

**Giải pháp:** 
1. Copy template về Drive: https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/copy
2. Lấy ID MỚI (của bản copy)
3. Gửi ID MỚI cho bot

---

### Lỗi 2: "Không thể kết nối!" (403 Permission Denied)
```
❌ Không thể kết nối!
Nguyên nhân phổ biến:
❌ Bạn CHƯA SHARE spreadsheet với bot
```

**Giải pháp:**
1. Gõ `/getsaemail` để lấy service account email
2. Share spreadsheet với email đó (quyền Viewer)
3. Thử lại: `/setsheet [ID]`

---

### Lỗi 3: "/setwebapp đơ" (không có hành động nào)
```
/setwebapp AKfycby...
(Không phản hồi)
```

**Nguyên nhân:** Thiếu URL đầy đủ (phải có `https://`)

**Giải pháp:** Gửi URL FULL:
```
/setwebapp https://script.google.com/macros/s/AKfycby.../exec
```

---

### Lỗi 4: "Web App URL không hợp lệ"
```
❌ URL không hợp lệ!
Web App URL phải có dạng:
https://script.google.com/macros/s/AKfycby.../exec
```

**Giải pháp:**
1. Mở Apps Script: Extensions → Apps Script
2. Click **Deploy → Manage deployments**
3. Copy URL (phải BẮT ĐẦU bằng `https://script.google.com/macros/s/`)
4. Gửi lại: `/setwebapp [URL_ĐẦY_ĐỦ]`

---

### Lỗi 5: "DateHelper.generateId is not a function"
```
❌ Lỗi: DateHelper.generateId is not a function
```

**Nguyên nhân:** Bạn copy template CŨ (trước khi fix bug)

**Giải pháp:** Copy template MỚI:
https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/copy

---

## 📞 Commands Chính

| Command | Mô tả |
|---------|-------|
| `/start` | Bắt đầu |
| `/setwebapp [URL]` | Lưu Web App URL (Quick Record) |
| `/mywebapp` | Xem URL hiện tại |
| `/taoweb` | Hướng dẫn deploy Web App |
| `/getsaemail` | Xem service account email |
| `/setsheet [ID]` | Kết nối spreadsheet (Premium AI) |
| `/help` | Trợ giúp |

---

## 📋 Checklist Kiểm Tra

**Nếu bạn muốn dùng Quick Record:**
- [ ] Copy template về Drive
- [ ] Deploy Web App (Extensions → Apps Script)
- [ ] Copy Web App URL (bắt đầu bằng `https://script.google.com`)
- [ ] `/setwebapp [URL_ĐẦY_ĐỦ]`
- [ ] Test: `chi 50k test`

**Nếu bạn muốn dùng Premium AI:**
- [ ] Copy template về Drive (KHÔNG dùng template ID gốc)
- [ ] `/getsaemail` - Lấy service account email
- [ ] Share spreadsheet với email đó (quyền Viewer)
- [ ] Lấy Spreadsheet ID (từ URL bản copy)
- [ ] `/setsheet [ID_CỦA_BẠN]`

---

## 🔑 Service Account Info

**Email để share spreadsheet (Premium AI):**
```
eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com
```

**Quyền cần share:** Viewer (chỉ đọc)

**Lấy email:** `/getsaemail`

---

## 💡 Tips

1. **Quick Record = đơn giản nhất** (không cần share với ai)
2. **Premium AI = nâng cao** (cần share với service account)
3. Luôn dùng **bản copy của bạn**, KHÔNG dùng template ID gốc
4. Web App URL phải là **URL đầy đủ** (có `https://`)
5. Khi share, nhớ **bỏ tick "Notify people"**

---

**Last updated:** 2026-02-09 19:50
