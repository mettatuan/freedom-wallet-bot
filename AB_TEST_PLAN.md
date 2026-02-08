# 🧪 A/B TESTING PLAN - VIP UNLOCK FLOW

## 🎯 MỤC TIÊU

Test variations để tối ưu conversion và engagement trong VIP unlock flow.

**Target metrics:**
- Day 1 completion rate: 50% (current) → 70% (goal)
- 7-day retention: 35% (estimated) → 55% (goal)
- Web App setup rate: 65% (estimated) → 80% (goal)

**Sample size:** 100-200 users per variant (tổng 200-400 users)

**Duration:** 2-3 weeks

---

## 📋 TEST #1: BUTTON COPY (CTA Wording)

### Hypothesis
Button copy ảnh hưởng trực tiếp đến click-through rate. "Action-oriented" language sẽ tăng engagement.

### Variants

| Element | Version A (Control) | Version B (Test) |
|---------|---------------------|------------------|
| **Message 3B - Main CTA** | "✅ Đã tạo xong Web App" | "🚀 Tôi sẵn sàng sử dụng" |
| **Day 1 - Completion CTA** | "✅ Hoàn thành Day 1" | "✅ Tôi đã thêm giao dịch đầu tiên" |

### Reasoning
- Version A: Đơn giản, factual
- Version B: 
  - "Tôi sẵn sàng" = commitment language (psychological buy-in)
  - "Tôi đã thêm giao dịch" = more specific, verifiable action

### Metrics to Track
- Click-through rate (CTR) on each button
- Time-to-click (faster = clearer CTA)
- Actual completion rate (did they really do it?)

### Implementation
```python
# In registration.py
import random

# Randomly assign user to variant
user_variant = "A" if random.random() < 0.5 else "B"

# Store in database
user.ab_test_variant = user_variant

# Use variant-specific button text
if user_variant == "A":
    button_text = "✅ Đã tạo xong Web App"
else:
    button_text = "🚀 Tôi sẵn sàng sử dụng"
```

---

## 📋 TEST #2: SETUP TIME MESSAGING

### Hypothesis
Reducing perceived time investment increases action-taking. "Nhanh hơn bạn nghĩ" creates curiosity + urgency.

### Variants

| Element | Version A (Control) | Version B (Test) |
|---------|---------------------|------------------|
| **Message 3B - Time frame** | "tạo Web App (3–5 phút)" | "tạo Web App (nhanh hơn bạn nghĩ)" |

### Reasoning
- Version A: Concrete time estimate (sets expectations)
- Version B: 
  - "Nhanh hơn bạn nghĩ" = psychological frame (challenges assumption)
  - Creates curiosity gap
  - No commitment to specific time (under-promise, over-deliver)

### Metrics to Track
- CTR on "Xem hướng dẫn 3 bước" button
- Actual setup completion rate
- Time-to-complete (does B lead to faster attempts?)

### Potential Risks
- Version B might feel vague or clickbait-y
- If setup takes >5 minutes, might lose trust

**Mitigation:** Monitor feedback/support requests for frustration signals

---

## 📋 TEST #3: DAY 1 TASK FRAMING

### Hypothesis
Framing task as "first transaction" vs "first success" affects motivation and completion.

### Variants

| Element | Version A (Control) | Version B (Test) |
|---------|---------------------|------------------|
| **Day 1 - Task description** | "Thêm giao dịch đầu tiên" | "Tạo thành công đầu tiên" |
| **Day 1 - Examples** | "Ly cafe: -35k, Lương: +15M" | "Bất cứ điều gì bạn chi hôm nay" |

### Reasoning
- Version A: Task-focused (complete a step)
- Version B: 
  - Outcome-focused (achieve a win)
  - "Thành công" = stronger emotional payoff
  - "Bất cứ điều gì" = maximum flexibility

### Metrics to Track
- Day 1 completion rate
- Number of transactions added (does B lead to MORE than 1?)
- User sentiment in support messages

---

## 📋 TEST #4: MESSAGE 3 SPLIT TIMING

### Hypothesis
Delay between 3A → 3B affects user readiness to act.

### Variants

| Element | Version A (Control) | Version B (Test) |
|---------|---------------------|------------------|
| **3A → 3B delay** | User clicks "Tiếp tục" (self-paced) | Auto-send 3B after 30 seconds |

### Reasoning
- Version A: User controls pacing (respect autonomy)
- Version B: 
  - Automatic progression (less friction)
  - 30s = enough time to read benefits, not too long to lose attention

### Metrics to Track
- Time from 3A → 3B view
- Engagement with 3B (scroll depth, button clicks)
- Overall flow completion

### Potential Risks
- Version B might feel pushy if user is distracted
- Could create notification spam if user checks phone later

