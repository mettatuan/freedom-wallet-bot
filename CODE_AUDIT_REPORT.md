# CODE AUDIT REPORT - FreedomWallet Bot
**Date:** February 12, 2026  
**Status:** 🔴 CRITICAL ISSUES FOUND

---

## 🚨 CRITICAL BUGS

### 1. **MISSING VALIDATION: Transaction Without Setup**
**Location:** `src/presentation/handlers/transaction_handler.py` line 51-150

**Problem:**
- CA transaction handler KHÔNG kiểm tra `sheet_url` và `webapp_url`
- User có thể ghi transaction TRƯỚC KHI setup Sheet
- Data sẽ chỉ lưu vào database local, KHÔNG sync lên Google Sheet
- User nghĩ đã ghi thành công nhưng data bị MẤT!

**Current Code:**
```python
async def quick_record_transaction(...):
    # Skip conversation check
    if context.user_data:
        return None
    
    # Parse transaction
    # ... No validation of sheet_url or webapp_url!
    
    # Direct execute use case
    result = await record_use_case.execute(...)
```

**Impact:** 🔴 HIGH - Data loss for users

**Fix Required:**
```python
# Check if user has completed setup
user_entity = await user_repository.get_by_id(user.id)
if not user_entity or not user_entity.sheet_url or not user_entity.webapp_url:
    await update.message.reply_text(
        "⚠️ Bạn chưa setup Sheet!\n\n"
        "Vui lòng setup trước khi ghi chi tiêu:\n"
        "/setup"
    )
    return
```

---

## 🔄 FILE DUPLICATION ISSUES

### 2. **Transaction Handlers: 7 FILES doing same thing!**

| # | File Path | Function | Status |
|---|-----------|----------|--------|
| 1 | `src/presentation/handlers/transaction_handler.py` | `quick_record_transaction()` | ✅ CA (Active) |
| 2 | `src/application/use_cases/record_transaction.py` | `RecordTransactionUseCase` | ✅ CA (Active) |
| 3 | `bot/handlers/quick_record_template.py` | `handle_quick_record()` | ⚠️ Legacy |
| 4 | `bot/handlers/quick_record_direct.py` | Direct handler | ⚠️ Legacy |
| 5 | `bot/handlers/quick_record_webhook.py` | Webhook handler | ⚠️ Legacy |
| 6 | `bot/handlers/premium_commands.py` | `quick_record_handler()` | ⚠️ Legacy |
| 7 | `bot/handlers/user_commands.py` | `record_transaction_command()` | ⚠️ Legacy |

**Registered in main.py:**
- Line 321-325: `register_quick_record_handlers()` - Legacy template
- Line 377: `ca_quick_record_transaction` (group 90) - CA
- Both run simultaneously → CONFLICT!

**Impact:** 🟡 MEDIUM - Confusion, hard to maintain

---

### 3. **Start Handlers: 2 FILES**

| File | Lines | Status |
|------|-------|--------|
| `bot/handlers/start.py` | 369 lines | Legacy (active when CA=False) |
| `src/presentation/handlers/start_handler.py` | 151 lines | CA (active when CA=True) |

**Registered in main.py:**
- Line 191: CA start (group 0)
- Line 248: Legacy start (no group specified)

**Problem:** 
- Legacy start still shows in `bot/handlers/start.py` line 40-260
- Contains WEB registration flow that may not work with CA schema

---

### 4. **Registration Handlers: 2 SYSTEMS**

| Type | Location | Entry Points |
|------|----------|--------------|
| Legacy | `bot/handlers/registration.py` | `/register`, ~~`start_free_registration`~~ (removed) |
| CA | `src/presentation/handlers/sheets_handler.py` | `/setup_ca`, `setup_sheet`, `start_free_registration` |

**Registered in main.py:**
- Line 157-184: Legacy registration_handler
- Line 207-232: CA setup_conversation (group 0)
- Line 250: Legacy registration_handler (DISABLED when CA=True) ✅

