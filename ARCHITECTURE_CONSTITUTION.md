# 🏛️ ARCHITECTURE CONSTITUTION

**Version**: 1.0  
**Effective Date**: February 12, 2026  
**Last Updated**: February 12, 2026  
**Owner**: @elirox_dev  
**Status**: Active

---

## 📜 PURPOSE

This document defines the **non-negotiable architectural rules** for FreedomWalletBot codebase. These rules exist to:

1. **Prevent architectural drift** - No spontaneous experimental architectures
2. **Maintain simplicity** - Solo developer project, not enterprise system
3. **Ensure maintainability** - Code should be understandable in 6 months
4. **Enable velocity** - Architecture should accelerate, not block, feature development

**History Context**: After CA experiment (10% feature coverage after weeks), we learned that architecture must serve product goals, not vice versa. This constitution prevents future architectural experiments from derailing production.

---

## 🚫 THE FIVE COMMANDMENTS

### **1. ONE RUNTIME ONLY**

```
❌ FORBIDDEN:
  - Dual architectures running in parallel
  - Feature flags switching between architectural styles
  - "Experiment" code paths alongside production code

✅ REQUIRED:
  - Single, unified runtime
  - All features follow same patterns
  - Experimental code must be in branches, not main
```

**Rationale**: Running CA + Legacy simultaneously caused:
- Model confusion (2 User models with different primary keys)
- Import chaos (which handler to use?)
- Maintenance burden (fix bugs in 2 places)
- Mental overhead (which system am I in?)

**Enforcement**: Any PR introducing parallel architecture systems will be rejected.

---

### **2. NO EXPERIMENTAL PARALLEL ARCHITECTURE**

```
❌ FORBIDDEN:
  - Creating src/ alongside app/ 
  - Implementing "new architecture" while old one still active
  - Gradual migration without removing old code
  - "Version 2" directories (app_v2/, handlers_v2/)

✅ REQUIRED:
  - Refactor in place (modify existing files)
  - Incremental improvements (one module at a time)
  - Delete old code before merging new patterns
  - Branch-based experiments only (never on main)
```

**Example - Bad**:
```
app/handlers/registration.py  # Old
src/presentation/handlers/registration_handler.py  # New (CA)
```

**Example - Good**:
```
# Branch: refactor/extract-registration-service
app/handlers/registration.py  # Refactored in place
app/services/registration_service.py  # New service extracted
```

**Rationale**: Parallel architectures create:
- Duplication (2x code to maintain)
- Confusion (which to modify?)
- Incomplete migrations (10% done, then abandoned)
- Dead code accumulation

**Enforcement**: CI rejects PRs with src/ or app_v2/ directories.

---

### **3. NO DUAL MODELS**

```
❌ FORBIDDEN:
  - Multiple ORM models for same database table
  - Different model attribute names for same DB column
  - Parallel Pydantic/SQLAlchemy models with different schemas

✅ REQUIRED:
  - One model class per database table
  - Standard location: app/utils/database.py (legacy) or app/models/ (future)
  - Column mapping allowed (e.g., id = Column("user_id", ...))
  - SQLAlchemy as single source of truth
```

**Rationale**: CA experiment had:
```python
# Legacy: app/utils/database.py
class User(Base):
    id = Column("user_id", Integer, primary_key=True)  # Maps to user_id

# CA: src/domain/entities/user.py
class User:
    user_id: int  # Different name, same column
```

This caused `sqlite3.OperationalError: no such column: users.id` when CA handlers queried legacy DB.

**Enforcement**: Grep pre-commit hook detects duplicate model definitions.

---

### **4. NO VERSIONED FILES**

```
❌ FORBIDDEN:
  - unlock_flow_v1.py, unlock_flow_v2.py, unlock_flow_v3.py
  - registration_old.py, registration_new.py
  - handler_legacy.py, handler_refactored.py
  - file.py.backup, file_backup_20260212.py

✅ REQUIRED:
  - Git tracks history (git log, git blame)
  - Delete old versions before committing new
  - Use feature flags for A/B testing, not file duplication
  - Backups belong in git tags/branches, not main branch
```

