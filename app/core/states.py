"""
🔐 STATE & PROGRAM DEFINITIONS
================================

Tách riêng USER STATE (bản chất) và CURRENT PROGRAM (chương trình tham gia)

Author: Freedom Wallet Team
Version: 2.0 (Improved Architecture)
"""

from enum import Enum, auto
from typing import Set, Dict

# ============================================================================
# USER STATES - Bản chất người dùng (ít thay đổi)
# ============================================================================

class UserState(Enum):
    """
    Core user states - Identity & tier
    
    Nguyên tắc:
    - State phản ánh VALUE của user (visitor → VIP → advocate)
    - KHÔNG phản ánh chương trình đang tham gia
    - State chỉ đi lên, KHÔNG đi xuống (trừ churn)
    """
    
    VISITOR = "VISITOR"
    # Chưa đăng ký, mới click link
    
    REGISTERED = "REGISTERED"
    # Đã đăng ký, 0-1 referrals
    
    VIP = "VIP"
    # Đã unlock VIP (2+ referrals)
    
    SUPER_VIP = "SUPER_VIP"
    # Đã unlock Super VIP (50+ referrals)
    
    ADVOCATE = "ADVOCATE"
    # Super VIP + active coach (100+ referrals hoặc revenue > threshold)
    
    CHURNED = "CHURNED"
    # Inactive 90+ days, re-engagement failed


class ProgramType(Enum):
    """
    Programs - Chương trình người dùng có thể tham gia
    
    Đặc điểm:
    - User có thể tham gia nhiều programs (VIP + mentor + affiliate)
    - Program có start/end date
    - Program có progression (day 1, 2, 3...)
    """
    
    # Nurture campaigns
    NURTURE_CAMPAIGN = "NURTURE_CAMPAIGN"
    # 7-day nurture for REGISTERED users
    
    # Education programs
    ONBOARDING_7_DAY = "ONBOARDING_7_DAY"
    # 7-day learning journey for VIP
    
    ADVANCED_WORKSHOP = "ADVANCED_WORKSHOP"
    # Advanced 30-day workshop for graduated VIP
    
    # Community programs
    MENTOR_PROGRAM = "MENTOR_PROGRAM"
    # Super VIP teaching others
    
    AFFILIATE_PROGRAM = "AFFILIATE_PROGRAM"
    # Revenue sharing active
    
    # Re-engagement
    REACTIVATION = "REACTIVATION"
    # Win-back campaign for inactive users


# ============================================================================
# STATE MACHINE - Logic chuyển state
# ============================================================================

class StateMachine:
    """
    Quản lý state transitions với validation
    """
    
    # Valid transitions map
    VALID_TRANSITIONS: Dict[UserState, Set[UserState]] = {
        UserState.VISITOR: {
            UserState.REGISTERED,
            UserState.CHURNED
        },
        UserState.REGISTERED: {
            UserState.VIP,
            UserState.CHURNED
        },
        UserState.VIP: {
            UserState.SUPER_VIP,
            UserState.CHURNED
        },
        UserState.SUPER_VIP: {
            UserState.ADVOCATE,
            UserState.VIP,  # Decay: Super VIP → VIP if inactive
            UserState.CHURNED
        },
        UserState.ADVOCATE: {
            UserState.SUPER_VIP,  # Decay: if fall below threshold
            UserState.CHURNED
        },
        UserState.CHURNED: {
            UserState.REGISTERED,  # Re-activation successful
        }
    }
    
    @classmethod
    def is_valid_transition(cls, from_state: UserState, to_state: UserState) -> bool:
        """
        Kiểm tra xem transition có hợp lệ không
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            bool: True if valid
        """
        return to_state in cls.VALID_TRANSITIONS.get(from_state, set())
    
    @classmethod
    def get_next_states(cls, current_state: UserState) -> Set[UserState]:
        """Get all possible next states"""
        return cls.VALID_TRANSITIONS.get(current_state, set())


# ============================================================================
# PROGRAM REQUIREMENTS - Điều kiện join program
# ============================================================================

