"""
Message Handler - Process user messages with FAQ or AI
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
import json
import html
from pathlib import Path
from datetime import datetime
from app.middleware.usage_tracker import check_message_limit
from app.utils.database import User
from config.settings import settings


# Load FAQ data
FAQ_FILE = Path(__file__).parent.parent.parent / "knowledge" / "faq.json"
with open(FAQ_FILE, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)


def search_faq(query: str) -> dict:
    """
    Search FAQ based on keywords matching
    Returns: {"found": bool, "answer": str, "category": str}
    """
    query_lower = query.lower()
    
    # Check default responses first
    default_responses = FAQ_DATA.get("default_responses", {})
    
    # Greeting
    if any(word in query_lower for word in default_responses.get("greeting", [])):
        return {
            "found": True,
            "answer": default_responses.get("greeting_response"),
            "category": "greeting"
        }
    
    # Thanks
    if any(word in query_lower for word in default_responses.get("thanks", [])):
        return {
            "found": True,
            "answer": default_responses.get("thanks_response"),
            "category": "thanks"
        }
    
    # Goodbye
    if any(word in query_lower for word in default_responses.get("goodbye", [])):
        return {
            "found": True,
            "answer": default_responses.get("goodbye_response"),
            "category": "goodbye"
        }
    
    # Search in FAQ categories
    for category in FAQ_DATA.get("categories", []):
        for question in category.get("questions", []):
            keywords = question.get("keywords", [])
            
            # Check if any keyword matches
            if any(keyword.lower() in query_lower for keyword in keywords):
                return {
                    "found": True,
                    "answer": question.get("answer"),
                    "category": category.get("name"),
                    "icon": category.get("icon")
                }
    
    # Not found
    return {
        "found": False,
        "answer": None,
        "category": None
    }


async def handle_sheet_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Handle Google Sheet URL input"""
    import re
    
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"📋 Processing Sheet URL from user {user.id}")
    
    # Parse Sheet URL
    sheet_match = re.search(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]{30,60})', message_text)
    
    if not sheet_match:
        await update.message.reply_text(
            "❌ **Link không hợp lệ!**\n\n"
            "Vui lòng gửi link Google Sheet đúng định dạng:\n"
            "`https://docs.google.com/spreadsheets/d/1Vlq3MA.../edit`\n\n"
            "💡 **Cách lấy:** Mở Sheet → Copy URL trên thanh địa chỉ",
            parse_mode="Markdown"
        )
        return
    
    sheet_id = sheet_match.group(1)
    logger.info(f"  → Extracted Sheet ID: {sheet_id}")
    
    # Save to context
    context.user_data['temp_sheet_id'] = sheet_id
    context.user_data['waiting_for_sheet_url'] = False
    context.user_data['waiting_for_webapp_url'] = True
    
    # Ask for Web App URL
    message = """
✅ **ĐÃ NHẬN LINK GOOGLE SHEET!**

📋 Sheet ID: `{sheet_id_preview}...`

━━━━━━━━━━━━━━━━━━━━━

**BƯỚC 2/2: Gửi Link Web App** 🔗

Bây giờ vui lòng gửi link Web App của bạn:

**Ví dụ:**
`https://script.google.com/macros/s/AKfycby.../exec`

━━━━━━━━━━━━━━━━━━━━━

💡 **Cách lấy:**
1. Vào Apps Script của bạn
2. Bấm **Deploy** → **Manage deployments**
3. Copy **Web App URL**
4. Gửi cho tôi

⏳ **Đang chờ link Web App...**
""".format(sheet_id_preview=sheet_id[:20])
    
    await update.message.reply_text(message, parse_mode="Markdown")


