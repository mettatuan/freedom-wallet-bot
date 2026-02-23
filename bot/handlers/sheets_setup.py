"""
Google Sheets Setup - Premium onboarding wizard
Guide user to connect their Google Sheets
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from bot.utils.database import get_user_by_id, SessionLocal, User, run_sync
from bot.services.sheets_reader import SheetsReader
from bot.services.analytics import Analytics
from datetime import datetime
import re
import os


def _save_spreadsheet_sync(user_id: int, spreadsheet_id: str) -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.spreadsheet_id = spreadsheet_id
            user.sheets_connected_at = datetime.now()
            db.commit()
    finally:
        db.close()


def _disconnect_sheets_sync(user_id: int):
    """Clears spreadsheet_id. Returns old spreadsheet_id string if one existed, else None."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.spreadsheet_id:
            return None
        old_id = user.spreadsheet_id
        user.spreadsheet_id = None
        user.sheets_connected_at = None
        db.commit()
        return old_id
    finally:
        db.close()


async def cmd_get_service_account_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show service account email for manual sharing"""
    import json
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'google_service_account.json')
    
    if not os.path.exists(creds_path):
        await update.message.reply_text(
            "❌ **Service account chưa được cấu hình!**\n\n"
            "Bot chưa có file `google_service_account.json`.\n\n"
            "**Bạn có thể dùng Quick Record thay thế:**\n"
            "1. Copy template về Drive\n"
            "2. Deploy Web App: /taoweb\n"
            "3. Gõ: `chi 50k test`\n\n"
            "Không cần share với ai!",
            parse_mode="Markdown"
        )
        return
    
    try:
        with open(creds_path, 'r') as f:
            sa_data = json.load(f)
            sa_email = sa_data.get('client_email', 'Unknown')
            project_id = sa_data.get('project_id', 'Unknown')
        
        await update.message.reply_text(
            f"📧 **Service Account Email:**\n\n"
            f"`{sa_email}`\n\n"
            f"🔑 Project: `{project_id}`\n\n"
            f"**Cách share spreadsheet:**\n"
            f"1️⃣ Mở spreadsheet của bạn\n"
            f"2️⃣ Click **Share** (góc trên phải)\n"
            f"3️⃣ Copy email trên → Paste vào\n"
            f"4️⃣ Quyền: **Viewer**\n"
            f"5️⃣ Bỏ tick \"Notify people\"\n"
            f"6️⃣ Click **Share**\n\n"
            f"Sau đó: `/setsheet [ID_SPREADSHEET_CỦA_BẠN]`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error reading service account: {e}")
        await update.message.reply_text(f"❌ Lỗi đọc service account: {str(e)}")


async def handle_connect_sheets_wizard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Premium onboarding: Connect Google Sheets wizard
    Called after user activates Premium trial
    """
    query = update.callback_query
    if query:
        await query.answer()
    
    # ✅ FIX: Check if user already has spreadsheet connected
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    if user and user.spreadsheet_id:
        # User already connected - show status
        connected_at = user.sheets_connected_at.strftime("%d/%m/%Y %H:%M") if user.sheets_connected_at else "Không rõ"
        
        message = f"""
📊 **Bạn đã kết nối Google Sheets rồi!**

🔗 Spreadsheet ID: `{user.spreadsheet_id[:20]}...`
📅 Kết nối lúc: {connected_at}

━━━━━━━━━━━━━━━━━━━━━
💡 **Bạn có thể:**
━━━━━━━━━━━━━━━━━━━━━

✅ Đổi sang Sheets khác
✅ Ngắt kết nối
✅ Kiểm tra trạng thái
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 Đổi sheet khác", callback_data="change_sheet")],
            [InlineKeyboardButton("🔌 Ngắt kết nối", callback_data="disconnect_sheet")],
            [InlineKeyboardButton("🏠 Menu", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(message, parse_mode="Markdown", reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
        
        return
    
    # User not connected - show wizard
    message = """
🔗 **KẾT NỐI GOOGLE SHEETS**

Để sử dụng tính năng Premium AI analysis và dashboard, bot cần đọc dữ liệu từ Google Sheets của bạn.

━━━━━━━━━━━━━━━━━━━━━
**📋 HƯỚNG DẪN 4 BƯỚC:**
━━━━━━━━━━━━━━━━━━━━━

**Bước 1:** Copy Template về Drive
[📄 Click để copy]

