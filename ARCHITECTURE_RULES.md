# 🏛️ ARCHITECTURE RULES - BẮT BUỘC

> **3 Luật Kiến Trúc Không Được Phá**  
> Enforce trong mọi Pull Request
## 🏛 Architecture Ownership

Architecture Owner: [FREEDOM WALLET BOT]

Only the Architecture Owner can:
- Approve structural changes
- Approve new root folders
- Modify layering rules
- Approve RFC architecture changes

Any structural PR without Architecture Owner approval = reject.

---

## 🔒 3 LUẬT BẮT BUỘC

### **LAW #1: Handler Chỉ Làm 3 Việc**

```python
# ✅ ĐÚNG
async def my_handler(update: Update, context: Context):
    """Handler pattern chuẩn."""
    # 1. Nhận input
    user_id = update.effective_user.id
    message = update.message.text
    
    # 2. Gọi service (business logic ở đây)
    from app.services.user_service import process_user_action
    result = await process_user_action(user_id, message)
    
    # 3. Trả response
    from app.keyboards.user_keyboards import main_menu
    await update.message.reply_text(result, reply_markup=main_menu())
```

```python
# ❌ SAI - Business logic trong handler
async def bad_handler(update: Update, context: Context):
    user_id = update.effective_user.id
    
    # ❌ KHÔNG ĐƯỢC: Query DB trực tiếp
    user = db.query(User).filter_by(id=user_id).first()
    
    # ❌ KHÔNG ĐƯỢC: Business logic
    if user.premium and user.balance > 1000:
        discount = 0.2
    else:
        discount = 0
    
    # ❌ KHÔNG ĐƯỢC: Hard-code keyboard
    keyboard = [[InlineKeyboardButton("OK", callback_data="ok")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f"Discount: {discount}", reply_markup=reply_markup)
```

**Enforcement:**
- ❌ Reject PR nếu handler có:
  - DB query trực tiếp
  - Business logic (if/else rules)
  - Hard-code keyboard
  - Calculation logic
  - External API calls trực tiếp

---

### **LAW #2: Không Versioned Files**

```bash
# ❌ SAI - Version trong tên file
unlock_flow_v1.py
unlock_flow_v2.py
unlock_flow_v3.py
unlock_flow_final.py
unlock_flow_new.py
unlock_flow_2026.py
registration_old.py
registration_backup.py

# ✅ ĐÚNG - Một file duy nhất, Git quản lý history
unlock_flow.py
registration.py
```

**Git Manages History:**
```bash
# Xem history
git log unlock_flow.py

# Xem changes
git diff HEAD~1 unlock_flow.py

# Rollback nếu cần
git checkout HEAD~1 -- unlock_flow.py
```

**Enforcement:**
- ❌ Reject PR nếu:
  - File name có `_v1`, `_v2`, `_final`, `_new`, `_old`
  - File name có date/year: `_2026`, `_jan`
  - Có backup files: `*.backup`, `*.old`

**Exception (DUY NHẤT):**
- Migration files: `001_add_user_table.py` (OK vì convention)

---

### **LAW #3: Không Thêm Root-Level Folders Tùy Tiện**

```
# ✅ ĐÚNG - Folders được phép (đã design)
FreedomWalletBot/
├── app/              ✅ Main application
├── config/           ✅ Configuration
├── tests/            ✅ Tests
├── docs/             ✅ Documentation
├── migrations/       ✅ DB migrations
├── scripts/          ✅ Utility scripts
├── data/             ✅ Runtime data
├── media/            ✅ Media assets
└── _archive/         ✅ Historical code
```

```
# ❌ SAI - Folders không được thêm
FreedomWalletBot/
├── helpers/          ❌ Use app/utils/
├── common/           ❌ Use app/utils/
├── shared/           ❌ Use app/utils/
├── lib/              ❌ Use app/
├── core/             ❌ Use app/core/
├── services/         ❌ Use app/services/
├── misc/             ❌ Use app/utils/
├── temp/             ❌ Use .gitignore
└── backup/           ❌ Use Git
```

**Nguyên tắc:**
- Nếu muốn thêm folder mới → Phải có **lý do kiến trúc rõ ràng**
- Không được tạo "catch-all" folders như `helpers/`, `misc/`
- Mọi code phải thuộc về `app/` hoặc một trong các folders đã design

**Enforcement:**
- ❌ Reject PR ngay nếu:
  - Thêm folder cấp cao mới không trong approved list
  - Tạo `helpers/`, `common/`, `shared/`, `misc/`, `temp/`

---

## 🎯 LAYERING ARCHITECTURE

### **Nguyên tắc phân tách trách nhiệm:**

