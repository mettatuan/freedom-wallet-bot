"""
🛡️ FRAUD DETECTION
===================

Phát hiện và ngăn chặn referral fraud

Red flags:
- Same IP/device nhiều accounts
- Too fast registration (bot-like)
- Referrer và referred có behavior giống nhau
- Fake engagement patterns

Author: Freedom Wallet Team
Version: 2.0
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from loguru import logger
from bot.utils.database import Database

# ============================================================================
# FRAUD DETECTOR
# ============================================================================

class FraudDetector:
    """
    Detect suspicious referral patterns
    """
    
    # Thresholds
    MAX_REFS_PER_IP_PER_DAY = 5
    MAX_REFS_PER_DEVICE_PER_DAY = 3
    MIN_TIME_BETWEEN_REFS = 60  # seconds
    SUSPICIOUS_VELOCITY_THRESHOLD = 10  # refs trong 1h
    
    def __init__(self):
        self.db = Database()
    
    # -------------------------------------------------------------------------
    # Registration Time Fraud
    # -------------------------------------------------------------------------
    
    async def check_registration_fraud(
        self, 
        referrer_id: int,
        new_user_id: int,
        ip_address: str,
        user_agent: str,
        device_fingerprint: str
    ) -> Dict:
        """
        Comprehensive fraud check
        
        Returns:
            dict: {
                'is_suspicious': bool,
                'fraud_score': float (0-100),
                'reasons': List[str],
                'action': 'allow' | 'review' | 'block'
            }
        """
        
        fraud_score = 0
        reasons = []
        
        # Check 1: IP abuse
        ip_score, ip_reason = await self._check_ip_abuse(referrer_id, ip_address)
        fraud_score += ip_score
        if ip_reason:
            reasons.append(ip_reason)
        
        # Check 2: Device abuse
        device_score, device_reason = await self._check_device_abuse(referrer_id, device_fingerprint)
        fraud_score += device_score
        if device_reason:
            reasons.append(device_reason)
        
        # Check 3: Velocity (too fast)
        velocity_score, velocity_reason = await self._check_velocity(referrer_id)
        fraud_score += velocity_score
        if velocity_reason:
            reasons.append(velocity_reason)
        
        # Check 4: Time pattern (all refs trong giờ hành chính?)
        pattern_score, pattern_reason = await self._check_time_pattern(referrer_id)
        fraud_score += pattern_score
        if pattern_reason:
            reasons.append(pattern_reason)
        
        # Check 5: Behavior similarity
        behavior_score, behavior_reason = await self._check_behavior_similarity(
            referrer_id, new_user_id
        )
        fraud_score += behavior_score
        if behavior_reason:
            reasons.append(behavior_reason)
        
        # Determine action
        action = self._determine_action(fraud_score)
        
        result = {
            'is_suspicious': fraud_score >= 30,
            'fraud_score': fraud_score,
            'reasons': reasons,
            'action': action
        }
        
        # Log if suspicious
        if result['is_suspicious']:
            logger.warning(
                f"🚨 FRAUD ALERT: Referrer {referrer_id} → New user {new_user_id}\n"
                f"Score: {fraud_score}, Reasons: {reasons}"
            )
        
        return result
    
    async def _check_ip_abuse(self, referrer_id: int, ip_address: str) -> tuple:
        """Check if IP đã dùng cho nhiều referrals"""
        
        # Count referrals from this IP in last 24h
        count = self.db.count_referrals_by_ip(
            referrer_id=referrer_id,
            ip_address=ip_address,
            since=datetime.now() - timedelta(days=1)
        )
        
        if count >= self.MAX_REFS_PER_IP_PER_DAY:
            return (40, f"IP {ip_address} used for {count} refs/24h")
        elif count >= 3:
            return (20, f"IP {ip_address} used for {count} refs/24h")
        
        return (0, None)
    
    async def _check_device_abuse(self, referrer_id: int, device_fingerprint: str) -> tuple:
        """Check if device đã dùng cho nhiều referrals"""
        
        count = self.db.count_referrals_by_device(
            referrer_id=referrer_id,
            device_fingerprint=device_fingerprint,
            since=datetime.now() - timedelta(days=1)
        )
        
        if count >= self.MAX_REFS_PER_DEVICE_PER_DAY:
            return (50, f"Device used for {count} refs/24h")
        elif count >= 2:
            return (25, f"Device used for {count} refs/24h")
        
        return (0, None)
    
    async def _check_velocity(self, referrer_id: int) -> tuple:
        """Check if referrals too fast (bot-like)"""
        
        # Get last 10 referrals
        recent_refs = self.db.get_recent_referrals(referrer_id, limit=10)
        
        if len(recent_refs) < 2:
            return (0, None)
        
        # Calculate time between refs
        time_diffs = []
        for i in range(1, len(recent_refs)):
            diff = (recent_refs[i-1].created_at - recent_refs[i].created_at).total_seconds()
            time_diffs.append(diff)
        
        avg_diff = sum(time_diffs) / len(time_diffs)
        
        # Too fast? (avg < 60s)
        if avg_diff < self.MIN_TIME_BETWEEN_REFS:
            return (35, f"Avg time between refs: {avg_diff:.0f}s (too fast)")
        
        # Check if >10 refs trong 1h
        refs_last_hour = self.db.count_referrals_since(
            referrer_id,
            since=datetime.now() - timedelta(hours=1)
        )
        
        if refs_last_hour >= self.SUSPICIOUS_VELOCITY_THRESHOLD:
            return (40, f"{refs_last_hour} refs in 1 hour")
        
        return (0, None)
    
    async def _check_time_pattern(self, referrer_id: int) -> tuple:
        """
        Check if all referrals trong working hours (9AM-5PM)
        
        Legit referrals spread throughout day, fraud often trong office hours
        """
        
        refs = self.db.get_all_referrals(referrer_id)
        
        if len(refs) < 5:
            return (0, None)  # Not enough data
        
        # Count refs by hour
        hour_counts = defaultdict(int)
        for ref in refs:
            hour = ref.created_at.hour
            hour_counts[hour] += 1
        
        # Check if 80%+ refs trong 9AM-5PM
        work_hours_count = sum(hour_counts[h] for h in range(9, 17))
        work_hours_pct = work_hours_count / len(refs)
        
        if work_hours_pct > 0.8:
            return (15, f"{work_hours_pct*100:.0f}% refs trong office hours")
        
        return (0, None)
    
    async def _check_behavior_similarity(self, referrer_id: int, referred_id: int) -> tuple:
        """
        Check if referrer và referred có behavior giống nhau (same person?)
        
        Signals:
        - Cùng timezone activity pattern
        - Cùng typing speed
        - Cùng navigation pattern trong bot
        """
        
        # Get activity logs
        referrer_activity = self.db.get_user_activity(referrer_id, days=7)
        referred_activity = self.db.get_user_activity(referred_id, days=1)
        
        if not referrer_activity or not referred_activity:
            return (0, None)
        
        # Check timezone (active hours)
        referrer_hours = set(a.hour for a in referrer_activity)
        referred_hours = set(a.hour for a in referred_activity)
        
        overlap = len(referrer_hours & referred_hours)
        if overlap > 10:  # Very similar activity times
            return (20, f"Activity time overlap: {overlap} hours")
        
        return (0, None)
    
    def _determine_action(self, fraud_score: float) -> str:
        """
        Determine action based on fraud score
        
        0-29: Allow (normal)
        30-59: Review (manual check required)
        60-100: Block (auto-reject)
        """
        
        if fraud_score < 30:
            return 'allow'
        elif fraud_score < 60:
            return 'review'
        else:
            return 'block'
    
    # -------------------------------------------------------------------------
    # Action Handling
    # -------------------------------------------------------------------------
    
    async def handle_fraud_detection(
        self, 
        referrer_id: int,
        referred_id: int,
        fraud_result: Dict
    ):
        """
        Take action based on fraud detection result
        """
        
        action = fraud_result['action']
        
        if action == 'allow':
            # Normal flow, do nothing
            return
        
        elif action == 'review':
            # Flag for manual review
            await self._flag_for_review(referrer_id, referred_id, fraud_result)
        
        elif action == 'block':
            # Auto-reject referral
            await self._block_referral(referrer_id, referred_id, fraud_result)
    
    async def _flag_for_review(self, referrer_id: int, referred_id: int, fraud_result: Dict):
        """Flag referral for manual review"""
        
        # Mark referral as pending review
        referral = self.db.get_referral(referrer_id, referred_id)
        referral.is_valid = False  # Temporarily invalid
        referral.review_status = 'PENDING'
        referral.fraud_score = fraud_result['fraud_score']
        referral.fraud_reasons = fraud_result['reasons']
        self.db.save(referral)
        
        # Don't increment referrer's count yet
        
        # Notify admin
        await self._notify_admin_review(referrer_id, referred_id, fraud_result)
        
        logger.info(f"Flagged referral {referrer_id}→{referred_id} for review")
    
    async def _block_referral(self, referrer_id: int, referred_id: int, fraud_result: Dict):
        """Auto-block referral"""
        
        # Mark referral as invalid
        referral = self.db.get_referral(referrer_id, referred_id)
        referral.is_valid = False
        referral.review_status = 'BLOCKED'
        referral.fraud_score = fraud_result['fraud_score']
        referral.fraud_reasons = fraud_result['reasons']
        self.db.save(referral)
        
        # Notify referrer (carefully worded)
        await self._notify_referrer_invalid(referrer_id, referred_id)
        
        # Notify admin
        await self._notify_admin_block(referrer_id, referred_id, fraud_result)
        
        logger.warning(f"Blocked referral {referrer_id}→{referred_id}, score: {fraud_result['fraud_score']}")
    
    async def _notify_admin_review(self, referrer_id: int, referred_id: int, fraud_result: Dict):
        """Gửi thông báo cho admin về case cần review"""
        
        from telegram import Bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        referrer = self.db.get_user(referrer_id)
        referred = self.db.get_user(referred_id)
        
        message = (
            "🔍 **FRAUD REVIEW NEEDED**\n\n"
            f"Referrer: {referrer.full_name} (ID: {referrer_id})\n"
            f"Referred: {referred.full_name} (ID: {referred_id})\n\n"
            f"**Fraud Score:** {fraud_result['fraud_score']}/100\n\n"
            f"**Reasons:**\n"
        )
        
        for reason in fraud_result['reasons']:
            message += f"• {reason}\n"
        
        message += f"\n[Review in Admin Panel](/admin/referrals/{referrer_id}_{referred_id})"
        
        # Send to admin chat
        await bot.send_message(
            chat_id=settings.ADMIN_CHAT_ID,
            text=message,
            parse_mode="Markdown"
        )
    
    async def _notify_referrer_invalid(self, referrer_id: int, referred_id: int):
        """Notify referrer về invalid referral (carefully worded)"""
        
        from telegram import Bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        referrer = self.db.get_user(referrer_id)
        
        # Gentle message (không accuse fraud trực tiếp)
        message = (
            "ℹ️ **Thông báo xác minh**\n\n"
            "Một trong những lượt giới thiệu gần đây của bạn đang được xác minh.\n\n"
            "Đây là quy trình thường xuyên để đảm bảo chất lượng cộng đồng.\n\n"
            "Nếu hợp lệ, lượt giới thiệu sẽ được cộng trong 24-48h.\n\n"
            "💡 Tiếp tục giới thiệu bạn bè thật để đạt VIP nhé!"
        )
        
        await bot.send_message(
            chat_id=referrer.telegram_id,
            text=message,
            parse_mode="Markdown"
        )


# ============================================================================
# ADMIN TOOLS
# ============================================================================

class FraudAdminTools:
    """
    Admin tools to review and manage fraud cases
    """
    
    def __init__(self):
        self.db = Database()
    
    async def get_pending_reviews(self) -> List:
        """Get all referrals pending manual review"""
        return self.db.get_referrals_by_review_status('PENDING')
    
    async def approve_referral(self, referral_id: int, admin_id: int):
        """Admin approves referral"""
        
        referral = self.db.get_referral_by_id(referral_id)
        referral.is_valid = True
        referral.review_status = 'APPROVED'
        referral.reviewed_by = admin_id
        referral.reviewed_at = datetime.now()
        self.db.save(referral)
        
        # Increment referrer's count
        referrer = self.db.get_user(referral.referrer_id)
        referrer.referral_count += 1
        self.db.save(referrer)
        
        # Notify referrer
        await self._notify_approved(referral.referrer_id)
        
        logger.info(f"Admin {admin_id} approved referral {referral_id}")
    
    async def reject_referral(self, referral_id: int, admin_id: int, reason: str):
        """Admin rejects referral"""
        
        referral = self.db.get_referral_by_id(referral_id)
        referral.is_valid = False
        referral.review_status = 'REJECTED'
        referral.reviewed_by = admin_id
        referral.reviewed_at = datetime.now()
        referral.rejection_reason = reason
        self.db.save(referral)
        
        # Notify referrer
        await self._notify_rejected(referral.referrer_id, reason)
        
        logger.info(f"Admin {admin_id} rejected referral {referral_id}: {reason}")
    
    async def _notify_approved(self, referrer_id: int):
        """Notify về approved referral"""
        
        from telegram import Bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        referrer = self.db.get_user(referrer_id)
        
        await bot.send_message(
            chat_id=referrer.telegram_id,
            text=(
                "✅ **Xác minh thành công!**\n\n"
                "Lượt giới thiệu đã được xác nhận.\n"
                f"Bạn hiện có **{referrer.referral_count}** lượt giới thiệu hợp lệ.\n\n"
                "Tiếp tục phát triển! 🚀"
            ),
            parse_mode="Markdown"
        )
    
    async def _notify_rejected(self, referrer_id: int, reason: str):
        """Notify về rejected referral"""
        
        from telegram import Bot
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        
        referrer = self.db.get_user(referrer_id)
        
        await bot.send_message(
            chat_id=referrer.telegram_id,
            text=(
                "❌ **Không hợp lệ**\n\n"
                "Lượt giới thiệu không đạt yêu cầu xác minh.\n\n"
                f"Lý do: {reason}\n\n"
                "💡 Hãy giới thiệu bạn bè thật để được công nhận nhé!"
            ),
            parse_mode="Markdown"
        )


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test_fraud_detection():
        detector = FraudDetector()
        
        # Simulate suspicious referral
        result = await detector.check_registration_fraud(
            referrer_id=123,
            new_user_id=456,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0...",
            device_fingerprint="abc123def456"
        )
        
        print(f"Fraud Score: {result['fraud_score']}")
        print(f"Action: {result['action']}")
        print(f"Reasons: {result['reasons']}")
    
    asyncio.run(test_fraud_detection())
