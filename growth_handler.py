"""
🌱 GROWTH LOOP HANDLER - Referral & Community Building

Xử lý:
- Referral tracking
- Shareable content generation
- Community growth metrics
- Ambassador program
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)


# ============================================
# REFERRAL SYSTEM
# ============================================

class ReferralSystem:
    """Manage referral tracking and rewards"""
    
    REFERRAL_BADGES = {
        "intro": {
            "threshold": 1,
            "emoji": "🌱",
            "title": "Introducer",
            "message": "Bạn đã giới thiệu người đầu tiên! 🌱"
        },
        "builder": {
            "threshold": 5,
            "emoji": "🌿",
            "title": "Community Builder",
            "message": "5 người tham gia nhờ bạn! Bạn đang xây dựng cộng đồng! 🌿"
        },
        "champion": {
            "threshold": 20,
            "emoji": "🌳",
            "title": "Growth Champion",
            "message": "20 người! Bạn là trụ cột của cộng đồng FreedomWallet! 🌳"
        },
        "legend": {
            "threshold": 50,
            "emoji": "🏆",
            "title": "Community Legend",
            "message": "50 người! Bạn là huyền thoại của cộng đồng! 🏆"
        }
    }
    
    def __init__(self, db):
        self.db = db
    
    def generate_referral_code(self, user_id: int) -> str:
        """Generate unique referral code"""
        return f"freedom_{user_id}"
    
    async def send_referral_link(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Send user's referral link"""
        user_id = update.effective_user.id
        code = self.generate_referral_code(user_id)
        link = f"https://t.me/FreedomWalletBot?start={code}"
        
        # Get referral stats
        stats = self.db.get_referral_stats(user_id)
        total = stats.get('total_referrals', 0)
        activated = stats.get('activated_referrals', 0)
        
        message = f"""
🌟 **Chia sẻ FreedomWallet**

FreedomWallet giúp:
✅ Ghi chép chi tiêu tự động
✅ Phân tích tài chính thông minh
✅ Xây dựng thói quen tiết kiệm
✅ 100% miễn phí, không giới hạn

**Link của bạn:**
`{link}`

---

📊 **Thành tích của bạn:**
👥 Đã giới thiệu: {total} người
✅ Đã kích hoạt: {activated} người

💡 Mỗi người bạn giúp đỡ = 1 bước đến tự do tài chính!

**Lưu ý:** Không có thưởng tiền, chỉ có ý nghĩa giúp người khác 💚
        """
        
        keyboard = [
            [InlineKeyboardButton("📤 Chia sẻ link", url=f"https://t.me/share/url?url={link}&text=FreedomWallet - Bot quản lý tài chính cá nhân miễn phí 100%!")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def track_referral(self, referrer_id: int, referred_id: int, referral_code: str):
        """Track new referral"""
        self.db.create_referral_tracking(
            referrer_id=referrer_id,
            referred_id=referred_id,
            referral_code=referral_code
        )
        
        logger.info(f"Referral tracked: {referrer_id} -> {referred_id}")
    
    async def check_referral_milestones(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        referrer_id: int
    ):
        """Check if referrer reached new milestone"""
        stats = self.db.get_referral_stats(referrer_id)
        activated = stats.get('activated_referrals', 0)
        badges = stats.get('referral_badges', [])
        
        # Check for new badges
        for badge_key, config in self.REFERRAL_BADGES.items():
            if activated >= config['threshold'] and badge_key not in badges:
                # Award badge
                self.db.add_referral_badge(referrer_id, badge_key)
                
                # Send celebration
                await self._send_referral_badge(
                    update, context, referrer_id, config
                )
    
    async def _send_referral_badge(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int,
        badge_config: Dict
    ):
        """Send referral badge celebration"""
        message = f"""
{badge_config['emoji']} **{badge_config['title']}**

{badge_config['message']}

Cảm ơn bạn đã giúp xây dựng cộng đồng FreedomWallet! 💚
        """
        
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode='Markdown'
        )
    
    def mark_referral_activated(self, referred_id: int):
        """Mark referral as activated (used bot >3 days)"""
        referral = self.db.get_referral_by_referred(referred_id)
        if referral and not referral['referred_activated']:
            self.db.update_referral_activated(referral['id'], True)
            
            # Update referrer stats
            self.db.increment_activated_referrals(referral['referrer_id'])


# ============================================
# SHAREABLE CONTENT GENERATOR
# ============================================

class ShareableContentGenerator:
    """Generate beautiful shareable images for achievements"""
    
    def __init__(self):
        self.template_path = "assets/achievement_template.png"
        self.font_path = "assets/fonts/Roboto-Bold.ttf"
    
    def generate_milestone_card(
        self,
        user_name: str,
        milestone_title: str,
        milestone_emoji: str,
        stats: Dict
    ) -> io.BytesIO:
        """Generate achievement card image"""
        
        # Create image (1080x1080 for Instagram)
        width, height = 1080, 1080
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            font_large = ImageFont.truetype(self.font_path, 80)
            font_medium = ImageFont.truetype(self.font_path, 50)
            font_small = ImageFont.truetype(self.font_path, 35)
        except:
            # Fallback to default
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw content
        y_offset = 150
        
        # Emoji
        draw.text((width/2, y_offset), milestone_emoji, 
                 font=font_large, anchor="mm", fill='white')
        y_offset += 120
        
        # Title
        draw.text((width/2, y_offset), milestone_title,
                 font=font_medium, anchor="mm", fill='#00ff88')
        y_offset += 100
        
        # Stats
        stats_text = f"🔥 {stats.get('streak', 0)} ngày streak\n"
        stats_text += f"💰 {stats.get('money_saved', 0):,} VNĐ tiết kiệm\n"
        stats_text += f"📊 {stats.get('transactions', 0)} giao dịch ghi chép"
        
        draw.text((width/2, y_offset), stats_text,
                 font=font_small, anchor="mm", fill='white', align='center')
        y_offset += 200
        
        # User name
        draw.text((width/2, y_offset), f"- {user_name} -",
                 font=font_small, anchor="mm", fill='#888888')
        y_offset += 100
        
        # Branding
        draw.text((width/2, height - 100), "FreedomWallet 💚",
                 font=font_small, anchor="mm", fill='#00ff88')
        draw.text((width/2, height - 50), "Tự do tài chính cho mọi người",
                 font=font_small, anchor="mm", fill='#666666')
        
        # Save to BytesIO
        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        
        return output
    
    async def send_shareable_achievement(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        milestone: Dict,
        user_stats: Dict
    ):
        """Generate and send shareable achievement card"""
        user_name = update.effective_user.first_name
        
        # Generate image
        image = self.generate_milestone_card(
            user_name=user_name,
            milestone_title=milestone['title'],
            milestone_emoji=milestone['emoji'],
            stats=user_stats
        )
        
        caption = f"""
{milestone['emoji']} **{milestone['title']}**

Chia sẻ thành tích của bạn để truyền cảm hứng cho người khác! 🚀

#TựDoTàiChính #FreedomWallet
        """
        
        keyboard = [
            [InlineKeyboardButton("📤 Chia sẻ ngay", 
                                url="https://t.me/share/url?url=https://t.me/FreedomWalletBot")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_photo(
            photo=image,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


# ============================================
# MONTHLY SUMMARY & ENGAGEMENT
# ============================================

class MonthlyEngagement:
    """Send monthly summaries to keep users engaged"""
    
    def __init__(self, db):
        self.db = db
    
    async def send_monthly_summary(
        self,
        user_id: int,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Send personalized monthly summary"""
        
        # Get user stats for the month
        stats = self.db.get_monthly_stats(user_id)
        
        # Calculate rankings
        rank_percentile = self.db.get_user_rank_percentile(user_id)
        
        message = f"""
📊 **BÁO CÁO THÁNG {datetime.now().strftime('%m/%Y')}**

💰 **Tài chính:**
• Tổng chi tiêu: {stats['total_expense']:,} VNĐ
• Tổng thu nhập: {stats['total_income']:,} VNĐ
• Tiết kiệm: {stats['saved']:,} VNĐ {self._get_trend_emoji(stats['saved'])}

📊 **Hoạt động:**
• Giao dịch ghi chép: {stats['transactions']} lần
• Ngày hoạt động: {stats['active_days']}/30
• Streak hiện tại: {stats['current_streak']} 🔥

🏆 **Xếp hạng:**
• Bạn thuộc top {rank_percentile}% users tích cực nhất!

🎯 **Milestone tiếp theo:**
{self._get_next_milestone(user_id)}

---

💚 Tiếp tục phát huy! Tháng sau sẽ tốt hơn nữa!
        """
        
        keyboard = []
        
        # Show donate option if eligible
        from donation_handler import DonationTiming
        timing = DonationTiming(self.db)
        
        if timing.should_show_donation_prompt(user_id, "monthly_summary"):
            keyboard.append([
                InlineKeyboardButton("💚 Ủng hộ cộng đồng", callback_data="donate_start:monthly")
            ])
        
        keyboard.append([
            InlineKeyboardButton("📤 Chia sẻ báo cáo", callback_data=f"share_monthly:{user_id}")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    def _get_trend_emoji(self, value: float) -> str:
        """Get emoji based on value trend"""
        if value > 0:
            return "📈"
        elif value < 0:
            return "📉"
        else:
            return "➡️"
    
    def _get_next_milestone(self, user_id: int) -> str:
        """Get next milestone to achieve"""
        from donation_handler import MilestoneDetector
        
        detector = MilestoneDetector(self.db)
        stats = self.db.get_user_stats(user_id)
        reached = stats.get('milestones_reached', [])
        
        # Find next unreached milestone
        for key, config in detector.MILESTONES.items():
            if key not in reached:
                threshold = config['threshold']
                current = stats.get(config['type'], 0)
                remaining = threshold - current
                
                return f"{config['title']}\nCòn {remaining} {config['type']} nữa!"
        
        return "Bạn đã đạt tất cả milestones! 👑"


# ============================================
# COMMUNITY IMPACT DASHBOARD
# ============================================

class CommunityImpactDashboard:
    """Show community-wide impact and statistics"""
    
    def __init__(self, db):
        self.db = db
    
    async def send_community_stats(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Send community impact dashboard"""
        
        stats = self.db.get_community_stats()
        
        message = f"""
🌍 **CỘNG ĐỒNG FREEDOMWALLET**

👥 **Người dùng:**
• Tổng: {stats['total_users']:,} users
• Hoạt động (30 ngày): {stats['active_users']:,}
• Mới tháng này: {stats['new_users']:,}

💰 **Tài chính cộng đồng:**
• Tổng đóng góp: {stats['total_donations']:,} VNĐ
• Contributors: {stats['total_contributors']:,} ({stats['contributor_ratio']:.1f}%)
• Chi phí tháng: {stats['monthly_costs']:,} VNĐ
• Dự trữ: {stats['reserve_balance']:,} VNĐ
• Đủ duy trì: {stats['months_runway']:.1f} tháng

📊 **Tác động:**
• Giao dịch ghi chép: {stats['total_transactions']:,}
• Tổng tiết kiệm: {stats['total_money_saved']:,} VNĐ
• Điểm engagement TB: {stats['avg_engagement_score']:.1f}/100

🚀 **Tăng trưởng:**
• MoM: +{stats['mom_growth']:.1f}%
• Referral: {stats['referral_signups']} người tháng này

---

💚 Cộng đồng lớn mạnh nhờ mọi người!
        """
        
        keyboard = [
            [InlineKeyboardButton("🏆 Wall of Fame", callback_data="wall_of_fame")],
            [InlineKeyboardButton("💚 Ủng hộ", callback_data="donate_start:community")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def send_wall_of_fame(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """Show top contributors"""
        
        query = update.callback_query
        await query.answer()
        
        # Get top contributors
        top_contributors = self.db.get_top_contributors(limit=20)
        
        message = "💎 **WALL OF FAME**\n\n"
        message += f"🙏 {len(top_contributors)} Contributors đã xây dựng cộng đồng FreedomWallet\n\n"
        
        # Top 10
        message += "🏆 **Top Contributors:**\n"
        for i, contributor in enumerate(top_contributors[:10], 1):
            name = contributor.get('display_name', 'Anonymous Supporter')
            
            if i <= 3:
                medals = ["🥇", "🥈", "🥉"]
                message += f"{medals[i-1]} {name}\n"
            else:
                message += f"{i}. {name}\n"
        
        message += f"\n✨ Và {max(0, len(top_contributors) - 10)} Contributors khác!\n"
        message += "\n💚 Cảm ơn tất cả vì đã tin tưởng và ủng hộ!"
        
        keyboard = [
            [InlineKeyboardButton("💚 Ủng hộ ngay", callback_data="donate_start:wall")],
            [InlineKeyboardButton("« Quay lại", callback_data="community_stats")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


# ============================================
# AMBASSADOR PROGRAM
# ============================================

class AmbassadorProgram:
    """Manage community ambassadors"""
    
    AMBASSADOR_CRITERIA = {
        "days_active": 30,  # At least 30 days using bot
        "donations": 1,  # Donated at least once
        "engagement_score": 70,  # High engagement
        "referrals": 5  # Referred at least 5 people
    }
    
    def __init__(self, db):
        self.db = db
    
    def check_ambassador_eligibility(self, user_id: int) -> bool:
        """Check if user is eligible to become ambassador"""
        stats = self.db.get_user_stats(user_id)
        donation_stats = self.db.get_donation_stats(user_id)
        referral_stats = self.db.get_referral_stats(user_id)
        
        return (
            stats.get('days_active', 0) >= self.AMBASSADOR_CRITERIA['days_active']
            and donation_stats.get('donation_count', 0) >= self.AMBASSADOR_CRITERIA['donations']
            and stats.get('engagement_score', 0) >= self.AMBASSADOR_CRITERIA['engagement_score']
            and referral_stats.get('activated_referrals', 0) >= self.AMBASSADOR_CRITERIA['referrals']
        )
    
    async def invite_to_ambassador_program(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int
    ):
        """Invite eligible user to become ambassador"""
        
        message = """
🎯 **Lời mời: FreedomWallet Ambassador**

Chúng tôi nhận thấy bạn là thành viên tích cực và có đóng góp lớn cho cộng đồng!

**FreedomWallet Ambassadors là gì?**
• Người passionate về tự do tài chính
• Giúp spread mission đến nhiều người hơn
• Đóng góp ý tưởng phát triển bot

**Quyền lợi (NON-MONETARY):**
• Badge: 🎯 Ambassador
• Early access to beta features
• Direct line với founder
• Được credit trong updates
• Cộng đồng Ambassadors riêng

**Trách nhiệm:**
• Share bot organically (không spam)
• Giúp newbies trong group
• Give feedback xây dựng
• Represent community values

**Lưu ý:** Đây là volunteer role, không có thưởng tiền. Chỉ dành cho người thực sự muốn xây dựng cộng đồng 💚

Bạn có muốn tham gia không?
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Tôi muốn tham gia!", callback_data=f"ambassador_join:{user_id}")],
            [InlineKeyboardButton("Để tôi suy nghĩ", callback_data="ambassador_later")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def onboard_ambassador(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int
    ):
        """Onboard new ambassador"""
        query = update.callback_query
        await query.answer("Chào mừng bạn trở thành Ambassador! 🎯")
        
        # Update database
        self.db.set_user_ambassador(user_id, True)
        self.db.add_badge(user_id, "ambassador")
        
        message = """
🎯 **Chào mừng Ambassador mới!**

Cảm ơn bạn đã tin tưởng và đồng hành cùng FreedomWallet! 💚

**Bước tiếp theo:**
1. Tham gia Ambassadors Group: [Link]
2. Đọc Ambassador Handbook: [Link]
3. Giới thiệu bản thân với team

**Resources:**
• Brand assets: [Link]
• Community guidelines: [Link]
• Monthly goals: [Link]

Hãy bắt đầu bằng việc tham gia group và say hi! 👋
        """
        
        keyboard = [
            [InlineKeyboardButton("💬 Tham gia Ambassadors Group", 
                                url="https://t.me/FreedomWalletAmbassadors")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


# ============================================
# MAIN GROWTH HANDLER
# ============================================

class GrowthHandler:
    """Main orchestrator for growth & community"""
    
    def __init__(self, db):
        self.db = db
        self.referral = ReferralSystem(db)
        self.shareable = ShareableContentGenerator()
        self.monthly = MonthlyEngagement(db)
        self.community = CommunityImpactDashboard(db)
        self.ambassador = AmbassadorProgram(db)
    
    async def handle_new_user(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        start_param: Optional[str] = None
    ):
        """Handle new user joining via referral or organic"""
        user_id = update.effective_user.id
        
        # Check if referral
        if start_param and start_param.startswith("freedom_"):
            referrer_id = int(start_param.replace("freedom_", ""))
            
            # Track referral
            self.referral.track_referral(referrer_id, user_id, start_param)
            
            # Thank referrer
            await context.bot.send_message(
                chat_id=referrer_id,
                text=f"🎉 Bạn vừa giới thiệu thành công 1 người vào FreedomWallet! Cảm ơn bạn đã giúp xây dựng cộng đồng 💚"
            )
    
    async def check_growth_milestones(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        user_id: int
    ):
        """Check for referral and ambassador milestones"""
        
        # Check referral badges
        await self.referral.check_referral_milestones(update, context, user_id)
        
        # Check ambassador eligibility
        if self.ambassador.check_ambassador_eligibility(user_id):
            if not self.db.is_user_ambassador(user_id):
                await self.ambassador.invite_to_ambassador_program(
                    update, context, user_id
                )


# ============================================
# USAGE EXAMPLE
# ============================================

"""
# In bot.py:

from growth_handler import GrowthHandler

growth_handler = GrowthHandler(db)

# Handle /start with referral
async def start_command(update, context):
    start_param = context.args[0] if context.args else None
    await growth_handler.handle_new_user(update, context, start_param)
    # ... rest of start logic

# Referral link command
async def referral_command(update, context):
    await growth_handler.referral.send_referral_link(update, context)

application.add_handler(CommandHandler("refer", referral_command))

# Monthly summary (scheduled job)
def send_monthly_summaries(context):
    active_users = db.get_all_active_users()
    for user in active_users:
        asyncio.create_task(
            growth_handler.monthly.send_monthly_summary(user['id'], context)
        )

job_queue.run_monthly(send_monthly_summaries, when=datetime.time(hour=10))
"""
