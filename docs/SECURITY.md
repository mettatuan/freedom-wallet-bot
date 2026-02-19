# 🔒 SECURITY PROTOCOL

## 🎯 SECURITY PRINCIPLES

1. **Zero Trust** - Never commit secrets to Git
2. **Least Privilege** - Minimal permissions for each component
3. **Defense in Depth** - Multiple security layers
4. **Monitoring** - Detect and respond to security events

---

## 🔐 SECRETS MANAGEMENT

### ❌ NEVER COMMIT THESE FILES

**Critical files (already in `.gitignore`):**
- `.env`
- `.env.local`
- `.env.production`
- `google_service_account.json`
- Any file containing passwords, tokens, or API keys

**Verify before commit:**
```powershell
# Check what will be committed
git status

# Verify .gitignore is working
git check-ignore .env
# Should output: .env

# If .env is tracked (BAD!), remove it:
git rm --cached .env
git commit -m "Remove .env from tracking"
```

---

### ✅ SAFE SECRET STORAGE

#### Production (.env file on VPS)

**Location:** `D:\FreedomWalletBot\.env`

**Permissions:**
- Only accessible by Administrator and SYSTEM
- Not readable by other users

**Set permissions:**
```powershell
# Remove inheritance
$Acl = Get-Acl ".env"
$Acl.SetAccessRuleProtection($true, $false)

# Grant access only to Administrators and SYSTEM
$Acl.Access | ForEach-Object { $Acl.RemoveAccessRule($_) }

$AdminRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Administrators", "FullControl", "Allow")
$SystemRule = New-Object System.Security.AccessControl.FileSystemAccessRule("SYSTEM", "FullControl", "Allow")

$Acl.AddAccessRule($AdminRule)
$Acl.AddAccessRule($SystemRule)

Set-Acl ".env" $Acl
```

---

### 🔑 CREDENTIALS CHECKLIST

**Required in `.env`:**

| Variable | Type | Example | Security Level |
|----------|------|---------|----------------|
| `TELEGRAM_BOT_TOKEN` | Secret | `1234567890:ABCdef...` | **CRITICAL** |
| `DATABASE_URL` | Secret | `postgresql://user:pass@...` | **CRITICAL** |
| `OPENAI_API_KEY` | Secret | `sk-...` | **HIGH** |
| `ADMIN_USER_ID` | Sensitive | `123456789` | **MEDIUM** |
| `GOOGLE_SHEETS_CREDENTIALS` | Secret (file path) | Path to JSON file | **HIGH** |

**Password strength requirements:**
- Database password: **Minimum 16 characters**, mixed case, numbers, symbols
- Use password generator: `[System.Web.Security.Membership]::GeneratePassword(20,5)`

---

## 🛡️ WINDOWS SERVER SECURITY

### Firewall Rules

**Inbound (Block all except):**
- RDP (Port 3389) - Admin IP only
- PostgreSQL (Port 5432) - Localhost only

**Outbound (Allow):**
- HTTPS (Port 443) - Telegram API
- PostgreSQL (internal)

**Configure:**
```powershell
# Block PostgreSQL from external access
New-NetFirewallRule -DisplayName "PostgreSQL (Block External)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5432 `
    -Action Block `
    -RemoteAddress Any

# Allow localhost only
New-NetFirewallRule -DisplayName "PostgreSQL (Allow Localhost)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5432 `
    -Action Allow `
    -RemoteAddress 127.0.0.1

# Allow bot outbound HTTPS
New-NetFirewallRule -DisplayName "Bot Outbound HTTPS" `
    -Direction Outbound `
    -Protocol TCP `
    -RemotePort 443 `
    -Action Allow `
    -Program "D:\FreedomWalletBot\.venv\Scripts\python.exe"
```

---

### Windows Updates

**Strategy:** Manual updates (not automatic)

**Monthly schedule:**
```powershell
# Check for updates
Get-WindowsUpdate

# Install critical updates only
Install-WindowsUpdate -KBArticleID "KB1234567" -AcceptAll
```

**Before updating:**
1. ✅ Backup database
2. ✅ Test in development
3. ✅ Schedule maintenance window
4. ✅ Monitor after update

---

## 🗄️ DATABASE SECURITY

### PostgreSQL Hardening

#### 1. Strong Passwords
```sql
-- Change default postgres password
ALTER USER postgres WITH PASSWORD 'very-strong-password-here';

