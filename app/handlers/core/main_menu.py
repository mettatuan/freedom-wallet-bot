"""
Main Menu Handler - User behavior-focused menu for Freedom Wallet Bot
Menu chuẩn theo hành vi người dùng
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from loguru import logger
from datetime import datetime, date


async def show_quick_record_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📌 Ghi nhanh thu chi - Menu chính nhất"""
    query = update.callback_query
    await query.answer()
    
    message = """
📌 **GHI NHANH THU CHI**

Cách nhanh nhất để ghi giao dịch:

━━━━━━━━━━━━━━━━━━━━━

**💬 Cách 1: Gửi tin nhắn (khuyến nghị)**

Ví dụ:
• `Cà phê 35k`
• `Ăn trưa 50k`
• `Lương 15tr`
• `Mua sách 150k`

→ Bot tự động lưu vào Sheet!

━━━━━━━━━━━━━━━━━━━━━

**📝 Cách 2: Dùng nút bên dưới**

Chọn loại giao dịch để bắt đầu

━━━━━━━━━━━━━━━━━━━━━

💡 **Tip:** Ghi trong 5 giây, không cần mở app!
"""
    
    keyboard = [
        [InlineKeyboardButton("💸 Ghi chi tiêu", callback_data="qr_start_chi")],
        [InlineKeyboardButton("💰 Ghi thu nhập", callback_data="qr_start_thu")],
        [InlineKeyboardButton("📊 Xem giao dịch hôm nay", callback_data="show_today_transactions")],
        [InlineKeyboardButton("💼 Tài khoản", callback_data="show_accounts_report")],
        [InlineKeyboardButton("🏺 Hũ tiền", callback_data="show_jars_report")],
        [InlineKeyboardButton("📊 Thu chi (tháng này)", callback_data="show_monthly_income_expense")],
        [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💰 Xem số dư - Đọc từ Google Sheets qua Web App API"""
    query = update.callback_query
    await query.answer("🔄 Đang tải số dư từ Google Sheets...")
    
    from app.utils.database import SessionLocal, User
    from app.services.sheets_api_client import SheetsAPIClient
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.spreadsheet_id:
            await query.edit_message_text(
                "❌ Bạn chưa kết nối Sheet!\n\n"
                "Vui lòng kết nối trước: /connectsheets",
                parse_mode="Markdown"
            )
            return
        
        # Try to read balance via Web App API
        try:
            # Initialize API client (calls Web App URL, not direct Sheets API)
            client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
            
            # Test connection first (ping Web App)
            ping_result = await client.ping()
            
            if not ping_result.get('success'):
                error_msg = ping_result.get('error', 'Unknown error')
                message = f"""
⚠️ **KHÔNG THỂ KẾT NỐI VỚI FREEDOM WALLET**

Lỗi: `{error_msg}`

Vui lòng kiểm tra:
• Web App URL có đúng không?
• Google Sheet có tồn tại?

💡 Thử mở Web App để kiểm tra!
"""
                keyboard = [
                    [InlineKeyboardButton("🔄 Thử lại", callback_data="show_balance")],
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                    [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return
            
            # Get balance via Web App API
            balance_result = await client.get_balance(use_cache=False)  # Force fresh data
            
            if not balance_result.get('success'):
                error_msg = balance_result.get('error', 'Unknown error')
                message = f"""
⚠️ **KHÔNG ĐỌC ĐƯỢC SỐ DƯ**

Lỗi: `{error_msg}`

💡 Mở Web App để xem chi tiết!
"""
                keyboard = [
                    [InlineKeyboardButton("🔄 Thử lại", callback_data="show_balance")],
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                    [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return
            
            # Extract balance data
            jars = balance_result.get('jars', [])
            total = balance_result.get('totalBalance', 0)
            
            if not jars:
                message = """
⚠️ **KHÔNG TÌM THẤY DỮ LIỆU**

Sheet của bạn có đúng cấu trúc không?

💡 Mở Web App để kiểm tra!
"""
                keyboard = [
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                    [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return
            
            # Format balance message
            jar_lines = []
            for jar in jars:
                jar_name = jar.get('name', jar.get('id', ''))
                jar_balance = jar.get('balance', 0)
                jar_lines.append(f"• {jar_name}: {jar_balance:,.0f} ₫")
            
            message = f"""
💰 **SỐ DƯ TÀI KHOẢN**

**Tổng:** {total:,.0f} ₫

━━━━━━━━━━━━━━━━━━━━━

**Phân bổ theo hũ:**
{chr(10).join(jar_lines)}

━━━━━━━━━━━━━━━━━━━━━

🔄 Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}

💡 Xem chi tiết hơn trên Web App!
"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 Làm mới", callback_data="show_balance")],
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")],
                [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Error reading balance: {e}")
            message = f"""
😓 **LỖI KHI ĐỌC DỮ LIỆU**

Có lỗi xảy ra khi đọc từ Google Sheets.

**Lỗi:** {str(e)[:100]}

💡 Thử mở Web App để xem số dư!
"""
            keyboard = [
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else "https://script.google.com")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    finally:
        db.close()


async def show_accounts_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💼 Báo cáo tài khoản - Hiển thị chi tiết các tài khoản"""
    query = update.callback_query
    await query.answer("🔄 Đang tải danh sách tài khoản...")
    
    from app.utils.database import SessionLocal, User
    from app.services.sheets_api_client import SheetsAPIClient
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.spreadsheet_id:
            await query.edit_message_text(
                "❌ Bạn chưa kết nối Sheet!\n\n"
                "Vui lòng kết nối trước: /connectsheets",
                parse_mode="Markdown"
            )
            return
        
        try:
            client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
            
            # Get balance data (includes accounts)
            balance_result = await client.get_balance(use_cache=False)
            
            if not balance_result.get('success'):
                error_msg = balance_result.get('error', 'Unknown error')
                message = f"""
⚠️ **KHÔNG ĐỌC ĐƯỢC DỮ LIỆU TÀI KHOẢN**

Lỗi: `{error_msg}`

💡 Mở Web App để xem chi tiết!
"""
                keyboard = [
                    [InlineKeyboardButton("🔄 Thử lại", callback_data="show_accounts_report")],
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                    [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return
            
            # Extract accounts data
            accounts = balance_result.get('accounts', [])
            total_accounts = sum(acc.get('balance', 0) for acc in accounts)
            
            if not accounts:
                message = """
⚠️ **KHÔNG TÌM THẤY TÀI KHOẢN**

Sheet của bạn có đúng cấu trúc không?

💡 Mở Web App để kiểm tra!
"""
                keyboard = [
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                    [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return
            
            # Format accounts message
            account_lines = []
            for acc in accounts:
                acc_name = acc.get('name', acc.get('id', ''))
                acc_balance = acc.get('balance', 0)
                percentage = (acc_balance / total_accounts * 100) if total_accounts > 0 else 0
                account_lines.append(f"• {acc_name}: {acc_balance:,.0f} ₫ ({percentage:.1f}%)")
            
            message = f"""
💼 **BÁO CÁO TÀI KHOẢN**

**Tổng tất cả tài khoản:** {total_accounts:,.0f} ₫

━━━━━━━━━━━━━━━━━━━━━

**Chi tiết các tài khoản:**
{chr(10).join(account_lines)}

━━━━━━━━━━━━━━━━━━━━━

🔄 Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}

💡 Xem chi tiết hơn trên Web App!
"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 Làm mới", callback_data="show_accounts_report")],
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")],
                [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Error reading accounts: {e}")
            message = f"""
😓 **LỖI KHI ĐỌC DỮ LIỆU TÀI KHOẢN**

Có lỗi xảy ra khi đọc từ Google Sheets.

**Lỗi:** {str(e)[:100]}

💡 Thử mở Web App để xem tài khoản!
"""
            keyboard = [
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else "https://script.google.com")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    finally:
        db.close()


async def show_jars_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏺 Báo cáo hũ tiền - Hiển thị chi tiết các hũ tiền"""
    query = update.callback_query
    await query.answer("🔄 Đang tải danh sách hũ tiền...")
    
    from app.utils.database import SessionLocal, User
    from app.services.sheets_api_client import SheetsAPIClient
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.spreadsheet_id:
            await query.edit_message_text(
                "❌ Bạn chưa kết nối Sheet!\n\n"
                "Vui lòng kết nối trước: /connectsheets",
                parse_mode="Markdown"
            )
            return
        
        try:
            client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
            
            # Get balance data (includes jars)
            balance_result = await client.get_balance(use_cache=False)
            
            if not balance_result.get('success'):
                error_msg = balance_result.get('error', 'Unknown error')
                message = f"""
⚠️ **KHÔNG ĐỌC ĐƯỢC DỮ LIỆU HŨ TIỀN**

Lỗi: `{error_msg}`

💡 Mở Web App để xem chi tiết!
"""
                keyboard = [
                    [InlineKeyboardButton("🔄 Thử lại", callback_data="show_jars_report")],
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                    [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return
            
            # Extract jars data
            jars = balance_result.get('jars', [])
            total_jars = sum(jar.get('balance', 0) for jar in jars)
            
            if not jars:
                message = """
⚠️ **KHÔNG TÌM THẤY HŨ TIỀN**

Sheet của bạn có đúng cấu trúc không?

💡 Mở Web App để kiểm tra!
"""
                keyboard = [
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                    [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return
            
            # Format jars message
            jar_lines = []
            for jar in jars:
                jar_name = jar.get('name', jar.get('id', ''))
                jar_balance = jar.get('balance', 0)
                percentage = (jar_balance / total_jars * 100) if total_jars > 0 else 0
                jar_lines.append(f"• {jar_name}: {jar_balance:,.0f} ₫ ({percentage:.1f}%)")
            
            message = f"""
🏺 **BÁO CÁO HŨ TIỀN**

**Tổng tất cả hũ:** {total_jars:,.0f} ₫

━━━━━━━━━━━━━━━━━━━━━

**Chi tiết các hũ:**
{chr(10).join(jar_lines)}

━━━━━━━━━━━━━━━━━━━━━

🔄 Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}

