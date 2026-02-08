# TEST ONBOARDING FLOW WITH BUTTONS
# Quick debugging commands

# 1. Check if bot is running
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*main.py*"}

# 2. View bot logs (last 20 lines)
Get-Content D:\Projects\FreedomWalletBot\data\logs\bot.log -Tail 20 -Wait

# 3. Test in Telegram:
#    a. Open @FreedomWalletBot
#    b. Send: /start WEB_72X314
#    c. Should receive VIP unlock + Day 1 onboarding with buttons
#    d. Click each button to test:
#       - 📑 Copy Template
#       - 🌐 Hướng dẫn Web App
#       - 🎥 Xem Video
#       - ✅ Hoàn thành Day 1
#       - ❓ Cần hỗ trợ

# 4. Stop bot
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 5. Restart bot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
cd D:\Projects\FreedomWalletBot
python main.py

# 6. Check database for onboarding progress
# (Open SQLite viewer: data/bot.db -> users table)

# Expected Flow:
# User sends /start → Bot detects VIP status → Enrolls in ONBOARDING_7_DAY
# → ProgramManager schedules Day 1 → send_onboarding_message() called
# → Message sent with inline keyboard buttons
# → User clicks button → Callback handler processes → Response sent
