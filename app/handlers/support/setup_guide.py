"""
Setup Guide Handler - Step-by-step usage guide
Structure: Setup (3 steps) → Accounts → Categories → Debts → Investments → Assets
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from loguru import logger

# Setup Guide Content - 10 Steps (New structure)
SETUP_GUIDE_STEPS = {
    0: {
        "title": "📘 BƯỚC 2: HƯỚNG DẪN SỬ DỤNG",
        "content": """
🎉 **Tuyệt vời! Bạn đã hoàn thành Bước 1!**

━━━━━━━━━━━━━━━━━━━━━

**📍 BẠN ĐANG Ở ĐÂU?**

✅ Bước 1: Tạo Web App (hoàn thành)
➡️ **BƯỚC 2: Học cách sử dụng** (bạn đang ở đây)

━━━━━━━━━━━━━━━━━━━━━

**🎯 CÁCH SỬ DỤNG HIỆU QUẢ**

**1️⃣ CÀI ĐẶT** (3 bước)
   a. Xóa dữ liệu mẫu
   b. Cài đặt hũ tiền
   c. 5 Cấp bậc tài chính

**2️⃣ TÀI KHOẢN** - Biết tiền ở đâu

**3️⃣ DANH MỤC** - Phân loại chi tiêu

**4️⃣ KHOẢN NỢ** - Làm chủ nợ

**5️⃣ ĐẦU TƯ** - Tiền làm việc cho bạn

**6️⃣ TÀI SẢN** - Tính Net Worth

━━━━━━━━━━━━━━━━━━━━━

⏱ **Thời gian**: 15-20 phút
💡 *Xem lại: /huongdan*
""",
        "image": None
    },
    
    1: {
        "title": "⚙️ CÀI ĐẶT (1/3) – XÓA DỮ LIỆU MẪU",
        "content": """
**🎯 Mục tiêu: Làm sạch app, chuẩn bị nhập dữ liệu thật**

━━━━━━━━━━━━━━━━━━━━━

**📋 CÁCH LÀM:**

1️⃣ Mở Web App của bạn

2️⃣ Vào **Cài đặt** (Settings) ở menu trên

3️⃣ Nhấn **Xóa dữ liệu mẫu** (Delete Sample Data)

4️⃣ Xác nhận → Tất cả dữ liệu mẫu bị xóa

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• App "trắng tinh"
• Sẵn sàng cho dữ liệu thực tế

━━━━━━━━━━━━━━━━━━━━━

**💡 Lưu ý:**
*Chỉ xóa dữ liệu mẫu 1 lần duy nhất khi bắt đầu!*
""",
        "image": "media/images/cai_dat.png"
    },
    
    2: {
        "title": "⚙️ CÀI ĐẶT (2/3) – CÀI ĐẶT HŨ TIỀN",
        "content": """
**🎯 Mục tiêu: Thiết lập 6 Hũ Tiền - Trái tim Freedom Wallet**

━━━━━━━━━━━━━━━━━━━━━

**🎯 6 HŨ TIÊU CHUẨN:**

1️⃣ **🏠 Chi tiêu thiết yếu** (55%)
2️⃣ **🎉 Hưởng thụ** (10%)
3️⃣ **🎓 Giáo dục** (10%)
4️⃣ **💰 Tiết kiệm dài hạn** (10%)
5️⃣ **💼 Đầu tư** (10%)
6️⃣ **❤️ Cho đi** (5%)

━━━━━━━━━━━━━━━━━━━━━

**📋 CÁCH LÀM:**

1️⃣ Vào **Cài đặt** → **6 Jars Settings**

2️⃣ Nhập % cho từng hũ (tổng = 100%)

3️⃣ Lưu lại → Hệ thống tự động phân bổ

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Mỗi khoản thu tự động phân bổ
• Tiêu tiền có kỉ luật
• Vừa sống tốt, vừa giàu lên
""",
        "image": "media/images/hu_tien.jpg"
    },
    
    3: {
        "title": "⚙️ CÀI ĐẶT (3/3) – 5 CẤP BẬC TÀI CHÍNH",
        "content": """
