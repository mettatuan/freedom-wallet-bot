# 📘 SETUP GUIDE FLOW - Hướng dẫn sử dụng từng bước

## 🎯 TỔNG QUAN

Flow hướng dẫn tương tác 8 bước giúp user làm chủ Freedom Wallet từ setup đến sử dụng nâng cao.

**Commit**: `2ddaf96` - Add interactive 8-step setup guide with /huongdan command + Day 1 button

---

## 📋 CẤU TRÚC 8 BƯỚC

### **Bước 0: Menu chính** 
- Giới thiệu 8 bước
- Jump buttons đến các section
- Command: `/huongdan`

### **Bước 1: BẮT ĐẦU**
- Xóa dữ liệu mẫu
- Đổi mật khẩu
- Chuẩn bị app "trắng"

### **Bước 2: TÀI KHOẢN** 
- Thêm tài khoản (tiền mặt, ngân hàng, ví điện tử)
- Sửa số dư ban đầu
- Hiển thị tổng tiền chính xác

### **Bước 3: GIAO DỊCH**
- 3 loại: Thu nhập / Chi tiêu / Chuyển tiền
- Ghi chép 5 thông tin: Ngày, số tiền, tài khoản, danh mục, ghi chú
- Habit: Ghi chép NGAY sau giao dịch

### **Bước 4: DANH MỤC**
- Categories: Ăn uống, nhà ở, giáo dục, giải trí...
- Báo cáo chi tiêu rõ ràng
- Nhận diện "lỗ hổng tài chính"

### **Bước 5: KHOẢN NỢ**
- Quản lý nợ vay, trả góp, thẻ tín dụng
- Theo dõi: Gốc, lãi suất, tiến độ
- Mindset: Nợ không phải kẻ thù

### **Bước 6: TÀI SẢN**
- Ghi nhận: Nhà đất, xe, vàng, tài sản giá trị
- Tính Net Worth = Tài sản - Nợ
- Không nhầm lẫn thu nhập và tài sản

### **Bước 7: ĐẦU TƯ**
- Theo dõi: Chứng khoán, vàng, BĐS, crypto...
- Xem: Vốn, giá trị hiện tại, lãi/lỗ, ROI
- Đầu tư có kỷ luật, dựa trên số liệu

### **Bước 8: 6 HŨ TIỀN**
- Trái tim Freedom Wallet
- Phân bổ cân bằng: 55% - 10% - 10% - 10% - 10% - 5%
- Vừa sống tốt – vừa giàu lên

### **Bước 9: KẾT LUẬN**
- 5 nguyên tắc vàng
- Kiên trì ít nhất 90 ngày
- Câu nói cuối: "Tự do tài chính đến từ hệ thống"

---

## 🎮 CÁCH SỬ DỤNG

### **1. Từ command**
```
/huongdan
```
→ Mở menu chính (Bước 0)

### **2. Từ Day 1 Onboarding**
User nhấn nút: **📘 Hướng dẫn sử dụng chi tiết**
→ Callback: `guide_step_0`
→ Mở menu chính

### **3. Navigation buttons**
Mỗi bước có:
- **⬅️ Quay lại** / **Tiếp theo ➡️**: Di chuyển tuyến tính
- **📘 Menu**: Quay về menu chính
- **💬 Cần trợ giúp?**: Link đến Group VIP

### **4. Hoàn thành**
Bước 9 → Nhấn **✅ Hoàn thành**
→ Callback: `guide_complete`
→ Message kết thúc + options

---

## 🔧 KỸ THUẬT IMPLEMENTATION

### **File structure**
```
bot/handlers/setup_guide.py          # Main handler
bot/handlers/onboarding.py           # Day 1 integration
main.py                               # Register handlers
docs/BROCHURE_Huong_dan_su_dung.html # Source content
docs/image 1-9.png                    # Screenshots
```

### **Key functions**

#### `setup_guide.py`
```python
SETUP_GUIDE_STEPS = {0: {...}, 1: {...}, ..., 9: {...}}

get_setup_guide_keyboard(current_step: int) 
    # Generate navigation buttons

send_guide_step(update, context, step: int)
    # Send specific step

huongdan_command(update, context)
    # /huongdan handler

guide_callback_handler(update, context)
    # Handle guide_step_X callbacks

register_setup_guide_handlers(application)
    # Register all handlers
```

#### `main.py`
```python
from bot.handlers.setup_guide import register_setup_guide_handlers

register_setup_guide_handlers(application)
```

#### `onboarding.py` (Day 1 buttons)
```python
"buttons": [
    [{"text": "📑 Copy Template", "url": "..."}],
    [{"text": "📖 Hướng dẫn tạo Web App", "url": "..."}],
    [{"text": "📘 Hướng dẫn sử dụng chi tiết", "callback_data": "guide_step_0"}],
    [{"text": "👥 Tham gia Group VIP", "url": "..."}]
]
```

