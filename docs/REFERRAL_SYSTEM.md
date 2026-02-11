# 🎁 Referral System Documentation

## Overview
Freedom Wallet Bot sử dụng hệ thống referral để unlock **FREE FOREVER** tier cho users.

### Business Logic
- **TRIAL**: Mọi user mới bắt đầu ở tier này (giới hạn features)
- **FREE**: Unlock khi giới thiệu thành công **2 người**
- **PREMIUM**: Upgrade bằng thanh toán 999k/năm

---

## Database Schema

### Users Table
```python
class User:
    id: int                      # Telegram user ID (primary key)
    username: str
    first_name: str
    last_name: str
    
    # Referral fields
    referral_code: str           # Unique code (8 chars, e.g., "A3B5C7D9")
    referred_by: int             # User ID who referred this user
    referral_count: int          # How many people this user referred (default: 0)
    is_free_unlocked: bool       # FREE tier unlocked? (default: False)
    
    # Subscription
    subscription_tier: str       # TRIAL | FREE | PREMIUM
    subscription_expires: datetime
```

### Referrals Table
```python
class Referral:
    id: int                      # Auto increment
    referrer_id: int             # Who shared the link
    referred_id: int             # Who joined via link
    referral_code: str           # Code used
    status: str                  # PENDING | VERIFIED | REWARDED
    created_at: datetime
    verified_at: datetime
```

### Subscriptions Table
```python
class Subscription:
    id: int
    user_id: int                 # Unique per user
    tier: str                    # TRIAL | FREE | PREMIUM
    payment_method: str          # VNPay | MoMo | Transfer
    amount_paid: float           # VND
    start_date: datetime
    end_date: datetime
    is_active: bool
    auto_renew: bool
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER A (Referrer)                        │
│  1. /start bot → Auto-generates referral_code: "ABC123"    │
│  2. /referral → Get link: t.me/bot?start=ABC123            │
│  3. Share link to friends                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ shares link
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    USER B (Referred)                        │
│  1. Click link: t.me/bot?start=ABC123                      │
│  2. Bot detects referral code "ABC123"                     │
│  3. Create Referral record:                                 │
│     - referrer_id: A                                        │
│     - referred_id: B                                        │
│     - status: VERIFIED                                      │
│  4. Update User A:                                          │
│     - referral_count += 1                                   │
│  5. Send welcome message to B                              │
│  6. Notify A: "You referred B successfully!"               │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ When referral_count >= 2
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              AUTO-UNLOCK FREE FOREVER                       │
│  - User A: is_free_unlocked = True                         │
│  - User A: subscription_tier = "FREE"                      │
│  - Send notification: "🎉 CONGRATS! FREE UNLOCKED!"        │
└─────────────────────────────────────────────────────────────┘
```

---

## API Functions

### Core Functions

#### `generate_referral_code(user_id: int) -> str`
Generates unique 8-character referral code using SHA256.

```python
code = generate_referral_code(123456789)
# Returns: "A3B5C7D9"
```

#### `create_referral(referrer_id, referred_id, code) -> (Referral | None, error | None)`
Creates referral relationship and updates counters.

```python
referral, error = await create_referral(
    referrer_id=111,
    referred_id=222,
    code="ABC123"
)
```

**Logic:**
1. Check if `referred_id` already has a referrer → reject
2. Create `Referral` record with status="VERIFIED"
3. Update `User.referred_by` for referred user
4. Increment `User.referral_count` for referrer
5. If `referral_count >= 2` → auto-unlock FREE tier

#### `get_user_referrals(user_id: int) -> List[Dict]`
Get all users referred by this user.

```python
refs = await get_user_referrals(111)
# Returns: [
#   {"id": 222, "name": "John", "date": datetime(...)},
#   {"id": 333, "name": "Jane", "date": datetime(...)}
# ]
```

---

## Bot Commands

### `/referral`
Show referral stats and link.

**Response:**
```
🎁 HỆ THỐNG GIỚI THIỆU BẠN BÈ

🎯 Còn 1 người nữa để mở khóa FREE!

📊 Thống Kê Của Bạn:
• Mã giới thiệu: ABC123
• Đã giới thiệu: 1 người
• Trạng thái: 🔒 Đang khóa

🔗 Link giới thiệu:
https://t.me/FreedomWalletBot?start=ABC123

📱 Cách sử dụng:
1. Copy link trên
2. Gửi cho bạn bè/gia đình
3. Khi 2 người đăng ký → FREE FOREVER!

💎 Quyền lợi FREE:
✓ Bot không giới hạn
✓ Template đầy đủ
✓ Hướng dẫn chi tiết
✓ Cộng đồng support

👥 Đã giới thiệu:
1. John Doe (15/02/2026)
```

**Buttons:**
- 📢 Chia sẻ ngay → Opens Telegram share dialog
- « Quay lại → Back to menu

---

## Deep Link Handling

### `/start` with referral code

**URL Format:**
```
https://t.me/FreedomWalletBot?start=ABC123
                                    ^^^^^^
                                 referral_code
```