async def handle_webapp_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 2: Handle Web App URL input and finalize connection"""
    import re
    from app.utils.database import SessionLocal, User
    from datetime import datetime
    
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"🔗 Processing Web App URL from user {user.id}")
    
    # Parse Web App URL
    webapp_match = re.search(r'(https://script\.google\.com/macros/s/[^\s]+)', message_text)
    
    if not webapp_match:
        await update.message.reply_text(
            "❌ **Link không hợp lệ!**\n\n"
            "Vui lòng gửi link Web App đúng định dạng:\n"
            "`https://script.google.com/macros/s/AKfycby.../exec`\n\n"
            "💡 **Cách lấy:** Apps Script → Deploy → Manage deployments → Copy URL",
            parse_mode="Markdown"
        )
        return
    
    webapp_url = webapp_match.group(1)
    sheet_id = context.user_data.get('temp_sheet_id')
    
    if not sheet_id:
        await update.message.reply_text(
            "❌ **Lỗi:** Không tìm thấy Sheet ID!\n\n"
            "Vui lòng bắt đầu lại từ đầu.",
            parse_mode="Markdown"
        )
        context.user_data.clear()
        return
    
    logger.info(f"  → Sheet ID: {sheet_id}, Web App URL: {webapp_url}")
    
    # Save to database
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            await update.message.reply_text(
                "❌ **Không tìm thấy tài khoản!**\n\n"
                "Vui lòng đăng ký trước: /register"
            )
            return
        
        # Update database
        db_user.spreadsheet_id = sheet_id
        db_user.web_app_url = webapp_url
        db_user.sheets_connected_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ Connected user {user.id}: sheet_id={sheet_id}, webapp_url={webapp_url}")
        
        # Clear state
        context.user_data['waiting_for_webapp_url'] = False
        context.user_data.pop('temp_sheet_id', None)
        
        # Success message
        success_message = """
�🎊🎊 **CHÚC MỪNG BẠN!** 🎊🎊🎊

**KẾT NỐI FREEDOM WALLET THÀNH CÔNG!**

━━━━━━━━━━━━━━━━━━━━━

✅ **Đã kết nối:**
📋 Google Sheet: `{sheet_preview}...` ✓
🔗 Web App: Đã kích hoạt ✓
⏰ Thời gian: Vừa xong

━━━━━━━━━━━━━━━━━━━━━

🎁 **QUYỀN LỢI CỦA BẠN:**

✨ **1. Ghi chi tiêu siêu nhanh**
   Chỉ gửi: `Cà phê 35k` → Tự động lưu!

💰 **2. Báo cáo tức thì**
   `/balance` → Xem số dư
   `/spending` → Phân tích chi tiêu

🤖 **3. AI tư vấn thông minh**
   Hỏi bất cứ điều gì về tài chính!

🔔 **4. Nhắc nhở tự động**
   Bot nhắc hàng ngày, kiếm streak!

━━━━━━━━━━━━━━━━━━━━━

