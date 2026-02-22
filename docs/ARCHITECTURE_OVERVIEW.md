# ARCHITECTURE OVERVIEW — Freedom Wallet Bot
> Cập nhật: 2026-02-21 | Phiên bản: v3.x Production
> **Tài liệu duy nhất** cho dev tham khảo cấu trúc & flow hệ thống.

---

## 1. TỔNG QUAN HỆ THỐNG

```
freedomwallet.app          Telegram
(Landing Page)                 |
      |                   /start (cold)
      |                   /start WEB_{hash}     ← từ landing page
      |                   /start REF{code}      ← referral link
      └────────────────── Telegram Bot ─────────────────────┐
                               |                             |
                         main.py (Entry)                     |
                               |                             |
              ┌────────────────┼────────────────┐            |
         Handler Groups (ưu tiên giảm dần)       |            |
              |                |                |             |
           group=-2        group=-1          group=0      group=100
       handle_keyboard_   handle_settings  transaction_  AI/FAQ
       menu (webapp_       url_input +      handlers    (message.py)
       setup.py)           webapp URL +     reminder
                           sheets URL       callbacks
```

**Nguyên tắc handler priority:**
- `group=-2`: `handle_keyboard_menu` — chặn keyboard button, raise `ApplicationHandlerStop` sau khi xử lý
- `group=-1`: URL input handlers — chặn text khi user đang paste URL
- `group=0`: Transaction, report, settings callbacks (mặc định)
- `group=100`: AI/FAQ — chỉ chạy nếu không handler nào khác match

---

## 2. ENTRY POINTS

| Trigger | File | Mô tả |
|---|---|---|
| `/start` | `handlers/start.py` | Chào welcome, hiện main keyboard |
| `/start WEB_{emailHash}` | `handlers/start.py` | Từ freedomwallet.app, sync Google Sheets |
| `/start REF{code}` | `handlers/start.py` | Referral link từ user khác |
| `/taoweb` | `handlers/webapp_setup.py` | Bắt đầu hướng dẫn tạo Web App |
| `/huongdan` | `handlers/setup_guide.py` | Hướng dẫn kết nối Google Sheets |
| `/register` | `handlers/registration.py` | Đăng ký thủ công (conversation) |
| Keyboard: ✍️ Ghi giao dịch | `handlers/transaction.py` | Ghi thu chi |
| Keyboard: 📊 Báo cáo | `handlers/transaction.py` | Báo cáo menu |
| Keyboard: 📂 Mở Google Sheet | `handlers/transaction.py` | Mở sheets user |
| Keyboard: 🌐 Mở Web App | `handlers/transaction.py` | Mở web app user |
| Keyboard: 🔗 Chia sẻ | `handlers/transaction.py` | Affiliate share menu |
| Keyboard: 💝 Đóng góp | `handlers/transaction.py` | Donation info |
| Keyboard: 📖 Hướng dẫn | `handlers/transaction.py` | Guide menu |
| Keyboard: ⚙️ Cài đặt | `handlers/transaction.py` | Settings menu |
| Natural text | `handlers/message.py` | AI parse giao dịch |

---

## 3. FUNNEL TỔNG QUAN

```
AWARENESS
    │
    ▼
[User click link] ─── Landing page (freedomwallet.app) ─── /start WEB_{hash}
    │                                                              │
    └──────────── Direct Telegram ─── /start (cold) ─────────────┤
                                                                   │
                                                      ▼
ACTIVATION
    │
    ├── WEB Path: Sync Google Sheets → Check referral count
    │       ├── referral_count >= 2 → UNLOCKED → Onboarding Day 1
    │       └── referral_count < 2  → Show referral link + daily nurture
    │
    └── Cold Path: Welcome → Show main keyboard → Encourage first txn
                                                                   │
                                                      ▼
RETENTION (Core Loop)
    │
    ✍️ Ghi giao dịch → AI parse → save DB → sync webhook → confirm
    📊 Báo cáo → weekly / monthly / insight
    ⏰ Reminder tự động (daily, weekly, monthly)
    🎉 Streak celebration (7/30/90 ngày)
                                                                   │
                                                      ▼
REFERRAL
    │
    🔗 Chia sẻ → personal affiliate link → /start REF{code}
    └── referrer.referral_count++ → unlock at 2 referrals
                                                                   │
                                                      ▼
REVENUE
    │
    💝 Đóng góp (donation) + Premium tier (future)
```

