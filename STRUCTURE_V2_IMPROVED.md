# 🏗️ CẤU TRÚC CẢI TIẾN - VERSION 2.0

> **Sau Feedback từ Senior Architect**  
> Target Score: **9.5/10** (từ 8.5/10)

---

## 📊 CẢI TIẾN CHÍNH

### **1. Models Di Chuyển Vào app/**
```diff
- models/                    # ❌ Root level - tách rời
-   ├── user.py
-   └── transaction.py

+ app/
+   ├── models/              # ✅ Trong app - tập trung
+   │   ├── user.py
+   │   └── transaction.py
```

**Lý do:**
- Domain entities tập trung trong `app/`
- Import path nhất quán: `from app.models import User`
- Encapsulation tốt hơn

---

### **2. Core vs Services - Ranh Giới Rõ Ràng**

#### **TRƯỚC (Unclear boundary):**
```
app/
├── core/                   # ❓ Gì cũng có
│   ├── fraud_detection.py  # Service?
│   ├── fraud_detector.py   # Logic?
│   ├── program_manager.py  # Service?
│   └── state_machine.py    # Logic?
└── services/               # ❓ Gì cũng có
    ├── analytics.py
    └── payment_service.py
```

#### **SAU (Clear separation):**
```
app/
├── core/                         # PURE DOMAIN LOGIC ONLY
│   ├── state_machine.py          # State transitions (pure)
│   ├── states.py                 # State definitions
│   ├── fraud_detector.py         # Fraud algorithms (pure)
│   ├── payment_rules.py          # Payment validation rules (pure)
│   └── subscription_rules.py     # Subscription logic (pure)
│
└── services/                     # ORCHESTRATION & WORKFLOWS
    ├── user_service.py           # User workflows
    ├── transaction_service.py    # Transaction workflows
    ├── analytics_service.py      # Analytics orchestration
    ├── payment_service.py        # Payment workflows (uses core/payment_rules)
    ├── fraud_detection_service.py # Fraud workflows (uses core/fraud_detector)
    └── sheets/
        ├── sheets_api_client.py
        ├── sheets_reader.py
        └── sheets_writer.py
```

**Nguyên tắc:**
```
Core:
- Pure functions (no side effects)
- NO database access
- NO external APIs
- NO logging
- ONLY domain rules & algorithms

Services:
- Has side effects (DB, API, logs)
- Orchestrate workflows
- Use Core for domain rules
- Transaction management
```

---

### **3. Docs Structure với Rule Cứng**

```
docs/
├── README.md                      # Navigation index
├── architecture/
│   ├── OVERVIEW.md
│   └── LAYERING.md
├── guides/
│   ├── GETTING_STARTED.md
│   ├── ADDING_FEATURES.md
│   └── DEPLOYMENT.md
├── flows/
│   └── USER_FLOWS.md              # ONE file, Git tracks versions
├── specifications/
│   └── BOT_MASTER_PROMPT.md
└── archive/
    └── (80+ old planning docs)    # Planning docs NOT in main docs/
```

**🔒 Rule Cứng:**
- ❌ KHÔNG tạo planning docs trong `docs/` (DAY1, WEEK1, SPRINT...)
- ❌ KHÔNG multiple versions (USER_FLOWS_v1, v2, v3...)
- ❌ KHÔNG temporary notes được commit
- ✅ Planning → Project management tool (Jira/Linear/Notion)
- ✅ 1 topic = 1 file (Git tracks history)

---

## 🎯 CẤU TRÚC HOÀN CHỈNH V2.0