🚀 **BẮT ĐẦU NGAY:**
Dùng Menu bên dưới để khám phá! ⬇️
""".format(sheet_preview=sheet_id[:20])
        
        keyboard = [
            [InlineKeyboardButton("📌 Ghi nhanh thu chi", callback_data="quick_record_menu")],
            [InlineKeyboardButton("📊 Báo cáo nhanh", callback_data="quick_report_menu")],
            [InlineKeyboardButton("📁 Hệ thống của tôi", callback_data="my_system_menu")],
            [InlineKeyboardButton("📖 Hướng dẫn sử dụng", callback_data="show_guide_choice"), 
             InlineKeyboardButton("⚙️ Cài đặt", callback_data="settings_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            success_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to save connection: {e}")
        await update.message.reply_text(
            f"❌ **Có lỗi xảy ra!**\n\n"
            f"Lỗi: {str(e)}\n\n"
            "Vui lòng thử lại hoặc liên hệ /support"
        )
    finally:
        db.close()


async def handle_webapp_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parse and save SHEET ID + WEBAPP URL from user message"""
    from app.utils.database import get_user_by_id, SessionLocal
    import re
    
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"📋 Parsing SHEET/WEBAPP connection from user {user.id}")
    
    # Method 1: Parse format SHEET: [ID] and WEBAPP: [URL]
    sheet_match = re.search(r'SHEET:\s*([a-zA-Z0-9_-]{30,60})', message_text, re.IGNORECASE)
    sheet_id = sheet_match.group(1).strip() if sheet_match else None
    
    webapp_match = re.search(r'WEBAPP:\s*(https://script\.google\.com/macros/s/[^\s]+)', message_text, re.IGNORECASE)
    webapp_url = webapp_match.group(1).strip() if webapp_match else None
    
    # Method 2: Parse direct Google Sheets URL (if SHEET: not found)
    if not sheet_id:
        sheets_url_match = re.search(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]{30,60})', message_text)
        if sheets_url_match:
            sheet_id = sheets_url_match.group(1).strip()
            logger.info(f"  → Extracted Sheet ID from URL: {sheet_id}")
    
    # Method 3: Parse direct Web App URL (if WEBAPP: not found)
    if not webapp_url:
        webapp_url_match = re.search(r'(https://script\.google\.com/macros/s/[^\s]+)', message_text)
        if webapp_url_match:
            webapp_url = webapp_url_match.group(1).strip()
            logger.info(f"  → Extracted Web App URL: {webapp_url}")
    
    logger.info(f"  → Final parsed: sheet_id={sheet_id}, webapp_url={webapp_url}")
    
    # Validation
    errors = []
    if not sheet_id and not webapp_url:
        await update.message.reply_text(
            "❌ **Không tìm thấy thông tin!**\n\n"
            "Vui lòng gửi 1 trong 2 cách:\n\n"
            "**Cách 1: Copy paste trực tiếp 2 links**\n"
            "https://docs.google.com/spreadsheets/d/1Vlq3MA...\n"
            "https://script.google.com/macros/s/AKfyc...\n\n"
            "**Cách 2: Theo format**\n"
            "```\n"
            "SHEET: [Sheet ID]\n"
            "WEBAPP: [Web App URL]\n"
            "```\n\n"
            "💡 Chỉ gửi 1 link cũng được nếu muốn cập nhật riêng!",
            parse_mode="Markdown"
        )
        return
    
    # Validate Sheet ID format
    if sheet_id and not re.match(r'^[a-zA-Z0-9_-]{30,60}$', sheet_id):
        errors.append("📋 **Sheet ID không hợp lệ** (phải 30-60 ký tự, chỉ chữ số và dấu gạch)")
    
    # Validate Web App URL format
    if webapp_url and not webapp_url.startswith("https://script.google.com/macros/s/"):
        errors.append("🔗 **Web App URL không hợp lệ** (phải bắt đầu bằng https://script.google.com/macros/s/)")
    
    if errors:
        await update.message.reply_text(
            "❌ **Có lỗi trong thông tin:**\n\n" + "\n".join(errors) + "\n\n"
            "Vui lòng kiểm tra lại và gửi đúng format!",
            parse_mode="Markdown"
        )
        return
    
    # Update database
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        if not db_user:
            await update.message.reply_text(
                "❌ **Không tìm thấy tài khoản!**\n\n"
                "Vui lòng đăng ký trước: /register"
            )
            return
        
        # Update fields
        updated_fields = []
        if sheet_id:
            db_user.spreadsheet_id = sheet_id
            updated_fields.append(f"📋 Sheet ID: `{sheet_id[:20]}...`")
        
        if webapp_url:
            db_user.web_app_url = webapp_url
            db_user.sheets_connected_at = datetime.utcnow()
            updated_fields.append(f"🔗 Web App: Đã kết nối ✅")
        
        db.commit()
        logger.info(f"✅ Updated user {user.id}: sheet_id={sheet_id}, webapp_url={webapp_url}")
        
        # Success message
        success_message = (
            "✅ **KẾT NỐI THÀNH CÔNG!**\n\n"
            "**Đã cập nhật:**\n" + "\n".join(updated_fields) + "\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎉 **Chúc mừng! Bạn đã sở hữu Freedom Wallet hoàn chỉnh!**\n\n"
            "**🤖 Tính năng bot hỗ trợ:**\n\n"
            "1️⃣ **Ghi chi tiêu nhanh**\n"
            "   Gửi: `Cà phê 35k`\n"
            "   → Bot tự động ghi vào Sheet\n\n"
            "2️⃣ **Xem báo cáo**\n"
            "   `/balance` - Xem tổng thu/chi\n"
            "   `/spending` - Chi tiêu theo danh mục\n\n"
            "3️⃣ **Nhắc nhở hàng ngày**\n"
            "   Bot sẽ nhắc bạn ghi chi tiêu\n"
            "   Duy trì streak để nhận huy chương!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 **Bắt đầu ngay:** Thử gửi `Ăn sáng 30k` để ghi giao dịch đầu tiên!\n\n"
            "📖 Hoặc dùng /help để xem tất cả lệnh!"
        )
        
        keyboard = [
            [InlineKeyboardButton("💬 Thử ghi chi tiêu", callback_data="try_quick_record")],
            [InlineKeyboardButton("📖 Xem hướng dẫn đầy đủ", callback_data="show_full_guide")],
            [InlineKeyboardButton("🏠 Menu chính", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            success_message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to update webapp connection: {e}")
        await update.message.reply_text(
            f"❌ **Có lỗi xảy ra!**\n\n"
            f"Lỗi: {str(e)}\n\n"
            "Vui lòng thử lại hoặc liên hệ /support"
        )
    finally:
        db.close()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages from users"""
    
    user = update.effective_user
    message_text = update.message.text
    logger.info(f"User {user.id} ({user.username}): {message_text}")
    
    # PRIORITY 1: Check if waiting for Sheet URL (Step 1 of connection)
    if context.user_data.get('waiting_for_sheet_url'):
        await handle_sheet_url_input(update, context)
        return
    
    # PRIORITY 2: Check if waiting for Web App URL (Step 2 of connection)
    if context.user_data.get('waiting_for_webapp_url'):
        await handle_webapp_url_input(update, context)
        return
    
    # PRIORITY 3: Check if user is sending SHEET + WEBAPP connection info (old format)
    if "SHEET:" in message_text or "WEBAPP:" in message_text:
        await handle_webapp_connection(update, context)
        return
    
    # CRITICAL: Skip if user is in a ConversationHandler flow
    # Check for any active conversation state in context
    conversation_state = context.user_data.get('conversation_state')
    if conversation_state is not None:
        logger.info(f"  → Skipping AI handler - user in conversation (state: {conversation_state})")
        return
    
    # Check if user is sending payment proof
    if context.user_data.get('awaiting_payment_proof'):
        await handle_payment_proof_text(update, context)
        return
    
    # Check if admin is sending rejection reason
    if context.user_data.get('rejecting_payment'):
        await handle_admin_rejection_reason(update, context)
        return
    
    # Check message limit (FREE tier = 5 msg/day)
    can_send = await check_message_limit(update, context)
    if not can_send:
        return  # Middleware already sent upgrade prompt
    
    # Phase 1: Simple FAQ keyword matching
    faq_result = search_faq(message_text)
    
    if faq_result["found"]:
        # Found answer in FAQ
        answer = faq_result["answer"]
        category = faq_result.get("category", "")
        icon = faq_result.get("icon", "💬")
        
        # Quick action buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Giải quyết", callback_data="feedback_solved"),
                InlineKeyboardButton("❌ Vẫn lỗi", callback_data="feedback_unsolved")
            ],
            [
                InlineKeyboardButton("💬 Hỏi thêm", callback_data="ask_more"),
                InlineKeyboardButton("🆘 Liên hệ support", callback_data="contact_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            answer,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    else:
        # Not found - fallback response
        fallback_text = """
🤔 **Xin lỗi, mình chưa hiểu câu hỏi của bạn.**

💡 **Gợi ý:**
• Hỏi bằng từ khóa đơn giản: "thêm giao dịch", "6 hũ", "tính ROI"
• Dùng /help để xem danh sách câu hỏi phổ biến
• Hoặc /support để liên hệ support team

🔍 **Ví dụ câu hỏi:**
• Làm sao thêm giao dịch?
• 6 hũ tiền là gì?
• Cách chuyển tiền giữa hũ?

💬 Thử hỏi lại nhé!
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📚 Xem FAQ", callback_data="help_faq"),
                InlineKeyboardButton("🆘 Liên hệ support", callback_data="contact_support")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            fallback_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


# Phase 2: Upgrade to AI-powered conversation
"""
from app.ai.gpt_client import GPTClient

gpt_client = GPTClient()

async def handle_message_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Enhanced version with GPT-4
    
    # Try FAQ first (faster)
    faq_result = search_faq(message_text)
    if faq_result["found"]:
        # Send FAQ answer
        ...
        return
    
    # If not in FAQ, use GPT-4
    try:
        # Get conversation context
        user_context = await get_user_context(user.id)
        
        # Call GPT-4
        ai_response = await gpt_client.chat(
            message=message_text,
            context=user_context,
            user_id=user.id
        )
        
        # Save to context memory
        await save_message_to_context(user.id, message_text, ai_response)
        
        # Send AI response
        await update.message.reply_text(ai_response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"GPT-4 error: {e}")
        # Fallback to not found message
        ...
"""


async def handle_payment_proof_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment proof submitted as text"""
    user_id = update.effective_user.id
    transaction_info = update.message.text
    
    # Clear the awaiting flag
    context.user_data['awaiting_payment_proof'] = False
    amount = context.user_data.get('payment_amount', 999000)
    
    # Create verification request
    from app.services.payment_service import PaymentVerificationService
    
    try:
        verification_id = await PaymentVerificationService.create_verification_request(
            user_id=user_id,
            amount=amount,
            transaction_info=transaction_info,
            submitted_by=user_id
        )
        
        message = f"""
✅ **ĐÃ NHẬN THÔNG TIN**

Mã xác nhận: `{verification_id}`

━━━━━━━━━━━━━━━━━━━━━
📋 **THÔNG TIN NHẬN ĐƯỢC:**
━━━━━━━━━━━━━━━━━━━━━

{transaction_info}

━━━━━━━━━━━━━━━━━━━━━
⏱️ **TIẾP THEO:**
━━━━━━━━━━━━━━━━━━━━━

• Hệ thống đang kiểm tra thanh toán
• Nếu đúng nội dung CK → Tự động kích hoạt (5-10 phút)
• Nếu sai nội dung → Admin xác nhận thủ công (15-30 phút)

━━━━━━━━━━━━━━━━━━━━━
🔔 **THÔNG BÁO:**
━━━━━━━━━━━━━━━━━━━━━

✅ Bạn sẽ nhận thông báo khi Premium được kích hoạt
💬 Mọi thắc mắc, liên hệ Admin

Cảm ơn bạn đã tin tưởng Freedom Wallet! 💎
"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")],
            [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Payment verification created: {verification_id} for user {user_id}")
        
        # Notify admin about new payment verification
        if settings.ADMIN_USER_ID:
            try:
                # Use HTML for safer parsing
                import html
                safe_username = html.escape(update.effective_user.username or 'N/A')
                safe_fullname = html.escape(update.effective_user.full_name or 'N/A')
                safe_transaction = html.escape(transaction_info)
                
                admin_message = f"""
🔔 <b>YÊU CẦU XÁC NHẬN THANH TOÁN MỚI</b>

Mã: <code>{verification_id}</code>
User ID: <code>{user_id}</code>
Username: @{safe_username}
Tên: {safe_fullname}
Số tiền: {amount:,.0f} VND

📋 <b>Thông tin:</b>
{safe_transaction}

⏱️ Thời gian: {update.message.date.strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━
💡 <b>Hành động:</b>

• Xem pending: /payment_pending
• Duyệt: /payment_approve {verification_id}
• Từ chối: /payment_reject {verification_id} [lý do]
"""
                
                # Add inline buttons for quick action
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Duyệt", callback_data=f"admin_approve_{verification_id}"),
                        InlineKeyboardButton("❌ Từ chối", callback_data=f"admin_reject_{verification_id}")
                    ],
                    [InlineKeyboardButton("📋 Xem tất cả pending", callback_data="admin_list_pending")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=settings.ADMIN_USER_ID,
                    text=admin_message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
                logger.info(f"Admin notification sent for {verification_id}")
            except Exception as notify_error:
                logger.error(f"Failed to notify admin: {notify_error}")
        
    except Exception as e:
        logger.error(f"Error creating payment verification: {e}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ Admin.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")
            ]])
        )


