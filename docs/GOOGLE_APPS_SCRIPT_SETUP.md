# 📝 HƯỚNG DẪN CÀI ĐẶT GOOGLE APPS SCRIPT
**RoadmapAutoInsert_v2.gs - Tự động cập nhật roadmap**

Google Sheet: https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit

---

## ✅ BƯỚC 1: DEPLOY SCRIPT

### **1.1. Mở Google Apps Script**

1. Mở Google Sheet của bạn
2. Click **Extensions** (Tiện ích mở rộng)
3. Click **Apps Script**

### **1.2. Copy Script**

1. Trong Apps Script Editor, xóa code mặc định
2. Copy toàn bộ nội dung file `RoadmapAutoInsert_v2.gs`
3. Paste vào editor
4. Click **Save** (Ctrl+S)

### **1.3. Đặt tên project**

- Click "Untitled project"
- Đổi tên: "Roadmap Automation v2.0"
- Click **Rename**

---

## ✅ BƯỚC 2: KIỂM TRA CẤU HÌNH

### **2.1. Kiểm tra tên Sheet**

Mở file `RoadmapAutoInsert_v2.gs`, tìm dòng:

```javascript
SHEET_NAME: 'Roadmap_Features',  // ⚠️ KIỂM TRA TÊN SHEET!
```

**Cách check tên sheet:**
1. Mở Google Sheet
2. Nhìn xuống dưới cùng, thấy tab sheet
3. Ví dụ: "Sheet1", "Roadmap", "Features", etc.

**Nếu tên khác**, sửa lại:
```javascript
SHEET_NAME: 'Sheet1',  // Hoặc tên sheet của bạn
```

### **2.2. Kiểm tra cấu trúc cột**

Sheet phải có **8 cột** theo thứ tự:

| Cột | Tên | Mô tả |
|-----|-----|-------|
| A | ID | FW#001, FW#002, ... |
| B | Timestamp | Ngày giờ |
| C | Email | Email người tạo |
| D | Title | Tiêu đề feature |
| E | Description | Mô tả chi tiết |
| F | Type | Tính năng, Bug Fix, UI/UX, ... |
| G | Status | IDEA, PLANNED, IN_PROGRESS, ... |
| H | Votes | Số vote |

**Nếu sheet chưa có header**, tạo row 1:

```
ID | Timestamp | Email | Title | Description | Type | Status | Votes
```

---

## ✅ BƯỚC 3: TEST SCRIPT

### **3.1. Run Test Function**

1. Trong Apps Script Editor
2. Chọn function **testInsertItem** ở dropdown
3. Click **Run** (▶️)

### **3.2. Authorize Permissions**

Lần đầu chạy sẽ hỏi permissions:

1. Click **Review permissions**
2. Chọn Google account của bạn
3. Click **Advanced**
4. Click **Go to Roadmap Automation (unsafe)**
5. Click **Allow**

### **3.3. Kiểm tra kết quả**

Sau khi run xong:

1. Mở Google Sheet
2. Check có row mới không:
   - ID: FW#xxx (auto-generate)
   - Title: "Test: Dynamic Roadmap System"
   - Status: IN_PROGRESS (màu vàng)

**Nếu thấy row mới** → ✅ **THÀNH CÔNG!**

**Nếu có lỗi:**
- Check lại tên sheet trong CONFIG
- Check cấu trúc cột (phải có 8 cột)
- Xem log lỗi trong Apps Script

---

## ✅ BƯỚC 4: SỬ DỤNG TỪ PYTHON

### **4.1. Deploy as Web App (Optional)**

Nếu muốn gọi từ Python bot:

1. Trong Apps Script, click **Deploy** → **New deployment**
2. Chọn type: **Web app**
3. Settings:
   - Description: "Roadmap API v2.0"
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Click **Deploy**
5. Copy **Web app URL**

### **4.2. Cập nhật .env**

Thêm vào file `.env`:

```bash
ROADMAP_APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
```

### **4.3. Test từ Python**

```python
from app.services.roadmap_service import sync_ai_idea

result = sync_ai_idea(
    "Test từ Python",
    "Kiểm tra tích hợp Python → Google Sheet"
)

print(result)
# Output: {'success': True, 'message': 'Added: FW#xxx - Test từ Python'}
```

