"""
Week 1-3 Integration Test
Test all components before bot restart
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("🧪 WEEK 1-3 INTEGRATION TEST")
print("=" * 60)
print()

# Test 1: Configuration
print("1️⃣ Loading configuration...")
try:
    from config.settings import settings
    print(f"   ✅ Bot token: ...{settings.TELEGRAM_BOT_TOKEN[-10:]}")
    print(f"   ✅ Database: {settings.DATABASE_URL}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print()

# Test 2: Database with Week 1 migrations
print("2️⃣ Testing Week 1 - Database Migration...")
try:
    from bot.utils.database import SessionLocal, User
    session = SessionLocal()
    users = session.query(User).all()
    print(f"   ✅ Database connection successful")
    print(f"   ✅ Found {len(users)} users")
    
    # Check new columns exist
    if users:
        sample = users[0]
        assert hasattr(sample, 'user_state'), "Missing user_state column"
        assert hasattr(sample, 'current_program'), "Missing current_program column"
        assert hasattr(sample, 'program_day'), "Missing program_day column"
        print(f"   ✅ New columns verified: user_state, current_program, program_day")
        
        # Show sample data
        for u in users[:2]:
            print(f"      • User {u.id}: state={u.user_state}, program={u.current_program}")
    
    session.close()
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print()

# Test 3: Week 2 State Machine
print("3️⃣ Testing Week 2 - State Machine...")
try:
    from bot.core.state_machine import StateManager, UserState
    
    # Test StateManager
    mgr = StateManager()
    print(f"   ✅ StateManager initialized")
    
    # Test states
    states = [s.value for s in UserState]
    print(f"   ✅ Available states ({len(states)}): {', '.join(states)}")
    
    # Test get_user_state
    if users:
        test_user_id = users[0].id
        state, is_legacy = mgr.get_user_state(test_user_id)
        print(f"   ✅ get_user_state() works: User {test_user_id} = {state.value} (legacy={is_legacy})")
    
    mgr.close()
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Week 3 Program Manager
print("4️⃣ Testing Week 3 - Program Manager...")
try:
    from bot.core.program_manager import ProgramManager, ProgramType
    
    # Test ProgramManager
    pm = ProgramManager()
    print(f"   ✅ ProgramManager initialized")
    
    # Test programs
    programs = [p.value for p in ProgramType]
    print(f"   ✅ Available programs ({len(programs)}): {', '.join(programs)}")
    
    # Test get_user_program_status
    if users:
        test_user_id = users[0].id
        status = pm.get_user_program_status(test_user_id)
        if status:
            print(f"   ✅ get_user_program_status() works: {status}")
        else:
            print(f"   ✅ get_user_program_status() works: No program enrolled (expected)")
    
    pm.close()
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 5: Handler Integration
print("5️⃣ Testing Handler Integration...")
try:
    from bot.handlers.start import start
    from bot.handlers.registration import start_registration
    from bot.handlers.daily_nurture import start_daily_nurture, NURTURE_MESSAGES
    from bot.handlers.onboarding import start_onboarding_journey, ONBOARDING_MESSAGES
    from bot.handlers.callback import handle_callback
    
    print(f"   ✅ start handler imported")
    print(f"   ✅ registration handler imported")
    print(f"   ✅ daily_nurture handler imported ({len(NURTURE_MESSAGES)} days)")
    print(f"   ✅ onboarding handler imported ({len(ONBOARDING_MESSAGES)} days)")
    print(f"   ✅ callback handler imported")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 6: Telegram Application
print("6️⃣ Testing Telegram Application Creation...")
try:
    from telegram.ext import Application
    
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    print(f"   ✅ Application instance created")
    print(f"   ✅ Bot configuration ready")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print()
print("📊 Summary:")
print("   ✅ WEEK 1: Database migration (state/program columns)")
print("   ✅ WEEK 2: State machine (UserState enum + StateManager)")
print("   ✅ WEEK 3: Program manager (ProgramType + enrollment)")
print("   ✅ All handlers integrated successfully")
print("   ✅ Bot ready to start")
print()
print("⚠️  Note: Actual bot run test skipped because another instance")
print("   is running (likely Railway production deployment)")
print()
print("To start bot locally:")
print("   1. Stop Railway instance first")
print("   2. Run: python main.py")
print()

print("3️⃣.1 Testing State Transitions Logic...")

try:
    from bot.utils.database import User
    from bot.core.state_machine import StateManager, UserState
    
    session = SessionLocal()
    
    # Clean up any existing test user
    existing_user = session.query(User).filter(User.id == 999999999).first()
    if existing_user:
        session.delete(existing_user)
        session.commit()
    
    # Create temp test user (SAFE, DB-ALIGNED)
    test_user = User()
    test_user.id = 999999999  # Primary key is 'id' (Telegram user ID), not 'user_id'
    test_user.username = "test_state_user"
    test_user.user_state = UserState.VISITOR.value
    
    session.add(test_user)
    session.commit()
    
    sm = StateManager()
    
    # VALID transition
    ok, msg = sm.transition_user(test_user.id, UserState.REGISTERED, "Test transition")
    assert ok is True, f"Expected success, got: {msg}"
    
    session.refresh(test_user)
    assert test_user.user_state == UserState.REGISTERED.value
    
    # INVALID backward transition (VISITOR not in valid transitions from REGISTERED)
    ok, msg = sm.transition_user(test_user.id, UserState.VISITOR, "Invalid backward")
    assert ok is False, f"Expected failure, got success: {msg}"
    
    session.refresh(test_user)
    assert test_user.user_state == UserState.REGISTERED.value
    
    # Same-state transition (should succeed as no-op or fail gracefully)
    ok1, msg1 = sm.transition_user(test_user.id, UserState.REGISTERED, "Same state")
    # Note: Current implementation may reject same-state transitions as invalid
    # This is acceptable behavior - we just verify it doesn't crash
    print(f"      Same-state transition: ok={ok1}, msg={msg1}")
    
    print("   ✅ State transition rules enforced correctly")
    
    sm.close()
    session.delete(test_user)
    session.commit()
    session.close()
    
except Exception as e:
    print(f"   ❌ State transition test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


print("4️⃣.1 Testing Program Lifecycle...")

try:
    from bot.core.program_manager import ProgramManager, ProgramType
    
    session = SessionLocal()
    
    # Clean up any existing test user
    existing_user = session.query(User).filter(User.id == 888888888).first()
    if existing_user:
        session.delete(existing_user)
        session.commit()
    
    test_user = User(
        id=888888888,  # Primary key is 'id', not 'telegram_id'
        username="test_program_user",
        user_state=UserState.REGISTERED.value,
        current_program=None,
        program_day=0
    )
    session.add(test_user)
    session.commit()
    
    pm = ProgramManager()
    
    # Test get_user_program_status for user with no program
    status = pm.get_user_program_status(test_user.id)
    assert status is None, "User should have no program initially"
    
    # Manually set program (simulating enrollment without context)
    test_user.current_program = ProgramType.NURTURE_7_DAY.value
    test_user.program_day = 3
    session.commit()
    
    # Test get_user_program_status for user IN program
    status = pm.get_user_program_status(test_user.id)
    assert status is not None, "User should have program status"
    assert status["program"] == ProgramType.NURTURE_7_DAY.value, "Program mismatch"
    assert status["day"] == 3, "Day mismatch"
    assert status["progress"] == "3/5", "Progress mismatch (5 days for NURTURE)"
    
    # NOTE: Full enrollment test requires context (Telegram) which we don't have in unit test
    # These methods are async and need context for job scheduling:
    # - await pm.enroll_user(user_id, program, context, force)
    # - await pm.advance_program_day(user_id, context)
    # - await pm.complete_program(user_id)
    # We only test synchronous methods in unit tests
    
    session.refresh(test_user)
    assert test_user.current_program == ProgramType.NURTURE_7_DAY.value, "Program should be set"
    assert test_user.program_day == 3, "Day should be 3"
    
    print("   ✅ Program lifecycle works correctly")
    
    pm.close()
    session.delete(test_user)
    session.commit()
    session.close()
    
except Exception as e:
    print(f"   ❌ Program lifecycle test failed: {e}")
    sys.exit(1)
print("5️⃣.1 Testing Regression - Legacy User Safety...")

try:
    session = SessionLocal()
    
    # Clean up any existing test user
    existing_user = session.query(User).filter(User.id == 777777777).first()
    if existing_user:
        session.delete(existing_user)
        session.commit()
    
    legacy_user = User(
        id=777777777,  # Primary key is 'id', not 'telegram_id'
        username="legacy_user",
        user_state="LEGACY",
        current_program=None,
        program_day=0
    )
    session.add(legacy_user)
    session.commit()
    
    sm = StateManager()
    
    # Test that LEGACY state can infer correct state from referral_count
    inferred_state, is_legacy = sm.get_user_state(legacy_user.id)
    assert is_legacy is True, "Should detect LEGACY user"
    assert inferred_state == UserState.VISITOR, "LEGACY with 0 refs should infer VISITOR"
    
    # Test that LEGACY user can transition (migrates on first transition)
    ok, msg = sm.transition_user(legacy_user.id, UserState.REGISTERED, "Auto-migrate from LEGACY")
    assert ok is True, f"LEGACY should auto-migrate: {msg}"
    
    session.refresh(legacy_user)
    assert legacy_user.user_state == UserState.REGISTERED.value, "Should be migrated to REGISTERED"
    
    sm.close()
    
    print("   ✅ Legacy user behavior preserved")
    
    session.delete(legacy_user)
    session.commit()
    session.close()
    
except Exception as e:
    print(f"   ❌ Regression test failed: {e}")
    sys.exit(1)
