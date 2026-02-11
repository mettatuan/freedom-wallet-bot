"""
Test Apps Script API with ping action
"""
import asyncio
import aiohttp


async def test_api_ping():
    """Test if API URL is correct using ping"""
    
    api_url = "https://script.google.com/macros/s/AKfycbzTB7Itr_bt-WM2lThWE3InvPz3Givv2TwSqxaLfiUOCnal_aVpPgjD9nLEuVuL5RODjQ/exec"
    api_key = "fwb_bot_testing_2026"
    spreadsheet_id = "1er6t9JQHLa9eZ1YTIM4aK0IhN37yPq6IUVbOg4-8mXg"
    
    print("\n" + "="*70)
    print("🧪 TEST APPS SCRIPT API - PING")
    print("="*70 + "\n")
    
    print(f"API URL: {api_url}")
    print(f"API Key: {api_key}")
    print(f"Spreadsheet ID: {spreadsheet_id}")
    print()
    
    payload = {
        "action": "ping",
        "api_key": api_key,
        "spreadsheet_id": spreadsheet_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Sending ping request...")
            
            async with session.post(
                api_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                status = response.status
                print(f"\n✅ HTTP Status: {status}")
                
                if status == 200:
                    result = await response.json()
                    print(f"✅ Response:")
                    print(f"   {result}")
                else:
                    text = await response.text()
                    print(f"❌ Error Response:")
                    print(f"   {text[:500]}")
    
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("✅ TEST COMPLETE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Test Apps Script API\n")
    asyncio.run(test_api_ping())
