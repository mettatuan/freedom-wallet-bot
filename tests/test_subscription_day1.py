"""
Test Subscription System - Day 1
Quick test to verify usage tracking works
"""
from bot.utils.database import User, get_user_by_id, SessionLocal
from bot.core.subscription import SubscriptionManager, SubscriptionTier
from datetime import datetime, date

def test_subscription_system():
    """Test basic subscription functions"""
    print("=" * 50)
    print("TESTING SUBSCRIPTION SYSTEM")
    print("=" * 50)
    
    # Get first user from database
    db = SessionLocal()
    user = db.query(User).first()
    
    if not user:
        print("❌ No users in database. Create a user first.")
        return
    
    print(f"\n📊 Testing with user: {user.username} (ID: {user.id})")
    
    # Test 1: Get user tier
    print("\n1️⃣ GET USER TIER:")
    tier = SubscriptionManager.get_user_tier(user)
    print(f"   Tier: {tier.value}")
    print(f"   Is Premium: {SubscriptionManager.is_premium(user)}")
    
    # Test 2: Message limit check
    print("\n2️⃣ MESSAGE LIMIT CHECK:")
    can_send, msg = SubscriptionManager.can_send_message(user)
    print(f"   Can send: {can_send}")
    if msg:
        print(f"   Message: {msg}")
    
    remaining = SubscriptionManager.get_remaining_messages(user)
    print(f"   Remaining: {remaining}/{SubscriptionManager.FREE_DAILY_MESSAGES}")
    
    # Test 3: Simulate message sending
    print("\n3️⃣ SIMULATE 3 MESSAGES:")
    for i in range(3):
        SubscriptionManager.increment_message_count(user)
        remaining = SubscriptionManager.get_remaining_messages(user)
        print(f"   Message {i+1} sent. Remaining: {remaining}")
    
    # Test 4: Start trial
    print("\n4️⃣ START TRIAL:")
    try:
        SubscriptionManager.start_trial(user, days=7)
        print(f"   ✅ Trial started!")
        print(f"   Trial ends: {user.trial_ends_at}")
        print(f"   New tier: {SubscriptionManager.get_user_tier(user).value}")
    except Exception as e:
        print(f"   ⚠️ Trial start skipped (may already be on trial)")
    
    # Test 5: Check unlimited access
    print("\n5️⃣ CHECK UNLIMITED ACCESS:")
    can_send, msg = SubscriptionManager.can_send_message(user)
    print(f"   Can send (on trial): {can_send}")
    remaining = SubscriptionManager.get_remaining_messages(user)
    print(f"   Remaining: {remaining} (should be 999999)")
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 50)
    
    db.close()

if __name__ == "__main__":
    test_subscription_system()
