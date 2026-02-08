"""
Onboarding Journey Handler - 7-Day Welcome Journey
Guides new users through Freedom Wallet features

Week 3: Integrated with ProgramManager
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime, timedelta

# Week 3: Import ProgramManager
from bot.core.program_manager import ProgramManager, ProgramType


# 7-Day Onboarding Content with Inline Keyboards
ONBOARDING_MESSAGES = {
    1: {
        "title": "� CHÚC MỪNG! BẠN ĐÃ MỞ KHÓA VIP",
        "content": """
👏 **Tuyệt vời! Bạn đã giới thiệu thành công 2 người!**

Giờ đây, bạn được truy cập **Freedom Wallet VIP** – công cụ quản lý tài chính cá nhân mạnh mẽ!

━━━━━━━━━━━━━━━━━━━━━

🎯 **HAI BƯỚC TIẾP THEO:**

**BƯỚC 1: TẠO WEB APP** (10-15 phút)
   • Copy Google Sheets Template
   • Deploy Web App cá nhân
   • 100% dữ liệu riêng tư

**BƯỚC 2: HỌC CÁCH DÙNG** (15-20 phút)
   • Quản lý tài khoản & giao dịch
   • Áp dụng 6 Hũ Tiền
   • Đạt tự do tài chính

━━━━━━━━━━━━━━━━━━━━━

💡 **Đừng lo!** Mình sẽ hướng dẫn từng bước.

👉 **Nhấn nút bên dưới để bắt đầu Bước 1!**
""",
        "delay_hours": 0,
        "buttons": [
            [{"text": "🚀 Bắt đầu thiết lập Freedom Wallet", "callback_data": "webapp_step_0"}]
        ]
    },
    
    2: {
        "title": "💰 Day 2: Hiểu về 6 Hũ Tiền",
        "content": """
💰 **6 HŨ TIỀN - CON ĐƯỜNG TỰ DO TÀI CHÍNH**

Đây là phương pháp được triệu người áp dụng thành công!

━━━━━━━━━━━━━━━━━━━━━

**🏠 HŨ 1: CHI TIÊU THIẾT YẾU (55%)**
• Ăn uống, nhà ở, điện nước
• Chi phí sống hàng ngày
• Target: Giữ dưới 55% thu nhập

**🎉 HŨ 2: HƯỞNG THỤ (10%)**
• Cafe, shopping, giải trí
• Reward bản thân
• Dùng hết mỗi tháng - sống cân bằng!

**💎 HŨ 3: ĐẦU TƯ DÀI HẠN (10%)**
• Cổ phiếu, quỹ đầu tư
• Bất động sản
• Tạo thu nhập thụ động

**📚 HŨ 4: HỌC TẬP & PHÁT TRIỂN (10%)**
• Sách, khóa học
• Hội thảo, workshop
• Đầu tư vào bản thân

**🎁 HŨ 5: TỪ THIỆN & CHO ĐI (5%)**
• Giúp đỡ người khác
• Đóng góp cộng đồng
• Tích lũy phước báo

**🆘 HŨ 6: DỰ PHÒNG (10%)**
• Quỹ khẩn cấp 3-6 tháng
• Bảo hiểm
• An toàn tài chính

━━━━━━━━━━━━━━━━━━━━━

📊 **VÍ DỤ THỰC TẾ:**

Thu nhập: 20,000,000 VNĐ/tháng
• Hũ 1: 11M (chi tiêu)
• Hũ 2: 2M (hưởng thụ)
• Hũ 3: 2M (đầu tư)
• Hũ 4: 2M (học tập)
• Hũ 5: 1M (từ thiện)
• Hũ 6: 2M (dự phòng)

💡 **MẸO:** Bạn có thể điều chỉnh % phù hợp
với hoàn cảnh riêng của mình!

📱 **THỰC HÀNH:**
Vào Freedom Wallet → "6 Jars" → Xem phân bổ của bạn

