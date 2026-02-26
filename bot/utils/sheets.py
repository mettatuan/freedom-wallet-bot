"""
Google Sheets Integration
Sync user registration data to Google Sheets
"""
import logging
import gspread
from google.oauth2.service_account import Credentials
from config.settings import settings
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger(__name__)


# Google Sheets scope
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def generate_email_hash(email: str) -> str:
    """
    Generate hash from email (same algorithm as JavaScript version)
    Used for WEB_* deep links
    """
    hash_value = 0
    for char in email:
        hash_value = ((hash_value << 5) - hash_value) + ord(char)
        hash_value = hash_value & 0xFFFFFFFF  # Keep it 32-bit
    
    # Convert to base36 and uppercase, limit to 8 chars (NO PADDING!)
    result = abs(hash_value)
    base36 = ''
    while result > 0:
        result, remainder = divmod(result, 36)
        if remainder < 10:
            base36 = chr(48 + remainder) + base36  # 0-9
        else:
            base36 = chr(55 + remainder) + base36  # A-Z
    
    # Return first 8 chars uppercase, NO padding (to match JavaScript)
    return base36[:8].upper() if base36 else "0"


def get_sheets_client():
    """Initialize Google Sheets client"""
    try:
        import os
        # Resolve path relative to project root
        creds_path = settings.GOOGLE_SHEETS_CREDENTIALS
        if not os.path.isabs(creds_path):
            # If relative path, resolve from project root (2 levels up from this file)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            creds_path = os.path.join(project_root, creds_path)
        
        creds = Credentials.from_service_account_file(
            creds_path,
            scopes=SCOPES
        )
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Error initializing sheets client: {e}", exc_info=True)
        return None


async def sync_user_to_sheet(user_id: int, email: str, phone: str = None, full_name: str = None):
    """
    Sync user registration data to Google Sheets
    Sheet structure: Telegram ID | Full Name | Email | Phone | Registered Date | Referral Code
    """
    try:
        client = get_sheets_client()
        if not client:
            logger.warning("Sheets client not initialized. Skipping sync.")
            return False
        
        # Open the spreadsheet (use SUPPORT_SHEET_ID or specific registration sheet)
        sheet_id = settings.SUPPORT_SHEET_ID
        if not sheet_id:
            logger.warning("No sheet ID configured")
            return False
        
        spreadsheet = client.open_by_key(sheet_id)
        
        # Try to get "User Registrations" worksheet, create if not exists
        try:
            worksheet = spreadsheet.worksheet("User Registrations")
        except:
            worksheet = spreadsheet.add_worksheet(title="User Registrations", rows=1000, cols=10)
            # Add headers
            worksheet.update('A1:G1', [[
                'Telegram ID', 'Họ Tên', 'Email', 'Số Điện Thoại', 
                'Ngày Đăng Ký', 'Trạng Thái', 'Ghi Chú'
            ]])
        
        # Check if user already exists
        cell = worksheet.find(str(user_id), in_column=1)
        
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [
            str(user_id),
            full_name or '',
            email or '',
            phone or '',
            timestamp,
            'Active',
            'Registered via Bot'
        ]
        
        if cell:
            # Update existing row
            row_num = cell.row
            worksheet.update(f'A{row_num}:G{row_num}', [row_data])
        else:
            # Append new row
            worksheet.append_row(row_data)
        
        logger.info(f"Synced user {user_id} to Google Sheets")
        return True
        
    except Exception as e:
        logger.error(f"Error syncing to sheets: {e}")
        return False


async def send_welcome_email(email: str, full_name: str, template_link: str):
    """
    Send welcome email with template link
    (Optional - can integrate with SendGrid/Mailgun later)
    """
    # TODO: Implement email sending
    # For now, just log
    logger.info(f"Would send email to {email} with template: {template_link}")
    pass


