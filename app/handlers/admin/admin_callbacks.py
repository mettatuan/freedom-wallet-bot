"""
Admin Callback Handlers - Quick payment approval via buttons
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from app.services.payment_service import PaymentVerificationService
from app.utils.database import get_db, PaymentVerification, User
from app.handlers.admin_payment import is_admin
from datetime import datetime
import html


async def handle_admin_approve_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin approve button click"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await query.edit_message_text(
            text="âŒ Báº¡n khÃ´ng cÃ³ quyá»n thá»±c hiá»‡n thao tÃ¡c nÃ y.",
            parse_mode="HTML"
        )
        return
    
    # Extract verification ID from callback_data
    # Format: admin_approve_VER123
    verification_id = query.data.replace("admin_approve_", "")
    
    try:
        # Approve payment
        success = await PaymentVerificationService.approve_payment(
            verification_id=verification_id,
            approved_by=user_id
        )
        
        if success:
            # Get verification details for Google Sheets logging
            db = next(get_db())
            ver_id = int(verification_id.replace("VER", ""))
            verification = db.query(PaymentVerification).filter(
                PaymentVerification.id == ver_id
            ).first()
            
            user = db.query(User).filter(User.id == verification.user_id).first()
            
            if user and verification:
                # Log to Google Sheets
                await log_payment_to_sheets(
                    verification_id=verification_id,
                    user_id=user.id,
                    username=user.username,
                    full_name=user.full_name,
                    amount=verification.amount,
                    status="APPROVED",
                    approved_by=user_id,
                    approved_at=datetime.now()
                )
            
            db.close()
            
            # Update message with success
            new_caption = f"""
âœ… <b>ÄÃƒ DUYá»†T THÃ€NH CÃ”NG</b>

MÃ£: <code>{verification_id}</code>

âœ… User Ä‘Ã£ Ä‘Æ°á»£c nÃ¢ng cáº¥p lÃªn Premium (365 ngÃ y)
âœ… ThÃ´ng tin Ä‘Ã£ lÆ°u vÃ o Google Sheets
âœ… User Ä‘Ã£ nháº­n thÃ´ng bÃ¡o kÃ­ch hoáº¡t

NgÆ°á»i duyá»‡t: {query.from_user.full_name}
Thá»i gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
            
            # Send notification to user
            try:
                from datetime import timedelta
                expire_date = datetime.now() + timedelta(days=365)
                
                await context.bot.send_message(
                    chat_id=verification.user_id,
                    text=f"""
ðŸŽ‰ <b>CHÃšC Má»ªNG! PREMIUM ÄÃƒ KÃCH HOáº T</b>

MÃ£ xÃ¡c nháº­n: <code>{verification_id}</code>

âœ… GÃ³i Premium Ä‘Ã£ Ä‘Æ°á»£c kÃ­ch hoáº¡t thÃ nh cÃ´ng!
â° Thá»i háº¡n: <b>365 ngÃ y</b> (Ä‘áº¿n {expire_date.strftime('%d/%m/%Y')})

ðŸŽ <b>QUYá»€N Lá»¢I:</b>
ðŸ’¬ KhÃ´ng giá»›i háº¡n tin nháº¯n
ðŸ¤– AI Assistant Premium
ðŸ“Š PhÃ¢n tÃ­ch chi tiÃªu thÃ´ng minh
ðŸŽ¯ Gá»£i Ã½ tÃ i chÃ­nh cÃ¡ nhÃ¢n hÃ³a
ðŸš€ Há»— trá»£ Æ°u tiÃªn 24/7

Gá»­i /start Ä‘á»ƒ khÃ¡m phÃ¡ tÃ­nh nÄƒng Premium!
""",
                    parse_mode="HTML"
                )
            except Exception as notify_error:
                logger.error(f"Failed to notify user {verification.user_id}: {notify_error}")
            
            try:
                await query.edit_message_text(
                    text=new_caption,
                    parse_mode="HTML"
                )
            except Exception as edit_error:
                logger.warning(f"Can't edit message, sending new: {edit_error}")
                await query.message.reply_text(
                    text=new_caption,
                    parse_mode="HTML"
                )
            
        else:
            await query.edit_message_text(
                text=f"âŒ Lá»—i khi duyá»‡t {verification_id}. CÃ³ thá»ƒ Ä‘Ã£ Ä‘Æ°á»£c xá»­ lÃ½ rá»“i.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Error in handle_admin_approve_callback: {e}", exc_info=True)
        await query.answer("âŒ CÃ³ lá»—i xáº£y ra. Vui lÃ²ng thá»­ láº¡i!", show_alert=True)


