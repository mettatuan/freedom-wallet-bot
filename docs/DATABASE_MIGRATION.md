# ============================================
# DATABASE MIGRATION: SQLite -> PostgreSQL
# ============================================
# Migration plan for moving from SQLite to PostgreSQL
# Author: DevOps Engineer
# Date: 2026-02-19
# ============================================

## OVERVIEW

Moving from SQLite (development) to PostgreSQL (production) without data loss.

## PREREQUISITES

1. **PostgreSQL Installation** (Windows Server 2016)
   - Download: PostgreSQL 15.x or 16.x (Latest stable)
   - URL: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
   - Install path: C:\Program Files\PostgreSQL\15\

2. **Required Python packages**
   ```
   psycopg2-binary==2.9.9  (already in requirements.txt)
   ```

## MIGRATION STEPS

### STEP 1: Install PostgreSQL on VPS

1. Download PostgreSQL installer for Windows x64
2. Run installer:
   - Port: **5432** (default)
   - Password: **Choose a strong password** (save it!)
   - Locale: English, United States
   - Components: PostgreSQL Server, pgAdmin 4, Command Line Tools

3. Add to Windows PATH (if not auto-added):
   ```
   C:\Program Files\PostgreSQL\15\bin
   ```

4. Test installation:
   ```powershell
   psql --version
   ```

### STEP 2: Create Production Database

Run in PowerShell (on VPS):

```powershell
# Connect to PostgreSQL as superuser
psql -U postgres

# Create database and user
CREATE DATABASE freedomwalletdb;
CREATE USER freedomwallet WITH PASSWORD 'your-strong-password-here';
GRANT ALL PRIVILEGES ON DATABASE freedomwalletdb TO freedomwallet;

# Exit
\q
```

### STEP 3: Export Data from SQLite (Local)

Run on your local machine:

```bash
# Run the export script
python scripts/migrate_db.py export --output=data/db_export.json
```

This will create a JSON export of all tables.

### STEP 4: Update Database URL

On VPS, edit `.env`:

```
DATABASE_URL=postgresql://freedomwallet:your-strong-password@localhost:5432/freedomwalletdb
```

### STEP 5: Import Data to PostgreSQL (VPS)

Transfer `db_export.json` to VPS, then run:

```bash
python scripts/migrate_db.py import --input=data/db_export.json
```

### STEP 6: Verify Migration

```bash
python scripts/migrate_db.py verify
```

This checks:
- All tables exist
- Row counts match
- Critical data integrity

## ROLLBACK PLAN

If migration fails:

1. Keep original SQLite file as backup
2. Restore `.env` to use SQLite:
   ```
   DATABASE_URL=sqlite:///data/bot.db
   ```
3. Restart bot

## POSTGRESQL OPTIMIZATION (Production)

After successful migration, run:

```sql
-- Connect to database
psql -U freedomwallet -d freedomwalletdb

-- Create indexes for performance
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_sheets_user_id ON user_sheets(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

-- Enable query logging (optional, for debugging)
ALTER DATABASE freedomwalletdb SET log_statement = 'all';
```

## BACKUP STRATEGY

PostgreSQL supports better backup than SQLite:

1. **Automated Daily Backup** (see backup_database.ps1)
2. **Point-in-Time Recovery** (WAL archiving - advanced)
3. **Hot Backup** (no downtime needed)

## MONITORING

After migration, monitor:

```powershell
# Check PostgreSQL status
Get-Service postgresql*

# Check database size
psql -U freedomwallet -d freedomwalletdb -c "SELECT pg_size_pretty(pg_database_size('freedomwalletdb'));"

# Check active connections
psql -U freedomwallet -d freedomwalletdb -c "SELECT count(*) FROM pg_stat_activity;"
```

## TROUBLESHOOTING

**Issue**: "could not connect to server"
**Solution**: Check if PostgreSQL service is running:
```powershell
Get-Service postgresql*
Start-Service postgresql-x64-15  # Adjust version
```

**Issue**: "password authentication failed"
**Solution**: Reset password:
```powershell
psql -U postgres
ALTER USER freedomwallet WITH PASSWORD 'new-password';
```

**Issue**: "relation does not exist"
**Solution**: Run migrations:
```bash
alembic upgrade head
```

## PERFORMANCE COMPARISON

SQLite vs PostgreSQL:

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Concurrent writes | ❌ Locks entire DB | ✅ Row-level locks |
| Max DB size | ~140TB (impractical) | Unlimited |
| Transactions | Limited | Full ACID |
| Production-ready | ❌ No | ✅ Yes |
| Backup | Manual file copy | Hot backup, PITR |
| Crash recovery | ❌ Risk of corruption | ✅ WAL recovery |

## TIMELINE

- Install PostgreSQL: **15 minutes**
- Create database: **5 minutes**
- Export SQLite data: **2 minutes**
- Import to PostgreSQL: **5 minutes**
- Verify migration: **3 minutes**

**Total**: ~30 minutes

## COMPLETION CHECKLIST

- [ ] PostgreSQL installed on VPS
- [ ] Database `freedomwalletdb` created
- [ ] User `freedomwallet` created with password
- [ ] Data exported from SQLite
- [ ] Data imported to PostgreSQL
- [ ] Migration verified (row counts match)
- [ ] `.env` updated with PostgreSQL URL
- [ ] Bot tested on production DB
- [ ] Backup script configured
- [ ] Old SQLite file backed up

---

**Next**: Run `scripts/migrate_db.py` to execute migration
