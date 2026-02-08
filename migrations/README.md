# Database Migrations

This directory contains database migration scripts for the Freedom Wallet Bot.

## Migration Strategy

**Foundation-First Approach (Week 1-3)**
- Week 1: Add state machine & program tracking columns
- Week 2: Soft-integrate state machine into handlers
- Week 3: Convert campaigns to programs

## How to Run Migrations

### Apply Migration
```bash
python migrations/001_add_state_program.py
```

### Revert Migration
```bash
python migrations/001_add_state_program.py downgrade
```

## Safety Guidelines

1. **Always backup database before migration**
   ```bash
   cp data/bot.db data/bot.db.backup
   ```

2. **Stop bot before running migration**
   - Check running processes
   - Kill bot gracefully
   - Wait for database locks to release

3. **Verify migration success**
   - Check column existence
   - Verify data backfill
   - Test bot restart

## Migration Log

| # | Date | Description | Status |
|---|------|-------------|--------|
| 001 | 2026-02-08 | Add state machine & program columns | Pending |

## Rollback Plan

If migration fails:
1. Stop migration script (Ctrl+C)
2. Restore backup: `cp data/bot.db.backup data/bot.db`
3. Review error logs
4. Fix script
5. Retry