---

## 4. CÁC FLOW QUAN TRỌNG

### Flow 1 — Tạo Web App (7 bước, command: /taoweb)

```
Trigger: /taoweb hoặc callback "webapp_step_0"
     │
     ▼
Step 0: Giới thiệu (Web App là gì, optional)
     │
     ▼
Step 1: Copy Template → button "📑 Copy Template" → Google Sheets
     │
     ▼
Step 2: Mở App Script (Extensions → Apps Script)
     │
     ▼
Step 3: Deploy Web App → lấy Web App URL
     │
     ▼
Step 4: Mở Web App lần đầu + Authorize Google
     │
     ▼
Step 5: Hoàn thành tạo Web App ✅
     │
     ▼
Step 6: Kết nối API với Telegram Bot
     │
     ├── "📱 Kết nối ngay" → callback "connect_webapp_start"
     │        │
     │        ▼ context.user_data['waiting_for_webapp_url'] = True
     │        │
     │        ▼ User paste URL → handle_webapp_url_message (group=-1)
     │        │
     │        ▼ Validate URL (regex: script.google.com/macros/s/.../exec)
     │        │
     │        ├─ Valid → save user.web_app_url → ask for Sheets URL
     │        │        → context.user_data['waiting_for_sheets_url'] = True
     │        │        → User paste Sheets URL → handle_sheets_url_message
     │        │        → save user.google_sheets_url + spreadsheet_id
     │        │        → show_quick_menu_keyboard(sheets_connected=True)
     │        │        → prompt "Xem Hướng dẫn sử dụng Web App" (usage flow)
     │        │
     │        └─ Invalid → show error, stay in waiting state
     │
     └── "⏭ Bỏ qua" → callback "guide_step_0" (Sheets guide)

Exit condition: user.web_app_url và user.google_sheets_url đã được lưu
Cancel: /cancel → clear context.user_data states
Idempotent: Có thể chạy lại bất kỳ lúc nào (dữ liệu chỉ overwrite)
```

**File:** `bot/handlers/webapp_setup.py` — `WEBAPP_SETUP_STEPS`, `send_webapp_setup_step()`, `handle_webapp_url_message()`, `handle_sheets_url_message()`

---

### Flow 2 — Sử dụng Web App (10 bước)

```
Trigger: callback "webapp_usage_step_0"
  ├── Sau khi hoàn thành kết nối (show_quick_menu_keyboard)
  ├── Từ Guide menu (📖 Hướng dẫn → "Sử dụng Web App")
  └── Trực tiếp từ setup guide step cuối

     ▼
Step 0: Đăng nhập (user/pass mặc định)
Step 1: Xóa dữ liệu mẫu
Step 2: Lập kế hoạch + 5 cấp bậc tài chính
Step 3: Thiết lập tài khoản (số dư thực tế)
Step 4: Thiết lập danh mục
Step 5: Hũ tiền — theo dõi & phân bổ
Step 6: Theo dõi tài sản
Step 7: Quản lý khoản nợ
Step 8: Theo dõi đầu tư
Step 9: Hoàn thành 🎉 + cộng đồng + add to home screen

Navigation: ⬅️ Quay lại / Tiếp theo ➡️
Quick-open buttons: 🌐 Mở Web App / 📋 Mở Google Sheets (nếu user đã kết nối)
Fallback: "💬 Cần trợ giúp?" → @tuanai_mentor
```

**File:** `bot/handlers/webapp_setup.py` — `WEBAPP_USAGE_STEPS`, `send_webapp_usage_step()`

---

### Flow 3 — Cập nhật Link Kết Nối Telegram (Settings)