async def handle_admin_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin reject button click"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await query.edit_message_text(
            text="âŒ Báº¡n khÃ´ng cÃ³ quyá»n thá»±c hiá»‡n thao tÃ¡c nÃ y.",
            parse_mode="HTML"
        )
        return
    
    # Extract verification ID
    verification_id = query.data.replace("admin_reject_", "")
    
    # Store verification_id in context for next message (reason)
    context.user_data['rejecting_payment'] = verification_id
    
    await query.edit_message_text(
        text=f"""
âŒ <b>Tá»ª CHá»I THANH TOÃN</b>

MÃ£: <code>{verification_id}</code>

Vui lÃ²ng gá»­i lÃ½ do tá»« chá»‘i:

<i>VÃ­ dá»¥: Sai ná»™i dung chuyá»ƒn khoáº£n, Sá»‘ tiá»n khÃ´ng Ä‘Ãºng, etc.</i>

Hoáº·c dÃ¹ng command:
/payment_reject {verification_id} [lÃ½ do]
""",
        parse_mode="HTML"
    )


async def handle_admin_list_pending_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle list pending payments button click"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        await query.answer("âŒ Báº¡n khÃ´ng cÃ³ quyá»n xem thÃ´ng tin nÃ y.", show_alert=True)
        return
    
    # Get all pending verifications
    db = next(get_db())
    pending = db.query(PaymentVerification).filter(
        PaymentVerification.status == "PENDING"
    ).order_by(PaymentVerification.created_at.desc()).all()
    
    if not pending:
        await query.answer("âœ… KhÃ´ng cÃ³ yÃªu cáº§u nÃ o Ä‘ang chá» duyá»‡t!", show_alert=True)
        db.close()
        return
    
    # Build message
    message = f"<b>ðŸ“‹ YÃŠU Cáº¦U CHá»œ DUYá»†T: {len(pending)}</b>\n\n"
    
    for ver in pending[:10]:  # Show max 10
        user = db.query(User).filter(User.id == ver.user_id).first()
        username = f"@{user.username}" if user and user.username else "N/A"
        full_name = user.full_name if user else "N/A"
        
        safe_username = html.escape(username)
        safe_fullname = html.escape(full_name)
        
        message += f"""
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
MÃ£: <code>VER{ver.id}</code>
User: {safe_fullname} ({safe_username})
Sá»‘ tiá»n: {ver.amount:,.0f} VND
Thá»i gian: {ver.created_at.strftime('%d/%m/%Y %H:%M')}

Duyá»‡t: /payment_approve VER{ver.id}
Tá»« chá»‘i: /payment_reject VER{ver.id}
"""
    
    db.close()
    
    # Send as new message
    await context.bot.send_message(
        chat_id=user_id,
        text=message,
        parse_mode="HTML"
    )
    
    await query.answer("âœ… ÄÃ£ gá»­i danh sÃ¡ch!")


