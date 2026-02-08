# 🧪 TEST GUIDE - VIP UNLOCK FLOW v2.1

## ✅ BOT STATUS: RUNNING

Bot đang chạy tại: **@FreedomWalletbot**  
Terminal ID: `91ad81b2-7c88-40e6-bf1d-9f104aafef9c`

---

## 🎯 MỤC TIÊU TEST

Test 3 thay đổi chính của v2.1:
1. ✅ Message 3 split thành 3A + 3B
2. ✅ "Day 1" → "BƯỚC ĐẦU TIÊN"
3. ✅ "Cho phép làm chậm" copy
4. ✅ Buttons: 5 → 3

---

## 📋 TEST SCENARIO: VIP UNLOCK FLOW

### SETUP (Tạo Test Environment)

**Cần 3 Telegram accounts để test:**
- **User A** (Main) - Người giới thiệu
- **User B** - Referral #1
- **User C** - Referral #2 (trigger VIP unlock)

**Hoặc dùng database để trigger trực tiếp:**
```python
# Option: Simulate VIP unlock via Python
from bot.utils.database import SessionLocal, User

with SessionLocal() as session:
    user = session.query(User).filter(User.id == YOUR_TELEGRAM_ID).first()
    user.referral_count = 2  # Simulate 2 completed referrals
    session.commit()
    
# Then send /start to trigger VIP unlock messages
```

---

## 🔍 TEST STEPS - FULL FLOW

### **STEP 1: User A Starts Bot**
```
Action: /start
Expected:
  - Welcome message
  - Registration flow begins
```

### **STEP 2: User A Gets Referral Link**
```
Action: Complete registration
Expected:
  - User A receives referral link: https://t.me/FreedomWalletbot?start=REF_[ID]
```

### **STEP 3: User B Registers via Link**
```
Action: User B clicks referral link → /start
Expected:
  - User A receives notification: "1/2 giới thiệu hoàn thành"
  - Message has 2 buttons: "Chia sẻ tiếp", "Xem tiến độ"
```

### **STEP 4: User C Registers (TRIGGER VIP UNLOCK)**
```
Action: User C clicks referral link → /start → completes registration
Expected: User A receives 4 messages sequentially:
```

---

## 📨 EXPECTED VIP UNLOCK MESSAGES (Check Each)

### ✅ **MESSAGE 1: Celebration Image** (Instant)

**Expected:**
- 🖼️ Image: `chucmung.png`
- Caption: "🎉 CHÚC MỪNG! 🎉"
- "[User C name] vừa hoàn tất đăng ký!"
- "Bạn đã HOÀN THÀNH 2 / 2 LƯỢT GIỚI THIỆU"

**No buttons** ✅

---

### ✅ **MESSAGE 2: VIP Announcement + Identity** (1s delay)

**Expected:**
```
━━━━━━━━━━━━━━━━━━━━━
👑 CHÀO MỪNG BẠN TRỞ THÀNH
THÀNH VIÊN VIP – FREEDOM WALLET
━━━━━━━━━━━━━━━━━━━━━

Bạn đã chính thức bước sang
giai đoạn sử dụng sâu hơn và hiệu quả hơn.

💡 Thành viên VIP là những người:
• Đã chủ động hành động
• Muốn quản lý tài chính nghiêm túc
• Sẵn sàng đi sâu hơn thay vì chỉ xem
```

**No buttons** ✅

**✨ Check:** Identity anchor có hiển thị đúng không?

---

### ✅ **MESSAGE 3A: Benefits** (2s after Message 2)

**Expected:**
```
🎁 QUYỀN LỢI DÀNH CHO BẠN:

✅ Công cụ quản lý tài chính đầy đủ
✅ Web App cá nhân
✅ Hướng dẫn từng bước
✅ Group VIP hỗ trợ trực tiếp

👉 Bước tiếp theo rất đơn giản.
```

**Buttons: 1 button only** ✅
```
┌───────────────────────────────────────┐
│  ➡️ Tiếp tục                          │
└───────────────────────────────────────┘
```

**✨ Check:**
- [ ] Chỉ 1 button (không có 5 buttons như v1)
- [ ] Text ngắn gọn, không hỏi gì cả

**Action:** Click "Tiếp tục"

---

### ✅ **MESSAGE 3B: Action Menu** (After click "Tiếp tục")

**Expected:**
```
🚀 Để sử dụng Freedom Wallet,
bạn cần tạo Web App (3–5 phút).

Bạn đã tạo xong chưa?
```

**Buttons: 2 buttons only** ✅
```
┌───────────────────────────────────────┐
│  ✅ Tôi đã tạo xong                   │
├───────────────────────────────────────┤
│  📖 Xem hướng dẫn 3 bước              │
└───────────────────────────────────────┘
```

