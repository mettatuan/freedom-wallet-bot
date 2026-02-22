"""
Save user registration to Google Sheet
Sheet: https://docs.google.com/spreadsheets/d/1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg/edit
"""

import gspread
from datetime import datetime
from loguru import logger


REGISTRATION_SHEET_ID = "1-fruHaSlCKIOpIfU5Qrkns0ze3bx3E-mKUgQ5fUF-Hg"
WORKSHEET_NAME = "FreedomWallet_Registrations"


def get_registration_worksheet():
    """Get the registration worksheet — uses google-auth (not oauth2client)"""
    try:
        # Try google-auth (modern, works with Python 3.12+)
        try:
            from google.oauth2.service_account import Credentials
            scopes = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = Credentials.from_service_account_file(
                'google_service_account.json',
                scopes=scopes
            )
            client = gspread.authorize(creds)
        except ImportError:
            # Fallback to oauth2client if available
            from oauth2client.service_account import ServiceAccountCredentials
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'google_service_account.json', scope
            )
            client = gspread.authorize(creds)

        spreadsheet = client.open_by_key(REGISTRATION_SHEET_ID)
        worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
        return worksheet

    except Exception as e:
        logger.error(f"Error accessing registration sheet: {e}")
        return None



async def find_user_in_sheet_by_referral_code(referral_code: str):
    """
    Find a registration row by referral code (column H: 🔗 Link giới thiệu).
    Used when user arrives via deep link WEB_<code>.
    Returns dict with row data, or None if not found.
    """
    try:
        worksheet = get_registration_worksheet()
        if not worksheet:
            return None

        all_values = worksheet.get_all_values()
        if len(all_values) < 2:
            return None

        for idx, row in enumerate(all_values[1:], start=2):  # Skip header
            row_code = row[7].strip() if len(row) > 7 else ""
            if row_code == referral_code:
                logger.info(f"✅ Found row by referral code '{referral_code}' at row {idx}")
                referral_count_raw = row[8].strip() if len(row) > 8 else "0"
                try:
                    referral_count = int(referral_count_raw) if referral_count_raw.isdigit() else 0
                except (ValueError, AttributeError):
                    referral_count = 0
                return {
                    "row_index":      idx,
                    "full_name":      row[3].strip() if len(row) > 3 else "",
                    "email":          row[4].strip() if len(row) > 4 else "",
                    "phone":          row[5].strip() if len(row) > 5 else "",
                    "plan":           row[6].strip() if len(row) > 6 else "FREE",
                    "referral_code":  row_code,
                    "referral_count": referral_count,
                    "source":         row[9].strip()  if len(row) > 9  else "Landing Page",
                    "status":         row[10].strip() if len(row) > 10 else "",
                    "referred_by":    row[11].strip() if len(row) > 11 else "",
                }

        logger.info(f"❌ Referral code '{referral_code}' not found in registration sheet")
        return None

    except Exception as e:
        logger.error(f"Error in find_user_in_sheet_by_referral_code: {e}", exc_info=True)
        return None


async def find_user_in_sheet_by_email(email: str):
    """
    Find a registration row directly by email address.
    Returns dict with row data, or None if not found.
    """
    try:
        worksheet = get_registration_worksheet()
        if not worksheet:
            return None

        all_values = worksheet.get_all_values()
        if len(all_values) < 2:
            return None

        for idx, row in enumerate(all_values[1:], start=2):  # Skip header
            row_email = row[4].strip() if len(row) > 4 else ""
            if row_email.lower() == email.lower():
                logger.info(f"✅ Found row by email '{email}' at row {idx}")
                referral_count_raw = row[8].strip() if len(row) > 8 else "0"
                try:
                    referral_count = int(referral_count_raw) if referral_count_raw.isdigit() else 0
                except (ValueError, AttributeError):
                    referral_count = 0
                return {
                    "row_index":      idx,
                    "full_name":      row[3].strip() if len(row) > 3 else "",
                    "email":          row_email,
                    "phone":          row[5].strip() if len(row) > 5 else "",
                    "plan":           row[6].strip() if len(row) > 6 else "FREE",
                    "referral_code":  row[7].strip() if len(row) > 7 else "",
                    "referral_count": referral_count,
                    "source":         row[9].strip()  if len(row) > 9  else "Landing Page",
                    "status":         row[10].strip() if len(row) > 10 else "",
                    "referred_by":    row[11].strip() if len(row) > 11 else "",
                }

        logger.info(f"❌ Email '{email}' not found in registration sheet")
        return None

    except Exception as e:
        logger.error(f"Error in find_user_in_sheet_by_email: {e}", exc_info=True)
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
        
        # Check if user already exists — by User ID first, then by Email
        all_values = worksheet.get_all_values()
        user_exists = False
        user_row = None

        # Pass 1: search by Telegram User ID (column B, index 1)
        for idx, row in enumerate(all_values[1:], start=2):  # Skip header
            if len(row) > 1 and str(row[1]).strip() == str(user_id):
                user_exists = True
                user_row = idx
                logger.info(f"🔍 Found existing row by User ID at row {user_row}")
                break

        # Pass 2: if not found by ID, search by Email (column E, index 4)
        # This handles landing-page rows that have no Telegram ID yet
        if not user_exists and email:
            for idx, row in enumerate(all_values[1:], start=2):
                row_email = row[4].strip() if len(row) > 4 else ""
                row_user_id = row[1].strip() if len(row) > 1 else ""
                if row_email.lower() == email.lower() and row_user_id == "":
                    # Match by email on a row that has no Telegram ID yet
                    user_exists = True
                    user_row = idx
                    logger.info(f"🔍 Found existing landing-page row by email at row {user_row} — will update with TG data")
        
        # Prepare row data
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if user_exists and user_row:
            # Preserve original registration date from landing page
            original_row = all_values[user_row - 1]  # 0-indexed
            original_date = original_row[0] if original_row else now_str
            row_data = [
                original_date,                  # 📅 Ngày đăng ký — keep original
                str(user_id),                   # User ID (filled from Telegram)
                username or "",                 # Username (filled from Telegram)
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
            worksheet.update(f'A{user_row}:L{user_row}', [row_data])
            logger.info(f"✅ Updated user {user_id} in registration sheet (row {user_row}), kept original date: {original_date}")
        else:
            row_data = [
                now_str,                        # 📅 Ngày đăng ký — new registration
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
            # Append new row
            worksheet.append_row(row_data)
            logger.info(f"✅ Added new user {user_id} to registration sheet")
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving to registration sheet: {e}", exc_info=True)
        return False
