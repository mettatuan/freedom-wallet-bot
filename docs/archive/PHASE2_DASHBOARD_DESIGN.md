# 📊 Phase 2 Metrics Dashboard Design

**Created:** February 10, 2026  
**Purpose:** Track 6 behavioral metrics during 60-day testing phase  
**Google Sheets URL:** https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit?usp=sharing

---

## 🎯 DASHBOARD OVERVIEW

**Purpose:** Monitor (NOT optimize) 6 key behavior metrics  
**Update Frequency:** Daily automatic + On-demand via Telegram  
**Duration:** Feb 24 - May 26, 2026 (60 days)

---

## 📋 GOOGLE SHEETS STRUCTURE

### **Sheet 1: DAILY METRICS SNAPSHOT** ⭐ MAIN VIEW

```
| Date       | FREE_30Day | FREE_Trans | VIP_Active | VIP_Premium | PREM_AI | PREM_Churn | Status |
|------------|------------|------------|------------|-------------|---------|------------|--------|
| 2026-02-24 | 45%        | 8.5        | 65%        | 25%         | 12.3    | 10%        | 🟡     |
| 2026-02-25 | 47%        | 9.2        | 68%        | 27%         | 13.1    | 9%         | 🟢     |
| 2026-02-26 | 50%        | 10.1       | 70%        | 30%         | 14.2    | 8%         | 🟢     |
```

**Columns:**
- `Date` - Daily timestamp
- `FREE_30Day` - FREE tier 30-day retention %
- `FREE_Trans` - Avg transactions per FREE user
- `VIP_Active` - VIP weekly active rate %
- `VIP_Premium` - VIP → Premium natural conversion %
- `PREM_AI` - Premium AI usage (avg msgs)
- `PREM_Churn` - Premium 90-day churn %
- `Status` - Overall health (🟢 All targets met | 🟡 1-2 below | 🔴 3+ below)

**Key Features:**
- Conditional formatting: Green if target met, Red if below
- Sparklines showing 7-day trend
- Weekly average row (every 7 days)

---

### **Sheet 2: FREE TIER DETAILS**

```
| Metric              | Current | Target | Status | Formula |
|---------------------|---------|--------|--------|---------|
| 30-Day Retention    | 50%     | ≥50%   | 🟢     | =B2/C2  |
| Trans per User      | 10.1    | ≥10    | 🟢     | =B3/C3  |
|---------------------|---------|--------|--------|---------|
| Total FREE Users    | 450     | -      | -      | COUNT   |
| Active (7d)         | 225     | -      | -      | COUNT   |
| New This Week       | 32      | -      | -      | COUNT   |
| Avg Referral/User   | 3.2     | -      | -      | AVG     |
```

**Breakdown:**
- 30-Day Retention: Users created 30+ days ago who were active in last 7 days
- Trans per User: Avg `total_transactions` for `is_free_unlocked=true` users
- Supporting metrics for context (not optimization targets)

**Data Source SQL:**
```sql
-- 30-day retention
SELECT 
  COUNT(CASE WHEN last_active >= NOW() - INTERVAL 7 DAY THEN 1 END) * 100.0 / COUNT(*) as retention_pct
FROM users 
WHERE created_at <= NOW() - INTERVAL 30 DAY
  AND is_free_unlocked = true;

-- Transactions per user
SELECT AVG(total_transactions) as avg_transactions
FROM users
WHERE is_free_unlocked = true
  AND total_transactions > 0;
```

---

### **Sheet 3: VIP TIER DETAILS**

```
| Metric                  | Current | Target | Status | Formula |
|-------------------------|---------|--------|--------|---------|
| Weekly Active Rate      | 70%     | ≥70%   | 🟢     | =B2/C2  |
| Natural Premium Conv    | 30%     | ~30%   | 🟢     | =B3/C3  |
|-------------------------|---------|--------|--------|---------|
| Total VIP Users         | 85      | -      | -      | COUNT   |
| - Rising Star (10+)     | 60      | -      | -      | COUNT   |
| - Super VIP (50+)       | 20      | -      | -      | COUNT   |
| - Legend (100+)         | 5       | -      | -      | COUNT   |
| Active Last 7d          | 60      | -      | -      | COUNT   |
| VIP → Premium           | 25      | -      | -      | COUNT   |
| Avg Refs per VIP        | 35.2    | -      | -      | AVG     |
```