async def handle_payment_proof_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment proof submitted as photo"""
    user_id = update.effective_user.id
    
    # Check if user is submitting payment proof
    if not context.user_data.get('awaiting_payment_proof'):
        # Not expecting payment proof, ignore
        return
    
    # Clear the awaiting flag
    context.user_data['awaiting_payment_proof'] = False
    amount = context.user_data.get('payment_amount', 999000)
    
    # Get photo file
    photo = update.message.photo[-1]  # Get highest resolution
    file = await photo.get_file()
    
    # Get caption if provided
    caption = update.message.caption or "Payment proof image"
    transaction_info = f"Photo: {file.file_id}\nCaption: {caption}"
    
    # Create verification request
    from app.services.payment_service import PaymentVerificationService
    
    try:
        verification_id = await PaymentVerificationService.create_verification_request(
            user_id=user_id,
            amount=amount,
            transaction_info=transaction_info,
            submitted_by=user_id
        )
        
        message = f"""
✅ **ĐÃ NHẬN ẢNH XÁC NHẬN**

Mã xác nhận: `{verification_id}`

━━━━━━━━━━━━━━━━━━━━━
📸 **ẢNH NHẬN ĐƯỢC:**
━━━━━━━━━━━━━━━━━━━━━

Đã lưu ảnh chuyển khoản của bạn

