# 🗺️ FLOW MAP - Freedom Wallet Bot
**Complete User Journey & System Architecture**

Generated: 2026-02-17  
Version: 2.0

---

## 📊 OVERVIEW

This document maps all user flows, state transitions, and system architecture for Freedom Wallet Telegram Bot.

---

## 🎯 CORE FLOWS

### **1. NEW USER REGISTRATION FLOW**

```
┌─────────────────────────────────────────────────────────────┐
│                     NEW USER JOURNEY                         │
└─────────────────────────────────────────────────────────────┘

1️⃣ VISITOR STATE
   ↓ User clicks bot link / /start
   ↓
2️⃣ REGISTRATION
   → Collect: Name, Email, Phone
   → Create User record
   → Assign: referral_code
   → State: VISITOR → REGISTERED
   → Tier: FREE
   ↓
3️⃣ WELCOME MESSAGE
   → Explain 6 Jars method
   → Show feature overview
   → Offer setup guide
   ↓
4️⃣ ONBOARDING (Optional)
   → State: REGISTERED → ONBOARDING
   → Guide: Google Sheets setup
   → Guide: Web app connection
   ↓
5️⃣ UNLOCK (Setup Complete)
   → Tier: FREE → UNLOCK
   → State: ONBOARDING → ACTIVE
   → Full feature access
   ↓
6️⃣ ACTIVE USER
   → Daily transaction logging
   → AI financial insights
   → Budget tracking
```

**Key Decision Points:**
- Skip setup → Remain FREE tier (limited features)
- Complete setup → UNLOCK tier (full access)
- 2+ referrals → VIP state (rewards)

---

### **2. REFERRAL & VIP FLOW**

```
┌─────────────────────────────────────────────────────────────┐
│                    REFERRAL JOURNEY                          │
└─────────────────────────────────────────────────────────────┘

User A (Referrer)
   ↓
Generates unique referral link
   ↓ Shares with friend
   ↓
User B (Referred) clicks link
   ↓
Registers via bot
   ↓
Backend: Link B to A (referred_by = A.id)
   ↓
A.referral_count += 1
   ↓
┌─── Check Milestones ───┐
│                        │
│ 2 refs  → VIP          │
│ 50 refs → SUPER_VIP    │
│ 100 refs → ADVOCATE    │
└────────────────────────┘
   ↓
Auto-transition state
   ↓
Notify user of upgrade
   ↓
Unlock benefits
```

**VIP Benefits:**
- **VIP (2+ refs):** FREE tier forever, exclusive tips, priority support
- **SUPER_VIP (50+ refs):** Premium features trial, coach badge
- **ADVOCATE (100+ refs):** Lifetime Premium, revenue share

---

### **3. FREE → UNLOCK → PREMIUM FLOW**

```
┌─────────────────────────────────────────────────────────────┐
│                   SUBSCRIPTION TIERS                         │
└─────────────────────────────────────────────────────────────┘

FREE TIER
│ Features:
│ - 5 AI messages/day
│ - Basic tutorials
│ - Manual transaction entry only
│ - No Google Sheets integration
│
↓ [Setup Google Sheets]
│
UNLOCK TIER
│ Features:
│ - 20 AI messages/day
│ - Google Sheets integration
│ - Auto-sync transactions
│ - Full 6 Jars method
│ - Budget tracking
│
↓ [Payment: 999k/year]
│
PREMIUM TIER
│ Features:
│ - Unlimited AI messages
│ - Advanced AI insights
│ - Predictive analytics
│ - Custom financial coaching
│ - Priority support
│ - Early access to features
```

**Upgrade Triggers:**
- FREE → UNLOCK: Complete sheets setup
- UNLOCK → PREMIUM: Payment received
- PREMIUM → UNLOCK: Subscription expires (auto-downgrade)

---

### **4. STATE MACHINE TRANSITIONS**

```
┌─────────────────────────────────────────────────────────────┐
│                 USER STATE DIAGRAM                           │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────┐
              ┌────→│ VISITOR  │
              │     └──────────┘
              │          ↓ register
              │     ┌──────────┐
              │     │REGISTERED│←──────┐
              │     └──────────┘       │
              │          ↓ setup       │ re-activation
              │     ┌──────────┐       │
              │     │ONBOARDING│       │
              │     └──────────┘       │
              │          ↓ complete    │
              │     ┌──────────┐       │
        decay │────→│  ACTIVE  │       │
              │     └──────────┘       │
              │          ↓ 2+ refs     │
              │     ┌──────────┐       │
        decay │────→│   VIP    │       │
              │     └──────────┘       │
              │          ↓ 50+ refs    │
              │     ┌──────────┐       │
        decay │────→│SUPER_VIP │       │
              │     └──────────┘       │
              │          ↓ 100+ refs   │
              │     ┌──────────┐       │
              └─────│ ADVOCATE │       │
                    └──────────┘       │
                         ↓             │
                    90+ days inactive  │
                         ↓             │
                    ┌──────────┐       │
                    │ CHURNED  │───────┘
                    └──────────┘
                         ↓ fraud
                    ┌──────────┐
                    │ BLOCKED  │ (terminal)
                    └──────────┘
```

**State Validation Rules:**
- All transitions validated by `StateTransitions.can_transition()`
- Cannot skip states (e.g., VISITOR → VIP directly)
- BLOCKED is terminal (no way out)
- CHURNED can be re-activated to ACTIVE

---

