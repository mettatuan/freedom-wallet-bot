"""
Manual monitoring - Quick status checks
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = "data/bot.db"
USER_ID = 1299465308

print("=" * 60)
print("🔍 QUICK STATUS CHECK")
print("=" * 60)
print()

# Get user status
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT subscription_tier, bot_chat_count, trial_ends_at, 
           premium_expires_at, last_active
    FROM users
    WHERE id = ?
""", (USER_ID,))

row = cursor.fetchone()

if row:
    tier = row[0] or 'FREE'
    count = row[1] or 0
    trial = row[2]
    premium = row[3]
    last_active = row[4]
    
    print(f"👤 User ID: {USER_ID}")
    print(f"🎯 Tier: {tier}")
    print(f"💬 Messages today: {count}/5" if tier == 'FREE' else f"💬 Messages: {count} (unlimited)")
    print(f"🎁 Trial ends: {trial or 'N/A'}")
    print(f"💎 Premium ends: {premium or 'N/A'}")
    print(f"⏰ Last active: {last_active or 'N/A'}")
    print()
    
    if tier == 'FREE':
        remaining = max(0, 5 - count)
        if remaining > 0:
            print(f"✅ Can send {remaining} more messages")
        else:
            print("❌ LIMIT REACHED - Should see upgrade prompt")
    else:
        print(f"✅ UNLIMITED access ({tier})")

else:
    print("❌ User not found")

conn.close()

print()
print("=" * 60)

# Check analytics
analytics_file = Path("data/analytics/events.jsonl")
if analytics_file.exists():
    with open(analytics_file, 'r') as f:
        events = f.readlines()
        print(f"📊 Total events logged: {len(events)}")
        
        if len(events) > 0:
            print("\n🔥 Recent 5 events:")
            for line in events[-5:]:
                import json
                event = json.loads(line)
                timestamp = event['timestamp'][:19]
                print(f"  • {timestamp} - {event['event']} (user {event['user_id']})")
else:
    print("📊 No analytics events yet")

print()
print("=" * 60)
print("✅ Ready to test! Bot is waiting for your actions...")
print()
print("📝 Test scenarios:")
print("1. Click 'Xem hướng dẫn' → Should work now!")
print("2. Send 6 messages → Hit limit → See upgrade prompt")
print("3. Click 'Dùng thử Premium' → See 3 options")
print("4. Test webapp/usage guide buttons")
print()