**Mitigation:** Test with smaller sample first (50 users)

---

## 📋 TEST #5: IDENTITY ANCHOR PLACEMENT

### Hypothesis
Placing identity anchor in Message 2 vs Message 3A affects self-identification.

### Variants

| Element | Version A (Control) | Version B (Test) |
|---------|---------------------|------------------|
| **Identity anchor** | Message 2 (before benefits) | Message 3A (after celebration, before benefits) |

### Reasoning
- Version A: Early framing → colors perception of benefits
- Version B: 
  - After dopamine spike → higher receptivity
  - Attached to benefits → direct connection

### Example Flow

**Version A (Current):**
```
Message 1: Celebration image
Message 2: VIP announcement + "VIP là người..." ← Identity here
Message 3A: Benefits + 1 button
```

**Version B:**
```
Message 1: Celebration image
Message 2: VIP announcement only
Message 3A: "VIP là người..." + Benefits + 1 button ← Identity here
```

### Metrics to Track
- 7-day retention (does earlier identity = stronger commitment?)
- Support quality (do B users ask better questions?)
- Day 2-3 engagement

---

## 🔧 IMPLEMENTATION GUIDE

### 1. Database Schema
```sql
-- Add to users table
ALTER TABLE users ADD COLUMN ab_test_variant VARCHAR(10);
ALTER TABLE users ADD COLUMN ab_test_assigned_at TIMESTAMP;

-- Tracking table
CREATE TABLE ab_test_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'button_click', 'message_view', 'task_complete'
    event_data TEXT,  -- JSON with details
    variant VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 2. Assignment Logic
```python
def assign_ab_variant(user_id: int, test_name: str) -> str:
    """
    Assign user to A/B test variant
    
    Args:
        user_id: Telegram user ID
        test_name: e.g., 'button_copy_v1'
    
    Returns:
        'A' or 'B'
    """
    import random
    import hashlib
    
    # Use consistent hashing (same user always gets same variant)
    hash_input = f"{user_id}_{test_name}".encode()
    hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
    
    variant = "A" if hash_value % 2 == 0 else "B"
    
    # Store in database
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.ab_test_variant = f"{test_name}:{variant}"
            user.ab_test_assigned_at = datetime.utcnow()
            session.commit()
    
    logger.info(f"User {user_id} assigned to variant {variant} for {test_name}")
    return variant
```

### 3. Event Tracking
```python
def track_ab_event(user_id: int, event_type: str, event_data: dict = None):
    """
    Track A/B test event
    
    Example:
        track_ab_event(123, 'button_click', {'button': 'webapp_ready', 'variant': 'B'})
    """
    with SessionLocal() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user or not user.ab_test_variant:
            return
        
        event = ABTestEvent(
            user_id=user_id,
            event_type=event_type,
            event_data=json.dumps(event_data) if event_data else None,
            variant=user.ab_test_variant.split(':')[-1],  # Extract 'A' or 'B'
            created_at=datetime.utcnow()
        )
        session.add(event)
        session.commit()
```

### 4. Usage Example
```python
# In registration.py - VIP unlock flow
async def send_vip_unlock_messages(user_id: int, context):
    # Assign to test
    variant = assign_ab_variant(user_id, 'button_copy_v1')
    
    # Track event
    track_ab_event(user_id, 'vip_unlock', {'variant': variant})
    
    # Use variant-specific copy
    if variant == "A":
        button_text = "✅ Đã tạo xong Web App"
    else:
        button_text = "🚀 Tôi sẵn sàng sử dụng"
    
    # Send message with variant button
    keyboard = [[InlineKeyboardButton(button_text, callback_data="webapp_ready")]]
    # ... rest of code
```

---

## 📊 ANALYSIS FORMULA

### Conversion Rate
```
CR = (Completed Actions / Total Users) × 100%
```

### Statistical Significance (Chi-squared test)
```python
from scipy.stats import chi2_contingency

# Example data
data = [
    [70, 30],  # Variant A: 70 completed, 30 not completed
    [85, 15]   # Variant B: 85 completed, 15 not completed
]

chi2, p_value, dof, expected = chi2_contingency(data)

if p_value < 0.05:
    print("✅ Statistically significant difference!")
    print(f"Variant B is {(85/100 - 70/100) / (70/100) * 100:.1f}% better than A")
else:
    print("❌ No significant difference (p={:.3f})".format(p_value))
```

### Confidence Interval (95%)
```python
import math

def calculate_ci(successes, trials, confidence=0.95):
    """
    Calculate confidence interval for conversion rate
    """
    p = successes / trials
    z = 1.96  # 95% confidence
    
    margin = z * math.sqrt((p * (1 - p)) / trials)
    
    return (p - margin, p + margin)