❓ Có thắc mắc về hũ nào không? Hỏi mình nhé!
""",
        "delay_hours": 24,
        "buttons": [
            [{"text": "📊 Xem 6 Hũ trong App", "callback_data": "onboard_open_app"}],
            [{"text": "💡 Ví dụ phân bổ", "callback_data": "onboard_example_day2"}],
            [{"text": "✅ Đã hiểu rồi", "callback_data": "onboard_complete_2"}],
            [{"text": "❓ Cần hỗ trợ", "callback_data": "onboard_help_2"}]
        ]
    },
    
    3: {
        "title": "🎯 Day 3: 5 Cấp Bậc Tài Chính",
        "content": """
🎯 **5 CẤP BẬC TÀI CHÍNH - BẠN ĐANG Ở ĐÂU?**

━━━━━━━━━━━━━━━━━━━━━

**🔴 CẤP 1: TÀI CHÍNH BẤT ỔN**
📍 Thu nhập < Chi tiêu
💔 Nợ nần, stress liên tục
🎯 Mục tiêu: Cắt giảm chi, tăng thu

**🟠 CẤP 2: TÀI CHÍNH ỔN ĐỊNH**
📍 Thu nhập = Chi tiêu
💰 Sống vừa đủ, không dư
🎯 Mục tiêu: Tạo thặng dư 10-20%

**🟡 CẤP 3: TÀI CHÍNH TÍCH LŨY**
📍 Thu nhập > Chi tiêu
💵 Bắt đầu tiết kiệm & đầu tư
🎯 Mục tiêu: Đầu tư 10-20% thu nhập

**🟢 CẤP 4: TÀI CHÍNH AN TOÀN**
📍 Có quỹ khẩn cấp 6+ tháng
💎 Thu nhập thụ động đáng kể
🎯 Mục tiêu: Tăng thu nhập thụ động

**🔵 CẤP 5: TỰ DO TÀI CHÍNH**
📍 Thu nhập thụ động > Chi tiêu
🏆 Không cần làm vẫn có tiền
🎯 Mục tiêu: Maintain & enjoy life!

━━━━━━━━━━━━━━━━━━━━━

🎮 **QUIZ: BẠN ĐANG Ở CẤP NÀO?**

1️⃣ Reply "1" nếu bạn ở Cấp 1
2️⃣ Reply "2" nếu bạn ở Cấp 2
3️⃣ Reply "3" nếu bạn ở Cấp 3
4️⃣ Reply "4" nếu bạn ở Cấp 4
5️⃣ Reply "5" nếu bạn ở Cấp 5

Mình sẽ cho tips để lên cấp tiếp theo!

📊 **Xem chi tiết trong app:**
Freedom Wallet → "Financial Level"
""",
        "delay_hours": 48,
        "buttons": [
            [{"text": "🎯 Quiz: Tôi ở cấp mấy?", "callback_data": "onboard_quiz_level"}],
            [{"text": "💡 Tips lên cấp", "callback_data": "onboard_level_tips"}],
            [{"text": "✅ Đã xác định cấp", "callback_data": "onboard_complete_3"}],
            [{"text": "❓ Cần hỗ trợ", "callback_data": "onboard_help_3"}]
        ]
    },
    
    4: {
        "title": "⚡ Day 4: Thêm Giao Dịch Đầu Tiên",
        "content": """
⚡ **THÊM GIAO DỊCH - THEO DÕI CHI TIÊU**

Đã setup xong? Giờ là lúc bắt đầu tracking!

━━━━━━━━━━━━━━━━━━━━━

📝 **CÁCH THÊM GIAO DỊCH:**

**Bước 1:** Mở Freedom Wallet
**Bước 2:** Click "Thêm giao dịch"
**Bước 3:** Điền thông tin:
   • Loại: Thu/Chi
   • Số tiền
   • Danh mục (Ăn uống, Di chuyển...)
   • Hũ tiền (nếu là chi tiêu)
   • Ghi chú (optional)

**Bước 4:** Lưu lại → Done!

━━━━━━━━━━━━━━━━━━━━━

💡 **TIPS PHÂN LOẠI:**

**Chi tiêu Hũ 1 (Thiết yếu):**
• Tiền nhà, điện nước
• Đi lại, xăng xe
• Marketing, chi phí kinh doanh

