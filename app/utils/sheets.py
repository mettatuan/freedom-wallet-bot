"""
Google Sheets Integration
Sync user registration data to Google Sheets
"""
import gspread
from google.oauth2.service_account import Credentials
from config.settings import settings
from datetime import datetime
from typing import Optional, Dict


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
        print(f"Error initializing sheets client: {e}")
        import traceback
        traceback.print_exc()
        return None


async def sync_user_to_sheet(user_id: int, email: str, phone: str = None, full_name: str = None):
    """
    Sync user registration data to Google Sheets
    Sheet structure: Telegram ID | Full Name | Email | Phone | Registered Date | Referral Code
    """
    try:
        client = get_sheets_client()
        if not client:
            print("Sheets client not initialized. Skipping sync.")
            return False
        
        # Open the spreadsheet (use SUPPORT_SHEET_ID or specific registration sheet)
        sheet_id = settings.SUPPORT_SHEET_ID
        if not sheet_id:
            print("No sheet ID configured")
            return False
        
        spreadsheet = client.open_by_key(sheet_id)
        
        # Try to get "User Registrations" worksheet, create if not exists
        try:
            worksheet = spreadsheet.worksheet("User Registrations")
        except:
            worksheet = spreadsheet.add_worksheet(title="User Registrations", rows=1000, cols=10)
            # Add headers
            worksheet.update('A1:G1', [[
                'Telegram ID', 'Há» TÃªn', 'Email', 'Sá»‘ Äiá»‡n Thoáº¡i', 
                'NgÃ y ÄÄƒng KÃ½', 'Tráº¡ng ThÃ¡i', 'Ghi ChÃº'
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
        
        print(f"âœ… Synced user {user_id} to Google Sheets")
        return True
        
    except Exception as e:
        print(f"âŒ Error syncing to sheets: {e}")
        return False


async def send_welcome_email(email: str, full_name: str, template_link: str):
    """
    Send welcome email with template link
    (Optional - can integrate with SendGrid/Mailgun later)
    """
    # TODO: Implement email sending
    # For now, just log
    print(f"ðŸ“§ Would send email to {email} with template: {template_link}")
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
            print("âŒ Sheets client not initialized")
            print("   Check: GOOGLE_SHEETS_CREDENTIALS in .env")
            return None
        
        sheet_id = settings.SUPPORT_SHEET_ID
        if not sheet_id:
            print("âŒ No sheet ID configured")
            print("   Fix: Set SUPPORT_SHEET_ID in .env file")
            return None
        
        # Validate Sheet ID format
        if len(sheet_id) < 20 or ' ' in sheet_id:
            print(f"âŒ Invalid Sheet ID format: {sheet_id}")
            print("   Sheet ID should be ~40 characters long")
            print("   Example: 1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg")
            print("   Current: Check SUPPORT_SHEET_ID in .env")
            return None
        
        print(f"ðŸ“„ Opening sheet: {sheet_id}")
        
        try:
            spreadsheet = client.open_by_key(sheet_id)
        except PermissionError:
            print(f"âŒ PERMISSION DENIED for sheet: {sheet_id}")
            print(f"   ")
            print(f"   ðŸ”§ FIX: Share this Google Sheet with service account:")
            print(f"   ðŸ“§ Email: eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com")
            print(f"   ðŸ”— Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
            print(f"   ")
            print(f"   Steps:")
            print(f"   1. Open the sheet URL above")
            print(f"   2. Click 'Share' button")
            print(f"   3. Add the service account email")
            print(f"   4. Set permission to 'Editor'")
            print(f"   5. Uncheck 'Notify people'")
            print(f"   6. Click 'Send'")
            return None
        
        # Check multiple possible worksheet names
        worksheet_names = ["FreedomWallet_Registrations", "Freedom Wallet Registrations", "Registrations", "Sheet1", "Form Responses 1"]
        worksheet = None
        
        for name in worksheet_names:
            try:
                worksheet = spreadsheet.worksheet(name)
                print(f"âœ… Found worksheet: {name}")
                break
            except:
                continue
        
        if not worksheet:
            print("âŒ No registration worksheet found")
            return None
        
        # Get all records
        records = worksheet.get_all_records()
        print(f"ðŸ“Š Found {len(records)} records in worksheet")
        
        # Debug: Show all column names from first record
        if records:
            print(f"ðŸ”‘ Column names: {list(records[0].keys())}")
        
        # Search for user by referral code (stored in "ðŸ”— Link giá»›i thiá»‡u" column)
        print(f"ðŸ” Looking for referral code: {email_hash}")
        for idx, record in enumerate(records, 1):
            # Get referral code from sheet (this is what landing page generates from email)
            referral_code = record.get('ðŸ”— Link giá»›i thiá»‡u', record.get('Link giá»›i thiá»‡u', record.get('Referral Code', record.get('ðŸ”— Link giá»›i thiá»‡u ', ''))))
            
            email = record.get('ðŸ“§ Email', record.get('Email', ''))
            
            print(f"  [{idx}] Email: {email} â†’ Referral Code: {referral_code}")
            
            # Match by referral code (not by email hash!)
            if referral_code == email_hash:
                print(f"âœ… MATCH! Found user by referral code: {email}")
                
                # Get referral count from sheet
                referral_count_str = str(record.get('ðŸ‘¥ Sá»‘ ngÆ°á»i Ä‘Ã£ giá»›i thiá»‡u', record.get('Sá»‘ ngÆ°á»i Ä‘Ã£ giá»›i thiá»‡u', '0')))
                try:
                    referral_count = int(referral_count_str) if referral_count_str.strip() else 0
                except (ValueError, AttributeError):
                    referral_count = 0
                
                print(f"ðŸ“Š Referral count from sheet: {referral_count}")
                
                return {
                    'full_name': record.get('Há» & TÃªn', record.get('Há» tÃªn', record.get('Full Name', record.get('fullName', '')))),
                    'email': email,
                    'phone': record.get('ðŸ‘¤ Äiá»‡n thoáº¡i', record.get('Sá»‘ Ä‘iá»‡n thoáº¡i', record.get('Phone', record.get('phone', '')))),
                    'plan': record.get('ðŸ’Ž GÃ³i', record.get('GÃ³i', record.get('Plan', record.get('plan', 'FREE')))),
                    'timestamp': record.get('ðŸ“… NgÃ y Ä‘Äƒng kÃ½', record.get('Timestamp', record.get('timestamp', ''))),
                    'referral_count': referral_count,
                }
        
        print(f"âŒ No user found with referral code: {email_hash}")
        return None
        
    except Exception as e:
        print(f"âŒ Error finding user in sheets: {e}")
        import traceback
        traceback.print_exc()
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
            print(f"âŒ No web registration found for email hash: {email_hash}")
            return None
        
        # Add telegram info
        user_data['telegram_id'] = telegram_id
        user_data['telegram_username'] = telegram_username
        user_data['source'] = 'WEB'
        user_data['is_registered'] = True
        
        print(f"âœ… Synced web registration for Telegram ID {telegram_id}: {user_data['email']}")
        return user_data
        
    except Exception as e:
        print(f"âŒ Error syncing web registration: {e}")
        import traceback
        traceback.print_exc()
        return None

