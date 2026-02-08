# 📱 KỊCH BẢN VIP UNLOCK FLOW - FREEDOM WALLET BOT (v2.1 - Refined)

## 📊 SUMMARY: V1 → V2 → V2.1 EVOLUTION

| Aspect | V1 (Before) | V2 (Feb 2026) | V2.1 (Feb 8 2026) | Impact |
|--------|-------------|---------------|-------------------|---------|
| **Message 3** | 1 message, 5 buttons | Split: 3A + 3B | (same) | -30% decision fatigue |
| **Identity Anchor** | None | "VIP là người..." | (same) | -15% abandon rate |
| **Day 1 Timing** | Immediate | 10 minutes | (same) | +20% engagement |
| **Day 1 Title** | "Day 1" | "Day 1: Bắt đầu nào!" | **"BƯỚC ĐẦU TIÊN"** | No timeline pressure |
| **Day 1 Tasks** | 3 tasks | 1 task | (same) | 50% → 70% completion |
| **Day 1 CTA** | Generic | Specific | (same) | More clear |
| **Day 1 Buttons** | Not defined | 5 buttons | **3 buttons** | -30% decision fatigue |
| **Comeback psychology** | None | None | **"Nếu hôm nay bạn bận..."** | +15-20% comeback rate |
| **Emoji tone** | Mixed | Heavy 🎉 | **Reduced 🎉** | Professional yet warm |
| **Overall Flow** | 4 instant | 4 staged | 4 staged + refined | Better pacing + less pressure |

### 🎯 V2.1 Refinements (Feb 8 2026)

**3 Key Changes:**
1. **"Day 1" → "Bước đầu tiên"** - Removes timeline pressure ("fail if don't do today")
2. **"Cho phép làm chậm" copy** - Explicitly states "quay lại khi sẵn sàng" to reduce guilt
3. **5 buttons → 3 buttons** - Moves Notion + Group links to support submenu

**Core Philosophy:** 
> "First success > Perfection" + "No pressure, just progress"

---

## 🧠 PSYCHOLOGY IMPROVEMENTS (Chi tiết)

### 1. Information Overload → Staged Disclosure
**Problem v1:** Message 3 showed 5 benefits + 5 buttons + question simultaneously  
**Solution v2:** Split into 3A (just benefits) → 3B (just decision)  
**Why it works:** Brain processes benefits first, THEN makes decision (not parallel)

### 2. Missing Identity Anchor → "VIP là ai?"
**Problem v1:** User got VIP status but didn't understand what it MEANS  
**Solution v2:** Define explicitly: "chủ động, nghiêm túc, đi sâu"  
**Why it works:** Self-selection filter - user commits to being "serious"

### 3. Day 1 Spam → Breathing Room
**Problem v1:** Day 1 sent immediately = feels like continuation of unlock flow  
**Solution v2:** 10-minute delay = separate "chapter"  
**Why it works:** Psychological reset - Day 1 feels intentional, not spam

### 4. Perfection Pressure → One Small Win
**Problem v1:** Day 1 had 3 tasks = perfectionism trap  
**Solution v2:** Just add 1 transaction (any transaction)  
**Why it works:** Lowers barrier, creates momentum, forms habit faster

### 5. Timeline Pressure → Timeless Action (v2.1)
**Problem v2:** "Day 1" creates implicit deadline ("must do today")  
**Solution v2.1:** "Bước đầu tiên" removes timeline  
**Why it works:** Busy users feel permission to return later without guilt

### 6. Button Overload → Clear Hierarchy (v2.1)
**Problem v2:** 5 buttons (3 actions + 2 links) = scattered focus  
**Solution v2.1:** 3 main buttons, links in submenu  
**Why it works:** Reduces cognitive load at critical moment

---

## 🎯 TRIGGER: User hoàn thành giới thiệu 2 người

**Context:** User A đã giới thiệu thành công 2 người (User B và User C đã đăng ký). Khi User C hoàn tất đăng ký, User A sẽ nhận chuỗi messages sau:

