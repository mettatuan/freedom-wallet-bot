"""
Recommendation Engine - Rule-based (Week 1)
Generates personalized suggestions for Premium users

Core principle: "Náº¿u tÃ´i lÃ  trá»£ lÃ½ cá»§a báº¡n, lÃºc nÃ y tÃ´i khuyÃªn báº¡n lÃ m viá»‡c nÃ y."
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from loguru import logger
from app.utils.database import get_user_by_id


class RecommendationEngine:
    """
    Rule-based recommendation engine for Premium users
    
    Rules priority:
    1. ChÆ°a ghi hÃ´m nay (10AM-9PM) â†’ Nháº¯c ghi chi tiÃªu
    2. Cuá»‘i ngÃ y (9PM-11PM) â†’ TÃ³m táº¯t ngÃ y hÃ´m nay
    3. Äáº§u tuáº§n (Monday morning) â†’ PhÃ¢n tÃ­ch tuáº§n trÆ°á»›c
    4. Cuá»‘i thÃ¡ng (Last 3 days) â†’ PhÃ¢n tÃ­ch thÃ¡ng
    5. Default â†’ Khuyáº¿n khÃ­ch duy trÃ¬ streak
    """
    
    @staticmethod
    def get_recommendation(user_id: int) -> Dict[str, str]:
        """
        Get personalized recommendation for user
        
        Returns:
            {
                'title': 'Gá»£i Ã½ cho báº¡n',
                'message': 'Chi tiáº¿t gá»£i Ã½',
                'action': 'callback_data',
                'emoji': 'ðŸŽ¯'
            }
        """
        user = get_user_by_id(user_id)
        
        if not user:
            return RecommendationEngine._default_recommendation()
        
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()  # 0=Monday, 6=Sunday
        day_of_month = now.day
        
        # Check if user recorded today
        recorded_today = RecommendationEngine._check_recorded_today(user)
        
        # Rule 1: ChÆ°a ghi hÃ´m nay (10AM-9PM)
        if not recorded_today and 10 <= hour < 21:
            return {
                'title': 'ðŸ’¡ ÄÃ£ ghi chi tiÃªu hÃ´m nay chÆ°a?',
                'message': (
                    f"ðŸ‘‹ ChÃ o {user.full_name or user.username}!\n\n"
                    f"ðŸ“ HÃ´m nay báº¡n chÆ°a ghi giao dá»‹ch nÃ o.\n\n"
                    f"Ghi ngay Ä‘á»ƒ giá»¯ streak {user.streak_count if user else 0} ngÃ y! ðŸ”¥"
                ),
                'action': 'quick_record',
                'emoji': 'ðŸ“'
            }
        
        # Rule 2: Cuá»‘i ngÃ y (9PM-11PM)
        if 21 <= hour < 23:
            return {
                'title': 'ðŸŒ™ TÃ³m táº¯t ngÃ y hÃ´m nay',
                'message': (
                    f"NgÃ y hÃ´m nay cá»§a báº¡n:\n\n"
                    f"{'âœ… ÄÃ£ ghi giao dá»‹ch' if recorded_today else 'âš ï¸ ChÆ°a ghi giao dá»‹ch'}\n"
                    f"ðŸ”¥ Streak: {user.streak_count if user else 0} ngÃ y\n\n"
                    f"ðŸ’¡ Báº¡n cÃ³ muá»‘n xem tÃ¬nh hÃ¬nh chi tiÃªu hÃ´m nay?"
                ),
                'action': 'today_summary',
                'emoji': 'ðŸ“Š'
            }
        
        # Rule 3: Äáº§u tuáº§n (Monday 8AM-12PM)
        if day_of_week == 0 and 8 <= hour < 12:
            return {
                'title': 'ðŸ“… Báº¯t Ä‘áº§u tuáº§n má»›i',
                'message': (
                    f"ChÃ o tuáº§n má»›i! ðŸŽ‰\n\n"
                    f"Tuáº§n trÆ°á»›c báº¡n Ä‘Ã£ ghi {user.streak_count if user else 0} ngÃ y liÃªn tá»¥c.\n\n"
                    f"ðŸ’¡ Báº¡n cÃ³ muá»‘n xem phÃ¢n tÃ­ch tuáº§n trÆ°á»›c?"
                ),
                'action': 'last_week_analysis',
                'emoji': 'ðŸ“ˆ'
            }
        
        # Rule 4: Cuá»‘i thÃ¡ng (Last 3 days)
        from calendar import monthrange
        _, last_day = monthrange(now.year, now.month)
        
        if day_of_month >= last_day - 2:
            return {
                'title': 'ðŸ“Š Sáº¯p háº¿t thÃ¡ng rá»“i!',
                'message': (
                    f"ThÃ¡ng {now.month} sáº¯p káº¿t thÃºc.\n\n"
                    f"Báº¡n Ä‘Ã£ ghi {user.streak_count if user else 0} ngÃ y trong thÃ¡ng nÃ y.\n\n"
                    f"ðŸ’¡ Muá»‘n xem phÃ¢n tÃ­ch thÃ¡ng nÃ y khÃ´ng?"
                ),
                'action': 'month_analysis',
                'emoji': 'ðŸ“Š'
            }
        
        # Rule 5: Milestone approaching (e.g., 6/7 days to weekly milestone)
        if user and user.streak_count and user.streak_count % 7 == 6:  # 6, 13, 20, 27...
            return {
                'title': 'ðŸ”¥ Sáº¯p Ä‘áº¡t milestone!',
                'message': (
                    f"Báº¡n Ä‘ang cÃ³ streak {user.streak_count} ngÃ y! ðŸ”¥\n\n"
                    f"Chá»‰ cáº§n 1 ngÃ y ná»¯a lÃ  Ä‘áº¡t milestone {user.streak_count + 1} ngÃ y!\n\n"
                    f"ðŸ’¡ HÃ£y ghi giao dá»‹ch Ä‘á»ƒ giá»¯ streak nhÃ©!"
                ),
                'action': 'quick_record',
                'emoji': 'ðŸŽ¯'
            }
        
        # Default: Encourage streak maintenance
        return RecommendationEngine._default_recommendation(user)
    
    @staticmethod
    def _check_recorded_today(user) -> bool:
        """Check if user has recorded any transaction today"""
        if not user.last_transaction_date:
            return False
        
        today = datetime.now().date()
        last_date = user.last_transaction_date
        
        # Convert to date if datetime
        if isinstance(last_date, datetime):
            last_date = last_date.date()
        
        return last_date == today
    
    @staticmethod
    def _default_recommendation(user=None) -> Dict[str, str]:
        """Default recommendation when no specific rule matches"""
        if user and user.streak_count and user.streak_count > 0:
            return {
                'title': 'ðŸ”¥ Giá»¯ vá»¯ng streak!',
                'message': (
                    f"Báº¡n Ä‘ang cÃ³ streak {user.streak_count} ngÃ y! ðŸ”¥\n\n"
                    f"HÃ£y tiáº¿p tá»¥c ghi chÃ©p Ä‘á»u Ä‘áº·n Ä‘á»ƒ:\n"
                    f"âœ… Náº¯m rÃµ tÃ i chÃ­nh\n"
                    f"âœ… PhÃ¡t hiá»‡n chi tiÃªu lÃ£ng phÃ­\n"
                    f"âœ… Äáº¡t má»¥c tiÃªu tÃ i chÃ­nh\n\n"
                    f"ðŸ’¡ TÃ´i cÃ³ thá»ƒ giÃºp gÃ¬ cho báº¡n hÃ´m nay?"
                ),
                'action': 'main_menu',
                'emoji': 'ðŸ’ª'
            }
        
        return {
            'title': 'ðŸ‘‹ Xin chÃ o!',
            'message': (
                f"TÃ´i lÃ  trá»£ lÃ½ tÃ i chÃ­nh cá»§a báº¡n! ðŸ¤–\n\n"
                f"TÃ´i cÃ³ thá»ƒ giÃºp báº¡n:\n"
                f"ðŸ“ Ghi chi tiÃªu nhanh\n"
                f"ðŸ“Š Xem tÃ¬nh hÃ¬nh tÃ i chÃ­nh\n"
                f"ðŸ§  PhÃ¢n tÃ­ch vÃ  gá»£i Ã½\n\n"
                f"ðŸ’¡ Báº¡n muá»‘n lÃ m gÃ¬?"
            ),
            'action': 'main_menu',
            'emoji': 'ðŸ¤–'
        }


class SmartGreeting:
    """Generate context-aware greetings"""
    
    @staticmethod
    def get_greeting(user) -> str:
        """Get time-appropriate greeting"""
        hour = datetime.now().hour
        name = user.full_name or user.username or "báº¡n"
        
        if 5 <= hour < 12:
            return f"â˜€ï¸ ChÃ o buá»•i sÃ¡ng {name}!"
        elif 12 <= hour < 18:
            return f"ðŸŒ¤ï¸ ChÃ o buá»•i chiá»u {name}!"
        elif 18 <= hour < 22:
            return f"ðŸŒ† ChÃ o buá»•i tá»‘i {name}!"
        else:
            return f"ðŸŒ™ Khuya rá»“i {name}!"


# Quick access functions
def get_recommendation_for_user(user_id: int) -> Dict[str, str]:
    """
    Quick access function to get recommendation
    
    Usage:
        recommendation = get_recommendation_for_user(user_id)
        await update.message.reply_text(
            recommendation['message'],
            reply_markup=create_button(recommendation['action'])
        )
    """
    return RecommendationEngine.get_recommendation(user_id)


def get_greeting(user) -> str:
    """Quick access to smart greeting"""
    return SmartGreeting.get_greeting(user)


if __name__ == "__main__":
    # Test recommendations
    print("Testing recommendation engine...")
    
    # Mock user for testing
    class MockUser:
        def __init__(self):
            self.full_name = "Tháº¯ng"
            self.username = "thang"
            self.current_streak = 5
            self.last_transaction_date = datetime.now() - timedelta(days=1)
    
    user = MockUser()
    rec = RecommendationEngine.get_recommendation(user.id if hasattr(user, 'id') else 123)
    
    print(f"\n{rec['emoji']} {rec['title']}")
    print(f"{rec['message']}")
    print(f"Action: {rec['action']}")