```
FreedomWalletBot/
│
├── 📄 main.py                      # Entry point
├── 📄 README.md                    # Master README (with architecture diagram)
├── 📄 ARCHITECTURE_RULES.md        # 🔒 3 LAWS + Enforcement
├── 📄 REFACTORING_PLAN.md         # Full refactoring plan
├── 📄 REFACTORING_SUMMARY.md      # Executive summary
├── 📄 requirements.txt
├── 📄 .env
├── 📄 .gitignore
│
├── config/                         # Configuration layer
│   ├── __init__.py
│   ├── settings.py                 # Pydantic settings
│   ├── .env.example
│   └── credentials/
│       └── google_service_account.json
│
├── app/                            # 🎯 Main application
│   │
│   ├── models/                     # ✨ Database models (domain entities)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── subscription.py
│   │   └── analytics.py
│   │
│   ├── handlers/                   # 📨 Telegram handlers (grouped by feature)
│   │   ├── __init__.py
│   │   │
│   │   ├── user/                   # User-facing handlers
│   │   │   ├── __init__.py
│   │   │   ├── start.py
│   │   │   ├── registration.py    # MERGED: registration + inline + free
│   │   │   ├── onboarding.py
│   │   │   ├── quick_record.py    # MERGED: direct + template + webhook
│   │   │   ├── user_commands.py
│   │   │   └── status.py
│   │   │
│   │   ├── premium/                # Premium features
│   │   │   ├── __init__.py
│   │   │   ├── unlock_flow.py     # MERGED: v3 + calm_flow
│   │   │   ├── premium_menu.py
│   │   │   ├── premium_commands.py
│   │   │   └── vip.py
│   │   │
│   │   ├── sheets/                 # Google Sheets integration
│   │   │   ├── __init__.py
│   │   │   ├── sheets_setup.py    # MERGED: setup + template_integration
│   │   │   └── sheets_commands.py # MERGED: premium + data commands
│   │   │
│   │   ├── admin/                  # Admin handlers
│   │   │   ├── __init__.py
│   │   │   ├── admin_callbacks.py
│   │   │   ├── admin_fraud.py
│   │   │   ├── admin_metrics.py
│   │   │   └── admin_payment.py
│   │   │
│   │   ├── engagement/             # User engagement
│   │   │   ├── __init__.py
│   │   │   ├── daily_reminder.py
│   │   │   ├── daily_nurture.py
│   │   │   ├── celebration.py
│   │   │   ├── streak_tracking.py
│   │   │   └── referral.py
│   │   │
│   │   ├── support/                # Support & guides
│   │   │   ├── __init__.py
│   │   │   ├── support.py
│   │   │   ├── tutorial.py
│   │   │   ├── setup_guide.py
│   │   │   └── webapp_setup.py
│   │   │
│   │   └── core/                   # Core handlers
│   │       ├── __init__.py
│   │       ├── message.py          # Text message handling
│   │       ├── callback.py         # Callback query handling
│   │       └── webapp_url_handler.py
│   │
│   ├── services/                   # 🔄 USE CASE ORCHESTRATION (workflows)
│   │   ├── __init__.py
│   │   ├── user_service.py         # User management workflows
│   │   ├── transaction_service.py  # Transaction workflows
│   │   ├── analytics_service.py    # Analytics orchestration
│   │   ├── payment_service.py      # Payment workflows (uses core/payment_rules)
│   │   ├── recommendation_service.py
│   │   ├── fraud_detection_service.py  # Fraud workflows (uses core/fraud_detector)
│   │   │
│   │   └── sheets/                 # Sheets service layer
│   │       ├── __init__.py
│   │       ├── sheets_api_client.py
│   │       ├── sheets_reader.py
│   │       └── sheets_writer.py
│   │
│   ├── core/                       # ⚙️ PURE DOMAIN LOGIC (business rules)
│   │   ├── __init__.py
│   │   ├── state_machine.py        # State transitions (pure logic)
│   │   ├── states.py               # State definitions
│   │   ├── subscription_rules.py   # Subscription validation & rules
│   │   ├── fraud_detector.py       # Fraud detection algorithms (pure)
│   │   ├── payment_rules.py        # Payment calculation & validation (pure)
│   │   └── recommendation_engine.py # Recommendation algorithms (pure)
│   │
│   ├── keyboards/                  # ⌨️ ALL keyboards consolidated
│   │   ├── __init__.py
│   │   ├── user_keyboards.py       # User flow keyboards
│   │   ├── premium_keyboards.py    # Premium keyboards
│   │   ├── admin_keyboards.py      # Admin keyboards
│   │   └── common_keyboards.py     # Shared/common keyboards
│   │
│   ├── ai/                         # 🤖 AI integration
│   │   ├── __init__.py
│   │   ├── context.py
│   │   ├── gpt_client.py
│   │   └── prompts.py
│   │
│   ├── knowledge/                  # 📚 Knowledge base
│   │   ├── __init__.py
│   │   ├── faq.json
│   │   ├── embeddings.py
│   │   └── docs/
│   │
│   ├── middleware/                 # 🛡️ Middleware
│   │   ├── __init__.py
│   │   └── (middleware files)
│   │
│   ├── jobs/                       # ⏰ Background jobs
│   │   ├── __init__.py
│   │   └── (job files)
│   │
│   └── utils/                      # 🔧 Utilities
│       ├── __init__.py
│       ├── database.py             # DB utilities
│       ├── formatters.py           # Text formatting
│       ├── validators.py           # Input validation
│       ├── sheets_helpers.py       # MERGED: sheets + sheets_registration
│       └── decorators.py           # Common decorators
│
├── migrations/                     # 📦 Database migrations
│   ├── __init__.py
│   ├── 001_add_state_program.py
│   └── (other migrations)
│
├── tests/                          # 🧪 Tests
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_services.py
│   │   ├── test_core.py
│   │   └── test_keyboards.py
│   ├── integration/
│   │   ├── test_registration_flow.py
│   │   └── test_sheets_integration.py
│   └── fixtures/
│       └── mock_data.py
│
├── scripts/                        # 📜 Utility scripts
│   ├── admin/
│   ├── database/
│   └── deployment/
│
├── data/                           # 💾 Runtime data
│   ├── logs/
│   │   └── bot.log
│   └── bot.db
│
├── media/                          # 🖼️ Media assets
│   └── (images, gifs, etc.)
│
├── docs/                           # 📚 Documentation (CLEANED)
│   ├── README.md                   # 📍 Navigation index
│   │
│   ├── architecture/               # System architecture
│   │   ├── OVERVIEW.md
│   │   ├── LAYERING.md             # Handler→Service→Core→Model
│   │   └── DATABASE_SCHEMA.md
│   │
│   ├── guides/                     # How-to guides
│   │   ├── GETTING_STARTED.md
│   │   ├── ADDING_FEATURES.md      # Step-by-step guide
│   │   ├── DEPLOYMENT.md
│   │   └── TESTING.md
│   │
│   ├── flows/                      # Flow diagrams & analysis
│   │   ├── USER_FLOWS.md           # All user flows (ONE file)
│   │   ├── REGISTRATION.md
│   │   └── UNLOCK_FLOW.md
│   │
│   ├── specifications/             # Specs & requirements
│   │   ├── BOT_MASTER_PROMPT.md
│   │   ├── FEATURES.md
│   │   └── API_SPECS.md
│   │
│   └── archive/                    # 🗄️ Old docs (80+ files moved here)
│       ├── planning/               # Old planning docs
│       │   ├── DAY1_SUMMARY.md
│       │   ├── WEEK_1_TEST.md
│       │   └── (70+ other files)
│       └── flows_old/              # Old flow versions
│           ├── FREE_FLOW_v1.md
│           └── (old versions)
│
└── _archive/                       # 🗂️ Historical code (keep as-is)
    └── (old implementations)
```

