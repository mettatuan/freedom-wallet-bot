"""
Test Super VIP Promotion (Week 4)

Tests:
1. Super VIP promotion at 50 referrals
2. Activity tracking updates
3. State transitions work correctly
"""
import sys
from config.settings import settings
from bot.utils.database import SessionLocal, User
from bot.core.state_machine import StateManager, UserState
from datetime import datetime, timedelta

print("=" * 60)
print("🧪 SUPER VIP PROMOTION TEST (WEEK 4)")
print("=" * 60)

# Test 1: Create test user with 49 refs (VIP)
print("\n1️⃣ Testing user with 49 refs (should be VIP)...")
try:
    session = SessionLocal()
    
    # Clean up existing test user
    existing = session.query(User).filter(User.id == 111111111).first()
    if existing:
        session.delete(existing)
        session.commit()
    
    test_user = User(
        id=111111111,
        username="test_super_vip",
        user_state=UserState.VIP.value,
        referral_count=49,
        is_free_unlocked=True
    )
    session.add(test_user)
    session.commit()
    
    with StateManager() as sm:
        state, is_legacy = sm.get_user_state(test_user.id)
        print(f"   ✅ User created: {state.value}, {test_user.referral_count} refs")
        assert state == UserState.VIP, f"Expected VIP, got {state}"
    
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 1 failed: {e}")
    sys.exit(1)


# Test 2: Increment to 50 refs → Should auto-promote to SUPER_VIP
print("\n2️⃣ Testing promotion to Super VIP at 50 refs...")
try:
    session = SessionLocal()
    
    test_user = session.query(User).filter(User.id == 111111111).first()
    test_user.referral_count = 50
    session.commit()
    
    with StateManager() as sm:
        new_state = sm.check_and_update_state_by_referrals(test_user.id)
        
        if new_state == UserState.SUPER_VIP:
            print(f"   ✅ Auto-promoted to SUPER_VIP!")
            
            # Verify state was updated
            session.refresh(test_user)
            assert test_user.user_state == UserState.SUPER_VIP.value
            print(f"   ✅ State in DB: {test_user.user_state}")
            
            # Verify activity timestamp was set
            assert test_user.super_vip_last_active is not None
            print(f"   ✅ Last active: {test_user.super_vip_last_active}")
        else:
            print(f"   ❌ Expected SUPER_VIP promotion, got {new_state}")
            sys.exit(1)
    
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 2 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 3: Update activity timestamp
print("\n3️⃣ Testing activity tracking...")
try:
    session = SessionLocal()
    
    test_user = session.query(User).filter(User.id == 111111111).first()
    
    # Set old timestamp
    old_time = datetime.utcnow() - timedelta(days=5)
    test_user.super_vip_last_active = old_time
    test_user.super_vip_decay_warned = True
    session.commit()
    
    print(f"   Old timestamp: {old_time}")
    
    # Update activity
    with StateManager() as sm:
        success = sm.update_super_vip_activity(test_user.id)
        assert success, "Activity update failed"
    
    # Verify update
    session.refresh(test_user)
    assert test_user.super_vip_last_active > old_time
    assert test_user.super_vip_decay_warned == False
    print(f"   ✅ Activity updated to: {test_user.super_vip_last_active}")
    print(f"   ✅ Warning flag reset: {test_user.super_vip_decay_warned}")
    
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 3 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 4: Verify state transitions still work
print("\n4️⃣ Testing state transition validation...")
try:
    with StateManager() as sm:
        # Valid: SUPER_VIP → CHURNED
        ok, msg = sm.transition_user(111111111, UserState.CHURNED, "Test churn")
        assert ok, f"Valid transition failed: {msg}"
        print(f"   ✅ Valid transition: SUPER_VIP → CHURNED")
        
        # Valid: CHURNED → REGISTERED (reactivation)
        ok, msg = sm.transition_user(111111111, UserState.REGISTERED, "Test reactivate")
        assert ok, f"Valid transition failed: {msg}"
        print(f"   ✅ Valid transition: CHURNED → REGISTERED")
        
        # Invalid: REGISTERED → SUPER_VIP (must go through VIP first)
        ok, msg = sm.transition_user(111111111, UserState.SUPER_VIP, "Test invalid")
        assert not ok, "Invalid transition should fail"
        print(f"   ✅ Invalid transition blocked: {msg}")
    
except Exception as e:
    print(f"   ❌ Test 4 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 5: Verify promotion doesn't happen for users with < 50 refs
print("\n5️⃣ Testing no promotion for < 50 refs...")
try:
    session = SessionLocal()
    
    # Create user with 25 refs
    test_user2 = User(
        id=222222222,
        username="test_not_super",
        user_state=UserState.VIP.value,
        referral_count=25
    )
    session.add(test_user2)
    session.commit()
    
    with StateManager() as sm:
        new_state = sm.check_and_update_state_by_referrals(test_user2.id)
        
        if new_state:
            print(f"   ❌ Unexpected promotion: {new_state}")
            sys.exit(1)
        else:
            print(f"   ✅ No promotion (correct - only 25 refs)")
    
    # Cleanup
    session.delete(test_user2)
    session.commit()
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 5 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Cleanup
print("\n🧹 Cleaning up test data...")
try:
    session = SessionLocal()
    test_user = session.query(User).filter(User.id == 111111111).first()
    if test_user:
        session.delete(test_user)
        session.commit()
    session.close()
    print("   ✅ Test user deleted")
except Exception as e:
    print(f"   ⚠️  Cleanup warning: {e}")


print("\n" + "=" * 60)
print("🎉 ALL SUPER VIP TESTS PASSED!")
print("=" * 60)
print("\n📊 Summary:")
print("   ✅ Super VIP promotion at 50 refs works")
print("   ✅ Activity tracking updates correctly")
print("   ✅ State transitions validated")
print("   ✅ No false promotions for < 50 refs")
print("\n🚀 Week 4 Super VIP feature is ready!")