**Current Violations** (to be fixed):
```
app/handlers/premium/unlock_flow_v3.py  # Keep, rename to unlock_flow.py
app/handlers/premium/unlock_calm_flow.py  # Merge into unlock_flow.py
```

**Rationale**: Git is our version control. File-based versioning causes:
- Import confusion (which version is active?)
- Dead code accumulation
- Merge conflicts (modify wrong version)

**Enforcement**: CI rejects files with version suffixes (_v1, _v2, etc.) except in _archive/.

---

### **5. HANDLER → SERVICE → MODEL ONLY**

```
❌ FORBIDDEN:
  - Handler → Model (direct DB queries)
  - Handler → Handler (circular dependencies)
  - Model → Handler (backwards dependency)
  - Service → Handler (presentation in business logic)

✅ REQUIRED:
  - Handler → Service → Model (unidirectional flow)
  - Thin handlers (<50 lines business logic)
  - Services contain business logic
  - Models are pure data (SQLAlchemy ORM)
```

**Architecture Diagram**:
```
┌──────────────────────────────────────┐
│  PRESENTATION                         │
│  app/handlers/                        │
│  • Parse Telegram updates            │
│  • Format responses                  │
│  • Call services                     │
│                                      │
│  Rules:                              │
│  ❌ NO session.query()              │
│  ❌ NO session.commit()             │
│  ❌ NO importing other handlers     │
│  ✅ Call services only              │
└──────────────────────────────────────┘
            ▼
┌──────────────────────────────────────┐
│  BUSINESS LOGIC                       │
│  app/services/                        │
│  • Validations                       │
│  • Calculations                      │
│  • Orchestration                     │
│  • Transaction management            │
│                                      │
│  Rules:                              │
│  ❌ NO Telegram imports             │
│  ❌ NO message formatting           │
│  ✅ Pure Python business logic      │
│  ✅ Easy to unit test               │
└──────────────────────────────────────┘
            ▼
┌──────────────────────────────────────┐
│  DATA ACCESS                          │
│  app/utils/database.py (models)      │
│  • SQLAlchemy models                 │
│  • Database schema                   │
│  • Queries via ORM                   │
└──────────────────────────────────────┘
```

**Current State**: Handlers do everything (see `HANDLER_AUDIT_REPORT.md`)

**Target State**: Gradual service extraction over 4 weeks

**Enforcement**: 
- Code review checklist: "Does this handler call session.query()?"
- Pre-commit hook: Detect `session.query()` in app/handlers/
- Audit quarterly using grep

---

## ⚖️ GOVERNANCE

### **Architecture Change Process**

**Who Can Modify Architecture**:
- Solo developer project → Owner decides
- Team project → Requires 2+ developer approval

**When Architecture Changes Are Allowed**:
1. **Major pain point** - Current architecture blocks critical feature
2. **Technical debt crisis** - Code unmaintainable
3. **Scale requirements** - User growth demands redesign

**When Architecture Changes Are NOT Allowed**:
1. **Chasing trends** - "Let's try Clean Architecture because it's popular"
2. **Resume building** - "I want to learn DDD"
3. **Premature optimization** - "We might need microservices someday"
4. **Boredom** - "Current code is boring, let's rewrite"

### **Required Justification for Architecture Changes**

Before proposing architecture change, answer **all 5 questions**:

1. **What problem does current architecture cause?**  
   (Vague: "messy code" ❌ | Specific: "53 handlers with direct DB queries" ✅)

2. **What is the business impact?**  
   (Vague: "hard to maintain" ❌ | Specific: "3 bugs/week from handler-DB coupling" ✅)

3. **What is the migration cost?**  
   (Vague: "a few weeks" ❌ | Specific: "400 hours = 10 weeks @ 1hr/day" ✅)