## 🔧 TECHNICAL ARCHITECTURE

### **System Components**

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM LAYERS                             │
└─────────────────────────────────────────────────────────────┘

┌────────────────────────────────────┐
│   TELEGRAM BOT LAYER               │  ← User interaction
│   - Command handlers               │
│   - Callback handlers              │
│   - Message handlers               │
└────────────────────────────────────┘
             ↓
┌────────────────────────────────────┐
│   SERVICE LAYER                    │  ← Business logic
│   - StateManager                   │
│   - SubscriptionService            │
│   - ReferralService                │
│   - AI Service (GPT-4)             │
└────────────────────────────────────┘
             ↓
┌────────────────────────────────────┐
│   DOMAIN LAYER                     │  ← Core models
│   - UserProfile                    │
│   - StateTransitions               │
│   - TierTransitions                │
└────────────────────────────────────┘
             ↓
┌────────────────────────────────────┐
│   DATA LAYER                       │  ← Persistence
│   - SQLAlchemy ORM                 │
│   - PostgreSQL database            │
│   - Google Sheets API              │
└────────────────────────────────────┘
```

---

### **State Machine Manager**

```python
# File: app/core/state_machine.py

class StateManager:
    """
    Central state management
    
    Features:
    - LEGACY user support (backward compatible)
    - Auto-migration on first interaction
    - Validation of all transitions
    - Logging and audit trail
    """
    
    def get_user_state(user_id) -> (UserState, is_legacy)
    def transition_user(user_id, new_state, reason)
    def check_and_update_state_by_referrals(user_id)
```

**Usage:**
```python
from app.core.state_machine import StateManager, UserState

with StateManager() as mgr:
    state, is_legacy = mgr.get_user_state(user_id)
    
    if is_legacy:
        # Auto-migrate
        mgr.transition_user(user_id, UserState.VIP, "Migration")
```

---

### **Unified States System**

```python
# File: app/core/unified_states.py

# Subscription Tiers
class SubscriptionTier(Enum):
    FREE = "FREE"          # Basic access
    UNLOCK = "UNLOCK"      # Full features
    PREMIUM = "PREMIUM"    # Paid subscription

# User States
class UserState(Enum):
    VISITOR = "VISITOR"
    REGISTERED = "REGISTERED"
    ONBOARDING = "ONBOARDING"
    ACTIVE = "ACTIVE"
    VIP = "VIP"
    SUPER_VIP = "SUPER_VIP"
    ADVOCATE = "ADVOCATE"
    CHURNED = "CHURNED"
    BLOCKED = "BLOCKED"
```

---

## 🤖 ROADMAP AUTOMATION

### **When to Update Roadmap**

```
┌─────────────────────────────────────────────────────────────┐
│                 ROADMAP TRIGGERS                             │
└─────────────────────────────────────────────────────────────┘

1. IDEA PROPOSED
   → insertRoadmapItem({status: "IDEA"})
   
2. TASK PLANNED
   → updateRoadmapStatus(id, "PLANNED")
   
3. CODING STARTED
   → updateRoadmapStatus(id, "IN_PROGRESS")
   
4. TASK COMPLETED
   → updateRoadmapStatus(id, "COMPLETED")
   
5. CODE REFACTORED
   → updateRoadmapStatus(id, "REFACTORED")
   
6. RELEASE CREATED
   → logReleaseVersion(version, description, features)
   → Batch update: COMPLETED → RELEASED
   → Append to CHANGELOG.md
```

**Google Apps Script API:**
```javascript
// Add new feature idea
insertRoadmapItem({
  title: "AI Budget Recommendations",
  description: "Auto-suggest budget based on patterns",
  type: "Tính năng",
  status: "IDEA"
});

// Update when development starts
updateRoadmapByTitle(
  "AI Budget Recommendations",
  "IN_PROGRESS"
);

// Log release
logReleaseVersion("v2.1.0", "Budget AI Release", [
  "AI Budget Recommendations",
  "Spending pattern analysis",
  "Smart alerts"
]);
```

---

## 📝 KEY FILES

| File | Purpose |
|------|---------|
| `app/core/unified_states.py` | State & tier definitions |
| `app/core/state_machine.py` | State transition logic |
| `app/utils/database.py` | User model & DB schema |
| `version.py` | Version management |
| `RoadmapAutoInsert_v2.gs` | Roadmap automation |
| `CHANGELOG.md` | Release history |

---

## 🧪 TESTING FLOWS

```
tests/
├── unit/
│   ├── test_state_transitions.py  # State machine logic
│   ├── test_tier_upgrades.py      # Subscription changes
│   └── test_referral_logic.py     # Referral counting
│
├── integration/
│   ├── test_registration_flow.py  # End-to-end registration
│   ├── test_sheets_setup.py       # Google Sheets integration
│   └── test_premium_upgrade.py    # Payment flow
│
└── e2e/
    └── test_complete_journey.py   # VISITOR → PREMIUM
```

**Coverage Goal:** 90%+

---

## 🚀 DEPLOYMENT

```
Production Flow:
1. Run tests: pytest tests/ -v
2. Update version.py (MAJOR.MINOR.PATCH)
3. Update CHANGELOG.md
4. Log to roadmap: logReleaseVersion()
5. Commit & push to git
6. Deploy to Railway.app
7. Monitor health checks
```

---

**Last Updated:** 2026-02-17  
**Version:** 2.0  
**Maintainer:** Freedom Wallet Team