class ProgramRequirements:
    """
    Định nghĩa requirements để tham gia program
    """
    
    REQUIREMENTS = {
        ProgramType.NURTURE_CAMPAIGN: {
            'min_state': UserState.REGISTERED,
            'max_state': UserState.REGISTERED,
            'max_referrals': 1,
        },
        
        ProgramType.ONBOARDING_7_DAY: {
            'min_state': UserState.VIP,
            'activation_required': False,  # Can start before activation
        },
        
        ProgramType.ADVANCED_WORKSHOP: {
            'min_state': UserState.VIP,
            'certificate_required': True,
            'activation_required': True,
        },
        
        ProgramType.MENTOR_PROGRAM: {
            'min_state': UserState.SUPER_VIP,
            'min_referrals': 50,
        },
        
        ProgramType.AFFILIATE_PROGRAM: {
            'min_state': UserState.SUPER_VIP,
            'revenue_share_enabled': True,
        },
        
        ProgramType.REACTIVATION: {
            'min_state': UserState.VIP,
            'days_inactive': 14,
        }
    }
    
    @classmethod
    def can_join(cls, program: ProgramType, user) -> bool:
        """
        Kiểm tra user có đủ điều kiện join program không
        
        Args:
            program: Program type
            user: User object
            
        Returns:
            bool: True if eligible
        """
        reqs = cls.REQUIREMENTS.get(program, {})
        
        # Check state
        if 'min_state' in reqs:
            if not cls._compare_states(user.user_state, reqs['min_state'], '>='):
                return False
        
        if 'max_state' in reqs:
            if not cls._compare_states(user.user_state, reqs['max_state'], '<='):
                return False
        
        # Check referrals
        if 'min_referrals' in reqs:
            if user.referral_count < reqs['min_referrals']:
                return False
        
        if 'max_referrals' in reqs:
            if user.referral_count > reqs['max_referrals']:
                return False
        
        # Check flags
        if reqs.get('certificate_required') and not user.certificate_issued:
            return False
        
        if reqs.get('activation_required') and user.activation_status != 'COMPLETED':
            return False
        
        if reqs.get('revenue_share_enabled') and not user.revenue_share_enabled:
            return False
        
        return True
    
    @staticmethod
    def _compare_states(state1: str, state2: UserState, operator: str) -> bool:
        """Compare states (hierarchy: VISITOR < REGISTERED < VIP < SUPER_VIP < ADVOCATE)"""
        
        hierarchy = {
            'VISITOR': 0,
            'REGISTERED': 1,
            'VIP': 2,
            'SUPER_VIP': 3,
            'ADVOCATE': 4,
            'CHURNED': -1
        }
        
        val1 = hierarchy.get(state1, 0)
        val2 = hierarchy.get(state2.value, 0)
        
        if operator == '>=':
            return val1 >= val2
        elif operator == '<=':
            return val1 <= val2
        elif operator == '>':
            return val1 > val2
        elif operator == '<':
            return val1 < val2
        elif operator == '==':
            return val1 == val2
        
        return False


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    
    # Example 1: Check state transition
    print("=== State Transition Validation ===")
    
    can_upgrade = StateMachine.is_valid_transition(
        UserState.REGISTERED,
        UserState.VIP
    )
    print(f"REGISTERED → VIP: {can_upgrade}")  # True
    
    invalid_jump = StateMachine.is_valid_transition(
        UserState.REGISTERED,
        UserState.SUPER_VIP
    )
    print(f"REGISTERED → SUPER_VIP: {invalid_jump}")  # False (must go through VIP)
    
    
    # Example 2: Program eligibility
    print("\n=== Program Eligibility ===")
    
    class MockUser:
        def __init__(self):
            self.user_state = 'VIP'
            self.referral_count = 5
            self.certificate_issued = False
            self.activation_status = 'COMPLETED'
            self.revenue_share_enabled = False
    
    user = MockUser()
    
    can_onboard = ProgramRequirements.can_join(ProgramType.ONBOARDING_7_DAY, user)
    print(f"VIP can join ONBOARDING_7_DAY: {can_onboard}")  # True
    
    can_mentor = ProgramRequirements.can_join(ProgramType.MENTOR_PROGRAM, user)
    print(f"VIP (5 refs) can join MENTOR_PROGRAM: {can_mentor}")  # False (need 50 refs)
    
    
    # Example 3: Get possible transitions
    print("\n=== Possible Next States ===")
    
    next_states = StateMachine.get_next_states(UserState.SUPER_VIP)
    print(f"From SUPER_VIP, can go to: {[s.value for s in next_states]}")
    # ['ADVOCATE', 'VIP', 'CHURNED']

