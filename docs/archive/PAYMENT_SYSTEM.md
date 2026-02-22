# 💳 Payment System - Documentation

## Tổng Quan

Hệ thống thanh toán tự động cho Freedom Wallet Bot với các tính năng:

- ✅ Tạo mã QR thanh toán tự động
- ✅ Xác nhận thanh toán thủ công bởi Admin
- ✅ Tự động nâng cấp tài khoản Premium
- ✅ Thông báo cho user khi kích hoạt

---

## 🔧 Cấu Hình

### 1. Thông Tin Ngân Hàng

File: `config/.env`

```env
# Payment Configuration
PAYMENT_BANK_NAME=OCB
PAYMENT_ACCOUNT_NAME=PHAM THANH TUAN
PAYMENT_ACCOUNT_NUMBER=0107103241416363
PREMIUM_PRICE_VND=999000
```

### 2. Admin User ID

```env
ADMIN_USER_ID=1299465308
```

Admin có quyền:
- Xem danh sách thanh toán chờ duyệt
- Phê duyệt/từ chối thanh toán
- Xem thống kê doanh thu

---

## 📱 Luồng Thanh Toán (User Flow)

### Bước 1: User Nhấn "Nâng Cấp Premium"

```
User nhấn nút: "💎 Nâng cấp Premium"
↓
Bot hiển thị:
- Mã QR thanh toán (VietQR)
- Thông tin chuyển khoản
- Nội dung CK: FW{user_id} PREMIUM
- Số tiền: 999,000 VNĐ
```

**Ảnh QR Code được tạo tự động:**
- URL: `https://img.vietqr.io/image/{bank_code}-{account_number}-compact.jpg?amount=999000&addInfo=FW1299465308 PREMIUM`
- Có thể quét bằng app ngân hàng bất kỳ
- Tự động điền đủ thông tin

### Bước 2: User Chuyển Khoản

User mở app ngân hàng và:
- **Quét mã QR** (khuyến nghị - tự động điền thông tin)
- HOẶC chuyển khoản thủ công với thông tin:
  - Ngân hàng: OCB
  - STK: 0107103241416363
  - Người nhận: PHAM THANH TUAN
  - Số tiền: 999,000 VNĐ
  - Nội dung: `FW{user_id} PREMIUM`

### Bước 3: User Xác Nhận Đã Chuyển

User nhấn nút: **"✅ Đã thanh toán"**

Bot yêu cầu gửi bằng chứng:
- **Ảnh chụp màn hình** giao dịch thành công
- HOẶC **Thông tin text** (số tiền, thời gian, 4 số cuối STK)

### Bước 4: Hệ Thống Tạo Yêu Cầu Xác Nhận

```
Bot tạo PaymentVerification:
- user_id: 1299465308
- amount: 999000
- transaction_info: "Photo: xxxxx" hoặc thông tin text
- status: PENDING
- verification_id: VER123
```

Bot gửi cho user:
```
✅ ĐÃ NHẬN THÔNG TIN
Mã xác nhận: VER123

⏱️ TIẾP THEO:
• Hệ thống đang kiểm tra thanh toán
• Nếu đúng nội dung CK → Tự động (5-10 phút)
• Nếu sai nội dung → Admin xác nhận (15-30 phút)
```

### Bước 5: Admin Xác Nhận

#### 5a. Xem Danh Sách Chờ Duyệt

Admin gửi: `/payment_pending`

Bot trả về:
```
🔍 YÊU CẦU XÁC NHẬN THANH TOÁN

VER123 - @username (ID: 1299465308)
💰 Số tiền: 999,000 VNĐ
⏱️ 5 phút trước
📝 Photo: file_id_xxxxx

Dùng: /payment_approve VER123
```

#### 5b. Phê Duyệt Thanh Toán

Admin gửi: `/payment_approve VER123`

Hệ thống:
1. ✅ Cập nhật PaymentVerification.status = "APPROVED"
2. ✅ Nâng cấp user lên Premium (365 ngày)
3. ✅ Gửi thông báo cho user:

```
🎉 CHÚC MỪNG! PREMIUM Đã Kích Hoạt

✅ THANH TOÁN ĐÃ XÁC NHẬN:
💰 Số tiền: 999,000 VNĐ
⏱️ Thời gian: 14:30 09/02/2026

💎 TÀI KHOẢN PREMIUM:
✅ Kích hoạt: Ngay bây giờ
📅 Hết hạn: 09/02/2027

🎁 BẮT ĐẦU SỬ DỤNG:
• Gửi tin nhắn không giới hạn
• Sử dụng tất cả tính năng Premium
• Hỗ trợ ưu tiên từ Admin
```

#### 5c. Từ Chối Thanh Toán (Nếu Cần)

Admin gửi: `/payment_reject VER123 Sai nội dung chuyển khoản`

Hệ thống gửi thông báo cho user:
```
❌ YÊU CẦU XÁC NHẬN BỊ TỪ CHỐI

📝 LÝ DO:
Sai nội dung chuyển khoản

💡 TIẾP THEO:
Vui lòng kiểm tra lại thông tin...
```

---

## 🔑 Các Lệnh Admin

### `/payment_pending`
Xem tất cả yêu cầu thanh toán đang chờ duyệt

**Output:**
- Danh sách các verification với status=PENDING
- Hiển thị 10 yêu cầu mới nhất
- Thông tin: VER ID, user, số tiền, thời gian, thông tin giao dịch

### `/payment_approve VER{id}`
Phê duyệt thanh toán và kích hoạt Premium

**Ví dụ:** `/payment_approve VER123`

**Hành động:**
1. Cập nhật verification status → APPROVED
2. Nâng cấp user lên Premium (365 ngày)
3. Gửi thông báo chúc mừng cho user
4. Xác nhận với admin

### `/payment_reject VER{id} [lý do]`
Từ chối thanh toán

**Ví dụ:** `/payment_reject VER123 Sai nội dung CK`

**Hành động:**
1. Cập nhật verification status → REJECTED
2. Lưu lý do từ chối
3. Gửi thông báo cho user với lý do
4. Xác nhận với admin

### `/payment_stats`
Xem thống kê thanh toán

**Output:**
- Số yêu cầu: Pending, Approved, Rejected
- Tổng doanh thu (từ các thanh toán approved)
- Số lượng Premium users

---

## 📊 Database Schema

### Bảng: `payment_verifications`

```sql
CREATE TABLE payment_verifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount FLOAT,
    transaction_info TEXT,
    transfer_code VARCHAR(50),
    status VARCHAR(20) DEFAULT 'PENDING',
    submitted_by INTEGER,
    approved_by INTEGER,
    created_at TIMESTAMP,
    approved_at TIMESTAMP,
    notes TEXT
);
```

**Các status:**
- `PENDING`: Chờ admin xác nhận
- `APPROVED`: Đã duyệt, user được nâng cấp
- `REJECTED`: Từ chối, cần xử lý lại

### Bảng: `users` (Cập nhật)

Các cột liên quan đến Premium:
```sql
subscription_tier VARCHAR(20) DEFAULT 'TRIAL'  -- TRIAL, FREE, PREMIUM
premium_started_at TIMESTAMP
premium_expires_at TIMESTAMP
```

---

## 🔐 Bảo Mật

### Mã Transfer Code

Format: `FW{user_id}`

**Ví dụ:**
- User ID 1299465308 → Transfer code: `FW1299465308`
- Dễ nhớ, dễ viết
- Unique cho mỗi user
- Có thể dùng để tự động verify (future)

### Verification ID

Format: `VER{id}`

**Ví dụ:** `VER123`

- Dễ đọc cho admin
- Unique trong hệ thống
- Dùng cho tra cứu và xử lý

---

## 🚀 Future Enhancements

### 1. Tự Động Xác Nhận (Auto-Verify)

**Tích hợp với Bank API:**
- Nhận webhook từ ngân hàng khi có giao dịch
- Parse nội dung CK để lấy transfer_code
- Tự động approve nếu khớp user_id và số tiền

