"""
Save user registration to Google Sheet
Sheet: https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from loguru import logger


REGISTRATION_SHEET_ID = "1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg"
WORKSHEET_NAME = "FreedomWallet_Registrations"


def get_registration_worksheet():
    """Get the registration worksheet"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            'google_service_account.json',
            scope
        )
        
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(REGISTRATION_SHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        
        return worksheet
        
    except Exception as e:
        logger.error(f"Error accessing registration sheet: {e}")
        return None


async def save_user_to_registration_sheet(
    user_id: int,
    username: str,
    full_name: str,
    email: str,
    phone: str,
    plan: str,
    referral_link: str,
    referral_count: int,
    source: str,
    status: str,
    referred_by: str = None
):
    """
    Save user to registration Google Sheet
    
    Columns:
    📅 Ngày đăng ký | User ID | Username | Họ & Tên | 📧 Email | 👤 Điện thoại | 
    💎 Gói | 🔗 Link giới thiệu | 👥 Số người đã giới thiệu | 📍 Nguồn | 📊 Trạng thái | 👤 Người giới thiệu
    """
    try:
        worksheet = get_registration_worksheet()
        if not worksheet:
            logger.error("Could not access registration worksheet")
            return False
        
        # Check if user already exists
        all_values = worksheet.get_all_values()
        user_exists = False
        user_row = None
        
        for idx, row in enumerate(all_values[1:], start=2):  # Skip header
            if len(row) > 1 and str(row[1]) == str(user_id):  # Column B (User ID)
                user_exists = True
                user_row = idx
                break
        
        # Prepare row data
        registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [
            registration_date,              # 📅 Ngày đăng ký
            str(user_id),                   # User ID
            username or "",                 # Username
            full_name or "",                # Họ & Tên
            email or "",                    # 📧 Email
            phone or "",                    # 👤 Điện thoại
            plan,                           # 💎 Gói
            referral_link,                  # 🔗 Link giới thiệu
            str(referral_count),            # 👥 Số người đã giới thiệu
            source,                         # 📍 Nguồn
            status,                         # 📊 Trạng thái
            referred_by or ""               # 👤 Người giới thiệu
        ]
        
        if user_exists:
            # Update existing row
            worksheet.update(f'A{user_row}:L{user_row}', [row_data])
            logger.info(f"✅ Updated user {user_id} in registration sheet (row {user_row})")
        else:
            # Append new row
            worksheet.append_row(row_data)
            logger.info(f"✅ Added new user {user_id} to registration sheet")
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving to registration sheet: {e}", exc_info=True)
        return False
