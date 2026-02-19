# ✅ DEPLOYMENT CHECKLIST - v2.0.0
**Freedom Wallet Bot - Unified Flow Architecture**

**Release Date:** 2026-02-17  
**Version:** v2.0.0  
**Risk Level:** 🟢 LOW (Backward compatible)

---

## 📋 PRE-DEPLOYMENT

### **Code Review**

- [ ] Review `app/core/unified_states.py`
- [ ] Review `app/core/state_machine.py`
- [ ] Review `app/services/roadmap_service.py`
- [ ] Review `version.py`
- [ ] Review `RoadmapAutoInsert_v2.gs`

### **Documentation Review**

- [ ] Read `FLOW_MAP.md`
- [ ] Read `TESTING_GUIDE.md`
- [ ] Read `MIGRATION_NOTES.md`
- [ ] Read `IMPLEMENTATION_SUMMARY_v2.md`
- [ ] Read `QUICK_START_v2.md`

### **Testing**

- [ ] Run all unit tests: `pytest tests/unit/ -v`
- [ ] Run integration tests: `pytest tests/integration/ -v`
- [ ] Run E2E tests: `pytest tests/e2e/ -v`
- [ ] Check coverage: `pytest --cov=app --cov-report=term-missing`
- [ ] Verify ≥90% coverage target

### **Environment Setup**

- [ ] Set `ROADMAP_APPS_SCRIPT_URL` in `.env`
- [ ] Verify Python 3.11+ installed
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Install test deps: `pip install pytest pytest-asyncio pytest-cov`

---

## 🚀 DEPLOYMENT STEPS

### **1. Backup Current System**

```bash
# Backup database
pg_dump freedom_wallet_bot > backup_$(date +%Y%m%d).sql

# Backup current code
git tag -a v1.x.x -m "Pre-v2.0 backup"
git push origin v1.x.x
```

- [ ] Database backup created
- [ ] Git tag created
- [ ] Backup verified

### **2. Deploy Code**

```bash
# Verify clean working directory
git status

# Commit v2.0 changes
git add .
git commit -m "Release v2.0.0: Unified Flow Architecture"

# Tag release
git tag -a v2.0.0 -m "v2.0.0: Unified Flow Architecture"

# Push to main
git push origin main
git push origin v2.0.0
```

- [ ] Changes committed
- [ ] Release tagged
- [ ] Pushed to repository

### **3. Deploy to Railway**

```bash
# Railway auto-deploys from main branch
# Monitor deployment in Railway dashboard
```

- [ ] Deployment triggered
- [ ] Build successful
- [ ] Health check passed

### **4. Deploy Roadmap Script**

**Manual Steps:**

1. Open Google Sheets with roadmap
2. Extensions → Apps Script
3. Create new file: `RoadmapAutoInsert_v2.gs`
4. Copy contents from `c:\Projects\FreedomWalletBot\RoadmapAutoInsert_v2.gs`
5. Save
6. Run: `testInsertItem()`
7. Authorize permissions

- [ ] Script file created
- [ ] Code copied
- [ ] Test function run successfully
- [ ] Permissions authorized

### **5. Configure Environment**

**In Railway Dashboard:**

1. Go to Variables
2. Add: `ROADMAP_APPS_SCRIPT_URL`
3. Value: Your deployed Apps Script URL
4. Redeploy

- [ ] Environment variable added
- [ ] Service redeployed
- [ ] Variable verified

---

## ✅ POST-DEPLOYMENT VERIFICATION

### **Health Checks**

```bash
# Check bot is running
curl https://your-bot-url.railway.app/health

# Expected: {"status": "ok", "version": "2.0.0"}
```

- [ ] Health endpoint responds
- [ ] Version shows v2.0.0
- [ ] No errors in response

### **Functional Tests**

**Test 1: New User Registration**
- [ ] Send `/start` to bot
- [ ] Complete registration flow
- [ ] Verify user created in DB
- [ ] Verify `user_state = "REGISTERED"`
- [ ] Verify `subscription_tier = "FREE"`

**Test 2: Referral Flow**
- [ ] User A generates referral link
- [ ] User B clicks link
- [ ] User B registers
- [ ] Verify `user_b.referred_by = user_a.id`
- [ ] Verify `user_a.referral_count += 1`
- [ ] Refer 1 more user
- [ ] Verify User A auto-upgrades to VIP

**Test 3: State Transition**
- [ ] Check user state via `/mystatus` or admin panel
- [ ] Verify state transitions logged
- [ ] No invalid transition errors

**Test 4: Roadmap Sync**
- [ ] Manually call roadmap service
- [ ] Verify new row in Google Sheet
- [ ] Verify status formatting applied
- [ ] No duplicate entries

### **Database Checks**

```sql
-- Check state distribution
SELECT user_state, COUNT(*) 
FROM users 
GROUP BY user_state;

-- Expected: Mix of LEGACY, REGISTERED, VIP, etc.

-- Check legacy users
SELECT COUNT(*) 
FROM users 
WHERE user_state = 'LEGACY' OR user_state IS NULL;

-- Should decrease over time as users interact
```

