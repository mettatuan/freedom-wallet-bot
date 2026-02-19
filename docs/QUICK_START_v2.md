# 🚀 QUICK START GUIDE - v2.0
**Get Started with Unified Flow Architecture**

Version: 2.0.0  
Date: 2026-02-17

---

## 📋 TABLE OF CONTENTS

1. [Setup](#setup)
2. [Using State Machine](#using-state-machine)
3. [Managing Tiers](#managing-tiers)
4. [Roadmap Integration](#roadmap-integration)
5. [Running Tests](#running-tests)
6. [Common Patterns](#common-patterns)

---

## 🔧 SETUP

### **1. Check Version**

```bash
cd c:\Projects\FreedomWalletBot
python version.py
```

**Expected Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Freedom Wallet Bot v2.0.0
  Unified Flow Architecture
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Release: 2026-02-17 (stable)
  Python: 3.11+
  API: v2
  DB Schema: v3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### **3. Set Environment Variables**

Create `.env` file:
```bash
# Roadmap Integration (Optional)
ROADMAP_APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
```

---

## 🎯 USING STATE MACHINE

### **Import State System**

```python
from app.core.state_machine import StateManager, UserState
from app.core.unified_states import SubscriptionTier
```

### **Check User State**

```python
# Initialize state manager
mgr = StateManager()

# Get current state
state, is_legacy = mgr.get_user_state(user_id)

print(f"State: {state.value}")
print(f"Is Legacy: {is_legacy}")
```

### **Transition User State**

```python
# Transition to new state
success, message = mgr.transition_user(
    user_id=123456789,
    new_state=UserState.VIP,
    reason="2+ referrals completed"
)

if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

### **Auto-Update by Referrals**

```python
# Check if user should upgrade based on referral count
new_state = mgr.check_and_update_state_by_referrals(user_id)

if new_state:
    print(f"Auto-upgraded to: {new_state.value}")
```

---

## 💎 MANAGING TIERS

### **Check Tier Properties**

```python
from app.core.unified_states import SubscriptionTier

tier = SubscriptionTier.UNLOCK

print(f"Display Name: {tier.display_name}")
print(f"AI Limit: {tier.ai_message_limit}")
print(f"Can Setup Sheets: {tier.can_setup_sheets}")
print(f"Has AI Insights: {tier.has_ai_insights}")
```

**Output:**
```
Display Name: Đã mở khóa
AI Limit: 20
Can Setup Sheets: True
Has AI Insights: False
```

### **Validate Tier Transitions**

```python
from app.core.unified_states import TierTransitions

# Check if upgrade is valid
can_upgrade = TierTransitions.can_upgrade(
    SubscriptionTier.FREE,
    SubscriptionTier.PREMIUM
)

print(f"Can upgrade FREE → PREMIUM: {can_upgrade}")
# Output: True
```

### **Use UserProfile**

```python
from app.core.unified_states import UserProfile
from datetime import datetime, timedelta

profile = UserProfile(
    user_id=123456789,
    state=UserState.ACTIVE,
    tier=SubscriptionTier.PREMIUM,
    created_at=datetime.utcnow(),
    last_active=datetime.utcnow(),
    referral_count=5,
    premium_expires_at=datetime.utcnow() + timedelta(days=365)
)

# Check premium status
if profile.is_premium_active():
    print("✅ Premium is active")

# Check if should unlock
if profile.should_unlock():
    print("✅ Should unlock to VIP")
```

---

## 🗺️ ROADMAP INTEGRATION

### **Setup Roadmap Service**

```python
from app.services.roadmap_service import RoadmapService, RoadmapStatus

# Initialize service
roadmap = RoadmapService()
```

### **Insert New Idea**

```python
result = roadmap.insert_item(
    title="AI Budget Recommendations",
    description="Automatically suggest budget allocation",
    status=RoadmapStatus.IDEA
)

print(result)
# Output: {'success': True, 'message': 'Added: FW#150 - AI Budget...'}
```

### **Update Status**

```python
# By title
result = roadmap.update_by_title(
    "AI Budget Recommendations",
    RoadmapStatus.IN_PROGRESS
)

# By ID
result = roadmap.update_status(
    "FW#150",
    RoadmapStatus.COMPLETED,
    notes="Implemented with GPT-4 integration"
)
```

### **Log Release**

```python
result = roadmap.log_release(
    version="v2.1.0",
    description="Budget AI Release",
    features=[
        "AI Budget Recommendations",
        "Spending Pattern Analysis"
    ]
)

print(result)
```

### **Convenience Functions**

```python
from app.services.roadmap_service import (
    sync_ai_idea,
    mark_task_planned,
    mark_task_in_progress,
    mark_task_completed,
    log_release_version
)

# Quick sync
sync_ai_idea("New Feature", "Description")
mark_task_planned("New Feature")
mark_task_in_progress("New Feature")
mark_task_completed("New Feature")

# Release
log_release_version("v2.1.0", "Release notes", ["Feature 1"])
```

---

## 🧪 RUNNING TESTS

### **Run All Tests**

```bash
pytest tests/ -v
```

### **Run Specific Test File**

```bash
pytest tests/unit/test_state_machine_comprehensive.py -v
```

### **Run with Coverage**

```bash
pytest --cov=app --cov-report=html
```

**View Report:**
```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

### **Run Only Unit Tests**

```bash
pytest tests/unit/ -v
```

### **Run Only Integration Tests**

```bash
pytest tests/integration/ -v
```

### **Run Only E2E Tests**

```bash
pytest tests/e2e/ -v -m e2e
```

---

## 🎨 COMMON PATTERNS

### **Pattern 1: Handle New User Registration**

```python
from app.core.state_machine import StateManager, UserState
from app.utils.database import SessionLocal, User

# Create user
user = User(
    id=telegram_user_id,
    username=telegram_username,
    user_state="VISITOR",
    subscription_tier="FREE"
)
db.add(user)
db.commit()

# Transition to REGISTERED
mgr = StateManager()
mgr.transition_user(
    user.id,
    UserState.REGISTERED,
    reason="Registration completed"
)
```

### **Pattern 2: Handle Referral Completion**

```python
# User B referred by User A
user_b.referred_by = user_a.id
user_a.referral_count += 1
db.commit()

# Check if User A should upgrade
mgr = StateManager()
new_state = mgr.check_and_update_state_by_referrals(user_a.id)

if new_state == UserState.VIP:
    # Send notification
    await context.bot.send_message(
        user_a.id,
        "🎉 Chúc mừng! Bạn đã unlock VIP tier!"
    )
    
    # Sync to roadmap
    from app.services.roadmap_service import sync_ai_idea
    sync_ai_idea(
        f"User {user_a.username} became VIP",
        f"Achieved 2+ referrals milestone"
    )
```

### **Pattern 3: Handle Google Sheets Setup**

```python
# User completes setup
user.sheet_url = sheet_url
user.web_app_url = webapp_url
user.subscription_tier = "UNLOCK"
db.commit()

# Transition state
mgr = StateManager()
mgr.transition_user(
    user.id,
    UserState.ACTIVE,
    reason="Google Sheets setup completed"
)

# Log to roadmap
roadmap.insert_item(
    title=f"User {user.username} setup completed",
    description="Transitioned from FREE to UNLOCK",
    status=RoadmapStatus.COMPLETED
)
```

### **Pattern 4: Handle Premium Upgrade**

```python
from datetime import datetime, timedelta

# Payment received
user.subscription_tier = "PREMIUM"
user.premium_started_at = datetime.utcnow()
user.premium_expires_at = datetime.utcnow() + timedelta(days=365)
db.commit()

# No state change needed (state = journey, tier = access)
# User stays in current state (e.g., ACTIVE or VIP)

# Update roadmap
roadmap.update_by_title(
    f"User {user.username} premium upgrade",
    RoadmapStatus.COMPLETED
)
```

### **Pattern 5: Check State Decay**

```python
# Check if SUPER_VIP should decay to VIP
mgr = StateManager()
decay_info = mgr.check_super_vip_decay(user_id)

if decay_info:
    print(f"⚠️ User {user_id} should decay:")
    print(f"  Current: {decay_info['current_state']}")
    print(f"  Target: {decay_info['target_state']}")
    print(f"  Reason: {decay_info['reason']}")
```

---

## 📚 REFERENCE

### **State Flow**

```
VISITOR → REGISTERED → ONBOARDING → ACTIVE
                         ↓
                        VIP → SUPER_VIP → ADVOCATE
```

### **Tier Flow**

```
FREE → UNLOCK → PREMIUM
```

### **Key Files**

- `app/core/unified_states.py` - Definitions
- `app/core/state_machine.py` - Logic
- `app/services/roadmap_service.py` - Roadmap API
- `version.py` - Version info

### **Documentation**

- `FLOW_MAP.md` - Complete architecture
- `TESTING_GUIDE.md` - Testing framework
- `MIGRATION_NOTES.md` - Migration guide

---

## 🆘 TROUBLESHOOTING

### **Issue: State transition fails**

**Check:**
```python
from app.core.unified_states import StateTransitions

# Get valid next states
valid = StateTransitions.get_valid_next_states(current_state)
print(f"Valid transitions: {[s.value for s in valid]}")
```

### **Issue: Roadmap sync not working**

**Check:**
```python
import os
print(os.getenv('ROADMAP_APPS_SCRIPT_URL'))
```

**Fix:** Set environment variable in `.env`

### **Issue: Tests fail**

**Run single test:**
```bash
pytest tests/unit/test_state_machine_comprehensive.py::TestStateTransitions::test_visitor_to_registered_valid -v
```

---

## 💡 TIPS

1. **Always use StateManager** - Don't modify `user.user_state` directly
2. **Check transitions first** - Use `StateTransitions.can_transition()` before attempting
3. **Log reasons** - Always provide a reason when transitioning
4. **Test locally first** - Run tests before deploying
5. **Monitor logs** - Check `data/logs/bot.log` for issues

---

**Quick Reference Card:**
```python
# State Machine
from app.core.state_machine import StateManager, UserState
mgr = StateManager()
state, is_legacy = mgr.get_user_state(user_id)
mgr.transition_user(user_id, UserState.VIP, "reason")

# Tier System
from app.core.unified_states import SubscriptionTier
tier = SubscriptionTier.PREMIUM
limit = tier.ai_message_limit

# Roadmap
from app.services.roadmap_service import roadmap_service
roadmap.insert_item(title, desc, status)
roadmap.update_by_title(title, new_status)

# Testing
pytest tests/ -v --cov=app
```

---

**Ready to build!** 🚀

**Version:** 2.0.0  
**Last Updated:** 2026-02-17
