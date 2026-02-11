# Freedom Wallet Bot - Full System Review Checklist

## 🎯 Current Status
- **API Issue**: Authentication failing (Invalid API key)
- **Categories Not Loading**: Fixed by adding web_app_url support
- **Payment System**: Working with Google Sheets logging
- **Quick Record**: Enhanced UI with category suggestions

---

## 1. 🔐 Premium Registration & Payment Flow

### Current Implementation
- [ ] **Trial System**: 7-day free trial on signup
- [ ] **Payment Verification**: VietQR → Admin approval → Activate Premium
- [ ] **Renewal Logic**: Smart renewal (extend from current expiry)
- [ ] **Google Sheets Logging**: 11 columns with status tracking

### Issues Found
- [ ] User.spreadsheet_id and User.web_app_url not set on signup
- [ ] No automatic connection after payment approval
- [ ] Missing onboarding flow after Premium activation

### Fixes Needed
1. Auto-set spreadsheet_id when user gets Premium
2. Create onboarding message with /connectsheets guide
3. Add Premium benefits showcase
4. Implement payment expiry reminder (7 days before)

---

## 2. 🤖 AI Assistant - Financial Advisor

### Current Capabilities
- ✅ Context-aware conversations (5 message history)
- ❌ No transaction context integration
- ❌ No proactive insights/tips
- ❌ Doesn't understand "Thu 50tr lương"

### Enhancement Needed
1. **Transaction Context**:
   - Feed recent transactions to AI context
   - AI suggests categories based on history
   - Spending pattern analysis

2. **Smart Responses**:
   - "Thu 50tr lương" → AI understands: Income, amount 50M, category Salary
   - "Mua cà phê 50k" → Expense, Ăn uống, 50k
   - Incomplete info → AI asks clarification

3. **Proactive Tips**:
   - Budget warnings: "Chi tiêu tháng này cao hơn 20%"
   - Savings goals: "Bạn đã tiết kiệm được 30% mục tiêu"
   - Category insights: "Chi Ăn uống nhiều nhất: 5tr"

### Code Structure
```
bot/handlers/ai_assistant_handler.py
- build_ai_context() → Add transaction history
- handle_ai_message() → Smart parsing fallback
```

---

## 3. 📝 Quick Record - Smart Transaction Entry

### Current Flow
```
User: "Thu 50tr lương"
  ↓
Parse: type=Thu, amount=50M, note="lương"
  ↓
Match category: CategoriesModule.getAll() → match "Lương"
  ↓
If matched: Show confirmation with auto-allocated jars
If not: Show category suggestions (6 popular + "Xem thêm")
  ↓
User confirms → Call API addTransaction
```

### Issues Found
1. **API Authentication**: Invalid API key (BLOCKING)
2. **No fallback categories**: If API fails, no suggestions shown
3. **Missing UserService**: Code references non-existent UserService
4. **Duplicate SheetsAPIClient calls**: Not using user.web_app_url

### Fixes Applied ✅
- [x] Enhanced keyword matching (income: lương, thưởng, etc.)
- [x] Added popular categories fallback
- [x] Changed UI: Category buttons instead of jar-only
- [x] Auto-allocate button for income with TRUE flag
- [x] Added user.web_app_url support in test script

### Fixes Needed
1. Fix API authentication (comment out or add correct key)
2. Fix UserService references → Use db.query(User) directly
3. Add success message with balance update
4. Add undo feature (last 5 transactions)

---

## 4. 🧹 Code Quality & Architecture

### Files to Clean
1. **bot/handlers/quick_record_template.py** (1387 lines)
   - Split into: parser.py, category_matcher.py, ui_builder.py
   - Remove duplicate get_categories calls
   - Extract jar allocation logic

2. **bot/handlers/admin_callbacks.py** (347 lines)
   - log_payment_to_sheets(): Optimize UPDATE logic
   - Extract color formatting to utils

3. **bot/handlers/message.py** (579 lines)
   - Extract rejection logic to payment_service
   - Remove HTML escaping duplication

### Architecture Improvements
```
bot/
  services/
    category_service.py         # NEW: Category matching logic
    transaction_parser.py       # NEW: Parse user message
    jar_allocator.py           # NEW: 6-jar allocation rules
    
  handlers/
    quick_record/              # NEW: Split handler
      __init__.py
      parser.py
      category_selector.py
      confirmation.py
```

---

