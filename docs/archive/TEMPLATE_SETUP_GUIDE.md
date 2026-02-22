# 📋 Hướng Dẫn Copy Template và Kết Nối Bot

## ⚠️ Lỗi Phổ Biến: Dùng Template ID Trực Tiếp

**KHÔNG BAO GIỜ** dùng Template ID gốc:
```
❌ SAI: 1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg
```

**Lý do:**
- Template thuộc về project, không phải của bạn
- Bạn không có quyền share với service account
- Nhiều người cùng dùng sẽ ghi đè nhau

---

## ✅ Cách Làm Đúng

### Bước 1: Copy Template

**Option A: Copy bằng link (Nhanh nhất)**
1. Click link: https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/copy
2. Đặt tên: "Freedom Wallet - [Tên bạn]"
3. Click **"Make a copy"**

**Option B: Copy thủ công**
1. Mở template: https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg
2. File → Make a copy
3. Đặt tên "Freedom Wallet - [Tên bạn]"
4. Click OK

### Bước 2: Lấy ID Mới

Sau khi copy, bạn sẽ thấy URL mới:
```
https://docs.google.com/spreadsheets/d/[ID_MỚI_CỦA_BẠN]/edit
```

**Ví dụ:**
```
https://docs.google.com/spreadsheets/d/1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P7q8R9s0T1u2V3w4X/edit
                                     ↑━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━↑
                                              Copy phần này (ID mới)
```

---

## 🔗 Hai Cách Kết Nối

### Option 1: Quick Record (Khuyến nghị cho người mới)

**Ưu điểm:**
- ✅ Đơn giản, không cần service account
- ✅ Ghi nhanh (chi/thu/chuyển)
- ✅ Tự động sync

**Bước làm:**
1. Copy template (như trên)
2. Mở Apps Script: **Extensions → Apps Script**
3. Click **Deploy → New deployment**
4. Chọn **Web app**
5. Who has access: **Anyone**
6. Click **Deploy**
7. Copy URL (dạng: `https://script.google.com/macros/s/.../exec`)
8. Gửi bot: `/setwebapp [URL]`
9. Test: Gõ `chi 50k test`

**Không cần share với ai!**

---

### Option 2: AI Analysis (Cho người dùng nâng cao)

**Ưu điểm:**
- ✅ Phân tích AI thông minh
- ✅ Báo cáo tự động
- ✅ Dự đoán chi tiêu

**Yêu cầu:**
- Bot phải có file `google_service_account.json`
- Bạn phải share spreadsheet với service account email

**Bước làm:**

#### 2.1. Hỏi admin email của service account
Gửi tin cho admin project:
```
"Cho mình xin service account email để share spreadsheet"
```

Admin sẽ trả lời (ví dụ):
```
freedom-wallet-bot@project-123456.iam.gserviceaccount.com
```

#### 2.2. Share spreadsheet
1. Mở spreadsheet của bạn (đã copy ở Bước 1)
2. Click **Share** (góc trên bên phải)
3. Paste email service account
4. Quyền: **Viewer** (chỉ đọc)
5. **Bỏ tick** "Notify people"
6. Click **Share**

#### 2.3. Kết nối với bot
```
/setsheet [ID_MỚI_CỦA_BẠN]
```

**Ví dụ:**
```
/setsheet 1a2B3c4D5e6F7g8H9i0J1k2L3m4N5o6P7q8R9s0T1u2V3w4X
```

#### 2.4. Kiểm tra
Bot sẽ báo:
```
✅ Kết nối thành công!

📊 Thông tin:
• Sheet: Freedom Wallet - John
• Số dư: 5,000,000đ

🤖 Tính năng đã mở:
✅ Quick Record
✅ AI Analysis (Premium)
```

---

## 🔧 Xử Lý Lỗi

### Lỗi 1: "Bạn đang dùng Template ID"
```
⚠️ Bạn đang dùng Template ID!
```

**Giải pháp:** Copy template về Drive của bạn (Bước 1 ở trên)

---

### Lỗi 2: "Permission denied"
```
❌ Không thể kết nối!
⚠️ Lỗi: Permission denied
```

**Nguyên nhân:**
- Bạn chưa share với service account email
- Hoặc share sai email

**Giải pháp:**
1. Kiểm tra lại service account email từ admin
2. Share lại spreadsheet với email đúng
3. Quyền: **Viewer**
4. Thử lại: `/setsheet [ID_CỦA_BẠN]`

---

### Lỗi 3: "Spreadsheet not found (404)"
```
❌ Không tìm thấy spreadsheet
```

**Nguyên nhân:**
- ID sai
- Hoặc spreadsheet đã bị xóa

**Giải pháp:**
1. Kiểm tra lại URL: `https://docs.google.com/spreadsheets/d/[ID]/edit`
2. Copy đúng phần ID (44 ký tự)
3. Thử lại

---

### Lỗi 4: "DateHelper.generateId is not a function"
```
❌ Lỗi: DateHelper.generateId is not a function
```

**Nguyên nhân:** Bạn copy template CŨ (trước khi fix bug)

**Giải pháp:**

**Option A: Copy template MỚI (Đơn giản)**
1. Copy template mới nhất: https://docs.google.com/spreadsheets/d/1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg/copy
2. Import dữ liệu cũ:
   - File → Import
   - Upload file cũ
   - Replace data

**Option B: Update Apps Script (Nâng cao)**
1. Mở Extensions → Apps Script
2. Tìm file `DateHelper.gs`
3. Thêm method này:
```javascript
generateId(prefix = '') {
  const timestamp = new Date().getTime().toString();
  return prefix ? `${prefix}_${timestamp}` : timestamp;
}
```
4. Ctrl+S lưu lại
5. Redeploy Web App

---

## 📞 Hỗ Trợ

**Nếu vẫn lỗi, hãy gửi cho admin:**
- Screenshot lỗi
- Spreadsheet ID của bạn
- Câu lệnh bạn đã gõ

---

## ✅ Checklist Kiểm Tra

Trước khi báo lỗi, kiểm tra:
- [ ] Đã copy template (không dùng Template ID gốc)
- [ ] Lấy đúng ID mới (từ URL bản copy)
- [ ] **Option 1:** Deploy Web App xong, copy đúng URL
- [ ] **Option 2:** Share với đúng service account email
- [ ] **Option 2:** Quyền Viewer (không phải Editor)
- [ ] Gõ lệnh đúng cú pháp: `/setsheet [ID]` hoặc `/setwebapp [URL]`

---

**Last updated:** 2026-02-09

**Template Version:** v2.0 (with DateHelper.generateId fix)