# Example
ci_a = calculate_ci(70, 100)  # [0.61, 0.79]
ci_b = calculate_ci(85, 100)  # [0.78, 0.92]

print(f"Variant A: {ci_a[0]:.1%} - {ci_a[1]:.1%}")
print(f"Variant B: {ci_b[0]:.1%} - {ci_b[1]:.1%}")
```

---

## 📅 ROLLOUT TIMELINE

### Week 1: Setup & Launch
- Day 1-2: Implement A/B test infrastructure
- Day 3-4: Test with 10 users (QA)
- Day 5-7: Launch Test #1 (Button Copy)

### Week 2-3: Run & Monitor
- Run all users through Test #1
- Collect 100+ users per variant
- Monitor metrics daily

### Week 4: Analyze & Decide
- Statistical analysis
- Pick winning variant
- Implement as default

### Week 5+: Next Tests
- Launch Test #2 (Setup Time)
- Repeat cycle

---

## 🚨 STOPPING RULES

**Stop test early if:**

1. **One variant clearly loses** (p < 0.01, >30% worse)
   - Example: Variant B has 30% completion vs A's 60%
   - Action: Stop sending users to B, analyze why

2. **Technical issues** (bugs, crashes)
   - Action: Rollback to stable version

3. **Negative user feedback spike** (>5 complaints in 48h)
   - Action: Review test design, possibly pause

4. **Sample size reached** (200 users per variant)
   - Action: Analyze results, make decision

**Don't stop because:**
- "Looks like B is winning after 20 users" → Wait for significance
- "I prefer A" → Data decides, not opinions
- "Taking too long" → Patience = valid results

---

## 💡 BEST PRACTICES

### 1. Test ONE Variable at a Time
❌ Bad: Change button text AND color AND placement  
✅ Good: Change button text only

**Why:** Can't tell which change caused the difference

### 2. Consistent User Experience
- Same user always sees same variant (use consistent hashing)
- Don't switch mid-session

### 3. Document Everything
- Hypothesis → Implementation → Results
- Share learnings (even from "failed" tests)

### 4. Qualitative + Quantitative
- Track metrics (CTR, completion rate)
- Read support messages (user sentiment)
- Ask "why" not just "what"

### 5. Start Small, Scale Up
- Test #1: Run with 50 users first
- If stable → Scale to 200
- If issues → Fix before scaling

---

## 📝 REPORTING TEMPLATE

```markdown
# A/B Test Report: [Test Name]

## Overview
- **Test:** [Name, e.g., "Button Copy - CTA Wording"]
- **Duration:** [Start date] - [End date]
- **Sample Size:** [N users per variant]

## Hypothesis
[What we expected to happen and why]

## Results
| Metric | Variant A | Variant B | Difference | P-value |
|--------|-----------|-----------|------------|---------|
| CTR | 45% | 62% | +38% | <0.01 |
| Completion | 50% | 68% | +36% | <0.01 |
| Retention (7d) | 35% | 41% | +17% | 0.08 |

## Winner
✅ **Variant B** - Statistically significant improvement

## Insights
- [Key learnings]
- [Unexpected findings]
- [User feedback]

## Next Steps
- [ ] Implement B as default
- [ ] Test [related variation]
- [ ] Monitor for [potential risk]

## Raw Data
[Link to spreadsheet/database query]
```

---

## 🎯 RECOMMENDED TEST ORDER

**Priority 1 (Launch First):**
1. ✅ Button Copy (Test #1) - Easy to implement, high impact
2. ✅ Day 1 Task Framing (Test #3) - Core to retention

**Priority 2 (After 2-3 weeks):**
3. Setup Time Messaging (Test #2)
4. Message 3 Split Timing (Test #4)

**Priority 3 (Advanced):**
5. Identity Anchor Placement (Test #5)
6. Emoji variations (if time permits)

**Rationale:** 
- Start with biggest levers (button copy affects everyone)
- Build confidence with infrastructure
- Learn from simpler tests before complex ones

---

## 🔥 QUICK WINS (No A/B Test Needed)

Implement these immediately (no split testing required):

1. ✅ **V1 → V2 Changes Already Implemented:**
   - Split Message 3 into 3A + 3B
   - Add identity anchor
   - Delay Day 1 by 10 minutes
   - Simplify Day 1 to 1 task

2. **Track Everything:**
   - Button clicks (by callback_data)
   - Message open rates (if possible via Telegram)
   - Support request frequency

3. **Qualitative Feedback:**
   - Add "❓ Cần hỗ trợ" button to all key messages
   - Read support logs weekly
   - Look for patterns (confusion points)

---

**Next Action:** Implement Test #1 (Button Copy) infrastructure and launch with next 100 VIP users.