---

## 🔄 LAYERING ARCHITECTURE

### **Dependency Flow:**
```
┌─────────────────────────────────────────────────┐
│                   HANDLERS                      │
│          (Input → Service → Output)             │
│               NO Business Logic                 │
└───────────────────┬─────────────────────────────┘
                    ↓ calls
┌─────────────────────────────────────────────────┐
│                  SERVICES                       │
│         (Orchestrate Workflows)                 │
│    • Coordinate Core + Models + APIs           │
│    • Transaction management                     │
│    • Side effects (DB, logging, API calls)     │
└──────────┬───────────────────────┬──────────────┘
           ↓ uses                  ↓ accesses
┌──────────────────────┐   ┌──────────────────────┐
│       CORE           │   │      MODELS          │
│  (Domain Rules)      │   │  (Data Entities)     │
│  • Pure functions    │   │  • SQLAlchemy models │
│  • NO side effects   │   │  • Relationships     │
│  • Algorithms        │   └──────────┬───────────┘
└──────────────────────┘              ↓
                                  DATABASE
```

### **Import Rules:**
```python
# ✅ ALLOWED
handlers → services
services → core
services → models
models → (nothing in app/)

# ❌ FORBIDDEN
handlers → models (must go through services)
core → services
core → models
core → anything with side effects
```

---

## 📏 KEY IMPROVEMENTS SUMMARY

