# Week 3 Implementation Summary: Program Manager Integration

**Date:** 2026-02-08  
**Status:** ✅ COMPLETED  
**Strategy:** Convert existing campaigns to programs with enrollment tracking

---

## 🎯 WHAT WAS DONE

### 1. Created Program Manager Core
**File:** [bot/core/program_manager.py](../bot/core/program_manager.py) (368 lines)

**Key Components:**

#### `ProgramType` Enum
```python
NURTURE_7_DAY       # For REGISTERED users (0-1 refs)
ONBOARDING_7_DAY    # For new VIP users
ADVANCED_WORKSHOP   # Future: Week 3-4
MENTOR_PROGRAM      # Future: Week 4+
REACTIVATION        # Future: For churned users
```

#### `ProgramManager` Class
**Main Methods:**
- `enroll_user()` - Enroll user in program with conflict handling
- `advance_program_day()` - Move to next day, auto-complete when done
- `complete_program()` - Mark program as finished (doesn't change user_state)
- `cancel_program()` - Remove from program and cancel scheduled jobs
- `get_user_program_status()` - Check enrollment, day, progress

**Scheduling:**
- `_schedule_program_day()` - Schedule specific day message
- `_send_program_message()` - Callback to send message (delegates to handlers)
- `_get_program_config()` - Import message content from handlers
- `_get_program_max_days()` - Get total days for program

**Key Design Decisions:**

1. **Content stays in handlers** - ProgramManager doesn't duplicate message content, it imports from daily_nurture.py and onboarding.py
2. **Program ≠ State** - Completing a program doesn't change user_state (states change from actions like referrals)
3. **force parameter** - Allows priority programs (VIP onboarding) to override nurture
4. **Context manager pattern** - Auto-closes database session

---

### 2. Converted Daily Nurture to NURTURE_7_DAY
**File:** [bot/handlers/daily_nurture.py](../bot/handlers/daily_nurture.py)

**Changes Made:**

#### Import ProgramManager (Line 11)
```python
from bot.core.program_manager import ProgramManager, ProgramType
```

#### Refactored `start_daily_nurture()` (Lines 82-110)
**Before:** Scheduled all 5 days directly using job_queue  
**After:** Enrolls user via ProgramManager with fallback

```python
async def start_daily_nurture(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    # Week 3: Use ProgramManager
    with ProgramManager() as pm:
        success = await pm.enroll_user(
            user_id, 
            ProgramType.NURTURE_7_DAY, 
            context,
            force=False  # Don't override existing programs
        )
```

**Fallback Safety:** If ProgramManager fails, calls `_start_daily_nurture_legacy()`

#### Created `_start_daily_nurture_legacy()` (Lines 112-132)
- Renamed old `start_daily_nurture()` logic
- Kept for backward compatibility
- Schedules all 5 days at once (old behavior)

#### Kept Unchanged:
- ✅ `NURTURE_MESSAGES` dictionary (content)
- ✅ `send_nurture_message()` function (message sender)
- ✅ `cancel_remaining_nurture()` function
- ✅ Button handlers (share_link, check_progress)

**Message Content:** 
- 5 days of encouragement for 0-1 ref users
- Day 1: Why manage finances?
- Day 2: Cost of not managing money
- Day 3: 6 Jars & 5 Financial Levels
- Day 4: Why we give gifts
- Day 5: Reminder + urgency

---

### 3. Converted Onboarding to ONBOARDING_7_DAY
**File:** [bot/handlers/onboarding.py](../bot/handlers/onboarding.py)

**Changes Made:**

#### Import ProgramManager (Line 11)
```python
from bot.core.program_manager import ProgramManager, ProgramType
```

#### Refactored `start_onboarding_journey()` (Lines 470-510)
**Before:** Scheduled all 7 days directly using job_queue  
**After:** Enrolls user via ProgramManager with priority override

```python
async def start_onboarding_journey(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    # Week 3: Use ProgramManager
    with ProgramManager() as pm:
        success = await pm.enroll_user(
            user_id, 
            ProgramType.ONBOARDING_7_DAY, 
            context,
            force=True  # Override nurture if exists (VIP takes priority)
        )
```

**Key Difference from Nurture:** `force=True` - VIP onboarding overrides nurture campaign

#### Created `_start_onboarding_journey_legacy()` (Lines 512-540)
- Renamed old logic
- Kept for backward compatibility
- Schedules all 7 days at once (old behavior)

#### Kept Unchanged:
- ✅ `ONBOARDING_MESSAGES` dictionary (7 days content)
- ✅ `send_onboarding_message()` function (message sender)
- ✅ `handle_onboarding_response()` function (DONE, ACCEPT handlers)

**Message Content:**
- 7 days of VIP onboarding
- Day 1: Welcome & Setup
- Day 2: 6 Jars explanation
- Day 3: 5 Financial Levels quiz
- Day 4: Add first transaction
- Day 5: Advanced features
- Day 6-7: Investment strategies

---

## 🔧 HOW IT WORKS

### Program Enrollment Flow

```
User triggers enrollment (e.g., registration, VIP unlock)
    ↓
Handler calls start_daily_nurture() or start_onboarding_journey()
    ↓
ProgramManager.enroll_user() checks eligibility
    ↓
Set user.current_program = "NURTURE_7_DAY"
Set user.program_day = 0
Set user.program_started_at = now()
    ↓
ProgramManager._schedule_program_day(user_id, program, day=1)
    ↓
Get delay_hours from NURTURE_MESSAGES[1]
Schedule job_queue.run_once() → _send_program_message()
    ↓
When time arrives: _send_program_message() calls send_nurture_message()
    ↓
send_nurture_message() sends actual Telegram message
```

### Day Progression (Future)

```
User completes day 1 action
    ↓
Handler calls pm.advance_program_day(user_id)
    ↓
user.program_day = 1 → 2
    ↓
Schedule day 2 message
    ↓
Repeat until day 7
    ↓
pm.complete_program(user_id)
    ↓
user.current_program = None
user.program_completed_at = now()
```

---

## 🧪 TESTING RESULTS

### Test 1: ProgramManager Import
```bash
$ python -c "from bot.core.program_manager import ProgramManager, ProgramType; ..."
ProgramManager imported successfully
Available programs: ['NURTURE_7_DAY', 'ONBOARDING_7_DAY', 'ADVANCED_WORKSHOP', 'MENTOR_PROGRAM', 'REACTIVATION']
```
✅ **Result:** All program types available

### Test 2: Handler Integration
```bash
$ python -c "from bot.handlers.daily_nurture import start_daily_nurture, NURTURE_MESSAGES; ..."
Daily nurture: 5 days
Onboarding: 7 days
All handlers imported successfully!
```
✅ **Result:** Handlers integrate with ProgramManager, message content preserved

### Test 3: Database State
```bash
$ python -c "from bot.utils.database import SessionLocal, User; ..."
1299465308 | VIP | None | day=0
6588506476 | REGISTERED | None | day=0
```
✅ **Result:** Database columns exist, no programs enrolled yet (expected - enrollment happens at runtime)

### Test 4: No Syntax Errors
```bash
get_errors on 3 files
```
✅ **Result:** 0 errors in program_manager.py, daily_nurture.py, onboarding.py

---

## 🔐 SAFETY MECHANISMS

### 1. Dual-Run Strategy
```python
try:
    # Try new ProgramManager
    with ProgramManager() as pm:
        success = await pm.enroll_user(...)
except Exception as e:
    # Fallback to legacy method
    await _start_daily_nurture_legacy(...)
```

### 2. Conflict Handling
```python
# Check if already enrolled
if user.current_program and not force:
    logger.info("Already in program, skipping")
    return False

# Override if force=True (VIP priority)
if user.current_program and force:
    await self._cancel_program(user_id, context)
```

### 3. Job Cleanup
```python
# Remove scheduled jobs when canceling program
job_prefix = f"program_{user_id}_"
current_jobs = context.job_queue.get_jobs_by_name(job_prefix)
for job in current_jobs:
    job.schedule_removal()
```

### 4. Content Preservation
- Message content still in handler files (NURTURE_MESSAGES, ONBOARDING_MESSAGES)
- ProgramManager imports content dynamically
- No duplication = single source of truth

---

## 📊 ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────┐
│                    USER ACTIONS                          │
│  (Registration, VIP unlock, Daily interaction)          │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 HANDLER LAYER                            │
│  • start.py, registration.py                            │
│  • Calls: start_daily_nurture(user_id, context)        │
│  • Calls: start_onboarding_journey(user_id, context)   │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              PROGRAM MANAGER                             │
│  • enroll_user(user_id, NURTURE_7_DAY, context)        │
│  • Update DB: current_program, program_day              │
│  • Schedule: _schedule_program_day(user_id, program, 1)│
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              JOB QUEUE (APScheduler)                     │
│  • run_once(_send_program_message, delay_hours)        │
│  • Job name: "program_{user_id}_NURTURE_7_DAY_day_1"   │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│         MESSAGE SENDER (Handler Callback)                │
│  • daily_nurture.send_nurture_message(context)         │
│  • onboarding.send_onboarding_message(context)         │
│  • Sends actual Telegram message with content           │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 KEY LEARNINGS

### What Worked Well:
1. **Separation of concerns** - ProgramManager handles enrollment, handlers handle content
2. **Fallback strategy** - Legacy methods prevent breaking changes
3. **force parameter** - Allows priority override (ONBOARDING > NURTURE)
4. **Context manager** - Clean session management

### Design Decisions:
1. **Why not move content to ProgramManager?**
   - Content belongs with handlers (single responsibility)
   - Easier to edit messages in handler files
   - ProgramManager just coordinates, doesn't own content

2. **Why separate functions (_legacy)?**
   - Clear migration path
   - Easy to remove after stable
   - Debugging easier

3. **Why force=True for onboarding?**
   - VIP users should get VIP content immediately
   - Nurture is for non-VIP, redundant after unlock
   - Clear priority: ONBOARDING > NURTURE

### Gotchas Avoided:
- ❌ Don't duplicate message content in multiple places
- ❌ Don't tightly couple ProgramManager to specific messages
- ❌ Don't forget to cancel jobs when changing programs
- ❌ Don't change user_state in complete_program() (state ≠ program)

---

## 🚀 WHAT'S NEXT

### Week 3 COMPLETED ✅
- ✅ Database migration (state/program columns)
- ✅ State machine core (VISITOR → VIP)
- ✅ Program manager (enrollment/progression)
- ✅ Nurture campaign conversion
- ✅ Onboarding campaign conversion

### Week 4-5: Add Features
1. **Super VIP Tier** (50+ refs)
   - New state: SUPER_VIP
   - Badge display
   - Leaderboard entry

2. **Fraud Detection** (Use referrals table fraud columns)
   - IP tracking
   - Velocity check
   - Manual review queue

3. **Decay Monitoring** (Use super_vip columns)
   - Day 10: Warning message
   - Day 14: Hide from leaderboard
   - Reactivation flow

4. **Progressive Disclosure** (State-based UI)
   - Show features based on user_state
   - REGISTERED: Basic menu
   - VIP: Full menu + gifts
   - SUPER_VIP: Leaderboard + bonus

---

## 📚 REFERENCES

- [Database Schema](DATABASE_SCHEMA.md)
- [Week 1 Migration](../migrations/001_add_state_program.py)
- [Week 2 State Machine](WEEK_2_STATE_MACHINE.md)
- [Program Manager Code](../bot/core/program_manager.py)
- [Daily Nurture Handler](../bot/handlers/daily_nurture.py)
- [Onboarding Handler](../bot/handlers/onboarding.py)
- [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md)
