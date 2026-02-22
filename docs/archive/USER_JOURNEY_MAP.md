# 🗺️ FREEDOM WALLET - USER JOURNEY MAP

**Visual flow của user từ lúc mới đến → Setup xong → Sử dụng**

---

## 🎯 JOURNEY OVERVIEW

```
NEW USER
   ↓
[REGISTRATION]
   ↓
[WEB APP SETUP - 6 Steps]
   ↓
[SETUP GUIDE]
   ↓
[ACTIVE USER - Main Menu]
```

---

## 📍 STAGE 1: NEW USER → REGISTERED

### **Entry Points:**

```
1. Direct Start
   /start
   ↓
   Welcome message
   ↓
   Start Registration

2. Referral Link
   /start REF{code}
   ↓
   Special welcome
   ↓
   Notify referrer
   ↓
   Start Registration

3. Web Registration
   /start WEB_{hash}
   ↓
   Sync from Google Sheets
   ↓
   Link Telegram to Web account
```

### **Registration Flow:**

```
┌────────────────────────────────────────┐
│  /start (first time)                   │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│  Welcome Message                       │
│  "Freedom Wallet là hệ thống..."       │
│                                        │
│  [🎁 Đăng ký FREE]                     │
│  [💎 Đăng ký PREMIUM]                  │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│  ConversationHandler: Registration     │
│  ├─ Ask: Full Name                     │
│  ├─ Ask: Phone                         │
│  ├─ Ask: Email                         │
│  └─ Confirm & Save                     │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│  ✅ "Cảm ơn bạn!"                       │
│  "Thông tin đã được lưu lại."          │
└────────────────────────────────────────┘
              ↓
              Wait 1.5s
              ↓
┌────────────────────────────────────────┐
│  📸 hu_tien.jpg image                  │
│                                        │
│  "Khi bạn cài đặt và sử dụng           │
│  Freedom Wallet, bạn không chỉ         │
│  dùng một ứng dụng..."                 │
│                                        │
│  "Bạn sẵn sàng tạo hệ thống            │
│  của riêng mình chưa?"                 │
│                                        │
│  [📋 Tạo Google Sheet]                 │
│  [❓ Hỏi thêm]                          │
└────────────────────────────────────────┘
              ↓ (Click "Tạo Google Sheet")
        [STAGE 2: WEB APP SETUP]
```

---

## 📍 STAGE 2: WEB APP SETUP (6 Steps)

### **Entry:**
- Callback: `free_step3_copy_template`
- Redirects to: `webapp_step_1`

### **Full Setup Flow:**

