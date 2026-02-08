# 📋 USER REGISTRATION FLOWS

## 🎯 Tổng Quan

Hệ thống hỗ trợ **2 luồng đăng ký** độc lập và đồng bộ:

### ✅ Flow 1: Đăng ký từ WEBSITE → BOT
User điền form trên freedomwallet.app, sau đó nhận template qua Bot

### ✅ Flow 2: Đăng ký từ REFERRAL LINK (Telegram)
User nhận link giới thiệu từ bạn bè, đăng ký trực tiếp trong Bot

---

## 🌐 FLOW 1: Website → Bot

### Bước 1: User đăng ký trên Website
```
1. User vào https://freedomwallet.app/
2. Click "Đăng ký ngay" → Điền form:
   - Họ tên: Nguyễn Văn A
   - Email: user@example.com
   - Số điện thoại: 0901234567
   - Gói: FREE / Premium
3. Submit → Data lưu vào Google Sheets
```

### Bước 2: Website hiển thị Success Modal với Bot Link
```html
🎉 Chúc Mừng Bạn Nhận Gói FREE!
✅ Bạn đã đăng ký thành công!

🎁 Bước 1: Nhận Template FREE
Mở Bot để nhận file Google Sheets template của bạn ngay!

[🤖 Mở Bot Nhận Template]
↓
https://t.me/FreedomWalletbot?start=WEB_AB12CD34
```

**Link Format:**
- `WEB_` prefix = đăng ký từ website
- `AB12CD34` = hash từ email (8 ký tự)

### Bước 3: User click button → Mở Telegram Bot
```
User click "Mở Bot Nhận Template"
→ Telegram app mở
→ Bot nhận /start WEB_AB12CD34
```

### Bước 4: Bot xử lý WEB Registration
```python
# bot/handlers/start.py

if code.startswith("WEB_"):
    email_hash = code[4:]  # Remove "WEB_" prefix
    
    # 1. Tìm user trong Google Sheets bằng email hash
    web_data = await sync_web_registration(user.id, user.username, email_hash)
    
    # 2. Update user trong bot database
    await update_user_registration(
        user_id=user.id,
        email=web_data['email'],
        phone=web_data['phone'],
        full_name=web_data['full_name'],
        source='WEB'
    )
    
    # 3. Gửi welcome + template link
    await update.message.reply_text(
        "🎉 Chào mừng {name}!\n"
        "✅ Bạn đã đăng ký thành công từ website!\n"
        "📄 Nhận Template ngay: [link]\n"
    )
```

### Bước 5: User nhận template và sử dụng
```
✅ User nhận được:
- Welcome message cá nhân hóa (có tên từ website)
- Link template Google Sheets
- is_registered = True trong DB
- KHÔNG bị hỏi đăng ký lại
```

---

## 🎁 FLOW 2: Referral Link → Bot

### Bước 1: User A chia sẻ link giới thiệu
```
User A trong bot:
/referral → Copy link:
https://t.me/FreedomWalletbot?start=ABC12345

Share qua:
- Telegram message
- Facebook
- Zalo
```

**Link Format:**
- `ABC12345` = referral code (KHÔNG có prefix)
- Tự động phân biệt với WEB_ links

### Bước 2: User B click link giới thiệu
```
User B click link
→ Mở Telegram
→ Bot nhận /start ABC12345
```

### Bước 3: Bot xử lý Referral
```python
# bot/handlers/start.py

else:  # Không có prefix "WEB_"
    referral_code = code
    
    # 1. Tìm user A by referral code
    # 2. Tạo referral PENDING
    # 3. Thông báo cho user A: "User B vừa click link! ⏳ Đang chờ đăng ký..."
    referred = await handle_referral_start(update, context, referral_code)
```

### Bước 4: Bot prompt User B đăng ký
```
🎉 Bạn được [User A] giới thiệu!

Đăng ký ngay để:
✅ Nhận Template FREE
✅ Giúp [User A] mở khóa FREE trọn đời

👉 Bấm /register để bắt đầu
```

### Bước 5: User B điền form trong Bot
```
Bot: Nhập email của bạn:
User B: user-b@example.com

Bot: Nhập số điện thoại (hoặc /skip):
User B: 0909999999

Bot: Nhập họ tên (hoặc /skip):
User B: Nguyễn Thị B

Bot: Xác nhận thông tin:
✅ Email: user-b@example.com
✅ SĐT: 0909999999
✅ Tên: Nguyễn Thị B

[Xác nhận] [Hủy]
```

### Bước 6: User B xác nhận → Referral verified
```python
# bot/handlers/registration.py - confirm_registration()

# 1. Lưu user info vào DB
await update_user_registration(user_id, email, phone, full_name, source='BOT')

# 2. Sync lên Google Sheets
await sync_user_to_sheet(user_id, email, phone, full_name)

# 3. Verify referral (PENDING → VERIFIED)
referral = session.query(Referral).filter(
    Referral.referred_id == user_id,
    Referral.status == "PENDING"
).first()

if referral:
    referral.status = "VERIFIED"
    referral.verified_at = datetime.utcnow()
    
    # 4. Increment referrer's count
    referrer.referral_count += 1
    
    # 5. Thông báo cho User A
    await context.bot.send_message(
        referrer.id,
        f"🎉 {full_name} đã hoàn tất đăng ký!\n"
        f"Bạn đã giới thiệu {referrer.referral_count}/2 người"
    )
    
    # 6. Auto-unlock nếu đủ 2 người
    if referrer.referral_count >= 2:
        referrer.is_free_unlocked = True
        await context.bot.send_message(
            referrer.id,
            "🔓 Chúc mừng! Bạn đã mở khóa FREE FOREVER!"
        )
```

