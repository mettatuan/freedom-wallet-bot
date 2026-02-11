"""
Debug API Key loading
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Reload .env
project_root = Path(__file__).parent
dotenv_path = project_root / '.env'
print(f"📂 Loading .env from: {dotenv_path}")
print(f"📂 File exists: {dotenv_path.exists()}")

load_dotenv(dotenv_path=dotenv_path, override=True)

# Check API key
api_key = os.getenv("FREEDOM_WALLET_API_KEY")
print(f"\n🔑 FREEDOM_WALLET_API_KEY = '{api_key}'")
print(f"🔑 Length: {len(api_key) if api_key else 0}")
print(f"🔑 Type: {type(api_key)}")

# Check from bot.services
from bot.services.sheets_api_client import SHEETS_API_KEY
print(f"\n📦 From sheets_api_client module:")
print(f"🔑 SHEETS_API_KEY = '{SHEETS_API_KEY}'")
print(f"🔑 Length: {len(SHEETS_API_KEY)}")

# Check from config.settings
from config.settings import settings
print(f"\n⚙️ From config.settings:")
print(f"🔑 settings.FREEDOM_WALLET_API_KEY = '{settings.FREEDOM_WALLET_API_KEY}'")
print(f"🔑 Length: {len(settings.FREEDOM_WALLET_API_KEY) if settings.FREEDOM_WALLET_API_KEY else 0}")
