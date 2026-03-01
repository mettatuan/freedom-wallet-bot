# 🚀 Advanced Monitoring & Recovery System

## Tổng Quan

3 hệ thống nâng cao đã được triển khai để đảm bảo bot luôn stable và tự động recovery khi có vấn đề:

1. **🐕 Watchdog Service** - Tự động restart bot khi crash
2. **📊 Metrics Dashboard** - Theo dõi auto-fix success rate
3. **🔄 Auto-Rollback** - Phát hiện regression và tự động rollback code

---

## 1. 🐕 Watchdog Service

### Chức Năng

- ✅ Kiểm tra bot có đang chạy không (mỗi 30 giây)
- ✅ Nếu bot crash → tự động restart
- ✅ Kiểm tra restart flag từ auto-fix (Event Loop closed)
- ✅ Ghi log mỗi lần restart
- ✅ Alert admin nếu restart > 3 lần/10 phút (throttling)

### Setup Trên VPS

**Option 1: Run Background Terminal**

```powershell
# SSH vào VPS
ssh freedom-vps

# Navigate to bot directory
cd C:\FreedomWalletBot

# Run watchdog trong background
powershell -ExecutionPolicy Bypass -File scripts\watchdog_bot.ps1
```

**Option 2: Windows Scheduled Task (Khuyến nghị)**

```powershell
# Tạo scheduled task chạy at startup
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -NoProfile -File C:\FreedomWalletBot\scripts\watchdog_bot.ps1"

$trigger = New-ScheduledTaskTrigger -AtStartup

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest

Register-ScheduledTask -TaskName "FreedomWalletBot_Watchdog" `
    -Action $action -Trigger $trigger -Principal $principal

# Start watchdog
Start-ScheduledTask -TaskName "FreedomWalletBot_Watchdog"
```

### Logs

Watchdog logs được ghi vào: `C:\FreedomWalletBot\data\logs\watchdog.log`

```
[2026-03-01 08:30:00] 🐕 Watchdog Service Started
[2026-03-01 08:30:00]    Bot Path: C:\FreedomWalletBot
[2026-03-01 08:30:00]    Check Interval: 30s
[2026-03-01 08:30:30] Health check #1: ✅ Running
[2026-03-01 09:15:00] 🚨 Bot is NOT running - attempting restart...
[2026-03-01 09:15:03] ✅ Bot restarted successfully
```

### Configuration

Edit parameters trong `scripts\watchdog_bot.ps1`:

```powershell
$CheckIntervalSeconds = 30      # Interval giữa mỗi check
$MaxRestartsPerWindow = 3       # Max restarts trước khi throttle
$RestartWindowMinutes = 10      # Cửa sổ thời gian tính restarts
```

---

## 2. 📊 Metrics Dashboard

### Admin Commands

**A. View Stats**

```
/autofix_stats
```

**Output:**
```
📊 AUTO-FIX METRICS

Tổng quan:
  • Tổng lần fix: 150
  • Thành công: 127 (84.7%)
  • Thất bại: 23

Hoạt động gần đây:
  • 1 giờ qua: 12 fixes
  • 24 giờ qua: 95 fixes

Chi tiết theo handler:

  Database Locked
    Attempts: 45 | Success: 95.6% | Avg: 1.02s

  Connection Reset
    Attempts: 38 | Success: 92.1% | Avg: 0.51s

  SSL Certificate Error
    Attempts: 22 | Success: 68.2% | Avg: 0.31s
```

**B. View History**

```
/autofix_history [limit]
```

**Examples:**
- `/autofix_history` → Last 20 fixes
- `/autofix_history 50` → Last 50 fixes

**Output:**
```
📜 AUTO-FIX HISTORY

08:45:23 | ✅ Database Locked (1.01s)
08:47:15 | ✅ Connection Reset (0.52s)
08:51:02 | ❌ SSL Certificate Error (0.28s)
09:03:44 | ✅ Telegram Rate Limit (30.15s)
```

**C. Reset Metrics**

```
/autofix_reset CONFIRM
```

⚠️ **Warning:** This deletes all metrics history!

### Metrics Storage

- **File:** `data/metrics/autofix_metrics.json`
- **Retention:** Last 7 days of history, top 1000 entries
- **Auto-save:** Every 10 attempts

### Success Rate Trends

Monitor success rates over time để detect:
- Handler nào cần improve
- Loại lỗi nào tăng đột biến
- Patterns của failures

---

## 3. 🔄 Auto-Rollback System

### Cách Hoạt Động

```
Deploy New Code
    ↓
Create Health Snapshot (errors, response time)
    ↓
Monitor 15 phút
    ↓
Detect Regression?
    ├── NO → Continue monitoring
    └── YES → Auto-Rollback + Alert Admin
```

### Regression Triggers

Bot sẽ tự động rollback nếu:

1. **Error Rate Spike** - Tăng >50% so với baseline
2. **Critical Errors** - ≥3 critical errors trong window
3. **Response Time** - Tăng >2x so với baseline

### Admin Commands

**A. View Status**

```
/rollback_status
```

**Output:**
```
🔄 AUTO-ROLLBACK STATUS