---

## 🎯 CÁC FUNCTION CÓ SẴN

### **1. insertRoadmapItem(data)**

Thêm item mới vào roadmap:

```javascript
insertRoadmapItem({
  title: "AI Budget Recommendations",
  description: "Tự động suggest phân bổ ngân sách",
  type: CONFIG.TYPES.FEATURE,
  status: CONFIG.STATUSES.IDEA
});
```

### **2. updateRoadmapStatus(id, newStatus)**

Update status theo ID:

```javascript
updateRoadmapStatus("FW#123", CONFIG.STATUSES.IN_PROGRESS);
```

### **3. updateRoadmapByTitle(title, newStatus)**

Update status theo Title:

```javascript
updateRoadmapByTitle(
  "AI Budget Recommendations",
  CONFIG.STATUSES.COMPLETED
);
```

### **4. logReleaseVersion(version, description, features)**

Log release mới:

```javascript
logReleaseVersion(
  "v2.1.0",
  "Budget AI Release",
  [
    "AI Budget Recommendations",
    "Spending Analysis"
  ]
);
```

### **5. batchUpdateStatus(oldStatus, newStatus)**

Update hàng loạt:

```javascript
batchUpdateStatus(
  CONFIG.STATUSES.COMPLETED,
  CONFIG.STATUSES.RELEASED
);
```

---

## 🔍 TROUBLESHOOTING

### **Lỗi: "Sheet not found: Roadmap_Features"**

**Nguyên nhân:** Tên sheet trong CONFIG sai

**Fix:**
1. Check tên sheet thật (tab dưới cùng Google Sheet)
2. Sửa lại `SHEET_NAME` trong CONFIG
3. Save và run lại

### **Lỗi: "Missing required field: title"**

**Nguyên nhân:** Gọi function thiếu parameter

**Fix:**
```javascript
// ❌ SAI
insertRoadmapItem({});

// ✅ ĐÚNG
insertRoadmapItem({
  title: "Feature Title"
});
```

### **Lỗi: "Item already exists: ..."**

**Nguyên nhân:** Title đã tồn tại trong sheet

**Fix:**
- Đổi title khác, hoặc
- Dùng `updateRoadmapByTitle()` để update item cũ

### **Status không đổi màu**

**Nguyên nhân:** Conditional formatting chưa apply

**Fix:**
1. Run lại function
2. Hoặc manually run: `applyStatusFormatting(sheet, rowNumber, 1)`

---

## 📊 STATUS COLORS

| Status | Màu | Ý nghĩa |
|--------|-----|---------|
| IDEA | 🔴 Hồng nhạt | Ý tưởng mới |
| PLANNED | 🔵 Xanh dương | Đã approve, chưa làm |
| IN_PROGRESS | 🟡 Vàng | Đang code |
| COMPLETED | 🟢 Xanh lá | Code xong |
| REFACTORED | 🔵 Xanh nhạt | Đã refactor |
| RELEASED | 🟢 Xanh đậm | Đã release |
| ARCHITECTURE_UPDATE | ⚪ Xám | Update kiến trúc |

---

## ✅ CHECKLIST

**Setup hoàn tất khi:**

- [ ] Script đã paste vào Apps Script Editor
- [ ] Tên sheet trong CONFIG đúng
- [ ] Cấu trúc 8 cột đúng thứ tự
- [ ] Test function `testInsertItem` chạy thành công
- [ ] Thấy row mới xuất hiện trong sheet
- [ ] Status có màu sắc đúng
- [ ] (Optional) Deploy as Web App và có URL
- [ ] (Optional) Python bot connect được

---

## 🎉 HOÀN TẤT!

Script đã sẵn sàng tự động update roadmap!

**Bước tiếp theo:**
1. Tích hợp vào Python bot (xem `app/services/roadmap_service.py`)
2. Auto-sync khi có ý tưởng mới
3. Auto-update status khi task hoàn thành

**Hỗ trợ:**
- Slack: #freedom-wallet-dev
- Email: dev@freedomwallet.com

---

**Last Updated:** 2026-02-17  
**Version:** 2.0
