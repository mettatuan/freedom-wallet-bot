# 🔍 HANDLER ARCHITECTURE AUDIT REPORT

**Date**: February 12, 2026  
**Scope**: app/handlers/ directory (36 handler files)  
**Purpose**: Identify violations before incremental refactor

---

## 📊 AUDIT OVERVIEW

```
Total Handlers:     36 files
Domains:            7 (user, premium, engagement, admin, sheets, core, support)
Lines of Code:      ~12,000+ lines (estimated)

Violations Found:   78 instances
  - Direct DB Access:      53 instances (20+ handlers)
  - Handler→Handler Calls: 26 instances (15+ handlers)
  - Business Logic >30L:   Multiple (uncounted)
```

**Target Architecture**: `Handler → Service → Model`

**Current Reality**: `Handler → Handler → Model → (Handler)` (circular)

---

## 🚨 VIOLATION CATEGORY 1: Direct Database Access in Handlers

**Rule**: Handlers should NOT directly query/commit to database. Should call service layer.

### **HIGH SEVERITY** (>5 queries in single handler)

#### **1. `app/handlers/user/registration.py`** ❌
```python
# Lines 220, 234, 285, 411, 654, 660, 661
db_user = session.query(User).filter(User.id == user.id).first()
referral = session.query(Referral).filter(...).first()
referrer = session.query(User).filter(User.id == referral.referrer_id).first()
session.commit()
```
**Impact**: 150+ line function doing DB queries, fraud checks, VIP checks, state transitions, unlock flows  
**Business Logic**: Mixed with presentation logic (Telegram message formatting)  
**Refactor Target**: Extract to `UserRegistrationService` + `ReferralService`

---

#### **2. `app/handlers/admin/admin_fraud.py`** ❌
```python
# Lines 113, 121, 122, 128, 132, 137
referral = session.query(Referral).filter(Referral.id == referral_id).first()
referrer = session.query(User).filter(User.id == referral.referrer_id).first()
total_refs = session.query(Referral).filter(...).count()
verified_refs = session.query(Referral).filter(...).count()
```
**Impact**: Admin fraud review logic tightly coupled to handler  
**Refactor Target**: Extract to `FraudReviewService`

---

### **MEDIUM SEVERITY** (2-5 queries)

#### **3. `app/handlers/core/callback.py`** ❌
```python
# Line 980
top_users = session.query(User).filter(...).order_by(...).limit(10)
```
**Impact**: 1,700+ line callback handler doing everything  
**Refactor Target**: Split into domain-specific callback handlers, extract to `LeaderboardService`

---

#### **4. `app/handlers/premium/vip.py`** ❌
```python
# Line 126
db_session.commit()
```
**Impact**: VIP milestone checks mixed with presentation  
**Refactor Target**: Extract to `VIPMilestoneService`

---

### **LOW SEVERITY** (1 query, easy extraction)

- `app/handlers/core/message.py` - 1 query
- Additional handlers (grep found 20+ total matches)

---

## 🔁 VIOLATION CATEGORY 2: Handler-to-Handler Calls

**Rule**: Handlers should NOT call other handlers. Should call shared services instead.

### **ARCHITECTURAL DEBT MAP**

```
┌──────────────────────────────────────────────────────┐
│            HANDLER DEPENDENCY GRAPH                  │
│                                                      │
│  start.py                                            │
│    ├─► engagement/referral.py (handle_referral_start)│
│    ├─► user/onboarding.py (start_onboarding_journey) │
│    └─► engagement/daily_nurture.py (start_daily_nurture)
│                                                      │
│  registration.py                                     │
│    ├─► premium/vip.py (check_vip_milestone)         │
│    ├─► engagement/daily_nurture.py (cancel_remaining)│
│    └─► unlock_flow_v3.py (send_unlock_message_1)    │
│                                                      │
│  core/callback.py (1,700+ LINES)                    │
│    ├─► premium/premium_commands.py (PREMIUM_CALLBACKS)
│    ├─► user/start.py (start)                        │
│    ├─► engagement/referral.py (referral_command)    │
│    ├─► engagement/daily_nurture.py (handle_share_link)
│    ├─► user/onboarding.py (start_onboarding_journey)│
│    └─► admin/admin_callbacks.py (log_payment_to_sheets)
│                                                      │
│  user_commands.py                                    │
│    └─► engagement/streak_tracking.py (get_user_streak_stats)
│                                                      │
│  ... 26 total handler→handler imports               │
└──────────────────────────────────────────────────────┘
```

**Impact**: 
- Circular dependency risk ⚠️
- Hard to test (need to mock handlers)
- Business logic scattered across handlers
- Duplication likely (same logic in multiple handlers)

**Root Cause**: No service layer → handlers become "do everything" monoliths

---

### **CRITICAL OFFENDER: `core/callback.py`**

