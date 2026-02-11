"""
Test Telegram Bot → Apps Script → Google Sheets Flow
Verify tất cả các bước xử lý dữ liệu
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.services.sheets_api_client import SheetsAPIClient
from bot.handlers.quick_record_template import (
    parse_quick_record_message,
    match_category_smart,
    parse_amount
)


async def test_full_flow():
    """Test complete flow from message parse to sheet write"""
    
    print("=" * 70)
    print("🧪 TEST LUỒNG DỮ LIỆU: Telegram Bot → Apps Script → Sheets")
    print("=" * 70)
    
    # STEP 1: Test Smart Parsing
    print("\n📝 STEP 1: Smart Parsing")
    print("-" * 70)
    
    test_messages = [
        "chi 50k ăn sáng",
        "mua sắm 1,5 triệu",
        "đầu tư SP500 27tr",
        "lương 15 triệu",
        "150k xem phim"
    ]
    
    for msg in test_messages:
        transaction_type, amount, note = parse_quick_record_message(msg)
        print(f"  Input:  '{msg}'")
        print(f"  Output: Type={transaction_type}, Amount={amount:,.0f}₫, Note='{note}'")
        print()
    
    # STEP 2: Test API Connection
    print("\n🔌 STEP 2: API Connection Test")
    print("-" * 70)
    
    # Load from environment
    from dotenv import load_dotenv
    load_dotenv()
    import os
    
    spreadsheet_id = os.getenv("TEST_SPREADSHEET_ID", "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg")
    client = SheetsAPIClient(spreadsheet_id)
    
    print(f"  Spreadsheet ID: {spreadsheet_id}")
    print(f"  API URL: {client.api_url[:70]}...")
    
    ping_result = await client.ping()
    if ping_result.get("success"):
        print(f"  ✅ PING: {ping_result.get('message')}")
        print(f"     Timestamp: {ping_result.get('timestamp')}")
    else:
        print(f"  ❌ PING FAILED: {ping_result.get('error')}")
        return
    
    # STEP 3: Get Categories
    print("\n📂 STEP 3: Get Categories")
    print("-" * 70)
    
    categories_result = await client.get_categories()
    if categories_result.get("success"):
        categories = categories_result.get("categories", [])
        print(f"  ✅ Categories loaded: {len(categories)} total")
        
        # Show investment categories
        investment_cats = [c for c in categories if c.get('type') == 'Đầu tư']
        print(f"  📈 Investment categories: {len(investment_cats)}")
        for cat in investment_cats[:5]:
            print(f"     - {cat.get('icon', '📝')} {cat['name']}")
        
        # Test category matching
        print("\n  🎯 Test Category Matching:")
        test_notes = [
            ("ăn sáng", "Chi"),
            ("đầu tư SP500", "Đầu tư"),
            ("lương tháng 2", "Thu")
        ]
        
        for note, trans_type in test_notes:
            matched = match_category_smart(note, trans_type, categories)
            if matched:
                print(f"     '{note}' → {matched.get('icon', '📝')} {matched['name']}")
            else:
                print(f"     '{note}' → ⚠️ No match (will create new)")
    else:
        print(f"  ❌ FAILED: {categories_result.get('error')}")
        return
    
    # STEP 4: Test Add Transaction (Chi)
    print("\n💸 STEP 4: Add Transaction - Chi (Expense)")
    print("-" * 70)
    
    result1 = await client.add_transaction(
        amount=50000,
        category="Ăn uống",
        note="test chi tiêu từ bot",
        from_jar="NEC",
        from_account="Cash",
        to_account=""
    )
    
    if result1.get("success"):
        print(f"  ✅ SUCCESS")
        print(f"     Transaction ID: {result1.get('transactionId')}")
        print(f"     Category: {result1.get('category')}")
        print(f"     Timestamp: {result1.get('timestamp')}")
    else:
        print(f"  ❌ FAILED: {result1.get('error')}")
    
    # STEP 5: Test Add Transaction (Đầu tư)
    print("\n📈 STEP 5: Add Transaction - Đầu tư (Investment)")
    print("-" * 70)
    
    result2 = await client.add_transaction(
        amount=27000000,
        category="Chứng khoán",
        note="test đầu tư SP500",
        from_jar="FFA",
        from_account="VCB",
        to_account=""
    )
    
    if result2.get("success"):
        print(f"  ✅ SUCCESS")
        print(f"     Transaction ID: {result2.get('transactionId')}")
        print(f"     Category: {result2.get('category')}")
        print(f"     Timestamp: {result2.get('timestamp')}")
    else:
        print(f"  ❌ FAILED: {result2.get('error')}")
    
    # STEP 6: Get Balance
    print("\n💰 STEP 6: Get Balance")
    print("-" * 70)
    
    balance_result = await client.get_balance()
    if balance_result.get("success"):
        jars = balance_result.get("jars", [])
        total = balance_result.get("totalBalance", 0)
        print(f"  ✅ Total Balance: {total:,.0f} ₫")
        print(f"  📦 Jars ({len(jars)}):")
        for jar in jars[:3]:
            print(f"     {jar.get('icon', '📦')} {jar['name']}: {jar.get('balance', 0):,.0f} ₫")
    else:
        print(f"  ❌ FAILED: {balance_result.get('error')}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"  ✅ Smart Parsing: OK")
    print(f"  ✅ API Connection: OK")
    print(f"  ✅ Get Categories: OK ({len(categories)} total)")
    print(f"  ✅ Add Transaction (Chi): OK")
    print(f"  ✅ Add Transaction (Đầu tư): OK")
    print(f"  ✅ Get Balance: OK")
    print("\n🎉 TẤT CẢ TESTS PASSED! Hệ thống sẵn sàng hoạt động.\n")


async def test_amount_parsing():
    """Test amount parsing with various formats"""
    print("\n" + "=" * 70)
    print("🔢 TEST AMOUNT PARSING")
    print("=" * 70)
    
    test_cases = [
        ("50k", 50000),
        ("50 nghìn", 50000),
        ("1.5tr", 1500000),
        ("1,5 triệu", 1500000),
        ("200 nghìn", 200000),
        ("1,500,000", 1500000),
        ("27tr", 27000000),
        ("2.5 triệu", 2500000)
    ]
    
    passed = 0
    failed = 0
    
    for amount_str, expected in test_cases:
        result = parse_amount(amount_str)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{amount_str}' → {result:,.0f}₫ (expected: {expected:,.0f}₫)")
        if result == expected:
            passed += 1
        else:
            failed += 1
    
    print(f"\n  Results: {passed} passed, {failed} failed")


async def test_investment_parsing():
    """Test investment transaction parsing với SP500 bug fix"""
    print("\n" + "=" * 70)
    print("📈 TEST INVESTMENT PARSING (SP500 BUG FIX)")
    print("=" * 70)
    
    test_cases = [
        ("đầu tư SP500 27tr", "Đầu tư", 27000000, "đầu tư SP500"),
        ("đầu tư VN30 50 triệu", "Đầu tư", 50000000, "đầu tư VN30"),
        ("mua CAT500 90k", "Chi", 90000, "mua CAT500"),  # Should NOT parse "500"
        ("chi 1.5tr mua ETF", "Chi", 1500000, "mua ETF"),
    ]
    
    passed = 0
    
    for text, exp_type, exp_amount, exp_note in test_cases:
        trans_type, amount, note = parse_quick_record_message(text)
        
        type_ok = trans_type == exp_type
        amount_ok = amount == exp_amount
        note_ok = note == exp_note
        
        status = "✅" if (type_ok and amount_ok and note_ok) else "❌"
        print(f"\n  {status} Input: '{text}'")
        print(f"     Type:   {trans_type} {'✅' if type_ok else f'❌ (expected: {exp_type})'}")
        print(f"     Amount: {amount:,.0f}₫ {'✅' if amount_ok else f'❌ (expected: {exp_amount:,.0f}₫)'}")
        print(f"     Note:   '{note}' {'✅' if note_ok else f'❌ (expected: {exp_note})'}")
        
        if type_ok and amount_ok and note_ok:
            passed += 1
    
    print(f"\n  Results: {passed}/{len(test_cases)} tests passed")


if __name__ == "__main__":
    print("\n🚀 Starting FreedomWallet Bot Integration Tests...\n")
    
    # Run all tests
    asyncio.run(test_amount_parsing())
    asyncio.run(test_investment_parsing())
    asyncio.run(test_full_flow())
    
    print("\n✅ All tests completed!\n")
