"""
Payment Service - QR Code generation and payment verification
Supports automatic payment detection and Premium upgrade
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
from config.settings import settings
import urllib.parse


class PaymentService:
    """Service for handling payments and generating QR codes"""
    
    # Bank code mapping for VietQR
    BANK_CODES = {
        "OCB": "970448",
        "VIETCOMBANK": "970436",
        "TECHCOMBANK": "970407",
        "MBBANK": "970422",
        "AGRIBANK": "970405",
        "BIDV": "970418",
        "VPBANK": "970432",
        "SACOMBANK": "970403",
        "ACB": "970416",
        "VIETINBANK": "970415"
    }
    
    @staticmethod
    def generate_transfer_code(user_id: int) -> str:
        """
        Generate unique transfer code for user
        Format: FW{user_id}
        
        Example: User 1299465308 â†’ FW1299465308
        """
        return f"FW{user_id}"
    
    @staticmethod
    def generate_qr_url(
        user_id: int,
        amount: int,
        package: str = "PREMIUM"
    ) -> str:
        """
        Generate VietQR URL for bank transfer
        
        Args:
            user_id: Telegram user ID
            amount: Amount in VND
            package: Package name (PREMIUM, etc.)
        
        Returns:
            QR code image URL
        """
        bank_code = PaymentService.BANK_CODES.get(
            settings.PAYMENT_BANK_NAME,
            "970448"  # Default OCB
        )
        
        account_number = settings.PAYMENT_ACCOUNT_NUMBER
        transfer_code = PaymentService.generate_transfer_code(user_id)
        
        # Message format: FW{user_id} {package}
        message = f"{transfer_code} {package}"
        
        # VietQR API format
        # https://img.vietqr.io/image/{bankCode}-{accountNumber}-{template}.jpg?amount={amount}&addInfo={message}&accountName={accountName}
        
        qr_url = f"https://img.vietqr.io/image/{bank_code}-{account_number}-compact.jpg"
        
        params = {
            "amount": str(amount),
            "addInfo": message,
            "accountName": settings.PAYMENT_ACCOUNT_NAME
        }
        
        query_string = urllib.parse.urlencode(params)
        full_url = f"{qr_url}?{query_string}"
        
        logger.info(f"Generated QR for user {user_id}: {transfer_code}, amount: {amount:,} VND")
        
        return full_url
    
    @staticmethod
    def parse_transfer_message(message: str) -> Optional[int]:
        """
        Parse transfer message to extract user ID
        
        Args:
            message: Transfer message (e.g., "FW1299465308 PREMIUM")
        
        Returns:
            User ID if valid, None otherwise
        """
        try:
            parts = message.strip().split()
            if not parts:
                return None
            
            transfer_code = parts[0].upper()
            
            # Check format: FW{user_id}
            if transfer_code.startswith("FW"):
                user_id_str = transfer_code[2:]
                return int(user_id_str)
            
            return None
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def get_payment_instructions(user_id: int, package: str = "PREMIUM") -> Dict[str, Any]:
        """
        Get payment instructions for user
        
        Args:
            user_id: Telegram user ID
            package: Package name
        
        Returns:
            Dict with payment details
        """
        amount = settings.PREMIUM_PRICE_VND
        transfer_code = PaymentService.generate_transfer_code(user_id)
        qr_url = PaymentService.generate_qr_url(user_id, amount, package)
        
        return {
            "bank_name": settings.PAYMENT_BANK_NAME,
            "account_name": settings.PAYMENT_ACCOUNT_NAME,
            "account_number": settings.PAYMENT_ACCOUNT_NUMBER,
            "amount": amount,
            "transfer_code": transfer_code,
            "message": f"{transfer_code} {package}",
            "qr_url": qr_url,
            "package": package
        }
    
    @staticmethod
    async def verify_payment(
        user_id: int,
        transaction_id: Optional[str] = None
    ) -> bool:
        """
        Verify if payment has been received
        
        This is a placeholder for future integration with:
        - Bank API webhooks
        - Payment gateway callbacks
        - Manual verification by admin
        
        Args:
            user_id: Telegram user ID
            transaction_id: Optional transaction ID from bank
        
        Returns:
            True if payment verified, False otherwise
        """
        # TODO: Implement actual payment verification
        # Options:
        # 1. Bank API integration (if available)
        # 2. Webhook from payment gateway
        # 3. Manual verification by admin
        # 4. Google Sheets logging with admin approval
        
        logger.info(f"Payment verification requested for user {user_id}, tx: {transaction_id}")
        
        # For now, return False - requires manual verification
        return False
    
    @staticmethod
    def format_payment_message(payment_info: Dict[str, Any]) -> str:
        """
        Format payment instructions message
        
        Args:
            payment_info: Payment info dict from get_payment_instructions()
        
        Returns:
            Formatted message text
        """
        amount_formatted = f"{payment_info['amount']:,}"
        
        message = f"""
ðŸ’³ **THANH TOÃN {payment_info['package']}**

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ“± **QUÃ‰T MÃƒ QR:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ‘‡ QuÃ©t mÃ£ QR bÃªn dÆ°á»›i báº±ng app ngÃ¢n hÃ ng

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸ’° **HOáº¶C CHUYá»‚N KHOáº¢N:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

ðŸ¦ **NgÃ¢n hÃ ng:** {payment_info['bank_name']}
ðŸ‘¤ **NgÆ°á»i nháº­n:** {payment_info['account_name']}
ðŸ’³ **Sá»‘ TK:** `{payment_info['account_number']}`

ðŸ’µ **Sá»‘ tiá»n:** {amount_formatted} VNÄ

âœï¸ **Ná»™i dung CK:**
`{payment_info['message']}`

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
âš ï¸ **LÆ¯U Ã QUAN TRá»ŒNG:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