**Current State**:
- 1,727 lines (longest file in codebase)
- Imports from 8+ different handler modules
- Handles 50+ different callback_data patterns
- Mixes:
  - Admin callbacks
  - Premium callbacks
  - Engagement callbacks
  - Support callbacks
  - VIP unlock flows
  - User onboarding triggers

**Why This Exists**:  
Telegram bots typically have 1 callback handler routing to different flows. **This is acceptable as a router**, but should be **thin** - just routing to services/handlers.

**Current Problem**: It does routing AND business logic AND imports other handlers.

**Refactor Strategy**:
1. Keep `callback.py` as router only (200 lines max)
2. Extract domain-specific callback groups:
   - `admin_callbacks.py` (already exists, good!)
   - `premium_callbacks.py` (extract from callback.py)
   - `engagement_callbacks.py` (extract)
   - `support_callbacks.py` (extract)
3. Each callback handler calls services, not other handlers

---

## 🔢 VIOLATION CATEGORY 3: Business Logic in Handlers (>30 lines)

**Rule**: Handlers should be thin adapters. Business logic >30 lines should be extracted to services.

### **Examples Found**:

#### **1. `registration.py` - Line 200-350 (150 lines)** ❌
```python
async def confirm_registration_callback(update, context):
    # ... 150 lines of:
    # - Database queries (User, Referral)
    # - Fraud detection logic
    # - VIP milestone checks
    # - State transitions
    # - Referral count updates
    # - Unlock flow triggers
    # - Telegram message formatting
    # - Error handling
```
**What it SHOULD be**:
```python
async def confirm_registration_callback(update, context):
    """Handler - thin adapter only"""
    user = update.effective_user
    email = context.user_data['email']
    
    # Call service layer
    result = await registration_service.complete_registration(
        user_id=user.id,
        email=email,
        phone=context.user_data.get('phone'),
        full_name=context.user_data['full_name']
    )
    
    # Format response (handler's responsibility)
    if result.success:
        await query.edit_message_text(MSG_REGISTRATION_SUCCESS)
        
        # Trigger post-registration flows (via services)
        if result.referral_verified:
            await referral_service.notify_referrer(result.referrer_id, user.first_name)
```

---

#### **2. `callback.py` - Multiple functions >100 lines** ❌

File too large to audit individual functions, but clear violations exist.

---

## 📈 DOMAIN DISTRIBUTION

**Current Handler Count by Domain**:

```
user/          11 files  (31%)  ← HIGH FRAGMENTATION
premium/        5 files  (14%)
engagement/     5 files  (14%)
admin/          4 files  (11%)
sheets/         4 files  (11%)
core/           4 files  (11%)
support/        3 files  ( 8%)
──────────────────────────────
TOTAL:         36 files
```

**Analysis**:
- `user/` has 11 files - many are variants (quick_record_*, free_*, inline_registration, registration)
- `premium/` has 5 files - includes 2 unlock flows (v3, calm_flow)
- `core/callback.py` handles callbacks for ALL domains (architectural smell)

---

## 🎯 REFACTOR PRIORITIES

### **Phase 1: Extract Service Layer** (2 weeks)

**Target**: Eliminate direct DB access in handlers

**Steps**:
1. Create `app/services/` directory
2. Extract services one by one:
   - `UserRegistrationService` (from registration.py)
   - `ReferralService` (from registration.py, admin_fraud.py)
   - `VIPMilestoneService` (from vip.py)
   - `FraudReviewService` (from admin_fraud.py)
   - `StreakTrackingService` (from engagement/streak_tracking.py)
   - `LeaderboardService` (from callback.py)

**Success Metric**: Zero `session.query()` or `session.commit()` calls in handlers

---

### **Phase 2: Remove Handler→Handler Imports** (1 week)

**Target**: Replace handler calls with service calls

**Strategy**:
- Handlers should only call:
  - Services (business logic)
  - Other handlers via Telegram context (e.g., ConversationHandler transitions)
  - NOT directly import + call handler functions

**Example**:
```python
# BEFORE (BAD):
from app.handlers.premium.vip import check_vip_milestone
await check_vip_milestone(referrer.id, context)

# AFTER (GOOD):
from app.services.vip_service import vip_service
milestone_reached = await vip_service.check_milestone(referrer.id)
if milestone_reached:
    await context.bot.send_message(...)  # Handler formats response
```

---

### **Phase 3: Split Monolithic Handlers** (1 week)

**Target**: Reduce 36 files → ~25 files by merging variants

See **Merge Candidates** section below.

---

## 🔀 HANDLER MERGE CANDIDATES

### **Domain: user/ (11 → 6 files)**

