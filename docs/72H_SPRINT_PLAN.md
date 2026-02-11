# 🚀 72-HOUR PREMIUM MVP SPRINT

**Goal:** Premium "đáng tiền" trong 72h → Giảm trial churn  
**Timeline:** Saturday → Monday (3 days, 8 hours total)  
**Status:** 📋 Ready to start

---

## 🎯 WHY 72 HOURS?

**The Critical Window:**
- 70% trial cancellations happen in first 48h
- Users decide "worth it or not" in first 24h
- Fast MVP = Fast feedback = Fast iteration

**What we'll prove:**
- Premium has clear value (unlimited vs 5 msg)
- ROI is visible (dashboard shows savings)
- Users want to keep Premium (60% conversion)

---

## 📅 DAY-BY-DAY PLAN

### **DAY 1 (SATURDAY) - 4 HOURS**

#### Morning (2-3h): Usage Tracking + Tier System

**Task 1.1: Database Migration** (30 min)
```python
# migrations/add_usage_tracking.py
- bot_chat_count: Integer
- bot_chat_limit_date: Date
- subscription_tier: Enum['FREE', 'PREMIUM', 'TRIAL']
- premium_started_at: DateTime
- trial_ends_at: DateTime
```

**Task 1.2: Subscription Manager** (1.5h)
```python
# bot/core/subscription.py
class SubscriptionManager:
    def can_use_feature(user, feature):
        if is_premium(user):
            return True
        
        if feature == 'bot_chat':
            if daily_usage >= 5:
                return False, "⚠️ Bạn đã hết 5 tin nhắn hôm nay"
        
        return True
```

**Task 1.3: Usage Middleware** (45 min)
```python
# bot/middleware/usage_tracker.py
async def track_message_usage(update, context):
    user = get_user(update.effective_user.id)
    
    can_send, msg = SubscriptionManager.can_use_feature(user, 'bot_chat')
    
    if not can_send:
        await update.message.reply_text(
            f"{msg}\n\n"
            "💎 Nâng cấp Premium: Unlimited messages!\n"
            "[🎯 Dùng thử 7 ngày FREE](callback:start_trial)"
        )
        return False  # Block message
    
    # Increment counter
    user.bot_chat_count += 1
    db.commit()
    
    return True  # Allow message
```

**Deliverable:**
- ✅ FREE locked at 5 msg/day
- ✅ Premium unlimited
- ✅ Clear upgrade prompt when hit limit

---

#### Afternoon (1h): Metrics Setup

**Task 1.4: Analytics Tracking** (1h)
```python
# bot/services/analytics.py
class Analytics:
    def track_event(user_id, event_name, properties=None):
        # Simple CSV/JSON logging for now
        log_to_file('analytics.jsonl', {
            'timestamp': datetime.now(),
            'user_id': user_id,
            'event': event_name,
            'properties': properties
        })
    
    # Events to track:
    # - 'chat_limit_hit' → FREE users hitting 5 msg
    # - 'trial_started' → Trial conversions
    # - 'premium_menu_click' → Which buttons clicked
    # - 'recommendation_clicked' → Gợi ý acceptance rate
```

**Deliverable:**
- ✅ Basic event tracking
- ✅ Can measure 3 key metrics

---

### **DAY 2 (SUNDAY) - 3 HOURS**

#### Morning (45 min): 24h WOW Moment

**Task 2.1: WOW Moment Job** (45 min)
```python
# bot/jobs/wow_moment.py
async def send_24h_wow_moment(user_id):
    user = get_user(user_id)
    
    # Calculate value received in 24h
    messages_sent = count_messages(user_id, last_24h=True)
    time_saved = messages_sent * 3 / 60  # 3 min per message
    value = time_saved * 100_000  # 100K VNĐ/hour
    
    message = f"""
🎊 24 GIỜ VỚI PREMIUM!

Bạn đã nhận được:
💬 {messages_sent} câu trả lời AI
⏱️ {time_saved:.1f} giờ tiết kiệm
💰 Giá trị: ~{value:,.0f} VNĐ

━━━━━━━━━━━━━━━━━━━━━
💎 ROI hiện tại:
Chi: 2,750 VNĐ (83K/30 days)
Nhận: {value:,.0f} VNĐ

→ Bạn đang "lời" {value - 2750:,.0f} VNĐ! 🚀

💡 Còn 6 ngày trial - tiếp tục trải nghiệm!
"""
    
    await bot.send_message(user_id, message, parse_mode='Markdown')

# Schedule 24h after trial/premium start
def schedule_wow_moment(user_id):
    run_date = datetime.now() + timedelta(hours=24)
    scheduler.add_job(
        send_24h_wow_moment,
        'date',
        run_date=run_date,
        args=[user_id]
    )
```

