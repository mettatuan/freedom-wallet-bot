"""
Google Sheets Reader - Premium Feature
Read user's financial data from their Google Sheets
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, Dict, List
from loguru import logger
from datetime import datetime, date
import os


class SheetsReader:
    """Read data from user's Google Sheets (View-only access)"""
    
    # Scopes: Only READ permission (user shares as Viewer)
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    
    def __init__(self, spreadsheet_id: str):
        """
        Initialize Sheets Reader
        
        Args:
            spreadsheet_id: User's Google Sheets ID (44 chars)
        """
        self.spreadsheet_id = spreadsheet_id
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Sheets API service"""
        try:
            creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'google_service_account.json')
            creds = Credentials.from_service_account_file(creds_path, scopes=self.SCOPES)
            self.service = build('sheets', 'v4', credentials=creds)
            logger.info(f"✅ Sheets service initialized for {self.spreadsheet_id[:10]}...")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Sheets service: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """
        Test if bot can access the spreadsheet
        
        Returns:
            bool: True if accessible, False otherwise
        """
        try:
            # Get spreadsheet metadata (lighter than reading cells)
            # This verifies: 1) Spreadsheet exists, 2) Service account has access
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_names = [sheet['properties']['title'] for sheet in spreadsheet.get('sheets', [])]
            logger.info(f"✅ Connection test successful: {self.spreadsheet_id[:10]}...")
            logger.info(f"📊 Found sheets: {', '.join(sheet_names)}")
            return True
            
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning(f"⚠️ Permission denied: User hasn't shared with service account")
            elif e.resp.status == 404:
                logger.warning(f"⚠️ Spreadsheet not found: Invalid ID")
            else:
                logger.error(f"❌ HTTP Error {e.resp.status}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    async def get_balance_summary(self) -> Optional[Dict]:
        """
        Get 6 Jars balance summary
        
        Returns:
            Dict with jar names and balances, or None if error
        """
        try:
            # Read from "Dashboard" sheet, cells with jar balances
            # Assuming structure:
            # A2: Necessities, B2: Balance
            # A3: Education, B3: Balance
            # ... etc
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Dashboard!A2:B7'  # 6 jars
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return None
            
            jars = {}
            for row in values:
                if len(row) >= 2:
                    jar_name = row[0].strip()
                    balance = self._parse_number(row[1])
                    jars[jar_name] = balance
            
            logger.info(f"📊 Retrieved balance for {len(jars)} jars")
            return jars
            
        except Exception as e:
            logger.error(f"❌ Failed to get balance summary: {e}")
            return None
    
    async def get_recent_transactions(self, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get recent transactions
        
        Args:
            limit: Number of transactions to retrieve
        
        Returns:
            List of transaction dicts, or None if error
        """
        try:
            # Read from "Transactions" sheet
            # Assuming columns: Date, Category, Amount, Jar, Note, Method
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Transactions!A2:F100'  # Header in row 1, data from row 2
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []
            
            transactions = []
            for row in values[:limit]:  # Take only last N transactions
                if len(row) >= 3:  # At least Date, Category, Amount
                    txn = {
                        'date': row[0] if len(row) > 0 else '',
                        'category': row[1] if len(row) > 1 else '',
                        'amount': self._parse_number(row[2]) if len(row) > 2 else 0,
                        'jar': row[3] if len(row) > 3 else '',
                        'note': row[4] if len(row) > 4 else '',
                        'method': row[5] if len(row) > 5 else ''
                    }
                    transactions.append(txn)
            
            logger.info(f"📝 Retrieved {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            logger.error(f"❌ Failed to get transactions: {e}")
            return None
    
    async def get_monthly_spending(self, year: int = None, month: int = None) -> Optional[Dict]:
        """
        Get monthly spending by category
        
        Args:
            year: Target year (default: current year)
            month: Target month (default: current month)
        
        Returns:
            Dict with categories and amounts, or None if error
        """
        if not year:
            year = date.today().year
        if not month:
            month = date.today().month
        
        try:
            # Read all transactions
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Transactions!A2:C1000'  # Date, Category, Amount
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return {}
            
            # Filter by month and aggregate
            spending_by_category = {}
            for row in values:
                if len(row) >= 3:
                    # Parse date (assuming format: dd/mm/yyyy or yyyy-mm-dd)
                    txn_date = self._parse_date(row[0])
                    if txn_date and txn_date.year == year and txn_date.month == month:
                        category = row[1].strip()
                        amount = abs(self._parse_number(row[2]))  # Absolute value
                        
                        if category in spending_by_category:
                            spending_by_category[category] += amount
                        else:
                            spending_by_category[category] = amount
            
            logger.info(f"💰 Monthly spending: {len(spending_by_category)} categories")
            return spending_by_category
            
        except Exception as e:
            logger.error(f"❌ Failed to get monthly spending: {e}")
            return None
    
    async def get_total_balance(self) -> Optional[float]:
        """
        Get total balance across all jars
        
        Returns:
            Float total balance, or None if error
        """
        jars = await self.get_balance_summary()
        if not jars:
            return None
        
        total = sum(jars.values())
        logger.info(f"💵 Total balance: {total:,.0f}")
        return total
    
    # Helper methods
    
    def _parse_number(self, value: str) -> float:
        """Parse number from string (handles commas, currency symbols)"""
        if not value:
            return 0.0
        
        try:
            # Remove currency symbols, commas, spaces
            cleaned = str(value).replace(',', '').replace('₫', '').replace('VND', '').strip()
            return float(cleaned)
        except:
            return 0.0
    
    def _parse_date(self, value: str) -> Optional[date]:
        """Parse date from string"""
        if not value:
            return None
        
        try:
            # Try common formats
            for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    return datetime.strptime(value, fmt).date()
                except:
                    continue
            return None
        except:
            return None


# Example premium command using SheetsReader
async def get_user_sheets_reader(user_id: int) -> Optional[SheetsReader]:
    """
    Get SheetsReader instance for a Premium user
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        SheetsReader instance, or None if not configured
    """
    from app.utils.database import get_user_by_id
    
    user = await get_user_by_id(user_id)
    if not user or not user.spreadsheet_id:
        return None
    
    return SheetsReader(user.spreadsheet_id)

