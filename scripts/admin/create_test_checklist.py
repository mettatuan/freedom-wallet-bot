"""
Manual Test Guide - Premium Flow
================================

CHUẨN BỊ:
---------
1. Start bot: python main.py
2. Mở Telegram, tìm bot Freedom Wallet
3. Ghi chú lỗi nào gặp phải (nếu có)

TEST 1: TRIAL ACTIVATION (Kích hoạt dùng thử)
----------------------------------------------
[ ] 1.1. Gửi /start
    Expected: Thấy welcome message với nút "🎁 Dùng thử Premium (7 ngày)"
    
[ ] 1.2. Click "🎁 Dùng thử Premium"
    Expected: Thấy thông báo trial activated, menu Premium hiện ra
    
[ ] 1.3. Kiểm tra thông báo
    Expected: 
    - ✅ Trial được kích hoạt
    - ✅ Thấy streak hiện tại
    - ✅ Thấy 6 nút menu (Ghi chi tiêu, Tình hình, Phân tích, Gợi ý, Setup, Hỗ trợ)


TEST 2: PREMIUM MENU NAVIGATION (Điều hướng menu)
-------------------------------------------------
[ ] 2.1. Click "💬 Ghi chi tiêu nhanh"
    Expected: Thấy hướng dẫn nhập giao dịch nhanh
    
[ ] 2.2. Click "« Quay lại"
    Expected: Quay về Premium menu (6 nút)
    ⚠️ NẾU LỖI: Ghi chú lỗi xuất hiện
    
[ ] 2.3. Click "📊 Tình hình hôm nay"
    Expected: Thấy thống kê hôm nay (chi tiêu, streak)
    
[ ] 2.4. Click "« Quay lại"
    Expected: Quay về Premium menu
    ⚠️ NẾU LỖI: Ghi chú lỗi xuất hiện
    
[ ] 2.5. Click "🧠 Phân tích cho tôi"
    Expected: Thấy loading 2-3s, sau đó hiện phân tích
    
[ ] 2.6. Click "« Quay lại"
    Expected: Quay về Premium menu
    ⚠️ NẾU LỖI: Ghi chú lỗi xuất hiện
    
[ ] 2.7. Click "🎯 Gợi ý tiếp theo"
    Expected: Thấy gợi ý hành động
    
[ ] 2.8. Click "« Quay lại"
    Expected: Quay về Premium menu
    ⚠️ NẾU LỖI: Ghi chú lỗi xuất hiện
    
[ ] 2.9. Click "🛠️ Setup giúp tôi"
    Expected: Thấy menu setup với các tùy chọn
    
[ ] 2.10. Click "« Quay lại"
    Expected: Quay về Premium menu
    ⚠️ NẾU LỖI: Ghi chú lỗi xuất hiện
    
[ ] 2.11. Click "🚀 Hỗ trợ ưu tiên"
    Expected: Thấy thông tin liên hệ support
    
[ ] 2.12. Click "« Quay lại"
    Expected: Quay về Premium menu
    ⚠️ NẾU LỖI: Ghi chú lỗi xuất hiện


TEST 3: PREMIUM UPGRADE (Nâng cấp Premium)
------------------------------------------
[ ] 3.1. Gửi /start hoặc click button về trang chủ
    
[ ] 3.2. Click "💎 Xem gói Premium" hoặc "💎 Nâng cấp Premium"
    Expected: Thấy thông tin gói Premium với giá 999,000 VND/năm
    
[ ] 3.3. Click "💎 Nâng cấp Premium ngay" hoặc "💬 Chat với Support để thanh toán"
    Expected: 
    - ✅ Thấy mã QR thanh toán (ảnh QR code)
    - ✅ Thấy thông tin chuyển khoản:
        • Bank: OCB
        • Tên: PHAM THANH TUAN
        • Số TK: 0107103241416363
        • Số tiền: 999,000 VND
        • Nội dung: FW1299465308 PREMIUM
    
[ ] 3.4. Kiểm tra QR code
    Expected: QR code load được, không bị lỗi 404
    ⚠️ NẾU LỖI: Ghi chú "QR code không load"


TEST 4: PAYMENT SUBMISSION (Gửi xác nhận thanh toán)
----------------------------------------------------
[ ] 4.1. Click "✅ Đã thanh toán"
    Expected: Thấy hướng dẫn gửi ảnh hoặc thông tin chuyển khoản
    
[ ] 4.2. Gửi text: "Đã chuyển 999,000 VND lúc 14:30 ngày 10/02/2026"
    Expected: 
    - ✅ Bot phản hồi "✅ ĐÃ NHẬN THÔNG TIN"
    - ✅ Có mã xác nhận (VER1, VER2, etc.)
    - ✅ Thông báo sẽ được xử lý trong 5-30 phút
    
[ ] 4.3. Hoặc gửi ảnh screenshot chuyển khoản
    Expected: 
    - ✅ Bot phản hồi "✅ ĐÃ NHẬN ẢNH XÁC NHẬN"
    - ✅ Có mã xác nhận
    

TEST 5: ADMIN APPROVAL (Duyệt thanh toán - Admin only)
------------------------------------------------------
⚠️ CHỈ ADMIN MỚI LÀM PHẦN NÀY

[ ] 5.1. Gửi /payment_pending
    Expected: Thấy danh sách yêu cầu xác nhận (nếu có)
    
[ ] 5.2. Copy mã VER từ danh sách (ví dụ: VER1)
    
[ ] 5.3. Gửi /payment_approve VER1
    Expected:
    - ✅ Bot phản hồi "✅ Đã phê duyệt VER1"
    - ✅ User được nâng cấp lên Premium 365 ngày
    - ✅ User nhận thông báo "🎉 CHÚC MỪNG! PREMIUM Đã Kích Hoạt"
    
[ ] 5.4. User kiểm tra lại
    - Gửi /start
    - Expected: Thấy badge Premium hoặc thông báo Premium active


TEST 6: PREMIUM FEATURES ACCESS (Truy cập tính năng Premium)
------------------------------------------------------------
[ ] 6.1. Sau khi Premium được kích hoạt, gửi /start
    Expected: Thấy Premium menu hoặc badge Premium
    
[ ] 6.2. Gửi nhiều tin nhắn liên tiếp (> 5 tin nhắn)
    Expected: 
    - ✅ KHÔNG bị giới hạn
    - ✅ Bot phản hồi tất cả tin nhắn
    
[ ] 6.3. Click vào các menu Premium
    Expected: Tất cả menu hoạt động bình thường


TEST 7: ERROR HANDLING (Xử lý lỗi)
----------------------------------
[ ] 7.1. Click "« Quay lại" nhiều lần liên tiếp (5-10 lần)
    Expected: 
    - ✅ KHÔNG có lỗi "😓 Xin lỗi, có lỗi xảy ra"
    - ✅ Menu chuyển đổi mượt mà
    
[ ] 7.2. Click nút ngẫu nhiên trong Premium menu
    Expected: 
    - ✅ Mọi nút đều hoạt động
    - ✅ Không có lỗi 
    
[ ] 7.3. Gửi các lệnh /start, /help, /support khi đang ở menu
    Expected: 
    - ✅ Bot phản hồi đúng
    - ✅ Không bị crash


CHECKLIST TỔNG HỢP:
===================
[ ] Trial activation hoạt động
[ ] Premium menu có 6 nút
[ ] Tất cả nút "Quay lại" hoạt động
[ ] Không có lỗi "😓 Xin lỗi, có lỗi xảy ra"
[ ] Payment QR code hiển thị đúng
[ ] Thông tin chuyển khoản đúng (OCB, số TK)
[ ] User có thể gửi xác nhận thanh toán
[ ] Admin có thể duyệt thanh toán
[ ] Premium được kích hoạt sau khi duyệt
[ ] User Premium không bị giới hạn tin nhắn


KẾT QUẢ:
=========
Số test passed: ____ / 7
Số lỗi gặp phải: ____

LỖI CHI TIẾT (nếu có):
---------------------
1. 
2. 
3. 


ĐÁNH GIÁ:
==========
[ ] PASS - Tất cả flow hoạt động mượt mà
[ ] MINOR ISSUES - Có vài lỗi nhỏ không ảnh hưởng
[ ] MAJOR ISSUES - Có lỗi nghiêm trọng cần fix
[ ] FAIL - Flow không hoạt động


GHI CHÚ BỔ SUNG:
================


"""
with open("test_premium_manual_checklist.txt", "w", encoding="utf-8") as f:
    f.write(__doc__)

print("✅ Test checklist saved to: test_premium_manual_checklist.txt")
print("\n📋 Bây giờ bạn có thể:")
print("1. Mở file test_premium_manual_checklist.txt")
print("2. In ra hoặc xem trên màn hình")
print("3. Làm theo từng bước và đánh dấu [x] khi hoàn thành")
print("4. Ghi chú lỗi nếu gặp")
print("\n💡 Tip: Mở 2 tab Telegram - 1 tab là user, 1 tab là admin")