4. **What is the ROI?**  
   (Vague: "better code" ❌ | Specific: "Save 5 hours/month debugging = 60 hours/year" ✅)

5. **Can we solve it incrementally?**  
   (If YES → Do that instead of big architecture change)

**Example - Good Justification**:
```markdown
## Proposal: Extract Service Layer

**Problem**: 53 instances of direct DB queries in handlers
**Business Impact**: 
  - 3 bugs/week from business logic in handlers
  - 2 hours/week debugging
  - Unable to unit test business logic

**Migration Cost**: 
  - 4 weeks @ 1 hour/day = 28 hours
  - Extract 7 services gradually
  - Non-breaking (handlers keep working)

**ROI**: 
  - Save 2 hours/week = 104 hours/year
  - Break-even in 3 months
  - Positive ROI after 3 months

**Incremental?**: YES
  - One service at a time
  - No rewrite
  - No parallel architecture

**Approved**: ✅
```

**Example - Bad Justification**:
```markdown
## Proposal: Migrate to Clean Architecture

**Problem**: Code is messy
**Business Impact**: Hard to maintain
**Migration Cost**: A few weeks
**ROI**: Better code quality
**Incremental?**: We'll do it gradually

**Rejected**: ❌ (vague, no metrics, CA already failed once)
```

---

## 🛡️ ENFORCEMENT MECHANISMS

### **1. Pre-Commit Hooks**

```bash
# .git/hooks/pre-commit

# Check 1: No dual models
if git diff --cached --name-only | grep -qE "src/.*models|domain/.*entities"; then
  echo "❌ ARCHITECTURE VIOLATION: Dual models detected"
  echo "Rule: ONE MODEL PER TABLE (app/utils/database.py)"
  exit 1
fi

# Check 2: No versioned files
if git diff --cached --name-only | grep -qE "_v[0-9]+\.py$|_old\.py$|_new\.py$"; then
  echo "❌ ARCHITECTURE VIOLATION: Versioned file detected"
  echo "Rule: Use git for versioning, not filenames"
  exit 1
fi

# Check 3: No direct DB queries in handlers
if git diff --cached app/handlers/ | grep -qE "session\.query\(|session\.commit\("; then
  echo "⚠️  ARCHITECTURE WARNING: Direct DB query in handler"
  echo "Rule: Handlers should call services, not DB directly"
  echo "Proceed? (y/n)"
  # Allow with confirmation (gradual migration)
fi

# Check 4: No handler→handler imports
if git diff --cached app/handlers/ | grep -qE "from app\.handlers\..*import"; then
  echo "⚠️  ARCHITECTURE WARNING: Handler importing another handler"
  echo "Rule: Handlers should call services, not other handlers"
  echo "Proceed? (y/n)"
fi
```

### **2. Code Review Checklist**

Before approving PR, verify:

- [ ] No parallel architecture directories (src/, app_v2/, etc.)
- [ ] No duplicate models for same table
- [ ] No versioned files (_v1, _v2, _old, _new)
- [ ] Handlers don't directly query DB (use services)
- [ ] Handlers don't import other handlers (use services)
- [ ] New service layer properly tested
- [ ] Architecture changes justified (if applicable)

### **3. Quarterly Architecture Audit**

**Every 3 months**, run automated audit:

```bash
# Audit script: scripts/audit_architecture.sh

echo "🔍 Running Architecture Audit..."

# Count violations
DB_IN_HANDLERS=$(grep -rn "session.query\|session.commit" app/handlers/ | wc -l)
HANDLER_IMPORTS=$(grep -rn "from app.handlers" app/handlers/ | wc -l)
VERSIONED_FILES=$(find app/ -name "*_v[0-9]*.py" -o -name "*_old.py" -o -name "*_new.py" | wc -l)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ARCHITECTURE HEALTH REPORT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Direct DB queries in handlers: $DB_IN_HANDLERS"
echo "Handler→Handler imports: $HANDLER_IMPORTS"
echo "Versioned files: $VERSIONED_FILES"
echo ""

if [ $DB_IN_HANDLERS -gt 0 ] || [ $HANDLER_IMPORTS -gt 0 ] || [ $VERSIONED_FILES -gt 0 ]; then
  echo "⚠️  VIOLATIONS DETECTED"
  echo "See HANDLER_AUDIT_REPORT.md for details"
else
  echo "✅ ARCHITECTURE COMPLIANT"
fi
```

