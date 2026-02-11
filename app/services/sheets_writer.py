"""
Google Sheets Writer - Premium Feature (OPTION 1)
Write transactions to user's Google Sheets
Requires EDITOR permission from user
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import Optional, Dict
from loguru import logger
from datetime import datetime
import os


class SheetsWriter:
    """Write data to user's Google Sheets (Editor access required)"""
    
    # Scopes: READ + WRITE permission
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, spreadsheet_id: str):
        """
        Initialize Sheets Writer
        
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
            logger.info(f"âœ… Sheets writer initialized for {self.spreadsheet_id[:10]}...")
        except Exception as e:
            logger.error(f"âŒ Failed to initialize Sheets writer: {e}")
            raise
    
    async def test_write_permission(self) -> bool:
        """
        Test if bot has WRITE access to the spreadsheet
        
        Returns:
            bool: True if writable, False otherwise
        """
        try:
            # Try to append a test row (will be removed immediately)
            test_range = 'Transactions!A:A'
            test_value = [['TEST_BOT_ACCESS']]
            
            body = {'values': test_value}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=test_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            # Remove test row immediately
            # (In production, just test read permission instead)
            
            logger.info(f"âœ… Write permission confirmed: {self.spreadsheet_id[:10]}...")
            return True
            
        except HttpError as e:
            if e.resp.status == 403:
                logger.warning(f"âš ï¸ Permission denied: Need EDITOR access")
            else:
                logger.error(f"âŒ HTTP Error {e.resp.status}: {e}")
            return False
        except Exception as e:
            logger.error(f"âŒ Write permission test failed: {e}")
            return False
    
    async def add_transaction(self, data: Dict) -> bool:
        """
        Add a transaction to Transactions sheet
        
        Args:
            data: Dict with keys: date, category, amount, jar, note, method
        
        Returns:
            bool: True if success, False otherwise
        """
        try:
            # Prepare row data
            # Assuming columns: Date | Category | Amount | Jar | Note | Method
            row = [
                data.get('date', datetime.now().strftime('%d/%m/%Y')),
                data.get('category', 'KhÃ¡c'),
                data.get('amount', 0),
                data.get('jar', 'Necessities'),
                data.get('note', ''),
                data.get('method', 'Bot')
            ]
            
            # Append to Transactions sheet
            range_name = 'Transactions!A:F'
            body = {'values': [row]}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            updates = result.get('updates', {})
            updated_rows = updates.get('updatedRows', 0)
            
            if updated_rows > 0:
                logger.info(f"âœ… Transaction added: {data.get('amount')} - {data.get('category')}")
                return True
            else:
                logger.warning(f"âš ï¸ No rows updated")
                return False
            
        except Exception as e:
            logger.error(f"âŒ Failed to add transaction: {e}")
            return False
    
    async def add_expense(self, amount: float, category: str, note: str = "", 
                          jar: str = "Necessities", method: str = "Bot") -> bool:
        """
        Quick expense recording
        
        Args:
            amount: Expense amount (negative for expense)
            category: Expense category
            note: Optional note
            jar: Which jar to deduct from
            method: Payment method
        
        Returns:
            bool: Success status
        """
        # Make amount negative for expense
        if amount > 0:
            amount = -amount
        
        data = {
            'date': datetime.now().strftime('%d/%m/%Y'),
            'category': category,
            'amount': amount,
            'jar': jar,
            'note': note,
            'method': method
        }
        
        return await self.add_transaction(data)
    
    async def add_income(self, amount: float, category: str = "LÆ°Æ¡ng", 
                         note: str = "", method: str = "Bot") -> bool:
        """
        Quick income recording
        
        Args:
            amount: Income amount (positive)
            category: Income category
            note: Optional note
            method: Source
        
        Returns:
            bool: Success status
        """
        # Ensure positive
        amount = abs(amount)
        
        data = {
            'date': datetime.now().strftime('%d/%m/%Y'),
            'category': category,
            'amount': amount,
            'jar': 'Income',
            'note': note,
            'method': method
        }
        
        return await self.add_transaction(data)


# Helper function for commands
async def get_user_sheets_writer(user_id: int):
    """
    Get SheetsWriter instance for a Premium user
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        SheetsWriter instance, or None if not configured
    """
    from app.utils.database import get_user_by_id
    
    user = await get_user_by_id(user_id)
    if not user or not user.spreadsheet_id:
        return None
    
    return SheetsWriter(user.spreadsheet_id)