```
┌──────────────────────────────────┐
│         HANDLERS                 │  ← Input/Output only
│  (Receive → Call → Respond)      │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│         SERVICES                 │  ← Orchestration
│  (Coordinate workflows)          │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│          CORE                    │  ← Domain Rules
│  (Business logic & algorithms)   │
└────────────┬─────────────────────┘
             ↓
┌──────────────────────────────────┐
│         MODELS                   │  ← Data Entities
│  (Database schema)               │
└────────────┬─────────────────────┘
             ↓
         DATABASE
```

### **Layer Responsibilities:**

#### **1. Handlers Layer** (`app/handlers/`)
**ONLY:**
- Extract input từ Telegram Update
- Call service functions
- Format & send response
- Handle Telegram-specific errors

**KHÔNG ĐƯỢC:**
- Business logic
- Direct DB access
- External API calls
- Calculations

#### **2. Services Layer** (`app/services/`)
**ONLY:**
- Orchestrate workflows
- Coordinate between Core, Models, External APIs
- Transaction management
- Error handling & retry logic

**Example:**
```python
# app/services/payment_service.py
from app.core.payment_rules import calculate_discount
from app.models import User, Payment
from app.services.sheets.sheets_writer import log_payment

async def process_payment(user_id: int, amount: float):
    """Orchestrate payment workflow."""
    # 1. Get data
    user = await User.get(user_id)
    
    # 2. Apply domain rules (từ Core)
    discount = calculate_discount(user.tier, amount)
    final_amount = amount - discount
    
    # 3. Execute transaction
    payment = await Payment.create(
        user_id=user_id,
        amount=final_amount,
        discount=discount
    )
    
    # 4. Side effects (log, notify)
    await log_payment(payment)
    
    return payment
```

#### **3. Core Layer** (`app/core/`)
**ONLY:**
- Pure domain logic
- Business rules & validations
- Algorithms (fraud detection, recommendations)
- State machine logic

**KHÔNG ĐƯỢC:**
- DB access
- External API calls
- Logging (except critical errors)
- Side effects

**Example:**
```python
# app/core/payment_rules.py
def calculate_discount(tier: str, amount: float) -> float:
    """Pure domain rule - no side effects."""
    if tier == "VIP":
        return amount * 0.20
    elif tier == "PREMIUM":
        return amount * 0.10
    else:
        return 0.0
```

#### **4. Models Layer** (`app/models/`)
**ONLY:**
- SQLAlchemy model definitions
- Basic model methods (CRUD helpers)
- Relationships

**KHÔNG ĐƯỢC:**
- Business logic
- Complex calculations
- External API calls

---

## 📏 FOLDER RULES

### **app/core vs app/services - Ranh Giới Rõ Ràng**