Status: ✅ Enabled
Monitoring Window: 15 minutes
Error Rate Threshold: 1.5x
Response Time Threshold: 2.0x
Critical Error Threshold: 3

Current Commit: f8a13e9
Snapshots Stored: 24

📜 Recent Rollbacks:
✅ 2026-03-01 07:15
   → abc1234
   Reason: Error rate increased 2.3x (5 → 12)
```

**B. Enable/Disable**

```
/rollback_enable   # Turn ON auto-rollback
/rollback_disable  # Turn OFF auto-rollback
```

**C. Manual Snapshot**

```
/rollback_snapshot
```

Creates health snapshot at current moment (useful sau deploy mới).

**D. Manual Rollback**

```
/rollback_now <commit_hash> CONFIRM
```

**Example:**
```
/rollback_now abc1234 CONFIRM
```

⚠️ **Warning:** This will reset code and restart bot!

### Data Storage

- **Config:** `data/rollback/config.json`
- **Snapshots:** `data/rollback/health_snapshots.json` (30 days)
- **History:** `data/rollback/rollback_history.json` (50 entries)

### Monitoring Window

Sau mỗi deploy:
- **0-3 min:** Bot warm-up (không check)
- **3-18 min:** Active monitoring (2-min intervals)
- **18+ min:** Normal monitoring

### Alert Examples

**Rollback Success:**
```
🔄 AUTO-ROLLBACK EXECUTED

Reason: Error rate increased 2.1x (8 → 17)

Rolled back to: abc1234

Bot sẽ restart trong ít giây.
```

**Rollback Failed:**
```
🚨 AUTO-ROLLBACK FAILED

Regression detected: Critical error Event Loop closed

❌ Rollback thất bại - cần can thiệp thủ công!

Kiểm tra ngay: /healthcheck
```

---

## 🔧 Configuration Guide

### Adjust Thresholds

Edit `data/rollback/config.json`:

```json
{
  "enabled": true,
  "monitoring_window_minutes": 15,
  "error_rate_threshold": 1.5,
  "response_time_threshold": 2.0,
  "critical_error_threshold": 3
}
```

**Recommendations:**

- **Conservative** (ít rollback nhưng chậm): 
  - `error_rate_threshold: 2.0`
  - `critical_error_threshold: 5`

- **Aggressive** (rollback nhanh nhưng có thể false positive):
  - `error_rate_threshold: 1.3`
  - `critical_error_threshold: 2`

---

## 📈 Deployment Flow với Auto-Systems

### Standard Deployment

```bash
# 1. Test locally
python main.py

# 2. Commit & push
git add -A
git commit -m "feat: new feature"
git push

# 3. Deploy to VPS
ssh freedom-vps "cd C:\FreedomWalletBot && git pull && taskkill /F /IM python.exe && timeout /t 5 && schtasks /run /tn FreedomWalletBot"

# 4. Create baseline snapshot (trong bot)
/rollback_snapshot

# 5. Monitor for 15-20 minutes
# → Auto-rollback sẽ tự động trigger nếu có vấn đề
```

### Emergency Rollback

```bash
# 1. Check current commit
/rollback_status

# 2. Find last good commit
git log --oneline -10

# 3. Rollback
/rollback_now <good_commit_hash> CONFIRM

# Bot sẽ tự động restart với code cũ
```

---

## 🎯 Expected Impact

**Với 3 Systems này:**

- **Uptime:** 95% → 99.5% (tự động restart khi crash)
- **MTTR (Mean Time To Recovery):** 10 phút → 2 phút
- **Manual interventions:** -80% (hầu hết tự động handle)
- **False positives:** <5% (rollback nhầm)
- **Admin workload:** -60% (ít phải check logs/restart thủ công)

---

## 🐛 Troubleshooting

### Watchdog không restart bot

**Check:**
1. Task có đang chạy không? `Get-ScheduledTask -TaskName "FreedomWalletBot_Watchdog"`
2. Check log: `type C:\FreedomWalletBot\data\logs\watchdog.log`
3. Test manual: `.\scripts\watchdog_bot.ps1`

### Metrics không hiển thị

**Check:**
1. File exists? `C:\FreedomWalletBot\data\metrics\autofix_metrics.json`
2. Permissions OK?
3. Run `/autofix_reset CONFIRM` để reset

### Rollback không trigger

**Check:**
1. Enabled? `/rollback_status`
2. Có baseline snapshot? (cần ≥2 commits)
3. Check config: `type data\rollback\config.json`

---

## 📚 Related Documentation

- [Auto-Fix System](AUTO_FIX_SYSTEM.md) - Chi tiết 6 auto-fix handlers
- [Health Monitor](../bot/jobs/health_monitor.py) - Bot health checks
- [Error Tracker](../bot/core/error_tracker.py) - Error tracking & alerting

---

**Deployed:** March 1, 2026  
**Version:** 2.0.0  
**Commit:** f8a13e9