**Bước 2:** Share quyền View
👉 Trong Sheets, bấm "Share" (góc trên phải)
👉 Thêm email: `freedomwallet-bot@service-account.iam.gserviceaccount.com`
👉 Chọn quyền: **Viewer** (chỉ đọc)
👉 Bấm "Send"

**Bước 3:** Lấy Spreadsheet ID
URL: `docs.google.com/spreadsheets/d/[ID]/edit`
👉 Copy phần ID (44 ký tự)

**Bước 4:** Gửi ID cho bot
Gõ: `/setsheet [PASTE_ID]`

━━━━━━━━━━━━━━━━━━━━━
🔒 **BẢO MẬT:**
━━━━━━━━━━━━━━━━━━━━━

✅ Bot CHỈ có quyền **đọc** (Viewer)
✅ KHÔNG thể sửa/xóa data của bạn
✅ Bạn có thể thu hồi quyền bất cứ lúc nào

💡 **Tip:** Nếu không muốn share, bạn vẫn dùng được template bình thường, chỉ thiếu tính năng AI analysis tự động.
"""
    
    # Get template ID from environment
    template_id = os.getenv("TEMPLATE_SPREADSHEET_ID", "1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI")
    template_url = f"https://docs.google.com/spreadsheets/d/{template_id}/copy"
    
    keyboard = [
        [InlineKeyboardButton("📄 Copy Template", url=template_url)],
        [InlineKeyboardButton("📖 Xem video hướng dẫn", url="https://youtu.be/your-tutorial-video")],
        [InlineKeyboardButton("⏭️ Bỏ qua (dùng thử không kết nối)", callback_data="skip_sheets_connection")],
        [InlineKeyboardButton("🏠 Menu Premium", callback_data="premium_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(message, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=reply_markup)
    
    logger.info(f"User {update.effective_user.id} viewed Sheets connection wizard")


async def handle_set_sheet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /setsheet SPREADSHEET_ID
    Connect user's Google Sheets
    
    ✅ Works for ALL users (not just Premium)
    - With service account → Full AI analysis + Quick Record
    - Without service account → Quick Record only
    """
    user_id = update.effective_user.id
    logger.info(f"🔍 /setsheet command received from user {user_id}")
    logger.info(f"📝 Args: {context.args}")
    
    user = await get_user_by_id(user_id)
    
    # Validate args
    if not context.args:
        await update.message.reply_text(
            "❌ **Thiếu Spreadsheet ID!**\n\n"
            "Cách dùng:\n"
            "`/setsheet YOUR_SPREADSHEET_ID`\n\n"
            "📖 Xem hướng dẫn: /connectsheets",
            parse_mode="Markdown"
        )
        return
    
    spreadsheet_id = context.args[0].strip()
    
    # ✅ CHECK: If user is using TEMPLATE ID (they need to COPY first!)
    template_id = os.getenv("TEMPLATE_SPREADSHEET_ID", "1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI")
    if spreadsheet_id == template_id:
        template_url = f"https://docs.google.com/spreadsheets/d/{template_id}/copy"
        await update.message.reply_text(
            "⚠️ **Bạn đang dùng Template ID!**\n\n"
            "⚠️ **Lỗi:** Bạn KHÔNG THỂ dùng trực tiếp template này.\n\n"
            "**Bạn cần:**\n"
            "1️⃣ **Copy template về Drive của bạn**\n"
            f"   👉 [Click để copy]({template_url})\n\n"
            "2️⃣ **Lấy ID MỚI** (của bản copy)\n"
            "   URL: `docs.google.com/spreadsheets/d/[ID_MỚI]/edit`\n\n"
            "3️⃣ **Gửi ID MỚI cho bot:**\n"
            "   `/setsheet [ID_MỚI]`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "💡 **Hoặc dùng Quick Record (không cần service account):**\n"
            "1. Copy template\n"
            "2. Deploy Web App (Extensions → Apps Script)\n"
            "3. `/setwebapp [URL]`\n"
            "4. Gõ: `chi 50k test`",
            parse_mode="Markdown"
        )
        return
    
    # Validate ID format (44 chars, alphanumeric + - _ )
    if not re.match(r'^[a-zA-Z0-9_-]{30,60}$', spreadsheet_id):
        # Get example ID from environment
        example_id = os.getenv("TEMPLATE_SPREADSHEET_ID", "1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI")
        await update.message.reply_text(
            "❌ **ID không hợp lệ!**\n\n"
            "Spreadsheet ID phải:\n"
            "• Dài 30-60 ký tự\n"
            "• Chỉ chứa chữ, số, dấu gạch\n\n"
            f"Ví dụ: `{example_id}`"
        )
        return
    
    # Test connection
    await update.message.reply_text("🔄 Đang kiểm tra kết nối...")
    
    try:
        # ✅ FIX: Try to test connection, but allow fallback if service account not configured
        sheets = None
        can_test_connection = False
        
        # Check if service account file exists
        creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'google_service_account.json')
        if os.path.exists(creds_path):
            try:
                sheets = SheetsReader(spreadsheet_id)
                can_connect = await sheets.test_connection()
                can_test_connection = True
                
                if not can_connect:
                    # Get service account email
                    import json
                    sa_email = "eliroxbot-calendar@eliroxbot-calendar.iam.gserviceaccount.com"
                    try:
                        with open(creds_path, 'r') as f:
                            sa_data = json.load(f)
                            sa_email = sa_data.get('client_email', sa_email)
                    except:
                        pass
                    
                    await update.message.reply_text(
                        f"❌ **Không thể kết nối!**\n\n"
                        f"**Nguyên nhân phổ biến:**\n"
                        f"❌ Bạn CHƯA SHARE spreadsheet với bot\n\n"
                        f"**Cách sửa:**\n"
                        f"1️⃣ Mở spreadsheet: `docs.google.com/spreadsheets/d/{spreadsheet_id}/edit`\n"
                        f"2️⃣ Click **Share** (góc trên bên phải)\n"
                        f"3️⃣ Paste email này:\n"
                        f"`{sa_email}`\n"
                        f"4️⃣ Quyền: **Viewer** (chỉ đọc)\n"
                        f"5️⃣ **Bỏ tick** \"Notify people\"\n"
                        f"6️⃣ Click Share\n"
                        f"7️⃣ Thử lại: `/setsheet {spreadsheet_id}`\n\n"
                        f"📖 Hoặc dùng Quick Record: /taoweb",
                        parse_mode="Markdown"
                    )
                    
                    Analytics.track_event(user_id, 'sheets_connection_failed', {
                        'spreadsheet_id': spreadsheet_id[:10] + '...',
                        'error': 'permission_denied'
                    })
                    return
            except Exception as e:
                logger.warning(f"⚠️ Could not test connection with SheetsReader: {e}")
                can_test_connection = False
        
        # If service account not configured, save ID without testing (for Quick Record)
        if not can_test_connection:
            logger.info(f"⚠️ Service account not found, saving spreadsheet ID without testing")
            await update.message.reply_text(
                "⚠️ **Không thể kiểm tra kết nối** (chưa config service account)\n\n"
                "Đang lưu ID để dùng Quick Record...\n\n"
                "💡 **Lưu ý:**\n"
                "• Quick Record (chi 50k) sẽ hoạt động ✅\n"
                "• AI Analysis bị tắt (cần service account) ❌"
            )
        
        # Connection successful! Save to database
        await run_sync(_save_spreadsheet_sync, user_id, spreadsheet_id)
        
        # Get balance preview (only if connection test succeeded)
        balance = None
        jars = None
        
        if can_test_connection and sheets:
            try:
                balance = await sheets.get_total_balance()
                jars = await sheets.get_balance_summary()
            except Exception as e:
                logger.warning(f"⚠️ Could not get balance preview: {e}")
        
        balance_text = ""
        if balance is not None:
            balance_text = f"\n💰 **Tổng tài sản:** {balance:,.0f} VNĐ\n"
            if jars:
                balance_text += "\n**Chi tiết 6 Hũ:**\n"
                for jar_name, amount in jars.items():
                    balance_text += f"• {jar_name}: {amount:,.0f} VNĐ\n"
        
        success_message = f"✅ **KẾT NỐI THÀNH CÔNG!**\n\n"
        success_message += f"📊 Spreadsheet: `{spreadsheet_id[:20]}...`\n"
        success_message += balance_text
        success_message += f"\n━━━━━━━━━━━━━━━━━━━━━\n"
        success_message += f"🚀 **Bây giờ bạn có thể:**\n"
        success_message += f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        success_message += f"💬 Ghi giao dịch nhanh:\n"
        success_message += f"   • `chi 50k cà phê`\n"
        success_message += f"   • `thu 5tr lương`\n"
        success_message += f"   • `đầu tư 1tr Bitcoin`\n\n"
        success_message += f"📊 Xem số dư: /balance\n"
        
        if can_test_connection:
            success_message += f"📈 AI analysis: /analyze\n"
        
        await update.message.reply_text(
            success_message,
            parse_mode="Markdown"
        )
        
        # Track successful connection
        Analytics.track_event(user_id, 'sheets_connected', {
            'spreadsheet_id': spreadsheet_id[:10] + '...',
            'has_balance': balance is not None,
            'total_balance': balance if balance else 0
        })
        
        logger.info(f"✅ User {user_id} connected Sheets: {spreadsheet_id[:10]}...")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ **Lỗi kết nối!**\n\n"
            f"Chi tiết: `{str(e)}`\n\n"
            f"Vui lòng thử lại hoặc liên hệ /support"
        )
        
        logger.error(f"❌ Sheets connection error for user {user_id}: {e}")
        Analytics.track_event(user_id, 'sheets_connection_error', {'error': str(e)})