**Merge Group 1: Quick Record variants**
```
CURRENT (3 files):
  - quick_record_direct.py
  - quick_record_webhook.py  
  - quick_record_template.py

AFTER (1 file):
  - quick_record.py
    ├─ handle_direct_record()
    ├─ handle_webhook_record()
    └─ handle_template_record()
```
**Rationale**: Same domain (quick record), different input methods. Can be single module.

---

**Merge Group 2: Registration variants**
```
CURRENT (3 files):
  - registration.py
  - free_registration.py
  - inline_registration.py

AFTER (1 file):
  - registration.py
    ├─ start_registration()        # Main flow
    ├─ start_free_registration()   # Free tier flow
    └─ start_inline_registration() # Inline query flow
```
**Rationale**: All handle user registration, just different entry points.

---

**Result**: user/ goes from **11 → 6 files** (-45% reduction)

---

### **Domain: premium/ (5 → 3 files)**

**Merge Group 3: Unlock flows**
```
CURRENT (2 files):
  - unlock_flow_v3.py
  - unlock_calm_flow.py

AFTER (1 file):
  - unlock_flows.py
    ├─ send_unlock_v3_message_1()
    ├─ send_unlock_v3_message_2()
    └─ send_unlock_calm_message_1()
```
**Rationale**: Both are unlock flows, just different messaging strategies. Combine into versioned functions.

---

**Result**: premium/ goes from **5 → 3 files** (-40% reduction)

---

### **Domain: sheets/ (4 → 3 files)**

**Merge Group 4: Premium data commands**
```
CURRENT (2 files):
  - premium_data_commands.py
  - sheets_premium_commands.py

AFTER (1 file):
  - sheets_premium.py
    ├─ handle_premium_export()
    └─ handle_premium_analysis()
```
**Rationale**: Both handle premium sheets features.

---

**Result**: sheets/ goes from **4 → 3 files** (-25% reduction)

---

### **TOTAL REDUCTION**

```
BEFORE:  36 handler files
AFTER:   25 handler files  (-30% reduction)

Benefits:
  ✅ Easier navigation
  ✅ Reduced import complexity
  ✅ Clearer domain boundaries
  ✅ Less duplication (shared helpers in same file)
```

---

## 📋 SUMMARY & NEXT STEPS

### **Violations Summary**

| Category | Count | Severity |
|----------|-------|----------|
| Direct DB access in handlers | 53 instances | High |
| Handler→Handler imports | 26 instances | High |
| Business logic >30 lines | Multiple | Medium |
| Monolithic files (>1000 lines) | 1 file (callback.py) | High |
| File fragmentation | 11 variants | Low |

---

### **Recommended Execution Order**

**Week 1-2: Service Layer Extraction**
- [ ] Create `app/services/` directory structure
- [ ] Extract `UserRegistrationService` (biggest offender)
- [ ] Extract `ReferralService`
- [ ] Extract `VIPMilestoneService`
- [ ] Extract `FraudReviewService`
- [ ] Update handlers to call services instead of direct DB

**Week 3: Remove Handler→Handler Calls**
- [ ] Replace handler imports with service calls
- [ ] Add service layer tests
- [ ] Verify no circular dependencies

**Week 4: File Consolidation**
- [ ] Merge quick_record variants → 1 file
- [ ] Merge registration variants → 1 file
- [ ] Merge unlock_flow variants → 1 file
- [ ] Merge sheets premium variants → 1 file
- [ ] Update main.py handler registration

**Week 5: Architecture Governance**
- [ ] Write Architecture Constitution (prevent future violations)
- [ ] Add pre-commit hook (detect handler→model queries)
- [ ] Document service layer patterns
- [ ] Add architecture decision log (ADR)

---

## 🏛️ TARGET ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│                 PRESENTATION                     │
│                                                  │
│  app/handlers/                                   │
│    ├─ user/               (6 files)             │
│    ├─ premium/            (3 files)             │
│    ├─ engagement/         (5 files)             │
│    ├─ admin/              (4 files)             │
│    ├─ sheets/             (3 files)             │
│    ├─ core/               (3 files)             │
│    └─ support/            (3 files)             │
│                                                  │
│  Responsibilities:                               │
│    • Parse Telegram updates                     │
│    • Format responses                           │
│    • Handle conversation flow                   │
│    • Call service layer                         │
│                                                  │
│  Rules:                                          │
│    ❌ NO database queries                       │
│    ❌ NO business logic >30 lines               │
│    ❌ NO handler-to-handler calls               │
│    ✅ Call services only                        │
└─────────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────┐
│                 BUSINESS LOGIC                   │
│                                                  │
│  app/services/                                   │
│    ├─ user_registration_service.py              │
│    ├─ referral_service.py                       │
│    ├─ vip_milestone_service.py                  │
│    ├─ fraud_review_service.py                   │
│    ├─ streak_tracking_service.py                │
│    ├─ leaderboard_service.py                    │
│    └─ sheets_integration_service.py             │
│                                                  │
│  Responsibilities:                               │
│    • Business logic (validations, calculations) │
│    • Orchestrate model operations               │
│    • Transaction management                     │
│    • Call repositories/models                   │
│                                                  │
│  Rules:                                          │
│    ❌ NO Telegram-specific code                 │
│    ❌ NO message formatting                     │
│    ✅ Pure Python business logic                │
│    ✅ Easy to unit test                         │
└─────────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────┐
│                  DATA ACCESS                     │
│                                                  │
│  app/utils/database.py (Models)                 │
│    ├─ User                                       │
│    ├─ Referral                                   │
│    ├─ Transaction                                │
│    └─ Payment                                    │
│                                                  │
│  Responsibilities:                               │
│    • SQLAlchemy models                          │
│    • Database queries                           │
│    • Schema definitions                         │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🎓 LESSONS FROM CA ROLLBACK