-- Use strong password for app user
ALTER USER freedomwallet WITH PASSWORD 'another-strong-password';
```

#### 2. Restrict Access

**Edit:** `C:\Program Files\PostgreSQL\15\data\pg_hba.conf`

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections only
local   all             all                                     scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

# Deny all external connections
host    all             all             0.0.0.0/0               reject
```

**Reload:**
```powershell
Restart-Service postgresql-x64-15
```

#### 3. Encryption at Rest (Optional)

Use Windows BitLocker for `D:\` drive encryption.

#### 4. Connection Encryption

**Edit:** `C:\Program Files\PostgreSQL\15\data\postgresql.conf`

```conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

---

## 🔍 MONITORING & AUDITING

### Log Security Events

**Bot logs:** `data\logs\bot.log`

**Monitor for:**
- Failed authentication attempts
- Unauthorized access attempts
- Database errors
- API rate limiting

**Automated monitoring:**
```powershell
# Add to health_check.ps1
$SuspiciousPatterns = @(
    "unauthorized",
    "forbidden",
    "authentication failed",
    "rate limit"
)

foreach ($pattern in $SuspiciousPatterns) {
    $Matches = Select-String -Path "data\logs\bot.log" -Pattern $pattern -CaseSensitive
    if ($Matches) {
        Write-Host "⚠️ Security alert: $pattern detected"
        # Send alert here
    }
}
```

---

### Database Audit Log

**Enable PostgreSQL logging:**

```conf
# In postgresql.conf
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_statement = 'ddl'  # Log schema changes
log_connections = on
log_disconnections = on
log_duration = on
```

---

## 🚨 INCIDENT RESPONSE

### Security Breach Checklist

**If token/credentials compromised:**

1. **Immediate Actions (within 5 minutes):**
   ```powershell
   # Stop bot
   Stop-Service FreedomWalletBot
   
   # Disconnect from network (if severe)
   Disable-NetAdapter -Name "Ethernet"
   ```

2. **Revoke Credentials:**
   - Telegram: Talk to @BotFather, use `/revoke`
   - OpenAI: Revoke API key at platform.openai.com
   - Database: Change passwords

3. **Assess Damage:**
   ```powershell
   # Check database for unauthorized changes
   psql -U freedomwallet -d freedomwalletdb
   SELECT * FROM users ORDER BY created_at DESC LIMIT 100;
   
   # Check logs for suspicious activity
   Select-String -Path "data\logs\bot.log" -Pattern "ERROR|CRITICAL"
   ```

4. **Restore from Backup (if needed):**
   ```powershell
   # Restore database
   psql -U freedomwallet -d freedomwalletdb -f "backups\database\latest.sql"
   ```

5. **Update Credentials:**
   - Generate new bot token
   - Update `.env`
   - Change all passwords

6. **Resume Operations:**
   ```powershell
   Start-Service FreedomWalletBot
   ```

---

## 🔒 ACCESS CONTROL

### VPS Access

**RDP Access:**
- ✅ Use strong password (20+ characters)
- ✅ Enable Network Level Authentication (NLA)
- ✅ Restrict to specific IP addresses
- ✅ Use VPN when possible
- ❌ Never allow RDP from public internet

**Configure:**
```powershell
# Restrict RDP to specific IP
New-NetFirewallRule -DisplayName "RDP (Restricted)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 3389 `
    -Action Allow `
    -RemoteAddress "YOUR_IP_ADDRESS"
```

### User Accounts

**Principle:** One admin account, one service account

```powershell
# Create limited service account (optional)
New-LocalUser -Name "BotService" -Password (ConvertTo-SecureString "StrongPassword123!" -AsPlainText -Force) -FullName "Bot Service Account" -Description "Service account for FreedomWalletBot"

# Deny login rights
# In Local Security Policy: Deny log on locally
```

---

## 📱 TELEGRAM BOT SECURITY

### Bot Settings

**Configure with @BotFather:**

1. Enable privacy mode: `/setprivacy` → `ENABLED`
   - Bot only receives messages addressed to it
   