async def handle_disconnect_sheets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /disconnectsheets
    Remove Sheets connection
    """
    user_id = update.effective_user.id
    
    old_id = await run_sync(_disconnect_sheets_sync, user_id)
    if old_id is None:
        await update.message.reply_text(
            "ℹ️ Bạn chưa kết nối Google Sheets nào!"
        )
        return
    
    await update.message.reply_text(
        "✅ **Đã ngắt kết nối Google Sheets**\n\n"
        "📊 Bạn vẫn có thể dùng template bình thường.\n"
        "Chỉ thiếu tính năng AI analysis tự động.\n\n"
        "🔗 Kết nối lại: /connectsheets"
    )
    
    Analytics.track_event(user_id, 'sheets_disconnected', {
        'old_id': old_id[:10] + '...'
    })
    
    logger.info(f"User {user_id} disconnected Sheets")


async def handle_skip_sheets_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle skip button in connection wizard"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    await query.edit_message_text(
        "✅ **OK, bỏ qua kết nối!**\n\n"
        "📊 Bạn vẫn có thể:\n"
        "• Dùng Google Sheets template bình thường\n"
        "• Tự quản lý tài chính\n"
        "• Chat với bot (nhưng bot không biết số liệu của bạn)\n\n"
        "🔗 Muốn kết nối sau: /connectsheets",
        parse_mode="Markdown"
    )
    
    Analytics.track_event(user_id, 'sheets_connection_skipped')
    logger.info(f"User {user_id} skipped Sheets connection")


async def handle_change_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle change sheet button - show instructions"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get template ID from environment
    template_id = os.getenv("TEMPLATE_SPREADSHEET_ID", "1Vlq3MAplg_FtpaOqqcvgz1UNMfemHiQcKFcdfE4nOtI")
    template_url = f"https://docs.google.com/spreadsheets/d/{template_id}/copy"
    
    message = """
