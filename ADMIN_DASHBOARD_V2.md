# 🎛️ Admin Dashboard V2 - Complete Guide

## 📊 Overview

Dashboard toàn diện với 5-row layout, segment management, analytics, và payment tracking.

## ✨ Features Mới

### 1. **Enhanced Metrics**
```
🛡️ ADMIN PANEL   cập nhật 21:30 VN
━━━━━━━━━━━━━━━━━━━━━━
👥 Total: 32   📋 Đăng ký: 30   💳 Pending: 2
🤖 BOT: 15   🌐 Landing: 17
🔗 Kết nối: 6 (18.75%)   📝 Giao dịch: 5 (15.6%)
[██░░░░░░░░] 18%
━━━━━━━━━━━━━━━━━━━━━━
Đăng ký: 26 | Kết nối: 1 | Giao dịch: 5
📅 Hôm nay: 3   7 ngày: 30
💰 Doanh thu: 2.5M VNĐ
```

**Metrics mới:**
- ✅ BOT vs Landing Page breakdown
- ✅ User segments (Đăng ký / Kết nối / Giao dịch)
- ✅ Pending payments count
- ✅ Revenue stats

### 2. **5-Row Keyboard Layout**

#### **Row 1: User Management**
- **👥 Users** → View all users với filters
- **📊 Segments** → Chi tiết 3 segments với conversion rates
- **📈 Analytics** → Conversion funnel, activation rates, source breakdown

#### **Row 2: Actions**
- **📣 Broadcast** → Menu cho từng segment (Đăng ký, Kết nối, Giao dịch, Setup)
- **💳 Payments (2)** → Pending verifications & revenue
- **🔍 Search** → Search user by ID or email

#### **Row 3: Data Sync**
- **🔄 Sync Jobs** → Auto-sync status + manual triggers
- **📊 Sheet** → Direct link to Google Sheet (32 users synced)
- **📧 Email** → Email broadcast options

#### **Row 4: System**
- **🏥 Health** → System health & error tracking
- **⚠️ Errors** → Recent errors log
- **🔧 Tools** → Admin commands & VPS scripts

#### **Row 5: Navigation**
- **🔄 Refresh** → Update dashboard data
- **✖️ Close** → Close admin panel

## 🎯 New Screens

### **Segments View** (`adm:segments`)
```
📊 USER SEGMENTS

📍 Đăng ký: 26 users (81.2%)
   Chỉ mới đăng ký, chưa kết nối spreadsheet

📍 Đã kết nối Bot: 1 users (3.1%)
   Có spreadsheet nhưng chưa ghi giao dịch

📍 Ghi giao dịch: 5 users (15.6%)
   Đã có giao dịch trong hệ thống
```

**Actions:**
- 📤 Broadcast Đăng ký (26) → Send onboarding
- 📤 Broadcast Giao dịch (5) → Request feedback

### **Analytics View** (`adm:analytics`)
```
📈 ANALYTICS

Conversion Funnel:
Total Users → 32
├─ Đăng ký → 26 (81.2%)
├─ Kết nối → 1 (3.1%)
└─ Giao dịch → 5 (15.6%)

Activation Rate: 18.8%
Active Rate: 15.6%

By Source:
🤖 BOT: 15 users
🌐 Landing Page: 17 users

Payment:
💰 Revenue: 2500K VNĐ
💳 Pending: 2 verifications
```

### **Broadcast Menu** (`adm:broadcast_menu`)
```
📣 BROADCAST MENU

Chọn segment để gửi:

📤 Đăng ký: 26 users
   → Onboarding message

📤 Đã kết nối: 1 users
   → Khuyến khích giao dịch đầu tiên

📤 Giao dịch: 5 users
   → Feedback & Premium offer

📤 Setup Chưa xong: 24 users
   → Setup guide
```

### **Sync Jobs** (`adm:sync_jobs`)
```
🔄 SYNC JOBS

Auto Sync Schedule:
• Landing Page → DB: Every 30 min
• DB → Sheet: Manual only

Manual Triggers:
cd C:\FreedomWalletBot
python bot/utils/sync_landing_page.py
python bot/utils/sync_db_to_sheet.py
```

### **Google Sheet** (`adm:open_sheet`)
```
📊 GOOGLE SHEET

• 32 users synced
• Auto-updates every 30 min
• Includes status & source

[📊 Open Sheet] → Direct link
```

### **Payments** (`adm:payments`)
```
💳 PAYMENT VERIFICATIONS

Pending: 2 verifications
Revenue: 2500K VNĐ

Commands:
/payment_list - View pending
/payment_stats - Statistics
```

### **Search** (`adm:search`)
```
🔍 SEARCH USER

Send:
/admin_find [user_id or email]

Example:
/admin_find 6588506476
/admin_find mettatuan@gmail.com
```

