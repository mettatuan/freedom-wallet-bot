# 🚀 QUICK SETUP - AUTOMATION & ENFORCEMENT

> **Time:** 5 minutes  
> **Before starting Phase 2**

---

## ✅ STEP 1: Assign Architecture Owner (2 minutes)

Edit [ARCHITECTURE_RULES.md](ARCHITECTURE_RULES.md):

```diff
### Architecture Owner
- Primary Owner:     [YOUR NAME/ROLE HERE]
- Backup Owner:      [BACKUP NAME/ROLE]
+ Primary Owner:     John Doe (Senior Engineer)
+ Backup Owner:      Jane Smith (Tech Lead)
```

Replace with actual team member names.

---

## ✅ STEP 2: Install Pre-commit Hooks (2 minutes)

```bash
# Navigate to project
cd D:\Projects\FreedomWalletBot

# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Test (should show violations - expected)
pre-commit run --all-files
```

**Expected output:**
```
Check Architecture Dependencies............................Failed
- hook id: check-architecture-dependencies
- exit code: 1

❌ Found 6 dependency violation(s):
... (violations shown)
```

**✅ This is CORRECT!** Violations will be fixed in Phase 2.

---

## ✅ STEP 3: Test Dependency Checker (1 minute)

```bash
# Run manual check
python scripts/check_dependencies.py
```

**Should detect 6 violations** in current code.

---

## ✅ STEP 4: Verify CI/CD (Optional)

Push to branch and create test PR:

```bash
# Create test branch
git checkout -b test/automation-check

# Make a small change
echo "# Test" >> TEST.md
git add TEST.md
git commit -m "test: verify automation"

# Push
git push origin test/automation-check
```

Create PR on GitHub → Check "Architecture Dependency Check" action runs.

---

## 🎯 READY CHECKLIST

After completing steps above:

- [ ] Architecture Owner assigned in ARCHITECTURE_RULES.md
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Dependency checker tested (found 6 violations ✅)
- [ ] CI/CD workflow verified (optional)

---

## 🚀 START PHASE 2

```bash
# Create refactoring branch
git checkout -b feat/architecture-refactoring-v2

# Create safety tag
git tag before-refactoring-v2

# Start restructuring!
# Follow STRUCTURE_V2_IMPROVED.md
```

---

## 📞 Troubleshooting

**Q: Pre-commit hook fails on commit?**  
A: Expected! Violations will be fixed in Phase 2. You can bypass temporarily:
```bash
git commit --no-verify -m "wip: refactoring"
```

**Q: Python script not found?**  
A: Ensure you're in project root: `D:\Projects\FreedomWalletBot`

**Q: Dependency checker finds 0 violations after refactor?**  
A: Perfect! ✅ Architecture is clean.

---

**⏱️ Total Time:** 5 minutes  
**Status:** Ready to proceed 🚀