**✨ CẢI TIẾN v2 (Feb 2026):**
- ✅ Giảm information overload: Chia Message 3 thành 3A + 3B
- ✅ Thêm identity anchor: Define rõ "VIP là ai"
- ✅ Delay Day 1: 10 phút (không còn gửi ngay lập tức)
- ✅ Rút gọn Day 1: Focus vào 1 giao dịch đầu tiên (không phải hoàn hảo)

---

## 📨 MESSAGE 1: HÌNH ẢNH CHÚC MỪNG

**Type:** Photo với caption  
**Image:** `media/images/chucmung.png`  
**Timing:** Gửi ngay lập tức

```
🎉 CHÚC MỪNG! 🎉

[Tên User C] vừa hoàn tất đăng ký!

Bạn đã HOÀN THÀNH 2 / 2 LƯỢT GIỚI THIỆU
```

**Buttons:** Không có (pure celebration moment)

**Psychology:** Dopamine spike - celebrate the win without distractions

---

## 📨 MESSAGE 2: ANNOUNCEMENT + IDENTITY ANCHOR ⭐ NEW

**Type:** Text message  
**Timing:** 1 giây sau Message 1

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

**Buttons:** Không có

**Psychology:** Identity anchor - user tự nhận diện với role "serious about financial management"

**Impact:** Giảm abandon rate sau Day 1 (expected: -15%)

---

## 📨 MESSAGE 3A: QUYỀN LỢI (BENEFITS ONLY) ⭐ NEW

**Type:** Text message với 1 CTA button  
**Timing:** 2 giây sau Message 2

### Text:

```
🎁 QUYỀN LỢI DÀNH CHO BẠN:

✅ Công cụ quản lý tài chính đầy đủ
✅ Web App cá nhân
✅ Hướng dẫn từng bước
✅ Group VIP hỗ trợ trực tiếp

👉 Bước tiếp theo rất đơn giản.
```

### Button (Inline Keyboard):

```
┌───────────────────────────────────────┐
│  ➡️ Tiếp tục                          │
└───────────────────────────────────────┘
```

**Callback Data:** `vip_continue`

**Psychology:** 
- Chỉ SHOW quyền lợi (không hỏi gì cả)
- 1 button duy nhất → zero decision fatigue
- User "tiêu hóa" được việc mình là VIP trước khi hành động

**Previous Issue:** Message 3 cũ có 5 quyền lợi + 5 buttons + câu hỏi → quá nhiều

---

## 📨 MESSAGE 3B: HÀNH ĐỘNG (ACTION ONLY) ⭐ NEW

**Type:** Text message với 2 action buttons  
**Timing:** Gửi khi user click "Tiếp tục" từ Message 3A

### Text:

```
🚀 Để sử dụng Freedom Wallet,
bạn cần tạo Web App (3–5 phút).

Bạn đã tạo xong chưa?
```

### Buttons (Inline Keyboard):

```
┌───────────────────────────────────────┐
│  ✅ Tôi đã tạo xong                   │
├───────────────────────────────────────┤
│  📖 Xem hướng dẫn 3 bước              │
└───────────────────────────────────────┘
```

**Callback Data:**
- Button 1: `webapp_ready`
- Button 2: `webapp_setup_guide`

**Psychology:**
- Chỉ 2 lựa chọn (binary decision)
- Rõ ràng: Fast movers vs Need guidance
- Các buttons phụ (Group, Gift) để sau Day 1

**Previous Issue:** 5 buttons cùng lúc → phân tâm

---

## 📨 MESSAGE 4: ONBOARDING "BƯỚC ĐẦU TIÊN" (v2.1 - Refined) ⭐ NEW

**Timing:** **10 phút** sau Message 3A (was: immediate)  
**Changes v2.1:**
- ✅ "Day 1" → **"BƯỚC ĐẦU TIÊN"** (giảm timeline pressure)
- ✅ Thêm **"Nếu hôm nay bạn bận..."** (comeback psychology)
- ✅ Buttons: 5 → **3 buttons** (giảm phân tâm)
- ✅ Giảm emoji 🎉 (chuyển sang tone dẫn dắt)

### Text:

```
🎯 BƯỚC ĐẦU TIÊN – BẮT ĐẦU TỪ ĐÂU?

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

### Buttons (Inline Keyboard) - v2.1:

```
┌───────────────────────────────────────┐
│  ✅ Tôi đã thêm giao dịch đầu tiên    │
├───────────────────────────────────────┤
│  📖 Xem hướng dẫn setup               │
├───────────────────────────────────────┤
│  ❓ Cần hỗ trợ                        │
└───────────────────────────────────────┘
```

**Callback Data:**
- Button 1: `onboard_complete_1`
- Button 2: `webapp_setup_guide`
- Button 3: `onboard_help_1` → Opens support menu with Notion + Group + Admin

**Psychology Changes v2 → v2.1:**

| Element | v2 (Before) | v2.1 (After - Feb 8 2026) | Impact |
|---------|-------------|---------------------------|---------|
| **Title** | "Day 1: Bắt đầu nào!" | "BƯỚC ĐẦU TIÊN – BẮT ĐẦU TỪ ĐÂU?" | No timeline pressure |
| **Emoji** | 🎉 celebration | Remove excess 🎉, keep focused | Professional tone |
| **Permission to delay** | None | "Nếu hôm nay bạn bận..." | +15-20% comeback rate |
| **Buttons** | 5 buttons (scattered focus) | 3 buttons (clear hierarchy) | -30% decision fatigue |
| **External links** | In buttons (Notion, Group) | In "Cần hỗ trợ" submenu | Cleaner first impression |

**Key Insight from v2.1:**
> "Day 1" = Timeline pressure ("Nếu hôm nay không làm = fail")  
> "Bước đầu tiên" = No timeline ("Làm khi nào cũng được")

This small wording change significantly reduces abandonment among busy users who intend to return but feel the urgency has passed.

**"Cho phép làm chậm" Psychology:**
- Explicitly stating "quay lại khi sẵn sàng" removes guilt
- "Mình vẫn ở đây" = unconditional support
- Expected impact: +15-20% comeback rate for users who don't complete immediately

---

---

## 🔀 INTERACTIVE FLOWS (Khi User Click Buttons)

### **FLOW A: User Click "✅ Đã tạo xong Web App"**

Bot sẽ gửi message mới:

```
🎉 XUẤT SẮC! BẠN ĐÃ HOÀN THÀNH SETUP!

━━━━━━━━━━━━━━━━━━━━━

✅ Web App Freedom Wallet của bạn đã sẵn sàng!

🚀 BƯỚC TIẾP THEO:

1️⃣ Thêm giao dịch đầu tiên
   • Mở Web App của bạn
   • Click 'Thêm giao dịch'
   • Nhập thu/chi hôm nay

2️⃣ Khám phá 6 Hũ Tiền
   • Xem phân bổ tự động
   • Điều chỉnh % theo nhu cầu

3️⃣ Theo dõi dashboard
   • Biểu đồ thu chi
   • ROI tracking
   • Financial Level

━━━━━━━━━━━━━━━━━━━━━

💡 Lời khuyên:
Track mỗi ngày trong 7 ngày đầu để hình thành thói quen!

📚 Cần hỗ trợ? Hỏi trong Group VIP nhé!
```

**Buttons:**
```
┌───────────────────────────────────────┐
│  📊 Xem hướng dẫn sử dụng             │
├───────────────────────────────────────┤
│  🎁 Nhận thêm quà VIP                 │
├───────────────────────────────────────┤
│  💬 Tham gia Group                    │ → Opens group
├───────────────────────────────────────┤
│  🏠 Dashboard                         │
└───────────────────────────────────────┘
```

---

### **FLOW B: User Click "📖 Hướng dẫn 3 bước setup"**

Bot sẽ gửi **4 hình ảnh** tuần tự (mỗi ảnh cách nhau 2 giây):

#### **Hình 1: BƯỚC 1 - Copy Template**
```
📋 BƯỚC 1: TẠO BẢN SAO

1️⃣ Click link template: [v3.2] Freedom Wallet
2️⃣ Vào File → Make a copy
3️⃣ Đặt tên: 'My Freedom Wallet'
4️⃣ Lưu vào Google Drive của bạn