```
Trigger A: Keyboard ⚙️ Cài đặt
     │
     ▼
handle_settings_menu() → InlineKeyboard 2 section:

  ⏰ NHẮC NHỞ:
    [🔔/🔕 Nhắc nhở] [🕗 Giờ nhắc: {hour}h]
    [📅 Tuần / 📆 Tháng toggles]

  🔗 KẾT NỐI:
    [🌐 Đổi Web App URL]
    [📊 Đổi Google Sheet URL]
     │
     ├── settings_toggle_reminder/weekly/monthly
     │       └── toggle DB + refresh keyboard live
     │
     ├── settings_pick_hour → hour grid 05h-22h
     │       └── settings_hour_{N} → save reminder_hour → back
     │
     ├── settings_change_webapp
     │       └── context.user_data['awaiting_settings'] = 'web_app_url'
     │       └── User types URL → handle_settings_url_input (group=-1)
     │       → validate (starts with http) → save user.web_app_url → confirm
     │
     └── settings_change_sheet
             └── context.user_data['awaiting_settings'] = 'webhook_url'
             └── User types URL → handle_settings_url_input (group=-1)
             → validate → save user.webhook_url → confirm

/cancel khi awaiting_settings:
  → cancel_command() (webapp_setup.py) clears 'awaiting_settings' → "❌ Đã huỷ."

Trigger B: connect_webapp_start (từ /taoweb step 6)
  → handle_webapp_url_message() (group=-1, waiting_for_webapp_url)
  → khác với settings flow — đây là first-time setup, hỏi thêm Sheets URL

⚠️ PHÂN BIỆT:
  - settings flow: chỉ update 1 URL, không hỏi URL thứ hai
  - taoweb flow: update cả 2 URL liên tiếp (webapp → sheets)

Tránh trùng lặp:
  - Không tạo bản ghi mới — chỉ overwrite trên User row hiện tại
  - ApplicationHandlerStop sau mỗi URL input để chặn transaction handler
```

**Files:**
- `bot/handlers/transaction.py` — `handle_settings_menu()`, `handle_settings_callback()`, `handle_settings_url_input()`
- `bot/handlers/webapp_setup.py` — `handle_webapp_url_message()`, `handle_sheets_url_message()`, `cancel_command()`

---

### Flow 4 — WEB Deep Link (từ Landing Page)

```
Trigger: https://t.me/FreedomWalletbot?start=WEB_{emailHash}
     │
     ▼
start() handler → code.startswith("WEB_") → emailHash = code[4:]
     │
     ▼
sync_web_registration(user.id, username, emailHash)
  → tìm trong Google Sheets SUPPORT_SHEET_ID
  → match column "🔗 Link giới thiệu" == emailHash

     ├── Success (web_data) → update_user_registration() → check referral_count
     │       ├── count >= 2: UNLOCKED
     │       │     → welcome message → start_onboarding_journey()
     │       │     → enable reminders → return
     │       └── count < 2: NOT UNLOCKED
     │             → show referral link + progress buttons
     │             → start_daily_nurture() → return
     │
     └── Failure (None, e.g. Sheets not configured)  ← GRACEFUL FALLBACK
             → try to credit referrer in local DB:
               query User WHERE referral_code == emailHash
               if found: referrer.referral_count++ + db_user.referred_by = code
             → fall through to normal /start welcome (không block user)
```

**File:** `bot/handlers/start.py` — `start()` WEB_ block, lines ~40–170

---

### Flow 5 — Ghi Giao Dịch (Core Loop)

```
Trigger A: Keyboard ✍️ Ghi giao dịch
Trigger B: Natural text ("cà phê 35k", "lương 15tr thu nhập")

     ▼
handle_quick_transaction() (transaction.py)
  → AI parse (NLP): extract amount, category, type (expense/income), jar
  → save to DB (Transaction table)
  → sync to webhook (user.webhook_url) → POST to Web App
  → reply confirmation with inline buttons:
      [✅ Xác nhận] [✏️ Sửa] [🗑️ Xóa]

Callback: handle_txn_callback()
  → txn_confirm_{id}: finalize
  → txn_edit_{id}: prompt edit  
  → txn_delete_{id}: soft delete

Exit: transaction saved + synced
```

---

### Flow 6 — Referral

