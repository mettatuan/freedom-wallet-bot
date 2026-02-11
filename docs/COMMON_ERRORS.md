# 🚨 Lỗi Thường Gặp & Cách Sửa

## 1️⃣ "/setwebapp đơ" (không có phản hồi)

**Hiện tượng:**
```
User: /setwebapp AKfycbwloP0ItK9dnDRl8AW2V-1r9eZe1LRC-Y3yNx-7BNAd2r9uoKBmWLWq2bBQjLYZtY0pGQ
Bot: (không phản hồi gì)
```

**Nguyên nhân:** Thiếu URL đầy đủ (phải có `https://script.google.com/macros/s/`)

**Cách sửa:**
```
✅ ĐÚNG: /setwebapp https://script.google.com/macros/s/AKfycbwloP0ItK9dnDRl8AW2V-1r9eZe1LRC-Y3yNx-7BNAd2r9uoKBmWLWq2bBQjLYZtY0pGQ/exec
❌ SAI: /setwebapp AKfycbwloP0ItK9...
```

**Lấy URL đúng:**
1. Mở spreadsheet
2. Extensions → Apps Script
3. Click **Deploy → Manage deployments**
4. Copy **TOÀN BỘ URL** (từ `https://` đến `/exec`)
5. Gửi lại: `/setwebapp [URL_ĐẦY_ĐỦ]`

---

## 2️⃣ "Không thể kết nối!" (403 Permission Denied)

**Hiện tượng:**
```
User: /setsheet 1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI
Bot: ❌ Không thể kết nối!
     Nguyên nhân phổ biến:
     ❌ Bạn CHƯA SHARE spreadsheet với bot
```

**Nguyên nhân:** Spreadsheet chưa được share với service account email

**Cách sửa:**

**Bước 1: Lấy service account email**
```
/getsaemail
```

Bot trả về:
```
📧 Service Account Email:
eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com
```

**Bước 2: Share spreadsheet**
1. Mở spreadsheet: `https://docs.google.com/spreadsheets/d/1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI/edit`
2. Click **Share** (góc trên bên phải)
3. Paste email: `eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com`
4. Quyền: **Viewer** (chỉ đọc)
5. **Bỏ tick** "Notify people"
6. Click **Share**

**Bước 3: Thử lại**
```
/setsheet 1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI
```

---

## 3️⃣ "Bạn đang dùng Template ID!"

**Hiện tượng:**
```
User: /setsheet 1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg
Bot: ⚠️ Bạn đang dùng Template ID!
     Lỗi: Bạn KHÔNG THỂ dùng trực tiếp template này.
```

**Nguyên nhân:** Bạn gửi Template ID gốc (thuộc về project, không phải của bạn)

**Cách sửa:**

**Bước 1: Copy template về Drive của bạn**
Click link: https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/copy

**Bước 2: Lấy ID MỚI**
Sau khi copy, URL sẽ có dạng:
```
https://docs.google.com/spreadsheets/d/1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P7q8R9s0T1u2V3w4X/edit
                                     ↑━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━↑
                                              Copy phần này
```

**Bước 3: Gửi ID MỚI**
```
/setsheet 1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P7q8R9s0T1u2V3w4X
```

---

## 4️⃣ "Web App URL không hợp lệ!"

**Hiện tượng:**
```
User: /setwebapp script.google.com/macros/s/.../exec
Bot: ❌ URL không hợp lệ!
     Web App URL phải có dạng:
     https://script.google.com/macros/s/AKfycby.../exec
```

**Nguyên nhân:** Thiếu `https://` ở đầu URL

**Cách sửa:**
```
✅ ĐÚNG: https://script.google.com/macros/s/.../exec
❌ SAI: script.google.com/macros/s/.../exec
❌ SAI: AKfycby...
```

---

## 5️⃣ "DateHelper.generateId is not a function"

**Hiện tượng:**
```
User: chi 50k test
Bot: ❌ Lỗi: DateHelper.generateId is not a function
```

**Nguyên nhân:** Bạn copy template CŨ (trước khi fix bug)

**Cách sửa:**

**Option A: Copy template MỚI (Đơn giản)**
1. Click: https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/copy
2. Redeploy Web App (Extensions → Apps Script → Deploy)
3. `/setwebapp [URL_MỚI]`

**Option B: Update Apps Script (Nâng cao)**
1. Mở spreadsheet cũ → Extensions → Apps Script
2. Tìm file `DateHelper.gs`
3. Thêm method:
```javascript
generateId(prefix = '') {
  const timestamp = new Date().getTime().toString();
  return prefix ? `${prefix}_${timestamp}` : timestamp;
}
```
4. Ctrl+S lưu
5. Redeploy Web App

---

## 🔥 Flowchart Chọn Giải Pháp

```
Bạn muốn ghi giao dịch qua bot?
│
├─ YES → Dùng Quick Record
│         1. Copy template
│         2. Deploy Web App
│         3. /setwebapp [URL]
│         4. chi 50k test
│         → XONG! ✅
│
└─ NO → Chỉ cần Dashboard & AI?
          1. Copy template
          2. /getsaemail
          3. Share với service account email
          4. /setsheet [ID]
          → XONG! ✅
```

---

## 📞 Hỗ Trợ Trực Tiếp

**Nếu vẫn lỗi sau khi làm theo hướng dẫn:**

Gửi tin nhắn cho admin với format:
```
🚨 BÁO LỖI

1️⃣ Bạn muốn dùng tính năng gì?
   [ ] Quick Record (ghi giao dịch)
   [ ] Premium AI (phân tích)

2️⃣ Bạn đã làm bước nào?
   [ ] Copy template
   [ ] Deploy Web App / Share với SA
   [ ] Gửi lệnh /setwebapp hoặc /setsheet

3️⃣ Lệnh bạn đã gửi:
   /setwebapp ... hoặc /setsheet ...

4️⃣ Lỗi hiển thị:
   (Copy toàn bộ tin nhắn lỗi)

5️⃣ Screenshot (nếu có):
   [Đính kèm ảnh]
```

---

**Last updated:** 2026-02-09 19:50