**Breakdown:**
- Weekly Active: VIP users (`vip_tier IS NOT NULL`) active in last 7 days
- Natural Premium Conv: VIP users with `subscription_tier = 'PREMIUM'`
- VIP tier distribution (not optimization target)

**Data Source SQL:**
```sql
-- Weekly active rate
SELECT 
  COUNT(CASE WHEN last_active >= NOW() - INTERVAL 7 DAY THEN 1 END) * 100.0 / COUNT(*) as active_pct
FROM users 
WHERE vip_tier IS NOT NULL;

-- Natural Premium conversion
SELECT 
  COUNT(CASE WHEN subscription_tier = 'PREMIUM' THEN 1 END) * 100.0 / COUNT(*) as conversion_pct
FROM users
WHERE vip_tier IS NOT NULL;
```

---

### **Sheet 4: PREMIUM TIER DETAILS**

```
| Metric              | Current | Target | Status | Formula |
|---------------------|---------|--------|--------|---------|
| AI Usage (msg/user) | 14.2    | ≥10    | 🟢     | =B2/C2  |
| 90-Day Churn        | 8%      | <15%   | 🟢     | =B3/C3  |
|---------------------|---------|--------|--------|---------|
| Total Premium Users | 45      | -      | -      | COUNT   |
| Trial Users         | 12      | -      | -      | COUNT   |
| Active (7d)         | 38      | -      | -      | COUNT   |
| Avg Sub Duration    | 125d    | -      | -      | AVG     |
| Feature Usage:      |         |        |        |         |
| - AI Chat           | 42      | -      | -      | COUNT   |
| - Unlimited Msgs    | 45      | -      | -      | COUNT   |
| - Advanced Analysis | 28      | -      | -      | COUNT   |
```

**Breakdown:**
- AI Usage: Avg `bot_chat_count` for users with `subscription_tier IN ('TRIAL', 'PREMIUM')`
- 90-Day Churn: Users who started premium 90+ days ago but subscription expired
- Feature usage for understanding (not optimization)

**Data Source SQL:**
```sql
-- AI usage per user
SELECT AVG(bot_chat_count) as avg_ai_usage
FROM users
WHERE subscription_tier IN ('TRIAL', 'PREMIUM')
  AND bot_chat_count > 0;

-- 90-day churn
SELECT 
  COUNT(CASE WHEN subscription_expires < NOW() THEN 1 END) * 100.0 / COUNT(*) as churn_pct
FROM users
WHERE premium_started_at <= NOW() - INTERVAL 90 DAY
  AND subscription_tier IN ('TRIAL', 'PREMIUM');
```

---

### **Sheet 5: WEEKLY SUMMARY**

```
| Week | Start Date | FREE Ret | FREE Trans | VIP Active | VIP Conv | PREM AI | PREM Churn | Notes |
|------|------------|----------|------------|------------|----------|---------|------------|-------|
| 3    | 2026-02-24 | 48%      | 9.5        | 67%        | 28%      | 13.2    | 9%         | Launch |
| 4    | 2026-03-03 | 51%      | 10.8       | 71%        | 31%      | 14.5    | 8%         | Stable |
| 5    | 2026-03-10 | 53%      | 11.2       | 73%        | 33%      | 15.1    | 7%         | Growth |
```

**Purpose:**
- Week-over-week trend view
- Identify patterns (not optimization signals)
- Notes column for context (bugs, holidays, etc.)

**Charts:**
- Line chart: All 6 metrics over time with target lines
- Stacked area: User distribution (FREE/VIP/PREMIUM)
- Heatmap: Daily status (🟢🟡🔴) for pattern recognition

---

### **Sheet 6: RAW DATA LOG**

```
| Timestamp           | Metric Name     | Value | Source    | Notes |
|---------------------|-----------------|-------|-----------|-------|
| 2026-02-24 08:00:00 | FREE_30Day      | 48%   | Auto      | -     |
| 2026-02-24 08:00:05 | FREE_Trans      | 9.5   | Auto      | -     |
| 2026-02-24 14:30:22 | VIP_Active      | 67%   | Manual    | Check |
```

