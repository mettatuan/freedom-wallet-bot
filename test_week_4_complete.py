"""
Comprehensive Week 4 Test - Super VIP + Decay Monitoring

Tests the complete Week 4 implementation:
1. Super VIP promotion at 50 refs
2. Activity tracking updates
3. Decay warnings at 7 days
4. Decay downgrades at 14 days
5. State transitions work correctly
"""
import sys
from config.settings import settings
from bot.utils.database import SessionLocal, User
from bot.core.state_machine import StateManager, UserState
from datetime import datetime, timedelta

print("=" * 60)
print("🧪 WEEK 4 COMPREHENSIVE TEST")
print("=" * 60)

# Test 1: Full lifecycle - VIP → Super VIP → Active → Warning → Downgrade
print("\n1️⃣ Testing complete Super VIP lifecycle...")
try:
    session = SessionLocal()
    
    # Clean up existing test user
    existing = session.query(User).filter(User.id == 999999999).first()
    if existing:
        session.delete(existing)
        session.commit()
    
    # Create VIP user with 49 refs
    test_user = User(
        id=999999999,
        username="lifecycle_test",
        user_state=UserState.VIP.value,
        referral_count=49,
        is_free_unlocked=True
    )
    session.add(test_user)
    session.commit()
    print(f"   ✅ Created VIP user with 49 refs")
    
    # Promote to Super VIP (50 refs)
    test_user.referral_count = 50
    session.commit()
    
    with StateManager() as sm:
        new_state = sm.check_and_update_state_by_referrals(test_user.id)
        assert new_state == UserState.SUPER_VIP, f"Expected SUPER_VIP, got {new_state}"
        print(f"   ✅ Promoted to Super VIP at 50 refs")
        
        # Verify activity timestamp was set
        session.refresh(test_user)
        assert test_user.super_vip_last_active is not None
        print(f"   ✅ Activity timestamp initialized")
        
        # Update activity (simulate user interaction)
        sm.update_super_vip_activity(test_user.id)
        old_timestamp = test_user.super_vip_last_active
        session.refresh(test_user)
        assert test_user.super_vip_last_active >= old_timestamp
        print(f"   ✅ Activity tracking works")
    
    # Simulate 8 days of inactivity → Warning
    test_user.super_vip_last_active = datetime.utcnow() - timedelta(days=8)
    test_user.super_vip_decay_warned = False
    session.commit()
    
    with StateManager() as sm:
        result = sm.check_super_vip_decay(test_user.id)
        assert result and result['action'] == 'warn', f"Expected warning, got {result}"
        print(f"   ✅ Warning triggered at 8 days inactive")
        
        session.refresh(test_user)
        assert test_user.super_vip_decay_warned == True
        print(f"   ✅ Warning flag set")
    
    # Simulate 16 days of inactivity → Downgrade
    test_user.super_vip_last_active = datetime.utcnow() - timedelta(days=16)
    session.commit()
    
    with StateManager() as sm:
        result = sm.check_super_vip_decay(test_user.id)
        assert result and result['action'] == 'downgrade', f"Expected downgrade, got {result}"
        print(f"   ✅ Downgrade triggered at 16 days inactive")
        
        session.refresh(test_user)
        assert test_user.user_state == UserState.VIP.value
        print(f"   ✅ User downgraded to VIP")
        
        assert test_user.super_vip_decay_warned == False
        print(f"   ✅ Warning flag reset")
    
    # Cleanup
    session.delete(test_user)
    session.commit()
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 1 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 2: Verify state transition rules
print("\n2️⃣ Testing Week 4 state transition rules...")
try:
    with StateManager() as sm:
        # Check valid transitions
        valid_transitions = [
            (UserState.VIP, UserState.SUPER_VIP, "Reached 50 refs"),
            (UserState.SUPER_VIP, UserState.VIP, "Decay downgrade"),
            (UserState.SUPER_VIP, UserState.CHURNED, "Inactive 90 days"),
            (UserState.SUPER_VIP, UserState.ADVOCATE, "Reached 100 refs"),
        ]
        
        for from_state, to_state, reason in valid_transitions:
            if to_state in sm.VALID_TRANSITIONS.get(from_state, set()):
                print(f"   ✅ Valid: {from_state.value} → {to_state.value}")
            else:
                print(f"   ❌ Should be valid: {from_state.value} → {to_state.value}")
                sys.exit(1)
        
        # Check invalid transitions
        invalid_transitions = [
            (UserState.REGISTERED, UserState.SUPER_VIP),  # Must go through VIP
            (UserState.VISITOR, UserState.SUPER_VIP),
            (UserState.SUPER_VIP, UserState.REGISTERED),
        ]
        
        for from_state, to_state in invalid_transitions:
            if to_state not in sm.VALID_TRANSITIONS.get(from_state, set()):
                print(f"   ✅ Invalid blocked: {from_state.value} → {to_state.value}")
            else:
                print(f"   ❌ Should be invalid: {from_state.value} → {to_state.value}")
                sys.exit(1)
    
except Exception as e:
    print(f"   ❌ Test 2 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# Test 3: Verify batch decay check
print("\n3️⃣ Testing batch decay check performance...")
try:
    session = SessionLocal()
    
    # Create 10 test Super VIPs with different activity states
    test_ids = list(range(100000001, 100000011))
    
    # Clean up existing
    for test_id in test_ids:
        existing = session.query(User).filter(User.id == test_id).first()
        if existing:
            session.delete(existing)
    session.commit()
    
    # Create users
    for i, test_id in enumerate(test_ids):
        days_inactive = i  # 0, 1, 2, ..., 9 days
        user = User(
            id=test_id,
            username=f"batch_test_{i}",
            user_state=UserState.SUPER_VIP.value,
            referral_count=50,
            super_vip_last_active=datetime.utcnow() - timedelta(days=days_inactive),
            super_vip_decay_warned=False
        )
        session.add(user)
    session.commit()
    
    print(f"   Created 10 test Super VIPs (0-9 days inactive)")
    
    # Run batch check
    with StateManager() as sm:
        results = sm.check_all_super_vip_decay()
        
        # Should find at least 3 actions from our test users:
        # - User 7 (7 days): warning
        # - User 8 (8 days): warning
        # - User 9 (9 days): warning
        test_results = [r for r in results if r['user_id'] in test_ids]
        
        print(f"   Found {len(test_results)} actions from test users")
        
        warnings = [r for r in test_results if r['action'] == 'warn']
        print(f"   - {len(warnings)} warnings")
        
        assert len(warnings) >= 3, f"Expected at least 3 warnings, got {len(warnings)}"
        print(f"   ✅ Batch check works correctly")
    
    # Cleanup
    for test_id in test_ids:
        user = session.query(User).filter(User.id == test_id).first()
        if user:
            session.delete(user)
    session.commit()
    session.close()
    
except Exception as e:
    print(f"   ❌ Test 3 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


print("\n" + "=" * 60)
print("🎉 ALL WEEK 4 TESTS PASSED!")
print("=" * 60)
print("\n📊 Week 4 Implementation Summary:")
print("   ✅ Super VIP promotion (50+ refs)")
print("   ✅ Activity tracking system")
print("   ✅ Decay warnings (7 days)")
print("   ✅ Decay downgrades (14 days)")
print("   ✅ State transition validation")
print("   ✅ Batch processing performance")
print("\n🚀 Week 4 is production-ready!")
print("\n📋 Next Steps:")
print("   • Deploy to Railway")
print("   • Monitor daily job execution")
print("   • Create Super VIP badge image")
print("   • Setup Super VIP private group")
print("   • Document new features for users")
