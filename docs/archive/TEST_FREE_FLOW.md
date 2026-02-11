# 🧪 TEST FREE FLOW - Testing Guide

**Date:** February 10, 2026  
**Purpose:** Test toàn bộ FREE unlock flow theo Three-Tier Master Strategy  
**Status:** ✅ Bot running, ready for testing

---

## 📋 Test Scenario: FREE Flow (Value-First)

### **Strategic Context:**
- **Messaging:** "Sở Hữu Ngay, Dùng Mãi" ♾️
- **Psychology:** User cảm thấy "Tôi SỞ HỮU công cụ này mãi mãi"
- **Unlock Requirement:** 2 referrals
- **Duration:** Forever (không trial, không expire)
- **Value:** Template + 5 AI msgs/day + Community

---

## 🎯 Test Steps

### **1️⃣ START BOT**

**Action:**
```
Mở Telegram → Search bot → /start
```

**Expected Result:**
```
Chào [Name]! 👋

Bạn muốn làm gì hôm nay?

[🆓 Nhận Miễn Phí Ngay]  ⭐️ NEW
[📊 Tài Chính Cá Nhân]
[💬 Trợ Lý AI]
[⚙️ Cài Đặt]
```

**Verify:**
- ✅ Welcome message appears
- ✅ Button "🆓 Nhận Miễn Phí Ngay" visible
- ✅ Clean, friendly tone (no urgency)
- ✅ No mention of "trial" or "limited time"

---

### **2️⃣ TAP "🆓 Nhận Miễn Phí Ngay"**

**Action:**
```
Nhấn button "🆓 Nhận Miễn Phí Ngay"
```

**Expected Result:**
```
🎁 MỞ KHÓA MIỄN PHÍ MÃI MÃI

Sở hữu Freedom Wallet Template với:

✅ Template Google Sheets chuyên nghiệp
✅ 5 câu hỏi AI mỗi ngày
✅ Quick Record nhanh 5s
✅ Community hỗ trợ

📌 Cách mở khóa:
Giới thiệu 2 người bạn sử dụng bot

🔗 Link giới thiệu của bạn:
https://t.me/YourBot?start=ref_123456

📊 Tiến độ: 0/2 người ✨

[📋 Copy Link]
[❓ Cần Giúp Đỡ?]
[🏠 Về Menu]
```

**Verify:**
- ✅ Clear value proposition (4 benefits listed)
- ✅ Unlock method explained (2 referrals)
- ✅ Personal referral link visible
- ✅ Progress counter shows 0/2
- ✅ Messaging: "Mở khóa" NOT "Dùng thử"
- ✅ Messaging: "Mãi mãi" visible
- ✅ NO countdown, NO urgency, NO scarcity
- ✅ Copy link button available

---

### **3️⃣ COPY REFERRAL LINK**

**Action:**
```
Nhấn [📋 Copy Link]
```

**Expected Result:**
```
✅ Đã copy link giới thiệu vào clipboard!

💡 Bạn có thể share link này:
• Nhóm bạn bè
• Facebook, Zalo
• Nhóm cộng đồng tài chính

Remember: 2 người đăng ký = Mở khóa FREE mãi mãi! ♾️
```

**Verify:**
- ✅ Confirmation message appears
- ✅ Suggestions for sharing (not pushy)
- ✅ Reminder of benefit (ownership forever)
- ✅ Link actually copied (test paste)

---

### **4️⃣ SIMULATE REFERRAL #1**

**Action:**
```
Open incognito browser/another device
Open referral link: https://t.me/YourBot?start=ref_123456
/start in Telegram
```

**Expected Result (Referee):**
```
Chào bạn! 👋

Bạn được [User Name] giới thiệu đến Freedom Wallet Bot!

[🆓 Nhận Miễn Phí Ngay]
[📊 Tài Chính Cá Nhân]
[💬 Trợ Lý AI]
```

**Expected Result (Referrer - Original User):**
```
🎉 CÓ NGƯỜI BẠN MỚI!

[Name] vừa tham gia qua link của bạn!

📊 Tiến độ: 1/2 người ✨

Còn 1 người nữa là mở khóa FREE mãi mãi!

[📋 Share Tiếp]
```

**Verify (Referee):**
- ✅ Referrer name appears in welcome message
- ✅ Same unlock flow available
- ✅ No mention of trial or expiry

**Verify (Referrer):**
- ✅ Notification of new referral
- ✅ Progress updated: 1/2
- ✅ Encouraging message (not pushy)
- ✅ Option to share again