**Why This Incremental Approach Works**:

1. **No rewrite** - Extract services gradually
2. **No breaking changes** - Handlers still work during refactor
3. **Testable progress** - Each service extraction is independently verifiable
4. **Business continuity** - Bot remains operational throughout
5. **Pragmatic** - Improve what matters (handler→service boundary)

**What We're NOT Doing**:

- ❌ Full Clean Architecture (overkill for solo dev)
- ❌ Repositories layer (SQLAlchemy models are enough)
- ❌ Use cases/entities split (too granular)
- ❌ Dependency injection containers (unnecessary complexity)
- ❌ Event sourcing/CQRS (premature)

**What We ARE Doing**:

- ✅ Clear separation: Handler → Service → Model
- ✅ Testable business logic (services)
- ✅ Maintainable handlers (thin adapters)
- ✅ Domain grouping (fewer files, clearer ownership)
- ✅ Architecture governance (prevent future violations)

---

## 🚀 SUCCESS METRICS

**Before Refactor**:
```
Handler → Handler → Model (circular)
53 direct DB queries in handlers
26 handler→handler imports
36 fragmented handler files
1 file with 1,700+ lines
```

**After Refactor (Target)**:
```
Handler → Service → Model (clean)
0 direct DB queries in handlers
0 handler→handler imports  
25 logical handler modules
No files >500 lines
```

**Timeline**: 4-5 weeks (1 hour/day, steady progress)

**Risk Level**: Low (incremental, non-breaking changes)

---

## 📝 APPENDIX: Full Handler Inventory

```
app/handlers/
├── admin/
│   ├── admin_callbacks.py       [OK - Focused]
│   ├── admin_fraud.py           [❌ Direct DB - 6 queries]
│   ├── admin_metrics.py         [? - Not audited yet]
│   └── admin_payment.py         [? - Not audited yet]
│
├── core/
│   ├── callback.py              [❌ 1,727 lines - Split needed]
│   ├── message.py               [❌ Direct DB - 1 query]
│   ├── webapp_setup.py          [OK - Focused]
│   └── webapp_url_handler.py    [OK - Focused]
│
├── engagement/
│   ├── celebration.py           [? - Not audited yet]
│   ├── daily_nurture.py         [? - Not audited yet]
│   ├── daily_reminder.py        [? - Not audited yet]
│   ├── referral.py              [? - Not audited yet]
│   └── streak_tracking.py       [? - Not audited yet]
│
├── premium/
│   ├── premium_commands.py      [? - Not audited yet]
│   ├── premium_menu_implementation.py [? - Not audited yet]
│   ├── unlock_calm_flow.py      [Merge candidate]
│   ├── unlock_flow_v3.py        [Merge candidate]
│   └── vip.py                   [❌ Direct DB - commit]
│
├── sheets/
│   ├── premium_data_commands.py [Merge candidate]
│   ├── sheets_premium_commands.py [Merge candidate]
│   ├── sheets_setup.py          [? - Not audited yet]
│   └── sheets_template_integration.py [? - Not audited yet]
│
├── support/
│   ├── setup_guide.py           [OK - Focused]
│   ├── support.py               [? - Not audited yet]
│   └── tutorial.py              [OK - Focused]
│
└── user/
    ├── free_flow.py             [? - Not audited yet]
    ├── free_registration.py     [Merge candidate]
    ├── inline_registration.py   [Merge candidate]
    ├── onboarding.py            [? - Not audited yet]
    ├── quick_record_direct.py   [Merge candidate]
    ├── quick_record_template.py [Merge candidate]
    ├── quick_record_webhook.py  [Merge candidate]
    ├── registration.py          [❌ Direct DB - 7+ queries, 150+ line function]
    ├── start.py                 [? - Not audited yet]
    ├── status.py                [? - Not audited yet]
    └── user_commands.py         [? - Not audited yet]
```

---

**Report End** - Ready for Architecture Constitution draft.