### Bước 7: User B nhận template
```
✅ Đăng ký thành công!
📄 Đây là template: [link]
```

---

## 🔍 So Sánh 2 Flows

| Đặc điểm | Flow 1: Website | Flow 2: Referral |
|----------|----------------|------------------|
| **Entry Point** | freedomwallet.app | Referral link từ bạn |
| **Deep Link** | `WEB_HASH` | `REFERRAL_CODE` |
| **Form điền ở** | Website | Bot |
| **Data sync** | Sheets → Bot | Bot → Sheets |
| **Prompt đăng ký** | ❌ Không (đã đăng ký) | ✅ Có |
| **Referral tracking** | ❌ Không | ✅ Có |
| **is_registered** | Ngay lập tức | Sau khi confirm |

---

## 🗂️ Database Schema

```sql
-- User registration từ Website
User {
    id: 123456789
    email: "user@example.com"
    phone: "0901234567"
    full_name: "Nguyễn Văn A"
    is_registered: True
    subscription_tier: "FREE"
    source: "WEB"  -- (implicit)
}

-- User registration từ Referral
User {
    id: 987654321
    referred_by: 123456789
    email: "user-b@example.com"
    phone: "0909999999"
    full_name: "Nguyễn Thị B"
    is_registered: True
    subscription_tier: "TRIAL"
    source: "BOT"  -- (implicit)
}

Referral {
    id: 1
    referrer_id: 123456789
    referred_id: 987654321
    referral_code: "ABC12345"
    status: "VERIFIED"  -- (was PENDING before registration)
    verified_at: "2026-02-07 08:00:00"
}
```

---

## 🛠️ Technical Implementation

### 1. Email Hash Function (JavaScript trong landing page)
```javascript
function generateReferralCode(email) {
    const hash = email.split('').reduce((acc, char) => {
        return ((acc << 5) - acc) + char.charCodeAt(0);
    }, 0);
    return Math.abs(hash).toString(36).toUpperCase().substring(0, 8);
}

// Example:
// user@example.com → "AB12CD34"
```

### 2. Email Hash Function (Python trong bot)
```python
# bot/utils/sheets.py

def generate_email_hash(email: str) -> str:
    hash_value = 0
    for char in email:
        hash_value = ((hash_value << 5) - hash_value) + ord(char)
        hash_value = hash_value & 0xFFFFFFFF
    
    result = abs(hash_value)
    base36 = ''
    while result > 0:
        result, remainder = divmod(result, 36)
        if remainder < 10:
            base36 = chr(48 + remainder) + base36
        else:
            base36 = chr(55 + remainder) + base36
    
    return base36[:8].upper().ljust(8, '0')
```

### 3. Deep Link Detection (Bot)
```python
# bot/handlers/start.py

if context.args:
    code = context.args[0]
    
    if code.startswith("WEB_"):
        # Flow 1: Website registration
        email_hash = code[4:]
        await handle_web_registration(update, context, email_hash)
    else:
        # Flow 2: Referral
        referral_code = code
        await handle_referral_start(update, context, referral_code)
```

### 4. Google Sheets Sync
```python
# bot/utils/sheets.py

async def sync_web_registration(telegram_id, telegram_username, email_hash):
    # 1. Find user in Sheets by email hash
    worksheet = spreadsheet.worksheet("Freedom Wallet Registrations")
    records = worksheet.get_all_records()
    
    for record in records:
        email = record.get('Email')
        if generate_email_hash(email) == email_hash:
            return {
                'full_name': record['Họ tên'],
                'email': email,
                'phone': record['Số điện thoại'],
                'plan': record['Gói']
            }
    
    return None
```

---

## 🧪 Testing Checklist

### Test Flow 1: Website → Bot
- [ ] User điền form trên landing page → Submit success
- [ ] Success modal hiển thị bot link với WEB_ prefix
- [ ] Click bot link → Mở Telegram
- [ ] Bot nhận /start WEB_HASH → Tìm được user trong Sheets
- [ ] Bot gửi welcome message với tên đúng từ website
- [ ] User KHÔNG thấy nút "Đăng ký" nữa
- [ ] `is_registered = True` trong database

### Test Flow 2: Referral → Bot
- [ ] User A copy referral link từ /referral
- [ ] User B click link → Mở Telegram
- [ ] Bot prompt User B đăng ký: /register
- [ ] User B điền form (email, phone, name)
- [ ] Referral status: PENDING → VERIFIED
- [ ] User A nhận notification
- [ ] referral_count tăng lên
- [ ] Test với 2 người → User A unlock FREE

---

## 📝 Notes

1. **Email Hash Collision**: Rất thấp (base36 8 chars = 2.8 trillion combinations)
2. **Google Sheets Worksheet Name**: Code tìm tự động các tên phổ biến:
   - "Freedom Wallet Registrations"
   - "Registrations"  
   - "Sheet1"
   - "Form Responses 1"
3. **Referral Code Format**: 8 chars SHA256 hash (không có prefix)
4. **WEB Code Format**: `WEB_` + 8 chars email hash

---

## 🚀 Deployment

### Cần cập nhật:
1. ✅ Landing page (index.html) - Added bot link buttons
2. ✅ Bot handlers (start.py) - WEB_ detection
3. ✅ Sheets integration (sheets.py) - Email hash + sync functions
4. ✅ Database (database.py) - update_user_registration()
5. ⏳ Google Sheets credentials - Cần setup
6. ⏳ Template link - Cần thêm vào welcome message

### Environment Variables cần có:
```bash
GOOGLE_SHEETS_CREDENTIALS=google_service_account.json
SUPPORT_SHEET_ID=1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg
```
