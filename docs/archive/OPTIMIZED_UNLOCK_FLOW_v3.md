# 🧭 OPTIMIZED POST-UNLOCK FLOW v3.0 (Feb 2026)

## 📋 OVERVIEW

**Trigger:** User completes 2 referrals  
**Philosophy:** Ownership-first, Action-driven, Calm confidence  
**Duration:** 3 messages over user-controlled pace

**Key Improvements from v2.1:**
- ✅ Removed "VIP celebration" spam (4 → 3 messages)
- ✅ User-controlled pacing (button-triggered, not time-delayed)
- ✅ Ownership language ("của bạn") not status ("VIP")
- ✅ Identity-based motivation (who you are) not incentive-based
- ✅ Removed information overload (no benefits list, no emoji spam)

---

## 🎯 DESIGN PRINCIPLES

1. **Mỗi message = 1 nhiệm vụ duy nhất**
2. **Không quá 2-3 buttons**
3. **Tạo cảm giác: "Tôi đã vào hệ thống – giờ chỉ cần bắt đầu dùng"**
4. **Ownership framing:** "của bạn", không "được cho"
5. **Identity > Incentive:** làm vì con người mình muốn trở thành
6. **Action-first:** giá trị đến từ dùng, không từ đọc
7. **Calm confidence:** giọng điềm tĩnh, không bán, không hối

---

## 📱 MESSAGE SEQUENCE

### **MESSAGE 1: RECOGNITION & OWNERSHIP**

**Timing:** Immediate (0s) after 2nd referral completes registration  
**Type:** Text message  
**Mục tiêu:** Chuyển trạng thái tâm lý từ "hoàn thành nhiệm vụ xã hội" → "sở hữu công cụ cá nhân"

#### Copy:
```
🎉 Chúc mừng bạn!

Bạn đã hoàn tất mốc 2 người giới thiệu.
Từ đây, Freedom Wallet đã sẵn sàng để bạn sử dụng đầy đủ cho chính mình.

Không phải xem thử.
Không phải làm cho có.

👉 Đây là hệ thống quản lý tài chính cá nhân của bạn.
```

#### Buttons:
```
┌───────────────────────────────────────┐
│  🔓 Tiếp tục                          │
├───────────────────────────────────────┤
│  📊 Xem trạng thái của tôi            │
└───────────────────────────────────────┘
```

**Callback Data:**
- Button 1: `unlock_continue`
- Button 2: `unlock_status`

#### Psychology:
- ✅ **Ghi nhận hành động** → dopamine
- ✅ **Dùng từ "của bạn"** → kích hoạt ownership bias
- ✅ **Không nhắc đến "unlock/free/referral"** → tránh cảm giác giao dịch
- ✅ **3 câu phủ định** → clear away wrong assumptions before stating truth
- ✅ **Short and direct** → mobile-friendly, không quá tải

---

### **MESSAGE 2: IDENTITY + SINGLE NEXT STEP**

**Trigger:** User clicks "🔓 Tiếp tục"  
**Timing:** Immediate (0s)  
**Type:** Text message  
**Mục tiêu:** Định nghĩa "VIP là ai" + dẫn 1 bước duy nhất

#### Copy:
```
Từ thời điểm này, bạn là thành viên VIP của Freedom Wallet.

Thành viên VIP là những người:
• Chủ động quản lý tiền của mình
• Muốn nhìn rõ dòng tiền, không đoán mò
• Sẵn sàng bắt đầu bằng hành động thực tế

Bước tiếp theo rất đơn giản:
👉 Thiết lập Freedom Wallet để bắt đầu sử dụng.
```

#### Buttons:
```
┌───────────────────────────────────────┐
│  🛠 Bắt đầu thiết lập                 │
├───────────────────────────────────────┤
│  🧭 Xem lộ trình cá nhân              │
└───────────────────────────────────────┘
```

**Callback Data:**
- Button 1: `setup_start`
- Button 2: `view_roadmap`

#### Psychology:
- ✅ **Định nghĩa VIP = kiểu người, không phải quyền lợi**
- ✅ **Tạo chuẩn mực hành vi** (identity-based motivation)
- ✅ **Chỉ 1 hành động chính**, không phân tâm
- ✅ **"Sẵn sàng bắt đầu bằng hành động"** → self-selection bias
- ✅ **Peer identity modeling** → "những người..." triggers social comparison