2. Set bot commands: `/setcommands`
   - Controls what users can execute

3. Set bot description: `/setdescription`
   - Clear purpose statement

### Rate Limiting

**In `.env`:**
```env
MAX_MESSAGES_PER_MINUTE=10
MAX_SUPPORT_TICKETS_PER_DAY=3
```

**Enforce in code:**
```python
from telegram.ext import MessageHandler, filters
from app.middleware.rate_limiter import RateLimiter

# In main.py
rate_limiter = RateLimiter(max_per_minute=10)
application.add_handler(MessageHandler(filters.ALL, rate_limiter.check), group=-1)
```

### Input Validation

**Always validate:**
- User input (no SQL injection)
- File uploads (if any)
- Callback data
- Deep links

---

## 🔐 DATA PROTECTION (GDPR/Privacy)

### User Data Handling

**Principles:**
1. **Minimize data collection** - Only collect what's necessary
2. **Encrypt sensitive data** - Use database encryption
3. **Regular cleanup** - Delete old/inactive users
4. **Backup protection** - Encrypt backups

### GDPR Compliance

**User rights:**
- Right to access data: `/mydata` command
- Right to deletion: `/deletemydata` command
- Right to export: Export user data to JSON

**Implementation:**
```python
# In user_commands.py
@handler("/mydata")
async def my_data(update, context):
    # Export user's data
    pass

@handler("/deletemydata")
async def delete_my_data(update, context):
    # Delete user's data (anonymize)
    pass
```

---

## 🛡️ BACKUP SECURITY

### Encryption

**Encrypt backups (optional but recommended):**

```powershell
# Using 7-Zip with password
$BackupFile = "backups\database\freedomwallet_20260219.sql"
$Password = "your-secure-backup-password"

& "C:\Program Files\7-Zip\7z.exe" a -tzip -pYOUR_PASSWORD "$BackupFile.zip" $BackupFile
Remove-Item $BackupFile  # Delete unencrypted version
```

### Offsite Backup (Recommended)

**Options:**
1. **Cloud storage** (encrypted)
   - OneDrive, Google Drive, Dropbox
   - Encrypt before upload

2. **SFTP/SCP** to another server
   ```powershell
   # Using WinSCP or similar
   ```

3. **External hard drive** (disconnected when not backing up)

---

## 📋 SECURITY CHECKLIST

### Initial Setup
- [ ] `.env` file has correct permissions (Admin only)
- [ ] `.gitignore` includes all secret files
- [ ] Strong passwords for all accounts (16+ chars)
- [ ] PostgreSQL only accepts localhost connections
- [ ] Windows Firewall configured correctly
- [ ] RDP restricted to specific IP
- [ ] Windows updates applied
- [ ] Antivirus enabled and updated

### Monthly Review
- [ ] Review access logs
- [ ] Check for failed login attempts
- [ ] Verify firewall rules
- [ ] Update dependencies: `pip list --outdated`
- [ ] Test backup restoration
- [ ] Review user data (GDPR compliance)

### Emergency Contacts
- Telegram: @YourAdminUsername
- Email: your-email@example.com
- Phone: +XX-XXX-XXX-XXXX

---

## 🚫 COMMON SECURITY MISTAKES

### ❌ DON'T DO THIS:

1. **Committing secrets to Git**
   ```powershell
   # NEVER do this:
   git add .env
   ```

2. **Hardcoding secrets in code**
   ```python
   # NEVER do this:
   BOT_TOKEN = "123456:ABCdef..."  # ❌
   
   # Always use:
   BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ✅
   ```

3. **Using SQLite in production**
   - No concurrent writes
   - Corruption risk
   - No encryption at rest

4. **Exposing PostgreSQL to internet**
   - Always localhost only

5. **Weak passwords**
   - Use password manager
   - 16+ characters minimum

6. **No backups**
   - Always have daily backups
   - Test restoration regularly

7. **Running as Administrator**
   - Use service account when possible

---

## 📚 SECURITY RESOURCES

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Windows Server Benchmarks](https://www.cisecurity.org/benchmark/microsoft_windows_server)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Telegram Bot Security Best Practices](https://core.telegram.org/bots/faq#security)

---

**🔒 Security is a continuous process, not a one-time setup. Review and update regularly!**
