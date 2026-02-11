"""Test investment transaction parsing - especially SP500 case"""
import sys
import re

# Inline copy of the parsing functions to avoid database imports

# Keywords
GRAMMAR_EXPENSE_KEYWORDS = ['chi', 'trả', 'tiêu', 'tốn', 'đóng', 'nạp']
GRAMMAR_INCOME_KEYWORDS = ['thu', 'nhận', 'nạp']
SEMANTIC_EXPENSE_KEYWORDS = ['mua']
SEMANTIC_INCOME_KEYWORDS = ['lương', 'thưởng', 'bán']
SEMANTIC_INVESTMENT_KEYWORDS = ['đầu tư']

EXPENSE_KEYWORDS = GRAMMAR_EXPENSE_KEYWORDS + SEMANTIC_EXPENSE_KEYWORDS
INCOME_KEYWORDS = GRAMMAR_INCOME_KEYWORDS + SEMANTIC_INCOME_KEYWORDS
INVESTMENT_KEYWORDS = SEMANTIC_INVESTMENT_KEYWORDS

# Regex pattern for amount
AMOUNT_PATTERN = r'(\d+(?:[,.\d]*)?)\s*(triệu|nghìn|nghin|tr|k)?'

def parse_amount(amount_str: str) -> float:
    """Parse amount string to float"""
    amount_str = amount_str.lower().strip()
    multiplier = 1
    
    # Check for multiplier units (longest first to avoid "5triệu" -> "5iệu" bug)
    if 'triệu' in amount_str or 'trieu' in amount_str:
        multiplier = 1000000
        amount_str = amount_str.replace('triệu', '').replace('trieu', '')
    elif 'nghìn' in amount_str or 'nghin' in amount_str:
        multiplier = 1000
        amount_str = amount_str.replace('nghìn', '').replace('nghin', '')
    elif 'tr' in amount_str:
        multiplier = 1000000
        amount_str = amount_str.replace('tr', '')
    elif 'k' in amount_str:
        multiplier = 1000
        amount_str = amount_str.replace('k', '')
    
    # Replace comma with dot for Vietnamese number format (1,5 = 1.5)
    if ',' in amount_str:
        if '.' not in amount_str and amount_str.count(',') == 1:
            amount_str = amount_str.replace(',', '.')
        else:
            amount_str = amount_str.replace(',', '')
    
    try:
        return float(amount_str) * multiplier
    except ValueError:
        return 0

def parse_quick_record_message(text: str):
    """Parse transaction message"""
    text = text.strip()
    text_lower = text.lower()
    
    # Step 1: Detect transaction type
    transaction_type = None
    type_keyword = None
    
    # Check investment first
    for keyword in INVESTMENT_KEYWORDS:
        if keyword in text_lower:
            transaction_type = "Đầu tư"
            type_keyword = keyword
            break
    
    if not transaction_type:
        for keyword in EXPENSE_KEYWORDS:
            if keyword in text_lower:
                transaction_type = "Chi"
                type_keyword = keyword
                break
    
    if not transaction_type:
        for keyword in INCOME_KEYWORDS:
            if keyword in text_lower:
                transaction_type = "Thu"
                type_keyword = keyword
                break
    
    # Step 2: Extract amount - find ALL matches and pick best
    amount = 0
    amount_match = None
    
    all_matches = list(re.finditer(AMOUNT_PATTERN, text, re.IGNORECASE))
    
    if all_matches:
        # Filter out matches with letters immediately before (SP500, CAT001)
        valid_matches = []
        for match in all_matches:
            start_pos = match.start()
            if start_pos > 0 and text[start_pos - 1].isalpha():
                continue  # Skip - part of a word/code
            valid_matches.append(match)
        
        if valid_matches:
            # Prioritize matches with units
            matches_with_units = [m for m in valid_matches if m.group(2)]
            if matches_with_units:
                amount_match = matches_with_units[0]
            else:
                amount_match = valid_matches[0]
            
            if amount_match:
                amount_str = amount_match.group(1)
                unit_str = amount_match.group(2) or ''
                full_amount_str = amount_str + unit_str
                amount = parse_amount(full_amount_str)
    
    if amount <= 0:
        return None, 0, ""
    
    # Step 3: Extract note
    parts_to_remove = []
    
    if type_keyword:
        keyword_match = re.search(rf'\b{type_keyword}\b', text, re.IGNORECASE)
        if keyword_match:
            should_remove = False
            
            if type_keyword in GRAMMAR_EXPENSE_KEYWORDS or type_keyword in GRAMMAR_INCOME_KEYWORDS:
                should_remove = True
            elif type_keyword in SEMANTIC_INVESTMENT_KEYWORDS:
                should_remove = False
            elif type_keyword in SEMANTIC_EXPENSE_KEYWORDS:
                if amount_match:
                    text_between = text[keyword_match.end():amount_match.start()].strip()
                    if len(text_between) == 0:
                        should_remove = True
            
            if should_remove:
                parts_to_remove.append((keyword_match.start(), keyword_match.end()))
    
    if amount_match:
        parts_to_remove.append((amount_match.start(), amount_match.end()))
    
    parts_to_remove.sort(reverse=True)
    
    note = text
    for start, end in parts_to_remove:
        note = note[:start] + note[end:]
    
    note = ' '.join(note.split()).strip()
    
    if not transaction_type:
        transaction_type = "Chi"
    
    return transaction_type, amount, note

