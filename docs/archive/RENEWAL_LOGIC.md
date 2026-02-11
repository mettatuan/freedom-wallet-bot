# 📚 RENEWAL LOGIC - Hướng dẫn Gia hạn Premium

## 🎯 Tổng quan

Hệ thống Premium now hỗ trợ **gia hạn thông minh** (smart renewal) - tự động phát hiện user đang gia hạn hay đăng ký mới, và tính toán ngày hết hạn chính xác.

---

## 🔄 Logic Gia hạn

### **Case 1: Đăng ký mới (New Registration)**
- **Điều kiện:** User chưa từng có Premium
- **Kết quả:** Premium expires = **Hôm nay + 365 ngày**

```
User: Chưa Premium
Action: Admin approve payment
Result: Premium từ hôm nay đến 365 ngày sau
```

### **Case 2: Gia hạn sớm (Early Renewal)**
- **Điều kiện:** User đang Premium, còn ít ngày (≤30 ngày)
- **Kết quả:** Premium expires = **Ngày hết hạn cũ + 365 ngày**
- **Lợi ích:** Không mất thời gian còn lại

```
User: Premium, expires 01/03/2025 (còn 20 ngày)
Action: User thanh toán sớm → Admin approve
Result: Premium extends to 01/03/2026 (20 + 365 = 385 ngày)
```

### **Case 3: Gia hạn sau khi hết hạn (Expired Renewal)**
- **Điều kiện:** User đã hết Premium
- **Kết quả:** Premium expires = **Hôm nay + 365 ngày**

```
User: Premium expired 10 days ago
Action: User thanh toán → Admin approve
Result: Premium từ hôm nay đến 365 ngày sau
```

---

## 📊 Ví dụ Thực tế

### Scenario A: User mới
```
Date: 10/02/2025
User: Chưa Premium
Payment: 999,000 VND
Admin: Approve

✅ Result:
  - Subscription: PREMIUM
  - Expires: 10/02/2026 (365 ngày)
```

### Scenario B: User Premium còn 20 ngày
```
Date: 10/02/2025
User: Premium, expires 01/03/2025 (20 ngày)
Payment: 999,000 VND (gia hạn sớm)
Admin: Approve

✅ Result:
  - Subscription: PREMIUM
  - Expires: 01/03/2026 (385 ngày từ hôm nay)
  - Bonus: Giữ được 20 ngày còn lại!
```

### Scenario C: User Premium expired
```
Date: 10/02/2025
User: Premium expired 01/02/2025 (9 ngày trước)
Payment: 999,000 VND (gia hạn sau khi hết)
Admin: Approve

✅ Result:
  - Subscription: PREMIUM
  - Expires: 10/02/2026 (365 ngày từ hôm nay)
```

---

## 🗄️ Database & History

### Payment History Preservation
- **Các lần APPROVED ở các năm khác nhau → Giữ TẤT CẢ** (payment history)
- Chỉ xóa duplicates trong cùng tháng (same period)

```
User: @tuanai_mentor
Payments:
  - 2025-02: VER1 APPROVED ✅ (Year 1)
  - 2026-02: VER10 APPROVED ✅ (Year 2)
  - 2027-02: VER20 APPROVED ✅ (Year 3)

→ Tất cả đều được giữ lại (history)
```

### Duplicate Cleanup Rules
- **Same period + same status:** Giữ 1 mới nhất
- **Different periods:** Giữ tất cả (multi-year history)

```
Example 1: Duplicates in same period
  - 2025-02: VER5 APPROVED, VER6 APPROVED
  → Keep: VER6 (newest), Delete: VER5

Example 2: Different periods
  - 2025-02: VER5 APPROVED
  - 2026-02: VER10 APPROVED
  → Keep: Both (payment history)
```

---

## 🛠️ Technical Implementation

### File: `bot/services/payment_service.py`

```python
async def approve_payment(verification_id, approved_by):
    # Get user and verification
    
    # Smart Renewal Logic
    now = datetime.utcnow()
    
    if (user.subscription_tier == "PREMIUM" and 
        user.premium_expires_at and 
        user.premium_expires_at > now):
        
        # RENEWAL: Extend from current expiry
        user.premium_expires_at += timedelta(days=365)
        logger.info(f"Premium RENEWAL for user {user.id}")
    
    else:
        # NEW or EXPIRED: Start from now
        SubscriptionManager.upgrade_to_premium(user, months=12)
        logger.info(f"Premium ACTIVATION for user {user.id}")
    
    # Update verification status
    verification.status = "APPROVED"
    db.commit()
```

---

## 📋 Testing

### Test Script: `test_renewal_logic.py`

```bash
python test_renewal_logic.py
```

**Tests:**
1. User 1 (new) → 365 days from today
2. User 2 (20 days left) → 385 days from today

---

## 🧹 Cleanup Script

### Smart Cleanup: `cleanup_duplicates_preserve_history.py`

```bash
python cleanup_duplicates_preserve_history.py
```

**Features:**
- Preserves multi-year payment history
- Only removes duplicates within same period
- Color-coded summary

---

## 📝 Google Sheets Integration

### Automatic Logging
When admin approves/rejects payment:
- **Auto-logs to Google Sheet:** [Payment Sheet](https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/)
- **Color coding:**
  - 🟢 Green: APPROVED
  - 🟡 Yellow: PENDING
  - 🔴 Red: REJECTED

---

## ❓ FAQ

### Q1: User còn 300 ngày, có thể gia hạn sớm không?
**A:** Chưa được. User phải đợi đến khi còn ≤30 ngày mới được gia hạn sớm.

### Q2: User thanh toán nhiều lần trong cùng tháng?
**A:** Cleanup script sẽ giữ 1 request mới nhất, xóa duplicates.

### Q3: Làm sao biết user đang gia hạn hay đăng ký mới?
**A:** Hệ thống tự động check:
- User Premium + còn hạn = Gia hạn (extend)
- User hết hạn hoặc chưa Premium = Đăng ký mới (start from now)

### Q4: Có mất thời gian Premium còn lại không?
**A:** Không. Nếu user còn 20 ngày và gia hạn, hệ thống sẽ thêm 365 ngày vào ngày hết hạn cũ (không overwrite).

---

## ✅ Summary

| Case | Condition | Result | Days from now |
|------|-----------|--------|---------------|
| New Registration | Never Premium | Today + 365 | 365 |
| Early Renewal | Premium, ≤30 days left | Old expiry + 365 | ~30 + 365 = 395 |
| Expired Renewal | Premium expired | Today + 365 | 365 |

---

**Last updated:** 10/02/2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
