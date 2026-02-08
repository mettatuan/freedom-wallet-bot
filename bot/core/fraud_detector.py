"""
🛡️ FRAUD DETECTION SYSTEM (Week 5)
====================================

Multi-layer fraud detection:
- Velocity checks (refs per time window)
- IP clustering (same IP, multiple refs)
- User-agent clustering (same device pattern)
- Device fingerprint matching
- Manual review queue

Strategy: Soft flags + manual review (NO auto-ban)

Author: Freedom Wallet Team
Version: 1.0 (Week 5 - Fraud Prevention)
Date: 2026-02-08
"""

from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from bot.utils.database import SessionLocal, Referral, User
from loguru import logger
import hashlib


class FraudDetector:
    """
    Fraud detection engine with scoring system
    
    Scoring Rules:
    - 0-30: AUTO_APPROVED (low risk)
    - 31-70: PENDING_REVIEW (medium risk, soft flag)
    - 71-100: HIGH_RISK (needs immediate review)
    
    Usage:
        detector = FraudDetector()
        score, flags = detector.check_referral(referrer_id, ip, user_agent, device_fp)
        if score > 30:
            # Flag for review
    """
    
    # Configuration (tuneable thresholds)
    VELOCITY_WINDOWS = {
        'hour': {'window': timedelta(hours=1), 'max_refs': 3, 'score': 25},
        'day': {'window': timedelta(days=1), 'max_refs': 10, 'score': 20},
        'week': {'window': timedelta(days=7), 'max_refs': 30, 'score': 15},
    }
    
    IP_CLUSTER_THRESHOLD = 5  # Same IP, max 5 different users
    IP_CLUSTER_SCORE = 30
    
    DEVICE_CLUSTER_THRESHOLD = 3  # Same device fingerprint, max 3 users
    DEVICE_CLUSTER_SCORE = 40
    
    USER_AGENT_SIMILARITY_SCORE = 15  # Similar user-agent pattern
    
    def __init__(self):
        self.session = SessionLocal()
    
    def check_referral(
        self, 
        referrer_id: int,
        referred_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_fingerprint: Optional[str] = None
    ) -> Tuple[int, List[str]]:
        """
        Check referral for fraud signals
        
        Args:
            referrer_id: User making referrals
            referred_id: New user being referred
            ip_address: IP address of referred user
            user_agent: User-agent string
            device_fingerprint: Unique device identifier
        
        Returns:
            (fraud_score, flags) - Tuple of score (0-100) and list of flags
        """
        score = 0
        flags = []
        
        # Check 1: Velocity (refs per time window)
        velocity_score, velocity_flags = self._check_velocity(referrer_id)
        score += velocity_score
        flags.extend(velocity_flags)
        
        # Check 2: IP clustering (same IP, multiple referred users)
        if ip_address:
            ip_score, ip_flags = self._check_ip_cluster(referrer_id, ip_address)
            score += ip_score
            flags.extend(ip_flags)
        
        # Check 3: Device fingerprint clustering
        if device_fingerprint:
            device_score, device_flags = self._check_device_cluster(referrer_id, device_fingerprint)
            score += device_score
            flags.extend(device_flags)
        
        # Check 4: User-agent patterns
        if user_agent:
            ua_score, ua_flags = self._check_user_agent(referrer_id, user_agent)
            score += ua_score
            flags.extend(ua_flags)
        
        # Check 5: Self-referral (same user trying to refer themselves)
        if referrer_id == referred_id:
            score += 100
            flags.append("SELF_REFERRAL")
        
        # Cap score at 100
        score = min(score, 100)
        
        logger.info(
            f"🛡️ Fraud check: referrer={referrer_id}, score={score}, flags={flags}"
        )
        
        return (score, flags)
    
    def _check_velocity(self, referrer_id: int) -> Tuple[int, List[str]]:
        """
        Check referral velocity (refs per time window)
        
        Returns:
            (score, flags)
        """
        score = 0
        flags = []
        
        now = datetime.utcnow()
        
        for window_name, config in self.VELOCITY_WINDOWS.items():
            window_start = now - config['window']
            
            # Count refs in this window
            ref_count = self.session.query(Referral).filter(
                Referral.referrer_id == referrer_id,
                Referral.created_at >= window_start
            ).count()
            
            if ref_count > config['max_refs']:
                score += config['score']
                flags.append(f"VELOCITY_{window_name.upper()}_{ref_count}")
                logger.warning(
                    f"⚠️ Velocity alert: User {referrer_id} has {ref_count} refs in last {window_name}"
                )
        
        return (score, flags)
    
    def _check_ip_cluster(self, referrer_id: int, ip_address: str) -> Tuple[int, List[str]]:
        """
        Check if same IP has been used for multiple referrals
        
        Returns:
            (score, flags)
        """
        score = 0
        flags = []
        
        # Count unique referred_ids with this IP from this referrer
        ip_refs = self.session.query(Referral).filter(
            Referral.referrer_id == referrer_id,
            Referral.ip_address == ip_address
        ).all()
        
        unique_referred = set(ref.referred_id for ref in ip_refs)
        
        if len(unique_referred) > self.IP_CLUSTER_THRESHOLD:
            score += self.IP_CLUSTER_SCORE
            flags.append(f"IP_CLUSTER_{len(unique_referred)}")
            logger.warning(
                f"⚠️ IP clustering: {len(unique_referred)} different users from IP {ip_address} for referrer {referrer_id}"
            )
        
        return (score, flags)
    
    def _check_device_cluster(self, referrer_id: int, device_fp: str) -> Tuple[int, List[str]]:
        """
        Check if same device fingerprint has been used multiple times
        
        Returns:
            (score, flags)
        """
        score = 0
        flags = []
        
        # Count unique referred_ids with this device fingerprint
        device_refs = self.session.query(Referral).filter(
            Referral.referrer_id == referrer_id,
            Referral.device_fingerprint == device_fp
        ).all()
        
        unique_referred = set(ref.referred_id for ref in device_refs)
        
        if len(unique_referred) > self.DEVICE_CLUSTER_THRESHOLD:
            score += self.DEVICE_CLUSTER_SCORE
            flags.append(f"DEVICE_CLUSTER_{len(unique_referred)}")
            logger.warning(
                f"⚠️ Device clustering: {len(unique_referred)} different users from device {device_fp[:8]}... for referrer {referrer_id}"
            )
        
        return (score, flags)
    
    def _check_user_agent(self, referrer_id: int, user_agent: str) -> Tuple[int, List[str]]:
        """
        Check for suspicious user-agent patterns
        
        Returns:
            (score, flags)
        """
        score = 0
        flags = []
        
        # Get recent referrals from this referrer
        recent_refs = self.session.query(Referral).filter(
            Referral.referrer_id == referrer_id,
            Referral.user_agent.isnot(None)
        ).order_by(Referral.created_at.desc()).limit(10).all()
        
        if not recent_refs:
            return (0, [])
        
        # Check for identical user-agents (exact duplicates)
        user_agents = [ref.user_agent for ref in recent_refs]
        identical_count = user_agents.count(user_agent)
        
        if identical_count > 2:
            score += self.USER_AGENT_SIMILARITY_SCORE
            flags.append(f"UA_DUPLICATE_{identical_count}")
            logger.warning(
                f"⚠️ User-agent duplication: {identical_count} identical UAs for referrer {referrer_id}"
            )
        
        return (score, flags)
    
    def get_review_status(self, fraud_score: int) -> str:
        """
        Determine review status based on fraud score
        
        Returns:
            AUTO_APPROVED | PENDING_REVIEW | HIGH_RISK
        """
        if fraud_score <= 30:
            return "AUTO_APPROVED"
        elif fraud_score <= 70:
            return "PENDING_REVIEW"
        else:
            return "HIGH_RISK"
    
    def get_pending_reviews(self, limit: int = 50) -> List[Dict]:
        """
        Get referrals pending manual review
        
        Returns:
            List of dicts with referral info + fraud details
        """
        pending = self.session.query(Referral).filter(
            Referral.review_status.in_(['PENDING_REVIEW', 'HIGH_RISK'])
        ).order_by(
            Referral.velocity_score.desc(),  # High risk first
            Referral.created_at.desc()
        ).limit(limit).all()
        
        results = []
        for ref in pending:
            # Get referrer and referred user info
            referrer = self.session.query(User).filter(User.id == ref.referrer_id).first()
            referred = self.session.query(User).filter(User.id == ref.referred_id).first()
            
            results.append({
                'referral_id': ref.id,
                'referrer_id': ref.referrer_id,
                'referrer_name': referrer.username or referrer.full_name if referrer else 'Unknown',
                'referred_id': ref.referred_id,
                'referred_name': referred.username or referred.full_name if referred else 'Unknown',
                'fraud_score': ref.velocity_score,
                'review_status': ref.review_status,
                'ip_address': ref.ip_address,
                'user_agent': ref.user_agent[:50] + '...' if ref.user_agent and len(ref.user_agent) > 50 else ref.user_agent,
                'created_at': ref.created_at,
            })
        
        return results
    
    def approve_referral(self, referral_id: int, admin_id: int, reason: str = None) -> bool:
        """
        Manually approve a flagged referral
        
        Args:
            referral_id: Referral ID to approve
            admin_id: Admin user ID approving
            reason: Optional reason
        
        Returns:
            True if successful
        """
        referral = self.session.query(Referral).filter(Referral.id == referral_id).first()
        
        if not referral:
            logger.error(f"Referral {referral_id} not found")
            return False
        
        referral.review_status = "AUTO_APPROVED"
        referral.reviewed_by = admin_id
        referral.reviewed_at = datetime.utcnow()
        
        # If referral was PENDING, now mark as VERIFIED
        if referral.status == "PENDING":
            referral.status = "VERIFIED"
            referral.verified_at = datetime.utcnow()
            
            # Increment referrer count
            referrer = self.session.query(User).filter(User.id == referral.referrer_id).first()
            if referrer:
                referrer.referral_count += 1
        
        self.session.commit()
        
        logger.info(
            f"✅ Referral {referral_id} manually approved by admin {admin_id}"
            + (f": {reason}" if reason else "")
        )
        
        return True
    
    def reject_referral(self, referral_id: int, admin_id: int, reason: str = None) -> bool:
        """
        Manually reject a flagged referral
        
        Args:
            referral_id: Referral ID to reject
            admin_id: Admin user ID rejecting
            reason: Optional reason
        
        Returns:
            True if successful
        """
        referral = self.session.query(Referral).filter(Referral.id == referral_id).first()
        
        if not referral:
            logger.error(f"Referral {referral_id} not found")
            return False
        
        referral.review_status = "REJECTED"
        referral.reviewed_by = admin_id
        referral.reviewed_at = datetime.utcnow()
        referral.status = "REJECTED"  # Also mark status as rejected
        
        self.session.commit()
        
        logger.info(
            f"⛔ Referral {referral_id} rejected by admin {admin_id}"
            + (f": {reason}" if reason else "")
        )
        
        return True
    
    def get_fraud_stats(self) -> Dict:
        """
        Get overall fraud detection statistics
        
        Returns:
            Dict with fraud stats
        """
        total_refs = self.session.query(Referral).count()
        
        auto_approved = self.session.query(Referral).filter(
            Referral.review_status == "AUTO_APPROVED"
        ).count()
        
        pending_review = self.session.query(Referral).filter(
            Referral.review_status == "PENDING_REVIEW"
        ).count()
        
        high_risk = self.session.query(Referral).filter(
            Referral.review_status == "HIGH_RISK"
        ).count()
        
        rejected = self.session.query(Referral).filter(
            Referral.review_status == "REJECTED"
        ).count()
        
        return {
            'total_referrals': total_refs,
            'auto_approved': auto_approved,
            'pending_review': pending_review,
            'high_risk': high_risk,
            'rejected': rejected,
            'approval_rate': round(auto_approved / total_refs * 100, 1) if total_refs > 0 else 0,
        }
    
    def close(self):
        """Close database session"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_device_fingerprint(user_agent: str, telegram_id: int) -> str:
    """
    Generate device fingerprint from available data
    
    Note: In Telegram bot, we don't have access to browser fingerprinting,
    so we create a simple hash from user_agent + telegram_id
    
    Args:
        user_agent: User-agent string (from Telegram app)
        telegram_id: Telegram user ID
    
    Returns:
        64-char hex fingerprint
    """
    data = f"{user_agent}_{telegram_id}"
    return hashlib.sha256(data.encode()).hexdigest()


def check_referral_fraud(
    referrer_id: int,
    referred_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Tuple[int, List[str], str]:
    """
    Convenience function to check fraud
    
    Returns:
        (fraud_score, flags, review_status)
    """
    # Generate device fingerprint if user_agent available
    device_fp = None
    if user_agent:
        device_fp = generate_device_fingerprint(user_agent, referred_id)
    
    with FraudDetector() as detector:
        score, flags = detector.check_referral(
            referrer_id,
            referred_id,
            ip_address,
            user_agent,
            device_fp
        )
        review_status = detector.get_review_status(score)
        
        return (score, flags, review_status)
