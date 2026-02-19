"""
Freedom Wallet Sheets API Client (Option 3 - Template Integration)
Gọi API từ Google Sheets Web App đã deploy
Version 2.0 - Added authentication & caching (Phase 1.5)
"""
import aiohttp
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Web App URL - Bot API Handler (Vietnamese sheet support + dd/MM/yyyy date format + Authentication)
SHEETS_API_URL = os.getenv(
    "FREEDOM_WALLET_API_URL",
    "https://script.google.com/macros/s/AKfycbwzT4WokC13aouSr8f3X_2gxiAORid_gzObwFS187o8nw4_aI_DpLq6Mx38QRP_q2cc/exec"
)

# API Key for authentication (Phase 1.5)
SHEETS_API_KEY = os.getenv("FREEDOM_WALLET_API_KEY", "")

# Freedom Wallet Template URL for users to copy
TEMPLATE_URL = "https://docs.google.com/spreadsheets/d/YOUR_TEMPLATE_ID/copy"


class SheetsAPIClient:
    """Client to interact with Freedom Wallet API with in-memory caching"""
    
    def __init__(self, spreadsheet_id: str, webapp_url: Optional[str] = None):
        self.spreadsheet_id = spreadsheet_id
        # ✅ FIX: Use user's webapp_url if provided, otherwise use default
        self.api_url = webapp_url or SHEETS_API_URL
        
        # 🐛 DEBUG: Log API URL being used
        logger.info(f"🔧 SheetsAPIClient initialized:")
        logger.info(f"   📊 Spreadsheet ID: {spreadsheet_id[:20]}...")
        logger.info(f"   🌐 API URL: {self.api_url[:80]}...")
        logger.info(f"   ✅ Using {'USER' if webapp_url else 'DEFAULT'} URL")
        
        # Simple in-memory cache (Phase 1.5 optimization)
        self._cache = {}  # {key: (data, timestamp)}
        self._cache_ttl = 300  # 5 minutes
        
    def _get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if still valid"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            import time
            if time.time() - timestamp < self._cache_ttl:
                logger.debug(f"📦 Cache hit: {key}")
                return data
            else:
                # Cache expired
                del self._cache[key]
                logger.debug(f"⏰ Cache expired: {key}")
        return None
    
    def _set_cache(self, key: str, data: Dict[str, Any]):
        """Store data in cache with timestamp"""
        import time
        self._cache[key] = (data, time.time())
        logger.debug(f"💾 Cached: {key}")
    
    def _invalidate_cache(self, key: str):
        """Remove cached data after write operations"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"🗑️ Cache invalidated: {key}")
    
    async def _call_api(self, action: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call Freedom Wallet API via POST with authentication
        
        Args:
            action: API action (ping, getBalance, addTransaction, etc.)
            data: Additional data to send
        
        Returns:
            API response as dict
        """
        payload = {
            "action": action,
            "spreadsheet_id": self.spreadsheet_id,
            "api_key": SHEETS_API_KEY  # Authentication (Phase 1.5)
        }
        
        if data:
            payload.update(data)
        
        # ✅ Changed to INFO level for visibility
        logger.info(f"📤 API Call: action={action}")
        logger.info(f"   🌐 URL: {self.api_url}")
        logger.info(f"   📦 Payload keys: {list(payload.keys())}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)  # ✅ Increased to 60s for slow Google Apps Script
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"📥 API Response SUCCESS: {result.get('success')}, action={action}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"API error {response.status}: {error_text[:500]}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text[:200]}"
                        }
        except aiohttp.ClientError as e:
            error_type = type(e).__name__
            logger.error(f"Network error calling API ({error_type}): {e}")
            
            # Provide specific error messages
            if "TimeoutError" in error_type or "ServerTimeoutError" in error_type:
                return {
                    "success": False,
                    "error": "Google Sheets phản hồi quá lâu (>60s). Vui lòng thử lại sau."
                }
            else:
                return {
                    "success": False,
                    "error": f"Lỗi kết nối: {str(e)[:100]}"
                }
        except Exception as e:
            logger.error(f"Unexpected error calling API: {e}", exc_info=True)  # ✅ Added traceback
            return {
                "success": False,
                "error": f"Lỗi không xác định: {str(e)[:100]}"
            }
    
    async def ping(self) -> Dict[str, Any]:
        """
        Test connection to Sheets
        
        Returns:
            {"success": True, "message": "...", "timestamp": "..."}
        """
        return await self._call_api("ping")
    
    async def get_balance(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get balance of all jars and accounts (with caching)
        
        Args:
            use_cache: If True, return cached data if available (default: True)
        
        Returns:
            {
                "success": True,
                "jars": [...],
                "accounts": [...],
                "totalBalance": 1234567890
            }
        """
        # Check cache first
        if use_cache:
            cached = self._get_cache('balance')
            if cached:
                return cached
        
        # Cache miss - call API
        logger.debug("📡 API call: getBalance")
        result = await self._call_api("getBalance")
        
        # Store in cache if successful
        if result.get('success'):
            self._set_cache('balance', result)
        
        return result
    
    async def add_transaction(
        self,
        amount: float,
        category: str,
        note: str = "",
        transaction_date: Optional[str] = None,
        transaction_type: str = "Chi",
        from_jar: str = "NEC",
        from_account: str = "Cash",
        to_account: str = ""
    ) -> Dict[str, Any]:
        """
        Add a single transaction
        
        Args:
            amount: Transaction amount (positive)
            category: Transaction category
            note: Transaction note/description
            transaction_date: Date in ISO format (default: today)
            transaction_type: "Chi" or "Thu" (default: "Chi")
            from_jar: Source jar ID (default: NEC)
            from_account: Source account (default: Cash)
            to_account: Destination account (optional, for transfers)
        
        Returns:
            {"success": True, "message": "...", "transactionId": "..."}
        """
        if transaction_date is None:
            transaction_date = datetime.now().strftime("%Y-%m-%d")
        
        transaction = {
            "date": transaction_date,
            "type": transaction_type,  # ✅ FIX: Use parameter instead of hardcoded
            "amount": abs(amount),
            "category": category,
            "fromJar": from_jar,
            "fromAccount": from_account,
            "toAccount": to_account,
            "note": note
        }
        
        # Invalidate balance cache after write
        self._invalidate_cache('balance')
        
        return await self._call_api("addTransaction", {"data": transaction})
    
    async def add_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add multiple transactions in batch
        
        Args:
            transactions: List of transaction dicts
        
        Returns:
            {"success": True, "message": "...", "count": 5}
        """
        return await self._call_api("addTransactions", {"data": transactions})
    
    async def get_recent_transactions(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get recent transactions
        
        Args:
            limit: Number of transactions to retrieve
        
        Returns:
            {
                "success": True,
                "transactions": [...],
                "count": 10
            }
        """
        return await self._call_api("getTransactions", {"data": {"limit": limit}})
    
    async def get_categories(self) -> Dict[str, Any]:
        """
        Get all categories from sheet
        
        Returns:
            {
                "success": True,
                "categories": [
                    {
                        "id": "CAT001",
                        "name": "Ăn uống",
                        "type": "Chi",
                        "icon": "🍽️",
                        "jarId": "NEC",
                        "autoAllocate": False,
                        "note": "..."
                    },
                    ...
                ],
                "count": 50
            }
        """
        return await self._call_api("getCategories")


def extract_spreadsheet_id(url_or_id: str) -> Optional[str]:
    """
    Extract spreadsheet ID from URL or return ID if already valid
    
    Args:
        url_or_id: Google Sheets URL or spreadsheet ID
    
    Returns:
        Spreadsheet ID or None if invalid
    
    Examples:
        >>> extract_spreadsheet_id("https://docs.google.com/spreadsheets/d/1ABC.../edit")
        "1ABC..."
        >>> extract_spreadsheet_id("1ABC...")
        "1ABC..."
    """
    import re
    
    # Already an ID (alphanumeric + _ - only)
    if re.match(r'^[a-zA-Z0-9_-]+$', url_or_id) and len(url_or_id) > 20:
        return url_or_id
    
    # Extract from URL
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url_or_id)
    if match:
        return match.group(1)
    
    return None


async def test_sheets_connection(spreadsheet_id: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Test connection to a spreadsheet
    
    Args:
        spreadsheet_id: Google Sheets ID
    
    Returns:
        (success, message, data)
        - success: True if connection OK
        - message: User-friendly message
        - data: Balance data if successful
    """
    client = SheetsAPIClient(spreadsheet_id)
    
    # Test ping first
    ping_result = await client.ping()
    if not ping_result.get("success"):
        return False, f"❌ Không thể kết nối: {ping_result.get('error', 'Unknown error')}", None
    
    # Get balance to verify data access
    balance_result = await client.get_balance()
    if not balance_result.get("success"):
        return False, f"❌ Không thể đọc dữ liệu: {balance_result.get('error', 'Unknown error')}", None
    
    # Success!
    total = balance_result.get("totalBalance", 0)
    jar_count = len(balance_result.get("jars", []))
    
    message = f"✅ Kết nối thành công!\n\n"
    message += f"💰 Tổng số dư: {total:,.0f} ₫\n"
    message += f"🏺 Số hũ: {jar_count}\n"
    
    return True, message, balance_result