**Purpose:**
- Audit trail for all metric updates
- Troubleshoot data issues
- Verify calculation accuracy

---

## 🎨 DASHBOARD VISUAL DESIGN

### **Color Coding:**
```
🟢 GREEN (Target Met):
  - FREE_30Day ≥ 50%
  - FREE_Trans ≥ 10
  - VIP_Active ≥ 70%
  - VIP_Premium ≥ 25% (range: 25-35% OK)
  - PREM_AI ≥ 10
  - PREM_Churn < 15%

🟡 YELLOW (Close to Target):
  - Within 10% of target
  - Not concerning yet
  - Continue observing

🔴 RED (Below Target):
  - More than 10% below target
  - Document why (not fix!)
  - Check for bugs or data issues
```

### **Conditional Formatting Rules:**
```
Sheet 1 (Daily Metrics):
  - FREE_30Day: ≥50% = GREEN, 45-49.9% = YELLOW, <45% = RED
  - FREE_Trans: ≥10 = GREEN, 9-9.9 = YELLOW, <9 = RED
  - VIP_Active: ≥70% = GREEN, 63-69.9% = YELLOW, <63% = RED
  - VIP_Premium: 25-35% = GREEN, 20-24.9% or 35.1-40% = YELLOW, others = RED
  - PREM_AI: ≥10 = GREEN, 9-9.9 = YELLOW, <9 = RED
  - PREM_Churn: <15% = GREEN, 15-17% = YELLOW, >17% = RED
```

---

## 🔄 UPDATE MECHANISMS

### **1. Automatic Daily Update (8:00 AM)**
```python
# Scheduled job runs daily at 8 AM Vietnam time
# Updates Sheet 1 (Daily Metrics) with current data
# Appends to Sheet 6 (Raw Data Log)
```

### **2. Manual On-Demand Update**
**Via Telegram:** `/admin_metrics`
```
Admin sends /admin_metrics in bot
→ Calculates all 6 metrics in real-time
→ Displays in Telegram message
→ Updates Google Sheets
→ Sends confirmation
```

**Via Google Sheets:**
- Button: "🔄 Refresh Now" (runs Apps Script)
- Updates timestamp and pulls latest data

---

## 📱 TELEGRAM ADMIN MENU

### **Command: `/admin_metrics`**

**Output Example:**
```
📊 PHASE 2 METRICS DASHBOARD
━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Date: 2026-02-24 14:30
⏱️ Update: On-Demand (Manual)

━━━━━━━━━━━━━━━━━━━━━━━━━━
🎁 FREE TIER
━━━━━━━━━━━━━━━━━━━━━━━━━━
30-Day Retention: 50% 🟢 (Target: ≥50%)
Trans/User: 10.1 🟢 (Target: ≥10)

Total FREE Users: 450
Active (7d): 225 (50%)
New This Week: 32

━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ VIP TIER (Identity Layer)
━━━━━━━━━━━━━━━━━━━━━━━━━━
Weekly Active: 70% 🟢 (Target: ≥70%)
Natural Premium: 30% 🟢 (Target: ~30%)

Total VIP Users: 85
├─ Rising Star (10+): 60
├─ Super VIP (50+): 20
└─ Legend (100+): 5

Active (7d): 60/85

━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 PREMIUM TIER (Power Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━
AI Usage: 14.2 msg 🟢 (Target: ≥10)
90-Day Churn: 8% 🟢 (Target: <15%)

Total Premium: 45
Trial Users: 12
Active (7d): 38/45 (84%)

━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 OVERALL STATUS: 🟢 HEALTHY
━━━━━━━━━━━━━━━━━━━━━━━━━━
All 6 metrics meeting targets ✅

🔗 Full Dashboard:
https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit

⚠️ REMEMBER:
• Track, don't optimize
• Document, don't fix
• Observe, don't intervene
• Wait 60 days before any changes

━━━━━━━━━━━━━━━━━━━━━━━━━━
Next Auto Update: Tomorrow 8:00 AM
```

### **Quick Commands:**
```
/admin_metrics        - View current metrics
/admin_metrics_week   - View weekly summary
/admin_metrics_export - Download CSV
/admin_metrics_reset  - Clear cache (admin only)
```

