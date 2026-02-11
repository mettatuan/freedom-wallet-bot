"""Test regex filter patterns"""
import re

# New regex pattern from handler
pattern = r'\d+(?:[,.\d]*)?(?:\s*(?:k|tr|triệu|nghìn|nghin)\b|(?:,\d{3})+)'

test_cases = [
    # Should MATCH (valid transactions)
    ("mua sắm 1,5 triệu", True),
    ("chi 50k tiền ăn", True),
    ("xem phim 150k", True),
    ("150k xem phim", True),
    ("lương 5 triệu", True),
    ("200 nghìn taxi", True),
    ("1,500,000 mua nhà", True),
    ("chi tiền ăn 50k", True),
    ("50k cơm trưa", True),
    ("mua cà phê 35k", True),
    ("1.5tr du lịch", True),
    
    # Should NOT match (not transactions)
    ("xin chào", False),
    ("help me", False),
    ("tôi cần hỗ trợ", False),
    ("làm sao thêm giao dịch", False),
]

print("="*70)
print("REGEX FILTER TEST")
print("="*70)
print()

passed = 0
failed = 0

for text, should_match in test_cases:
    match = re.search(pattern, text, re.IGNORECASE)
    matched = match is not None
    
    if matched == should_match:
        status = "✅ PASS"
        passed += 1
    else:
        status = "❌ FAIL"
        failed += 1
    
    expected = "MATCH" if should_match else "NO MATCH"
    got = "MATCH" if matched else "NO MATCH"
    
    print(f"{status} '{text}'")
    print(f"  Expected: {expected}, Got: {got}")
    if match:
        print(f"  Matched: '{match.group()}'")
    print()

print("="*70)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("="*70)