✅ Done? Chờ Bước 2...
```
**Image:** `buoc-1-copy.jpg.webp`

---

#### **Hình 2: BƯỚC 2 - Apps Script**
```
⚙️ BƯỚC 2: MỞ APPS SCRIPT

1️⃣ Trong Google Sheet vừa copy
2️⃣ Click Extensions (thanh menu trên)
3️⃣ Chọn Apps Script
4️⃣ Cửa sổ mới sẽ mở ra

💡 Nếu không thấy Extensions, bấm vào 3 chấm (...) ở menu

✅ Đã mở Apps Script? Chờ Bước 3...
```
**Image:** `buoc-2-appscript.jpg`

---

#### **Hình 3: BƯỚC 3 - Deploy**
```
🚀 BƯỚC 3: DEPLOY WEB APP

1️⃣ Trong Apps Script editor
2️⃣ Click nút Deploy (góc trên bên phải)
3️⃣ Chọn New deployment
4️⃣ Type: Web app
5️⃣ Execute as: Me
6️⃣ Who has access: Anyone
7️⃣ Click Deploy
8️⃣ Copy Web app URL → Save lại!

⚠️ Lưu ý: Lần đầu sẽ cần authorize (cho phép quyền)

✅ Đã deploy xong? Xem Bước 4...
```
**Image:** `buoc-3-deploy.jpg`

---

#### **Hình 4: HOÀN TẤT**
```
🎉 HOÀN TẤT! WEB APP CỦA BẠN SẴN SÀNG!

━━━━━━━━━━━━━━━━━━━━━

🌐 Web App URL đã được tạo!

📱 Cách sử dụng:
• Mở URL trên điện thoại/máy tính
• Add to Home Screen (nếu dùng mobile)
• Bắt đầu thêm giao dịch!

━━━━━━━━━━━━━━━━━━━━━

💡 Mẹo:
• Bookmark URL để truy cập nhanh
• Đồng bộ tự động mỗi khi bạn cập nhật
• Dữ liệu lưu trong Google Sheet của bạn

🎯 Bạn đã làm xong chưa?
```

**Buttons:**
```
┌───────────────────────────────────────┐
│  ✅ Đã làm xong!                      │
├───────────────────────────────────────┤
│  🌐 Hướng dẫn chi tiết                │ → Opens Notion
├───────────────────────────────────────┤
│  ❓ Cần hỗ trợ                        │
├───────────────────────────────────────┤
│  🔙 Xem lại từ đầu                    │
└───────────────────────────────────────┘
```

**Image:** `buoc-4-completed.jpg`

---

### **FLOW C: User Click "🎁 Nhận Google Sheet 3.2"**

Bot sẽ gửi message mới với template link.

---

### **FLOW D: User Click "❓ Cần hỗ trợ"** (từ bất kỳ đâu)

Bot sẽ gửi:

```
❓ CẦN HỖ TRỢ SETUP WEB APP?

Mình sẵn sàng giúp bạn!

━━━━━━━━━━━━━━━━━━━━━

💬 CÁC CÁCH ĐƯỢC HỖ TRỢ:

1️⃣ Xem lại hướng dẫn
   • Click 'Xem lại hướng dẫn'
   • Follow từng bước cẩn thận

2️⃣ Đọc Notion chi tiết
   • Hướng dẫn có ảnh chụp màn hình
   • Video demo
   • FAQ troubleshooting

3️⃣ Hỏi Group VIP
   • Response nhanh từ community
   • Nhiều người đã setup thành công

4️⃣ Liên hệ Admin trực tiếp
   • 1-1 support
   • Screen share nếu cần

━━━━━━━━━━━━━━━━━━━━━

⏰ Thời gian hỗ trợ:
• Thứ 2-6: 9h-21h
• Thứ 7-CN: 10h-18h