💡 Xem chi tiết hơn trên Web App!
"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 Làm mới", callback_data="show_jars_report")],
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")],
                [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Error reading jars: {e}")
            message = f"""
😓 **LỖI KHI ĐỌC DỮ LIỆU HŨ TIỀN**

Có lỗi xảy ra khi đọc từ Google Sheets.

**Lỗi:** {str(e)[:100]}

💡 Thử mở Web App để xem hũ tiền!
"""
            keyboard = [
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else "https://script.google.com")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    finally:
        db.close()


async def show_monthly_income_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Báo cáo thu chi tháng này"""
    query = update.callback_query
    await query.answer("🔄 Đang tải dữ liệu thu chi...")
    
    from app.utils.database import SessionLocal, User
    from app.services.sheets_api_client import SheetsAPIClient
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.spreadsheet_id:
            await query.edit_message_text(
                "❌ Bạn chưa kết nối Sheet!\n\n"
                "Vui lòng kết nối trước: /connectsheets",
                parse_mode="Markdown"
            )
            return
        
        try:
            client = SheetsAPIClient(user.spreadsheet_id, user.web_app_url)
            
            # Get recent transactions (limit 200 to ensure we get all monthly transactions)
            transactions_result = await client.get_recent_transactions(limit=200)
            
            if not transactions_result.get('success'):
                error_msg = transactions_result.get('error', 'Unknown error')
                message = f"""
⚠️ **KHÔNG ĐỌC ĐƯỢC DỮ LIỆU GIAO DỊCH**

Lỗi: `{error_msg}`

💡 Mở Web App để xem chi tiết!
"""
                keyboard = [
                    [InlineKeyboardButton("🔄 Thử lại", callback_data="show_monthly_income_expense")],
                    [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                    [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return
            
            # Filter transactions for current month
            transactions = transactions_result.get('transactions', [])
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            monthly_income = 0
            monthly_expense = 0
            count_income = 0
            count_expense = 0
            
            for txn in transactions:
                # Parse transaction date
                txn_date_str = txn.get('date', '')
                try:
                    # Try different date formats
                    if '/' in txn_date_str:
                        # Format: DD/MM/YYYY or D/M/YYYY
                        parts = txn_date_str.split('/')
                        if len(parts) == 3:
                            txn_day, txn_month, txn_year = int(parts[0]), int(parts[1]), int(parts[2])
                    elif '-' in txn_date_str:
                        # Format: YYYY-MM-DD
                        txn_date = datetime.strptime(txn_date_str, "%Y-%m-%d")
                        txn_month = txn_date.month
                        txn_year = txn_date.year
                    else:
                        continue
                    
                    # Check if transaction is in current month
                    if txn_month == current_month and txn_year == current_year:
                        txn_type = txn.get('type', '').strip()
                        txn_amount = abs(float(txn.get('amount', 0)))
                        
                        if txn_type == 'Thu':
                            monthly_income += txn_amount
                            count_income += 1
                        elif txn_type == 'Chi':
                            monthly_expense += txn_amount
                            count_expense += 1
                            
                except (ValueError, IndexError):
                    continue
            
            balance = monthly_income - monthly_expense
            balance_emoji = "📈" if balance >= 0 else "📉"
            balance_text = "Thặng dư" if balance >= 0 else "Thâm hụt"
            
            month_name = datetime.now().strftime("%m/%Y")
            
            message = f"""
📊 **BÁO CÁO THU CHI THÁNG {month_name}**

**💰 Tổng thu:** {monthly_income:,.0f} ₫
   └ {count_income} giao dịch

**💸 Tổng chi:** {monthly_expense:,.0f} ₫
   └ {count_expense} giao dịch

━━━━━━━━━━━━━━━━━━━━━

{balance_emoji} **{balance_text}:** {abs(balance):,.0f} ₫

━━━━━━━━━━━━━━━━━━━━━

🔄 Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M')}

💡 Xem chi tiết hơn trên Web App!
"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 Làm mới", callback_data="show_monthly_income_expense")],
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")],
                [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ Error reading monthly transactions: {e}")
            message = f"""
😓 **LỖI KHI ĐỌC DỮ LIỆU THU CHI**

Có lỗi xảy ra khi đọc từ Google Sheets.

**Lỗi:** {str(e)[:100]}

💡 Thử mở Web App để xem thu chi!
"""
            keyboard = [
                [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else "https://script.google.com")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="quick_report_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    finally:
        db.close()


async def show_quick_report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Báo cáo nhanh - Kiểm tra nhanh"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.spreadsheet_id:
            await query.edit_message_text(
                "❌ Bạn chưa kết nối Sheet!\n\n"
                "Vui lòng kết nối trước: /connectsheets",
                parse_mode="Markdown"
            )
            return
        
        message = """
📊 **BÁO CÁO NHANH**

Xem tổng quan tài chính của bạn:

━━━━━━━━━━━━━━━━━━━━━

**💰 Số dư hiện tại**
Xem tổng số dư tất cả ví/lọ

**📈 Thu chi tháng này**
Tổng thu, tổng chi, chênh lệch

**💳 Tình trạng các hũ**
Các hũ tiết kiệm đang có bao nhiêu

**📊 Chi tiêu theo danh mục**
Phân tích chi tiêu chi tiết

━━━━━━━━━━━━━━━━━━━━━

💡 **Tip:** Muốn báo cáo sâu hơn? Mở Web App!
"""
        
        keyboard = [
            [InlineKeyboardButton(" Tài khoản", callback_data="show_accounts_report")],
            [InlineKeyboardButton("🏺 Hũ tiền", callback_data="show_jars_report")],
            [InlineKeyboardButton("📊 Thu chi (tháng này)", callback_data="show_monthly_income_expense")],
            [InlineKeyboardButton("🌐 Mở Web App", url=user.web_app_url if user and user.web_app_url else "https://script.google.com")],
            [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def show_my_system_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📁 Hệ thống của tôi - Quản lý Sheet & Web App"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        sheet_status = "✅ Đã kết nối" if user and user.spreadsheet_id else "❌ Chưa kết nối"
        webapp_status = "✅ Đã kích hoạt" if user and user.web_app_url else "❌ Chưa kích hoạt"
        sheet_id_preview = user.spreadsheet_id[:15] + "..." if user and user.spreadsheet_id else "Chưa có"
        
        message = f"""
📁 **HỆ THỐNG CỦA TÔI**

━━━━━━━━━━━━━━━━━━━━━

**💡 Nhắc nhở quan trọng:**

Hệ thống này thuộc về bạn!
• Google Sheet = Của bạn
• Web App = Của bạn  
• Dữ liệu = Của bạn

Bot chỉ là cầu nối giúp ghi nhanh.

━━━━━━━━━━━━━━━━━━━━━

**📋 Google Sheet**
Trạng thái: {sheet_status}
Sheet ID: `{sheet_id_preview}`

**🔗 Web App**
Trạng thái: {webapp_status}

━━━━━━━━━━━━━━━━━━━━━

**🔧 Bạn có thể:**
• Mở Sheet/Web App của mình
• Kiểm tra kết nối
• Cập nhật URL mới
• Xem hướng dẫn chỉnh sửa nâng cao
"""
        
        keyboard = []
        
        if user and user.spreadsheet_id:
            sheet_url = f"https://docs.google.com/spreadsheets/d/{user.spreadsheet_id}"
            keyboard.append([InlineKeyboardButton("📋 Mở Google Sheet của tôi", url=sheet_url)])
        
        if user and user.web_app_url:
            keyboard.append([InlineKeyboardButton("🔗 Mở Web App của tôi", url=user.web_app_url)])
        
        keyboard.extend([
            [InlineKeyboardButton("🔍 Kiểm tra kết nối", callback_data="check_connection")],
            [InlineKeyboardButton("🔄 Cập nhật Sheet ID", callback_data="update_sheet_id")],
            [InlineKeyboardButton("🔄 Cập nhật Web App URL", callback_data="update_webapp_url")],
            [InlineKeyboardButton("📖 Hướng dẫn nâng cao", callback_data="advanced_guide")],
            [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """❓ Hướng dẫn - Hướng dẫn ngắn gọn"""
    query = update.callback_query
    await query.answer()
    
    message = """
❓ **HƯỚNG DẪN SỬ DỤNG**

━━━━━━━━━━━━━━━━━━━━━

**📝 Cách ghi giao dịch**

Gửi tin nhắn theo format:
• `Cà phê 35k`
• `Ăn sáng 50 nghìn`
• `Lương 15 triệu`

Bot tự hiểu và lưu!

━━━━━━━━━━━━━━━━━━━━━

**✏️ Cách sửa giao dịch**

Vào Sheet hoặc Web App → Sửa trực tiếp
Hoặc ghi lại giao dịch mới

━━━━━━━━━━━━━━━━━━━━━

**🆘 Lỗi thường gặp**

1. "Bot không phản hồi"
   → Kiểm tra kết nối Sheet/Web App

2. "Ghi sai số tiền"
   → Vào Sheet sửa trực tiếp

3. "Web App không mở được"
   → Deploy lại Apps Script

━━━━━━━━━━━━━━━━━━━━━

💬 **Cần hỗ trợ thêm?**
Liên hệ admin hoặc xem hướng dẫn chi tiết
"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Hướng dẫn Deploy Web App", callback_data="show_deploy_guide")],
        [InlineKeyboardButton("🐛 Báo lỗi", callback_data="report_bug")],
        [InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_admin")],
        [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚙️ Cài đặt - Cấu hình bot"""
    query = update.callback_query
    await query.answer()
    
    message = """
⚙️ **CÀI ĐẶT**

Tùy chỉnh bot theo ý bạn:

━━━━━━━━━━━━━━━━━━━━━

**🔔 Nhắc nhở định kỳ**
Cài đặt thời gian bot nhắc ghi chi tiêu

**⚠️ Mức cảnh báo**
Cảnh báo khi chi tiêu vượt ngưỡng

**🌐 Ngôn ngữ**
Tiếng Việt / English

**🔕 Thông báo**
Bật/tắt thông báo từ bot

**🔄 Kết nối lại**
Kết nối lại Sheet/Web App nếu lỗi

━━━━━━━━━━━━━━━━━━━━━

💡 **Lưu ý:** Cài đặt này chỉ ảnh hưởng bot
Không thay đổi dữ liệu Sheet của bạn
"""
    
    keyboard = [
        [InlineKeyboardButton("🔔 Cài đặt nhắc nhở", callback_data="setup_reminders")],
        [InlineKeyboardButton("⚠️ Cài đặt cảnh báo", callback_data="setup_alerts")],
        [InlineKeyboardButton("🔕 Quản lý thông báo", callback_data="manage_notifications")],
        [InlineKeyboardButton("🔄 Kết nối lại", callback_data="reconnect_system")],
        [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏠 Menu chính - Động theo hành vi user"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        name = user.full_name if user and user.full_name else update.effective_user.first_name
        
        # Simple greeting
        greeting = f"👋 Chào {name}!"
        
        message = f"""
🏠 **FREEDOM WALLET**

{greeting}

━━━━━━━━━━━━━━━━━━━━━

**💡 GHI NHANH:**
Gửi: `Cà phê 35k` → Tự động lưu!

**🤖 HỎI BẤT CỨ LÚC NÀO:**
"Tôi chi bao nhiêu tháng này?"
"Còn bao nhiêu tiền?"

━━━━━━━━━━━━━━━━━━━━━

**Chọn chức năng:**
"""
        
        keyboard = [
            [InlineKeyboardButton("📌 Ghi nhanh thu chi", callback_data="quick_record_menu")],
            [InlineKeyboardButton("📊 Báo cáo nhanh", callback_data="quick_report_menu")],
            [InlineKeyboardButton("📁 Hệ thống của tôi", callback_data="my_system_menu")],
            [InlineKeyboardButton("📖 Hướng dẫn sử dụng", callback_data="show_guide_choice"), 
             InlineKeyboardButton("⚙️ Cài đặt", callback_data="settings_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Delete previous message (might be photo) and send new text message
        try:
            await query.message.delete()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def show_guide_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📚 Menu chọn loại hướng dẫn: Tạo Web App vs Sử dụng Web App"""
    query = update.callback_query
    await query.answer()
    
    message = """
📚 **CHỌN LOẠI HƯỚNG DẪN**

Bạn cần hướng dẫn gì?

━━━━━━━━━━━━━━━━━━━━━

**🚀 Hướng dẫn tạo Web App**
• Dành cho người mới, chưa có Web App
• 5 bước: Copy Sheet → Deploy Apps Script
• Thời gian: ~10-15 phút

━━━━━━━━━━━━━━━━━━━━━

**📱 Hướng dẫn sử dụng Web App**
• Dành cho người đã tạo xong Web App
• Hướng dẫn từ đăng nhập → sử dụng đầy đủ
• Bắt đầu từ: Đăng nhập lần đầu

━━━━━━━━━━━━━━━━━━━━━

💡 **Mẹo:** Nếu bạn chưa có Web App, chọn hướng dẫn tạo trước!
"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Hướng dẫn tạo Web App", callback_data="show_deploy_guide")],
        [InlineKeyboardButton("📱 Hướng dẫn sử dụng Web App", callback_data="show_webapp_usage_steps")],
        [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Delete previous message (might be photo) and send new text message
    try:
        await query.message.delete()
    except:
        pass
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_webapp_usage_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📱 Hướng dẫn sử dụng Web App - Step by step từ đăng nhập"""
    query = update.callback_query
    await query.answer()
    
    # Extract step number from callback data (e.g., "usage_step_1")
    current_step = int(query.data.split("_")[-1]) if "_" in query.data and query.data.split("_")[-1].isdigit() else 1
    
    steps = {
        1: {  # BƯỚC 1: Đăng nhập
            "title": "🌐 BƯỚC 1: Đăng nhập Web App",
            "text": """
**🌐 BƯỚC 1: Đăng nhập vào Web App**

Bây giờ hãy mở Web App của bạn lần đầu tiên!

**🔹 Làm thế nào:**
1. Mở Web App URL bạn vừa copy
2. Nhập **tên đăng nhập:** mặc định là `Admin`
3. Nhập **mật khẩu:** mặc định là `2369`
4. Đợi Web App load xong

🔐 **An toàn 100%:** Dữ liệu chỉ lưu trên Google Drive của bạn
⏱️ **Lần đầu có thể mất 5-10 giây** để Apps Script khởi động

💡 **Mẹo:** Sau khi đăng nhập thành công, hãy bookmark (Ctrl+D) để truy cập nhanh!
""",
            "image": "media/images/web_app_login.jpg",
            "keyboard": [
                [InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_2")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        2: {  # BƯỚC 2: Màn hình chính
            "title": "📊 BƯỚC 2: Màn hình chính Web App",
            "text": """
**📊 BƯỚC 2: Màn hình chính Web App**

Chào mừng bạn đến với Freedom Wallet! 🎉

**🔹 Bạn sẽ thấy:**
• 💰 **Tổng tài sản** - Số dư hiện tại của bạn
• 📊 **Dòng tiền** - Thu nhập vs Chi tiêu tháng này
• 📈 **Biểu đồ** - Phân tích chi tiêu theo danh mục
• 🎯 **Cấp độ tài chính** - Điểm số quản lý tiền của bạn
• ⚡ **Ghi nhanh** - Nút truy cập nhanh các tính năng

✨ **Đây là lần đầu tiên bạn nhìn thấy toàn bộ tiền ở một nơi!**

💡 **Mẹo:** 
• Bookmark trang này để truy cập nhanh hàng ngày
• Web App hoạt động tốt nhất trên Chrome/Firefox
• Có thể thêm vào màn hình chính điện thoại (như 1 app)
""",
            "image": "media/images/web_apps.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_1"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_3")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        3: {  # BƯỚC 3: Xóa dữ liệu mẫu & Đổi mật khẩu
            "title": "🗑️ BƯỚC 3: Xóa dữ liệu mẫu & Đổi mật khẩu",
            "text": """
**🗑️ BƯỚC 3: Xóa dữ liệu mẫu & Đổi mật khẩu**

Trước khi bắt đầu, hãy dọn sạch dữ liệu mẫu và bảo mật tài khoản!

━━━━━━━━━━━━━━━━━━━━━

**🔹 BƯỚC 1: XÓA DỮ LIỆU MẪU**

1. Mở Web App → Tab "Cài đặt"
2. Tìm phần "Dữ liệu hệ thống"
3. Click "Xóa dữ liệu mẫu"
4. Xác nhận xóa

✅ **Tại sao?** Dữ liệu mẫu chỉ để demo, bắt đầu với dữ liệu sạch!

━━━━━━━━━━━━━━━━━━━━━

**🔹 BƯỚC 2: ĐỔI MẬT KHẨU**

1. Tab "Cài đặt" → "Đổi mật khẩu"
2. Mật khẩu cũ: `2369`
3. Nhập mật khẩu mới (ít nhất 4 ký tự)
4. Nhập lại để xác nhận
5. Click "Lưu"

🔐 **Quan trọng:** 
• Chọn mật khẩu dễ nhớ nhưng khó đoán
• Không chia sẻ mật khẩu với ai
• Ghi nhớ mật khẩu - không có chức năng quên mật khẩu!

━━━━━━━━━━━━━━━━━━━━━

💡 **Mẹo:** Dùng mật khẩu là ngày sinh hoặc số điện thoại để dễ nhớ!
""",
            "image": "media/images/cai_dat.png",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_2"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_4")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        4: {  # BƯỚC 4: Cài đặt 6 hũ tiền
            "title": "🏺 BƯỚC 4: Cài đặt 6 hũ tiền",
            "text": """
**🏺 BƯỚC 4: Cài đặt 6 hũ tiền**

Phương pháp 6 hũ tiền giúp phân bổ thu nhập khoa học!

━━━━━━━━━━━━━━━━━━━━━

**🔹 6 HŨ TIỀN VÀ % PHÂN BỔ:**

1️⃣ **Nhu cầu thiết yếu (55%)**
   • Ăn, ở, đi lại, hóa đơn cố định
   • Chi phí sống hàng ngày

2️⃣ **Tự do tài chính (10%)**
   • Đầu tư, tích lũy tài sản
   • KHÔNG BAO GIỜ động vào!

3️⃣ **Giáo dục (10%)**
   • Học hỏi, phát triển bản thân
   • Khóa học, sách vở

4️⃣ **Tiết kiệm dài hạn (10%)**
   • Mua nhà, xe, mục tiêu lớn
   • Dự phòng khẩn cấp

5️⃣ **Giải trí (10%)**
   • Du lịch, sở thích, shopping
   • Thư giãn, tận hưởng cuộc sống

6️⃣ **Cho đi (5%)**
   • Từ thiện, quà tặng gia đình
   • Chia sẻ yêu thương

━━━━━━━━━━━━━━━━━━━━━

**🔹 CÁCH CÀI ĐẶT:**

1. Tab "Cài đặt" → "Quản lý hũ tiền"
2. Xem % mặc định đã được thiết lập
3. Điều chỉnh % nếu cần (sau 3 tháng thử)
4. Click "Lưu cấu hình"

━━━━━━━━━━━━━━━━━━━━━

💡 **Mẹo:** Tuân thủ % mặc định trong 3 tháng đầu trước khi tùy chỉnh!
""",
            "image": "media/images/hu_tien.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_3"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_5")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        5: {  # BƯỚC 5: Cài đặt 5 cấp bậc tài chính
            "title": "📊 BƯỚC 5: Cài đặt 5 cấp bậc tài chính",
            "text": """
**📊 BƯỚC 5: Cài đặt 5 cấp bậc tài chính**

Đo lường hành trình tự do tài chính!

**🔹 5 CẤP ĐỘ:**

**Level 1 - Đảm Bảo:**
Thu nhập >= Chi tiêu (1 tháng)

**Level 2 - An Toàn:**
Tiết kiệm 3-6 tháng chi tiêu

**Level 3 - Độc Lập:**
Đầu tư sinh lời đủ sống
Công thức: (Chi × 12) / 4%

**Level 4 - Tự Do:**
Sống thoải mái không làm việc
= Level 3 × 5

**Level 5 - Di Sản:**
Để lại cho thế hệ sau
= Level 4 × 5

**🔹 CÁCH CÀI ĐẶT:**

1. Tab "Cài đặt" → "Cấp bậc"
2. Nhập chi tiêu cơ bản/tháng
3. Hệ thống tự tính 5 levels
4. Điều chỉnh nếu cần
5. Click "Lưu"

🎯 Mục tiêu: Level 1 → Level 5!
""",
            "image": "media/images/5_cap_bac_tai_chinh.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_4"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_6")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        6: {  # BƯỚC 6: Kế hoạch xài tiền ý nghĩa
            "title": "💰 BƯỚC 6: Kế hoạch xài tiền ý nghĩa",
            "text": """
**💰 BƯỚC 6: Thiết lập Kế hoạch xài tiền ý nghĩa**

Lập kế hoạch chi tiêu cho từng hũ tiền mỗi tháng!

━━━━━━━━━━━━━━━━━━━━━

**🔹 LÀM THẾ NÀO:**

1. Tab "Cài đặt" → "Kế hoạch chi tiêu"
2. Chọn từng hũ tiền để chi tiết hóa
3. Thêm các khoản chi cố định

━━━━━━━━━━━━━━━━━━━━━

**📝 VÍ DỤ KẾ HOẠCH:**

**Hũ 1: Nhu cầu thiết yếu (25tr/tháng)**
• Ăn uống: 10.000.000đ
• Nhà ở: 10.000.000đ
• Đi lại: 2.000.000đ
• Điện nước - Internet: 1.500.000đ
• Y tế - Bảo hiểm: 1.500.000đ

**Hũ 2: Tự do tài chính (4tr/tháng)**
• Đầu tư CRYPTO: 4.000.000đ

**Hũ 3: Giáo dục (2tr/tháng)**
• Khóa học tài chính cá nhân: 2.000.000đ

**Hũ 4: Tiết kiệm dài hạn (2tr/tháng)**
• Bảo hiểm nhân thọ: 2.000.000đ

**Hũ 5: Giải trí (1tr/tháng)**
• Du lịch cuối tuần: 1.000.000đ

**Hũ 6: Cho đi (1tr/tháng)**
• Giúp đỡ gia đình: 1.000.000đ

━━━━━━━━━━━━━━━━━━━━━

✅ **Lợi ích:** Biết rõ tiền sẽ xài vào đâu, tránh chi tiêu vô tội vạ!
""",
            "image": "media/images/ke_hoach_xai_tien_y_nghia.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_5"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_7")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        7: {  # BƯỚC 7: Quản lý tài khoản
            "title": "🏦 BƯỚC 7: Quản lý Tài khoản",
            "text": """
**🏦 BƯỚC 7: Thêm - Xóa - Sửa Tài khoản**

Quản lý tất cả nguồn tiền của bạn tại một nơi!

━━━━━━━━━━━━━━━━━━━━━

**🔹 CÁC LOẠI TÀI KHOẢN:**

• 💵 **Tiền mặt** - Cash trong ví
• 🏦 **Ngân hàng** - Tài khoản ngân hàng
• 💳 **Ví điện tử** - Momo, Zalopay, VNPay...
• 💎 **Tài sản** - Vàng, ngoại tệ, crypto

━━━━━━━━━━━━━━━━━━━━━

**🔹 CÁCH THÊM TÀI KHOẢN:**

1. Tab "Cài đặt" → "Tài khoản"
2. Click "Thêm tài khoản"
3. Chọn loại tài khoản
4. Nhập tên (VD: Ví Momo, VCB Chính)
5. Nhập số dư hiện tại
6. Chọn biểu tượng (tùy chọn)
7. Click "Lưu"

━━━━━━━━━━━━━━━━━━━━━

**🔹 SỬA / XÓA TÀI KHOẢN:**

• **Sửa:** Click vào tài khoản → Chỉnh sửa thông tin
• **Xóa:** Swipe trái → Nút xóa (⚠️ Lưu ý: Xóa tài khoản sẽ xóa tất cả giao dịch liên quan!)

━━━━━━━━━━━━━━━━━━━━━

💡 **Mẹo:**
• Thêm tất cả tài khoản bạn đang dùng
• Cập nhật số dư định kỳ để chính xác
• Đặt tên dễ nhớ để phân biệt
""",
            "image": "media/images/tai_khoan.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_6"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_8")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        8: {  # BƯỚC 8: Quản lý danh mục
            "title": "📁 BƯỚC 8: Quản lý Danh mục",
            "text": """
**📁 BƯỚC 8: Thêm - Xóa - Sửa Danh mục**

Phân loại thu chi để dễ theo dõi và phân tích!

━━━━━━━━━━━━━━━━━━━━━

**🔹 DANH MỤC MẶC ĐỊNH:**

**Thu nhập:**
• 💰 Lương
• 💼 Thưởng
• 📈 Đầu tư
• 🎁 Quà tặng

**Chi tiêu:**
• 🍜 Ăn uống
• 🏠 Nhà ở
• 🚗 Đi lại
• 👕 Quần áo
• 📱 Mua sắm
• 🎮 Giải trí
• 💊 Y tế
• 📚 Giáo dục

━━━━━━━━━━━━━━━━━━━━━

**🔹 CÁCH THÊM DANH MỤC:**

1. Tab "Cài đặt" → "Danh mục"
2. Chọn loại: Thu nhập / Chi tiêu
3. Click "Thêm danh mục"
4. Nhập tên danh mục (VD: Ăn sáng, Cafe)
5. Chọn icon (tùy chọn)
6. Chọn màu sắc
7. Click "Lưu"

━━━━━━━━━━━━━━━━━━━━━

**🔹 SỬA / XÓA DANH MỤC:**

• **Sửa:** Click vào danh mục → Chỉnh sửa
• **Xóa:** Swipe trái → Nút xóa
• ⚠️ **Lưu ý:** Không xóa được danh mục đã có giao dịch

━━━━━━━━━━━━━━━━━━━━━

💡 **Mẹo:**
• Tạo danh mục chi tiết để phân tích tốt hơn
• VD: Thay vì "Ăn uống", chia thành "Ăn sáng", "Ăn trưa", "Cafe"
• Dùng màu sắc khác nhau để dễ phân biệt
""",
            "image": "media/images/danh_muc.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_7"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_9")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        9: {  # BƯỚC 9: Giao dịch
            "title": "💳 BƯỚC 9: Hướng dẫn Giao dịch",
            "text": """
**💳 BƯỚC 9: Hướng dẫn ghi Giao dịch**

Ghi lại mọi thu chi để quản lý tài chính hiệu quả!

━━━━━━━━━━━━━━━━━━━━━

**🔹 CÁCH GHI GIAO DỊCH:**

**Trên Web App:**
1. Tab "Giao dịch" → Click "Thêm mới"
2. Chọn loại: Thu nhập / Chi tiêu
3. Nhập số tiền (VD: 350000)
4. Chọn danh mục (VD: Ăn uống)
5. Chọn tài khoản (VD: Ví Momo)
6. Chọn ngày giờ
7. Ghi chú (tùy chọn)
8. Click "Lưu"

**Qua Bot (Nhanh hơn):**
• Chỉ cần gửi: `Cà phê 35k`
• Bot tự động phân loại và lưu
• Xem lịch sử: /transactions

━━━━━━━━━━━━━━━━━━━━━

**💡 MẸO GHI GIAO DỊCH:**
• Ghi ngay khi chi tiêu, đừng để quên
• Dùng Bot cho giao dịch nhỏ (nhanh)
• Dùng Web App cho giao dịch phức tạp (có hóa đơn, hình ảnh)
• Thêm ghi chú để dễ nhớ sau này
• Chụp hóa đơn để lưu trữ (nếu cần)

━━━━━━━━━━━━━━━━━━━━━

✅ **Lợi ích:** Biết rõ tiền đi đâu, tránh chi tiêu quá đà!
""",
            "image": "media/images/giao_dich.jpg",
            "keyboard": [
                [InlineKeyboardButton("🚀 Thử ghi nhanh", callback_data="quick_record_menu")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_8"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_10")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        10: {  # BƯỚC 10: Khoản nợ
            "title": "📋 BƯỚC 10: Hướng dẫn Khoản nợ",
            "text": """
**📋 BƯỚC 10: Hướng dẫn quản lý Khoản nợ**

Quản lý các khoản vay mượn để không quên ai nợ ai!

━━━━━━━━━━━━━━━━━━━━━

**🔹 2 LOẠI KHOẢN NỢ:**

**1️⃣ Vay tiền (Bạn nợ người khác)**
• Tab "Khoản nợ" → Thêm mới
• Chọn loại: "Vay"
• Nhập số tiền vay
• Tên người cho vay
• Ngày vay & Hạn trả
• Lãi suất (nếu có)
• Ghi chú mục đích vay

**2️⃣ Cho vay (Người khác nợ bạn)**
• Tab "Khoản nợ" → Thêm mới
• Chọn loại: "Cho vay"
• Nhập số tiền cho vay
• Tên người vay
• Ngày cho vay & Hạn thu
• Lãi suất (nếu có)
• Ghi chú

━━━━━━━━━━━━━━━━━━━━━

**💡 TÍNH NĂNG:**
• Theo dõi tiến độ trả nợ
• Nhắc nhở khi đến hạn
• Tính lãi suất tự động
• Xem tổng nợ phải trả/phải thu
• Lịch sử giao dịch trả nợ

━━━━━━━━━━━━━━━━━━━━━

⚠️ **Lưu ý:** Quản lý nợ tốt giúp tránh mất tiền và mối quan hệ!
""",
            "image": "media/images/khoan_no.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_9"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_11")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        11: {  # BƯỚC 11: Đầu tư
            "title": "📈 BƯỚC 11: Hướng dẫn Đầu tư",
            "text": """
**📈 BƯỚC 11: Hướng dẫn quản lý Đầu tư**

Theo dõi các khoản đầu tư để biết tài sản tăng/giảm thế nào!

━━━━━━━━━━━━━━━━━━━━━

**🔹 CÁC LOẠI ĐẦU TƯ:**

**Chứng khoán / Crypto / Vàng / BĐS**
• Tab "Đầu tư" → Thêm mới
• Chọn loại tài sản
• Nhập số tiền đầu tư ban đầu
• Giá trị hiện tại
• Ngày mua
• Số lượng (cổ phiếu, gram vàng...)
• Ghi chú (mã cổ phiếu, địa chỉ BĐS...)

**Quỹ đầu tư / Tiết kiệm ngân hàng**
• Thêm thông tin kỳ hạn
• Lãi suất (%/năm)
• Ngày đáo hạn
• Tự động tính lãi

━━━━━━━━━━━━━━━━━━━━━

**💡 TÍNH NĂNG:**
• Xem tổng giá trị danh mục đầu tư
• Tính lãi/lỗ tự động (%)
• So sánh ROI giữa các khoản
• Biểu đồ phân bổ tài sản
• Nhắc nhở khi đến hạn rút
• Lịch sử giá trị theo thời gian

━━━━━━━━━━━━━━━━━━━━━

📊 **Lợi ích:** Biết rõ tài sản đang sinh lời hay mất giá!
""",
            "image": "media/images/dau_tu.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_10"),
                 InlineKeyboardButton("Tiếp ▶️", callback_data="usage_step_12")],
                [InlineKeyboardButton("« Menu hướng dẫn", callback_data="show_guide_choice")]
            ]
        },
        12: {  # BƯỚC 12: Tài sản
            "title": "🏠 BƯỚC 12: Hướng dẫn Tài sản",
            "text": """
**🏠 BƯỚC 12: Hướng dẫn quản lý Tài sản**

Quản lý toàn bộ tài sản để biết mình giàu đến đâu!

━━━━━━━━━━━━━━━━━━━━━

**🔹 CÁC LOẠI TÀI SẢN:**

**1️⃣ Tài sản cố định**
• Nhà đất, xe cộ, máy móc
• Tab "Tài sản" → Thêm mới
• Nhập tên tài sản (VD: Nhà HCM)
• Giá trị hiện tại
• Ngày mua & Giá mua
• Tỷ lệ khấu hao (tự động tính)

**2️⃣ Tài sản lưu động**
• Tiền mặt, tiền gửi ngân hàng
• Vàng, ngoại tệ
• Tự động đồng bộ từ tài khoản

**3️⃣ Tài sản vô hình**
• Bản quyền, thương hiệu
• Cổ phần công ty
• Giá trị ước tính

━━━━━━━━━━━━━━━━━━━━━

**💡 TÍNH NĂNG:**
• Xem tổng tài sản ròng (Net Worth)
• Theo dõi tăng/giảm theo thời gian
• Phân loại tài sản theo nhóm
• Tính khấu hao tự động
• Biểu đồ phân bổ tài sản
• Xuất báo cáo tài sản PDF/Excel

━━━━━━━━━━━━━━━━━━━━━

✅ **Hoàn thành!** Bạn đã biết cách sử dụng đầy đủ Freedom Wallet!

🎉 **Bắt đầu hành trình tự do tài chính ngay hôm nay!**

💬 **Câu hỏi?** Liên hệ Admin qua bot hoặc tham gia Community!
""",
            "image": "media/images/tai_san.jpg",
            "keyboard": [
                [InlineKeyboardButton("🔄 Xem lại từ đầu", callback_data="usage_step_1")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="usage_step_11")],
                [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
            ]
        }
    }
    
    step_data = steps.get(current_step, steps[1])
    
    # Delete previous message and send new one (avoid "no text to edit" error)
    try:
        await query.message.delete()
    except:
        pass
    
    # Send with image if available
    if step_data["image"]:
        from pathlib import Path
        image_path = Path(step_data["image"])
        
        try:
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=photo,
                    caption=f"**{step_data['title']}**\n\n{step_data['text']}",
                    reply_markup=InlineKeyboardMarkup(step_data["keyboard"]),
                    parse_mode="Markdown"
                )
        except Exception as e:
            # Fallback to text if image fails
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"**{step_data['title']}**\n\n{step_data['text']}\n\n⚠️ (Không tải được hình: {e})",
                reply_markup=InlineKeyboardMarkup(step_data["keyboard"]),
                parse_mode="Markdown"
            )
    else:
        # Text only
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"**{step_data['title']}**\n\n{step_data['text']}",
            reply_markup=InlineKeyboardMarkup(step_data["keyboard"]),
            parse_mode="Markdown"
        )


async def show_webapp_usage_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📖 Hướng dẫn sử dụng Web App - Sau khi đã deploy xong"""
    query = update.callback_query
    await query.answer()
    
    message = """
📱 **HƯỚNG DẪN SỬ DỤNG WEB APP**

Sau khi đã deploy xong, đây là cách sử dụng Web App:

━━━━━━━━━━━━━━━━━━━━━

**🌐 MỞ WEB APP**

1. Click vào link Web App của bạn
2. Hoặc mở Google Sheet → Extensions → Apps Script → Deploy

Trang chủ hiển thị:
• 💰 Số dư hiện tại
• 📊 Biểu đồ thu chi
• 📈 Xu hướng chi tiêu

━━━━━━━━━━━━━━━━━━━━━

**✏️ GHI GIAO DỊCH**

**Tab "Giao dịch":**
• Chọn loại: Thu / Chi
• Nhập số tiền
• Chọn danh mục (Ăn uống, Di chuyển...)
• Thêm ghi chú (optional)
• Click "Lưu"

**Ghi nhanh:** Dùng bot Telegram
• Gửi: `Cà phê 35k`
• Bot tự động lưu vào Sheet!

━━━━━━━━━━━━━━━━━━━━━

**📊 XEM BÁO CÁO**

**Tab "Dashboard":**
• Tổng quan tháng này
• So sánh với tháng trước
• Top 5 danh mục chi nhiều nhất

**Tab "Báo cáo":**
• Báo cáo theo tháng/quý/năm
• Biểu đồ chi tiết
• Xuất Excel

━━━━━━━━━━━━━━━━━━━━━

**💰 QUẢN LÝ LỌ TIỀN**

**Tab "Hũ tiết kiệm":**
• Tạo hũ mới (Mua xe, Du lịch...)
• Chuyển tiền vào hũ
• Theo dõi tiến độ
• Đặt mục tiêu

━━━━━━━━━━━━━━━━━━━━━

**⚙️ CÀI ĐẶT**

**Tab "Settings":**
• Thêm/sửa danh mục
• Đổi mật khẩu Web App
• Cài đặt ngôn ngữ
• Chọn currency (VNĐ, USD...)

━━━━━━━━━━━━━━━━━━━━━

**💡 TIPS SỬ DỤNG HIỆU QUẢ**

✅ **Ghi đều đặn:** Nhập giao dịch ngay sau khi chi tiêu
✅ **Dùng bot:** Gửi Telegram nhanh hơn mở Web App
✅ **Xem báo cáo cuối tháng:** Phân tích để tiết kiệm
✅ **Đặt mục tiêu:** Tạo hũ tiết kiệm rõ ràng
✅ **Backup định kỳ:** Export Excel mỗi tháng

━━━━━━━━━━━━━━━━━━━━━

**🆘 LỖI THƯỜNG GẶP**

❌ **"Web App báo lỗi 401"**
→ Kiểm tra lại mật khẩu

❌ **"Không thấy giao dịch mới"**
→ Refresh trang (F5)

❌ **"Bot không đồng bộ với Web App"**
→ Kiểm tra kết nối Sheet ID

━━━━━━━━━━━━━━━━━━━━━

🎓 **Cần hỗ trợ thêm?**
• Xem hướng dẫn Deploy
• Liên hệ Admin
• Tham gia VIP Group
"""
    
    keyboard = [
        [InlineKeyboardButton("🚀 Xem hướng dẫn Deploy", callback_data="show_deploy_guide")],
        [InlineKeyboardButton("📁 Mở Hệ thống của tôi", callback_data="my_system_menu")],
        [InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_admin")],
        [InlineKeyboardButton("« Menu chính", callback_data="show_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


# ═══════════════════════════════════════════════════════════════════════
# Additional Menu Handlers (System, Help, Settings callbacks)
# ═══════════════════════════════════════════════════════════════════════

async def handle_advanced_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📖 Hướng dẫn nâng cao - Chi tiết về chỉnh sửa Sheet/Web App"""
    query = update.callback_query
    await query.answer()
    
    message = """
📖 **HƯỚNG DẪN NÂNG CAO**

━━━━━━━━━━━━━━━━━━━━━

**🔧 Chỉnh sửa Google Sheet**

1. **Thêm/xóa hũ tiền:**
   • Vào sheet "Hũ tiền"
   • Thêm dòng mới hoặc xóa dòng cũ
   • Tổng % phải = 100%

2. **Thêm danh mục:**
   • Vào sheet "Danh mục"
   • Thêm tên danh mục + loại (Thu/Chi)
   • Gắn với hũ tiền tương ứng

3. **Sửa giao dịch:**
   • Vào sheet "Giao dịch"
   • Sửa trực tiếp các cột

━━━━━━━━━━━━━━━━━━━━━

**⚠️ LƯU Ý QUAN TRỌNG:**

• KHÔNG xóa header (dòng đầu tiên)
• KHÔNG thay đổi tên sheet
• KHÔNG xóa công thức trong ô
• Backup trước khi sửa lớn

━━━━━━━━━━━━━━━━━━━━━

📚 **Tài liệu chi tiết:**
🔗 [Link tài liệu](https://example.com/docs)

💡 Cần hỗ trợ? Dùng /support
"""
    
    keyboard = [
        [InlineKeyboardButton("« Quay lại Hệ thống", callback_data="my_system_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_check_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔍 Kiểm tra kết nối Sheet/Web App"""
    query = update.callback_query
    await query.answer()
    
    db = next(get_db())
    try:
        user = db.query(User).filter(User.telegram_id == query.from_user.id).first()
        
        sheet_status = "❌ Chưa kết nối"
        webapp_status = "❌ Chưa kết nối"
        
        if user:
            if user.spreadsheet_id:
                sheet_status = "✅ Đã kết nối"
            if user.web_app_url:
                webapp_status = "✅ Đã kết nối"
        
        message = f"""
🔍 **KIỂM TRA KẾT NỐI**

━━━━━━━━━━━━━━━━━━━━━

**📋 Google Sheet:** {sheet_status}
**🔗 Web App:** {webapp_status}

━━━━━━━━━━━━━━━━━━━━━

💡 **Nếu chưa kết nối:**
1. Vào /start để cài đặt
2. Làm theo hướng dẫn từng bước
3. Test lại sau khi setup xong

🐛 **Nếu đã kết nối nhưng lỗi:**
• Kiểm tra quyền truy cập Sheet
• Kiểm tra Web App đã deploy chưa
• Dùng /support để báo lỗi chi tiết
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Kết nối lại", callback_data="reconnect_system")],
            [InlineKeyboardButton("« Quay lại", callback_data="my_system_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_update_sheet_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔄 Cập nhật Sheet ID"""
    query = update.callback_query
    await query.answer()
    
    message = """
🔄 **CẬP NHẬT SHEET ID**

━━━━━━━━━━━━━━━━━━━━━

Để cập nhật Sheet ID mới:

1️⃣ Copy Sheet ID từ URL:
   `https://docs.google.com/spreadsheets/d/`**`[SHEET_ID]`**`/edit`

2️⃣ Dùng lệnh:
   `/update_sheet_id [SHEET_ID mới]`

━━━━━━━━━━━━━━━━━━━━━

💡 **Ví dụ:**
```
/update_sheet_id 1ABC...xyz
```

⚠️ **Lưu ý:**
• Sheet mới phải có cấu trúc giống cũ
• Dữ liệu cũ không tự động chuyển
"""
    
    keyboard = [
        [InlineKeyboardButton("« Quay lại", callback_data="my_system_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_setup_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔔 Cài đặt nhắc nhở định kỳ"""
    query = update.callback_query
    await query.answer()
    
    message = """
🔔 **CÀI ĐẶT NHẮC NHỞ**

━━━━━━━━━━━━━━━━━━━━━

Bot có thể nhắc bạn ghi chi tiêu hàng ngày!

**📅 Thời gian nhắc:**
• Sáng: 9:00 AM
• Trưa: 12:00 PM  
• Tối: 8:00 PM

**🔕 Tắt nhắc nhở:**
Dùng lệnh `/reminder off`

━━━━━━━━━━━━━━━━━━━━━

💡 **Chọn thời gian phù hợp với lịch trình của bạn!**
"""
    
    keyboard = [
        [InlineKeyboardButton("🌅 Nhắc Sáng (9:00)", callback_data="reminder_morning")],
        [InlineKeyboardButton("☀️ Nhắc Trưa (12:00)", callback_data="reminder_noon")],
        [InlineKeyboardButton("🌙 Nhắc Tối (20:00)", callback_data="reminder_evening")],
        [InlineKeyboardButton("🔕 Tắt nhắc nhở", callback_data="reminder_off")],
        [InlineKeyboardButton("« Quay lại", callback_data="settings_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_setup_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """⚠️ Cài đặt cảnh báo chi tiêu"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        alert_status = "✅ Bật" if user and getattr(user, 'alert_enabled', False) else "🔕 Tắt"
        
        message = f"""
⚠️ **CÀI ĐẶT CẢNH BÁO**

━━━━━━━━━━━━━━━━━━━━━

**Trạng thái:** {alert_status}

Bot sẽ cảnh báo khi chi tiêu vượt ngưỡng!

**📊 Loại cảnh báo:**

1. **Cảnh báo theo ngày:**
   • Mức: 500k / ngày
   • Bot nhắc khi vượt

2. **Cảnh báo theo tuần:**
   • Mức: 2 triệu / tuần
   • Nhắc nếu tiêu quá

3. **Cảnh báo theo tháng:**
   • Mức: 8 triệu / tháng
   • Theo dõi ngân sách

━━━━━━━━━━━━━━━━━━━━━

💡 **Bạn có thể tùy chỉnh mức cảnh báo!**
"""
        
        keyboard = []
        if user and getattr(user, 'alert_enabled', False):
            keyboard.append([InlineKeyboardButton("🔕 Tắt cảnh báo", callback_data="alert_off")])
        else:
            keyboard.append([InlineKeyboardButton("✅ Bật cảnh báo", callback_data="alert_on")])
        
        keyboard.append([InlineKeyboardButton("📊 Cài mức cảnh báo", callback_data="set_alert_level")])
        keyboard.append([InlineKeyboardButton("« Quay lại", callback_data="settings_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_alert_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE, enable: bool):
    """Toggle alert on/off"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Add alert_enabled field if not exists
            if not hasattr(user.__class__, 'alert_enabled'):
                from sqlalchemy import Column, Boolean
                user.__class__.alert_enabled = Column(Boolean, default=False)
            
            user.alert_enabled = enable  # type: ignore
            db.commit()
        
        status = "✅ Bật" if enable else "🔕 Tắt"
        message = f"""
{"✅" if enable else "🔕"} **Đã {"bật" if enable else "tắt"} cảnh báo chi tiêu!**

Bot sẽ {"nhắc bạn" if enable else "không nhắc"} khi chi tiêu vượt ngưỡng đã đặt.

💡 Bạn có thể thay đổi bất cứ lúc nào trong Cài đặt!
"""
        
        keyboard = [[InlineKeyboardButton("« Quay lại", callback_data="setup_alerts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_set_alert_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set alert spending level"""
    query = update.callback_query
    await query.answer()
    
    message = """
📊 **CÀI MỨC CẢNH BÁO**

━━━━━━━━━━━━━━━━━━━━━

**Tính năng đang phát triển...**

Hiện tại mức cảnh báo mặc định:
• 500k / ngày
• 2 triệu / tuần
• 8 triệu / tháng

━━━━━━━━━━━━━━━━━━━━━

💡 **Sắp ra mắt:**
Tùy chỉnh mức cảnh báo theo nhu cầu!

Gửi góp ý: /support
"""
    
    keyboard = [[InlineKeyboardButton("« Quay lại", callback_data="setup_alerts")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_manage_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔕 Quản lý thông báo"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        notif_status = "✅ Bật" if user and getattr(user, 'notifications_enabled', True) else "🔕 Tắt"
        
        message = f"""
🔕 **QUẢN LÝ THÔNG BÁO**

━━━━━━━━━━━━━━━━━━━━━

**Trạng thái:** {notif_status}

**Loại thông báo:**

✅ Ghi giao dịch thành công
✅ Nhắc nhở ghi chi tiêu
✅ Cảnh báo vượt ngân sách
✅ Cập nhật từ hệ thống

━━━━━━━━━━━━━━━━━━━━━

**Tùy chỉnh:**
• Bật/tắt từng loại thông báo
• Giữ lại thông báo quan trọng
• Tắt tất cả nếu không muốn bị quấy rầy

💡 **Khuyến nghị:** Bật thông báo giao dịch
"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Bật tất cả", callback_data="notif_all_on")],
            [InlineKeyboardButton("🔕 Tắt tất cả", callback_data="notif_all_off")],
            [InlineKeyboardButton("⚙️ Tùy chỉnh chi tiết", callback_data="notif_custom")],
            [InlineKeyboardButton("« Quay lại", callback_data="settings_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_notif_all_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bật tất cả thông báo"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Add notifications_enabled field if not exists
            if not hasattr(user.__class__, 'notifications_enabled'):
                from sqlalchemy import Column, Boolean
                user.__class__.notifications_enabled = Column(Boolean, default=True)
            
            user.notifications_enabled = True  # type: ignore
            user.reminder_enabled = True
            db.commit()
        
        message = """
✅ **ĐÃ BẬT TẤT CẢ THÔNG BÁO!**

Bot sẽ gửi thông báo cho bạn về:
• Giao dịch được ghi thành công
• Nhắc nhở ghi chi tiêu hàng ngày
• Cảnh báo khi vượt ngân sách
• Cập nhật tính năng mới

━━━━━━━━━━━━━━━━━━━━━

💡 Bạn có thể tắt bất cứ lúc nào trong Cài đặt!
"""
        
        keyboard = [[InlineKeyboardButton("« Quay lại", callback_data="manage_notifications")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_notif_all_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tắt tất cả thông báo"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Add notifications_enabled field if not exists
            if not hasattr(user.__class__, 'notifications_enabled'):
                from sqlalchemy import Column, Boolean
                user.__class__.notifications_enabled = Column(Boolean, default=True)
            
            user.notifications_enabled = False  # type: ignore
            user.reminder_enabled = False
            db.commit()
        
        message = """
🔕 **ĐÃ TẮT TẤT CẢ THÔNG BÁO!**

Bot sẽ không gửi thông báo nữa.

Bạn vẫn có thể:
• Ghi giao dịch bình thường
• Xem báo cáo
• Sử dụng đầy đủ tính năng

━━━━━━━━━━━━━━━━━━━━━

💡 Bật lại bất cứ lúc nào trong Cài đặt!
"""
        
        keyboard = [[InlineKeyboardButton("« Quay lại", callback_data="manage_notifications")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_notif_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tùy chỉnh chi tiết thông báo"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        # Get current settings
        notif_enabled = getattr(user, 'notifications_enabled', True) if user else True
        reminder_enabled = user.reminder_enabled if user and hasattr(user, 'reminder_enabled') else False
        
        message = """
⚙️ **TÙY CHỈNH THÔNG BÁO**

━━━━━━━━━━━━━━━━━━━━━

**Bật/tắt từng loại:**

" "Nhắc nhở hàng ngày
   → Nhắc ghi chi tiêu
   
✅ Thông báo giao dịch
   → Xác nhận ghi thành công
   
✅ Cảnh báo ngân sách
   → Nhắc khi chi vượt mức
   
✅ Cập nhật hệ thống
   → Tính năng mới, bảo trì

━━━━━━━━━━━━━━━━━━━━━

💡 **Tính năng đang phát triển...**
Hiện tại chỉ có Bật/Tắt tất cả.

Gửi góp ý: /support
""".replace('" "', '🔕' if not reminder_enabled else '✅')
        
        keyboard = [
            [InlineKeyboardButton("🔔 Cài đặt nhắc nhở", callback_data="setup_reminders")],
            [InlineKeyboardButton("« Quay lại", callback_data="manage_notifications")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_reconnect_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔄 Kết nối lại Sheet/Web App"""
    query = update.callback_query
    await query.answer()
    
    message = """
🔄 **KẾT NỐI LẠI HỆ THỐNG**

━━━━━━━━━━━━━━━━━━━━━

**Khi nào cần kết nối lại?**

• Bot không ghi được giao dịch
• Lỗi "Không tìm thấy Sheet"
• Web App không load dữ liệu
• Thay đổi Sheet/Web App mới

━━━━━━━━━━━━━━━━━━━━━

**Cách kết nối lại:**

1️⃣ Dùng lệnh `/start` để setup lại
2️⃣ Hoặc cập nhật từng phần:
   • `/update_sheet_id [ID]`
   • `/update_webapp_url [URL]`

━━━━━━━━━━━━━━━━━━━━━

💡 **Lưu ý:** Kết nối lại không mất dữ liệu cũ!
"""
    
    keyboard = [
        [InlineKeyboardButton("🔄 Setup lại từ đầu", callback_data="start_registration")],
        [InlineKeyboardButton("« Quay lại", callback_data="settings_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_show_deploy_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📖 Hướng dẫn Deploy Web App"""
    query = update.callback_query
    await query.answer()
    
    message = """
📖 **HƯỚNG DẪN DEPLOY WEB APP**

━━━━━━━━━━━━━━━━━━━━━

**Bước 1: Mở Apps Script**
• Vào Google Sheet → Extensions → Apps Script

**Bước 2: Deploy**
• Click Deploy → New deployment
• Type: Web app
• Execute as: Me
• Who has access: Anyone

**Bước 3: Copy URL**
• Copy Web app URL
• Dán vào bot: `/update_webapp_url [URL]`

━━━━━━━━━━━━━━━━━━━━━

📹 **Video hướng dẫn:**
🔗 [Xem video](https://youtube.com/example)

💡 Gặp khó khăn? Dùng /support
"""
    
    keyboard = [
        [InlineKeyboardButton("« Quay lại", callback_data="help_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_show_contribution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💝 Menu Đóng góp"""
    query = update.callback_query
    await query.answer()
    
    message = """
💝 **ĐÓNG GÓP CHO FREEDOM WALLET**

Trân trọng biết ơn bạn đã quan tâm đến sự phát triển của Freedom Wallet! 🙏

━━━━━━━━━━━━━━━━━━━━━

**🎯 Chọn cách đóng góp:**

**1️⃣ Đóng góp ý tưởng**
   Gửi ý tưởng tính năng mới, cải tiến UX

**2️⃣ Báo lỗi**
   Phát hiện bug? Báo ngay để được fix!

**3️⃣ Đóng góp tài chính**
   Hỗ trợ chi phí phát triển & duy trì

**4️⃣ Giới thiệu bạn bè**
   Chia sẻ Freedom Wallet với người thân

━━━━━━━━━━━━━━━━━━━━━

**🌟 Roadmap 2026:**

• 🤖 AI phân tích chi tiêu thông minh
• 📊 Báo cáo đa chiều nâng cao  
• 🔔 Nhắc nhở thông minh theo ngữ cảnh
• 💎 Tính năng Premium mới
• 🌐 Web App tích hợp sâu hơn

💡 **Ý tưởng của bạn có thể trở thành tính năng tiếp theo!**
"""
    
    keyboard = [
        [InlineKeyboardButton("💡 Đóng góp ý tưởng", callback_data="contribute_idea")],
        [InlineKeyboardButton("🐛 Báo lỗi", callback_data="report_bug")],
        [InlineKeyboardButton("💰 Đóng góp tài chính", callback_data="financial_support")],
        [InlineKeyboardButton("🎁 Giới thiệu bạn bè", callback_data="show_referral")],
        [InlineKeyboardButton("« Quay lại", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Check if message has photo
    if query.message.photo:
        try:
            await query.message.delete()
        except:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def handle_contribute_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💡 Đóng góp ý tưởng"""
    query = update.callback_query
    await query.answer()
    
    message = """
💡 **ĐÓNG GÓP Ý TƯỞNG**

━━━━━━━━━━━━━━━━━━━━━

Trân trọng biết ơn bạn muốn góp phần cải thiện Freedom Wallet! 🙏

**📝 Gửi ý tưởng của bạn:**

1️⃣ **Gõ trực tiếp:**
   Gửi tin nhắn bắt đầu với `#ytưởng`
   Ví dụ: `#ytưởng Thêm biểu đồ chi tiêu theo danh mục`

2️⃣ **Hoặc dùng lệnh:**
   `/support [mô tả ý tưởng]`

━━━━━━━━━━━━━━━━━━━━━

**💭 Gợi ý nội dung:**

• Tính năng mới bạn muốn có
• Cải tiến giao diện/UX
• Tích hợp với công cụ khác
• Báo cáo/thống kê mới

━━━━━━━━━━━━━━━━━━━━━

✨ **Ý tưởng hay sẽ được ưu tiên phát triển!**

📊 Admin sẽ tổng hợp và cập nhật vào roadmap.
"""
    
    keyboard = [[InlineKeyboardButton("« Quay lại", callback_data="show_contribution")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_financial_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💰 Đóng góp tài chính"""
    query = update.callback_query
    await query.answer()
    
    # Delete old message to send photo with caption
    try:
        await query.message.delete()
    except:
        pass
    
    message = """
💰 **ĐÓNG GÓP TÀI CHÍNH**

Trân trọng biết ơn bạn đã muốn hỗ trợ chi phí phát triển & duy trì Freedom Wallet! 🙏

━━━━━━━━━━━━━━━━━━━━━

**🏦 THÔNG TIN CHUYỂN KHOẢN:**

**Ngân hàng:** OCB (Phương Đông)
**Số TK:** 0814267626
**Chủ TK:** PHAM THANH TUAN
**Nội dung:** FW [Tên của bạn]

━━━━━━━━━━━━━━━━━━━━━

**💝 Mọi đóng góp đều có ý nghĩa:**

• Duy trì server & database
• Phát triển tính năng mới
• Hỗ trợ kỹ thuật 24/7
• Cải thiện trải nghiệm người dùng

━━━━━━━━━━━━━━━━━━━━━

 Trân trọng biết ơn!
"""
    
    keyboard = [[InlineKeyboardButton("« Quay lại", callback_data="show_contribution")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send QR code image with caption
    from pathlib import Path
    qr_path = Path(__file__).parent.parent.parent.parent / "media" / "images" / "donation_qr_ocb.png"
    
    try:
        with open(qr_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo,
                caption=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            logger.info(f"✅ Sent donation QR code to user {query.from_user.id}")
    except FileNotFoundError as e:
        logger.error(f"❌ QR code not found: {qr_path} - {e}")
        # Fallback if QR not found
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"{message}\n\n⚠️ QR code đang được cập nhật...",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"❌ Error sending donation QR: {e}", exc_info=True)
        # Fallback for any other error
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


async def handle_show_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎁 Giới thiệu bạn bè"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User
    user_id = update.effective_user.id
    username = update.effective_user.username or "friend"
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.referral_code:
            # Generate referral code if not exists
            import random
            import string
            referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            if user:
                user.referral_code = referral_code
                db.commit()
        else:
            referral_code = user.referral_code
        
        ref_link = f"https://t.me/FreedomWalletBot?start={referral_code}"
        ref_count = user.referral_count if user else 0
        
        message = f"""
🎁 **GIỚI THIỆU BẠN BÈ**

━━━━━━━━━━━━━━━━━━━━━

**Link giới thiệu của bạn:**
`{ref_link}`

**Số người đã tham gia:** {ref_count}

━━━━━━━━━━━━━━━━━━━━━

**🎯 Chia sẻ ngay:**

Sao chép link và gửi cho bạn bè qua:
• Telegram
• Facebook
• Zalo
• Email

━━━━━━━━━━━━━━━━━━━━━

**💝 TẠI SAO NÊN CHIA SẺ?**

Freedom Wallet được tạo ra với sứ mệnh:
**Giúp hàng triệu người có kế hoạch xài tiền có ý nghĩa, biết rõ bản thân đang ở cấp độ tài chính nào và đơn giản đạt Tự do Tài chính hơn**

━━━━━━━━━━━━━━━━━━━━━

**🙏 Freedom Wallet được tạo ra để giúp mỗi người:**

Tăng sự rõ ràng về tiền

Tăng kỷ luật tài chính mỗi ngày

Tăng khả năng ra quyết định đúng

Tăng tốc độ tiến tới tự do tài chính

━━━━━━━━━━━━━━━━━━━━━

**🌱 Kiến tạo cộng đồng tự do tài chính**

Khi bạn gửi hệ thống này cho ai đó, bạn có thể giúp họ:

• Tăng nhận thức về dòng tiền của mình
• Có kế hoạch chi tiêu rõ ràng hơn 
• Tăng khả năng kiểm soát chi tiêu
• Tăng mức tích lũy theo thời gian
• Tăng sự tự tin trong quyết định tài chính

Không cần hứa hẹn lớn lao.
Chỉ cần giúp một người quản lý tiền tốt hơn hôm qua là đủ.

Khi nhiều người tăng trưởng cùng nhau,
một cộng đồng tài chính lành mạnh sẽ hình thành.

Nếu bạn tin điều này có ích,
bạn có thể chia sẻ.
━━━━━━━━━━━━━━━━━━━━━

💡 **Mẹo:** Chia sẻ trong group Zalo/FB về tài chính cá nhân!
"""
        
        keyboard = [
            [InlineKeyboardButton("📱 Share qua Telegram", url=f"https://t.me/share/url?url={ref_link}&text=Quản lý tài chính thông minh với Freedom Wallet!")],
            [InlineKeyboardButton("📊 Xem thống kê giới thiệu", callback_data="referral_stats")],
            [InlineKeyboardButton("« Quay lại", callback_data="show_contribution")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_referral_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Xem thống kê giới thiệu"""
    query = update.callback_query
    await query.answer()
    
    from app.utils.database import SessionLocal, User, Referral
    user_id = update.effective_user.id
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            await query.edit_message_text("❌ User not found")
            return
        
        ref_count = user.referral_count or 0
        referral_code = user.referral_code or "N/A"
        
        # Get list of referred users
        referrals = db.query(Referral).filter(Referral.referrer_id == user_id).all()
        
        # Calculate rewards
        free_unlocked = user.is_free_unlocked
        vip_tier = user.vip_tier or "None"
        
        message = f"""
📊 **THỐNG KÊ GIỚI THIỆU**

━━━━━━━━━━━━━━━━━━━━━

**Mã giới thiệu:** `{referral_code}`
**Số người tham gia:** {ref_count}

━━━━━━━━━━━━━━━━━━━━━

**🎁 ƯU ĐÃI ĐẠT ĐƯỢC:**

{'✅' if free_unlocked else '⏳'} FREE tier (2+ người)
{'✅' if vip_tier == 'RISING_STAR' else '⏳'} VIP Rising Star (10+ người)
{'✅' if vip_tier == 'SUPER_VIP' else '⏳'} SUPER VIP (50+ người)
{'✅' if vip_tier == 'LEGEND' else '⏳'} LEGEND (100+ người)

━━━━━━━━━━━━━━━━━━━━━

**📈 TIẾN TRÌNH:**

"""
        
        # Add progress bars
        if ref_count < 2:
            message += f"→ FREE: {ref_count}/2 người\n"
        elif ref_count < 10:
            message += f"✅ FREE: Đã mở khóa!\n→ RISING STAR: {ref_count}/10 người\n"
        elif ref_count < 50:
            message += f"✅ RISING STAR: Đã đạt!\n→ SUPER VIP: {ref_count}/50 người\n"
        elif ref_count < 100:
            message += f"✅ SUPER VIP: Đã đạt!\n→ LEGEND: {ref_count}/100 người\n"
        else:
            message += f"🏆 LEGEND: Đã đạt! Bạn là huyền thoại!\n"
        
        message += """
━━━━━━━━━━━━━━━━━━━━━

💡 **Cách tăng nhanh:**
• Chia sẻ trong group Zalo/FB về tài chính
• Post trên timeline kèm trải nghiệm
• Gửi trực tiếp cho bạn bè quan tâm
"""
        
        keyboard = [
            [InlineKeyboardButton("🔗 Lấy link giới thiệu", callback_data="show_referral")],
            [InlineKeyboardButton("« Quay lại", callback_data="show_referral")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    finally:
        db.close()


async def handle_report_bug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🐛 Báo lỗi"""
    query = update.callback_query
    await query.answer()
    
    message = """
🐛 **BÁO LỖI**

━━━━━━━━━━━━━━━━━━━━━

**Cách báo lỗi hiệu quả:**

1️⃣ **Mô tả lỗi:**
   • Lỗi xảy ra khi nào?
   • Thao tác gì trước đó?
   • Lỗi có lặp lại không?

2️⃣ **Thông tin hệ thống:**
   • Screenshot lỗi
   • Sheet ID (nếu liên quan)
   • Web App URL (nếu liên quan)

3️⃣ **Gửi qua:**
   • Lệnh: `/support [mô tả lỗi]`
   • Hoặc liên hệ admin trực tiếp

━━━━━━━━━━━━━━━━━━━━━

⚡ **Lỗi khẩn cấp?** Tag @admin ngay!

💡 Báo lỗi chi tiết = Fix nhanh hơn!
"""
    
    keyboard = [
        [InlineKeyboardButton("💬 Gửi báo lỗi ngay", callback_data="send_bug_report")],
        [InlineKeyboardButton("« Quay lại", callback_data="show_contribution")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def handle_contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💬 Liên hệ Admin"""
    query = update.callback_query
    await query.answer()
    
    message = """
💬 **LIÊN HỆ ADMIN**

━━━━━━━━━━━━━━━━━━━━━

**📧 Kênh hỗ trợ:**

• **Telegram:** @FreedomWalletSupport
• **Email:** support@freedomwallet.vn
• **Facebook:** fb.com/FreedomWallet

━━━━━━━━━━━━━━━━━━━━━

**🕐 Thời gian hỗ trợ:**
• Thứ 2 - Thứ 6: 9:00 - 18:00
• Thứ 7: 9:00 - 12:00
• Chủ nhật: Nghỉ

━━━━━━━━━━━━━━━━━━━━━

**⚡ Khẩn cấp?**
Dùng lệnh `/support` để gửi ticket
Admin sẽ trả lời trong 24h

💡 Trước khi liên hệ, check FAQ xem đã có câu trả lời chưa!
"""
    
    keyboard = [
        [InlineKeyboardButton("💬 Gửi hỗ trợ ticket", callback_data="send_support_ticket")],
        [InlineKeyboardButton("« Quay lại", callback_data="help_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


def register_main_menu_handlers(application):
    """Register main menu handlers"""
    
    # Main menu
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern="^show_main_menu$"))
    
    # New menu structure (behavior-focused)
    application.add_handler(CallbackQueryHandler(show_quick_record_menu, pattern="^quick_record_menu$"))
    application.add_handler(CallbackQueryHandler(show_quick_report_menu, pattern="^quick_report_menu$"))
    application.add_handler(CallbackQueryHandler(show_balance, pattern="^show_balance$"))
    application.add_handler(CallbackQueryHandler(show_accounts_report, pattern="^show_accounts_report$"))
    application.add_handler(CallbackQueryHandler(show_jars_report, pattern="^show_jars_report$"))
    application.add_handler(CallbackQueryHandler(show_monthly_income_expense, pattern="^show_monthly_income_expense$"))
    application.add_handler(CallbackQueryHandler(show_my_system_menu, pattern="^my_system_menu$"))
    application.add_handler(CallbackQueryHandler(show_help_menu, pattern="^help_menu$"))
    application.add_handler(CallbackQueryHandler(show_settings_menu, pattern="^settings_menu$"))
    
    # Guide menu handlers
    application.add_handler(CallbackQueryHandler(show_guide_choice, pattern="^show_guide_choice$"))
    application.add_handler(CallbackQueryHandler(show_webapp_usage_steps, pattern="^(usage_step_\\d+|show_webapp_usage_steps)$"))
    application.add_handler(CallbackQueryHandler(show_webapp_usage_guide, pattern="^show_webapp_usage_guide$"))
    
    # Additional handlers for System, Help, Settings menus
    application.add_handler(CallbackQueryHandler(handle_advanced_guide, pattern="^advanced_guide$"))
    application.add_handler(CallbackQueryHandler(handle_check_connection, pattern="^check_connection$"))
    application.add_handler(CallbackQueryHandler(handle_update_sheet_id, pattern="^update_sheet_id$"))
    application.add_handler(CallbackQueryHandler(handle_setup_reminders, pattern="^setup_reminders$"))
    application.add_handler(CallbackQueryHandler(handle_setup_alerts, pattern="^setup_alerts$"))
    application.add_handler(CallbackQueryHandler(lambda u, c: handle_alert_toggle(u, c, True), pattern="^alert_on$"))
    application.add_handler(CallbackQueryHandler(lambda u, c: handle_alert_toggle(u, c, False), pattern="^alert_off$"))
    application.add_handler(CallbackQueryHandler(handle_set_alert_level, pattern="^set_alert_level$"))
    application.add_handler(CallbackQueryHandler(handle_manage_notifications, pattern="^manage_notifications$"))
    application.add_handler(CallbackQueryHandler(handle_notif_all_on, pattern="^notif_all_on$"))
    application.add_handler(CallbackQueryHandler(handle_notif_all_off, pattern="^notif_all_off$"))
    application.add_handler(CallbackQueryHandler(handle_notif_custom, pattern="^notif_custom$"))
    application.add_handler(CallbackQueryHandler(handle_reconnect_system, pattern="^reconnect_system$"))
    application.add_handler(CallbackQueryHandler(handle_show_deploy_guide, pattern="^show_deploy_guide$"))
    application.add_handler(CallbackQueryHandler(handle_show_contribution, pattern="^show_contribution$"))
    application.add_handler(CallbackQueryHandler(handle_contribute_idea, pattern="^contribute_idea$"))
    application.add_handler(CallbackQueryHandler(handle_financial_support, pattern="^financial_support$"))
    application.add_handler(CallbackQueryHandler(handle_show_referral, pattern="^show_referral$"))
    application.add_handler(CallbackQueryHandler(handle_referral_stats, pattern="^referral_stats$"))
    application.add_handler(CallbackQueryHandler(handle_report_bug, pattern="^report_bug$"))
    application.add_handler(CallbackQueryHandler(handle_contact_admin, pattern="^contact_admin$"))
    
    logger.info("✅ Main menu handlers registered")
