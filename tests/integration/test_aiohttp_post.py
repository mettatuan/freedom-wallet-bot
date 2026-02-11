"""
Test API với aiohttp (giống sheets_api_client.py)
"""
import asyncio
import aiohttp
import json

async def test_aiohttp():
    url = "https://script.google.com/macros/s/AKfycbxuVMMtTGXIrWphC3qzTTm5uudBLWunQzWONDEFX8RAoi3AiL0fXUbPz9MpEv_IWOpZ/exec"
    
    payload = {
        "action": "ping",
        "spreadsheet_id": "1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI",
        "api_key": "fwb_bot_testing_2026"
    }
    
    print("📡 Testing with aiohttp (same as bot)...")
    print(f"🔗 URL: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    print("\n" + "="*70)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"✅ Status Code: {response.status}")
                print(f"📄 Headers: {dict(response.headers)}")
                print(f"\n📄 Response:")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    except:
                        text = await response.text()
                        print(text)
                else:
                    text = await response.text()
                    print(text)
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_aiohttp())