**🎯 Mục tiêu: Xác định bạn đang ở đâu, đi đến đâu**

━━━━━━━━━━━━━━━━━━━━━

**📈 5 CẤP BẬC:**

🔴 **Cấp 1: Bình ổn tài chính**
   → Chi tiêu bằng thu nhập

🟠 **Cấp 2: An toàn tài chính**
   → Có quỹ dự phòng 3-6 tháng

🟡 **Cấp 3: Độc lập tài chính**
   → Không phụ thuộc lương

🟢 **Cấp 4: Tự do tài chính**
   → Thu nhập thụ động > chi tiêu

🔵 **Cấp 5: Dồi dào tài chính**
   → Làm được bất cứ điều gì

━━━━━━━━━━━━━━━━━━━━━

**📋 CÁCH DÙNG:**

1️⃣ Tự đánh giá bạn đang ở cấp nào

2️⃣ Đặt mục tiêu lên cấp tiếp theo

3️⃣ Theo dõi tiến độ hàng tháng

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Có lộ trình rõ ràng
• Động lực thúc đẩy
• Biết mình cần làm gì
""",
        "image": "media/images/5_cap_bac_tai_chinh.jpg"
    },
    
    4: {
        "title": "💳 TÀI KHOẢN – BIẾT TIỀN Ở ĐÂU",
        "content": """
**🎯 Mục tiêu: Biết tiền của bạn đang nằm ở đâu**

━━━━━━━━━━━━━━━━━━━━━

**📌 VÍ DỤ TÀI KHOẢN:**

• 💵 Tiền mặt
• 🏦 Tài khoản ngân hàng (VCB, TCB, MB...)
• 📱 Ví điện tử (Momo, ZaloPay, VNPay...)

━━━━━━━━━━━━━━━━━━━━━

**📋 CÁCH LÀM:**

1️⃣ Vào mục **Accounts** (Tài khoản)

2️⃣ ➕ Thêm tất cả tài khoản của bạn

3️⃣ Nhập **số dư ban đầu** (phải khớp với thực tế!)

4️⃣ Lưu lại → Xem tổng tài sản

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Biết tổng tiền có bao nhiêu
• Tiền nằm ở đâu
• Nền tảng cho tracking sau này

━━━━━━━━━━━━━━━━━━━━━

**💡 Quan trọng:**
*Số dư ban đầu sai → tất cả báo cáo sai!*
""",
        "image": "media/images/tai_khoan.jpg"
    },
    
    5: {
        "title": "📂 DANH MỤC – PHÂN LOẠI CHI TIÊU",
        "content": """
**🎯 Mục tiêu: Hiểu tiền đi đâu, vào đâu**

━━━━━━━━━━━━━━━━━━━━━

**📂 VÍ DỤ DANH MỤC:**

**Chi tiêu:**
• 🍜 Ăn uống
• 🏠 Nhà ở
• 🎓 Giáo dục
• 🎉 Giải trí
• 🚗 Di chuyển
• 👨‍⚕️ Sức khỏe

**Thu nhập:**
• 💼 Lương
• 💰 Kinh doanh
• 🎁 Quà tặng

━━━━━━━━━━━━━━━━━━━━━

**📋 CÁCH LÀM:**

1️⃣ Vào mục **Categories**

2️⃣ Thêm các danh mục phù hợp với cuộc sống

3️⃣ Khi ghi giao dịch → chọn danh mục

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Báo cáo chi tiêu theo danh mục
• Nhận diện "lỗ hổng" tiền
• Cắt giảm chi tiêu hiệu quả

━━━━━━━━━━━━━━━━━━━━━

