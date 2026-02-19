"""
Simplified Registration Flow - Pay What You Want Model
Không phân biệt tier, cho dùng full tính năng, trả phí tùy tâm

Flow:
1. User đăng ký từ web → Bot nhận deep link
2. Xác nhận thông tin đúng/sai
3. Chúc mừng
4. Hướng dẫn setup Web App từng bước
5. Hướng dẫn sử dụng
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime
from app.utils.database import get_user_by_id, update_user_registration, SessionLocal, User
from app.utils.sheets import sync_web_registration


async def handle_web_registration(update: Update, context: ContextTypes.DEFAULT_TYPE, email_hash: str):
    """
    Xử lý user đăng ký từ web/landing page
    
    Flow:
    1. Lấy thông tin từ Google Sheets
    2. Hiển thị thông tin để xác nhận
    3. Nếu đúng → Chúc mừng + Hướng dẫn setup
    """
    user = update.effective_user
    logger.info(f"🌐 Web registration flow for user {user.id}, email_hash: {email_hash}")
    
    # Step 1: Sync data from Google Sheets
    web_data = await sync_web_registration(user.id, user.username or '', email_hash)
    
    if not web_data:
        # User chưa đăng ký → Show onboarding flow
        await show_onboarding_flow(update, context)
        return
    
    # Step 2: Hiển thị thông tin để xác nhận
    email = web_data.get('email', 'N/A')
    phone = web_data.get('phone', 'Chưa cung cấp')
    full_name = web_data.get('full_name', user.first_name)
    
    confirmation_message = (
        f"👋 **Chào {full_name}!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎉 **Chúng tôi đã nhận được đăng ký của bạn!**\n\n"
        "📋 **Vui lòng xác nhận thông tin:**\n\n"
        f"📧 Email: `{email}`\n"
        f"📱 Phone: `{phone}`\n"
        f"👤 Họ tên: `{full_name}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ **Thông tin có chính xác không?**"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Đúng rồi, tiếp tục", callback_data=f"confirm_info_yes|{email}"),
            InlineKeyboardButton("❌ Sai, đăng ký lại", callback_data="confirm_info_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Store web_data in context for later use
    context.user_data['pending_registration'] = web_data
    
    await update.message.reply_text(
        confirmation_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def confirm_registration_yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User xác nhận thông tin đúng → Chúc mừng + Hướng dẫn setup"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Get registration data from context
    web_data = context.user_data.get('pending_registration')
    if not web_data:
        await query.edit_message_text(
            "❌ Phiên đăng ký hết hạn. Vui lòng bắt đầu lại từ link trong email."
        )
        return
    
    # Save to database
    await update_user_registration(
        user_id=user.id,
        email=web_data.get('email'),
        phone=web_data.get('phone'),
        full_name=web_data.get('full_name'),
        source='WEB'
    )
    
    logger.info(f"✅ User {user.id} confirmed registration: {web_data.get('email')}")
    
    # Chúc mừng
    full_name = web_data.get('full_name', user.first_name)
    
    congratulations_message = (
        f"🎊 **Chúc mừng {full_name}!** 🎊\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✨ **Bạn đã chính thức trở thành thành viên Freedom Wallet!**\n\n"
        "🎁 **Những gì bạn nhận được:**\n\n"
        "✅ **FULL tính năng** - Không giới hạn\n"
        "✅ **Ghi chi tiêu siêu nhanh** qua chat\n"
        "✅ **AI phân tích tài chính** thông minh\n"
        "✅ **Báo cáo real-time** trực quan\n"
        "✅ **Nhắc nhở tự động** mỗi ngày\n"
        "✅ **Hỗ trợ ưu tiên** 24/7\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 **Freedom Wallet hoạt động theo mô hình:**\n"
        "**\"Pay What You Want\"** (Phí tùy tâm)\n\n"
        "• Dùng **FULL tính năng** trước - không giới hạn\n"
        "• Nếu thấy có giá trị → Ủng hộ monthly/yearly\n"
        "• Không ép buộc, **hoàn toàn tùy tâm** bạn 😊\n\n"
        "🎯 **Phí ủng hộ giúp:**\n"
        "✓ Duy trì & nâng cấp hệ thống\n"
        "✓ Phát triển tính năng mới\n"
        "✓ Hỗ trợ hàng triệu người có công cụ đạt tự do tài chính\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 **Sẵn sàng bắt đầu chưa?**"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Bắt đầu setup ngay!", callback_data="start_setup_guide")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        congratulations_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def confirm_registration_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User báo thông tin sai → Cho nhập lại NGAY trong Telegram"""
    query = update.callback_query
    await query.answer()
    
    message = (
        "😅 **Thông tin chưa chính xác?**\n\n"
        "Không sao! Hãy nhập lại thông tin ngay tại đây.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 **Chọn cách đăng ký:**"
    )
    
    keyboard = [
        [InlineKeyboardButton("✍️ Nhập thông tin lại", callback_data="re_register_telegram")],
        [InlineKeyboardButton("📧 Liên hệ hỗ trợ", callback_data="contact_support")],
        [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message, 
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def start_setup_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Redirect to comprehensive deploy guide in free_flow.py
    Removed duplicate 4-step wizard - now using main deploy guide (13 steps)
    """
    query = update.callback_query
    await query.answer("📚 Đang tải hướng dẫn chi tiết...")
    
    # Redirect to deploy guide step 0
    from app.handlers.user.free_flow import show_deploy_guide_step_0
    await show_deploy_guide_step_0(update, context)


# REMOVED: setup_step2_deploy_script() - duplicate of deploy guide steps
# REMOVED: setup_step3_connect_bot() - duplicate of deploy guide steps
# URL input handler is kept below for connecting webapp after deploy


async def handle_webapp_url_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nhận và validate Web App URL từ user"""
    
    if not context.user_data.get('waiting_for_webapp_url'):
        return  # Not in setup flow
    
    user = update.effective_user
    url = update.message.text.strip()
    
    # Validate URL
    import re
    url_pattern = r'^https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec$'
    
    if not re.match(url_pattern, url):
        await update.message.reply_text(
            "❌ **URL không hợp lệ**\n\n"
            "URL phải có dạng:\n"
            "`https://script.google.com/macros/s/AKfycby.../exec`\n\n"
            "Vui lòng paste lại URL đúng."
        )
        return
    
    # Test connection
    from app.services.sheets_api_client import SheetsAPIClient
    
    await update.message.reply_text("⏳ Đang kiểm tra kết nối...")
    
    try:
        # Get spreadsheet ID from user
        db_user = await get_user_by_id(user.id)
        if not db_user or not db_user.spreadsheet_id:
            await update.message.reply_text(
                "❌ Lỗi: Không tìm thấy Spreadsheet ID.\n\n"
                "Vui lòng chạy lại từ đầu hoặc liên hệ admin."
            )
            return
        
        # Test API
        client = SheetsAPIClient(db_user.spreadsheet_id, url)
        result = await client.ping()
        
        if result.get('success'):
            # Save URL to database
            from app.utils.database import SessionLocal
            db = SessionLocal()
            try:
                user_record = db.query(User).filter(User.id == user.id).first()
                if user_record:
                    user_record.web_app_url = url
                    db.commit()
                    logger.info(f"✅ Saved Web App URL for user {user.id}")
                    
                    # Clear waiting state
                    context.user_data['waiting_for_webapp_url'] = False
                    
                    # Move to final step
                    await setup_step4_complete(update, context)
                else:
                    await update.message.reply_text("❌ Lỗi: Không tìm thấy user trong database")
            finally:
                db.close()
        else:
            error_msg = result.get('error', 'Unknown error')
            await update.message.reply_text(
                f"❌ **Kết nối thất bại**\n\n"
                f"Lỗi: {error_msg}\n\n"
                "Vui lòng kiểm tra lại:\n"
                "1. URL có đúng không?\n"
                "2. Web App đã deploy chưa?\n"
                "3. Access setting: Anyone\n\n"
                "Paste lại URL để thử lại."
            )
    except Exception as e:
        logger.error(f"Error testing Web App URL: {e}")
        await update.message.reply_text(
            f"❌ **Lỗi khi test kết nối**\n\n"
            f"Chi tiết: {str(e)}\n\n"
            "Vui lòng thử lại hoặc liên hệ admin."
        )


async def setup_step4_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 4: Hoàn tất setup + Hướng dẫn sử dụng"""
    
    success_message = (
        "🎉 **SETUP HOÀN TẤT!** 🎉\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✅ Bạn đã kết nối thành công!\n\n"
        "🎯 **Bây giờ bạn có thể:**\n\n"
        "1️⃣ **Ghi nhanh thu chi** ngay trong chat:\n"
        "   💬 `Cà phê 35k`\n"
        "   💬 `Lương tháng 3 15tr`\n"
        "   💬 `Ăn trưa 50k hũ NEC`\n\n"
        "2️⃣ **Xem báo cáo** bất cứ lúc nào:\n"
        "   💬 `Tháng này chi bao nhiêu?`\n"
        "   💬 `Báo cáo tháng 2`\n"
        "   💬 `/balance` (xem số dư)\n\n"
        "3️⃣ **Hỏi AI** về tài chính:\n"
        "   💬 `Tư vấn tiết kiệm cho tôi`\n"
        "   💬 `Tôi nên làm gì để đạt mục tiêu?`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📖 **Muốn xem hướng dẫn chi tiết?**\n"
        "👇 Chọn menu bên dưới:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📖 Hướng dẫn sử dụng", callback_data="show_usage_guide")],
        [InlineKeyboardButton("🎬 Video tutorials", url="https://youtube.com/playlist/YOUR_PLAYLIST")],
        [InlineKeyboardButton("🚀 Bắt đầu ghi ngay!", callback_data="quick_record_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send via message (not edit since we're coming from text input)
    await update.message.reply_text(
        success_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_usage_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị hướng dẫn sử dụng chi tiết"""
    query = update.callback_query
    await query.answer()
    
    guide = (
        "📖 **HƯỚNG DẪN SỬ DỤNG FREEDOM WALLET**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**1️⃣ GHI NHANH THU CHI**\n\n"
        "Chỉ cần gửi tin nhắn theo cú pháp:\n\n"
        "📝 **Cú pháp cơ bản:**\n"
        "`[Danh mục] [Số tiền]`\n\n"
        "**Ví dụ:**\n"
        "• `Cà phê 35k` → Chi 35,000đ cho Cà phê\n"
        "• `Ăn trưa 50k` → Chi 50,000đ cho Ăn uống\n"
        "• `Lương 15tr` → Thu 15,000,000đ lương\n\n"
        "📝 **Cú pháp nâng cao:**\n"
        "`[Danh mục] [Số tiền] [Hũ] [Ghi chú]`\n\n"
        "**Ví dụ:**\n"
        "• `Cà phê 35k NEC` → Lấy từ hũ NEC\n"
        "• `Xăng 200k PLAY đi chơi` → Thêm ghi chú\n"
        "• `Lương 15tr FFA tiết kiệm` → Cho vào hũ FFA\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**2️⃣ XEM BÁO CÁO**\n\n"
        "• `/balance` - Số dư tất cả hũ\n"
        "• `/spending` - Chi tiêu tháng này\n"
        "• `Báo cáo tháng 2` - Báo cáo tháng 2\n"
        "• `Chi bao nhiêu tuần này?` - Hỏi AI\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**3️⃣ HỎI AI TƯ VẤN**\n\n"
        "Gửi tin nhắn tự nhiên, AI sẽ trả lời:\n\n"
        "• `Tư vấn tiết kiệm cho tôi`\n"
        "• `Tôi chi nhiều danh mục nào?`\n"
        "• `Làm sao để đạt mục tiêu 50tr?`\n"
        "• `So sánh tháng này với tháng trước`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**4️⃣ MENU NHANH**\n\n"
        "Dùng nút menu phía dưới để:\n"
        "• Ghi nhanh thu chi\n"
        "• Xem báo cáo\n"
        "• Quản lý hệ thống\n"
        "• Cài đặt\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 **Mẹo hay:**\n"
        "• Ghi mỗi ngày để có thói quen tốt\n"
        "• Dùng AI để phân tích xu hướng\n"
        "• Xem báo cáo cuối tuần để điều chỉnh\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "❓ Cần hỗ trợ? Gõ /support"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Bắt đầu dùng ngay!", callback_data="quick_record_menu")],
        [InlineKeyboardButton("📹 Xem video tutorials", url="https://youtube.com/playlist/YOUR_PLAYLIST")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        guide,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_onboarding_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Hiển thị flow quảng bá lợi ích của Freedom Wallet cho user chưa đăng ký
    """
    user = update.effective_user
    
    onboarding_message = (
        f"👋 **Chào {user.first_name}!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **Chào mừng đến với Freedom Wallet!**\n\n"
        "💰 **Quản lý tài chính thông minh với:**\n\n"
        "✅ **Ghi chép tự động** - AI phân loại giao dịch\n"
        "✅ **6 Jars Method** - Phân bổ tiền khoa học\n"
        "✅ **Báo cáo trực quan** - Dashboard thời gian thực\n"
        "✅ **Đồng bộ Google Sheets** - Dữ liệu luôn an toàn\n"
        "✅ **Hoàn toàn MIỄN PHÍ** - Trả phí tùy tâm\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎁 **Đặc biệt:**\n"
        "• Không giới hạn giao dịch\n"
        "• Không quảng cáo\n"
        "• Hỗ trợ 24/7\n"
        "• Cộng đồng 10,000+ người dùng\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 **Bạn sẽ có được:**\n"
        "🔹 Kiểm soát hoàn toàn chi tiêu\n"
        "🔹 Tiết kiệm được nhiều hơn 30%\n"
        "🔹 Đạt mục tiêu tài chính nhanh hơn\n"
        "🔹 Ngủ ngon hơn (không lo tiền nong!)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 **Bắt đầu ngay chỉ với 3 bước:**"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Đăng ký ngay (30 giây)", callback_data="start_quick_registration")],
        [InlineKeyboardButton("📹 Xem demo", callback_data="show_demo")],
        [InlineKeyboardButton("💬 Tìm hiểu thêm", callback_data="learn_more_benefits")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        onboarding_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def start_quick_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bắt đầu flow đăng ký nhanh"""
    query = update.callback_query
    await query.answer()
    
    registration_message = (
        "📝 **Đăng ký nhanh - 3 bước đơn giản**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Bước 1:** Điền form đăng ký (30 giây)\n"
        "👉 https://freedomwallet.app/register\n\n"
        "**Bước 2:** Nhấn nút trong email xác nhận\n\n"
        "**Bước 3:** Quay lại bot này để setup\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "✨ **Sau khi đăng ký xong:**\n"
        "• Bấm vào link trong email\n"
        "• Bot sẽ tự động nhận diện bạn\n"
        "• Hướng dẫn từng bước setup Google Sheets\n"
        "• Bắt đầu ghi chép ngay!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 **Lưu ý:** Sử dụng email Gmail để dễ dàng kết nối Google Sheets"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔗 Mở form đăng ký", url="https://freedomwallet.app/register")],
        [InlineKeyboardButton("✅ Tôi đã đăng ký xong", callback_data="check_registration")],
        [InlineKeyboardButton("← Quay lại", callback_data="back_to_onboarding")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        registration_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def show_demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị video demo"""
    query = update.callback_query
    await query.answer()
    
    demo_message = (
        "📹 **Xem Freedom Wallet hoạt động**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎬 **Video tutorials:**\n\n"
        "1️⃣ **Giới thiệu tổng quan** (2 phút)\n"
        "   → Hiểu cách app hoạt động\n\n"
        "2️⃣ **Setup trong 5 phút** (5 phút)\n"
        "   → Từng bước cài đặt chi tiết\n\n"
        "3️⃣ **Ghi chép hàng ngày** (3 phút)\n"
        "   → Cách dùng nhanh nhất\n\n"
        "4️⃣ **6 Jars Method** (8 phút)\n"
        "   → Phân bổ tiền thông minh\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💬 **Câu chuyện thành công:**\n"
        "\"Sau 3 tháng dùng Freedom Wallet, tôi tiết kiệm được 8 triệu/tháng!\"\n"
        "- Nguyễn Văn A, Hà Nội\n\n"
        "\"App này giúp tôi kiểm soát chi tiêu và đạt mục tiêu mua nhà!\"\n"
        "- Trần Thị B, TP.HCM"
    )
    
    keyboard = [
        [InlineKeyboardButton("▶️ Xem playlist đầy đủ", url="https://youtube.com/playlist/YOUR_PLAYLIST")],
        [InlineKeyboardButton("🚀 Đăng ký ngay", callback_data="start_quick_registration")],
        [InlineKeyboardButton("← Quay lại", callback_data="back_to_onboarding")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        demo_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def learn_more_benefits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hiển thị chi tiết lợi ích"""
    query = update.callback_query
    await query.answer()
    
    benefits_message = (
        "💎 **Tại sao chọn Freedom Wallet?**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **1. Đơn giản & Nhanh chóng**\n"
        "• Ghi giao dịch trong 5 giây\n"
        "• AI tự động phân loại\n"
        "• Không cần nhập thủ công nhiều\n\n"
        "📊 **2. Khoa học & Hiệu quả**\n"
        "• Áp dụng 6 Jars Method\n"
        "• Phân bổ tiền theo mục đích\n"
        "• Dashboard trực quan dễ hiểu\n\n"
        "🔒 **3. An toàn & Riêng tư**\n"
        "• Dữ liệu lưu trên Google Sheets của BẠN\n"
        "• Bot chỉ đọc/ghi, không lưu trữ\n"
        "• Bạn kiểm soát 100% dữ liệu\n\n"
        "🆓 **4. Miễn phí & Công bằng**\n"
        "• Dùng toàn bộ tính năng miễn phí\n"
        "• Trả phí tùy tâm nếu thấy hữu ích\n"
        "• Không quảng cáo, không giới hạn\n\n"
        "🤝 **5. Cộng đồng & Hỗ trợ**\n"
        "• Group 10,000+ người dùng\n"
        "• Chia sẻ kinh nghiệm quản lý tài chính\n"
        "• Hỗ trợ 24/7 khi cần\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📈 **Kết quả thực tế:**\n"
        "• 85% user tiết kiệm được nhiều hơn\n"
        "• 92% user kiểm soát tốt hơn chi tiêu\n"
        "• 78% user đạt mục tiêu tài chính\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⏰ **Đã sẵn sàng thay đổi cuộc sống?**"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Đăng ký ngay!", callback_data="start_quick_registration")],
        [InlineKeyboardButton("📹 Xem demo trước", callback_data="show_demo")],
        [InlineKeyboardButton("← Quay lại", callback_data="back_to_onboarding")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        benefits_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def back_to_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quay lại màn hình onboarding chính"""
    query = update.callback_query
    await query.answer()
    
    # Gọi lại hàm show_onboarding_flow nhưng dùng query thay vì message
    user = update.effective_user
    
    onboarding_message = (
        f"👋 **Chào {user.first_name}!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **Chào mừng đến với Freedom Wallet!**\n\n"
        "💰 **Quản lý tài chính thông minh với:**\n\n"
        "✅ **Ghi chép tự động** - AI phân loại giao dịch\n"
        "✅ **6 Jars Method** - Phân bổ tiền khoa học\n"
        "✅ **Báo cáo trực quan** - Dashboard thời gian thực\n"
        "✅ **Đồng bộ Google Sheets** - Dữ liệu luôn an toàn\n"
        "✅ **Hoàn toàn MIỄN PHÍ** - Trả phí tùy tâm\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎁 **Đặc biệt:**\n"
        "• Không giới hạn giao dịch\n"
        "• Không quảng cáo\n"
        "• Hỗ trợ 24/7\n"
        "• Cộng đồng 10,000+ người dùng\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 **Bạn sẽ có được:**\n"
        "🔹 Kiểm soát hoàn toàn chi tiêu\n"
        "🔹 Tiết kiệm được nhiều hơn 30%\n"
        "🔹 Đạt mục tiêu tài chính nhanh hơn\n"
        "🔹 Ngủ ngon hơn (không lo tiền nong!)\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👇 **Bắt đầu ngay chỉ với 3 bước:**"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚀 Đăng ký ngay (30 giây)", callback_data="start_quick_registration")],
        [InlineKeyboardButton("📹 Xem demo", callback_data="show_demo")],
        [InlineKeyboardButton("💬 Tìm hiểu thêm", callback_data="learn_more_benefits")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        onboarding_message,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def check_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kiểm tra xem user đã đăng ký chưa"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    
    # Check database
    db_user = get_user_by_id(user.id)
    
    if db_user and db_user.email:
        # Đã đăng ký rồi
        await query.edit_message_text(
            "✅ **Tuyệt vời! Tìm thấy thông tin của bạn**\n\n"
            "Bạn đã đăng ký thành công!\n\n"
            "Bây giờ chúng ta sẽ setup Google Sheets để bắt đầu ghi chép. 🚀"
        )
        # Chuyển sang flow setup
        await start_setup_guide(update, context)
    else:
        # Chưa đăng ký
        await query.edit_message_text(
            "⏳ **Chưa tìm thấy thông tin đăng ký**\n\n"
            "Có thể do:\n"
            "• Bạn chưa điền form\n"
            "• Chưa bấm link xác nhận trong email\n"
            "• Hệ thống đang xử lý (đợi 1-2 phút)\n\n"
            "📝 **Hướng dẫn:**\n"
            "1. Điền form tại: https://freedomwallet.app/register\n"
            "2. Check email và bấm link xác nhận\n"
            "3. Quay lại bot này và bấm nút dưới đây"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 Kiểm tra lại", callback_data="check_registration")],
            [InlineKeyboardButton("🔗 Mở form đăng ký", url="https://freedomwallet.app/register")],
            [InlineKeyboardButton("💬 Liên hệ hỗ trợ", callback_data="contact_support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_reply_markup(reply_markup=reply_markup)


async def re_register_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle re-registration request - Start registration flow in Telegram"""
    query = update.callback_query
    await query.answer()
    
    # Start registration ConversationHandler
    from app.handlers.user.registration import start_registration
    
    # Call registration flow
    await start_registration(update, context)


async def contact_support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle contact support request"""
    query = update.callback_query
    await query.answer()
    
    message = (
        "💬 **HỖ TRỢ TRỰC TIẾP**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Cách 1: Telegram Group**\n"
        "👉 https://t.me/freedomwalletapp\n"
        "• Hỏi đáp trực tiếp\n"
        "• Admin & community hỗ trợ\n"
        "• Response trong 1-2 giờ\n\n"
        "**Cách 2: Email**\n"
        "📧 support@freedomwallet.app\n"
        "• Gửi screenshot vấn đề\n"
        "• Chi tiết thông tin cần sửa\n"
        "• Response trong 24h\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 **Lưu ý:** Đính kèm email/phone đã đăng ký để admin hỗ trợ nhanh hơn!"
    )
    
    keyboard = [
        [InlineKeyboardButton("💬 Tham gia Group", url="https://t.me/freedomwalletapp")],
        [InlineKeyboardButton("🏠 Về trang chủ", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, parse_mode="Markdown", reply_markup=reply_markup)


def register_simplified_registration_handlers(application):
    """Register all simplified registration handlers"""
    from telegram.ext import CallbackQueryHandler, MessageHandler, filters
    
    # Onboarding flow callbacks
    application.add_handler(CallbackQueryHandler(start_quick_registration, pattern="^start_quick_registration$"))
    application.add_handler(CallbackQueryHandler(show_demo, pattern="^show_demo$"))
    application.add_handler(CallbackQueryHandler(learn_more_benefits, pattern="^learn_more_benefits$"))
    application.add_handler(CallbackQueryHandler(back_to_onboarding, pattern="^back_to_onboarding$"))
    application.add_handler(CallbackQueryHandler(check_registration, pattern="^check_registration$"))
    
    # Registration confirmation callbacks
    application.add_handler(CallbackQueryHandler(confirm_registration_yes, pattern="^confirm_info_yes"))
    application.add_handler(CallbackQueryHandler(confirm_registration_no, pattern="^confirm_info_no$"))
    
    # Re-registration callback (NEW)
    application.add_handler(CallbackQueryHandler(re_register_handler, pattern="^re_register_telegram$"))
    application.add_handler(CallbackQueryHandler(contact_support_handler, pattern="^contact_support$"))
    
    # Setup guide callbacks
    application.add_handler(CallbackQueryHandler(start_setup_guide, pattern="^start_setup_guide$"))
    # REMOVED: setup_step2 and setup_step3 - now redirecting to deploy guide
    application.add_handler(CallbackQueryHandler(show_usage_guide, pattern="^show_usage_guide$"))
    
    # Message handler for Web App URL input (during setup)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Regex(r'https://script\.google\.com/'),
            handle_webapp_url_input
        ),
        group=50  # Higher priority than general message handler
    )
    
    logger.info("✅ Simplified registration handlers registered")