---

### **5️⃣ SIMULATE REFERRAL #2**

**Action:**
```
Repeat step 4 with another user/device
```

**Expected Result (Referrer - Original User):**
```
🎊 CHÚC MỪNG! FREE ĐÃ MỞ KHÓA!

Bạn vừa sở hữu Freedom Wallet Template mãi mãi! ♾️

✨ Những gì bạn có:
✅ Template Google Sheets chuyên nghiệp
✅ 5 câu hỏi AI mỗi ngày
✅ Quick Record nhanh 5s
✅ Community hỗ trợ

🚀 Bước tiếp theo:
[🔗 Kết Nối Google Sheets]
[📊 Xem Template]
[💬 Hỏi AI]

💡 Mẹo: Tiếp tục giới thiệu để trở thành VIP và nhận thêm ưu đãi!
```

**Verify:**
- ✅ Celebration message appears
- ✅ Emphasizes "sở hữu mãi mãi"
- ✅ Lists all benefits again
- ✅ Clear next steps provided
- ✅ Soft CTA for VIP (not pushy)
- ✅ Database: `is_free_unlocked = TRUE`
- ✅ Database: `free_unlocked_at = current timestamp`
- ✅ Database: `referral_count = 2`

---

### **6️⃣ ACCESS FREE FEATURES**

#### **6A: Connect Google Sheets**

**Action:**
```
Nhấn [🔗 Kết Nối Google Sheets]
```

**Expected Result:**
```
🔗 KẾT NỐI GOOGLE SHEETS

Để kết nối template:

1️⃣ Mở link này: [Google Sheets Template]
2️⃣ Chọn "File" → "Make a copy"
3️⃣ Chia sẻ sheet với: [email]
4️⃣ Gửi link sheet cho bot

[📋 Copy Email]
[❓ Hướng Dẫn Chi Tiết]
```

**Verify:**
- ✅ Clear setup instructions
- ✅ Template link works
- ✅ Service account email visible
- ✅ Help available

---

#### **6B: Use AI Assistant (5 msgs/day)**

**Action:**
```
Gửi câu hỏi: "Tôi nên tiết kiệm bao nhiêu mỗi tháng?"
```

**Expected Result:**
```
💬 TRỢ LÝ AI

[Answer to question]

📊 Bạn còn 4/5 câu hỏi hôm nay.
🔄 Reset vào 00:00 ngày mai.

💡 Muốn hỏi không giới hạn?
[🎯 Tìm Hiểu VIP] ⭐
```

**Verify:**
- ✅ AI responds to question
- ✅ Counter shows remaining (4/5)
- ✅ Reset time mentioned
- ✅ Soft VIP CTA (not pushy)
- ✅ No hard limit blocking

**Action (After 5 messages):**
```
Gửi câu hỏi thứ 6
```

**Expected Result:**
```
⏰ ĐÃ HẾT LƯỢT HỎI HÔM NAY

Bạn đã dùng hết 5 câu hỏi miễn phí.

🔄 Lượt mới vào: 00:00 ngày mai

💡 Hoặc:
[⭐ Trở Thành VIP] - Không giới hạn AI
[🏠 Về Menu]

Remember: FREE đủ cho hầu hết người dùng! 
Chỉ nâng cấp khi thực sự cần.
```

**Verify:**
- ✅ Friendly limit message (not angry)
- ✅ Clear when reset happens
- ✅ VIP option mentioned (not aggressive)
- ✅ Anti-pushy message bottom
- ✅ **CRITICAL:** "FREE đủ cho hầu hết người dùng" present

---

#### **6C: Quick Record**

**Action:**
```
Gửi: "Cà phê 30k"
```

**Expected Result:**
```
✅ ĐÃ GHI NHANH

📝 Cà phê 30k
📅 10/02/2026
💰 -30,000 VND

[✏️ Sửa]
[📊 Xem Báo Cáo]
[🏠 Menu]
```

**Verify:**
- ✅ Quick record parses correctly
- ✅ Amount, date, category extracted
- ✅ Data saved to Google Sheets
- ✅ Confirmation clean and fast

---

### **7️⃣ VERIFY DATABASE**

**Action:**
```sql
SELECT 
    telegram_id,
    full_name,
    referral_count,
    is_free_unlocked,
    free_unlocked_at,
    vip_tier,
    created_at
FROM users
WHERE telegram_id = [test_user_id];
```