**💡 Tip:**
*Danh mục chi tiết → phân tích tốt hơn!*
""",
        "image": "media/images/danh_muc.jpg"
    },
    
    6: {
        "title": "💳 KHOẢN NỢ – LÀM CHỦ NỢ",
        "content": """
**🎯 Mục tiêu: Không né tránh - chủ động làm chủ nợ**

━━━━━━━━━━━━━━━━━━━━━

**💳 CÓ THỂ QUẢN LÝ:**

• Nợ vay ngân hàng
• Trả góp (xe, nhà, điện thoại)
• Nợ cá nhân
• Thẻ tín dụng

━━━━━━━━━━━━━━━━━━━━━

**📋 CÁCH LÀM:**

1️⃣ Vào mục **Debts** (Khoản nợ)

2️⃣ Thêm tất cả khoản nợ hiện tại

3️⃣ Nhập: Số tiền gốc, lãi suất, kỳ hạn

4️⃣ Cập nhật khi trả nợ

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Biết chính xác tổng nợ
• Có chiến lược thoát nợ
• Giảm stress tài chính

━━━━━━━━━━━━━━━━━━━━━

**💡 Mindset:**
*"Nợ không phải kẻ thù - không biết mình nợ bao nhiêu mới là kẻ thù"*
""",
        "image": "media/images/khoan_no.jpg"
    },
    
    7: {
        "title": "📈 ĐẦU TƯ – TIỀN LÀM VIỆC CHO BẠN",
        "content": """
**🎯 Mục tiêu: Theo dõi các khoản đầu tư hiệu quả**

━━━━━━━━━━━━━━━━━━━━━

**📈 CÓ THỂ TRACKING:**

• Chứng khoán (cổ phiếu, quỹ)
• Vàng
• Bất động sản cho thuê
• Kinh doanh
• Crypto

━━━━━━━━━━━━━━━━━━━━━

**📋 CÁCH LÀM:**

1️⃣ Vào mục **Investments**

2️⃣ Thêm từng khoản đầu tư

3️⃣ Nhập: Vốn gốc, giá trị hiện tại

4️⃣ Cập nhật định kỳ → Xem ROI

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Biết đầu tư lãi/lỗ bao nhiêu
• Quyết định dựa trên số liệu
• Quản lý portfolio hiệu quả

━━━━━━━━━━━━━━━━━━━━━

**💡 Lưu ý:**
*Chỉ là công cụ tracking - không phải tư vấn đầu tư!*
""",
        "image": "media/images/dau_tu.jpg"
    },
    
    8: {
        "title": "🏠 TÀI SẢN – TÍNH NET WORTH",
        "content": """
**🎯 Mục tiêu: Biết giá trị thực sự của bạn**

━━━━━━━━━━━━━━━━━━━━━

**🏠 VÍ DỤ TÀI SẢN:**

• Nhà đất
• Xe (ô tô, xe máy)
• Trang sức, vàng
• Đồ điện tử giá trị
• Tài sản khác

━━━━━━━━━━━━━━━━━━━━━

**📋 CÁCH LÀM:**

1️⃣ Vào mục **Assets**

2️⃣ Thêm tất cả tài sản lớn

3️⃣ Nhập: Giá mua, giá hiện tại

4️⃣ Cập nhật định kỳ

━━━━━━━━━━━━━━━━━━━━━

**✅ KẾT QUẢ:**
• Tính được **Net Worth**
• Biết mình "giàu" thật sự chưa
• Theo dõi tăng trưởng tài sản

━━━━━━━━━━━━━━━━━━━━━

**💡 Công thức vàng:**
```
Net Worth = Tài sản - Nợ
```

*Thu nhập cao ≠ Giàu*
*Giàu = Net Worth cao!*
""",
        "image": "media/images/tai_san.jpg"
    },
    
    9: {
        "title": "🎯 KẾT LUẬN – TỔNG QUAN",
        "content": """
**🏆 NGUYÊN TẮC VÀNG KHI DÙNG FREEDOM WALLET:**

