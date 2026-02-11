"""
Test quick record parser với message "37k cafe"
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from bot.handlers.quick_record_template import parse_quick_record_message

# Test cases
test_messages = [
    "37k cafe",
    "chi 37k cafe",
    "cafe 37k",
    "37k",
    "50k ăn sáng",
    "chi 50k ăn sáng",
    "Thu 5tr lương",
    "lương 5tr",
    "150k",
]

print("\n" + "="*80)
print("🧪 QUICK RECORD PARSER TEST")
print("="*80)

for msg in test_messages:
    print(f"\n📝 Input: '{msg}'")
    print("-" * 80)
    
    try:
        transaction_type, amount, note = parse_quick_record_message(msg)
        
        if transaction_type and amount > 0:
            print(f"✅ SUCCESS:")
            print(f"   Type: {transaction_type}")
            print(f"   Amount: {amount:,.0f} VND")
            print(f"   Note: '{note}'")
        else:
            print(f"❌ PARSE FAILED:")
            print(f"   Type: {transaction_type}")
            print(f"   Amount: {amount}")
            print(f"   Note: '{note}'")
            
    except Exception as e:
        print(f"💥 EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80 + "\n")