**Code placeholder:**
```python
# In payment_service.py
async def verify_payment(user_id, transaction_id):
    # TODO: Call bank API
    # TODO: Check transaction amount
    # TODO: Parse transfer message
    # TODO: Auto-approve if match
    pass
```

### 2. Payment Gateway (MoMo, ZaloPay)

Tích hợp API các cổng thanh toán:
- MoMo: Deep link để mở app
- ZaloPay: QR code
- VNPay: Chuyển hướng web

### 3. Subscription Auto-Renew

- Lưu thông tin thanh toán
- Tự động gia hạn khi hết hạn
- Gửi thông báo trước khi gia hạn

### 4. Tiered Pricing

- Premium Monthly: 99,000 VND/tháng
- Premium Yearly: 999,000 VND/năm (giảm 17%)
- Lifetime: 2,999,000 VND (một lần)

---

## 📝 Testing Guide

### Test Case 1: Happy Path

1. User nhấn "Nâng cấp Premium"
2. User quét QR code
3. User chuyển khoản với đúng nội dung
4. User nhấn "Đã thanh toán"
5. User gửi ảnh chụp màn hình
6. Admin chạy `/payment_pending`
7. Admin chạy `/payment_approve VER123`
8. User nhận thông báo kích hoạt
9. User gửi tin nhắn → Không bị giới hạn

**Expected:** ✅ Premium activated, user can use unlimited

### Test Case 2: Wrong Transfer Content

1. User chuyển khoản nhưng **quên ghi nội dung**
2. User gửi bằng chứng
3. Admin thấy thiếu transfer_code
4. Admin chạy `/payment_reject VER123 Thiếu nội dung CK`
5. User nhận thông báo từ chối
6. User liên hệ admin để xử lý

**Expected:** ❌ Rejected, user needs to re-submit or contact admin

### Test Case 3: Multiple Payments

1. User A chuyển khoản
2. User B chuyển khoản
3. User C chuyển khoản
4. Admin chạy `/payment_pending` → Thấy 3 yêu cầu
5. Admin duyệt từng cái: `/payment_approve VER1`, `/payment_approve VER2`, `/payment_approve VER3`

**Expected:** ✅ All 3 users activated

---

## 🐛 Troubleshooting

### Issue: QR Code không hiển thị

**Nguyên nhân:** URL VietQR bị lỗi hoặc bank_code sai

**Giải pháp:**
1. Check `settings.PAYMENT_BANK_NAME` = "OCB"
2. Check `BANK_CODES["OCB"]` = "970448"
3. Test QR URL trực tiếp trên browser

### Issue: User không nhận thông báo

**Nguyên nhân:** User đã block bot hoặc bot không có quyền gửi

**Giải pháp:**
1. Check log: "Error notifying user"
2. Yêu cầu user /start lại bot
3. Admin gửi tin nhắn thủ công cho user

### Issue: Admin không thấy pending payments

**Nguyên nhân:** User chưa gửi bằng chứng hoặc DB lỗi

**Giải pháp:**
1. Check log: PaymentVerification created
2. Check database: `SELECT * FROM payment_verifications WHERE status='PENDING'`
3. Yêu cầu user gửi lại bằng chứng

---

## 📞 Support

**Admin Contact:**
- Telegram: @Mettatuan
- User ID: 1299465308

**Documentation:**
- Payment System: `docs/PAYMENT_SYSTEM.md` (file này)
- Premium Menu: `docs/PREMIUM_MENU_GUIDE.md`
- Database Schema: `docs/DATABASE_SCHEMA.md`

---

## ✅ Checklist Deployment

- [x] Cấu hình thông tin ngân hàng trong .env
- [x] Set ADMIN_USER_ID trong .env
- [x] Tạo bảng payment_verifications trong database
- [x] Test QR code generation
- [ ] Test payment flow end-to-end
- [ ] Train admin về các lệnh payment
- [ ] Thông báo users về phương thức thanh toán mới

---

**Last Updated:** February 9, 2026
**Version:** 1.0
**Author:** GitHub Copilot
