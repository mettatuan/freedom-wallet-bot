# 📋 PHASE 2 QUICK REFERENCE (60 DAYS)

**Timeframe:** Feb 24 - May 26, 2026  
**Status:** Testing in Production  
**Rule:** NO CHANGES until Week 15

---

## 🎯 3-TIER STRATEGY SUMMARY

### **FREE Tier (Foundation)**
```
Psychology: "Tôi SỞ HỮU"
Unlock: 2 referrals
Duration: Forever ♾️
Features: Template + 5 msg/day + Community
Target KPIs:
  - 30-day retention ≥50%
  - ≥10 transactions/month
```

### **VIP Tier (Identity Layer) ⭐ BREAKTHROUGH**
```
Psychology: "Tôi THUỘC VỀ"
Milestones:
  - 10 refs → Rising Star (VIP group + 20% discount)
  - 50 refs → Super VIP (Premium 1 year FREE)
  - 100 refs → Legend (Premium LIFETIME)
Target KPIs:
  - Weekly active ≥70%
  - Natural Premium conversion ~30%
Note: Some best VIPs never pay → COMPLETELY OK
```

### **PREMIUM Tier (Power Mode)**
```
Psychology: "Tôi ĐẦU TƯ"
Price: 999k/year
Features: Unlimited AI + chat + analysis
Triggers: 
  - User asks deep questions
  - Hits limit 5+ times
  - Active 30+ days
Target KPIs:
  - AI usage ≥10 msg/trial
  - 90-day churn <15%
```

---

## ⚠️ CRITICAL: DON'T SELF-SABOTAGE

### **❌ ABSOLUTELY DO NOT:**

```
❌ Add new features
❌ Test pricing changes  
❌ A/B test messaging
❌ Add conversion metrics
❌ Optimize for sales
❌ Add urgency tactics
❌ Create "creative" CTAs
❌ Pitch Premium earlier
❌ Add scarcity language
❌ Change unlock requirements
❌ Modify VIP milestones
❌ Adjust benefits
❌ Run experiments
❌ Add analytics tracking (sales)
```

### **✅ ONLY DO:**

```
✅ Monitor 6 behavior metrics
✅ Fix critical bugs
✅ User support
✅ Server maintenance
✅ Security patches
```

---

## 🗣️ ONE ANSWER TO ALL REQUESTS

**When anyone suggests:**
- "What if we test X?"
- "Can we try Y?"
- "Let's add Z feature"
- "I have an idea to boost conversion"
- "Maybe we should optimize..."

**YOU SAY:**
```
"Không. Chiến lược đã ký. Đợi đủ 60 ngày."

(No. Strategy is signed. Wait full 60 days.)
```

**No exceptions. No "just this once." No "small change."**

---

## 📊 6 METRICS TO TRACK (NOT OPTIMIZE)

### **Week 3-14: OBSERVE ONLY**

**FREE Metrics:**
```sql
-- 30-day retention
SELECT COUNT(*) FROM users 
WHERE created_at <= NOW() - INTERVAL 30 DAY
AND last_active >= NOW() - INTERVAL 7 DAY;

-- Transactions per user
SELECT AVG(transaction_count) FROM users
WHERE is_free_unlocked = true;

-- Referral quality
SELECT AVG(retention_30day) FROM users
WHERE referred_by IS NOT NULL;
```

**VIP Metrics:**
```sql
-- Weekly active
SELECT COUNT(*) FROM users
WHERE vip_tier IS NOT NULL
AND last_active >= NOW() - INTERVAL 7 DAY;

-- Natural Premium conversion
SELECT COUNT(*) FROM users
WHERE vip_tier IS NOT NULL
AND subscription_tier = 'PREMIUM';

-- Repeat referrals
SELECT COUNT(*) FROM users
WHERE vip_tier IS NOT NULL
AND referral_count > 10;
```

**PREMIUM Metrics:**
```sql
-- AI usage per trial
SELECT AVG(bot_chat_count) FROM users
WHERE subscription_tier = 'TRIAL';

-- Trial engagement
SELECT COUNT(*) FROM users
WHERE subscription_tier = 'TRIAL'
AND bot_chat_count >= 5;

-- 90-day churn
SELECT COUNT(*) FROM users
WHERE subscription_tier = 'PREMIUM'
AND premium_expires_at < NOW() + INTERVAL 90 DAY
AND last_active < NOW() - INTERVAL 30 DAY;
```

---

## 🚨 WHAT IF DATA LOOKS BAD?

### **Scenario 1: FREE retention only 30%**