━━━━━━━━━━━━━━━━━━━━━

1️⃣ **Ghi chép HÀNG NGÀY**
   → Mỗi giao dịch phải được ghi lại

2️⃣ **Xem báo cáo HÀNG TUẦN**
   → Kiểm tra chi tiêu, điều chỉnh kịp thời

3️⃣ **Đánh giá tài chính MỖI THÁNG**
   → Xem tổng quan, so sánh với tháng trước

4️⃣ **Điều chỉnh mục tiêu MỖI QUÝ**
   → Thay đổi % 6 hũ nếu cần

5️⃣ **Kiên trì ÍT NHẤT 90 NGÀY**
   → Đủ để hình thành thói quen

━━━━━━━━━━━━━━━━━━━━━

**🌱 Câu nói cuối:**

*"Tự do tài chính không đến từ may mắn*
*– mà đến từ hệ thống."*

━━━━━━━━━━━━━━━━━━━━━

🎉 **Chúc bạn thành công trên hành trình tự do tài chính!**
""",
        "image": "media/images/tong_quan.jpg"
    }
}


def get_usage_guide_keyboard(current_step: int) -> InlineKeyboardMarkup:
    """Generate navigation keyboard for usage guide"""
    buttons = []
    
    # Navigation row
    nav_row = []
    if current_step > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Quay lại", callback_data=f"usage_{current_step-1}"))
    
    if current_step < 9:
        nav_row.append(InlineKeyboardButton("Tiếp theo ➡️", callback_data=f"usage_{current_step+1}"))
    
    if nav_row:
        buttons.append(nav_row)
    
    # Jump to specific sections (only show on step 0)
    if current_step == 0:
        buttons.append([
            InlineKeyboardButton("⚙️ Cài đặt (1-3)", callback_data="usage_1"),
            InlineKeyboardButton("💳 Tracking (4-8)", callback_data="usage_4")
        ])
    
    # Menu row
    menu_row = []
    if current_step != 0:
        menu_row.append(InlineKeyboardButton("📘 Menu", callback_data="usage_0"))
    
    if current_step == 9:
        menu_row.append(InlineKeyboardButton("✅ Hoàn thành", callback_data="usage_complete"))
    
    if menu_row:
        buttons.append(menu_row)
    
    # Help row (always available)
    buttons.append([
        InlineKeyboardButton("💬 Cần trợ giúp?", url="https://t.me/freedomwalletapp")
    ])
    
    return InlineKeyboardMarkup(buttons)


async def send_guide_step(update: Update, context: ContextTypes.DEFAULT_TYPE, step: int):
    """Send a specific guide step"""
    try:
        if step not in SETUP_GUIDE_STEPS:
            await update.callback_query.answer("❌ Bước không hợp lệ!")
            return
        
        guide_data = SETUP_GUIDE_STEPS[step]
        keyboard = get_usage_guide_keyboard(step)
        
        message_text = f"{guide_data['title']}\n\n{guide_data['content']}"
        
        # Handle image + text combination
        if guide_data.get('image'):
            # If there's an image, we need to delete old message and send new photo message
            if update.callback_query:
                # Delete the old message
                await update.callback_query.message.delete()
                
                # Send new photo message
                with open(guide_data['image'], 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=photo,
                        caption=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                await update.callback_query.answer()
            else:
                # Command: send photo directly
                with open(guide_data['image'], 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
        else:
            # No image, just text
            if update.callback_query:
                # Check if previous message was a photo
                if update.callback_query.message.photo:
                    # Previous was photo, need to delete and send new text message
                    await update.callback_query.message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                    await update.callback_query.answer()
                else:
                    # Previous was text, can edit
                    await update.callback_query.edit_message_text(
                        text=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                    await update.callback_query.answer()
            else:
                await update.message.reply_text(
                    text=message_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
        
        logger.info(f"Sent guide step {step} to user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending guide step {step}: {e}")
        if update.callback_query:
            await update.callback_query.answer("❌ Có lỗi xảy ra!")


async def huongdan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /huongdan command"""
    await send_guide_step(update, context, step=0)