---

### **MESSAGE 3: DAY 1 – FIRST REAL USAGE**

**Trigger:** User clicks "🛠 Bắt đầu thiết lập"  
**Timing:** Immediate (0s)  
**Type:** Text message  
**Mục tiêu:** Tạo first success trong 10-15 phút

#### Copy:
```
🎯 BƯỚC ĐẦU TIÊN – THIẾT LẬP FREEDOM WALLET

Bạn chỉ cần làm 3 việc (10–15 phút):
1️⃣ Copy Google Sheets Template
2️⃣ Tạo Web App cá nhân
3️⃣ Nhập số dư + 1 giao dịch đầu tiên

👉 Không cần biết code.
👉 Làm chậm cũng hoàn toàn ổn.
```

#### Buttons:
```
┌───────────────────────────────────────┐
│  📑 Copy Template                     │
├───────────────────────────────────────┤
│  🌐 Hướng dẫn Web App                 │
├───────────────────────────────────────┤
│  ❓ Cần hỗ trợ                        │
└───────────────────────────────────────┘
```

**Callback Data:**
- Button 1: `copy_template` → Opens Google Sheets template
- Button 2: `webapp_guide` → Opens webapp setup guide
- Button 3: `setup_help` → Opens support menu

#### Psychology:
- ✅ **Giới hạn phạm vi** → giảm cognitive load
- ✅ **"1 giao dịch đầu tiên" = mục tiêu rất thấp** → dễ hoàn thành
- ✅ **Trấn an trước khi user nghi ngờ** khả năng của mình
- ✅ **Numbered list (3 items)** → manageable chunking
- ✅ **Time estimate (10-15 phút)** → sets expectation
- ✅ **"Làm chậm cũng ổn"** → removes time pressure

---

### **MESSAGE 4 (OPTIONAL): GENTLE FOLLOW-UP**

**Trigger:** User hasn't clicked any button after 24 hours  
**Timing:** 24 hours after Message 1  
**Type:** Text message  
**Mục tiêu:** Comeback reminder without pressure

#### Copy:
```
👋 Nhắc nhẹ từ Freedom Wallet

Chỉ cần hoàn thành bước thiết lập đầu tiên,
bạn sẽ bắt đầu thấy dòng tiền của mình rõ ràng hơn.

Khi bạn sẵn sàng, mình ở đây để tiếp tục.
```

#### Button:
```
┌───────────────────────────────────────┐
│  🛠 Tiếp tục thiết lập                │
└───────────────────────────────────────┘
```

**Callback Data:** `setup_start`

#### Psychology:
- ✅ **Không thúc ép, không FOMO**
- ✅ **Cho phép user giữ quyền kiểm soát**
- ✅ **Tăng comeback rate mà không gây phản cảm**
- ✅ **"Khi bạn sẵn sàng"** → user decides timing
- ✅ **"Mình ở đây"** → unconditional support

---

## 🔀 ALTERNATIVE PATHS

### **If user clicks "📊 Xem trạng thái của tôi"** (Message 1)

```
📊 TRẠNG THÁI CỦA BẠN

✅ Đã hoàn tất: 2/2 giới thiệu
✅ Trạng thái: Thành viên VIP
✅ Quyền truy cập: Đầy đủ tính năng

Bước tiếp theo:
👉 Thiết lập Freedom Wallet để sử dụng.
```

**Button:**
```
┌───────────────────────────────────────┐
│  🔓 Bắt đầu ngay                      │
└───────────────────────────────────────┘
```

**Callback:** `unlock_continue` (leads to Message 2)

---

### **If user clicks "🧭 Xem lộ trình cá nhân"** (Message 2)

```
🧭 LỘ TRÌNH CÁ NHÂN

**Hôm nay:**
✓ Thiết lập Web App (10-15 phút)
✓ Nhập giao dịch đầu tiên

**Tuần này:**
• Hiểu về 6 Hũ Tiền
• Theo dõi dòng tiền hàng ngày
• Xem báo cáo chi tiêu

**Tháng này:**
• Xây dựng Quỹ Khẩn Cấp
• Lập kế hoạch tài chính rõ ràng
• Làm chủ tài chính cá nhân

Sẵn sàng bắt đầu?
```