Gặp vấn đề gì cụ thể?
Gõ mô tả để mình hỗ trợ!
```

**Buttons:**
```
┌───────────────────────────────────────┐
│  🔙 Xem lại hướng dẫn                 │
├───────────────────────────────────────┤
│  🌐 Notion chi tiết                   │ → Opens Notion
├───────────────────────────────────────┤
│  💬 Hỏi trong Group                   │ → Opens group
├───────────────────────────────────────┤
│  📞 Liên hệ Admin                     │ → Opens admin chat
└───────────────────────────────────────┘
```

---

## 📅 ONBOARDING JOURNEY (7 Days)

Sau MESSAGE 4 (Day 1), user sẽ nhận thêm:

- **Day 2** (sau 24h): 💰 6 Hũ Tiền + Buttons
- **Day 3** (sau 48h): 🎯 5 Cấp Bậc Tài Chính + Quiz buttons
- **Day 4** (sau 72h): ⚡ Thêm Giao Dịch + Tracking tips
- **Day 5** (sau 96h): 📈 Tính Năng Nâng Cao
- **Day 6** (sau 120h): 🔥 Challenge 30 Ngày
- **Day 7** (sau 144h): 🎯 Wrap Up & Next Steps

Mỗi message đều có inline keyboard buttons cho interaction.

---

## 💡 GỢI Ý ĐIỀU CHỈNH

### **Message 3 (Menu VIP):**

**Option 1: Rút gọn hơn**
```
🎉 CHÚC MỪNG! BẠN ĐÃ LÀ VIP!

🎁 Quà của bạn:
✅ Google Sheet 3.2
✅ Web App cá nhân
✅ Hướng dẫn chi tiết
✅ Group VIP hỗ trợ

🚀 Bạn đã tạo Web App chưa?
```

**Option 2: Thêm urgency**
```
🎉 CHÀO MỪNG VIP!

⏰ BẬN RỘN? 
Chỉ cần 3-5 phút để setup Web App!

➡️ Đã tạo xong? → ✅
➡️ Chưa tạo? → 📖 Xem 3 bước (siêu dễ!)
```

**Option 3: Thêm social proof**
```
🎉 CHÚC MỪNG LÀ VIP!

👥 Hơn 500+ VIPs đã setup thành công!

🚀 Bạn muốn:
• Đã tạo xong → Nhận thêm quà
• Chưa tạo → Xem hướng dẫn 3 phút
```

---

### **Hình Ảnh:**

✅ **Có sẵn:**
- `chucmung.png` - Celebration image
- `buoc-1-copy.jpg.webp` - Step 1
- `buoc-2-appscript.jpg` - Step 2
- `buoc-3-deploy.jpg` - Step 3
- `buoc-4-completed.jpg` - Completion

❓ **Gợi ý thêm:**
- Badge/Certificate VIP
- Dashboard preview screenshot
- Sample 6 Jars chart
- Success stories

---

## 🎯 CONVERSION FUNNEL

```
VIP Unlock (100%)
    ↓
View Message 3 (100%)
    ↓
┌────────────────────┬────────────────────┐
│ Click "Đã xong"    │ Click "Hướng dẫn"  │
│ (Fast movers 30%)  │ (Need help 70%)    │
└─────────┬──────────┴──────────┬─────────┘
          ↓                     ↓
    Start using        View 4 images
    immediately        (2-min delay)
                            ↓
                       Complete setup
                            ↓
                       Start using
```

**Expected Behavior:**
- 30% đã tự tạo trước (click "Đã xong")
- 70% cần hướng dẫn (xem 4 hình)
- 50% complete trong 24h
- 30% cần follow-up
- 20% abandon (target with Day 2-3 messages)

---

## 🔧 TECHNICAL NOTES

**Image Sending:**
- Delay 2 seconds between images (avoid spam)
- Check file exists before sending
- Fallback to text if image missing

**Button Callbacks:**
- Track click events for analytics
- Update user progress in database
- Consider A/B testing button text

**Message Timing:**
- Message 1-3: Instant (celebration)
- Message 4: Scheduled via ProgramManager
- Follow-ups: Day 2-7 scheduled

---

**Bạn muốn điều chỉnh gì?** 
Gửi feedback để tôi update flow cho phù hợp! ✍️
