# 🗑️ DEAD CODE REMOVAL LIST
**Freedom Wallet Bot - System Cleanup**  
Generated: 2026-02-17

## FILES TO REMOVE

### Root Directory Test Files (Outdated/Duplicates)
```
✗ test_sheets_flow.py
✗ test_full_flow.py
✗ test_button_flow.py
```
**Reason:** Replaced by comprehensive pytest suite in `tests/` directory

### Archive Directory (Safe to Remove)
```
✗ _archive/clean_architecture_experiment/
✗ _archive/debug_scripts/
✗ _archive/old_docs/
✗ _archive/old_logs/
✗ _archive/migrations/
```
**Reason:** Experimental code, outdated migration scripts, replaced by new architecture

### Encoding Fix Scripts (One-Time Use)
```
✗ fix_encoding.py
✗ fix_encoding_safe.py
✗ fix_with_ftfy.py
```
**Reason:** One-time fix scripts, no longer needed

### Backup Scripts in Archive
```
✗ _archive/PUSH.bat
✗ _archive/push_to_github.ps1
✗ _archive/quick_push.ps1
✗ _archive/setup_github.ps1
✗ _archive/test_onboarding_buttons.ps1
```
**Reason:** Outdated deployment scripts, replaced by current workflow

## FILES TO KEEP (Do NOT Remove)

### Root Test Files (Active)
```
✓ tests/test_basic.py
✓ tests/test_bot.py
✓ tests/test_subscription_day1.py
✓ tests/unit/*
✓ tests/integration/*
✓ tests/e2e/*
```
**Reason:** Active test suite with pytest framework

### Core Application Files
```
✓ app/*
✓ config/*
✓ migrations/*
✓ scripts/*
✓ main.py
✓ RoadmapAutoInsert.gs (will be upgraded)
```

## ESTIMATED CLEANUP

- **Files to Remove:** ~15 files
- **Disk Space Freed:** ~2-5 MB
- **Reduced Confusion:** High (no more duplicate test files)
- **Risk Level:** Low (all targets are archived/duplicates)

## EXECUTION PLAN

1. ✅ Move files to `_to_delete/` folder first (safety)
2. ✅ Run full test suite to ensure nothing breaks
3. ✅ Delete after 1 week if no issues
4. ✅ Update .gitignore to prevent future clutter

## COMMANDS TO EXECUTE

```powershell
# Create safety folder
mkdir _to_delete

# Move root test files
mv test_sheets_flow.py _to_delete/
mv test_full_flow.py _to_delete/
mv test_button_flow.py _to_delete/

# Move encoding scripts
mv fix_encoding.py _to_delete/
mv fix_encoding_safe.py _to_delete/
mv fix_with_ftfy.py _to_delete/

# Archive is already in _archive/, safe to remove later

# Run tests to verify
pytest tests/ -v
```

---

**Next Steps After Cleanup:**
1. ✅ Unified test suite in `tests/` directory
2. ✅ Clean codebase structure
3. ✅ Focus on active development files only