**Deliverable:**
- ✅ Auto-send WOW moment 24h after upgrade
- ✅ Show concrete ROI numbers
- ✅ Reduce early cancellations

---

#### Afternoon Part 1 (1-1.5h): ROI Dashboard

**Task 2.2: ROI Calculator + /mystatus** (1-1.5h)
```python
# bot/services/roi_calculator.py
class ROICalculator:
    HOURLY_RATE = 100_000  # VNĐ/hour
    PREMIUM_MONTHLY = 83_000  # VNĐ/month
    
    def calculate_monthly_roi(user):
        # Count usage this month
        messages = count_messages(user.id, current_month=True)
        analyses = count_feature_usage(user.id, 'analysis', current_month=True)
        
        # Calculate time saved
        time_saved = (
            messages * 3 / 60 +      # 3 min per AI message
            analyses * 30 / 60       # 30 min per analysis
        )
        
        # Calculate value
        value = time_saved * self.HOURLY_RATE
        cost = self.PREMIUM_MONTHLY
        roi = (value - cost) / cost * 100
        
        return {
            'messages': messages,
            'analyses': analyses,
            'time_saved': time_saved,
            'value': value,
            'cost': cost,
            'roi': roi,
            'profit': value - cost
        }

# Update /mystatus command
async def mystatus_premium(update, context):
    user = get_user(update.effective_user.id)
    roi = ROICalculator().calculate_monthly_roi(user)
    
    message = f"""
💎 TÀI KHOẢN PREMIUM

━━━━━━━━━━━━━━━━━━━━━
📊 THÁNG NÀY:
━━━━━━━━━━━━━━━━━━━━━

💬 {roi['messages']} tin nhắn
📊 {roi['analyses']} phân tích
⏱️ {roi['time_saved']:.1f}h tiết kiệm

━━━━━━━━━━━━━━━━━━━━━
💰 ROI:
━━━━━━━━━━━━━━━━━━━━━

Chi: {roi['cost']:,} VNĐ
Nhận: {roi['value']:,.0f} VNĐ

Lời: {roi['profit']:,.0f} VNĐ ({roi['roi']:.0f}%)

🎉 Premium = Đầu tư sinh lời!
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')
```

**Deliverable:**
- ✅ /mystatus shows clear ROI
- ✅ Premium users see concrete value
- ✅ Justification for payment

---

#### Afternoon Part 2 (30 min): Trial Day-6 Reminder

**Task 2.3: Trial Churn Prevention** (30 min)
```python
# bot/jobs/trial_churn_prevention.py
async def send_trial_day6_reminder(user_id):
    user = get_user(user_id)
    roi = ROICalculator().calculate_monthly_roi(user)
    
    message = f"""
⏰ TRIAL ENDING IN 24H

━━━━━━━━━━━━━━━━━━━━━
💎 7 NGÀY VỚI PREMIUM:
━━━━━━━━━━━━━━━━━━━━━

⏱️ Bạn đã tiết kiệm: {roi['time_saved']:.1f}h
💬 {roi['messages']} câu hỏi đã trả lời
📊 {roi['analyses']} phân tích chi tiết

━━━━━━━━━━━━━━━━━━━━━
💰 GIÁ TRỊ ĐÃ NHẬN:
━━━━━━━━━━━━━━━━━━━━━
~{roi['value']:,.0f} VNĐ (chỉ trong 7 ngày!)

Nếu giữ Premium:
→ Mỗi tháng nhận {roi['value'] * 4:,.0f} VNĐ value
→ Chỉ chi 83K = ROI {roi['roi'] * 4:.0f}%

💡 Không muốn mất trợ lý này?

[💎 Giữ Premium - 83K/tháng]
[📅 Nhắc tôi sau 24h]
"""
    
    await bot.send_message(user_id, message, parse_mode='Markdown')

# Schedule 24h before trial ends (Day 6 of 7-day trial)
def schedule_trial_reminder(user_id, trial_end_date):
    run_date = trial_end_date - timedelta(hours=24)
    scheduler.add_job(
        send_trial_day6_reminder,
        'date',
        run_date=run_date,
        args=[user_id]
    )
```

**Deliverable:**
- ✅ Auto-reminder 24h before trial ends
- ✅ Show value received
- ✅ Clear CTA to keep Premium
- ✅ Target: 60% trial→paid conversion

---

### **DAY 3 (MONDAY) - 1 HOUR**