**Trigger**: 
- Manually every quarter
- Automatically on release branches
- Before deployment to production

---

## 📚 APPROVED PATTERNS

### **Pattern 1: Service Extraction**

**Status**: ✅ Approved (incremental improvement)

```python
# BEFORE (violation):
# app/handlers/user/registration.py
async def complete_registration(update, context):
    session = SessionLocal()
    user = session.query(User).filter(User.id == ...).first()
    user.email = email
    session.commit()
    await update.message.reply_text("✅ Done!")

# AFTER (compliant):
# app/services/registration_service.py
class RegistrationService:
    def complete_registration(self, user_id: int, email: str):
        session = SessionLocal()
        user = session.query(User).filter(User.id == user_id).first()
        user.email = email
        session.commit()
        return user

# app/handlers/user/registration.py
async def complete_registration(update, context):
    user = await registration_service.complete_registration(
        user_id=update.effective_user.id,
        email=context.user_data['email']
    )
    await update.message.reply_text("✅ Done!")
```

---

### **Pattern 2: Handler Consolidation**

**Status**: ✅ Approved (reduces fragmentation)

```python
# BEFORE (3 files):
# quick_record_direct.py
# quick_record_webhook.py
# quick_record_template.py

# AFTER (1 file):
# quick_record.py
async def handle_direct_record(...): pass
async def handle_webhook_record(...): pass
async def handle_template_record(...): pass
```

---

### **Pattern 3: Column Mapping**

**Status**: ✅ Approved (pragmatic ORM pattern)

```python
# Intentional design (NOT a hack):
class User(Base):
    __tablename__ = "users"
    
    # Model attribute: id (application code uses this)
    # Database column: user_id (SQLite schema has this)
    id = Column("user_id", Integer, primary_key=True)
    
    # Rationale: 
    # - Preserves 100+ existing User.id references in code
    # - Standard SQLAlchemy pattern (not a workaround)
    # - Documented in ARCHITECTURE_DECISION.md
```

---

## 🚫 REJECTED PATTERNS

### **Anti-Pattern 1: Clean Architecture (Full)**

**Status**: ❌ Rejected (overkill for solo dev)

**Rationale**:
- Attempted in CA experiment (Jan-Feb 2026)
- 10% feature coverage after 3 weeks
- 90% feature gap vs legacy
- Negative ROI (400 hours to migrate)
- Better: Incremental service extraction

**See**: `ARCHITECTURE_DECISION.md` for full analysis

---

### **Anti-Pattern 2: Microservices**

**Status**: ❌ Rejected (premature)

**Rationale**:
- 1,000 users (not 1M)
- Monolith handles load fine
- Microservices add:
  - Inter-service communication complexity
  - Distributed transaction challenges
  - Deployment overhead
  - Monitoring complexity

**When to Reconsider**: 
- 100k+ users
- Team size 10+ developers
- Multiple products sharing services

---

### **Anti-Pattern 3: Repositories Layer**

**Status**: ❌ Rejected (unnecessary abstraction)

**Rationale**:
- SQLAlchemy models already abstract DB
- Adding repository layer = extra indirection
- No plan to switch from SQLAlchemy
- Better: Services call models directly

```python
# ❌ DON'T DO THIS (unnecessary layer):
class UserRepository:
    def get_by_id(self, user_id: int):
        return session.query(User).filter(User.id == user_id).first()

# ✅ DO THIS (service calls model directly):
class UserService:
    def get_user(self, user_id: int):
        return session.query(User).filter(User.id == user_id).first()
```

