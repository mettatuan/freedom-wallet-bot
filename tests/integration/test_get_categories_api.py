"""
Test getCategories API call to debug why categories are not loaded
"""
import sys
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv

# Force reload .env before any imports
project_root = Path(__file__).parent
load_dotenv(project_root / '.env', override=True)

# Verify API key is loaded
api_key_check = os.getenv("FREEDOM_WALLET_API_KEY")
print(f"\n🔑 Pre-import API key check: '{api_key_check}' (length: {len(api_key_check) if api_key_check else 0})\n")

sys.path.insert(0, str(Path(__file__).parent))

from bot.services.sheets_api_client import SheetsAPIClient, SHEETS_API_KEY
from bot.utils.database import get_db, User
from config.settings import settings

# Verify again after import
print(f"🔑 Post-import SHEETS_API_KEY: '{SHEETS_API_KEY}' (length: {len(SHEETS_API_KEY)})\n")


async def test_get_categories():
    """Test getCategories for admin user"""
    
    print("\n" + "="*70)
    print("🧪 TEST GET CATEGORIES API")
    print("="*70 + "\n")
    
    # Get admin user from database
    admin_id = settings.ADMIN_USER_ID
    print(f"📝 Admin ID: {admin_id}")
    
    db = next(get_db())
    user = db.query(User).filter(User.id == admin_id).first()
    
    if not user:
        print(f"❌ User not found in database!")
        return
    
    print(f"✅ User found: {user.full_name or user.username}")
    print(f"📊 Spreadsheet ID: {user.spreadsheet_id}")
    
    if not user.spreadsheet_id:
        print(f"❌ User has no spreadsheet connected!")
        return
    
    print(f"\n{'='*70}")
    print("🔄 Calling getCategories API...")
    print(f"{'='*70}\n")
    
    try:
        client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
        result = await client.get_categories()
        
        print(f"✅ API Response:")
        print(f"   Success: {result.get('success')}")
        
        if result.get('error'):
            print(f"   ❌ Error: {result.get('error')}")
        
        if result.get('success'):
            categories = result.get('categories', [])
            print(f"   📊 Total categories: {len(categories)}")
            
            if categories:
                print(f"\n{'='*70}")
                print("📋 CATEGORIES PREVIEW (first 10):")
                print(f"{'='*70}\n")
                
                for i, cat in enumerate(categories[:10], 1):
                    icon = cat.get('icon', '❓')
                    name = cat.get('name', 'N/A')
                    cat_type = cat.get('type', 'N/A')
                    jar_id = cat.get('jarId', '-')
                    auto = cat.get('autoAllocate', False)
                    cat_id = cat.get('id', 'N/A')
                    
                    print(f"{i:2}. {icon} {name:20} | {cat_type:6} | Jar: {jar_id:4} | Auto: {auto} | ID: {cat_id}")
                
                # Show income categories
                income_cats = [c for c in categories if c.get('type') == 'Thu']
                print(f"\n{'='*70}")
                print(f"💰 INCOME CATEGORIES (Thu): {len(income_cats)}")
                print(f"{'='*70}\n")
                
                for cat in income_cats[:10]:
                    icon = cat.get('icon', '❓')
                    name = cat.get('name', 'N/A')
                    jar_id = cat.get('jarId', '-')
                    auto = cat.get('autoAllocate', False)
                    cat_id = cat.get('id', 'N/A')
                    
                    print(f"   {icon} {name:20} | Jar: {jar_id:4} | Auto: {auto} | ID: {cat_id}")
                
                # Check if "Lương" exists
                luong_cats = [c for c in categories if 'lương' in c.get('name', '').lower() or 'luong' in c.get('name', '').lower()]
                
                print(f"\n{'='*70}")
                print(f"🔍 SEARCH RESULT: 'Lương' category")
                print(f"{'='*70}\n")
                
                if luong_cats:
                    for cat in luong_cats:
                        print(f"   ✅ FOUND: {cat}")
                else:
                    print(f"   ❌ NOT FOUND: No 'Lương' category")
                
            else:
                print(f"\n⚠️ Categories array is EMPTY!")
                print(f"   Full response: {result}")
        else:
            print(f"\n❌ API call FAILED!")
            print(f"   Full response: {result}")
    
    except Exception as e:
        print(f"\n❌ Exception occurred:")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*70}")
    print("✅ TEST COMPLETE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    print("\n🤖 Freedom Wallet Bot - Test Get Categories API\n")
    asyncio.run(test_get_categories())
