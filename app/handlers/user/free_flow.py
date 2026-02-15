"""
FREE Flow - Step-by-step guided setup
No FOMO, no pressure, clear value proposition
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from app.utils.database import SessionLocal, User


async def free_check_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user has registration info"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Check if user has complete info
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        
        if db_user and db_user.email and db_user.full_name:
            # Has info, go to step 2
            logger.info(f"User {user.id} has registration info, proceeding to step 2")
            await free_step2_show_value(update, context)
        else:
            # No info yet, ask to register first
            logger.info(f"User {user.id} missing registration info")
            
            from pathlib import Path
            
            message = """
Chào bạn,

Freedom Wallet không phải một app để bạn tải về.
Đây là một hệ thống bạn tự sở hữu.

Mỗi người dùng có:
• Google Sheet riêng
• Apps Script riêng
• Web App riêng

Dữ liệu nằm trên Drive của bạn.
Không phụ thuộc vào ai.

Để bắt đầu, vui lòng nhập lệnh /register 
để điền thông tin đăng ký.
"""
            
            image_path = Path("media/images/web_apps.jpg")
            
            try:
                # Delete the original message
                await query.message.delete()
                
                # Send photo with caption
                await query.message.reply_photo(
                    photo=open(image_path, 'rb'),
                    caption=message,
                    parse_mode="Markdown"
                )
                
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                await query.edit_message_text(
                    message,
                    parse_mode="Markdown"
                )
                
    finally:
        db.close()


async def free_step2_show_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 2 - Show value before any technical setup"""
    query = update.callback_query
    await query.answer()
    
    message = """
Trước khi làm bất cứ bước kỹ thuật nào,
bạn cần biết mình sẽ nhận được điều gì.

Khi hệ thống hoàn tất, bạn sẽ thấy:

• Tổng tài sản hiện có
• Dòng tiền thu – chi theo tháng
• 6 Hũ tiền phân bổ tự động
• Cấp độ tài chính hiện tại của bạn
• Tình trạng đầu tư, nợ và tài sản

Không phải để xem cho vui.
Mà để bạn biết rõ tiền của mình đang ở đâu.

Bạn sẵn sàng tạo hệ thống của riêng mình chưa?
"""
    
    keyboard = [
        [InlineKeyboardButton("Tạo hệ thống", callback_data="free_step3_copy_template")],
        [InlineKeyboardButton("Hỏi thêm", callback_data="free_ask_question")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def free_step3_copy_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 3 - Copy Google Sheet template"""
    query = update.callback_query
    await query.answer()
    
    message = """
**Bước 1: Tạo Google Sheet của riêng bạn.**

Nhấn nút bên dưới.
Chọn "Tạo bản sao".
Đặt tên theo ý bạn.

Từ đây trở đi,
đây là hệ thống tài chính cá nhân của bạn.
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy Template", url="https://docs.google.com/spreadsheets/d/YOUR_TEMPLATE_ID/copy")],
        [InlineKeyboardButton("✅ Tôi đã copy xong", callback_data="free_step4_deploy_script")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def free_step4_deploy_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 4 - Deploy Apps Script"""
    query = update.callback_query
    await query.answer()
    
    message = """
**Bước 2: Kích hoạt Web App.**

Apps Script giúp Sheet của bạn trở thành một ứng dụng thực thụ.

Chỉ cần làm theo hướng dẫn,
khoảng 3–5 phút.

Đừng lo nếu chưa quen kỹ thuật.
Làm chậm từng bước là được.
"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Xem hướng dẫn", callback_data="show_deploy_guide")],
        [InlineKeyboardButton("✅ Tôi đã deploy xong", callback_data="free_step5_open_webapp")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def free_step5_open_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 5 - Open Web App first time"""
    query = update.callback_query
    await query.answer()
    
    message = """
Bây giờ bạn có thể mở Web App của mình.

Lần đầu mở, bạn sẽ thấy:
• Tổng tài sản
• Dòng tiền
• Biểu đồ chi tiêu
• Cấp độ tài chính

Đây là lần đầu bạn nhìn toàn cảnh tiền của mình ở một nơi.
"""
    
    keyboard = [
        [InlineKeyboardButton("🌐 Mở Web App", callback_data="get_webapp_url")],
        [InlineKeyboardButton("✅ Tôi đã xem", callback_data="free_step6_first_action")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Delete previous message (photo) and send new text message
    await query.message.delete()
    await query.message.chat.send_message(
        text=message,
        reply_markup=reply_markup
    )


async def free_step6_first_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 6 - First important action"""
    query = update.callback_query
    await query.answer()
    
    message = """
Việc quan trọng nhất hôm nay:

Nhập:
• Số dư hiện tại
• 1–2 giao dịch gần đây

Không cần nhiều.
Chỉ cần bắt đầu.

Tự do tài chính không đến từ kế hoạch lớn.
Nó đến từ việc bạn biết tiền mình đang ở đâu.
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ Tôi đã nhập", callback_data="free_step7_reinforce")],
        [InlineKeyboardButton("❓ Cần hỗ trợ", callback_data="ask_support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def free_step7_reinforce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 7 - Reinforce awareness behavior"""
    query = update.callback_query
    await query.answer()
    
    message = """
Từ hôm nay,
bạn không còn mơ hồ về tiền nữa.

Mỗi khoản thu – chi đều có nơi ghi lại.
Mỗi quyết định đều có dữ liệu phía sau.

Tuần đầu, chỉ cần:
**Ghi lại mọi khoản phát sinh.**

Đừng cố tối ưu.
Chỉ cần trung thực với con số.
"""
    
    keyboard = [
        [InlineKeyboardButton("Tiếp tục", callback_data="free_step8_optional_sharing")],
        [InlineKeyboardButton("Nhắc tôi sau", callback_data="schedule_reminder")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def free_step8_optional_sharing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """STEP 8 - Optional sharing (natural, no pressure)"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    from app.utils.database import get_user_by_id
    db_user = await get_user_by_id(user.id)
    
    ref_code = db_user.referral_code if db_user else "unknown"
    ref_link = f"https://t.me/FreedomWalletVNBot?start={ref_code}"
    
    message = f"""
Nếu bạn thấy hệ thống này có ích,
bạn có thể chia sẻ với 2 người bạn
cũng đang muốn quản lý tiền rõ ràng hơn.

Khi bạn giới thiệu 2 người thật sự dùng,
bên mình sẽ hỗ trợ bạn cấu hình thêm Telegram,
để bạn ghi thu chi ngay trong chat này.

Không bắt buộc.
Chỉ khi bạn thấy phù hợp.

🔗 Link của bạn: `{ref_link}`
"""
    
    keyboard = [
        [InlineKeyboardButton("Chia sẻ với bạn bè", callback_data="show_share_guide")],
        [InlineKeyboardButton("Tìm hiểu Telegram", callback_data="explain_telegram_unlock")],
        [InlineKeyboardButton("Để sau", callback_data="skip_sharing")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def learn_more(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show more details about Freedom Wallet"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Check if user is registered
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.id == user.id).first()
        has_registration = db_user and db_user.email and db_user.full_name
    finally:
        db.close()
    
    message = """
**Freedom Wallet là gì?**

Hệ thống quản lý tài chính cá nhân dựa trên:
• Google Sheets (dữ liệu của bạn)
• Apps Script (logic tự động)
• Web App (giao diện thân thiện)

**Khác gì app khác?**

• Bạn sở hữu 100% dữ liệu
• Không phụ thuộc vào dịch vụ nào
• Miễn phí, không giới hạn thời gian
• Tùy biến theo nhu cầu riêng

**Phù hợp với ai?**

• Người muốn kiểm soát tiền rõ ràng
• Không thích app thu phí hàng tháng
• Muốn hiểu sâu về dòng tiền của mình
• Coi trọng quyền riêng tư dữ liệu

Bạn muốn bắt đầu chứ?
"""
    
    if has_registration:
        # Already registered, can start setup
        keyboard = [
            [InlineKeyboardButton("🚀 Bắt đầu setup", callback_data="free_start_step2")],
            [InlineKeyboardButton("« Quay lại", callback_data="back_to_start")]
        ]
    else:
        # Not registered yet, need to register first
        keyboard = [
            [InlineKeyboardButton("📝 Đăng ký ngay", callback_data="start_free_registration")],
            [InlineKeyboardButton("« Quay lại", callback_data="back_to_start")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Delete the photo message and send new text message
    try:
        await query.message.delete()
        await query.message.reply_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in learn_more: {e}")
        await query.message.reply_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )


async def back_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Go back to start menu"""
    query = update.callback_query
    await query.answer()
    
    # Import start function and call it
    from app.handlers.user.start import start
    
    # Simulate /start command
    await query.message.delete()
    
    # Create a fake message for start command
    class FakeMessage:
        def __init__(self, original_message):
            self.reply_text = original_message.reply_text
            self.reply_photo = original_message.reply_photo
            self.chat = original_message.chat
            
    class FakeUpdate:
        def __init__(self, original_update):
            self.effective_user = original_update.effective_user
            self.message = FakeMessage(original_update.callback_query.message)
    
    fake_update = FakeUpdate(update)
    await start(fake_update, context)


async def skip_sharing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User chose to skip sharing"""
    query = update.callback_query
    await query.answer()
    
    message = """
Không sao cả.

Bạn đã có hệ thống riêng rồi.
Điều quan trọng nhất là bạn dùng nó mỗi ngày.

Nếu cần trợ giúp bất cứ lúc nào,
gõ /help hoặc hỏi tôi trực tiếp.

Chúc bạn quản lý tiền tốt! 💪
"""
    
    keyboard = [
        [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )


async def show_deploy_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed deploy guide - Step by step with images"""
    query = update.callback_query
    await query.answer()
    
    # Get current step from callback data (default: overview)
    callback_data = query.data
    current_step = 0  # Overview
    
    if "deploy_guide_step" in callback_data:
        try:
            current_step = int(callback_data.split("_")[-1])
        except:
            current_step = 0
    
    # Step content
    steps = {
        0: {  # Overview
            "title": "🚀 HƯỚNG DẪN DEPLOY WEB APP",
            "text": """
Chào bạn! 👋

Đây là hướng dẫn **từng bước có hình ảnh** để deploy Web App của bạn.

**📋 Các bước chính:**

**Bước 0:** Copy Template Sheet
**Bước 1:** Mở Apps Script Editor
**Bước 2:** Click Deploy
**Bước 3:** Cấu hình Web App
**Bước 4:** Authorize (4 bước nhỏ)
**Bước 5:** Copy Web App URL

━━━━━━━━━━━━━━━━━━━━━

⏱️ **Thời gian:** Khoảng 3-5 phút
📱 **Yêu cầu:** Tài khoản Google của bạn

Bấm "▶️ Bắt đầu" để xem từng bước chi tiết!
""",
            "image": None,
            "keyboard": [
                [InlineKeyboardButton("▶️ Bắt đầu (Bước 0)", callback_data="deploy_guide_step_1")],
                [InlineKeyboardButton("« Quay lại", callback_data="free_step4_deploy_script")]
            ]
        },
        1: {  # Step 0: Copy template
            "title": "📋 BƯỚC 0: Copy Template",
            "text": """
**📋 BƯỚC 0: Copy Template Sheet**

Trước tiên, bạn cần copy template về Google Drive của mình.

**🔹 Làm thế nào:**
1. Click vào nút "Make a copy"
2. Sheet sẽ được copy vào Drive của bạn
3. Tự động mở sheet mới

━━━━━━━━━━━━━━━━━━━━━

✅ **Xong bước này?** Bấm "Tiếp ▶️" để sang bước tiếp theo!
""",
            "image": "media/images/buoc-1-copy.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_0"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_2")]
            ]
        },
        2: {  # Step 1: Open Apps Script
            "title": "📝 BƯỚC 1: Mở Apps Script Editor",
            "text": """
**📝 BƯỚC 1: Mở Apps Script Editor**

Giờ bạn cần vào Apps Script để deploy.

**🔹 Làm thế nào:**
1. Trong Google Sheet vừa copy
2. Click vào menu **Extensions**
3. Chọn **Apps Script**
4. Tab mới sẽ mở ra với code editor

━━━━━━━━━━━━━━━━━━━━━

💡 **Tip:** Đây là nơi chứa code tự động tính toán cho bạn!
""",
            "image": "media/images/buoc-2-appscript.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_1"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_3")]
            ]
        },
        3: {  # Step 2: Deploy
            "title": "🚀 BƯỚC 2: Click Deploy",
            "text": """
**🚀 BƯỚC 2: Click Deploy**

Bây giờ bạn sẽ deploy (xuất bản) Web App.

**🔹 Làm thế nào:**
1. Ở góc trên bên phải, tìm nút **"Deploy"**
2. Click vào nút **Deploy**
3. Chọn **"New deployment"**

━━━━━━━━━━━━━━━━━━━━━

⚡ **Quan trọng:** Đừng bỏ qua bước này, không deploy thì Web App không hoạt động!
""",
            "image": "media/images/buoc-3-deploy.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_2"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_4")]
            ]
        },
        4: {  # Step 3: Configure
            "title": "⚙️ BƯỚC 3: Cấu hình Web App",
            "text": """
**⚙️ BƯỚC 3: Cấu hình Web App**

Thiết lập quyền truy cập cho Web App.

**🔹 Làm thế nào:**
1. Click vào icon **⚙️ (bánh răng)**
2. Chọn type: **"Web app"**
3. **Execute as:** Chọn **"Me"** (tài khoản của bạn)
4. **Who has access:** Chọn **"Anyone"**
5. Click nút **"Deploy"** màu xanh

━━━━━━━━━━━━━━━━━━━━━

📌 **Giải thích:**
• **Me** = Web App chạy với quyền của bạn
• **Anyone** = Bất kỳ ai có link đều dùng được (chỉ bạn có link)
""",
            "image": "media/images/3.ChON_type_Web_app.JPG.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_3"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_5")]
            ]
        },
        5: {  # Step 4.1: Authorize - Click Authorize
            "title": "🔐 BƯỚC 4: Authorize (1/4)",
            "text": """
**🔐 BƯỚC 4: Authorize - Bước 1/4**

Google cần xác nhận bạn cho phép Web App truy cập Sheet.

**🔹 Làm thế nào:**
1. Một popup sẽ hiện ra
2. Click vào nút **"Authorize access"**

━━━━━━━━━━━━━━━━━━━━━

💡 **Tại sao?** Google cần chắc chắn bạn đồng ý cho phép Web App đọc/ghi dữ liệu vào Sheet của bạn.
""",
            "image": "media/images/6_Authorize.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_4"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_6")]
            ]
        },
        6: {  # Step 4.2: Authorize - Click Advanced
            "title": "🔐 BƯỚC 4: Authorize (2/4)",
            "text": """
**🔐 BƯỚC 4: Authorize - Bước 2/4**

Google sẽ cảnh báo vì Web App chưa được verify.

**🔹 Làm thế nào:**
1. Popup cảnh báo sẽ xuất hiện
2. Click vào link **"Advanced"** (Nâng cao)

━━━━━━━━━━━━━━━━━━━━━

⚠️ **Đừng lo!** Đây là Web App của chính bạn, hoàn toàn an toàn. Google chỉ cảnh báo vì chưa được kiểm duyệt chính thức (mất phí + thời gian).
""",
            "image": "media/images/6.1_Authorize_Advance.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_5"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_7")]
            ]
        },
        7: {  # Step 4.3: Authorize - Go to project
            "title": "🔐 BƯỚC 4: Authorize (3/4)",
            "text": """
**🔐 BƯỚC 4: Authorize - Bước 3/4**

Xác nhận bạn muốn tiếp tục với Web App chưa verify.

**🔹 Làm thế nào:**
1. Sau khi click "Advanced"
2. Click vào link **"Go to [Untitled project] (unsafe)"**

━━━━━━━━━━━━━━━━━━━━━

✅ **An toàn 100%:** Bạn đang cấp quyền cho chính code của mình, không phải ứng dụng bên thứ 3!
""",
            "image": "media/images/6.2_Authorize_verify.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_6"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_8")]
            ]
        },
        8: {  # Step 4.4: Authorize - Allow permissions
            "title": "🔐 BƯỚC 4: Authorize (4/4)",
            "text": """
**🔐 BƯỚC 4: Authorize - Bước 4/4 (Cuối cùng!)**

Cho phép các quyền cần thiết cho Web App.

**🔹 Làm thế nào:**
1. Danh sách quyền sẽ hiển thị
2. Click **"Select All"** (Chọn tất cả)
3. Click nút **"Continue"** màu xanh

━━━━━━━━━━━━━━━━━━━━━

📋 **Quyền yêu cầu:**
• Đọc/ghi Google Sheets
• Gửi email (cho reminder)
• Kết nối với services khác

🎉 **Gần xong rồi!** Chỉ còn 1 bước nữa thôi!
""",
            "image": "media/images/6.3_Authorize_cuoi.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_7"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_9")]
            ]
        },
        9: {  # Step 5: Copy URL
            "title": "🎊 BƯỚC 5: Copy Web App URL",
            "text": """
**🎊 BƯỚC 5: Copy Web App URL (XONG!)**

Lấy link Web App để sử dụng!

**🔹 Làm thế nào:**
1. Popup thành công sẽ hiện ra
2. Bạn sẽ thấy **"Web app URL"**
3. Click vào icon **📋 Copy** bên cạnh URL
4. Lưu lại URL này (dán vào Note hoặc gửi cho bot)

━━━━━━━━━━━━━━━━━━━━━

✅ **HOÀN THÀNH!**

🎉 Chúc mừng! Bạn đã deploy thành công Web App!

🔗 **Link này dùng để làm gì?**
• Mở Web App trên điện thoại/máy tính
• Ghi chi tiêu nhanh mọi lúc mọi nơi
• Xem báo cáo tài chính real-time

💾 **Lưu ý:** Hãy lưu link này cẩn thận. Đây là Web App riêng của bạn!
""",
            "image": "media/images/6.4_Authorize_copy_link.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_8"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_10")],
                [InlineKeyboardButton("🏠 Về menu", callback_data="free_step4_deploy_script")]
            ]
        },
        10: {  # Step 6: Login to Web App
            "title": "🌐 BƯỚC 6: Đăng nhập Web App",
            "text": """
**🌐 BƯỚC 6: Đăng nhập vào Web App**

Bây giờ hãy mở Web App của bạn lần đầu tiên!

**🔹 Làm thế nào:**
1. Mở Web App URL bạn vừa copy
2. Nhập **tên đăng nhập:** mặc định là `Admin`
   (💡 Bạn có thể đổi trong Google Sheet của bạn)
3. Nhập **mật khẩu:** mặc định là `2369`
   (💡 Bạn cũng có thể đổi trong Google Sheet)
4. Đợi Web App load xong

━━━━━━━━━━━━━━━━━━━━━

🔐 **An toàn 100%:**
Bạn đang đăng nhập vào Web App riêng của bạn.
Dữ liệu chỉ lưu trên Google Drive của bạn.
Không ai khác có quyền truy cập!

⏱️ **Lần đầu có thể mất 5-10 giây để load.**
""",
            "image": "media/images/web_app_login.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_9"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_11")]
            ]
        },
        11: {  # Step 7: Main Screen
            "title": "📊 BƯỚC 7: Màn hình chính",
            "text": """
**📊 BƯỚC 7: Màn hình chính Web App**

Chào mừng bạn đến với Freedom Wallet! 🎉

**🔹 Bạn sẽ thấy:**
• 💰 **Tổng tài sản** - Toàn cảnh tài chính hiện tại
• 📊 **Dòng tiền** - Thu nhập & Chi tiêu tháng này
• 📈 **Biểu đồ** - Phân tích chi tiêu theo danh mục
• 🎯 **Cấp độ tài chính** - Đánh giá sức khỏe tài chính
• ⚡ **Ghi nhanh** - Nút ghi giao dịch siêu tốc

━━━━━━━━━━━━━━━━━━━━━

✨ **Đây là lần đầu tiên:**
Bạn nhìn thấy toàn bộ tiền của mình ở một nơi.
Bạn kiểm soát 100% dữ liệu.
Bạn sở hữu hệ thống tài chính riêng!

💡 **Bạn có thể:**
• Bookmark trang này để truy cập nhanh
• Add to Home Screen trên mobile
• Chia sẻ với vợ/chồng nếu muốn
""",
            "image": "media/images/web_apps.jpg",
            "keyboard": [
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_10"), 
                 InlineKeyboardButton("Tiếp ▶️", callback_data="deploy_guide_step_12")]
            ]
        },
        12: {  # Step 8: Connect to Bot Offer
            "title": "🤖 Kết nối với Bot?",
            "text": """
**🤖 Bạn có muốn kết nối Freedom Wallet Bot?**

━━━━━━━━━━━━━━━━━━━━━

**✨ LỢI ÍCH KHI KẾT NỐI BOT:**

1️⃣ **Ghi chi tiêu siêu nhanh qua Telegram**
   → Chỉ cần gửi: "Cà phê 35k"
   → Bot tự động ghi vào Sheet của bạn!

2️⃣ **Xem báo cáo mọi lúc mọi nơi**
   → /balance - Xem số dư tài khoản
   → /spending - Xem chi tiêu tháng này
   → Không cần mở Web App!

3️⃣ **Nhắc nhở thông minh**
   → Nhắc ghi chi tiêu hàng ngày
   → Theo dõi streak (chuỗi ngày liên tục)
   → Gamification - Tạo động lực!

4️⃣ **AI phân tích & tư vấn**
   → Phân tích thói quen chi tiêu
   → Đề xuất tiết kiệm cá nhân hóa
   → Chat với AI advisor bất cứ lúc nào

━━━━━━━━━━━━━━━━━━━━━

**🔹 Để kết nối, bot cần 2 thông tin:**
• 📋 **Sheet ID** (từ URL Sheet của bạn)
• 🔗 **Web App URL** (bạn vừa copy)

**🔐 An toàn:**
Bot chỉ ghi dữ liệu vào Sheet của bạn.
Không đọc thông tin cá nhân khác.
Bạn có thể ngắt kết nối bất cứ lúc nào.

━━━━━━━━━━━━━━━━━━━━━

**❓ Bạn có muốn kết nối ngay không?**
""",
            "image": None,
            "keyboard": [
                [InlineKeyboardButton("✅ Có, tôi muốn kết nối", callback_data="connect_webapp_now")],
                [InlineKeyboardButton("⏭️ Không, tôi tự làm sau", callback_data="skip_webapp_setup")],
                [InlineKeyboardButton("◀️ Quay lại", callback_data="deploy_guide_step_11")]
            ]
        }
    }
    
    step_data = steps.get(current_step, steps[0])
    
    # Always delete previous message and send new one
    # This avoids "no text to edit" error when transitioning between photo/text messages
    try:
        await query.message.delete()
    except:
        pass  # Ignore if message already deleted
    
    # Send image with caption if image exists
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
            # Fallback to text only if image fails
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"**{step_data['title']}**\n\n{step_data['text']}\n\n⚠️ (Không tải được hình: {e})",
                reply_markup=InlineKeyboardMarkup(step_data["keyboard"]),
                parse_mode="Markdown"
            )
    else:
        # Text only (no image)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"**{step_data['title']}**\n\n{step_data['text']}",
            reply_markup=InlineKeyboardMarkup(step_data["keyboard"]),
            parse_mode="Markdown"
        )