**✨ Check:**
- [ ] Message 3A bị replace bởi Message 3B (edit_message_text)
- [ ] Chỉ 2 buttons (binary choice)
- [ ] Không có links Notion/Group ở đây

---

### ✅ **MESSAGE 4: "BƯỚC ĐẦU TIÊN"** (10 minutes after Message 3A)

**Expected Title:** 🎯 BƯỚC ĐẦU TIÊN – BẮT ĐẦU TỪ ĐÂU?

**Expected Content:**
```
Chào mừng đến với Freedom Wallet!

Trong 7 ngày tới, bạn sẽ:
✓ Làm chủ 6 Hũ Tiền
✓ Hiểu rõ 5 Cấp Bậc Tài Chính
✓ Xây dựng thói quen quản lý tiền

━━━━━━━━━━━━━━━━━━━━━

🎯 HÀNH ĐỘNG ĐẦU TIÊN - CHỈ 1 VIỆC:

Thêm giao dịch đầu tiên vào Web App

Đó là tất cả! Chỉ cần 1 giao dịch bất kỳ:
• Ly cafe sáng nay: -35,000đ
• Lương nhận được: +15,000,000đ
• Mua sách: -120,000đ

→ Bất cứ giao dịch nào cũng được!

━━━━━━━━━━━━━━━━━━━━━

💡 Tại sao chỉ 1 giao dịch?

Mình muốn bạn tập trung vào việc BẮT ĐẦU,
không phải hoàn hảo ngay từ đầu.

Một lần thành công nhỏ sẽ tạo động lực
cho những bước tiếp theo!

━━━━━━━━━━━━━━━━━━━━━

💬 Nếu hôm nay bạn bận,
chỉ cần quay lại khi sẵn sàng – mình vẫn ở đây.

🎯 Đã thêm giao dịch đầu tiên?
Click button bên dưới để tiếp tục!
```

**Buttons: 3 buttons** ✅
```
┌───────────────────────────────────────┐
│  ✅ Tôi đã thêm giao dịch đầu tiên    │
├───────────────────────────────────────┤
│  📖 Xem hướng dẫn setup               │
├───────────────────────────────────────┤
│  ❓ Cần hỗ trợ                        │
└───────────────────────────────────────┘
```

**⏰ Timing Check:**
- [ ] Message 4 arrives ~10 minutes after Message 3A
- [ ] NOT immediately (was the v2 bug)

**✨ v2.1 Changes Check:**
- [ ] Title says "BƯỚC ĐẦU TIÊN" (NOT "Day 1")
- [ ] NO 🎉 emoji at the start (professional tone)
- [ ] "Cho phép làm chậm" copy present: "💬 Nếu hôm nay bạn bận..."
- [ ] Only 3 buttons (NOT 5)
- [ ] No Notion/Group links in buttons (moved to submenu)

---

## 🔍 INTERACTIVE FLOW TESTS

### **TEST A: Click "Tôi đã tạo xong" (from Message 3B)**

**Expected:**
- Congratulations message
- Next steps (add transaction, explore 6 Jars, dashboard)
- 4 buttons (various options)

---

### **TEST B: Click "Xem hướng dẫn 3 bước" (from Message 3B)**

**Expected:**
- 4 images sent sequentially (2s delay each)
- Step 1: Copy template
- Step 2: Apps Script
- Step 3: Deploy
- Step 4: Completion with 4 buttons

---

### **TEST C: Click "❓ Cần hỗ trợ" (from Message 4)** ⭐ NEW

**Expected - Support Submenu:**
```
❓ CẦN HỖ TRỢ?

Không sao cả! Mình ở đây để giúp bạn.

━━━━━━━━━━━━━━━━━━━━━

Bạn có thể:

📖 Xem hướng dẫn chi tiết (có ảnh từng bước)
💬 Hỏi trong Group VIP (community rất nhiệt tình)
📞 Nhắn Admin (hỗ trợ 1-1)

━━━━━━━━━━━━━━━━━━━━━

⏰ Thời gian hỗ trợ:
• Thứ 2-6: 9h-21h
• Thứ 7-CN: 10h-18h

💬 Hoặc gõ trực tiếp câu hỏi để mình trả lời nhé!
```

**Buttons:**
```
┌───────────────────────────────────────┐
│  📖 Hướng dẫn chi tiết (Notion)       │ → Opens link
├───────────────────────────────────────┤
│  💬 Group VIP                         │ → Opens link
├───────────────────────────────────────┤
│  📞 Liên hệ Admin                     │ → Opens DM
├───────────────────────────────────────┤
│  🔙 Quay lại                          │
└───────────────────────────────────────┘
```