```
Trigger: /start REF{referralCode}

     ▼
handle_referral_start() (handlers/referral.py)
  → lookup User WHERE referral_code == code
  → if referrer found:
       - referrer.referral_count++
       - new_user.referred_by = referral_code
       - notify referrer: "🎉 Bạn có người giới thiệu mới!"
       - if referrer.referral_count >= 2 → auto-unlock + onboarding
  → show special welcome to new user
  → fall through to normal /start

Affiliate share (🔗 Chia sẻ button):
  → handle_share() (transaction.py)
  → fetch/generate user.referral_code
  → ref_url = https://t.me/{bot_username}?start={referral_code}
  → show stats (X người đã giới thiệu)
  → buttons: Telegram / Facebook / Zalo / 📋 Copy link (sends <code> message)
```

---

## 5. CẤU TRÚC FILE HANDLER

```
bot/handlers/
├── start.py              ← /start, deep links, welcome
├── transaction.py        ← CORE: keyboard menu, txn, report, settings, share, donate, guide
├── webapp_setup.py       ← /taoweb (create guide), usage guide, URL input, cancel
├── setup_guide.py        ← /huongdan (Sheets guide, guide_step_* callbacks)
├── message.py            ← AI parser (group=100, last resort)
├── referral.py           ← referral credit logic
├── registration.py       ← ConversationHandler /register
├── onboarding.py         ← scheduled onboarding journey (day 1+)
├── daily_nurture.py      ← nurture messages for non-unlocked users
├── daily_reminder.py     ← reminder registration
├── webapp_url_handler.py ← (legacy) additional URL handlers → xem note bên dưới
├── callback.py           ← (legacy) global callback fallback
├── vip.py                ← VIP identity tier handlers
├── admin_*.py            ← admin: fraud, payment, metrics
└── [các file khác]       ← streak, celebration, premium, quick_record, etc.
```

**⚠️ Lưu ý quan trọng — handler phân tán:**
- `transaction.py` xử lý toàn bộ main keyboard (✍️📊📂🌐🔗💝📖⚙️)
- `webapp_setup.py::handle_keyboard_menu` xử lý keyboard cũ ("💰 Ghi thu chi", "🌐 Mở Web Apps", v.v.) — keyboard này vẫn active với một số user
- `webapp_url_handler.py` có thể gây duplicate với `handle_webapp_url_message` trong `webapp_setup.py`

---

## 6. DATABASE SCHEMA (các field quan trọng)

```sql
User
├── id                  (Telegram user_id)
├── referral_code       (dùng cho affiliate link)
├── referral_count      (số người đã giới thiệu)
├── referred_by         (referral_code của người giới thiệu)
├── web_app_url         (Google Apps Script /exec URL)
├── webhook_url         (alias cho web_app_url — dùng để POST giao dịch)
├── google_sheets_url   (URL xem Google Sheets)
├── spreadsheet_id      (extracted ID từ sheets URL)
├── sheets_connected_at (timestamp)
├── reminder_enabled    (bool)
├── reminder_hour       (int, default 8)
├── weekly_reminder_enabled  (bool)
├── monthly_reminder_enabled (bool)
├── subscription_tier   ("FREE" | "PREMIUM")
└── [các field khác]

Transaction
├── user_id, amount, type (expense/income)
├── category, jar
├── description, raw_text
└── synced_at, deleted_at
```

---

## 7. FLOW TRÙNG LẶP — PHÂN TÍCH & ĐỀ XUẤT

### Đang hoạt động song song (chấp nhận được)

| Flow | File 1 | File 2 | Ghi chú |
|---|---|---|---|
| Keyboard menu | `transaction.py::handle_keyboard_menu` | `webapp_setup.py::handle_keyboard_menu` | Hai keyboard khác nhau (main vs old). Không xung đột nếu button text khác nhau. |
| URL input | `transaction.py::handle_settings_url_input` | `webapp_setup.py::handle_webapp_url_message` | Hai context khác (settings vs first-time setup). OK. |
| Guide step* callbacks | `setup_guide.py::guide_callback_handler` | `webapp_setup.py::webapp_callback_handler` | `guide_step_*` → setup_guide; `webapp_step_*` / `webapp_usage_step_*` → webapp_setup. Prefix tách biệt. OK. |

### Cần theo dõi (rủi ro trùng lặp)