---

## ⚙️ IMPLEMENTATION CHECKLIST

### **Phase A: Google Sheets Setup (Day 1)**
- [ ] Create spreadsheet structure (6 sheets)
- [ ] Set up conditional formatting rules
- [ ] Create charts and visualizations
- [ ] Test manual data entry

### **Phase B: Backend Service (Day 2)**
- [ ] Create `MetricsCalculationService` in `bot/services/`
- [ ] Implement SQL queries for 6 metrics
- [ ] Add caching layer (10-minute cache)
- [ ] Unit tests for calculations

### **Phase C: Telegram Integration (Day 3)**
- [ ] Create `admin_metrics.py` handler
- [ ] Implement `/admin_metrics` command
- [ ] Format Telegram message output
- [ ] Add inline buttons for refresh/export

### **Phase D: Google Sheets Integration (Day 4)**
- [ ] Create Google Sheets API service
- [ ] Implement update functions
- [ ] Test write operations
- [ ] Set up error handling

### **Phase E: Automation (Day 5)**
- [ ] Create scheduled job (daily 8 AM)
- [ ] Test automatic updates
- [ ] Set up alerting (failures)
- [ ] Document maintenance procedures

---

## 🔒 ACCESS CONTROL

**Admin Only:**
- User ID must match `settings.ADMIN_USER_ID`
- Commands return error for non-admin users
- Google Sheets: Share with admin email only
- API keys stored in environment variables

**Security:**
- No user PII in dashboard (only aggregates)
- Rate limiting: Max 1 request per minute
- Log all admin actions
- Encrypt sensitive data in transit

---

## 📊 SUCCESS CRITERIA

**This dashboard is successful if:**
1. ✅ Updates automatically every day at 8 AM
2. ✅ Admin can view metrics on-demand via Telegram
3. ✅ All 6 metrics calculated accurately
4. ✅ Data syncs to Google Sheets within 5 seconds
5. ✅ Zero manual data entry required
6. ✅ Historical data preserved (60+ days)
7. ✅ Charts and visualizations render correctly
8. ✅ Team uses it daily without asking for changes

**This dashboard FAILS if:**
- ❌ Team starts requesting "improvements"
- ❌ Additional metrics are added
- ❌ Used for optimization decisions before Week 15
- ❌ Becomes a "conversion funnel" dashboard

---

## ⚠️ CRITICAL WARNINGS

**DO NOT:**
- ❌ Add conversion metrics (sales, revenue, MRR)
- ❌ Create optimization alerts ("retention dropped!")
- ❌ Add funnel analysis or cohort tracking
- ❌ Build experiment frameworks
- ❌ Add "recommendations" or "insights"
- ❌ Share with marketing or sales teams
- ❌ Use for A/B test tracking

**THIS IS:**
- ✅ A behavior observation tool
- ✅ A "did the strategy work?" validator
- ✅ A discipline enforcement mechanism
- ✅ A 60-day pause button

**NOT:**
- ❌ A growth dashboard
- ❌ An optimization tool
- ❌ A sales pipeline tracker
- ❌ A conversion funnel

---

## 📝 MAINTENANCE

**Daily:**
- Verify automatic update ran at 8 AM
- Check for data anomalies (e.g., sudden spikes)
- Document any bugs found (don't fix strategy!)

**Weekly:**
- Review weekly summary
- Export data backup
- Document user feedback patterns

**Monthly:**
- Verify all 60 days of data preserved
- Check dashboard performance
- Update documentation if needed

**Week 15 (May 26):**
- Export complete 60-day dataset
- Create final analysis report
- Use data for strategic decision

---

## 🚀 DEPLOYMENT

**Steps:**
1. Create Google Sheets with structure above
2. Implement `MetricsCalculationService`
3. Create `admin_metrics.py` handler
4. Register handler in `main.py`
5. Test with dummy data
6. Deploy to production on Feb 24
7. Monitor first week closely
8. Set and forget for 60 days

**Timeline:**
- Design Complete: Feb 10 ✅
- Implementation: Feb 11-15
- Testing: Feb 16-23
- Deployment: Feb 24
- Phase 2 Testing: Feb 24 - May 26

---

**🎯 Remember: Track, Don't Optimize! 🔒**