**✨ Check:**
- [ ] Notion + Group links now in submenu (not main message)
- [ ] Soft tone: "Không sao cả!"
- [ ] Clear support options

---

## 📊 CHECKLIST - v2.1 VERIFICATION

### Psychology Checks

- [ ] **No timeline pressure:** "BƯỚC ĐẦU TIÊN" vs "Day 1"
- [ ] **Comeback permission:** "Nếu hôm nay bạn bận, quay lại khi sẵn sàng" present
- [ ] **Clear hierarchy:** 3 buttons (not 5) reduces decision fatigue
- [ ] **Identity anchor:** "VIP là người..." in Message 2
- [ ] **Staged disclosure:** 3A (benefits) → 3B (action) separated

### Technical Checks

- [ ] **Timing:** Message 4 delayed 10 minutes (not instant)
- [ ] **Buttons:** Message 4 has exactly 3 buttons
- [ ] **Links:** External links (Notion, Group) in submenu only
- [ ] **Emojis:** Reduced 🎉 usage in Message 4
- [ ] **Callbacks:** All buttons functional (onboard_complete_1, webapp_setup_guide, onboard_help_1)

### Flow Checks

- [ ] **Message sequence:** 1 → 2 → 3A → [user clicks] → 3B → [10min] → 4
- [ ] **Edit behavior:** 3A → 3B uses edit_message_text (not new message)
- [ ] **Support submenu:** Works and shows 4 options
- [ ] **Image sending:** 4 images in "Hướng dẫn 3 bước" work
- [ ] **No errors:** Check bot terminal for any exceptions

---

## 🐛 DEBUGGING

If issues occur:

### Check Bot Logs
```powershell
# In PowerShell (terminal already open)
# View real-time logs from bot terminal
```

### Common Issues

**Issue:** Message 4 arrives immediately (not 10 min delay)
- **Check:** `initial_delay_minutes=10` in registration.py
- **File:** bot/handlers/registration.py line ~355

**Issue:** 5 buttons instead of 3 in Message 4
- **Check:** onboarding.py ONBOARDING_MESSAGES[1]["buttons"]
- **File:** bot/handlers/onboarding.py line ~50

**Issue:** "Day 1" still showing
- **Check:** Title in ONBOARDING_MESSAGES[1]["title"]
- **File:** bot/handlers/onboarding.py line ~19

**Issue:** "Cho phép làm chậm" copy missing
- **Check:** Content in ONBOARDING_MESSAGES[1]["content"]
- **File:** bot/handlers/onboarding.py line ~20-55

---

## 🎯 EXPECTED OUTCOMES

### Success Criteria v2.1

✅ **User Experience:**
- Feels less pressure ("BƯỚC ĐẦU TIÊN" vs "Day 1")
- Has permission to delay ("quay lại khi sẵn sàng")
- Fewer decisions at critical moment (3 buttons)
- Clear support path (submenu)

✅ **Technical:**
- All messages arrive in correct order
- Timing delays work (1s, 2s, 10m)
- Buttons trigger correct callbacks
- Images load properly

✅ **Psychology:**
- Identity anchor creates commitment
- Staged disclosure reduces overwhelm
- "Cho phép làm chậm" reduces guilt
- Button reduction improves focus

---

## 📝 TEST NOTES

**Date:** February 8, 2026  
**Version:** v2.1  
**Commit:** 9a3ad90  

**Test Results:**
```
[ ] Message 1: Image + Caption ✅
[ ] Message 2: VIP + Identity ✅
[ ] Message 3A: Benefits + 1 button ✅
[ ] Message 3B: Action + 2 buttons ✅
[ ] Message 4: Bước đầu tiên + 3 buttons ✅
[ ] Timing: 10-minute delay ✅
[ ] Support submenu: Works ✅
[ ] Overall flow: Smooth ✅
```

**Issues Found:**
```
(List any bugs or unexpected behavior)
```

**User Feedback:**
```
(Note impressions about pressure, clarity, button count)
```

---

## 🚀 NEXT AFTER TEST

If v2.1 passes all checks:

1. ✅ **Document results** in this file
2. 🚀 **Deploy to Railway** (production)
3. 📊 **Monitor first 50 VIP unlocks**
4. 📝 **Collect feedback** from real users
5. 🧪 **Start A/B test #1** (Button Copy) after 100 users

---

**Bot URL:** https://t.me/FreedomWalletbot  
**GitHub:** https://github.com/mettatuan/freedom-wallet-bot  
**Docs:** VIP_UNLOCK_SCENARIO.md, AB_TEST_PLAN.md  

**Ready to test? Start with STEP 1!** 🚀