- [ ] Query executed
- [ ] Results make sense
- [ ] No unexpected states

### **Log Monitoring**

```bash
# Monitor logs for 30 minutes
tail -f data/logs/bot.log | grep "ERROR\|WARN\|State transition"
```

**Watch for:**
- [ ] No ERROR messages
- [ ] State transitions logged correctly
- [ ] No invalid transition warnings
- [ ] Legacy user migrations happening

---

## 🔧 POST-DEPLOYMENT TASKS

### **Week 1: Monitor**

- [ ] Day 1: Monitor logs every hour
- [ ] Day 2-3: Monitor logs twice daily
- [ ] Day 4-7: Monitor logs daily
- [ ] Check error rates in Railway dashboard
- [ ] Verify no spike in support tickets

### **Week 2: Optimize**

- [ ] Review state transition patterns
- [ ] Identify slow queries
- [ ] Optimize if needed
- [ ] Update documentation if gaps found

### **Week 3: Scale**

- [ ] Check auto-scaling metrics
- [ ] Verify performance under load
- [ ] Add more integration tests if needed
- [ ] Plan next features

---

## 🗑️ CLEANUP (After 1 Week Success)

### **Remove Dead Code**

Execute commands from `DEAD_CODE_REMOVAL_LIST.md`:

```bash
# Create safety folder
mkdir _to_delete

# Move deprecated files
mv test_sheets_flow.py _to_delete/
mv test_full_flow.py _to_delete/
mv test_button_flow.py _to_delete/
mv fix_encoding.py _to_delete/
mv fix_encoding_safe.py _to_delete/
mv fix_with_ftfy.py _to_delete/

# Run tests to verify
pytest tests/ -v

# If all pass, delete after review
# rm -rf _to_delete/
```

- [ ] Files moved to `_to_delete/`
- [ ] Tests still pass
- [ ] Team approved deletion
- [ ] Files permanently deleted

---

## 📊 SUCCESS METRICS

Track these metrics for 2 weeks:

| Metric | Target | Actual |
|--------|--------|--------|
| Uptime | 99.9% | ___ |
| Error Rate | <0.1% | ___ |
| Avg Response Time | <2s | ___ |
| State Migrations | 100+ | ___ |
| Test Coverage | ≥90% | ___ |
| User Satisfaction | No complaints | ___ |

- [ ] Metrics tracked
- [ ] All targets met
- [ ] Report generated

---

## 🆘 ROLLBACK PLAN

**If critical issues occur within 24 hours:**

### **Step 1: Revert Code**

```bash
git revert v2.0.0
git push origin main
```

### **Step 2: Redeploy**

Railway will auto-deploy reverted version.

### **Step 3: Verify**

```bash
curl https://your-bot-url.railway.app/health
# Should show v1.x.x
```

### **Step 4: Restore Database (if needed)**

```bash
psql freedom_wallet_bot < backup_YYYYMMDD.sql
```

- [ ] Rollback executed
- [ ] Old version running
- [ ] Users notified
- [ ] Issue documented

**Note:** Rollback is LOW RISK because v2.0 is backward compatible.

---

## 📞 CONTACTS

**On-Call Support:**
- Primary: [Name] - [Phone]
- Secondary: [Name] - [Phone]
- Emergency: [Name] - [Phone]

**Escalation:**
- Tech Lead: [Name]
- Product Manager: [Name]
- CTO: [Name]

**Channels:**
- Slack: #freedom-wallet-alerts
- Email: dev@freedomwallet.com
- Phone: Hotline number

---

## 📝 SIGN-OFF

**Pre-Deployment:**
- [ ] Tech Lead Approval: _________________ Date: _______
- [ ] QA Approval: _________________ Date: _______
- [ ] Product Approval: _________________ Date: _______

**Post-Deployment:**
- [ ] Deployment Verified: _________________ Date: _______
- [ ] Health Checks Passed: _________________ Date: _______
- [ ] Monitoring Active: _________________ Date: _______

**Final Sign-off (After 1 Week):**
- [ ] All Metrics Met: _________________ Date: _______
- [ ] Dead Code Removed: _________________ Date: _______
- [ ] Documentation Updated: _________________ Date: _______
- [ ] Release Complete: _________________ Date: _______

---

## 🎉 COMPLETION

**When all items checked:**

✅ v2.0.0 deployment is **COMPLETE**!

Update team:
```
🎉 Freedom Wallet Bot v2.0.0 deployed successfully!

✨ Features:
- Unified FREE → UNLOCK → PREMIUM flow
- Dynamic roadmap governance
- 90%+ test coverage
- Complete documentation

📊 Metrics: All green
🚀 Status: Production ready
📚 Docs: Updated

Thank you team! 🙌
```

---

**Checklist Version:** 1.0  
**Last Updated:** 2026-02-17  
**Maintained by:** Freedom Wallet Team