```
Step 0: Introduction (Optional)
┌────────────────────────────────────────┐
│  🎯 TẠO HỆ THỐNG TÀI CHÍNH CÁ NHÂN     │
│                                        │
│  "Bạn sắp tạo..."                      │
│                                        │
│  [Bắt đầu ➡️]                          │
│  [💬 Cần trợ giúp?]                    │
└────────────────────────────────────────┘
              ↓

Step 1: Copy Template ⭐ Main Entry Point
┌────────────────────────────────────────┐
│  📋 BƯỚC 1: SAO CHÉP TEMPLATE          │
│                                        │
│  📸 IMAGE: make-copy.png               │
│                                        │
│  Instructions:                         │
│  "1. Click link dưới đây               │
│   2. Click "Make a copy"               │
│   3. Template → Drive của bạn"         │
│                                        │
│  [📋 Copy Template Link] ← Special     │
│                                        │
│  [Tiếp theo ➡️]                        │
│  [💬 Cần trợ giúp?]                    │
└────────────────────────────────────────┘
              ↓

Step 2: Apps Script
┌────────────────────────────────────────┐
│  ⚙️ BƯỚC 2: BẬT APPS SCRIPT            │
│                                        │
│  📸 IMAGE: app-script.png              │
│                                        │
│  "1. Mở Sheet vừa copy                 │
│   2. Extensions > Apps Script          │
│   3. Paste code..."                    │
│                                        │
│  [⬅️ Quay lại]  [Tiếp theo ➡️]         │
│  [💬 Cần trợ giúp?]                    │
└────────────────────────────────────────┘
              ↓

Step 3: Deploy
┌────────────────────────────────────────┐
│  🚀 BƯỚC 3: DEPLOY WEB APP             │
│                                        │
│  📸 IMAGE: deploy-app.png              │
│                                        │
│  "1. Click Deploy > New deployment     │
│   2. Type: Web app                     │
│   3. Who has access: Anyone            │
│   4. Click Deploy                      │
│   5. Copy Web App URL"                 │
│                                        │
│  ⚠️ KHÔNG authorize ở đây!             │
│  (Sẽ authorize ở bước tiếp theo)       │
│                                        │
│  [⬅️ Quay lại]  [Tiếp theo ➡️]         │
│  [💬 Cần trợ giúp?]                    │
└────────────────────────────────────────┘
              ↓

Step 4: Login & Authorize ⭐ NEW!
┌────────────────────────────────────────┐
│  🔐 BƯỚC 4: MỞ WEB APP & ĐĂNG NHẬP     │
│                                        │
│  📸 IMAGE: use-deploy-app.png          │
│                                        │
│  📋 CÁCH LÀM:                          │
│                                        │
│  1️⃣ Mở Web App URL (vừa copy Bước 3)  │
│                                        │
│  2️⃣ Authorize lần đầu:                │
│                                        │
│  → Popup "Authorization required"      │
│  → Click "Authorize access"            │
│  → Chọn tài khoản Google               │
│  → Thấy "Google hasn't verified..."    │
│  → Click "Advanced" (Nâng cao)         │
│  → Click "Go to [Project] (unsafe)"    │
│  → Click "Allow" (Cho phép)            │
│                                        │
│  ━━━━━━━━━━━━━━━━━━━━                │
│                                        │
│  ✅ KẾT QUẢ:                           │
│  • Web App mở thành công               │
│  • Đã có quyền truy cập Sheets         │
│  • Sẵn sàng sử dụng!                   │
│                                        │
│  ━━━━━━━━━━━━━━━━━━━━                │
│                                        │
│  ❓ TẠI SAO "UNSAFE"?                  │
│                                        │
│  Không sao! Đây là app CỦA BẠN:        │
│  • Bạn tự tạo                          │
│  • Dữ liệu trong Drive của bạn         │
│  • Google chỉ cảnh báo vì chưa verify  │
│  • 100% an toàn!                       │
│                                        │
│  ━━━━━━━━━━━━━━━━━━━━                │
│                                        │
│  💡 Sau lần đầu → không authorize lại! │
│                                        │
│  [⬅️ Quay lại]  [Tiếp theo ➡️]         │
│  [💬 Cần trợ giúp?]                    │
└────────────────────────────────────────┘
              ↓

Step 5: Completion
┌────────────────────────────────────────┐
│  ✅ HOÀN TẤT!                          │
│                                        │
│  "Chúc mừng! Bạn đã tạo xong           │
│  hệ thống tài chính cá nhân."          │
│                                        │
│  "Tiếp theo: Học cách sử dụng"         │
│                                        │
│  [📘 Tiếp theo: Hướng dẫn sử dụng ➡️]  │
│  [💬 Cần trợ giúp?]                    │
└────────────────────────────────────────┘
              ↓ (Click "Hướng dẫn sử dụng")
        [STAGE 3: SETUP GUIDE]
```

### **Technical Details:**

**File:** `bot/handlers/webapp_setup.py`

**Callback Pattern:**
- `webapp_step_0` → Step 0
- `webapp_step_1` → Step 1 ⭐ Entry
- `webapp_step_2` → Step 2
- `webapp_step_3` → Step 3
- `webapp_step_4` → Step 4 (NEW)
- `webapp_step_5` → Step 5

**Images:**
- Step 1: `docs/make-copy.png`
- Step 2: `docs/app-script.png`
- Step 3: `docs/deploy-app.png`
- Step 4: `docs/use-deploy-app.png`
- Step 5: None

**Navigation Logic:**
```python
# Previous step (if not step 0)
if current_step > 0:
    [⬅️ Quay lại → webapp_step_{current_step-1}]

# Next step (if not step 5)
if current_step < 5:
    [Tiếp theo ➡️ → webapp_step_{current_step+1}]

# Completion (only step 5)
if current_step == 5:
    [📘 Hướng dẫn sử dụng ➡️ → guide_step_0]

# Help (all steps)
[💬 Cần trợ giúp? → https://t.me/tuanai_mentor]
```

---

## 📍 STAGE 3: SETUP GUIDE

### **Entry:**
- Callback: `guide_step_0` (from webapp_step_5)

### **Expected Flow:**

```
┌────────────────────────────────────────┐
│  📘 HƯỚNG DẪN SỬ DỤNG                  │
│                                        │
│  guide_step_0: Giới thiệu              │
│  guide_step_1: Ghi chi tiêu            │
│  guide_step_2: Xem báo cáo             │
│  guide_step_3: 6 Hũ tiền               │
│  ...                                   │
│                                        │
│  (Need to verify actual structure)     │
└────────────────────────────────────────┘
              ↓
        [STAGE 4: ACTIVE USER]
```

**TODO:**
- [ ] Review setup_guide.py structure
- [ ] Count total steps
- [ ] Verify final callback/end state

---

## 📍 STAGE 4: ACTIVE USER (After Setup Complete)

### **Expected Main Menu:**