â€¢ **PHáº¢I ghi Ä‘Ãºng ná»™i dung:** {payment_info['transfer_code']}
â€¢ Há»‡ thá»‘ng tá»± Ä‘á»™ng kÃ­ch hoáº¡t trong 5-10 phÃºt
â€¢ Náº¿u chÆ°a kÃ­ch hoáº¡t sau 15 phÃºt, liÃªn há»‡ Admin

â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”
ðŸŽ **SAU KHI THANH TOÃN:**
â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”â”

âœ… TÃ i khoáº£n Premium kÃ­ch hoáº¡t tá»± Ä‘á»™ng
âœ… Nháº­n thÃ´ng bÃ¡o xÃ¡c nháº­n
âœ… Sá»­ dá»¥ng ngay táº¥t cáº£ tÃ­nh nÄƒng

ðŸ’¬ **Cáº§n há»— trá»£?** Nháº¥n "LiÃªn há»‡ Admin" bÃªn dÆ°á»›i
"""
        return message


class PaymentVerificationService:
    """Service for manual payment verification by admin"""
    
    @staticmethod
    async def create_verification_request(
        user_id: int,
        amount: int,
        transaction_info: str,
        submitted_by: int
    ) -> str:
        """
        Create payment verification request
        
        Args:
            user_id: User who made payment
            amount: Payment amount
            transaction_info: Transaction details from user
            submitted_by: User ID who submitted verification
        
        Returns:
            Verification request ID
        """
        from app.utils.database import get_db, PaymentVerification
        
        db = next(get_db())
        try:
            verification = PaymentVerification(
                user_id=user_id,
                amount=amount,
                transaction_info=transaction_info,
                submitted_by=submitted_by,
                status="PENDING",
                created_at=datetime.utcnow()
            )
            
            db.add(verification)
            db.commit()
            db.refresh(verification)
            
            verification_id = f"VER{verification.id}"
            
            logger.info(f"Created verification request {verification_id} for user {user_id}")
            
            return verification_id
        finally:
            db.close()
    
    @staticmethod
    async def approve_payment(
        verification_id: str,
        approved_by: int
    ) -> bool:
        """
        Approve payment and upgrade user
        
        Args:
            verification_id: Verification request ID
            approved_by: Admin user ID
        
        Returns:
            True if approved successfully
        """
        from app.utils.database import get_db, PaymentVerification, User
        from app.core.subscription import SubscriptionManager
        
        db = next(get_db())
        try:
            # Get verification request
            ver_id = int(verification_id.replace("VER", ""))
            verification = db.query(PaymentVerification).filter(
                PaymentVerification.id == ver_id
            ).first()
            
            if not verification:
                logger.error(f"Verification {verification_id} not found")
                return False
            
            if verification.status != "PENDING":
                logger.warning(f"Verification {verification_id} already processed: {verification.status}")
                return False
            
            # Get user
            user = db.query(User).filter(User.id == verification.user_id).first()
            if not user:
                logger.error(f"User {verification.user_id} not found")
                return False
            
            # Smart Premium Upgrade/Renewal Logic
            now = datetime.utcnow()
            
            try:
                # Check if this is a renewal (user already Premium with valid subscription)
                if (user.subscription_tier == "PREMIUM" and 
                    user.premium_expires_at and 
                    user.premium_expires_at > now):
                    
                    # RENEWAL: Extend from current expiry date
                    days_until_expiry = (user.premium_expires_at - now).days
                    
                    # Extend 365 days from current expiry
                    from datetime import timedelta
                    user.premium_expires_at = user.premium_expires_at + timedelta(days=365)
                    
                    logger.info(f"Premium RENEWAL for user {user.id}: Extended from {days_until_expiry} days remaining to +365 more days")
                    logger.info(f"New expiry: {user.premium_expires_at}")
                
                else:
                    # NEW or EXPIRED: Use standard upgrade (starts from now)
                    SubscriptionManager.upgrade_to_premium(user, months=12)
                    logger.info(f"Premium ACTIVATION for user {user.id}: 365 days from now")
                
                success = True
                
            except Exception as upgrade_error:
                logger.error(f"Failed to upgrade user {user.id}: {upgrade_error}")
                success = False
            
            if success:
                # Update verification status
                verification.status = "APPROVED"
                verification.approved_by = approved_by
                verification.approved_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Payment approved: {verification_id}, user {user.id} upgraded to Premium")
                return True
            else:
                logger.error(f"Failed to upgrade user {user.id} to Premium")
                return False
                
        except Exception as e:
            logger.error(f"Error approving payment {verification_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    async def reject_payment(
        verification_id: str,
        rejected_by: int,
        reason: str
    ) -> bool:
        """
        Reject payment verification request
        
        Args:
            verification_id: Verification request ID (format: VER123)
            rejected_by: Admin user ID who rejected
            reason: Rejection reason
        
        Returns:
            True if rejected successfully
        """
        from app.utils.database import get_db, PaymentVerification
        
        db = next(get_db())
        try:
            # Get verification request
            ver_id = int(verification_id.replace("VER", ""))
            verification = db.query(PaymentVerification).filter(
                PaymentVerification.id == ver_id
            ).first()
            
            if not verification:
                logger.error(f"Verification {verification_id} not found")
                return False
            
            if verification.status != "PENDING":
                logger.warning(f"Verification {verification_id} already processed: {verification.status}")
                return False
            
            # Update verification status
            verification.status = "REJECTED"
            verification.approved_by = rejected_by
            verification.approved_at = datetime.utcnow()
            verification.notes = reason
            
            db.commit()
            
            logger.info(f"Payment rejected: {verification_id}, reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Error rejecting payment {verification_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()