async def log_payment_to_sheets(
    verification_id: str,
    user_id: int,
    username: str,
    full_name: str,
    amount: float,
    status: str,
    approved_by: int,
    approved_at: datetime,
    notes: str = ""
):
    """Log payment approval/rejection to Google Sheets for statistics"""
    try:
        from app.utils.sheets import get_sheets_client
        from config.settings import settings
        
        logger.info(f"Logging payment {verification_id} to Google Sheets")
        
        # Get sheets client
        client = get_sheets_client()
        if not client:
            logger.warning("Sheets client not initialized")
            return
        
        # Open the SUPPORT spreadsheet (the one user shared)
        sheet_id = settings.SUPPORT_SHEET_ID
        if not sheet_id:
            logger.warning("No SUPPORT_SHEET_ID configured")
            return
        
        spreadsheet = client.open_by_key(sheet_id)
        
        # Try to get "Payments" worksheet, create if not exists
        try:
            worksheet = spreadsheet.worksheet("Payments")
        except:
            # Create new worksheet with headers (11 columns)
            worksheet = spreadsheet.add_worksheet(title="Payments", rows=1000, cols=11)
            worksheet.update('A1:K1', [[
                'MÃ£ XÃ¡c Nháº­n', 'User ID', 'Username', 'Há» TÃªn', 
                'Sá»‘ Tiá»n (VND)', 'Tráº¡ng ThÃ¡i', 'NgÃ y Táº¡o', 'NgÃ y Duyá»‡t', 
                'Admin Duyá»‡t', 'Ghi ChÃº', 'GÃ³i'
            ]])
            # Format header
            worksheet.format('A1:K1', {
                'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            logger.info("Created new 'Payments' worksheet")
        
        # Get created_at from verification (need to query database)
        from app.utils.database import get_db
        db = next(get_db())
        ver_id = int(verification_id.replace("VER", ""))
        ver = db.query(PaymentVerification).filter(PaymentVerification.id == ver_id).first()
        created_at = ver.created_at if ver else approved_at
        db.close()
        
        # Prepare row data (11 columns to match header)
        row_data = [
            verification_id,                                            # A: MÃ£ XÃ¡c Nháº­n
            str(user_id),                                              # B: User ID
            username or "N/A",                                         # C: Username
            full_name or "N/A",                                        # D: Há» TÃªn
            amount,                                                    # E: Sá»‘ Tiá»n (VND)
            status,                                                    # F: Tráº¡ng ThÃ¡i
            created_at.strftime('%Y-%m-%d %H:%M:%S'),                 # G: NgÃ y Táº¡o
            approved_at.strftime('%Y-%m-%d %H:%M:%S') if approved_at else "",  # H: NgÃ y Duyá»‡t
            str(approved_by),                                          # I: Admin Duyá»‡t
            notes or "",                                               # J: Ghi ChÃº (rejection reason)
            "PREMIUM_365" if status == "APPROVED" else ""              # K: GÃ³i (only for approved)
        ]
        
        # Check if verification_id already exists in sheet
        try:
            all_values = worksheet.get_all_values()
            existing_row = None
            
            for idx, row in enumerate(all_values[1:], start=2):  # Skip header (row 1)
                if row and row[0] == verification_id:  # Column A = MÃ£ XÃ¡c Nháº­n
                    existing_row = idx
                    break
            
            if existing_row:
                # UPDATE existing row
                worksheet.update(f'A{existing_row}:K{existing_row}', [row_data], value_input_option='USER_ENTERED')
                logger.info(f"Updated existing row {existing_row} for {verification_id}")
                row_idx = existing_row - 1  # For color formatting (0-based)
            else:
                # APPEND new row
                worksheet.append_row(row_data, value_input_option='USER_ENTERED')
                logger.info(f"Appended new row for {verification_id}")
                all_values = worksheet.get_all_values()
                row_idx = len(all_values) - 1  # Last row index (0-based)
            
        except Exception as e:
            logger.error(f"Error checking/updating row: {e}")
            # Fallback to append
            worksheet.append_row(row_data, value_input_option='USER_ENTERED')
            all_values = worksheet.get_all_values()
            row_idx = len(all_values) - 1
        
        # Apply color formatting
        try:
            if status == "APPROVED":
                color = {'red': 0.7, 'green': 1, 'blue': 0.7}  # Light green
            elif status == "REJECTED":
                color = {'red': 1, 'green': 0.7, 'blue': 0.7}  # Light red
            else:  # PENDING
                color = {'red': 1, 'green': 1, 'blue': 0.7}  # Light yellow
            
            # Format the row
            spreadsheet.batch_update({
                'requests': [{
                    'repeatCell': {
                        'range': {
                            'sheetId': worksheet.id,
                            'startRowIndex': row_idx,
                            'endRowIndex': row_idx + 1,
                            'startColumnIndex': 0,
                            'endColumnIndex': 11
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': color
                            }
                        },
                        'fields': 'userEnteredFormat.backgroundColor'
                    }
                }]
            })
            logger.info(f"âœ… Applied color formatting for {status} status")
            
        except Exception as color_error:
            logger.warning(f"Failed to apply color formatting: {color_error}")
        
        logger.info(f"âœ… Payment {verification_id} logged to Google Sheets successfully")
        
    except Exception as e:
        logger.error(f"Failed to log payment to sheets: {e}", exc_info=True)
        # Don't fail the approval if logging fails

