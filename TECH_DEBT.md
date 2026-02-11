# Technical Debt - Architecture Violations

**Status**: ✅ **RESOLVED**  
**Priority**: ~~Medium (Fix in Phase 3)~~ **COMPLETED**  
**Created**: 2026  
**Resolved**: 2026-02-12  
**Owner**: @architecture-team

## Resolution Summary

**Phase 3 completed successfully!** All 7 architecture violations have been eliminated.

### What Changed:
1. ✅ Created `app/messages/` package for all message templates
2. ✅ Extracted message constants from handlers to messages
3. ✅ Moved business logic from handlers to services  
4. ✅ Updated all imports to respect layering rules
5. ✅ Dependency checker: **7 violations → 0 violations**

### Files Created:
- [app/messages/reminder_messages.py](app/messages/reminder_messages.py) (103 lines)
- [app/messages/nurture_messages.py](app/messages/nurture_messages.py) (58 lines)
- [app/messages/onboarding_messages.py](app/messages/onboarding_messages.py) (518 lines)
- [app/services/streak_service.py](app/services/streak_service.py) (50 lines)

### Files Modified:
- [app/services/messaging_service.py](app/services/messaging_service.py) - Updated imports
- [app/services/program_manager.py](app/services/program_manager.py) - Simplified logic, updated imports
- [app/services/reminder_scheduler.py](app/services/reminder_scheduler.py) - Updated imports

## Overview

During the Phase 2 refactoring (bot/ → app/), several architectural violations were identified in legacy scheduler and program management code. These violations are documented here as intentional tech debt to be addressed in Phase 3.

## Violations

### 1. Services importing from Handlers (7 violations)

**Problem**: The strict layering rule is: `handlers → services → core/models`  
Several service files import from handlers, creating circular dependency risks.

**Root Cause**:  
- Original "handlers" folder contained mixed concerns
- Some files are actually message templates/senders, not request handlers  
- Schedulers need to send proactive messages (not responses to user input)

**Affected Files**:

| File | Line | Import | Reason|
|------|------|--------|-------|
| app/services/messaging_service.py | 19 | app.handlers.engagement.daily_reminder | Imports message template constants |
| app/services/messaging_service.py | 62 | app.handlers.engagement.daily_reminder | Imports message template constants |
| app/services/program_manager.py | 263 | app.handlers.engagement.daily_nurture | Imports send function & constants |
| app/services/program_manager.py | 283 | app.handlers.engagement.daily_nurture | Imports message constants |
| app/services/program_manager.py | 267 | app.handlers.user.onboarding | Imports send function & constants |
| app/services/program_manager.py | 287 | app.handlers.user.onboarding | Imports message constants |
| app/services/reminder_scheduler.py | 15 | app.handlers.engagement.streak_tracking | Imports check_missed_days function |

**Mitigation**:  
- All violations are marked with `# NOTE: Tech Debt` and `# TODO` comments
- No NEW code should introduce similar violations
- CI/CD will warn (not fail) on these specific violations

## Remediation Plan (Phase 3)

### Step 1: Extract Message Constants
Move all message template constants out of handlers:
```
handlers/engagement/daily_reminder.py → messages/reminder_messages.py
handlers/engagement/daily_nurture.py → messages/nurture_messages.py  
handlers/user/onboarding.py → messages/onboarding_messages.py
```

### Step 2: Extract Messaging Logic
Move all proactive messaging functions to services:
```  
send_nurture_message → services/messaging_service.py
send_onboarding_message → services/messaging_service.py
check_missed_days → services/streak_service.py
```

### Step 3: Refactor Handlers
Keep only handler-specific logic (parse input, format response):
```python
# Good: Thin handler
async def handle_start(update, context):
    user_input = update.message.text  # Parse input
    result = await user_service.handle_start(user_input)  # Call service
    await update.message.reply_text(result)  # Format response
```

### Step 4: Clean Import Graph
Final structure should be:
```
handlers/ → services/   (✅ allowed)
services/ → core/       (✅ allowed)
services/ → models/     (✅ allowed)
services/ → messages/   (✅ allowed)
handlers/ ↛ models/     (❌ never)
services/ ↛ handlers/   (❌ never)
core/ ↛ anything        (❌ never - pure logic only)
```

## Acceptance Criteria

- [x] All 7 violations resolved ✅
- [x] `python scripts/check_dependencies.py` returns 0 errors ✅
- [x] No new violations introduced ✅
- [x] All tests pass ✅  
- [x] Documentation updated ✅

## Timeline

- **Phase 2** (✅ Complete): Document violations, continue refactoring
- **Phase 3** (✅ Complete): Fix violations using remediation plan
- **Completed**: 2026-02-12

## References

- [ARCHITECTURE_RULES.md](ARCHITECTURE_RULES.md) - Architecture laws
- [STRUCTURE_V2_IMPROVED.md](docs/STRUCTURE_V2_IMPROVED.md) - Target structure
- GitHub Issue: #TODO - Create issue for Phase 3

## Notes

**Why not fix now?**  
- Phase 2 scope is large (38 handlers reorganized, bot→app rename)
- Fixing messaging architecture requires careful refactoring of 3+ files
- Better to complete structural changes first, then polish layering
- Current violations are contained and well-documented

**Risk Level**: Low  
- Violations do not cause runtime bugs (Python's dynamic imports handle this)
- Clear HACK comments prevent accidental proliferation  
- No performance impact
- Tech debt is transparent and measurable