| Tiêu chí | **app/core/** | **app/services/** |
|----------|--------------|-------------------|
| **Vai trò** | Domain rules | Workflow orchestration |
| **Pure?** | Pure functions (no side effects) | Has side effects (DB, API, logs) |
| **Import** | KHÔNG import models, services | Import core, models |
| **DB Access** | ❌ KHÔNG | ✅ CÓ |
| **External API** | ❌ KHÔNG | ✅ CÓ |
| **Logging** | ❌ KHÔNG (except critical) | ✅ CÓ |
| **Example** | `calculate_discount()`, `is_fraud()` | `process_payment()`, `send_notification()` |

### **Example Breakdown:**

```python
# ✅ app/core/fraud_detector.py (Pure domain logic)
def is_suspicious_transaction(amount: float, user_history: list) -> bool:
    """Pure function - no side effects."""
    if amount > 10000:
        return True
    
    recent_large = [t for t in user_history if t > 5000]
    if len(recent_large) > 3:
        return True
    
    return False
```

```python
# ✅ app/services/fraud_detection_service.py (Orchestration)
from app.core.fraud_detector import is_suspicious_transaction
from app.models import User, Transaction, FraudAlert

async def check_fraud(user_id: int, amount: float):
    """Orchestrate fraud check workflow."""
    # 1. Get data
    user = await User.get(user_id)
    history = await Transaction.get_recent(user_id, days=30)
    
    # 2. Apply domain logic (từ core)
    is_fraud = is_suspicious_transaction(amount, history)
    
    # 3. Side effects
    if is_fraud:
        await FraudAlert.create(user_id=user_id, amount=amount)
        await notify_admin(user_id, amount)  # External call
        logger.warning(f"Fraud detected: {user_id}")  # Logging
    
    return is_fraud
```

---

## 📂 MODELS PLACEMENT RULE

### ✅ **ĐÚNG: models trong app/**
```
app/
├── models/              ← Domain entities tập trung
│   ├── __init__.py
│   ├── user.py
│   ├── transaction.py
│   └── subscription.py
├── services/
├── core/
└── handlers/
```

**Lý do:**
- Domain logic tập trung trong `app/`
- Encapsulation tốt hơn
- Import path nhất quán: `from app.models import User`

### ❌ **SAI: models ở root level**
```
models/                  ← Tách rời khỏi domain
├── user.py
└── ...

app/
├── services/
├── core/
└── handlers/
```

---

## 📚 DOCS RULES

### **Folder Structure (Bắt buộc):**
```
docs/
├── README.md                # Navigation index
├── architecture/            # System design
│   ├── OVERVIEW.md
│   └── CLEAN_ARCHITECTURE.md
├── guides/                  # How-to guides
│   ├── GETTING_STARTED.md
│   └── DEPLOYMENT.md
├── flows/                   # Flow diagrams
│   └── USER_FLOWS.md
├── specifications/          # Specs & requirements
│   └── BOT_MASTER_PROMPT.md
└── archive/                 # Old planning docs
    └── (old files here)
```

### **🔒 STRICT RULES:**

1. **KHÔNG TẠO planning docs trong docs/**
   ```
   ❌ docs/SPRINT_WEEK_1.md
   ❌ docs/DAY1_SUMMARY.md
   ❌ docs/MVP_PLAN.md
   ❌ docs/PHASE6_COMPLETE.md
   ```

2. **Planning docs → Project management tool**
   - Jira / Linear / GitHub Projects
   - Notion / Confluence
   - KHÔNG trong Git repo

3. **Nếu cần temporary notes → `/docs/archive` ngay**
   ```bash
   # Wrong
   git add docs/TEMP_NOTES.md
   
   # Right
   mv docs/TEMP_NOTES.md docs/archive/
   # Hoặc không commit
   ```

4. **1 topic = 1 file duy nhất**
   ```
   ❌ USER_FLOWS_v1.md, USER_FLOWS_v2.md, USER_FLOWS_FINAL.md
   ✅ USER_FLOWS.md (Git tracks versions)
   ```

---

## 🚫 PR REJECTION CRITERIA

### **Reject ngay nếu:**

#### **1. Handler Violations:**
- [ ] Handler có business logic
- [ ] Handler có DB query trực tiếp
- [ ] Handler có external API call trực tiếp
- [ ] Hard-code keyboard trong handler

#### **2. Naming Violations:**
- [ ] File name có version: `*_v1.py`, `*_v2.py`, `*_final.py`
- [ ] File name có date: `*_2026.py`, `*_jan.py`
- [ ] Backup files: `*.backup`, `*.old`

#### **3. Structure Violations:**
- [ ] Thêm root folder mới (helpers/, common/, misc/)
- [ ] Code business logic nằm ngoài services/core
- [ ] Models ở root level thay vì app/models

#### **4. Docs Violations:**
- [ ] Planning docs trong docs/ (not in archive/)
- [ ] Multiple versions của same doc
- [ ] Temporary notes được commit

#### **5. Import Violations:**
- [ ] Handler import models trực tiếp
- [ ] Core import services
- [ ] Core import models
- [ ] Circular imports

---

## ✅ PR APPROVAL CHECKLIST

```markdown
### Architecture Review Checklist

- [ ] Handlers chỉ làm: input → service → output
- [ ] Business logic trong services hoặc core (not handlers)
- [ ] Pure domain logic trong core (no side effects)
- [ ] No versioned files (*_v1, *_v2, *_final)
- [ ] No new root folders
- [ ] Models trong app/models/
- [ ] Docs follow structure (no planning docs)
- [ ] Imports follow layering (Handler → Service → Core → Model)
- [ ] Tests included
- [ ] README updated (if needed)
```

---

## 🎓 TRAINING FOR NEW DEVELOPERS

### **Onboarding Process:**

#### **Day 1: Architecture Understanding (2 hours)**
1. Read [README.md](../README.md) (20 min)
2. Read [ARCHITECTURE_RULES.md](ARCHITECTURE_RULES.md) (this file) (30 min)
3. Review [docs/architecture/OVERVIEW.md](../docs/architecture/OVERVIEW.md) (40 min)
4. Watch architecture walkthrough video (30 min)

#### **Day 2: Code Examples (3 hours)**
1. Study good handler example: `app/handlers/user/registration.py`
2. Study service example: `app/services/payment_service.py`
3. Study core example: `app/core/fraud_detector.py`
4. Complete quiz (10 questions)

#### **Day 3: First PR (4 hours)**
1. Pick simple task (add new handler)
2. Follow checklist
3. Submit PR
4. Review feedback
5. Fix & merge

---

## 📊 METRICS TO TRACK

Monitor these to ensure architecture stays clean:

| Metric | Target | Red Flag |
|--------|--------|----------|
| **Handlers with business logic** | 0% | > 5% |
| **Files with versions (*_v2)** | 0 | > 0 |
| **Root folders** | ≤ 10 | > 12 |
| **Docs files in main folders** | ≤ 15 | > 30 |
| **Handler LOC** | < 50 lines | > 100 lines |
| **Service LOC** | < 150 lines | > 300 lines |
| **Core function LOC** | < 50 lines | > 100 lines |

**Monthly Review:**
- Count violations
- If > 3 violations → Mandatory team training

---

## 🔄 ARCHITECTURE EVOLUTION

### **Khi nào được thay đổi architecture?**

**KHÔNG được thay đổi tùy tiện.**

**Process để propose changes:**

1. **Tạo RFC (Request for Comments)**
   - File: `docs/architecture/RFC_001_my_proposal.md`
   - Nội dung: Problem, Proposed Solution, Pros/Cons, Impact

2. **Team Review** (2-3 days)
   - Mọi người comment
   - Senior architect review

3. **Decision**
   - Approved → Update ARCHITECTURE_RULES.md
   - Rejected → Document lý do trong RFC

4. **Implementation** (nếu approved)
   - Follow migration plan
   - Update docs
   - Update tests
   - Team training

**Example Valid Reasons:**
- Scale issues (performance bottleneck)
- Security concerns
- New major feature requires new pattern
- Industry best practice update

**Invalid Reasons:**
- "I prefer it this way"
- "It's easier for me"
- "Other projects do it"
- "I don't like current structure"

---

## 📞 Questions?

**Q: Tôi không chắc code mới nên đặt ở đâu?**  
A: Follow decision tree:
```
Is it business logic?
├─ Yes: Is it pure domain rules?
│  ├─ Yes → app/core/
│  └─ No (has side effects) → app/services/
└─ No: Is it handling Telegram input?
   ├─ Yes → app/handlers/
   └─ No → app/utils/
```

**Q: Tôi cần temporary file để test, có được commit không?**  
A: KHÔNG. Use `.gitignore` hoặc đặt trong `_archive/`

**Q: File hiện tại vi phạm rule, tôi phải làm gì?**  
A: Refactor trong PR riêng, không mix với feature development

**Q: Tôi thấy cách khác tốt hơn, có thể change không?**  
A: Tạo RFC, team review. KHÔNG tự ý thay đổi.

---

## 🛡️ ENFORCEMENT & OWNERSHIP

### **Architecture Owner**
```
Primary Owner:     [YOUR NAME/ROLE HERE]
Backup Owner:      [BACKUP NAME/ROLE]
Review Committee:  [Senior Engineers/Tech Leads]

Contact:           [email/slack channel]
```

**Responsibilities:**
- ✅ Approve/reject architecture changes (RFC process)
- ✅ Review PRs for architecture compliance
- ✅ Maintain & update ARCHITECTURE_RULES.md
- ✅ Train team on architecture principles
- ✅ Monitor metrics & violations
- ✅ Enforce 3 Laws strictly

**Decision Authority:**
- Only Architecture Owner can approve:
  - New root-level folders
  - Changes to layering rules
  - Exceptions to 3 Laws (document in RFC)
  - Major refactoring plans

### **Automated Enforcement**

#### **1. Pre-commit Hooks**
Installed locally, runs before commit:
```bash
# Install
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

**Checks:**
- ✅ Dependency direction (core cannot import services/models)
- ✅ No versioned files (*_v1, *_v2, *_final)
- ✅ No backup files (*.backup, *.old)
- ✅ No forbidden root folders
- ✅ No planning docs in main docs/

#### **2. CI/CD Pipeline**
Runs on every PR:
```yaml
# .github/workflows/architecture-check.yml
- Architecture Dependency Check
- Naming Convention Check
- Documentation Structure Check
```

**PR blocked if:**
- ❌ Dependency violations detected
- ❌ Versioned files found
- ❌ Backup files committed
- ❌ Forbidden folders added
- ❌ Planning docs in main docs/

#### **3. Manual Script**
Run anytime:
```bash
python scripts/check_dependencies.py
```

**Output:**
```
✅ No dependency violations found!
✅ Architecture rules enforced successfully.

# Or:
❌ Found 3 dependency violation(s):
1. ERROR: app/core/fraud.py:15
   Import: app.services.payment_service
   Reason: core/ CANNOT import from services/
```

---

**Last Updated:** 2026-02-12  
**Version:** 1.1 (Added Enforcement & Ownership)  
**Status:** 🟢 Active & Enforced  
**Owner:** [TO BE ASSIGNED]  
**Automated:** ✅ Yes (CI + pre-commit)

---

**📌 Remember:** 
- Architecture rules exist to prevent chaos in 6 months.
- Design ≠ Enforcement. Automation is mandatory.
- Better to argue now than to rewrite later.