**❌ DON'T:** Add urgency, change unlock req, add features  
**✅ DO:** Document observation, wait until Week 15  
**WHY:** Need full 60 days to see cohort behavior

### **Scenario 2: Zero VIP conversions to Premium**

**❌ DON'T:** Add sales pitch, offer discounts  
**✅ DO:** Document, continue observing  
**WHY:** VIP is identity layer, not revenue target

### **Scenario 3: Premium trial users don't engage**

**❌ DON'T:** Add ROI messaging, send reminders  
**✅ DO:** Note product-market fit issue, wait  
**WHY:** Testing Value-First, not Push strategy

### **Scenario 4: Someone has a "quick win" idea**

**❌ DON'T:** "Just try it for a week"  
**✅ DO:** "Documented for Week 15 review"  
**WHY:** Changing strategy invalidates test

---

## 📅 WEEK-BY-WEEK DISCIPLINE

### **Week 3-6 (Expected: Excitement Phase)**
- Team excited about launch ✨
- Ideas flowing 💡
- "What if we..." 🤔
- **ACTION:** Document ideas, do NOT implement

### **Week 7-10 (Expected: Doubt Phase)**
- "Data looks concerning..." 😰
- "Should we tweak X?" 🔧
- "Competitor does Y..." 👀
- **ACTION:** Review strategy doc, hold the line

### **Week 11-14 (Expected: Panic Phase)**
- "Numbers aren't moving!" 📉
- "We're losing money!" 💸
- "Let's try SOMETHING!" 🚨
- **ACTION:** Breathe. 60 days = test validity. Trust process.

### **Week 15 (Decision Week)**
- Analyze full 60-day data 📊
- Compare to success criteria ✅
- Make informed decision 🎯
- Scale / Pivot / Iterate 🚀

---

## 💡 REMINDERS FOR HARD MOMENTS

### **When revenue dips:**
> "We're testing PMF, not maximizing revenue. 
> Revenue during test ≠ revenue after validation."

### **When users ask for features:**
> "Noted for roadmap. Testing core value proposition first."

### **When team wants to optimize:**
> "Optimization comes AFTER validation. 
> Can't optimize what hasn't been validated."

### **When competitors launch similar:**
> "We're testing our unique insight (VIP = Identity). 
> Their tactics are irrelevant to our validation."

---

## 🎯 WEEK 15 DECISION FRAMEWORK

**Data to Analyze:**
- All 6 metrics vs targets
- User feedback themes
- Technical stability
- Team observations

**Possible Outcomes:**

**🟢 SCALE:** Hit 4+ of 6 metrics
```
→ Double down on current strategy
→ Increase marketing
→ Expand features within strategy
→ Hire for growth
```

**🟡 ITERATE:** Hit 2-3 of 6 metrics
```
→ Identify what worked
→ Refine what didn't
→ Retest for another 60 days
→ Adjust ONE variable only
```

**🔴 PIVOT:** Hit 0-1 of 6 metrics
```
→ Acknowledge failure fast
→ Analyze root cause
→ Design new strategy
→ Retest new approach
```

**Decision Maker:** Product Lead + Dev Team  
**Decision Date:** May 26, 2026 (Week 15)  
**Decision Criteria:** Data + Insights, not opinions

---

## 📞 EMERGENCY ONLY

**Critical Bug:** Fix immediately (doesn't affect strategy)  
**Server Down:** Fix immediately  
**Security Issue:** Fix immediately  
**Payment Bug:** Fix immediately

**Everything Else:** Wait until Week 15

---

## ✅ DAILY CHECKLIST

**Morning:**
- [ ] Check server status
- [ ] Review error logs
- [ ] Monitor VIP milestone triggers
- [ ] Support ticket review

**Evening:**
- [ ] Record day's metrics
- [ ] Document user feedback
- [ ] Note any "idea" requests (don't implement)
- [ ] Remind team: 60 days, no changes

---

## 🏆 SUCCESS DEFINITION

**Phase 2 Success ≠ Revenue Growth**  
**Phase 2 Success = Valid Test Completed**

**We succeed if:**
✅ Full 60 days of clean data  
✅ No strategy changes  
✅ 6 metrics tracked consistently  
✅ Team holds discipline  
✅ Users experience intended strategy  

**Revenue comes AFTER validation.**

---

**Print this. Pin it. Read it daily.**  
**Strategy is LOCKED. Trust the process. 🔒**

---

**Next Milestone:** Week 15 Decision (May 26, 2026)  
**Days Remaining:** 105 days  
**Strategy Status:** LOCKED 🔒  

**🚀 Stay strong. Trust the data. EXECUTE.**