```
┌────────────────────────────────────────┐
│  User types /start                     │
│  (after webapp_setup_complete = True)  │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│  🎯 FREEDOM WALLET MENU                │
│                                        │
│  "Xin chào [Name],                     │
│  Bạn đã ghi chi tiêu [X] ngày"         │
│                                        │
│  [💬 Ghi chi tiêu]                     │
│    → quick_record callback             │
│                                        │
│  [📊 Xem tổng quan hôm nay]            │
│    → today_status callback             │
│                                        │
│  [📈 Báo cáo tháng này]                │
│    → monthly_report callback           │
│                                        │
│  [🛠️ Cài đặt & Kết nối Sheet]         │
│    → sheets_setup callback             │
│                                        │
│  [❓ Trợ giúp]                          │
│    → help_menu callback                │
└────────────────────────────────────────┘
```

**Current Status:** ❌ NOT IMPLEMENTED YET

**In start.py (current):**
```python
# FREE tier shows:
welcome_text = f"""
Chào {user.first_name}, tôi là Trợ lý tài chính của bạn
Freedom Wallet không phải một app để bạn tải về.
...

Nếu bạn muốn đăng ký sở hữu hệ thống web app này,
"""
# (Message cut off in current implementation)
```

**TODO:**
- [ ] Add main menu for webapp-complete users
- [ ] Create quick recording flow
- [ ] Implement today_status callback
- [ ] Implement monthly_report callback

---

## 🔄 STATE TRANSITIONS

### **User State Progression:**

```
┌─────────────┐
│   VISITOR   │  New user, no account
└─────────────┘
      ↓ /start + complete registration
┌──────────────┐
│  REGISTERED  │  Has account, not setup webapp
└──────────────┘
      ↓ complete webapp setup (6 steps)
┌──────────────┐
│ SETUP_DONE   │  Web App created, ready to use
└──────────────┘
      ↓ complete setup guide
┌──────────────┐
│    ACTIVE    │  Using the system
└──────────────┘
      ↓ referral_count >= 2 OR manual
┌──────────────┐
│     VIP      │  Unlocked features
└──────────────┘
      ↓ premium subscription
┌──────────────┐
│   PREMIUM    │  All features
└──────────────┘
```

### **Database Fields Needed:**

```python
User:
    id: int
    telegram_id: int
    username: str
    full_name: str
    phone: str
    email: str
    
    # State tracking
    is_registered: bool = False          # ✅ Exists
    subscription_tier: str = "FREE"      # ✅ Exists
    referral_count: int = 0              # ✅ Exists
    webapp_setup_complete: bool = False  # ⚠️ Need to verify/add
    guide_complete: bool = False         # ⚠️ New field needed?
    
    # Usage tracking
    first_record_at: datetime = None     # ⚠️ New field needed?
    last_active_at: datetime = None      # ✅ Exists?
    streak_count: int = 0                # ✅ Exists
    total_records: int = 0               # ⚠️ New field needed?
    
    # Settings
    reminder_enabled: bool = False       # ✅ Exists
```

---

## 🛣️ ALTERNATIVE PATHS

### **1. User Stops Mid-Setup**

```
User at webapp_step_3
    ↓
Closes bot or gets distracted
    ↓
Types /start again
    ↓
❓ What happens?

Options:
A) Resume from step 3 (need to save progress)
B) Start from step 1 again
C) Show menu with "Continue setup" button

Current: Unknown (need to test)
Recommended: Option C
```

**Implementation for Option C:**
```python
# In start.py:
if user.is_registered and not user.webapp_setup_complete:
    # Check if any progress made (optional)
    keyboard = [
        [InlineKeyboardButton("📋 Tiếp tục setup Web App", 
                             callback_data="webapp_step_1")],
        [InlineKeyboardButton("❓ Tôi cần trợ giúp", 
                             callback_data="help_setup")]
    ]
    await update.message.reply_text(
        f"Chào {user.first_name},\n\n"
        f"Bạn đã đăng ký nhưng chưa hoàn tất setup Web App.\n\n"
        f"Setup chỉ mất 5-10 phút.\n"
        f"Sau đó bạn có thể bắt đầu ghi chi tiêu ngay!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
```

### **2. User Completes Setup But Forgets**

```
User completed webapp_setup months ago
    ↓
Forgot how to use
    ↓
Types /start
    ↓
Show main menu WITH reminder:

"Xin chào [Name], lâu không gặp!

Bạn đã setup Web App từ [date].
Sheet vẫn còn trên Drive của bạn.

Bạn muốn làm gì hôm nay?"

[💬 Ghi chi tiêu]
[📊 Xem tổng quan]
[📘 Xem lại hướng dẫn]
[❓ Trợ giúp]
```

---

## 📊 DROP-OFF POINTS (Potential Issues)

### **Where Users Might Get Stuck:**

