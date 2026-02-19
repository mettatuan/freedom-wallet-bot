"""
🎯 DONATION HANDLER - FreedomWallet Trust Economy Model

Xử lý toàn bộ logic donation flow:
- Milestone detection
- Donation prompts
- Payment processing
- Contributor recognition
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import hashlib
import hmac
import json

logger = logging.getLogger(__name__)


# ============================================
# CONFIGURATION
# ============================================

DONATION_CONFIG = {
    "cooldown_days": 14,  # Minimum days between donation prompts
    "max_asks_per_month": 2,
    "suggested_amounts": {
        "coffee": {"amount": 20000, "label": "☕ 20k - Một ly cà phê", "emoji": "☕"},
        "meal": {"amount": 50000, "label": "🍜 50k - Một bữa phở", "emoji": "🍜"},
        "book": {"amount": 100000, "label": "📚 100k - Một quyển sách", "emoji": "📚"},
        "supporter": {"amount": 500000, "label": "💎 500k - Core Supporter", "emoji": "💎"},
    },
    "payment_methods": {
        "momo": {
            "name": "Momo",
            "enabled": True,
            "partner_code": "MOMO_PARTNER_CODE",  # From environment
            "access_key": "MOMO_ACCESS_KEY",
            "secret_key": "MOMO_SECRET_KEY",
        },
        "bank": {
            "name": "Chuyển khoản ngân hàng",
            "enabled": True,
            "account_number": "19036653824018",
            "bank_name": "Techcombank",
            "account_name": "FREEDOM WALLET",
        }
    }
}


# ============================================
# MILESTONE DETECTION
# ============================================

class MilestoneDetector:
    """Detect when user reaches milestones"""
    
    MILESTONES = {
        "3_days_streak": {
            "type": "streak",
            "threshold": 3,
            "title": "3 ngày liên tiếp! 🔥",
            "message": "Bạn đã dùng bot 3 ngày liên tục! Thói quen tốt đang hình thành.",
            "show_donate": False,
            "badge": "early_bird"
        },
        "first_week": {
            "type": "days_active",
            "threshold": 7,
            "title": "Tuần đầu hoàn thành! 🎉",
            "message": "7 ngày đầu tiên thành công! Bot đã giúp bạn xây dựng thói quen tài chính tốt.",
            "show_donate": True,
            "badge": "week_warrior"
        },
        "30_days": {
            "type": "days_active",
            "threshold": 30,
            "title": "1 tháng kiên trì! 💪",
            "message": "30 ngày ghi chép chi tiêu đều đặn! Thói quen đã hình thành vững chắc.",
            "show_donate": True,
            "badge": "monthly_master"
        },
        "100_transactions": {
            "type": "transactions",
            "threshold": 100,
            "title": "100 giao dịch! 📊",
            "message": "Bạn đã ghi chép 100 giao dịch! Kỷ luật tài chính đáng nể.",
            "show_donate": True,
            "badge": "transaction_pro"
        },
        "saved_1million": {
            "type": "money_saved",
            "threshold": 1000000,
            "title": "Tiết kiệm 1 triệu! 💰",
            "message": "Bạn đã tiết kiệm được 1 triệu VNĐ! Bước đầu tiên vững chắc đến tự do tài chính.",
            "show_donate": True,
            "badge": "saver_bronze"
        },
        "saved_5million": {
            "type": "money_saved",
            "threshold": 5000000,
            "title": "Tiết kiệm 5 triệu! 💎",
            "message": "5 triệu VNĐ tiết kiệm được! Tài chính của bạn ngày càng vững vàng.",
            "show_donate": True,
            "badge": "saver_gold"
        },
        "1_year": {
            "type": "days_active",
            "threshold": 365,
            "title": "1 năm đồng hành! 👑",
            "message": "365 ngày cùng FreedomWallet! Bạn là huyền thoại của cộng đồng.",
            "show_donate": True,
            "badge": "legend"
        }
    }
    
    def __init__(self, db):
        self.db = db
    
    def check_milestones(self, user_id: int) -> List[Dict]:
        """Check all milestones for user, return newly reached ones"""
        stats = self.db.get_user_stats(user_id)
        reached_milestones = stats.get('milestones_reached', [])
        new_milestones = []
        
        for key, config in self.MILESTONES.items():
            # Skip if already reached
            if key in reached_milestones:
                continue
            
            # Check threshold
            if self._check_threshold(stats, config):
                new_milestones.append({
                    'key': key,
                    'config': config
                })
                # Update DB
                self.db.add_milestone(user_id, key)
        
        return new_milestones
    
    def _check_threshold(self, stats: Dict, config: Dict) -> bool:
        """Check if threshold is met"""
        milestone_type = config['type']
        threshold = config['threshold']
        
        if milestone_type == 'streak':
            return stats.get('current_streak', 0) >= threshold
        elif milestone_type == 'days_active':
            return stats.get('days_active', 0) >= threshold
        elif milestone_type == 'transactions':
            return stats.get('transactions_logged', 0) >= threshold
        elif milestone_type == 'money_saved':
            return stats.get('money_saved', 0) >= threshold
        
        return False


# ============================================
# DONATION TIMING LOGIC
# ============================================

class DonationTiming:
    """Determine when to show donation prompt"""
    
    def __init__(self, db):
        self.db = db
    
    def should_show_donation_prompt(self, user_id: int, context: str = "milestone") -> bool:
        """
        Determine if we should show donation prompt
        
        Args:
            user_id: Telegram user ID
            context: Why we're considering showing prompt (milestone, monthly, manual)
        
        Returns:
            bool: True if should show
        """
        # Check opt-out
        reminder_status = self.db.get_donation_reminder_status(user_id)
        if reminder_status and reminder_status.get('opted_out'):
            return False
        
        # Check cooldown
        last_reminded = reminder_status.get('last_reminded_at') if reminder_status else None
        if last_reminded:
            days_since = (datetime.now() - last_reminded).days
            if days_since < DONATION_CONFIG['cooldown_days']:
                logger.info(f"User {user_id}: Cooldown active ({days_since} days)")
                return False
        
        # Check monthly limit
        this_month_count = self.db.count_donation_reminders_this_month(user_id)
        if this_month_count >= DONATION_CONFIG['max_asks_per_month']:
            logger.info(f"User {user_id}: Monthly limit reached ({this_month_count})")
            return False
        
        # Check if recently donated (don't ask again for 30 days)
        last_donation = self.db.get_last_donation(user_id)
        if last_donation:
            days_since_donation = (datetime.now() - last_donation['created_at']).days
            if days_since_donation < 30:
                logger.info(f"User {user_id}: Recently donated ({days_since_donation} days ago)")
                return False
        
        # Check engagement score (only ask engaged users)
        stats = self.db.get_user_stats(user_id)
        engagement = stats.get('engagement_score', 0)
        if engagement < 60:
            logger.info(f"User {user_id}: Low engagement ({engagement})")
            return False
        
        # All checks passed
        return True


# ============================================
# DONATION PROMPT HANDLER
# ============================================

class DonationPrompt:
    """Generate and send donation prompts"""
    
    def __init__(self, db):
        self.db = db
    
    async def send_milestone_donation_prompt(
        self, 
        update: Update, 
        context: ContextTypes.DEFAULT_TYPE,
        milestone: Dict
    ):
        """Send donation prompt after milestone"""
        user_id = update.effective_user.id
        
        # Get community stats for social proof
        community_stats = self.db.get_community_stats()
        
        message = f"""