### **Tools Menu** (`adm:tools`)
```
🔧 ADMIN TOOLS

Available Commands:
/broadcast_all [msg] - Send to all
/admin_users [filter] - List users
/admin_find [id/email] - Search user
/payment_list - Pending payments
/health - System status

VPS Scripts:
• broadcast_segments.py - Segment broadcast
• check_bot_status.ps1 - Bot status
• C:\nssm\nssm.exe restart FreedomWalletBot
```

## 🚀 Usage

### **Access Dashboard**
```
Send: /admin
```

### **Navigate**
Click any button để access các chức năng tương ứng.

### **Quick Actions**

#### View User Segments:
```
/admin → 📊 Segments
```

#### Send Broadcast:
```
/admin → 📣 Broadcast → Choose segment
```

#### Check Analytics:
```
/admin → 📈 Analytics
```

#### Manage Payments:
```
/admin → 💳 Payments
```

#### Control Sync:
```
/admin → 🔄 Sync Jobs
```

## 📝 Developer Notes

### **Code Changes**

#### `_get_stats()` - Enhanced metrics:
```python
# Added:
- bot_users / landing_users (by activation_source)
- dang_ky / ket_noi / giao_dich (user segments)
- pending_payments (PaymentVerification status)
- revenue (sum of approved payments)
```

#### `_dashboard_text()` - New format:
```python
# Shows:
- Total, Registered, Pending payments
- BOT vs Landing source
- Connection rate & Transaction count
- Segment breakdown (Đăng ký | Kết nối | Giao dịch)
- Daily/Weekly active, Revenue
```

#### `_dashboard_keyboard()` - 5 rows:
```python
# Row structure:
Row 1: User Management (Users, Segments, Analytics)
Row 2: Actions (Broadcast, Payments, Search)
Row 3: Data Sync (Sync Jobs, Sheet, Email)
Row 4: System (Health, Errors, Tools)
Row 5: Navigation (Refresh, Close)
```

### **New Callbacks**

Added handlers:
- `adm:segments` → Show segment breakdown
- `adm:analytics` → Show conversion funnel
- `adm:broadcast_menu` → Broadcast options
- `adm:broadcast_dang_ky` → Broadcast to "Đăng ký" segment
- `adm:broadcast_ket_noi` → Broadcast to "Kết nối" segment
- `adm:broadcast_giao_dich` → Broadcast to "Giao dịch" segment
- `adm:payments` → Payment management
- `adm:search` → User search guide
- `adm:sync_jobs` → Sync control
- `adm:open_sheet` → Google Sheet link
- `adm:tools` → Admin tools menu

## 🎯 Business Impact

### **Before:**
- ❌ Limited visibility into user segments
- ❌ No source tracking (BOT vs Landing)
- ❌ Manual user counting
- ❌ No payment overview in dashboard

### **After:**
- ✅ Full segment breakdown (Đăng ký 81%, Kết nối 3%, Giao dịch 16%)
- ✅ Source tracking (BOT 15, Landing 17)
- ✅ Real-time metrics auto-update
- ✅ Payment tracking integrated
- ✅ Analytics với conversion rates
- ✅ Quick access to all tools

### **Key Metrics Visible:**
1. **Activation Rate**: 18.75% (6/32 users connected)
2. **Active Rate**: 15.6% (5/32 users with transactions)
3. **Churn Risk**: 81.2% users only registered (26/32)
4. **Revenue**: Real-time tracking
5. **Pending Payments**: Immediate visibility

## 🔧 Maintenance

### **Add New Callback:**
```python
elif data == "adm:your_new_feature":
    await query.edit_message_text(
        "Your content here",
        parse_mode="HTML",
        reply_markup=_back_btn
    )
```

### **Add New Metric:**
```python
# In _get_stats():
new_metric = base_q().filter(User.field == value).count()

# Return in dict:
return {
    # ... existing metrics
    "new_metric": new_metric,
}

# Use in _dashboard_text():
f"📊 New Metric: {s['new_metric']}"
```

## 📚 Related Files

- `bot/handlers/admin_menu.py` - Main dashboard code
- `bot/utils/sync_landing_page.py` - Auto-sync LP → DB
- `bot/utils/sync_db_to_sheet.py` - DB → Sheet sync
- `broadcast_segments.py` - Segmented broadcast tool
- `check_bot_status.ps1` - Bot status checker
- `setup_service.ps1` - Windows Service installer

## 🎉 Changelog

### **v2.0.0 (2026-03-01)**
- ✅ Added BOT vs Landing Page source tracking
- ✅ Added user segments (Đăng ký / Kết nối / Giao dịch)
- ✅ Added payment & revenue tracking
- ✅ Redesigned keyboard to 5-row layout
- ✅ Added Analytics screen với conversion funnel
- ✅ Added Broadcast menu với segment options
- ✅ Added Sync Jobs control
- ✅ Added direct Google Sheet link
- ✅ Added Search user feature
- ✅ Added Tools menu
- ✅ Enhanced dashboard text with comprehensive metrics

---

**Last Updated:** March 1, 2026  
**Version:** 2.0.0  
**Author:** GitHub Copilot + Mettatuan