## 5. 🔧 Apps Script Integration

### Current Issues
- ❌ API key mismatch: Bot uses "fwb_bot_testing_2026", Apps Script expects different key
- ❌ Each user has different webapp_url, bot uses default URL
- ✅ getCategories endpoint exists and working

### Solutions
**Option A: Disable Auth (Quick Fix)**
```javascript
// In Code.gs doPost()
// Comment out API key validation for testing
// if (!apiKey || !VALID_API_KEYS[apiKey]) { ... }
```

**Option B: Correct Key**
- Find actual API key in Apps Script VALID_API_KEYS
- Update .env: FREEDOM_WALLET_API_KEY=<correct_key>

**Option C: Per-User WebApp**
- Each user deploys own Apps Script
- Bot stores user.web_app_url during /connectsheets
- SheetsAPIClient uses user.web_app_url

**Recommendation**: Option C (already implemented, just need to fix auth)

---

## 6. 🧪 Testing Plan

### Manual Test Flow
1. **New User Journey**
   ```
   /start → Welcome + Trial 7 days
   /premium → Payment instruction
   Send screenshot → Admin approves
   User gets Premium → Auto-prompt /connectsheets
   Share Google Sheets → Bot saves spreadsheet_id
   "Thu 50tr lương" → Bot suggests "Lương" category
   Confirm → Transaction recorded, balance updated
   ```

2. **AI Assistant Test**
   ```
   "Tôi vừa nhận lương 50 triệu"
   → AI: "Chúc mừng! Bạn muốn ghi thu nhập này vào sổ không?"
   
   "Tôi chi bao nhiêu tháng này?"
   → AI: (query transactions) "Bạn đã chi 15 triệu tháng này"
   ```

3. **Edge Cases**
   ```
   "50k" → Amount too vague, ask clarification
   "Thu lương" → No amount, ask amount
   "Mua" → No category, show suggestions
   ```

---

## 7. 📚 Documentation Needed

1. **USER_GUIDE.md**
   - Premium benefits
   - How to use quick record
   - 6-jar allocation explained
   - AI assistant tips

2. **DEPLOYMENT.md**
   - Apps Script setup for users
   - Bot configuration
   - Database migration

3. **API_REFERENCE.md**
   - All bot commands
   - Apps Script endpoints
   - Webhook setup

---

## 🚀 Priority Actions (Next 2 Hours)

### Critical (BLOCKING) 🔴
1. **Fix API Authentication**
   - Test with API key: Check Apps Script VALID_API_KEYS
   - Or: Comment out auth in Code.gs doPost()
   - Test: python test_get_categories_api.py should return categories

2. **Fix UserService References**
   - Replace: `user = await UserService.get_user_by_telegram_id(user_id)`
   - With: 
   ```python
   db = next(get_db())
   user = db.query(User).filter(User.id == user_id).first()
   ```

### High Priority 🟡
3. **Complete Quick Record Flow**
   - Fix remaining SheetsAPIClient(user.web_app_url) calls
   - Test full flow: "Thu 50tr lương" → Recorded successfully
   
4. **Restart Bot with All Fixes**
   - Kill old process
   - Start new: python main.py
   - Test in Telegram

### Nice to Have 🟢
5. **AI Context Enhancement**
   - Add transaction history to AI context
   - Smart category suggestions
   
6. **Code Cleanup**
   - Split quick_record_template.py
   - Extract reusable utilities

---

## 🎯 Success Criteria

**Bot is ready for users when:**
- [ ] User can sign up and get 7-day trial ✅
- [ ] User can pay and get approved ✅
- [ ] User can connect Google Sheets ❌ (need to guide)
- [ ] User types "Thu 50tr lương" → Bot records correctly ❌ (API auth)
- [ ] AI Assistant understands context and helps ❌ (need enhancement)
- [ ] No errors in logs ❌ (UserService errors)
- [ ] All tests pass ❌ (need to run)

**Current Status**: 60% Complete
**Blockers**: API auth, UserService, incomplete testing
**ETA**: 2-3 hours to complete all fixes

---

## 📋 Implementation Order

1. Fix API auth (15 min)
2. Fix UserService (30 min)
3. Complete SheetsAPIClient (15 min)
4. Test full flow (30 min)
5. AI enhancement (1 hour)
6. Code cleanup (30 min)
7. Documentation (30 min)

**Total**: ~3.5 hours