---

## 📖 LEARNING FROM HISTORY

### **Case Study: CA Rollback (February 2026)**

**What Happened**:
- Implemented Clean Architecture alongside legacy
- Dual architecture: src/ (CA) + app/ (legacy)
- After 3 weeks: 4 handlers in CA, 40+ in legacy
- Dual User models caused runtime errors
- Decision: Rollback CA, keep legacy, extract services incrementally

**Lessons Learned**:

1. **"Architecture serves product, not vice versa"**  
   CA was elegant but blocked feature development

2. **"Big-bang migrations fail, incremental wins"**  
   400 hours = 10 weeks = too long for ROI

3. **"Dual systems = double maintenance"**  
   Fixing bugs in 2 places unsustainable

4. **"Column mapping isn't a hack"**  
   Standard ORM pattern, just document it

5. **"Know when to rollback"**  
   Sunk cost fallacy avoided → saved 300+ hours

**Outcome**:
- Rolled back CA professionally (5 phases)
- Preserved learnings in _archive/
- Wrote this constitution
- Defined incremental refactor path (4 weeks)

**References**:
- `ARCHITECTURE_DECISION.md` - Full rollback rationale
- `ARCHITECTURE_GAP_ANALYSIS.md` - Feature gap breakdown
- `_archive/clean_architecture_experiment/README.md` - Preserved CA code

---

## ✅ AMENDMENT PROCESS

This constitution can be amended when:

1. **Context changes significantly**:
   - User base grows 10x (1k → 10k users)
   - Team size grows (1 → 5+ developers)
   - Product pivots (bot → web app)

2. **Evidence of pain**:
   - Metrics show current rules block velocity
   - Bug rate increases despite following rules
   - Developer frustration documented

3. **Proposal process**:
   - Write ADR (Architecture Decision Record)
   - Justify change with metrics
   - Review quarterly audit results
   - Update this constitution
   - Communicate to team

**Example - Valid Amendment**:
```markdown
## Amendment 1.1 - Allow Repository Layer

**Context**: Migrating from SQLite to PostgreSQL + Redis
**Pain Point**: 15 services need to support dual databases during migration
**Proposal**: Add repository abstraction for database switching
**ROI**: Enables 2-week phased migration vs 6-week big-bang
**Approved**: 2026-06-15
```

---

## 🎯 SUCCESS CRITERIA

**This constitution succeeds if**:

- ✅ No parallel architectures introduced in next 12 months
- ✅ No spontaneous "Clean Architecture v2" experiments
- ✅ Service layer extraction happens incrementally (not big-bang)
- ✅ Handler count reduced from 36 → 25 via consolidation
- ✅ Direct DB queries in handlers reduced from 53 → 0
- ✅ Handler→Handler imports reduced from 26 → 0
- ✅ Developer can understand codebase in 30 minutes (not 3 days)

**Review Date**: August 12, 2026 (6 months)

---

## 📞 QUESTIONS?

**"What if I have a great architecture idea?"**

1. Check if it solves a real problem (not theoretical)
2. Write proposal with metrics (see Governance section)
3. Try it in a branch first (never on main)
4. Measure ROI before full migration
5. Remember: CA experiment failed, incremental refactor works

**"Can I use Design Patterns?"**

Yes! Patterns are good. What's banned:
- ❌ Full architecture paradigm shifts (Clean, Hexagonal, Onion)
- ❌ Parallel architecture systems (dual runtimes)
- ✅ Service pattern (approved)
- ✅ Strategy pattern (for A/B tests)
- ✅ Observer pattern (for events)

**"What if current rules block me?"**

1. Document the blocker (specific example)
2. Propose minimal rule change
3. Justify with metrics/pain points
4. Update constitution if approved

---

**Constitution End** - Architecture is now governed. 🏛️