**Expected Result:**
```
telegram_id: 123456789
full_name: Test User
referral_count: 2
is_free_unlocked: TRUE
free_unlocked_at: 2026-02-10 23:05:00
vip_tier: NULL (not VIP yet)
created_at: 2026-02-10 22:50:00
```

**Verify:**
- ✅ `is_free_unlocked = TRUE`
- ✅ `free_unlocked_at` timestamp set
- ✅ `referral_count = 2`
- ✅ `vip_tier` still NULL (VIP requires 10+ refs)

---

## ✅ Test Checklist

### **Messaging & Psychology:**
- [ ] ✅ "Sở Hữu Ngay, Dùng Mãi" messaging clear
- [ ] ✅ NO "trial", "limited time", "urgency" language
- [ ] ✅ "Mãi mãi" / "Forever" emphasized
- [ ] ✅ Ownership feeling conveyed

### **Unlock Flow:**
- [ ] ✅ 2 referrals required (not more, not less)
- [ ] ✅ Progress counter accurate (0/2 → 1/2 → 2/2)
- [ ] ✅ Referral link works
- [ ] ✅ Auto-unlock after 2nd referral
- [ ] ✅ Celebration message appears

### **FREE Features:**
- [ ] ✅ Google Sheets template accessible
- [ ] ✅ AI assistant 5 msgs/day limit working
- [ ] ✅ AI limit message friendly, not angry
- [ ] ✅ Quick Record working
- [ ] ✅ All features persist (no expiry)

### **Database:**
- [ ] ✅ `is_free_unlocked` set to TRUE
- [ ] ✅ `free_unlocked_at` timestamp recorded
- [ ] ✅ `referral_count` updated correctly

### **Anti-Pushy Elements:**
- [ ] ✅ VIP CTAs present but SUBTLE
- [ ] ✅ "FREE đủ cho hầu hết người dùng" message visible
- [ ] ✅ No aggressive upselling
- [ ] ✅ User feels satisfied with FREE

---

## 🚨 Common Issues & Fixes

### **Issue 1: Referral không đếm**
**Symptom:** Progress stuck at 0/2 sau khi có người dùng link  
**Check:**
```python
# bot/handlers/unlock_flow_v3.py
# Line ~50: track_referral function
```
**Fix:** Verify `referred_by` field được set khi user /start với referral link

---

### **Issue 2: Unlock message không xuất hiện**
**Symptom:** User có 2 refs nhưng không thấy celebration  
**Check:**
```python
# bot/handlers/unlock_flow_v3.py
# Line ~120: check_and_unlock_free function
```
**Fix:** Verify `is_free_unlocked` check và `update` query

---

### **Issue 3: AI limit không reset**
**Symptom:** User vẫn bị chặn sau 00:00  
**Check:**
```python
# bot/services/ai_service.py
# Daily reset logic
```
**Fix:** Verify timezone (Vietnam = UTC+7) và reset logic

---

## 📊 Success Metrics (Track Only, Don't Optimize)

After testing, track these in dashboard:

1. **30-Day Retention:** Users active 7+ days after unlock
   - Target: ≥50%
   
2. **Transactions per User:** Average recorded transactions
   - Target: ≥10/month
   
3. **AI Usage:** Average AI questions per user
   - Target: 3-5 msgs/day (within FREE limit)
   
4. **VIP Conversion:** % of FREE users who reach 10+ refs
   - Natural progression (no optimization needed)

---

## 🎯 Next Steps After Testing

**If all tests pass:**
- [ ] Deploy to production (Feb 24, 2026)
- [ ] Start 60-day observation period
- [ ] Track metrics via `/admin_metrics`
- [ ] NO changes to flow for 60 days

**If tests fail:**
- [ ] Document issue in this file
- [ ] Fix critical bugs only
- [ ] Re-test before deployment
- [ ] Do NOT change strategy

---

## 🔒 CRITICAL REMINDER

**Three-Tier Master Strategy is LOCKED until Week 15 (May 26, 2026).**

During testing:
- ✅ Fix bugs
- ✅ Verify functionality
- ✅ Document observations
- ❌ NO feature additions
- ❌ NO messaging changes
- ❌ NO conversion optimization

**One answer to all change requests:**
> "Không. Chiến lược đã ký. Đợi đủ 60 ngày."

---

**Testing Date:** February 10, 2026  
**Tester:** [Your Name]  
**Bot Status:** ✅ Running  
**Test Result:** [ ] PASS / [ ] FAIL  
**Notes:**

