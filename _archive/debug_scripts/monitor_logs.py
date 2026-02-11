#!/usr/bin/env python3
"""Real-time bot log monitor"""
import time
import os

log_file = "data/logs/bot.log"

print("🔍 Monitoring bot logs (Press Ctrl+C to stop)...\n")
print("=" * 70)

# Get initial file size
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(0, 2)  # Go to end
        
        try:
            while True:
                line = f.readline()
                if line:
                    # Highlight important lines
                    if 'ERROR' in line or 'Failed' in line:
                        print(f"❌ {line.strip()}")
                    elif 'start_command' in line or 'User' in line:
                        print(f"👤 {line.strip()}")
                    elif '✅' in line or 'SUCCESS' in line:
                        print(f"✅ {line.strip()}")
                    else:
                        print(f"   {line.strip()}")
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n✅ Stopped monitoring")
else:
    print(f"❌ Log file not found: {log_file}")
