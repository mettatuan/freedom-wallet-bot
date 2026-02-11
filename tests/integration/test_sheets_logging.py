"""
Test Google Sheets Payment Logging
Verify that payment data can be written to Google Sheets
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from bot.utils.sheets import get_sheets_client
from config.settings import settings
from datetime import datetime


def test_sheets_connection():
    """Test 1: Verify Google Sheets connection"""
    print("\n" + "=" * 60)
    print("  TEST 1: GOOGLE SHEETS CONNECTION")
    print("=" * 60)
    
    try:
        client = get_sheets_client()
        if not client:
            print("❌ Failed to initialize sheets client")
            return False
        
        print("✅ Sheets client initialized")
        
        # Test opening the support sheet
        sheet_id = settings.SUPPORT_SHEET_ID
        if not sheet_id:
            print("❌ No SUPPORT_SHEET_ID configured in .env")
            return False
        
        print(f"📋 Sheet ID: {sheet_id}")
        
        spreadsheet = client.open_by_key(sheet_id)
        print(f"✅ Opened spreadsheet: {spreadsheet.title}")
        
        # List all worksheets
        worksheets = spreadsheet.worksheets()
        print(f"📊 Worksheets ({len(worksheets)}):")
        for ws in worksheets:
            print(f"   • {ws.title} ({ws.row_count} rows x {ws.col_count} cols)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_payments_worksheet():
    """Test 2: Create or verify Payments worksheet"""
    print("\n" + "=" * 60)
    print("  TEST 2: PAYMENTS WORKSHEET")
    print("=" * 60)
    
    try:
        client = get_sheets_client()
        spreadsheet = client.open_by_key(settings.SUPPORT_SHEET_ID)
        
        # Try to get Payments worksheet
        try:
            worksheet = spreadsheet.worksheet("Payments")
            print(f"✅ 'Payments' worksheet exists")
            print(f"   Rows: {worksheet.row_count}")
            print(f"   Cols: {worksheet.col_count}")
            
            # Check headers
            headers = worksheet.row_values(1)
            if headers:
                print(f"   Headers: {', '.join(headers)}")
            
        except Exception as e:
            print(f"⚠️  'Payments' worksheet not found, creating...")
            
            # Create new worksheet
            worksheet = spreadsheet.add_worksheet(title="Payments", rows=1000, cols=10)
            
            # Add headers
            headers = [
                'Ngày Duyệt', 'Mã Xác Nhận', 'User ID', 'Username', 
                'Họ Tên', 'Số Tiền (VND)', 'Trạng Thái', 'Admin Duyệt', 'Gói'
            ]
            worksheet.update('A1:I1', [headers])
            print(f"✅ Created 'Payments' worksheet with headers")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_write_test_payment():
    """Test 3: Write a test payment record"""
    print("\n" + "=" * 60)
    print("  TEST 3: WRITE TEST PAYMENT")
    print("=" * 60)
    
    try:
        client = get_sheets_client()
        spreadsheet = client.open_by_key(settings.SUPPORT_SHEET_ID)
        worksheet = spreadsheet.worksheet("Payments")
        
        # Test data
        test_data = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "TEST001",
            "123456789",
            "@test_user",
            "Test User",
            999000,
            "TEST",
            "999999999",
            "PREMIUM_365"
        ]
        
        print(f"📝 Writing test payment...")
        worksheet.append_row(test_data, value_input_option='USER_ENTERED')
        print(f"✅ Test payment written successfully")
        
        # Read back to verify
        last_row = worksheet.get_all_values()[-1]
        print(f"✅ Verified: {last_row[1]} (User: {last_row[4]})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "=" * 60)
    print("  GOOGLE SHEETS PAYMENT LOGGING TEST")
    print("=" * 60)
    print(f"\nSheet ID: {settings.SUPPORT_SHEET_ID}")
    print(f"Service Account: eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com")
    print("\n⚠️  Make sure you've shared the sheet with the service account!")
    
    # Run tests
    results = []
    
    results.append(("Sheets Connection", test_sheets_connection()))
    results.append(("Payments Worksheet", test_create_payments_worksheet()))
    results.append(("Write Test Payment", test_write_test_payment()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Payment logging is ready!")
        print("\n📋 Next steps:")
        print("1. Test payment approval in bot")
        print("2. Check Google Sheet for new row")
        print("3. Verify all data is correct")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Common issues:")
        print("• Sheet not shared with service account")
        print("• Service account credentials file missing")
        print("• SUPPORT_SHEET_ID not configured in .env")


if __name__ == "__main__":
    main()