🔄 **ĐỔI SANG GOOGLE SHEETS KHÁC**

━━━━━━━━━━━━━━━━━━━━━
**📋 HƯỚNG DẪN:**
━━━━━━━━━━━━━━━━━━━━━

**Bước 1:** Copy Template mới (nếu chưa có)
[📄 Click để copy]

**Bước 2:** Share quyền View
👉 Trong Sheets, bấm "Share"
👉 Thêm: `freedomwallet-bot@service-account.iam.gserviceaccount.com`
👉 Quyền: **Viewer**

**Bước 3:** Lấy Spreadsheet ID
URL: `docs.google.com/spreadsheets/d/[ID]/edit`
👉 Copy phần [ID]

**Bước 4:** Gửi ID cho bot
Gõ: `/setsheet [PASTE_ID_MỚI]`

━━━━━━━━━━━━━━━━━━━━━
ℹ️ **Lưu ý:** Khi đổi sheet mới, sheet cũ sẽ bị ngắt kết nối.
"""
    
    keyboard = [
        [InlineKeyboardButton("📄 Copy Template", url=template_url)],
        [InlineKeyboardButton("« Quay lại", callback_data="connect_sheets_wizard")],
        [InlineKeyboardButton("🏠 Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode="Markdown", reply_markup=reply_markup)
    
    Analytics.track_event(user_id, 'change_sheet_requested')
    logger.info(f"User {user_id} requested to change sheet")


async def handle_disconnect_sheet_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle disconnect sheet button - show confirmation"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = await get_user_by_id(user_id)
    
    if not user or not user.spreadsheet_id:
        await query.edit_message_text(
            "ℹ️ Bạn chưa kết nối Google Sheets nào!",
            parse_mode="Markdown"
        )
        return
    
    message = f"""
🔌 **NGẮT KẾT NỐI GOOGLE SHEETS**

📊 Sheet hiện tại: `{user.spreadsheet_id[:20]}...`

━━━━━━━━━━━━━━━━━━━━━
⚠️ **Sau khi ngắt:**
━━━━━━━━━━━━━━━━━━━━━