async def find_user_in_sheet_by_email_hash(email_hash: str) -> Optional[Dict]:
    """
    Find user in Google Sheets by email hash
    Returns user data if found, None otherwise
    
    Sheet structure: Timestamp | Full Name | Email | Phone | Plan | Source | Status | Referral Code | Referrer
    """
    try:
        client = get_sheets_client()
        if not client:
            logger.error("Sheets client not initialized. Check GOOGLE_SHEETS_CREDENTIALS in .env")
            return None
        
        sheet_id = settings.REGISTRATION_SHEET_ID or settings.SUPPORT_SHEET_ID
        if not sheet_id:
            logger.error("No registration sheet ID configured. Set ADMIN_SUPPORT_SHEET_ID in .env")
            return None
        
        # Validate Sheet ID format
        if len(sheet_id) < 20 or ' ' in sheet_id:
            logger.error(f"Invalid Sheet ID format: {sheet_id} (should be ~40 chars)")
            return None
        
        logger.info(f"Opening sheet: {sheet_id[:20]}...")
        
        try:
            spreadsheet = client.open_by_key(sheet_id)
        except PermissionError:
            logger.error(
                f"PERMISSION DENIED for sheet {sheet_id}. "
                f"Share it with: eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com"
            )
            return None
        
        # Check multiple possible worksheet names
        worksheet_names = ["FreedomWallet_Registrations", "Freedom Wallet Registrations", "Registrations", "Sheet1", "Form Responses 1"]
        worksheet = None
        
        for name in worksheet_names:
            try:
                worksheet = spreadsheet.worksheet(name)
                logger.info(f"Found worksheet: {name}")
                break
            except:
                continue
        
        if not worksheet:
            logger.error("No registration worksheet found")
            return None
        
        # Get all records
        records = worksheet.get_all_records()
        logger.info(f"Found {len(records)} records in worksheet")
        
        if records:
            logger.debug(f"Column names: {list(records[0].keys())}")
        
        # Search for user by referral code
        logger.info(f"Looking for referral code: {email_hash}")
        for record in records:
            referral_code = record.get('🔗 Link giới thiệu', record.get('Link giới thiệu', record.get('Referral Code', record.get('🔗 Link giới thiệu ', ''))))
            email = record.get('📧 Email', record.get('Email', ''))
            
            if referral_code == email_hash:
                logger.info(f"Match found by referral code: {email}")
                
                referral_count_str = str(record.get('👥 Số người đã giới thiệu', record.get('Số người đã giới thiệu', '0')))
                try:
                    referral_count = int(referral_count_str) if referral_count_str.strip() else 0
                except (ValueError, AttributeError):
                    referral_count = 0
                
                return {
                    'full_name': record.get('Họ & Tên', record.get('Họ tên', record.get('Full Name', record.get('fullName', '')))),
                    'email': email,
                    'phone': record.get('👤 Điện thoại', record.get('Số điện thoại', record.get('Phone', record.get('phone', '')))),
                    'plan': record.get('💎 Gói', record.get('Gói', record.get('Plan', record.get('plan', 'FREE')))),
                    'timestamp': record.get('📅 Ngày đăng ký', record.get('Timestamp', record.get('timestamp', ''))),
                    'referral_count': referral_count,
                }
        
        logger.warning(f"No user found with referral code: {email_hash}")
        return None
        
    except Exception as e:
        logger.error(f"Error finding user in sheets: {e}", exc_info=True)
        return None


async def sync_web_registration(telegram_id: int, telegram_username: str, email_hash: str) -> Optional[Dict]:
    """
    Sync user from web registration (Google Sheets) to bot database
    
    1. Find user in Sheets by email hash
    2. Return user data for bot to create/update user record
    
    Returns user data if found, None otherwise
    """
    try:
        # Find user in sheets
        user_data = await find_user_in_sheet_by_email_hash(email_hash)
        
        if not user_data:
            logger.warning(f"No web registration found for email hash: {email_hash}")
            return None
        
        # Add telegram info
        user_data['telegram_id'] = telegram_id
        user_data['telegram_username'] = telegram_username
        user_data['source'] = 'WEB'
        user_data['is_registered'] = True
        
        logger.info(f"Synced web registration for Telegram ID {telegram_id}: {user_data['email']}")
        return user_data
        
    except Exception as e:
        logger.error(f"Error syncing web registration: {e}", exc_info=True)
        return None