**Chi tiêu Hũ 2 (Hưởng thụ):**
• Cafe, trà sữa
• Ăn nhà hàng
• Shopping, giải trí

**Thu nhập:**
• Lương, thưởng
• Doanh thu kinh doanh
• Lãi đầu tư, lãi ngân hàng

━━━━━━━━━━━━━━━━━━━━━

🎯 **THÁCH THỨC:**

Hôm nay, thêm ít nhất **3 giao dịch** gần đây:
1️⃣ 1 giao dịch chi tiêu thiết yếu
2️⃣ 1 giao dịch hưởng thụ
3️⃣ 1 giao dịch thu nhập (nếu có)

✅ Xong rồi? Nhắn "DONE" nhé!

❓ **Gặp vấn đề?**
• Không biết chọn danh mục?
• App báo lỗi?
• Cách nào nhanh nhất?

Hỏi mình ngay!
""",
        "delay_hours": 72,
        "buttons": [
            [{"text": "📝 Mở App để thêm", "callback_data": "onboard_open_app"}],
            [{"text": "💡 Tips phân loại", "callback_data": "onboard_tips_day4"}],
            [{"text": "✅ Đã thêm xong", "callback_data": "onboard_complete_4"}],
            [{"text": "❓ Cần hỗ trợ", "callback_data": "onboard_help_4"}]
        ]
    },
    
    5: {
        "title": "📈 Day 5: Tính Năng Nâng Cao",
        "content": """
📈 **TÍNH NĂNG NÂNG CAO - MASTER FREEDOM WALLET**

Giờ bạn đã quen với basics, nâng cấp thôi!

━━━━━━━━━━━━━━━━━━━━━

**1️⃣ ĐẦU TƯ & ROI TRACKER**

📊 Theo dõi hiệu suất đầu tư:
• Cổ phiếu
• Crypto
• Bất động sản
• Vàng, ngoại tệ

💡 **Cách dùng:**
• Nhập giá mua ban đầu
• Cập nhật giá hiện tại
• Xem ROI% tự động

━━━━━━━━━━━━━━━━━━━━━

**2️⃣ TÀI SẢN & NỢ**

💎 Quản lý tổng tài sản:
• Tiền mặt, ngân hàng
• Bất động sản
• Xe cộ, trang sức
• Nợ vay, thẻ tín dụng

💡 **Lợi ích:**
Biết chính xác net worth của bạn!

━━━━━━━━━━━━━━━━━━━━━

**3️⃣ BÁO CÁO & THỐNG KÊ**

📊 Dashboard tự động:
• Chi tiêu theo tháng
• So sánh với tháng trước
• Top danh mục chi nhiều nhất
• Xu hướng tiết kiệm

💡 **Xem ngay:**
Freedom Wallet → "Reports"

━━━━━━━━━━━━━━━━━━━━━

**4️⃣ NGÂN SÁCH & MỤC TIÊU**

🎯 Đặt mục tiêu:
• Tiết kiệm 10M trong 6 tháng
• Giảm chi tiêu hưởng thụ 20%
• Đầu tư 5M/tháng

📈 Theo dõi tiến độ tự động!

━━━━━━━━━━━━━━━━━━━━━

💪 **THÁCH THỨC:**

Khám phá 1 tính năng mới hôm nay:
1. Thử ROI Tracker với 1 khoản đầu tư
2. Nhập tài sản & nợ của bạn
3. Xem Reports tháng này

❓ Cần hướng dẫn chi tiết? Hỏi mình!
""",
        "delay_hours": 96
    },
    
    6: {
        "title": "👥 Day 6: Tham Gia Cộng Đồng",
        "content": """
👥 **THAM GIA CỘNG ĐỒNG FREEDOM WALLET**

Học hỏi & chia sẻ với 1000+ thành viên!

━━━━━━━━━━━━━━━━━━━━━

💬 **FREEDOM WALLET GROUP**