```
Registration Complete: 100%
    ↓
    ❌ DON'T click "Tạo Google Sheet"
    → Drop: 30%? (need analytics)

Step 1 Started: 70%
    ↓
    ❌ Can't find "Make a copy"
    → Drop: 10%?

Step 2: 60%
    ↓
    ❌ Apps Script confusing
    → Drop: 15%?

Step 3: 45%
    ↓
    ❌ Deploy too technical
    → Drop: 10%?

Step 4: 35% ⭐ NEW STEP
    ↓
    ❌ Scared by "unsafe" warning
    ❌ Can't authorize
    → Drop: 20%? (CRITICAL TO MONITOR)

Step 5 Complete: 15%
    ↓
    ❌ Don't proceed to guide
    → Drop: 5%?

Guide Complete: 10%
    ↓
    ❌ Never actually use Sheet
    → Drop: 50%?

Active User: 5%
```

### **Mitigation Strategies:**

**For Step 4 (Authorize):**
- ✅ Added detailed 7-step guide
- ✅ Added "TẠI SAO UNSAFE?" explanation
- ✅ Reassurance: "100% an toàn!"
- ✅ Visual: use-deploy-app.png image

**For Other Steps:**
- [ ] Add video tutorials
- [ ] Simplify instructions
- [ ] Offer 1-1 support (@tuanai_mentor)
- [ ] Create troubleshooting FAQ

---

## 🎯 CRITICAL SUCCESS FACTORS

### **For Successful User Journey:**

✅ **Clear Next Steps**
- Always show what to do next
- No dead ends
- Progress indicator (1/6, 2/6, etc.)

✅ **Visual Guidance**
- Screenshots for each step
- Highlight important buttons
- Show exact UI elements to click

✅ **Reassurance**
- "This is normal"
- "You're on the right track"
- "Only X more steps"

✅ **Easy Help Access**
- Help button on every step
- Direct link to support (@tuanai_mentor)
- FAQ for common issues

✅ **Save Progress**
- Don't lose user's place
- Can resume if interrupted
- No need to redo completed steps

---

## 🚀 RECOMMENDED IMPROVEMENTS

### **Priority 1 (High Impact):**

1. **Add Progress Indicator**
   ```
   Current: "📋 BƯỚC 1: SAO CHÉP TEMPLATE"
   Better:  "📋 BƯỚC 1/6: SAO CHÉP TEMPLATE"
              [●●○○○○] 33%
   ```

2. **Save Setup Progress**
   ```python
   user.webapp_setup_current_step = 3
   user.webapp_setup_started_at = datetime.now()
   ```

3. **Main Menu After Setup**
   - Clear menu with primary actions
   - Quick access to recording
   - Help always available

### **Priority 2 (Better UX):**

4. **Video Tutorials**
   - 1-minute video for each step
   - Hosted on YouTube
   - Embedded or linked in bot

5. **Estimated Time**
   ```
   "⏱️ Bước này mất ~2 phút"
   ```

6. **Success Confirmation**
   ```
   After each step:
   "✅ Tuyệt! Bạn đã hoàn thành Bước X"
   ```

### **Priority 3 (Analytics):**

7. **Track Drop-offs**
   ```python
   # Log analytics events:
   - webapp_step_1_started
   - webapp_step_1_completed
   - webapp_step_2_started
   - webapp_step_4_dropped (if >5min no progress)
   ```

8. **Time Tracking**
   ```python
   user.webapp_setup_duration = timedelta(...)
   # Average time per step
   # Identify slow steps
   ```

---

## 📝 TESTING SCENARIOS

### **Scenario 1: Happy Path**
```
New user → Register → Setup 6 steps → Guide → First record
Expected: Smooth flow, max 20 minutes
Test date: [Pending]
Result: [Pending]
```

### **Scenario 2: Interrupted Setup**
```
User → Register → Step 3 → Close bot → /start again
Expected: See "Continue setup" button
Test date: [Pending]
Result: [Pending]
```

### **Scenario 3: Authorization Fails**
```
User → Step 4 → Sees "unsafe" → Scared → Closes
Expected: NO! Guide should prevent this
Test date: [Pending]
Result: [Pending]
```

### **Scenario 4: Returning After Months**
```
User setup 3 months ago → Types /start
Expected: Welcome back + main menu
Test date: [Pending]
Result: [Pending]
```

---

## 📞 SUPPORT ESCALATION

### **If User Gets Stuck:**

```
USER → [💬 Cần trợ giúp?] button
   ↓
Opens @tuanai_mentor chat
   ↓
Bot auto-sends context:
   "User [Name] stuck at Step X
    Issue: [Common issue for this step]
    Link to their Drive: [if available]"
   ↓
Human support helps 1-1
   ↓
Mark issue in analytics
   ↓
Improve step if pattern emerges
```

---

**Last Updated:** 20/02/2026 16:45  
**Purpose:** Visual map for testing and improvement  
**Next Review:** After first 10 users complete flow
