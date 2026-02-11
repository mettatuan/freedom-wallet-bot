"""Quick test for Đầu tư SP500 parsing"""
import sys
import re

# Inline keywords
SEMANTIC_INVESTMENT_KEYWORDS = ['đầu tư']
AMOUNT_PATTERN = r'(\d+(?:[,.\d]*)?)\s*(triệu|nghìn|nghin|tr|k)?'

text = "Đầu tư SP500 27tr"
text_lower = text.lower()

# Check investment
for keyword in SEMANTIC_INVESTMENT_KEYWORDS:
    if keyword in text_lower:
        print(f"✅ Transaction type: Đầu tư (found '{keyword}')")
        break

# Find all amount matches
all_matches = list(re.finditer(AMOUNT_PATTERN, text, re.IGNORECASE))
print(f"\n📊 Found {len(all_matches)} amount matches:")
for i, match in enumerate(all_matches, 1):
    start_pos = match.start()
    has_letter_before = start_pos > 0 and text[start_pos - 1].isalpha()
    print(f"  {i}. '{match.group()}' at pos {start_pos} (letter before: {has_letter_before})")

# Filter valid matches
valid_matches = []
for match in all_matches:
    start_pos = match.start()
    if start_pos > 0 and text[start_pos - 1].isalpha():
        print(f"  ❌ Skip '{match.group()}' (part of word)")
        continue
    valid_matches.append(match)
    print(f"  ✅ Valid match: '{match.group()}'")

# Get best match
matches_with_units = [m for m in valid_matches if m.group(2)]
if matches_with_units:
    best = matches_with_units[0]
    print(f"\n✅ Best match (with unit): '{best.group()}' = {best.group(1)} {best.group(2) or ''}")
    
    # Calculate amount
    amount_str = best.group(1)
    unit_str = best.group(2) or ''
    
    if 'tr' in unit_str.lower():
        multiplier = 1000000
        amount = float(amount_str.replace(',', '.')) * multiplier
        print(f"✅ Amount: {amount:,.0f}₫")