**Status:** Partially fixed - Legacy disabled when CA enabled

---

## 📊 HANDLER REGISTRATION MAP

### main.py Handler Groups:

```
Group 0 (Highest Priority):
├─ CA /start command (line 191)
├─ CA callback handlers (lines 201-203)
└─ CA setup_conversation (line 232)

No Group (Default):
├─ Legacy /start (line 248, disabled when CA=True)
├─ Legacy registration (line 250, disabled when CA=True)
├─ /help, /mystatus, /referral (lines 252-254)
└─ support_handler (line 255)

Group 50:
└─ Photo handler (payment proof)

Group 90:
└─ ca_quick_record_transaction (line 377)

Group 100 (Lowest Priority):
└─ handle_message - AI fallback (line 386)
```

**Problem:** Legacy handlers still registered globally, not in `if not USE_CLEAN_ARCHITECTURE` block!

---

## 🎯 RECOMMENDATIONS

### IMMEDIATE (P0):
1. ✅ **Add validation** to CA transaction handler
   - Check `sheet_url` exists
   - Check `webapp_url` exists
   - Return error message if not setup

### SHORT TERM (P1):
2. **Move ALL legacy handlers** inside `if not USE_CLEAN_ARCHITECTURE:` block
   - Lines 260-325 should be conditional
   - Only register when CA is disabled

3. **Remove duplicate transaction handlers:**
   - Keep: CA handler (transaction_handler.py)
   - Archive: All 5 legacy quick_record files

### MEDIUM TERM (P2):
4. **Consolidate start handlers:**
   - Remove `bot/handlers/start.py`
   - Migrate any unique logic to CA version

5. **Clean up registration:**
   - Remove `bot/handlers/registration.py`
   - Use only CA sheets_handler

### LONG TERM (P3):
6. **File structure reorganization:**
   ```
   src/
   ├─ presentation/handlers/
   │  ├─ start_handler.py ✅ Keep
   │  ├─ sheets_handler.py ✅ Keep
   │  └─ transaction_handler.py ✅ Keep (after fix)
   
   bot/handlers/ → _archive/legacy_handlers/
   ├─ start.py ⚠️ Archive
   ├─ registration.py ⚠️ Archive
   ├─ quick_record_template.py ⚠️ Archive
   ├─ quick_record_direct.py ⚠️ Archive
   ├─ quick_record_webhook.py ⚠️ Archive
   └─ premium_commands.py ⚠️ Need review
   ```

---

## 📝 NAMING INCONSISTENCIES

### Handlers with same name "receive_email":
1. `src/presentation/handlers/sheets_handler.py:receive_email` - CA version
2. `bot/handlers/registration.py:receive_email` - Legacy version

**Both registered in main.py:**
- Line 166: Legacy (in AWAITING_EMAIL state)
- Line 215: CA (in CA_AWAITING_EMAIL state)

### Handlers with "quick_record":
- 7 different files/functions with this name!
- Very confusing for debugging

---

## ✅ ACTION PLAN

### Phase 1: Emergency Fix (Today)
- [ ] Add sheet_url validation to CA transaction handler
- [ ] Test validation with /start → register flow

### Phase 2: Handler Isolation (This week)
- [ ] Move all legacy handlers to conditional block
- [ ] Verify CA handlers work standalone
- [ ] Update tests

### Phase 3: Cleanup (Next week)
- [ ] Archive duplicate files to `_archive/legacy_handlers/`
- [ ] Remove legacy code from main.py
- [ ] Update documentation

---

## 📌 NOTES

**Current Architecture Status:**
- CA Phase 6 Complete ✅
- USE_CLEAN_ARCHITECTURE = True
- But legacy code still active! ⚠️

**Technical Debt:**
- 13+ duplicate handler files
- Mixed schema (users.id vs users.user_id)
- No proper feature flag isolation

---

*Generated by: Code Audit Tool*  
*Next Review: After Phase 1 fixes*