**Handler Logic:**
```python
async def start(update, context):
    if context.args:  # Has deep link parameter
        referral_code = context.args[0]
        
        # Process referral
        await handle_referral_start(update, context, referral_code)
    
    # Show normal welcome message
```

---

## Notifications

### When User Gets Referred
**To Referred User (B):**
```
🎉 Chào mừng!

Bạn được giới thiệu bởi John Doe.
Cảm ơn bạn đã tham gia Freedom Wallet! 💚
```

**To Referrer (A):**
```
🎊 Tin vui!

Bạn vừa giới thiệu thành công Jane Smith!

📊 Tiến độ: 1/2 người
🎯 Còn 1 người nữa để mở khóa FREE!
```

### When FREE Unlocked
```
🎉🎉🎉 CHÚC MỪNG! 🎉🎉🎉

Bạn vừa mở khóa FREE FOREVER!

✅ Quyền lợi của bạn:
✓ Sử dụng Bot không giới hạn
✓ Tải Template Freedom Wallet
✓ Hướng dẫn setup chi tiết
✓ Support trong cộng đồng

🚀 Bắt đầu ngay với /help
```

---

## Edge Cases & Validation

### 1. Self-referral
❌ User cannot refer themselves
```python
if referrer.id == referred_user.id:
    return "😅 Bạn không thể tự giới thiệu chính mình!"
```

### 2. Already referred
❌ User can only be referred once
```python
existing = session.query(Referral).filter(
    Referral.referred_id == user_id
).first()

if existing:
    return "Bạn đã được giới thiệu bởi người khác rồi!"
```

### 3. Invalid code
❌ Code doesn't match any user
```python
referrer = await get_user_by_referral_code(code)
if not referrer:
    # Just show normal /start, don't show error
    return False
```

---

## Testing Checklist

### Manual Tests

- [ ] **T1: Generate referral code**
  - Start bot: `/start`
  - Check user gets unique `referral_code` in database
  
- [ ] **T2: View referral stats**
  - Command: `/referral`
  - Verify: Shows code, count, link, status
  
- [ ] **T3: Share referral link**
  - Click "📢 Chia sẻ ngay" button
  - Verify: Opens Telegram share with pre-filled text
  
- [ ] **T4: New user joins via link**
  - User B clicks: `t.me/bot?start=ABC123`
  - Verify: 
    - B gets welcome message mentioning referrer
    - A gets notification
    - A's `referral_count` increments
    - Referral record created
  
- [ ] **T5: Auto-unlock FREE**
  - User A refers 2 people
  - Verify:
    - `is_free_unlocked = True`
    - `subscription_tier = "FREE"`
    - Notification sent
    - `/start` shows "✅ FREE FOREVER"
  
- [ ] **T6: Edge case - Self referral**
  - User A clicks own link
  - Verify: Error message shown
  
- [ ] **T7: Edge case - Already referred**
  - User B clicks another referral link
  - Verify: Error message shown
  
- [ ] **T8: Callback button**
  - Click "🎁 Giới thiệu bạn bè" from menu
  - Verify: Shows referral stats (same as `/referral`)

---

## Database Queries for Analytics

### Top Referrers
```sql
SELECT 
    u.id,
    u.username,
    u.first_name,
    u.referral_count,
    COUNT(r.id) as verified_refs
FROM users u
LEFT JOIN referrals r ON u.id = r.referrer_id AND r.status = 'VERIFIED'
GROUP BY u.id
ORDER BY u.referral_count DESC
LIMIT 10;
```

### Referral Conversion Rate
```sql
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN referred_by IS NOT NULL THEN 1 ELSE 0 END) as referred_users,
    ROUND(
        SUM(CASE WHEN referred_by IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as conversion_rate
FROM users;
```

### FREE Unlock Rate
```sql
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN is_free_unlocked THEN 1 ELSE 0 END) as free_unlocked,
    ROUND(
        SUM(CASE WHEN is_free_unlocked THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) as unlock_rate
FROM users;
```

---

## Future Enhancements

### Phase 2: Gamification
- [ ] Leaderboard: Top 10 referrers
- [ ] Badges: "Influencer" (5+ refs), "Ambassador" (10+ refs)
- [ ] Bonus rewards: Premium trial for 5+ refs

### Phase 3: Advanced Tracking
- [ ] Track referral source (Telegram, Facebook, WhatsApp)
- [ ] Attribution window (refs must be active for 7 days)
- [ ] Referral codes with custom text: `JOHN2026`

### Phase 4: Integration
- [ ] Sync with Google Sheets for analytics
- [ ] Webhooks to notify external systems
- [ ] API endpoints for web dashboard

---

## Support

### Common Issues

**Q: User không nhận được notification khi có ref mới?**
A: Check if user blocked bot. Use try/except when sending notifications.

**Q: Referral count không tăng?**
A: Debug queries. Check `referrals` table có record mới không.

**Q: Bot không detect referral code?**
A: Verify `context.args` có value. Log để debug.

---

**Version:** 1.0  
**Last Updated:** 07/02/2026  
**Author:** Freedom Wallet Team