#### Morning (30 min): Menu Click Tracking

**Task 3.1: Analytics Integration** (30 min)
```python
# Update bot/handlers/premium_commands.py

async def recommendation_handler(update, context):
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Track click
    Analytics.track_event(user_id, 'recommendation_clicked')
    
    # ... existing code ...

# Track all 6 menu buttons
PREMIUM_CALLBACKS = {
    'quick_record': lambda u, c: track_and_handle(u, c, quick_record_handler),
    'today_status': lambda u, c: track_and_handle(u, c, today_status_handler),
    'analysis': lambda u, c: track_and_handle(u, c, analysis_handler),
    'recommendation': lambda u, c: track_and_handle(u, c, recommendation_handler),
    'setup': lambda u, c: track_and_handle(u, c, setup_handler),
    'priority_support': lambda u, c: track_and_handle(u, c, priority_support_handler),
}

def track_and_handle(update, context, handler):
    Analytics.track_event(update.effective_user.id, f'menu_{handler.__name__}')
    return handler(update, context)
```

**Deliverable:**
- ✅ Track which menu buttons clicked
- ✅ Measure CTR "Gợi ý tiếp theo"
- ✅ Target: ≥60% CTR daily

---

#### Afternoon (30 min): Testing & Launch

**Task 3.2: End-to-End Testing** (30 min)

**Test scenarios:**
1. ✅ FREE user hits 5 msg limit → Upgrade prompt shown
2. ✅ User starts trial → 24h WOW scheduled
3. ✅ 24h later → WOW message received
4. ✅ Day 6 → Trial reminder received
5. ✅ /mystatus → ROI dashboard displayed
6. ✅ Menu clicks → Analytics logged

**Launch checklist:**
- [ ] Database migration successful
- [ ] Usage tracking working
- [ ] Jobs scheduled correctly
- [ ] Analytics logging
- [ ] No breaking errors

**Deliverable:**
- ✅ MVP ready for beta users
- ✅ Monitoring in place
- ✅ Can measure 3 key metrics

---

## 📊 SUCCESS CRITERIA (MEASURE AFTER WEEK 1)

### **Metric 1: Trial → Paid ≥ 60%**
```python
# Calculate after 10 trials completed
trial_to_paid = paid_conversions / total_trials
# Target: ≥ 60% (vs industry 40%)
```

### **Metric 2: Premium DAU ≥ 80%**
```python
# Calculate daily
premium_dau = users_active_today / total_premium_users
# Target: ≥ 80% (vs FREE 30%)
```

### **Metric 3: CTR "Gợi ý" ≥ 60%**
```python
# Calculate daily
recommendation_ctr = recommendation_clicks / premium_users
# Target: ≥ 60%
```

**If all 3 metrics hit → Strategy validated ✅**

---

## 🚨 WHAT TO SKIP (RESIST TEMPTATION!)

**Don't build these yet:**
- ❌ Export PDF/Excel (nice-to-have, low usage)
- ❌ Template library (not core value)
- ❌ Trend predictions (complex, validate need first)
- ❌ 1-1 consulting booking (manual OK for MVP)
- ❌ Advanced AI (rule-based works for now)

**Why skip?**
- Need conversion data first
- Premature optimization
- 80/20 rule: Focus on 20% features that drive 80% value

---

## 🎯 SPRINT OUTCOME

**After 72 hours, you'll have:**
✅ Working FREE tier (5 msg/day)  
✅ Working PREMIUM tier (unlimited)  
✅ 24h WOW moment (prevents churn)  
✅ Day-6 trial reminder (drives conversion)  
✅ ROI dashboard (shows value)  
✅ Analytics tracking (measures success)  

**Result:**
→ Complete Premium experience in 72h  
→ Can validate business model  
→ Data to inform next features  

---

## 🚀 START NOW

**Run these commands:**
```powershell
cd D:\Projects\FreedomWalletBot

# Day 1: Create files
New-Item -Path "migrations/add_usage_tracking.py" -ItemType File
New-Item -Path "bot/core/subscription.py" -ItemType File
New-Item -Path "bot/middleware/usage_tracker.py" -ItemType File

# Day 2: Add jobs
New-Item -Path "bot/jobs/wow_moment.py" -ItemType File
New-Item -Path "bot/jobs/trial_churn_prevention.py" -ItemType File
New-Item -Path "bot/services/roi_calculator.py" -ItemType File

# Day 3: Test
python -m pytest tests/test_subscription.py
python -m pytest tests/test_roi_calculator.py
```

**Or just say: "Bắt đầu Day 1!" 🔥**