| Aspect | Before | After | Impact |
|--------|--------|-------|--------|
| **Models location** | `/models` (root) | `/app/models` | Better encapsulation |
| **Core vs Services** | Unclear boundary | Clear separation | Maintainable |
| **Docs structure** | 90+ files chaos | 15 core + archive | Discoverable |
| **Docs rule** | No rules | STRICT: no planning docs | Stays clean |
| **Architecture diagram** | None | Added to README | Quick understanding |
| **3 Laws** | Implicit | Explicit in ARCHITECTURE_RULES.md | Enforceable |
| **PR Checklist** | Basic | Comprehensive with examples | Quality control |

---

## 🎯 SCORE PROGRESSION

| Version | Score | Improvements |
|---------|-------|--------------|
| **V0 (Current)** | 4.5/10 | Baseline |
| **V1 (Initial Plan)** | 8.5/10 | Basic refactoring |
| **V2 (After Feedback)** | **9.5/10** | All improvements applied |

**Để đạt 10/10 cần:**
- 6 tháng running production với 0 violations
- Team fully onboarded & following rules
- Metrics tracked & maintained
- No architecture drift

---

## 🚀 IMPLEMENTATION ORDER (Updated)

### **Phase 2: Core Restructure (Cập nhật)**

#### **Step 1: Rename & Create Structure**
```bash
# Rename bot/ to app/
git mv bot app

# Create new directories
mkdir app/models
mkdir app/handlers/user app/handlers/premium app/handlers/sheets
mkdir app/handlers/admin app/handlers/engagement app/handlers/support
mkdir app/handlers/core
mkdir app/keyboards
mkdir config/credentials

# Move models into app
# (will create new files organized properly)
```

#### **Step 2: Reorganize Core vs Services**
```bash
# Keep in core/ (pure domain logic):
# - state_machine.py
# - states.py
# - fraud_detector.py (algorithms only)

# Move to services/ (if has side effects):
# - program_manager.py → user_service.py
# - reminder_scheduler.py → notification_service.py
# - fraud_detection.py → fraud_detection_service.py
```

#### **Step 3: Move Config**
```bash
mv google_service_account.json config/credentials/
```

---

## ✅ FINAL CHECKLIST

### **Before Starting:**
- [ ] Review [ARCHITECTURE_RULES.md](ARCHITECTURE_RULES.md)
- [ ] Understand layering: Handler → Service → Core → Model
- [ ] Team alignment meeting (2 hours)

### **During Refactoring:**
- [ ] Follow structure exactly as designed
- [ ] Move models to `app/models/`
- [ ] Separate core (pure) from services (orchestration)
- [ ] No versioned files
- [ ] Archive 80+ old docs
- [ ] Keep docs/ clean with strict rules

### **After Refactoring:**
- [ ] Architecture diagram in README ✅
- [ ] ARCHITECTURE_RULES.md enforced ✅
- [ ] All tests passing
- [ ] Zero violations of 3 laws
- [ ] Documentation updated
- [ ] Team training completed

---

## 📊 SUCCESS METRICS V2.0

| Metric | Before | V1 Target | V2 Target | Current |
|--------|--------|-----------|-----------|---------|
| **Find file time** | 2-5 min | < 30s | < 20s | - |
| **Onboard dev** | 3-5 days | 4-6 hours | 3-4 hours | - |
| **Understand system** | 1-2 weeks | 10 min read | 5 min + diagram | - |
| **Code violations** | - | < 5% | 0% | - |
| **Docs files** | 90+ | 15 | 15 (strict rule) | - |
| **Architecture score** | 4.5/10 | 8.5/10 | **9.5/10** | - |

---

## 🎓 NEXT: Team Training

After refactoring complete:

**Week 1: Understanding**
- Day 1-2: Read docs (README, ARCHITECTURE_RULES, guides)
- Day 3: Architecture walkthrough session (2 hours)
- Day 4: Code review examples (good vs bad)
- Day 5: Quiz (must pass 90%)

**Week 2: Practice**
- Day 1-2: Fix existing violations (pair programming)
- Day 3-4: First feature PR (with mentor)
- Day 5: Independent PR (with review)

**Week 3: Enforce**
- All PRs follow checklist
- Zero tolerance for violations
- Weekly metrics review

---

**Status:** 🟢 Ready for Implementation  
**Version:** 2.0 (Improved)  
**Target Score:** 9.5/10  
**Timeline:** 10-12 days  
**Next:** Await final approval → Start Phase 2

---

**Created:** 2026-02-12  
**Updated:** 2026-02-12 (Post-feedback)  
**Owner:** Senior Architect Team