**Button:**
```
┌───────────────────────────────────────┐
│  🛠 Bắt đầu thiết lập                 │
└───────────────────────────────────────┘
```

**Callback:** `setup_start` (leads to Message 3)

---

## 📊 COMPARISON: v2.1 vs v3.0

| Element | v2.1 (Old) | v3.0 (New) | Impact |
|---------|------------|------------|--------|
| **Messages before action** | 4 (celebration + identity + benefits + Day 1) | 3 (recognition → identity → setup) | ↓ 25% noise |
| **Delays** | 1s, 2s, 10min | User-controlled (button-triggered) | ↑ User agency |
| **Benefits showcase** | Full list (5 items + emoji) | Removed | ↓ Information overload |
| **VIP framing** | Status-based ("You unlocked VIP!") | Identity-based ("VIP là những người...") | ↑ Motivation quality |
| **Celebration** | Image + 3 emoji messages | Single text, minimal emoji | ↓ Spam feeling |
| **Call to action** | 5+ buttons at Message 3 | 2-3 buttons max | ↓ Decision fatigue |
| **Setup pressure** | "Day 1" (timeline pressure) | "Bước đầu tiên" (no timeline) | ↑ Comeback rate |
| **Tone** | Excited sales pitch | Calm confidence | ↑ Professional feel |

---

## 🧠 PSYCHOLOGY SUMMARY

### Why this works:

1. **Ownership Bias Activation**
   - "của bạn" appears 3x in Message 1
   - No mention of "unlock" or "free" (transactional language)

2. **Identity-Based Motivation**
   - Defines "VIP" as character traits, not benefits
   - Users act to match self-image, not to get rewards

3. **Incremental Commitment**
   - Each button click = micro-commitment
   - Small yeses lead to big yeses

4. **Calm Authority**
   - No urgency, no FOMO, no pressure
   - Confidence = "You deserve this, use it when ready"

5. **User Control**
   - No time delays (except optional 24h reminder)
   - Buttons trigger next step (not auto-scheduled)
   - "Làm chậm cũng ổn" = explicit permission

---

## 🎯 EXPECTED OUTCOMES

**Metrics to track:**

| Metric | v2.1 Baseline | v3.0 Target | Method |
|--------|---------------|-------------|--------|
| Click "Tiếp tục" rate | 75% | 85% | Message 1 → 2 |
| Click "Bắt đầu thiết lập" | 60% | 75% | Message 2 → 3 |
| Setup completion (7 days) | 30% | 45% | Web App deployed |
| 24h reminder comeback | N/A | 20% | Gentle follow-up |
| User sentiment | Mixed | Positive | Support chat analysis |

**Qualitative improvements:**
- ✅ Less "spam" complaints
- ✅ More "clear direction" feedback
- ✅ Higher perceived professionalism
- ✅ Lower abandonment guilt

---

## 🔧 IMPLEMENTATION NOTES

### Files to modify:
1. `bot/handlers/registration.py` - Update referral completion notification
2. `bot/handlers/onboarding.py` - Replace 7-day journey Day 1
3. `bot/handlers/unlock_callbacks.py` (new) - Handle button callbacks

### Database changes:
- Add `unlock_flow_version` field to User model (track A/B test)
- Add `unlock_step` field (1, 2, 3, or "completed")

### Callback handlers needed:
- `unlock_continue` → Send Message 2
- `unlock_status` → Show status screen
- `setup_start` → Send Message 3
- `view_roadmap` → Show roadmap
- `copy_template` → Open Sheets template
- `webapp_guide` → Send setup guide
- `setup_help` → Open support menu

---

## 🚀 DEPLOYMENT PLAN

### Phase 1: A/B Test (2 weeks)
- 50% users get v2.1 (control)
- 50% users get v3.0 (test)
- Track all metrics above

### Phase 2: Analysis (3 days)
- Statistical significance test
- Qualitative feedback review
- Decision: roll out or iterate

### Phase 3: Full Rollout (if successful)
- Deploy v3.0 to 100% users
- Archive v2.1 as historical reference
- Update documentation

---

**Status:** 📝 Design approved, ready for implementation  
**Created:** Feb 10, 2026  
**Next Review:** After 100 unlocks (~2-3 weeks)
