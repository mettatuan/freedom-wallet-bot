# 🔄 MIGRATION NOTES - v2.0.0
**Unified Flow Architecture Migration Guide**

Release: v2.0.0  
Date: 2026-02-17  
Impact: **MEDIUM** (Backward compatible, soft integration)

---

## 📋 OVERVIEW

Version 2.0.0 introduces a unified state and tier system to replace the legacy referral-based logic. This migration is **backward compatible** with automatic migration strategy.

**No breaking changes** - existing users continue working normally.

---

## 🎯 WHAT'S CHANGING

### **1. State Management**

**Before (v1.x):**
```python
# Legacy approach
user.referral_count >= 2  # Determines VIP status
user.is_free_unlocked  # Boolean flag
```

**After (v2.0):**
```python
# Unified state machine
user.user_state = "VIP"  # Explicit state
user.subscription_tier = "UNLOCK"  # Separate tier
```

**Benefits:**
- ✅ Clear separation: State (journey) vs Tier (access)
- ✅ Validated transitions (cannot skip states)
- ✅ Audit trail (all transitions logged)
- ✅ Future-proof (easy to add new states)

---

### **2. Subscription Tiers**

**Before (v1.x):**
```python
user.subscription_tier in ["TRIAL", "FREE", "PREMIUM"]
user.is_free_unlocked  # Separate flag
```

**After (v2.0):**
```python
user.subscription_tier in ["FREE", "UNLOCK", "PREMIUM"]
# TRIAL merged into FREE
# is_free_unlocked replaced by UNLOCK tier
```

**Migration Strategy:**
- `TRIAL` → `FREE` (auto-convert on first interaction)
- `is_free_unlocked=True` → `UNLOCK` tier

---

### **3. Files Structure**

**New Files:**
- ✅ `app/core/unified_states.py` - State & tier definitions
- ✅ `version.py` - Version management
- ✅ `RoadmapAutoInsert_v2.gs` - Dynamic roadmap system
- ✅ `FLOW_MAP.md` - Complete flow documentation
- ✅ `TESTING_GUIDE.md` - Testing framework
- ✅ `DEAD_CODE_REMOVAL_LIST.md` - Cleanup tracking

**Modified Files:**
- ✅ `app/core/state_machine.py` - Enhanced with unified states
- ✅ `CHANGELOG.md` - Updated with v2.0.0 release notes

**Deprecated (but kept for compatibility):**
- `app/core/states.py` - Old state definitions (still works)
- Legacy referral_count logic (still supported)

---

## 🚀 MIGRATION STEPS

### **Step 1: Update Codebase**

```bash
# Pull latest code
git pull origin main

# Install dependencies (if any new)
pip install -r requirements.txt

# Verify version
python version.py
# Should output: v2.0.0
```

---

### **Step 2: Database Migration (AUTO)**

**No manual migration needed!** 

The system uses a **DUAL-RUN strategy:**

1. **Existing users (LEGACY):**
   - Keep current `user_state` = `NULL` or old value
   - System infers state from `referral_count`
   - Auto-migrates on first state transition

2. **New users:**
   - Use new state machine from day 1
   - Proper state tracking from registration

**Example Auto-Migration:**
```python
# User with referral_count=3, user_state=NULL
state_mgr = StateManager()
state, is_legacy = state_mgr.get_user_state(user_id)
# Returns: (UserState.VIP, is_legacy=True)

# Trigger transition (e.g., update activity)
state_mgr.transition_user(user_id, UserState.VIP)
# Auto-migrates: Sets user_state="VIP" in DB
```

---

### **Step 3: Update Roadmap System**

**Option A: Keep Both (Recommended)**

Keep old `RoadmapAutoInsert.gs` and add new `RoadmapAutoInsert_v2.gs` side-by-side.

```
1. Open Google Apps Script
2. Create new file: RoadmapAutoInsert_v2.gs
3. Copy contents from project file
4. Save
5. Test with: testInsertItem()
```

**Option B: Replace Old Script**

```
1. Backup old script (copy to text file)
2. Replace contents with v2.0 code
3. Run: migrateOldData() (one-time)
4. Test with: testInsertItem()
```

---

### **Step 4: Test System**

```bash
# Run full test suite
pytest tests/ -v

# Run specific migration tests
pytest tests/unit/test_state_machine.py::test_legacy_user_migration -v

# Check coverage
pytest --cov=app --cov-report=term-missing
```

**Expected Results:**
- ✅ All tests pass
- ✅ Coverage ≥ 90%
- ✅ No errors in logs

---

### **Step 5: Monitor Production**

After deployment, monitor:

1. **User State Transitions:**
```sql
-- Check auto-migrations
SELECT 
    COUNT(*) as legacy_users,
    user_state
FROM users
WHERE user_state = 'LEGACY' OR user_state IS NULL
GROUP BY user_state;
```

2. **Error Logs:**
```bash
tail -f data/logs/bot.log | grep "ERROR\|WARN"
```

3. **Roadmap Updates:**
- Check Google Sheet for new entries
- Verify status formatting
- Test dynamic functions

---

## 🔍 COMPATIBILITY MATRIX

| Component | v1.x | v2.0 | Compatible? |
|-----------|------|------|-------------|
| User model | `referral_count` | `user_state` | ✅ Yes (dual-run) |
| Subscription | TRIAL/FREE/PREMIUM | FREE/UNLOCK/PREMIUM | ✅ Auto-convert |
| Referral logic | Count-based | State-based | ✅ Both work |
| Handlers | Old imports | New imports | ✅ Both work |
| Database | 56 columns | 56 columns | ✅ No schema change |

---

## ⚠️ BREAKING CHANGES

**None!** This is a **soft integration** migration.

All existing code continues to work. New code uses unified states.

---

## 🐛 TROUBLESHOOTING

### **Issue: User state stuck at LEGACY**

**Cause:** User hasn't triggered a state transition yet.

**Fix:**
```python
# Manually migrate user
from app.core.state_machine import StateManager, UserState

with StateManager() as mgr:
    mgr.transition_user(user_id, UserState.VIP, "Manual migration")
```

---

### **Issue: Roadmap script not found**

**Cause:** New script not deployed to Google Apps Script.

**Fix:**
1. Open Google Sheets
2. Extensions → Apps Script
3. Copy `RoadmapAutoInsert_v2.gs` contents
4. Save and authorize

---

### **Issue: Tests fail with "UserState not found"**

**Cause:** Old import statement.

**Fix:**
```python
# Old (v1.x)
from app.core.states import UserState

# New (v2.0)
from app.core.state_machine import UserState
# OR
from app.core.unified_states import UserState, SubscriptionTier
```

---

### **Issue: Subscription tier mismatch**

**Cause:** User has `is_free_unlocked=True` but `subscription_tier=FREE`.

**Fix:**
```python
# Run tier sync script
from app.utils.database import SessionLocal, User

session = SessionLocal()
users = session.query(User).filter(
    User.is_free_unlocked == True,
    User.subscription_tier == "FREE"
).all()

for user in users:
    user.subscription_tier = "UNLOCK"
    print(f"Fixed user {user.id}: FREE → UNLOCK")

session.commit()
```

---

## 📊 ROLLBACK PLAN

If critical issues occur, rollback is simple:

### **Step 1: Revert Code**

```bash
git revert HEAD
git push origin main
```

### **Step 2: Redeploy Old Version**

```bash
# Railway.app will auto-deploy previous commit
# OR manually trigger:
railway up
```

### **Step 3: Verify**

```bash
# Check version
curl https://your-bot-url.railway.app/health
# Should return: v1.x.x
```

**Data Safety:**
- ✅ No database changes required
- ✅ State machine is additive only
- ✅ Old logic still works

---

## 🎯 POST-MIGRATION CHECKLIST

After successful deployment:

- [ ] All tests passing
- [ ] No errors in production logs
- [ ] User registration working
- [ ] Referral flow working
- [ ] State transitions logged
- [ ] Roadmap updates working
- [ ] CHANGELOG.md updated
- [ ] Version.py shows v2.0.0
- [ ] Documentation deployed
- [ ] Team notified

---

## 📞 SUPPORT

If issues arise:

1. **Check Logs:**
   ```bash
   tail -f data/logs/bot.log
   ```

2. **Run Diagnostics:**
   ```bash
   python -c "from app.core.state_machine import StateManager; print('OK')"
   ```

3. **Contact Team:**
   - Slack: #freedom-wallet-dev
   - Email: dev@freedomwallet.com

---

## 📚 ADDITIONAL RESOURCES

- [FLOW_MAP.md](FLOW_MAP.md) - Complete system architecture
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing framework
- [CHANGELOG.md](CHANGELOG.md) - Release history
- [RoadmapAutoInsert_v2.gs](RoadmapAutoInsert_v2.gs) - Roadmap API

---

**Migration Status:** ✅ READY FOR PRODUCTION  
**Risk Level:** 🟢 LOW (Backward compatible)  
**Estimated Downtime:** 0 minutes  
**Auto-Migration:** ✅ Enabled

**Last Updated:** 2026-02-17  
**Version:** 2.0.0  
**Author:** Freedom Wallet Team