❌ Bot sẽ không đọc được data
❌ AI analysis không hoạt động
❌ Dashboard bị khóa

✅ Bạn vẫn dùng được Sheets thủ công
✅ Có thể kết nối lại bất cứ lúc nào

━━━━━━━━━━━━━━━━━━━━━
Bạn có chắc muốn ngắt kết nối?
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Ngắt kết nối", callback_data="disconnect_sheet_confirmed")],
        [InlineKeyboardButton("« Không, giữ lại", callback_data="connect_sheets_wizard")],
        [InlineKeyboardButton("🏠 Menu", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode="Markdown", reply_markup=reply_markup)


async def handle_disconnect_sheet_confirmed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Actually disconnect the sheet"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    old_id = await run_sync(_disconnect_sheets_sync, user_id)
    if old_id:
        await query.edit_message_text(
            "✅ **Đã ngắt kết nối Google Sheets**\n\n"
            "📊 Bạn vẫn có thể dùng template bình thường.\n"
            "Chỉ thiếu tính năng AI analysis tự động.\n\n"
            "🔗 Kết nối lại: /connectsheets",
            parse_mode="Markdown"
        )
        Analytics.track_event(user_id, 'sheets_disconnected', {'old_id': old_id[:10] + '...'})
        logger.info(f"User {user_id} disconnected Sheets")
    else:
        await query.edit_message_text(
            "ℹ️ Không có sheet nào đang kết nối.",
            parse_mode="Markdown"
        )



# Register commands
async def cmd_get_service_account_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show service account email for manual sharing"""
    import json
    creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'google_service_account.json')
    
    if not os.path.exists(creds_path):
        await update.message.reply_text(
            "❌ **Service account chưa được cấu hình!**\n\n"
            "Bot chưa có file `google_service_account.json`.\n\n"
            "**Bạn có thể dùng Quick Record thay thế:**\n"
            "1. Copy template về Drive\n"
            "2. Deploy Web App: /taoweb\n"
            "3. Gõ: `chi 50k test`\n\n"
            "Không cần share với ai!",
            parse_mode="Markdown"
        )
        return
    
    try:
        with open(creds_path, 'r') as f:
            sa_data = json.load(f)
            sa_email = sa_data.get('client_email', 'Unknown')
            project_id = sa_data.get('project_id', 'Unknown')
        
        await update.message.reply_text(
            f"📧 **Service Account Email:**\n\n"
            f"`{sa_email}`\n\n"
            f"🔑 Project: `{project_id}`\n\n"
            f"**Cách share spreadsheet:**\n"
            f"1️⃣ Mở spreadsheet của bạn\n"
            f"2️⃣ Click **Share** (góc trên phải)\n"
            f"3️⃣ Copy email trên → Paste vào\n"
            f"4️⃣ Quyền: **Viewer**\n"
            f"5️⃣ Bỏ tick \"Notify people\"\n"
            f"6️⃣ Click **Share**\n\n"
            f"Sau đó: `/setsheet [ID_SPREADSHEET_CỦA_BẠN]`",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error reading service account: {e}")
        await update.message.reply_text(f"❌ Lỗi đọc service account: {str(e)}")


def register_sheets_setup_handlers(application):
    """Register all Sheets setup handlers"""
    from telegram.ext import CommandHandler, CallbackQueryHandler
    
    application.add_handler(CommandHandler('connectsheets', handle_connect_sheets_wizard))
    application.add_handler(CommandHandler('setsheet', handle_set_sheet_command))
    application.add_handler(CommandHandler('getsaemail', cmd_get_service_account_email))
    application.add_handler(CommandHandler('disconnectsheets', handle_disconnect_sheets))
    
    application.add_handler(CallbackQueryHandler(
        handle_connect_sheets_wizard, 
        pattern='^connect_sheets_wizard$'
    ))
    application.add_handler(CallbackQueryHandler(
        handle_skip_sheets_connection,
        pattern='^skip_sheets_connection$'
    ))
    application.add_handler(CallbackQueryHandler(
        handle_change_sheet,
        pattern='^change_sheet$'
    ))
    application.add_handler(CallbackQueryHandler(
        handle_disconnect_sheet_confirm,
        pattern='^disconnect_sheet$'
    ))
    application.add_handler(CallbackQueryHandler(
        handle_disconnect_sheet_confirmed,
        pattern='^disconnect_sheet_confirmed$'
    ))
    
    logger.info("✅ Sheets setup handlers registered")