async def usage_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle usage guide navigation callbacks"""
    query = update.callback_query
    callback_data = query.data
    
    try:
        if callback_data.startswith("usage_"):
            # Handle both usage_0-9 and usage_complete
            if callback_data == "usage_complete":
                pass  # Will be handled below
            else:
                step = int(callback_data.split("_")[-1])
                await send_guide_step(update, context, step)
                return
        
        if callback_data == "usage_complete":
            # Delete photo message from step 9 before sending text
            await query.message.delete()
            
            # Send completion message with next steps
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🎉 **CHÚC MỪNG! BẠN ĐÃ HOÀN THÀNH HƯỚNG DẪN!**\n\n"
                     "━━━━━━━━━━━━━━━━━━━━━\n\n"
                     "✅ **Bạn đã học được:**\n"
                     "• Cách cài đặt và xóa dữ liệu mẫu\n"
                     "• Thiết lập 6 Hũ Tiền và 5 Cấp bậc\n"
                     "• Quản lý Tài khoản, Danh mục, Nợ, Đầu tư, Tài sản\n\n"
                     "━━━━━━━━━━━━━━━━━━━━━\n\n"
                     "🚀 **BƯỚC TIẾP THEO - HÀNH ĐỘNG NGAY:**\n\n"
                     "**1️⃣ Ghi giao dịch đầu tiên** (Quan trọng nhất!)\n"
                     "   → Mở Web App của bạn (link ở Day 1)\n"
                     "   → Thử ghi 1 khoản chi tiêu hôm nay\n\n"
                     "**2️⃣ Thiết lập 6 Hũ Tiền của bạn**\n"
                     "   → Settings → 6 Jars → Điều chỉnh %\n\n"
                     "**3️⃣ Nhập số dư tài khoản chính xác**\n"
                     "   → Accounts → Thêm tất cả tài khoản\n\n"
                     "━━━━━━━━━━━━━━━━━━━━━\n\n"
                     "💎 **CAM KẾT 7 NGÀY ĐẦU TIÊN:**\n"
                     "Mỗi ngày bạn sẽ nhận được:\n"
                     "• 1 bài học thực tế về quản lý tài chính\n"
                     "• 1 nhiệm vụ nhỏ để thực hành\n"
                     "• Động lực và nhắc nhở từ bot\n\n"
                     "🎯 **Mục tiêu:** Ghi chép đủ 7 ngày → Hình thành thói quen!\n\n"
                     "🔥 **Tham gia Group để:**\n"
                     "• Được hỗ trợ trực tiếp khi gặp khó khăn\n"
                     "• Học hỏi kinh nghiệm từ cộng đồng\n"
                     "• Nhận tips & tricks độc quyền\n"
                     "• Tham gia thử thách 30 ngày ghi chép\n\n"
                     "💪 **Bắt đầu ngay hôm nay - Tương lai sẽ cảm ơn bạn!**",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👥 Tham gia Group VIP", url="https://t.me/freedomwalletapp")],
                    [InlineKeyboardButton("📖 Xem lại hướng dẫn", callback_data="usage_0")],
                    [InlineKeyboardButton("💬 Chat với Admin", url="https://t.me/freedomwalletapp")]
                ])
            )
            await query.answer("🎉 Hoàn thành! Bắt đầu ghi chép ngay nhé!")
        
    except Exception as e:
        logger.error(f"Error in guide callback handler: {e}")
        await query.answer("❌ Có lỗi xảy ra!")


def register_usage_guide_handlers(application):
    """Register all usage guide handlers"""
    application.add_handler(CommandHandler("huongdan", huongdan_command))
    application.add_handler(CallbackQueryHandler(usage_callback_handler, pattern="^usage_"))
    
    logger.info("✅ Usage guide handlers registered")