👉 [Tham gia ngay](https://t.me/freedomwalletapp)

📚 **Bạn sẽ nhận được:**

✓ Hỗ trợ trực tiếp từ team & community
✓ Tips tài chính hàng ngày
✓ Case studies thực tế
✓ Updates tính năng mới
✓ Tài liệu & templates miễn phí
✓ Livestream Q&A định kỳ

━━━━━━━━━━━━━━━━━━━━━

🔥 **TOPICS THƯỜNG TRÀ:**

• Cách tối ưu 6 Hũ Tiền
• Chiến lược đầu tư cho người mới
• Tiết kiệm 50% lương mỗi tháng
• Passive income ideas
• Khắc phục lỗi app nhanh

━━━━━━━━━━━━━━━━━━━━━

📖 **CÁC NGUỒN HỌC THÊM:**

**1. Notion Guide:**
👉 [eliroxbot.notion.site/freedomwallet](https://eliroxbot.notion.site/freedomwallet)
• Hướng dẫn chi tiết mọi tính năng
• Video tutorials
• Troubleshooting guide

**2. Resources & Templates:**
• Excel budgeting templates
• Financial planning worksheets
• Reading list cho financial literacy

━━━━━━━━━━━━━━━━━━━━━

💡 **CHIA SẺ THÀNH CÔNG CỦA BẠN!**

Bạn đã track được gì sau 6 ngày?
• Tiết kiệm được bao nhiêu?
• Phát hiện ra điểm nào lãng phí?
• Mục tiêu tiếp theo là gì?

Chia sẻ trong Group để inspire người khác nhé!

━━━━━━━━━━━━━━━━━━━━━

❓ **FAQ NHANH:**

Q: Group có thu phí không?
A: 100% miễn phí mãi mãi!

Q: Tôi có thể hỏi bất cứ điều gì?
A: Có! Team & community sẽ giúp bạn.

Q: Có được support 1-1 không?
A: Có! Tag @admin trong group.

🚀 Tham gia ngay để không bỏ lỡ!
""",
        "delay_hours": 120
    },
    
    7: {
        "title": "🎊 Day 7: Ôn Tập & Kế Hoạch",
        "content": """
🎊 **CHÚC MỪNG! BẠN ĐÃ HOÀN THÀNH 7 NGÀY ONBOARDING!**

━━━━━━━━━━━━━━━━━━━━━

📚 **REVIEW: NHỮNG GÌ BẠN ĐÃ HỌC**

✅ **Day 1:** Setup Web App hoàn chỉnh
✅ **Day 2:** Hiểu rõ 6 Hũ Tiền
✅ **Day 3:** Xác định cấp độ tài chính hiện tại
✅ **Day 4:** Tracking giao dịch thành thạo
✅ **Day 5:** Sử dụng tính năng nâng cao
✅ **Day 6:** Tham gia cộng đồng

━━━━━━━━━━━━━━━━━━━━━

🎯 **KẾ HOẠCH 30 NGÀY TỚI**

**TUẦN 2: TẠO THÓI QUEN**
• Track mọi giao dịch hàng ngày (cả nhỏ nhất)
• Review chi tiêu mỗi tối 5 phút
• Mục tiêu: 21 ngày = 1 thói quen

**TUẦN 3: TỐI ƯU HÓA**
• Phân tích chi tiêu tháng trước
• Tìm 3 điểm có thể cắt giảm
• Tăng hũ đầu tư thêm 5%

**TUẦN 4: MỞ RỘNG**
• Thử 1 cách đầu tư mới
• Đặt mục tiêu tiết kiệm cụ thể
• Share kinh nghiệm trong Group

━━━━━━━━━━━━━━━━━━━━━

💪 **THÁCH THỨC 30 NGÀY:**

Mình thách bạn trong 30 ngày tới:
1️⃣ Track 100% giao dịch
2️⃣ Tiết kiệm thêm 10% thu nhập
3️⃣ Tìm 1 nguồn thu thụ động mới

Nhắn "ACCEPT" để nhận challenge!

━━━━━━━━━━━━━━━━━━━━━

📊 **ĐÁNH GIÁ:**

Giúp mình cải thiện bằng cách trả lời:

**Onboarding 7 ngày có hữu ích không?**
1️⃣ = Rất tệ
2️⃣ = Tệ
3️⃣ = Bình thường
4️⃣ = Tốt
5️⃣ = Xuất sắc!

Reply số từ 1-5 nhé!

━━━━━━━━━━━━━━━━━━━━━

🎁 **SPECIAL BONUS:**

**Referral Rewards mới:**
Giới thiệu thêm 3 người → Nhận:
• 1 giờ tư vấn tài chính 1-1
• Premium templates pack
• Early access tính năng mới

Share link của bạn: /referral

━━━━━━━━━━━━━━━━━━━━━

🚀 **HÀNH TRÌNH MỚI BẮT ĐẦU!**

Freedom Wallet không chỉ là app,
đó là hành trình thay đổi tài chính của bạn.

Mình sẽ luôn ở đây support bạn!

💬 Cần gì cứ hỏi - /help
🎯 Đặt mục tiêu - /goals
📊 Xem tiến độ - /stats
👥 Cộng đồng - /community

**Chúc bạn thành công trên con đường tự do tài chính! 🎉**

P/S: Nhớ track chi tiêu hôm nay nhé! 😉
""",
        "delay_hours": 144
    }
}


async def start_onboarding_journey(user_id: int, context: ContextTypes.DEFAULT_TYPE, initial_delay_minutes: int = 0):
    """
    Start 7-day onboarding journey for a user
    
    Args:
        user_id: Telegram user ID
        context: Telegram context
        initial_delay_minutes: Delay before sending Day 1 (0 = immediate)
    
    Week 3: Now uses ProgramManager for enrollment
    Old scheduling logic kept for backward compatibility
    """
    try:
        logger.info(f"Starting onboarding journey for user {user_id} (delay: {initial_delay_minutes}m)")
        
        # Week 3: Use ProgramManager
        with ProgramManager() as pm:
            success = await pm.enroll_user(
                user_id, 
                ProgramType.ONBOARDING_7_DAY, 
                context,
                force=True,  # Override nurture if exists (VIP takes priority)
                initial_delay_minutes=initial_delay_minutes
            )
            
            if success:
                logger.success(f"✅ User {user_id} enrolled in ONBOARDING_7_DAY via ProgramManager")
                return True
            else:
                logger.warning(f"⚠️ Failed to enroll user {user_id} in ONBOARDING_7_DAY")
                # Fallback to legacy method
                return await _start_onboarding_journey_legacy(user_id, context)
        
    except Exception as e:
        logger.error(f"Failed to start onboarding for user {user_id}: {e}")
        # Fallback to legacy method
        return await _start_onboarding_journey_legacy(user_id, context)


async def _start_onboarding_journey_legacy(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Legacy method: Schedule all 7 days at once
    Kept for backward compatibility
    """
    try:
        logger.info(f"Using legacy onboarding scheduling for user {user_id}")
        bot_context = context.bot_data
        
        for day, message_data in ONBOARDING_MESSAGES.items():
            # Calculate when to send
            send_time = datetime.now() + timedelta(hours=message_data['delay_hours'])
            
            # Schedule message with buttons
            context.job_queue.run_once(
                send_onboarding_message,
                when=send_time,
                data={
                    'user_id': user_id,
                    'day': day,
                    'title': message_data['title'],
                    'content': message_data['content'],
                    'buttons': message_data.get('buttons', [])  # Include buttons if available
                },
                name=f"onboarding_day_{day}_user_{user_id}"
            )
            
            logger.info(f"Scheduled onboarding Day {day} for user {user_id} at {send_time}")
        
        logger.success(f"Started 7-day onboarding (legacy) for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to start legacy onboarding for user {user_id}: {e}")
        return False


async def send_onboarding_message(context: ContextTypes.DEFAULT_TYPE, user_id: int = None, day: int = None):
    """
    Send onboarding message with inline keyboard
    
    Can be called in two ways:
    1. From ProgramManager: send_onboarding_message(context, user_id, day)
    2. From legacy scheduler: send_onboarding_message(context) with job.data
    """
    # If user_id and day not provided, get from job.data (legacy)
    if user_id is None or day is None:
        job = context.job
        data = job.data
        user_id = data['user_id']
        day = data['day']
        title = data['title']
        content = data['content']
        buttons = data.get('buttons', [])
    else:
        # Get from ONBOARDING_MESSAGES (modern ProgramManager way)
        if day not in ONBOARDING_MESSAGES:
            logger.error(f"Invalid onboarding day: {day}")
            return
        
        message_data = ONBOARDING_MESSAGES[day]
        title = message_data['title']
        content = message_data['content']
        buttons = message_data.get('buttons', [])
    
    try:
        # Build inline keyboard if buttons provided
        reply_markup = None
        if buttons:
            keyboard = []
            for row in buttons:
                button_row = []
                for btn in row:
                    if 'url' in btn:
                        button_row.append(InlineKeyboardButton(btn['text'], url=btn['url']))
                    else:
                        button_row.append(InlineKeyboardButton(btn['text'], callback_data=btn['callback_data']))
                keyboard.append(button_row)
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"{title}\n{content}",
            parse_mode="Markdown",
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        
        logger.info(f"Sent onboarding Day {day} to user {user_id} with {len(buttons)} button rows")
        
        # TODO: Update onboarding_progress in database
        
    except Exception as e:
        logger.error(f"Failed to send onboarding Day {day} to user {user_id}: {e}")


async def handle_onboarding_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle user responses to onboarding messages
    """
    text = update.message.text.strip().upper()
    user_id = update.effective_user.id
    
    # Check for completion markers
    if text == "DONE":
        await update.message.reply_text(
            "🎉 Tuyệt vời! Bạn đã hoàn thành nhiệm vụ!\n"
            "Tiếp tục theo dõi nhé, mình sẽ gửi bài tiếp theo sớm thôi!",
            parse_mode="Markdown"
        )
        return
    
    # Check for challenge acceptance
    if text == "ACCEPT":
        await update.message.reply_text(
            "💪 **CHALLENGE ACCEPTED!**\n\n"
            "Mình sẽ nhắc bạn mỗi tuần để check progress.\n"
            "Cùng nhau làm nên điều tuyệt vời! 🚀",
            parse_mode="Markdown"
        )
        # TODO: Schedule weekly check-ins
        return
    
    # Check for level quiz answer (1-5)
    if text in ["1", "2", "3", "4", "5"]:
        level = int(text)
        tips = {
            1: "💡 **Tips lên Cấp 2:**\n• Liệt kê tất cả chi tiêu\n• Tìm 3 khoản có thể cắt\n• Tăng thu nhập (side hustle)\n• Dùng app track mỗi ngày",
            2: "💡 **Tips lên Cấp 3:**\n• Tạo ngân sách chi tiết\n• Áp dụng 6 Hũ Tiền\n• Tiết kiệm ít nhất 10%\n• Tìm cách tăng thu",
            3: "💡 **Tips lên Cấp 4:**\n• Xây quỹ khẩn cấp 6 tháng\n• Đầu tư 10-20% thu nhập\n• Học về đầu tư an toàn\n• Tăng passive income",
            4: "💡 **Tips lên Cấp 5:**\n• Scale passive income\n• Đa dạng hóa đầu tư\n• Tối ưu thuế\n• Enjoy life but stay disciplined",
            5: "🏆 **CHÚC MỪNG!**\nBạn đã đạt tự do tài chính!\nGiờ là lúc giúp đỡ người khác và enjoy cuộc sống!"
        }
        
        await update.message.reply_text(
            f"✅ Bạn đang ở **Cấp {level}**!\n\n{tips[level]}",
            parse_mode="Markdown"
        )
        return
    
    # Check for rating (1-5)
    # Will handle in general message handler


async def stop_onboarding_journey(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """
    Stop onboarding journey for a user (if they request)
    """
    try:
        jobs = context.job_queue.get_jobs_by_name(f"onboarding_*_user_{user_id}")
        for job in jobs:
            job.schedule_removal()
        
        logger.info(f"Stopped onboarding for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to stop onboarding for user {user_id}: {e}")
        return False