🎉 {milestone['config']['title']}

{milestone['config']['message']}

---

💚 **FreedomWallet duy trì 100% nhờ cộng đồng**

👥 {community_stats['total_contributors']:,} người đã ủng hộ
💰 Chi phí tháng: {community_stats['monthly_costs']:,} VNĐ
⏰ Đủ duy trì: {community_stats['runway_months']:.0f} tháng

Bot này luôn miễn phí. Nếu thấy có giá trị, bạn có thể đóng góp để giúp người khác cũng tự do tài chính 💚
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💚 Ủng hộ ngay", callback_data=f"donate_start:{milestone['key']}")
            ],
            [
                InlineKeyboardButton("🙏 Để sau", callback_data="donate_later"),
                InlineKeyboardButton("❌ Đóng", callback_data="donate_close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Track that we showed prompt
        self.db.log_donation_reminder(user_id, f"milestone_{milestone['key']}")
    
    async def send_donation_options(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        trigger_context: str = "milestone"
    ):
        """Show donation amount selection"""
        query = update.callback_query
        await query.answer()
        
        message = """
💚 **Ủng hộ FreedomWallet**

Bot này 100% miễn phí và sẽ luôn như vậy. Cộng đồng duy trì nhờ sự đóng góp tự nguyện.

Chọn mức ủng hộ (hoặc tự nhập số khác):
        """
        
        # Build keyboard with suggested amounts
        keyboard = []
        row = []
        for i, (key, config) in enumerate(DONATION_CONFIG['suggested_amounts'].items(), 1):
            if key == "custom":
                continue
            
            button = InlineKeyboardButton(
                config['label'],
                callback_data=f"donate_amount:{config['amount']}:{trigger_context}"
            )
            row.append(button)
            
            # 2 buttons per row
            if i % 2 == 0:
                keyboard.append(row)
                row = []
        
        if row:  # Add remaining buttons
            keyboard.append(row)
        
        # Add custom amount option
        keyboard.append([
            InlineKeyboardButton(
                "✍️ Nhập số khác...",
                callback_data=f"donate_custom:{trigger_context}"
            )
        ])
        
        # Back button
        keyboard.append([
            InlineKeyboardButton("« Quay lại", callback_data="donate_close")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


# ============================================
# PAYMENT HANDLER
# ============================================

class PaymentHandler:
    """Handle payment processing"""
    
    def __init__(self, db):
        self.db = db
    
    async def initiate_payment(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        amount: int,
        trigger_context: str
    ):
        """Show payment method selection"""
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        
        # Create pending donation
        donation_code = self._generate_donation_code(user_id)
        self.db.create_pending_donation(
            user_id=user_id,
            amount=amount,
            donation_code=donation_code,
            trigger_event=trigger_context
        )
        
        message = f"""
💰 **Số tiền ủng hộ: {amount:,} VNĐ**

Chọn phương thức thanh toán:
        """
        
        keyboard = []
        
        # Momo option
        if DONATION_CONFIG['payment_methods']['momo']['enabled']:
            keyboard.append([
                InlineKeyboardButton(
                    "📱 Momo",
                    callback_data=f"pay_momo:{donation_code}:{amount}"
                )
            ])
        
        # Bank transfer option
        if DONATION_CONFIG['payment_methods']['bank']['enabled']:
            keyboard.append([
                InlineKeyboardButton(
                    "🏦 Chuyển khoản",
                    callback_data=f"pay_bank:{donation_code}:{amount}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton("« Quay lại", callback_data="donate_start")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def process_momo_payment(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        donation_code: str,
        amount: int
    ):
        """Process Momo payment"""
        query = update.callback_query
        await query.answer()
        
        # Generate Momo payment link
        payment_url = self._create_momo_payment(
            donation_code=donation_code,
            amount=amount,
            order_info=f"Ung ho FreedomWallet - {donation_code}"
        )
        
        message = f"""
📱 **Thanh toán qua Momo**

Số tiền: {amount:,} VNĐ
Mã giao dịch: `{donation_code}`

Nhấn nút bên dưới để mở Momo và thanh toán:
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 Mở Momo", url=payment_url)],
            [InlineKeyboardButton("✅ Đã thanh toán", callback_data=f"verify_payment:{donation_code}")],
            [InlineKeyboardButton("« Quay lại", callback_data="donate_start")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def process_bank_transfer(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        donation_code: str,
        amount: int
    ):
        """Process bank transfer"""
        query = update.callback_query
        await query.answer()
        
        bank_info = DONATION_CONFIG['payment_methods']['bank']
        
        message = f"""
🏦 **Chuyển khoản ngân hàng**

📋 **Thông tin chuyển khoản:**
Ngân hàng: `{bank_info['bank_name']}`
Số tài khoản: `{bank_info['account_number']}`
Tên tài khoản: `{bank_info['account_name']}`
Số tiền: `{amount:,} VNĐ`
Nội dung CK: `{donation_code}`

⚠️ **QUAN TRỌNG**: Ghi đúng nội dung `{donation_code}` để tự động xác nhận.

Sau khi chuyển khoản, nhấn "Đã chuyển khoản" hoặc gửi ảnh chụp màn hình để xác nhận.
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Đã chuyển khoản", callback_data=f"verify_payment:{donation_code}")],
            [InlineKeyboardButton("« Quay lại", callback_data="donate_start")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def _generate_donation_code(self, user_id: int) -> str:
        """Generate unique donation code"""
        timestamp = int(datetime.now().timestamp())
        return f"FW{user_id}{timestamp % 100000}"
    
    def _create_momo_payment(self, donation_code: str, amount: int, order_info: str) -> str:
        """Create Momo payment request"""
        # Simplified - in production use proper Momo API
        config = DONATION_CONFIG['payment_methods']['momo']
        
        # Generate signature
        raw_data = f"partnerCode={config['partner_code']}&amount={amount}&orderId={donation_code}"
        signature = hmac.new(
            config['secret_key'].encode(),
            raw_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Return deep link (simplified)
        payment_url = f"https://nhantien.momo.vn/{config['partner_code']}?amount={amount}&note={donation_code}"
        
        return payment_url


# ============================================
# CONTRIBUTOR RECOGNITION
# ============================================

class ContributorRecognition:
    """Handle post-donation recognition and rewards"""
    
    def __init__(self, db):
        self.db = db
    
    async def send_thank_you(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        donation_id: int
    ):
        """Send thank you message after confirmed donation"""
        donation = self.db.get_donation(donation_id)
        user_id = donation['user_id']
        amount = donation['amount']
        
        # Update user status
        self.db.set_user_contributor(user_id, True)
        
        # Get contributor stats
        stats = self.db.get_donation_stats(user_id)
        contributor_number = self.db.get_contributor_count()
        
        # Get community impact
        community_stats = self.db.get_community_stats()
        
        message = f"""
🙏💚 **CẢM ƠN BẠN RẤT NHIỀU!**

Bạn vừa đóng góp **{amount:,} VNĐ** để xây dựng cộng đồng FreedomWallet.

📊 **Tác động của bạn:**
• Với {amount:,} VNĐ, bot có thể phục vụ ~{self._calculate_users_served(amount)} users trong 1 tháng
• Tổng cộng đồng đã đóng góp: {community_stats['total_donations']:,} VNĐ

🌟 **Chào mừng bạn trở thành Contributor!**
• Bạn là Contributor #{contributor_number:,}
• Tổng đóng góp của bạn: {stats['total_donated']:,} VNĐ
• Số lần ủng hộ: {stats['donation_count']}

Bạn có muốn hiển thị tên trên Wall of Fame không?
        """
        
        keyboard = [
            [InlineKeyboardButton(f"✅ Hiển thị: {update.effective_user.first_name}", callback_data=f"fame_show:{donation_id}")],
            [InlineKeyboardButton("🎭 Hiển thị ẩn danh", callback_data=f"fame_anonymous:{donation_id}")],
            [InlineKeyboardButton("❌ Không hiển thị", callback_data=f"fame_hide:{donation_id}")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Award badge
        self._award_contributor_badge(user_id, stats)
    
    async def invite_to_contributors_group(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int
    ):
        """Invite to contributors Telegram group"""
        message = """
💬 **Tham gia Contributors Group?**

Đây là nơi các Contributors:
• Chia sẻ kinh nghiệm tài chính
• Thảo luận về phát triển bot
• Kết nối với cộng đồng
• Được cập nhật sớm nhất

**Lưu ý:** Đây không phải tính năng đặc biệt của bot, chỉ là nhóm chat cộng đồng 💚
        """
        
        keyboard = [
            [InlineKeyboardButton("💬 Tham gia ngay", url="https://t.me/FreedomWalletContributors")],
            [InlineKeyboardButton("Để sau", callback_data="close")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def _calculate_users_served(self, amount: int) -> int:
        """Calculate how many users can be served with donation"""
        # Assuming 3,200,000 VND per month for 12,000 users
        cost_per_user_per_month = 3200000 / 12000  # ~267 VND
        return int(amount / cost_per_user_per_month)
    
    def _award_contributor_badge(self, user_id: int, stats: Dict):
        """Award appropriate badge based on contribution"""
        total = stats['total_donated']
        count = stats['donation_count']
        
        if total >= 2000000 or count >= 10:
            badge = "champion"
            tier = "Community Champion"
        elif total >= 500000 or count >= 3:
            badge = "supporter"
            tier = "Core Supporter"
        else:
            badge = "contributor"
            tier = "Contributor"
        
        self.db.update_contributor_tier(user_id, tier)
        self.db.add_badge(user_id, badge)


# ============================================
# MAIN DONATION HANDLER
# ============================================

class DonationHandler:
    """Main orchestrator for donation flow"""
    
    def __init__(self, db):
        self.db = db
        self.milestone_detector = MilestoneDetector(db)
        self.timing = DonationTiming(db)
        self.prompt = DonationPrompt(db)
        self.payment = PaymentHandler(db)
        self.recognition = ContributorRecognition(db)
    
    async def check_and_celebrate_milestones(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Check for new milestones and celebrate"""
        user_id = update.effective_user.id
        
        # Detect new milestones
        new_milestones = self.milestone_detector.check_milestones(user_id)
        
        for milestone in new_milestones:
            # Send celebration message
            await self._send_celebration(update, context, milestone)
            
            # Maybe show donation prompt
            if milestone['config']['show_donate']:
                if self.timing.should_show_donation_prompt(user_id, f"milestone_{milestone['key']}"):
                    await self.prompt.send_milestone_donation_prompt(
                        update, context, milestone
                    )
    
    async def _send_celebration(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        milestone: Dict
    ):
        """Send milestone celebration message"""
        message = f"""
{milestone['config']['title']}

{milestone['config']['message']}

Bạn vừa mở khóa badge: **{milestone['config']['badge']}** 🏆
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def handle_donation_callback(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle all donation-related callbacks"""
        query = update.callback_query
        data = query.data
        
        if data.startswith("donate_start"):
            await self.prompt.send_donation_options(update, context)
        
        elif data.startswith("donate_amount"):
            _, amount, trigger = data.split(":")
            await self.payment.initiate_payment(
                update, context, int(amount), trigger
            )
        
        elif data.startswith("pay_momo"):
            _, donation_code, amount = data.split(":")
            await self.payment.process_momo_payment(
                update, context, donation_code, int(amount)
            )
        
        elif data.startswith("pay_bank"):
            _, donation_code, amount = data.split(":")
            await self.payment.process_bank_transfer(
                update, context, donation_code, int(amount)
            )
        
        elif data.startswith("verify_payment"):
            _, donation_code = data.split(":")
            await self._handle_payment_verification(update, context, donation_code)
        
        elif data == "donate_later":
            await query.answer("Cảm ơn bạn! Donate bất cứ lúc nào với /donate")
            await query.delete_message()
        
        elif data == "donate_close":
            await query.delete_message()
    
    async def _handle_payment_verification(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        donation_code: str
    ):
        """Handle payment verification"""
        query = update.callback_query
        
        # Check if already verified (via webhook)
        donation = self.db.get_donation_by_code(donation_code)
        
        if donation and donation['status'] == 'confirmed':
            # Already confirmed
            await self.recognition.send_thank_you(update, context, donation['id'])
            await self.recognition.invite_to_contributors_group(
                update, context, donation['user_id']
            )
        else:
            # Pending manual verification
            await query.answer(
                "Đang xác nhận giao dịch... Vui lòng đợi vài phút.",
                show_alert=True
            )
            
            # Notify admin for manual verification
            self._notify_admin_for_verification(donation_code)


# ============================================
# USAGE EXAMPLE
# ============================================

"""
# In your bot.py:

from donation_handler import DonationHandler

# Initialize
donation_handler = DonationHandler(db)

# After user logs a transaction
async def log_transaction_handler(update, context):
    # ... log transaction logic ...
    
    # Check for milestones
    await donation_handler.check_and_celebrate_milestones(update, context)

# Register callback handlers
application.add_handler(CallbackQueryHandler(
    donation_handler.handle_donation_callback,
    pattern="^donate_|^pay_|^verify_|^fame_"
))

# Manual donate command
async def donate_command(update, context):
    await donation_handler.prompt.send_donation_options(
        update, context, trigger_context="manual"
    )

application.add_handler(CommandHandler("donate", donate_command))
"""
