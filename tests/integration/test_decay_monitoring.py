"""
Test Super VIP Decay Monitoring (Week 4)

Tests:
1. No action for active Super VIP (< 7 days)
2. Warning for 7+ days inactive
3. Downgrade for 14+ days inactive
4. Don't warn twice
5. Batch check all Super VIPs
"""
import sys
from config.settings import settings
from bot.utils.database import SessionLocal, User
from bot.core.state_machine import StateManager, UserState
from datetime import datetime, timedelta

print("=" * 60)
print("🧪 SUPER VIP DECAY MONITORING TEST (WEEK 4)")
print("=" * 60)

# Test 1: Active Super VIP (< 7 days) - No action
print("\n1️⃣ Testing active Super VIP (< 7 days)...")
try:
    session = SessionLocal()
    
    # Clean up existing test users
    for test_id in [111111111, 222222222, 333333333]:
        existing = session.query(User).filter(User.id == test_id).first()
        if existing:
            session.delete(existing)
    session.commit()
    
    # Create active Super VIP (last active 3 days ago)
    active_user = User(
        id=111111111,
        username="active_super_vip",
        user_state=UserState.SUPER_VIP.value,
        referral_count=50,
        super_vip_last_active=datetime.utcnow() - timedelta(days=3),
        super_vip_decay_warned=False
    )
    session.add(active_user)
    session.commit()
    
    with StateManager() as sm:
        result = sm.check_super_vip_decay(active_user.id)
        
        if result is None:
            print(f"   ✅ No decay action (correct - only 3 days inactive)")
        else:
            print(f"   ❌ Unexpected action: {result}")
            sys.exit(1)
    
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 1 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 2: Warning for 7+ days inactive
print("\n2️⃣ Testing decay warning (7 days inactive)...")
try:
    session = SessionLocal()
    
    # Create Super VIP inactive for 8 days
    warning_user = User(
        id=222222222,
        username="warning_super_vip",
        user_state=UserState.SUPER_VIP.value,
        referral_count=50,
        super_vip_last_active=datetime.utcnow() - timedelta(days=8),
        super_vip_decay_warned=False
    )
    session.add(warning_user)
    session.commit()
    
    with StateManager() as sm:
        result = sm.check_super_vip_decay(warning_user.id)
        
        if result and result['action'] == 'warn':
            print(f"   ✅ Warning triggered: {result['days_inactive']} days inactive")
            
            # Verify warning flag was set
            session.refresh(warning_user)
            assert warning_user.super_vip_decay_warned == True
            print(f"   ✅ Warning flag set in DB")
        else:
            print(f"   ❌ Expected warning, got: {result}")
            sys.exit(1)
    
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 2 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 3: Don't warn twice
print("\n3️⃣ Testing no duplicate warnings...")
try:
    session = SessionLocal()
    
    warning_user = session.query(User).filter(User.id == 222222222).first()
    
    with StateManager() as sm:
        result = sm.check_super_vip_decay(warning_user.id)
        
        if result is None:
            print(f"   ✅ No action (correct - already warned)")
        else:
            print(f"   ❌ Should not warn twice, got: {result}")
            sys.exit(1)
    
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 3 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 4: Downgrade for 14+ days inactive
print("\n4️⃣ Testing downgrade (14 days inactive)...")
try:
    session = SessionLocal()
    
    # Create Super VIP inactive for 15 days
    downgrade_user = User(
        id=333333333,
        username="downgrade_super_vip",
        user_state=UserState.SUPER_VIP.value,
        referral_count=50,
        super_vip_last_active=datetime.utcnow() - timedelta(days=15),
        super_vip_decay_warned=True  # Already warned
    )
    session.add(downgrade_user)
    session.commit()
    
    with StateManager() as sm:
        result = sm.check_super_vip_decay(downgrade_user.id)
        
        if result and result['action'] == 'downgrade':
            print(f"   ✅ Downgrade triggered: {result['days_inactive']} days inactive")
            
            # Verify user was downgraded to VIP
            session.refresh(downgrade_user)
            assert downgrade_user.user_state == UserState.VIP.value
            print(f"   ✅ User downgraded to: {downgrade_user.user_state}")
            
            # Verify warning flag was reset
            assert downgrade_user.super_vip_decay_warned == False
            print(f"   ✅ Warning flag reset")
        else:
            print(f"   ❌ Expected downgrade, got: {result}")
            sys.exit(1)
    
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 4 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 5: Batch check all Super VIPs
print("\n5️⃣ Testing batch check all Super VIPs...")
try:
    session = SessionLocal()
    
    # Create multiple Super VIPs with different statuses
    users = [
        # Active (no action)
        User(
            id=444444444,
            username="active1",
            user_state=UserState.SUPER_VIP.value,
            referral_count=50,
            super_vip_last_active=datetime.utcnow() - timedelta(days=2),
            super_vip_decay_warned=False
        ),
        # Need warning
        User(
            id=555555555,
            username="warn1",
            user_state=UserState.SUPER_VIP.value,
            referral_count=50,
            super_vip_last_active=datetime.utcnow() - timedelta(days=9),
            super_vip_decay_warned=False
        ),
        # Need downgrade
        User(
            id=666666666,
            username="downgrade1",
            user_state=UserState.SUPER_VIP.value,
            referral_count=50,
            super_vip_last_active=datetime.utcnow() - timedelta(days=16),
            super_vip_decay_warned=True
        ),
    ]
    
    for user in users:
        # Clean up if exists
        existing = session.query(User).filter(User.id == user.id).first()
        if existing:
            session.delete(existing)
    session.commit()
    
    for user in users:
        session.add(user)
    session.commit()
    
    with StateManager() as sm:
        results = sm.check_all_super_vip_decay()
        
        print(f"   Found {len(results)} decay actions:")
        
        # Should have 2 actions: 1 warning + 1 downgrade
        # (active user should not trigger action)
        warns = [r for r in results if r['action'] == 'warn']
        downgrades = [r for r in results if r['action'] == 'downgrade']
        
        print(f"   - {len(warns)} warnings")
        print(f"   - {len(downgrades)} downgrades")
        
        # Note: may have more than expected if there are real Super VIPs in DB
        # Just verify we got at least our test cases
        assert len(warns) >= 1, f"Expected at least 1 warning, got {len(warns)}"
        assert len(downgrades) >= 1, f"Expected at least 1 downgrade, got {len(downgrades)}"
        
        print(f"   ✅ Batch check works correctly")
    
    # Cleanup batch test users
    for user_id in [444444444, 555555555, 666666666]:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            session.delete(user)
    session.commit()
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 5 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Cleanup all test users
print("\n🧹 Cleaning up test data...")
try:
    session = SessionLocal()
    for test_id in [111111111, 222222222, 333333333, 444444444, 555555555, 666666666]:
        user = session.query(User).filter(User.id == test_id).first()
        if user:
            session.delete(user)
    session.commit()
    session.close()
    print("   ✅ All test users deleted")
except Exception as e:
    print(f"   ⚠️  Cleanup warning: {e}")


print("\n" + "=" * 60)
print("🎉 ALL DECAY MONITORING TESTS PASSED!")
print("=" * 60)
print("\n📊 Summary:")
print("   ✅ Active users not affected (< 7 days)")
print("   ✅ Warning sent at 7+ days inactive")
print("   ✅ No duplicate warnings")
print("   ✅ Downgrade at 14+ days inactive")
print("   ✅ Batch check processes all Super VIPs")
print("\n🚀 Week 4 Decay Monitoring is ready!")
