"""Google Sheets adapter for spreadsheet operations."""

from typing import Optional, List, Dict, Any
import gspread
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound, APIError
from oauth2client.service_account import ServiceAccountCredentials
import logging

logger = logging.getLogger(__name__)


class GoogleSheetsAdapter:
    """Adapter for Google Sheets API."""
    
    def __init__(self, credentials_file: str):
        """
        Initialize Google Sheets adapter.
        
        Args:
            credentials_file: Path to service account JSON credentials
        """
        self.credentials_file = credentials_file
        self._client: Optional[gspread.Client] = None
    
    def _get_client(self) -> gspread.Client:
        """Get or create Google Sheets client."""
        if self._client is None:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, 
                scope
            )
            self._client = gspread.authorize(creds)
        
        return self._client
    
    async def get_spreadsheet(self, sheet_url: str) -> Optional[Any]:
        """
        Get spreadsheet by URL.
        
        Args:
            sheet_url: Google Sheets URL
            
        Returns:
            Spreadsheet object or None if not found
        """
        try:
            client = self._get_client()
            return client.open_by_url(sheet_url)
        except (SpreadsheetNotFound, APIError) as e:
            logger.error(f"Failed to get spreadsheet {sheet_url}: {e}")
            return None
    
    async def create_worksheet(
        self, 
        sheet_url: str, 
        title: str, 
        rows: int = 100, 
        cols: int = 20
    ) -> bool:
        """
        Create new worksheet in spreadsheet.
        
        Args:
            sheet_url: Google Sheets URL
            title: Worksheet title
            rows: Number of rows
            cols: Number of columns
            
        Returns:
            True if created successfully, False otherwise
        """
        try:
            spreadsheet = await self.get_spreadsheet(sheet_url)
            if not spreadsheet:
                return False
            
            spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)
            logger.info(f"Created worksheet '{title}' in {sheet_url}")
            return True
        except APIError as e:
            logger.error(f"Failed to create worksheet '{title}': {e}")
            return False
    
    async def get_worksheet(self, sheet_url: str, worksheet_name: str) -> Optional[Any]:
        """
        Get worksheet by name.
        
        Args:
            sheet_url: Google Sheets URL
            worksheet_name: Worksheet name
            
        Returns:
            Worksheet object or None
        """
        try:
            spreadsheet = await self.get_spreadsheet(sheet_url)
            if not spreadsheet:
                return None
            
            return spreadsheet.worksheet(worksheet_name)
        except (WorksheetNotFound, APIError) as e:
            logger.error(f"Failed to get worksheet '{worksheet_name}': {e}")
            return None
    
    async def append_row(
        self, 
        sheet_url: str, 
        worksheet_name: str, 
        values: List[Any]
    ) -> bool:
        """
        Append row to worksheet.
        
        Args:
            sheet_url: Google Sheets URL
            worksheet_name: Worksheet name
            values: List of cell values
            
        Returns:
            True if appended successfully, False otherwise
        """
        try:
            worksheet = await self.get_worksheet(sheet_url, worksheet_name)
            if not worksheet:
                return False
            
            worksheet.append_row(values)
            logger.info(f"Appended row to '{worksheet_name}' in {sheet_url}")
            return True
        except APIError as e:
            logger.error(f"Failed to append row to '{worksheet_name}': {e}")
            return False
    
    async def update_cell(
        self, 
        sheet_url: str, 
        worksheet_name: str, 
        row: int, 
        col: int, 
        value: Any
    ) -> bool:
        """
        Update single cell.
        
        Args:
            sheet_url: Google Sheets URL
            worksheet_name: Worksheet name
            row: Row number (1-indexed)
            col: Column number (1-indexed)
            value: Cell value
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            worksheet = await self.get_worksheet(sheet_url, worksheet_name)
            if not worksheet:
                return False
            
            worksheet.update_cell(row, col, value)
            logger.info(f"Updated cell ({row}, {col}) in '{worksheet_name}'")
            return True
        except APIError as e:
            logger.error(f"Failed to update cell ({row}, {col}): {e}")
            return False
    
    async def get_all_values(
        self, 
        sheet_url: str, 
        worksheet_name: str
    ) -> Optional[List[List[Any]]]:
        """
        Get all values from worksheet.
        
        Args:
            sheet_url: Google Sheets URL
            worksheet_name: Worksheet name
            
        Returns:
            List of rows (each row is list of values) or None
        """
        try:
            worksheet = await self.get_worksheet(sheet_url, worksheet_name)
            if not worksheet:
                return None
            
            return worksheet.get_all_values()
        except APIError as e:
            logger.error(f"Failed to get all values from '{worksheet_name}': {e}")
            return None
    
    async def get_range(
        self, 
        sheet_url: str, 
        worksheet_name: str, 
        range_name: str
    ) -> Optional[List[List[Any]]]:
        """
        Get values from specific range.
        
        Args:
            sheet_url: Google Sheets URL
            worksheet_name: Worksheet name
            range_name: Range in A1 notation (e.g., 'A1:B10')
            
        Returns:
            List of rows in range or None
        """
        try:
            worksheet = await self.get_worksheet(sheet_url, worksheet_name)
            if not worksheet:
                return None
            
            return worksheet.get(range_name)
        except APIError as e:
            logger.error(f"Failed to get range '{range_name}' from '{worksheet_name}': {e}")
            return None
    
    async def batch_update(
        self, 
        sheet_url: str, 
        worksheet_name: str, 
        updates: List[Dict[str, Any]]
    ) -> bool:
        """
        Batch update multiple cells.
        
        Args:
            sheet_url: Google Sheets URL
            worksheet_name: Worksheet name
            updates: List of update dictionaries with 'range' and 'values' keys
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            worksheet = await self.get_worksheet(sheet_url, worksheet_name)
            if not worksheet:
                return False
            
            worksheet.batch_update(updates)
            logger.info(f"Batch updated {len(updates)} ranges in '{worksheet_name}'")
            return True
        except APIError as e:
            logger.error(f"Failed to batch update '{worksheet_name}': {e}")
            return False
    
    async def clear_worksheet(self, sheet_url: str, worksheet_name: str) -> bool:
        """
        Clear all data from worksheet.
        
        Args:
            sheet_url: Google Sheets URL
            worksheet_name: Worksheet name
            
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            worksheet = await self.get_worksheet(sheet_url, worksheet_name)
            if not worksheet:
                return False
            
            worksheet.clear()
            logger.info(f"Cleared worksheet '{worksheet_name}'")
            return True
        except APIError as e:
            logger.error(f"Failed to clear worksheet '{worksheet_name}': {e}")
            return False
    
    async def delete_worksheet(self, sheet_url: str, worksheet_name: str) -> bool:
        """
        Delete worksheet from spreadsheet.
        
        Args:
            sheet_url: Google Sheets URL
            worksheet_name: Worksheet name
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            spreadsheet = await self.get_spreadsheet(sheet_url)
            if not spreadsheet:
                return False
            
            worksheet = spreadsheet.worksheet(worksheet_name)
            spreadsheet.del_worksheet(worksheet)
            logger.info(f"Deleted worksheet '{worksheet_name}'")
            return True
        except (WorksheetNotFound, APIError) as e:
            logger.error(f"Failed to delete worksheet '{worksheet_name}': {e}")
            return False