# Register all handlers
def register_free_flow_handlers(application):
    """Register all FREE flow handlers"""
    from telegram.ext import CallbackQueryHandler
    
    # Note: start_free_registration is handled by registration ConversationHandler in main.py
    
    application.add_handler(CallbackQueryHandler(free_check_registration, pattern="^free_check_registration$"))
    application.add_handler(CallbackQueryHandler(free_step2_show_value, pattern="^free_start_step2$"))
    application.add_handler(CallbackQueryHandler(free_step3_copy_template, pattern="^free_step3_copy_template$"))
    application.add_handler(CallbackQueryHandler(free_step4_deploy_script, pattern="^free_step4_deploy_script$"))
    application.add_handler(CallbackQueryHandler(show_deploy_guide, pattern="^show_deploy_guide$"))
    application.add_handler(CallbackQueryHandler(show_deploy_guide, pattern="^deploy_guide_step_"))  # NEW: Handle all steps
    application.add_handler(CallbackQueryHandler(free_step5_open_webapp, pattern="^free_step5_open_webapp$"))
    application.add_handler(CallbackQueryHandler(free_step6_first_action, pattern="^free_step6_first_action$"))
    application.add_handler(CallbackQueryHandler(free_step7_reinforce, pattern="^free_step7_reinforce$"))
    application.add_handler(CallbackQueryHandler(free_step8_optional_sharing, pattern="^free_step8_optional_sharing$"))
    application.add_handler(CallbackQueryHandler(learn_more, pattern="^learn_more$"))
    application.add_handler(CallbackQueryHandler(back_to_start, pattern="^back_to_start$"))
    application.add_handler(CallbackQueryHandler(skip_sharing, pattern="^skip_sharing$"))
    
    logger.info("✅ FREE flow handlers registered")