━━━━━━━━━━━━━━━━━━━━━
⏱️ **TIẾP THEO:**
━━━━━━━━━━━━━━━━━━━━━

• Admin đang xác nhận thanh toán
• Thời gian xử lý: 15-30 phút (giờ hành chính)
• Ngoài giờ: Trong 2 giờ

━━━━━━━━━━━━━━━━━━━━━
🔔 **THÔNG BÁO:**
━━━━━━━━━━━━━━━━━━━━━

✅ Bạn sẽ nhận thông báo khi Premium được kích hoạt
💬 Mọi thắc mắc, liên hệ Admin

Cảm ơn bạn đã tin tưởng Freedom Wallet! 💎
"""
        
        keyboard = [
            [InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")],
            [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
        logger.info(f"Payment verification (photo) created: {verification_id} for user {user_id}")
        
        # Notify admin about new payment verification (with photo)
        if settings.ADMIN_USER_ID:
            try:
                # Use HTML for safer parsing
                import html
                safe_username = html.escape(update.effective_user.username or 'N/A')
                safe_fullname = html.escape(update.effective_user.full_name or 'N/A')
                safe_caption = html.escape(caption)
                
                admin_message = f"""
🔔 <b>YÊU CẦU XÁC NHẬN THANH TOÁN MỚI</b> 📸