### **Button types supported**
```python
# URL button
{"text": "Link text", "url": "https://..."}

# Callback button  
{"text": "Button text", "callback_data": "guide_step_0"}
```

### **Callback pattern**
```python
application.add_handler(
    CallbackQueryHandler(guide_callback_handler, pattern="^guide_")
)
```

Handles:
- `guide_step_0` ... `guide_step_9`: Navigation
- `guide_complete`: Completion message

---

## 📊 USER EXPERIENCE FLOW

```
User VIP unlock
    ↓
Day 1 Message (10 min delay)
    ↓
4 buttons hiển thị:
    1. 📑 Copy Template → Google Sheets
    2. 📖 Hướng dẫn tạo Web App → Notion
    3. 📘 Hướng dẫn sử dụng chi tiết → Setup Guide Menu
    4. 👥 Join Group VIP → Telegram
    ↓
User nhấn "📘 Hướng dẫn sử dụng chi tiết"
    ↓
Menu chính (Bước 0)
    ↓
User chọn Bước 1-4 hoặc 5-8
    ↓
Đọc từng bước với Tiếp theo/Quay lại
    ↓
Hoàn thành 9 bước
    ↓
Nhấn "✅ Hoàn thành"
    ↓
Message kết thúc + option xem lại
```

---

## 🎯 PSYCHOLOGY DESIGN

### **Progressive disclosure**
- Không overwhelm user với 8 bước cùng lúc
- Menu cho phép jump đến section quan tâm
- Linear navigation cho học từng bước

### **Clear navigation**
- Luôn có cách quay lại (Back button)
- Menu button ở mọi bước (except 0)
- Help button luôn có

### **Completion psychology**
- Step 9 = Celebration
- "Hoàn thành" button → sense of achievement
- Option xem lại → không bị mất

### **Integration với Day 1**
- Không force user vào guide ngay
- Optional button trong Day 1
- User tự quyết định khi nào học

---

## 📈 METRICS & OPTIMIZATION

### **Track metrics** (Future)
```python
# Add to database
- guide_started_at: datetime
- guide_completed_at: datetime  
- guide_last_step: int
- guide_completion_rate: float
```

### **Analytics questions**
1. Bao nhiêu % user click "📘 Hướng dẫn sử dụng chi tiết" từ Day 1?
2. Bước nào user dừng lại nhiều nhất?
3. Bao nhiêu % user hoàn thành đến Bước 9?
4. User xem lại guide bao nhiêu lần?

### **Potential improvements**
- Add images/GIFs vào từng bước
- Video tutorials embedded
- Interactive quizzes sau mỗi section
- Gamification: Badges cho completion
- Track time spent per step

---

## 🔄 MAINTENANCE

### **Update content**
Edit `SETUP_GUIDE_STEPS` in `setup_guide.py`:
```python
SETUP_GUIDE_STEPS = {
    1: {
        "title": "...",
        "content": """...""",
        "image": None  # Future: Add image URL
    }
}
```

### **Add new steps**
```python
# Just add to dict
10: {
    "title": "🎓 BƯỚC 9: Advanced Features",
    "content": "..."
}

# Update max step in keyboard logic
if current_step < 10:  # Change from 9
```

### **Testing**
```bash
# Test command
/huongdan

# Test callback
Click "📘 Hướng dẫn sử dụng chi tiết" from Day 1

# Test navigation
Click Tiếp theo → Check step advances
Click Quay lại → Check step goes back
Click Menu → Check return to step 0
```

---

## ✅ CHECKLIST

**Implemented:**
- [x] 8-step content structure
- [x] Menu navigation (Step 0)
- [x] Linear navigation (Back/Next)
- [x] Jump buttons (1-4, 5-8)
- [x] `/huongdan` command
- [x] Day 1 integration
- [x] Completion message
- [x] Help button (Group VIP link)
- [x] Callback pattern handling
- [x] Error handling

**Future enhancements:**
- [ ] Add images/screenshots
- [ ] Track completion metrics
- [ ] Quiz/checkpoints
- [ ] Badges/gamification
- [ ] Video tutorials
- [ ] Search function
- [ ] Bookmark favorite steps
- [ ] Share progress

---

## 🎉 SUCCESS CRITERIA

User sau 8 bước phải:
1. **Hiểu** được mọi tính năng của Freedom Wallet
2. **Biết cách** setup từ đầu (accounts → transactions → categories)
3. **Nắm rõ** triết lý 6 Hũ Tiền
4. **Có động lực** bắt đầu ghi chép ngay
5. **Cảm thấy hỗ trợ** (Group VIP link luôn có)

---

**Version**: 1.0
**Date**: 2026-02-08  
**Commit**: `2ddaf96`
**Status**: ✅ Production Ready
