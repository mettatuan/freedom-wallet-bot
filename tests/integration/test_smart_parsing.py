"""
Test Smart Natural Language Parsing

Demonstrates the new flexible parsing that understands various Vietnamese transaction formats
"""
import sys
sys.path.insert(0, 'D:/Projects/FreedomWalletBot')

from bot.handlers.quick_record_template import parse_quick_record_message

# Test cases with expected results
test_cases = [
    # Original format
    ("chi 50k tiền ăn", "Chi", 50000, "tiền ăn"),
    ("thu 1000k lương", "Thu", 1000000, "lương"),
    
    # Flexible word order - Amount at end
    ("chi xem phim 150k", "Chi", 150000, "xem phim"),
    ("chi tiền điện 200k", "Chi", 200000, "tiền điện"),
    ("mua cà phê 35k", "Chi", 35000, "mua cà phê"),  # Keep "mua" as part of category
    
    # No type keyword - Defaults to Chi
    ("xem phim 150k", "Chi", 150000, "xem phim"),
    ("cà phê 30k", "Chi", 30000, "cà phê"),
    ("150k xem phim", "Chi", 150000, "xem phim"),
    ("50k cơm trưa", "Chi", 50000, "cơm trưa"),
    
    # Income with smart detection
    ("lương 5 triệu", "Thu", 5000000, "lương"),
    ("nhận thưởng 2tr", "Thu", 2000000, "thưởng"),
    ("thu 500k bán hàng", "Thu", 500000, "bán hàng"),
    
    # Different amount formats
    ("chi 1,5 triệu mua quần áo", "Chi", 1500000, "mua quần áo"),
    ("chi 1.5tr đi du lịch", "Chi", 1500000, "đi du lịch"),
    ("mua sắm 1,500,000", "Chi", 1500000, "mua sắm"),
    
    # Various expense keywords
    ("trả 300k tiền nhà", "Chi", 300000, "tiền nhà"),
    ("đóng 500k học phí", "Chi", 500000, "học phí"),
    ("tiêu 80k xăng xe", "Chi", 80000, "xăng xe"),
    
    # Edge cases
    ("200 nghìn taxi", "Chi", 200000, "taxi"),
    ("50 nghin com", "Chi", 50000, "com"),
]

def test_parsing():
    print("=" * 80)
    print("SMART NATURAL LANGUAGE PARSING TEST")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected_type, expected_amount, expected_note) in enumerate(test_cases, 1):
        result_type, result_amount, result_note = parse_quick_record_message(input_text)
        
        # Check if matches expected
        type_match = result_type == expected_type
        amount_match = result_amount == expected_amount
        note_match = result_note.lower() == expected_note.lower()
        
        success = type_match and amount_match and note_match
        
        if success:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"
        
        print(f"{status} Test {i}: \"{input_text}\"")
        print(f"  Expected: {expected_type} | {expected_amount:,.0f}₫ | {expected_note}")
        print(f"  Got:      {result_type or 'None'} | {result_amount:,.0f}₫ | {result_note}")
        
        if not success:
            if not type_match:
                print(f"    ⚠️ Type mismatch")
            if not amount_match:
                print(f"    ⚠️ Amount mismatch")
            if not note_match:
                print(f"    ⚠️ Note mismatch")
        
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    # Summary of new capabilities
    print()
    print("✨ NEW CAPABILITIES:")
    print("  1. ✅ Flexible word order: 'chi 150k phim' OR 'chi phim 150k' OR 'phim 150k'")
    print("  2. ✅ No keyword needed: '150k xem phim' defaults to Chi")
    print("  3. ✅ Smart income detection: 'lương 5tr' auto-detects as Thu")
    print("  4. ✅ Multiple amount formats: 50k, 1.5tr, 1,5 triệu, 1,500,000")
    print("  5. ✅ Various keywords: chi, mua, trả, đóng, tiêu, thu, nhận")
    print("  6. ✅ Vietnamese units: k, tr, triệu, nghìn")
    print()

if __name__ == "__main__":
    test_parsing()