| Issue | Nguyên nhân | Recommendation |
|---|---|---|
| `webapp_url_handler.py` | Đăng ký riêng URL handlers qua `register_webapp_handlers` | Kiểm tra xem có conflict với `handle_webapp_url_message` không. Nếu trùng, disable `webapp_url_handler.py`. |
| 3 quick_record handlers | `quick_record_direct.py`, `quick_record_template.py`, `quick_record_webhook.py` | Chỉ 1 được dùng thực sự. Tắt 2 cái còn lại. |
| `registration.py` + `free_registration.py` + `inline_registration.py` | 3 ConversationHandler cho đăng ký | Audit xem ConversationHandler nào đang active. Tắt những cái không dùng. |
| `callback.py` | Global `CallbackQueryHandler(handle_callback)` ở cuối main.py | Là fallback tốt, nhưng check không xử lý lại những callback đã được handle trước đó. |

---

## 8. NGUYÊN TẮC KHI NÂNG CẤP

### ✅ ĐƯỢC làm

1. **Thêm feature mới vào file hiện tại** — đừng tạo file handler mới trừ khi feature hoàn toàn độc lập
2. **Dùng `context.user_data`** để track trạng thái nhập liệu ngắn hạn
3. **Raise `ApplicationHandlerStop`** sau khi xử lý xong keyboard button ở group=-2
4. **DB migration** khi thêm column — tạo file `migrations/add_{feature}.py`
5. **Thêm log** với `logger.info(f"User {user_id} ...")`

### ❌ KHÔNG được làm

1. **Không tạo ConversationHandler mới** nếu có thể dùng `context.user_data` state
2. **Không đăng ký `CallbackQueryHandler` global** mới — dùng pattern cụ thể
3. **Không tạo flow registration mới** — đã có `registration.py`, `free_registration.py`, WEB_ deep link
4. **Không thay đổi handler group numbers** (=-2, -1, 0, 100) — logic priority hiện tại đang stable
5. **Không sửa `ApplicationHandlerStop`** logic — sẽ phá vỡ keyboard flow

### 🔁 Quy trình thêm handler mới

```
1. Xác định: feature thuộc file nào? (transaction.py / webapp_setup.py / start.py)
2. Thêm function vào file đó
3. Đăng ký trong register_*_handlers() của file đó
4. Nếu cần DB column: tạo migration script
5. Test: chạy bot, kiểm tra không có double response
6. Update ARCHITECTURE_OVERVIEW.md (phần này)
```

---

## 9. DEPLOYMENT

**Local:**
```powershell
Set-Location D:\Projects\FreedomWalletBot
.\.venv\Scripts\python.exe main.py
```

**Restart:**
```powershell
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Set-Location D:\Projects\FreedomWalletBot
.\.venv\Scripts\python.exe main.py
```

**Env vars cần thiết:**
```
TELEGRAM_BOT_TOKEN=xxx
DATABASE_URL=sqlite:///./data/freedom_wallet.db
TEMPLATE_SPREADSHEET_ID=xxx        # Google Sheets template ID
SUPPORT_SHEET_ID=xxx               # (Optional) Sheets ID cho WEB_ sync
GOOGLE_SERVICE_ACCOUNT_KEY=xxx     # (Optional) Cho Sheets sync
LOG_LEVEL=INFO
ENV=development
```

**Nếu thiếu `SUPPORT_SHEET_ID` hoặc Google credentials:**
- WEB_ deep link flow sẽ gracefully fallback (không block user)
- Reminder sync qua Google Sheets sẽ skip

---

## 10. MONITORING & LOGS

Logs: `data/logs/bot.log` (UTF-8)

Pattern quan trọng để theo dõi:
```
✅ Bot started
❌ Failed to register * handlers   ← check import error
⚠️ WEB_ sheet lookup failed        ← Sheets config missing (OK, graceful)
User {id} started with code: WEB_  ← landing page conversion
User {id} started with code: REF   ← referral conversion
```

---

*File này là nguồn tham chiếu duy nhất cho kiến trúc hệ thống.*
*Khi thay đổi flow quan trọng, cập nhật file này trước khi merge code.*