def test_case(message: str, expected_type: str, expected_amount: float, expected_note: str):
    """Test a single parsing case"""
    result_type, result_amount, result_note = parse_quick_record_message(message)
    
    # Check if all match
    type_match = result_type == expected_type
    amount_match = result_amount == expected_amount
    note_match = result_note == expected_note
    
    status = "✅ PASS" if (type_match and amount_match and note_match) else "❌ FAIL"
    
    print(f"\n{status}: '{message}'")
    print(f"  Expected: {expected_type}, {expected_amount:,.0f}₫, '{expected_note}'")
    print(f"  Got:      {result_type}, {result_amount:,.0f}₫, '{result_note}'")
    
    if not type_match:
        print(f"  ⚠️ Type mismatch: expected '{expected_type}', got '{result_type}'")
    if not amount_match:
        print(f"  ⚠️ Amount mismatch: expected {expected_amount:,.0f}₫, got {result_amount:,.0f}₫")
    if not note_match:
        print(f"  ⚠️ Note mismatch: expected '{expected_note}', got '{result_note}'")
    
    return type_match and amount_match and note_match

print("=" * 60)
print("🧪 TEST INVESTMENT PARSING - SP500 & Product Codes")
print("=" * 60)

test_cases = [
    # Original bug case
    ("Đầu tư SP500 27tr", "Đầu tư", 27000000, "Đầu tư SP500"),
    
    # Variations of investment
    ("đầu tư sp500 27tr", "Đầu tư", 27000000, "đầu tư sp500"),
    ("Đầu tư VN30 5 triệu", "Đầu tư", 5000000, "Đầu tư VN30"),
    ("Đầu tư VTI 1,5tr", "Đầu tư", 1500000, "Đầu tư VTI"),
    
    # Make sure we DON'T match numbers in product codes
    ("Mua CAT500 90k", "Chi", 90000, "Mua CAT500"),
    ("Chi PRO123 150k", "Chi", 150000, "PRO123"),
    
    # Original cases should still work
    ("chi 50k tiền ăn", "Chi", 50000, "tiền ăn"),
    ("lương 5 triệu", "Thu", 5000000, "lương"),
    ("mua sắm 1,5 triệu", "Chi", 1500000, "mua sắm"),
]

passed = 0
total = len(test_cases)

for msg, exp_type, exp_amount, exp_note in test_cases:
    if test_case(msg, exp_type, exp_amount, exp_note):
        passed += 1

print("\n" + "=" * 60)
print(f"📊 RESULTS: {passed}/{total} tests passed")
print("=" * 60)

if passed == total:
    print("✅ ALL TESTS PASSED!")
    sys.exit(0)
else:
    print(f"❌ {total - passed} tests failed")
    sys.exit(1)