Mã: <code>{verification_id}</code>
User ID: <code>{user_id}</code>
Username: @{safe_username}
Tên: {safe_fullname}
Số tiền: {amount:,.0f} VND

📸 <b>Ảnh xác nhận:</b>
Đã gửi ảnh chuyển khoản
Caption: {safe_caption}

⏱️ Thời gian: {update.message.date.strftime('%d/%m/%Y %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━
💡 <b>Hành động:</b>

• Xem pending: /payment_pending
• Duyệt: /payment_approve {verification_id}
• Từ chối: /payment_reject {verification_id} [lý do]
"""
                
                # Add inline buttons for quick action
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Duyệt", callback_data=f"admin_approve_{verification_id}"),
                        InlineKeyboardButton("❌ Từ chối", callback_data=f"admin_reject_{verification_id}")
                    ],
                    [InlineKeyboardButton("📋 Xem tất cả pending", callback_data="admin_list_pending")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Send admin message with photo
                await context.bot.send_photo(
                    chat_id=settings.ADMIN_USER_ID,
                    photo=file.file_id,
                    caption=admin_message,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
                logger.info(f"Admin notification (with photo) sent for {verification_id}")
            except Exception as notify_error:
                logger.error(f"Failed to notify admin: {notify_error}")
        
    except Exception as e:
        logger.error(f"Error creating payment verification from photo: {e}")
        await update.message.reply_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ Admin.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💬 Liên hệ Admin", callback_data="contact_support")
            ]])
        )


async def handle_admin_rejection_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle rejection reason from admin"""
    from app.services.payment_service import PaymentVerificationService
    from app.utils.database import get_db, PaymentVerification
    from app.handlers.admin.admin_payment import is_admin
    
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(user_id):
        return
    
    verification_id = context.user_data.get('rejecting_payment')
    reason = update.message.text
    
    if not verification_id:
        return
    
    # Clear the flag
    context.user_data['rejecting_payment'] = None
    
    try:
        # Reject payment
        success = await PaymentVerificationService.reject_payment(
            verification_id=verification_id,
            rejected_by=user_id,
            reason=reason
        )
        
        if success:
            # Get verification details
            db = next(get_db())
            ver_id = int(verification_id.replace("VER", ""))
            verification = db.query(PaymentVerification).filter(
                PaymentVerification.id == ver_id
            ).first()
            
            if verification:
                # Log to Google Sheets
                from app.handlers.admin.admin_callbacks import log_payment_to_sheets
                from app.utils.database import User
                user = db.query(User).filter(User.id == verification.user_id).first()
                
                if user:
                    await log_payment_to_sheets(
                        verification_id=verification_id,
                        user_id=user.id,
                        username=user.username,
                        full_name=user.full_name,
                        amount=verification.amount,
                        status="REJECTED",
                        approved_by=user_id,
                        approved_at=verification.approved_at or datetime.now(),
                        notes=reason  # Pass rejection reason
                    )
                
                # Notify user
                safe_reason = html.escape(reason)
                try:
                    await context.bot.send_message(
                        chat_id=verification.user_id,
                        text=f"""
❌ <b>THANH TOÁN BỊ TỪ CHỐI</b>

Mã xác nhận: <code>{verification_id}</code>

━━━━━━━━━━━━━━━━━━━━━
📋 <b>LÝ DO:</b>
━━━━━━━━━━━━━━━━━━━━━

{safe_reason}

━━━━━━━━━━━━━━━━━━━━━
💡 <b>HƯỚNG DẪN:</b>
━━━━━━━━━━━━━━━━━━━━━

• Kiểm tra lại thông tin thanh toán
• Đảm bảo chuyển khoản đúng:
  - Số tiền: 999,000 VND
  - Ná»™i dung: FW{verification.user_id} PREMIUM
• Gửi lại ảnh/thông tin xác nhận

💬 Cần hỗ trợ? Dùng /support để liên hệ Admin
""",
                        parse_mode="HTML"
                    )
                except Exception as notify_error:
                    logger.error(f"Failed to notify user {verification.user_id}: {notify_error}")
            
            db.close()
            
            # Confirm to admin
            safe_reason_admin = html.escape(reason)
            await update.message.reply_text(
                f"""
✅ <b>ĐÃ TỪ CHỐI</b>

Mã: <code>{verification_id}</code>
Lý do: {safe_reason_admin}

User đã nhận thông báo.
""",
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                f"❌ Lỗi khi từ chối {verification_id}",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Error in handle_admin_rejection_reason: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Có lỗi xảy ra. Vui lòng thử lại!",
            parse_mode="HTML"
        )

