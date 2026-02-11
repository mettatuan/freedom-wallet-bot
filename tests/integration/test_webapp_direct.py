"""
Test Web App URL directly to diagnose why transactions aren't saving
"""
import requests
import json
from datetime import datetime

# Web App URL from user
WEBAPP_URL = 'https://script.google.com/macros/s/AKfycbwloP0ItK9dnDRl8AW2V-1r9eZe1LRC-Y3yNx-7BNAd2r9uoKBmWLWq2bBQjLYZtY0pGQ/exec'
SPREADSHEET_ID = '1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI'

def test_ping():
    """Test basic connectivity"""
    print('=' * 60)
    print('TEST 1: PING TEST')
    print('=' * 60)
    
    payload = {
        'api_key': 'fwb_bot_production_2026',
        'action': 'ping',
        'spreadsheet_id': SPREADSHEET_ID
    }
    
    try:
        response = requests.post(WEBAPP_URL, json=payload, timeout=10)
        print(f'✅ Status Code: {response.status_code}')
        print(f'📨 Response: {response.text[:500]}')
        
        try:
            data = response.json()
            print(f'✅ JSON Response: {json.dumps(data, indent=2)}')
            return data.get('success', False)
        except:
            print(f'⚠️  Response is not JSON')
            return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

def test_add_transaction():
    """Test adding a transaction"""
    print('\n' + '=' * 60)
    print('TEST 2: ADD TRANSACTION')
    print('=' * 60)
    
    tx_id = f'TX_TEST_{int(datetime.now().timestamp())}'
    
    payload = {
        'api_key': 'fwb_bot_production_2026',
        'action': 'addTransaction',
        'spreadsheet_id': SPREADSHEET_ID,
        'data': {
            'id': tx_id,
            'date': datetime.now().strftime('%d/%m/%Y'),
            'type': 'Chi',
            'category': '🍽️ Ăn uống',
            'amount': 50000,
            'fromAccount': 'Tiền mặt',
            'note': 'TEST từ Code.gs deployment check'
        }
    }
    
    print(f'📤 Sending payload:')
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        response = requests.post(WEBAPP_URL, json=payload, timeout=15)
        print(f'✅ Status Code: {response.status_code}')
        print(f'📨 Response: {response.text[:1000]}')
        
        try:
            data = response.json()
            print(f'\n✅ JSON Response:')
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                print(f'\n🎉 SUCCESS! Transaction ID: {data.get("transactionId")}')
                print(f'📊 Check spreadsheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit')
                return True
            else:
                print(f'\n❌ FAILED: {data.get("error", "Unknown error")}')
                return False
        except Exception as json_err:
            print(f'⚠️  Response is not JSON: {json_err}')
            print(f'Raw response: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Error: {e}')
        return False

if __name__ == '__main__':
    print('🔍 TESTING WEB APP DEPLOYMENT')
    print(f'📍 URL: {WEBAPP_URL[:60]}...')
    print(f'📊 Spreadsheet: {SPREADSHEET_ID}')
    print()
    
    # Test 1: Ping
    ping_ok = test_ping()
    
    # Test 2: Add Transaction
    if ping_ok:
        print('\n✅ Ping successful, proceeding to transaction test...')
        tx_ok = test_add_transaction()
        
        if tx_ok:
            print('\n' + '=' * 60)
            print('✅ ALL TESTS PASSED!')
            print('=' * 60)
            print('🎯 Your Web App is working correctly.')
            print('📊 Check your spreadsheet for the test transaction.')
        else:
            print('\n' + '=' * 60)
            print('⚠️  TRANSACTION TEST FAILED')
            print('=' * 60)
            print('Possible issues:')
            print('1. Apps Script not deployed correctly')
            print('2. Sheet name mismatch (looking for "Giao dịch")')
            print('3. Code.gs has bugs in addTransaction logic')
            print('4. Browser blocking Web App execution')
    else:
        print('\n' + '=' * 60)
        print('❌ PING TEST FAILED')
        print('=' * 60)
        print('Possible issues:')
        print('1. Web App URL is incorrect or outdated')
        print('2. Web App not deployed as "Anyone" access')
        print('3. Apps Script project not published')
        print('4. Network/firewall blocking requests')
