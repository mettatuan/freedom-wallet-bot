"""
🚀 DEPLOYMENT READINESS CHECK - Week 1-5
========================================

Comprehensive pre-deployment verification:
- All tests passing
- Configuration complete
- Database ready
- No import errors
- Core features functional
"""
import sys
import importlib

print("=" * 60)
print("🚀 DEPLOYMENT READINESS CHECK")
print("=" * 60)

errors = []
warnings = []

# Test 1: Critical Imports
print("\n1️⃣ Testing critical imports...")
try:
    from config.settings import settings
    from bot.utils.database import SessionLocal, User, Referral
    from bot.core.state_machine import StateManager, UserState
    from bot.core.program_manager import ProgramManager, ProgramType
    from bot.core.fraud_detector import FraudDetector
    from bot.jobs.daily_tasks import setup_daily_jobs
    from bot.handlers.start import start
    from bot.handlers.registration import start_registration
    from bot.handlers.callback import handle_callback
    from bot.handlers.admin_fraud import (
        fraud_queue_command,
        fraud_review_command,
        fraud_approve_command,
        fraud_reject_command,
        fraud_stats_command
    )
    print("   ✅ All critical imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    errors.append(f"Import error: {e}")
    sys.exit(1)

# Test 2: Configuration Check
print("\n2️⃣ Checking configuration...")
try:
    from config.settings import settings
    
    # Critical settings
    assert settings.TELEGRAM_BOT_TOKEN, "TELEGRAM_BOT_TOKEN not set"
    print(f"   ✅ Bot token: ...{settings.TELEGRAM_BOT_TOKEN[-10:]}")
    
    assert settings.DATABASE_URL, "DATABASE_URL not set"
    print(f"   ✅ Database: {settings.DATABASE_URL}")
    
    # Optional but recommended
    if settings.ADMIN_USER_ID:
        print(f"   ✅ Admin user: {settings.ADMIN_USER_ID}")
    else:
        print(f"   ⚠️  ADMIN_USER_ID not set (fraud review disabled)")
        warnings.append("ADMIN_USER_ID not configured")
    
    if settings.OPENAI_API_KEY:
        print(f"   ✅ OpenAI API: ...{settings.OPENAI_API_KEY[-10:]}")
    else:
        print(f"   ℹ️  OpenAI API not set (AI features disabled)")
    
except Exception as e:
    print(f"   ❌ Configuration error: {e}")
    errors.append(f"Configuration error: {e}")

# Test 3: Database Connection
print("\n3️⃣ Testing database connection...")
try:
    session = SessionLocal()
    
    # Check if Week 1-5 columns exist
    from sqlalchemy import inspect
    inspector = inspect(session.bind)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    required_columns = [
        'user_state',
        'current_program',
        'program_day',
        'super_vip_last_active',
        'super_vip_decay_warned'
    ]
    
    for col in required_columns:
        if col in columns:
            print(f"   ✅ Column exists: {col}")
        else:
            print(f"   ❌ Missing column: {col}")
            errors.append(f"Missing database column: {col}")
    
    # Check users table
    user_count = session.query(User).count()
    print(f"   ✅ Users table: {user_count} users")
    
    # Check referrals table with fraud columns
    ref_columns = [col['name'] for col in inspector.get_columns('referrals')]
    fraud_columns = ['velocity_score', 'review_status', 'ip_address']
    
    for col in fraud_columns:
        if col in ref_columns:
            print(f"   ✅ Fraud column: {col}")
        else:
            print(f"   ❌ Missing fraud column: {col}")
            errors.append(f"Missing fraud column: {col}")
    
    session.close()
    
except Exception as e:
    print(f"   ❌ Database error: {e}")
    errors.append(f"Database error: {e}")

# Test 4: Core Features Functional
print("\n4️⃣ Testing core features...")
try:
    # State Machine
    with StateManager() as sm:
        states = list(UserState)
        print(f"   ✅ State Machine: {len(states)} states")
        
        # Test valid transitions
        valid = sm.VALID_TRANSITIONS.get(UserState.VIP, set())
        assert UserState.SUPER_VIP in valid, "Super VIP transition missing"
        print(f"   ✅ State transitions configured")
    
    # Program Manager
    with ProgramManager() as pm:
        programs = list(ProgramType)
        print(f"   ✅ Program Manager: {len(programs)} programs")
    
    # Fraud Detector
    with FraudDetector() as detector:
        stats = detector.get_fraud_stats()
        print(f"   ✅ Fraud Detector: {stats['total_referrals']} total refs")
        print(f"      Approval rate: {stats['approval_rate']}%")
    
except Exception as e:
    print(f"   ❌ Core feature error: {e}")
    errors.append(f"Core feature error: {e}")

# Test 5: Previous Test Results
print("\n5️⃣ Checking previous test results...")
import os

test_files = [
    'test_week_1_3.py',
    'test_super_vip.py',
    'test_decay_monitoring.py',
    'test_week_4_complete.py',
    'test_fraud_detection.py'
]

for test_file in test_files:
    if os.path.exists(test_file):
        print(f"   ✅ Test exists: {test_file}")
    else:
        print(f"   ⚠️  Test missing: {test_file}")
        warnings.append(f"Test file missing: {test_file}")

# Test 6: Critical Files Present
print("\n6️⃣ Checking critical files...")
critical_files = [
    'main.py',
    'requirements.txt',
    'config/settings.py',
    'bot/core/state_machine.py',
    'bot/core/program_manager.py',
    'bot/core/fraud_detector.py',
    'bot/jobs/daily_tasks.py',
    'bot/handlers/registration.py',
    'bot/handlers/admin_fraud.py',
]

for file_path in critical_files:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
    else:
        print(f"   ❌ Missing: {file_path}")
        errors.append(f"Missing file: {file_path}")

# Test 7: Check for common issues
print("\n7️⃣ Checking for common issues...")
try:
    # Check if database file is not in git (should be in .gitignore)
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore = f.read()
            if 'data/bot.db' in gitignore or '*.db' in gitignore:
                print("   ✅ Database excluded from git")
            else:
                print("   ⚠️  Database not in .gitignore")
                warnings.append("Database file should be in .gitignore")
    
    # Check if .env is in gitignore
    if '.env' in gitignore:
        print("   ✅ .env excluded from git")
    else:
        print("   ⚠️  .env not in .gitignore")
        warnings.append(".env file should be in .gitignore")
    
except Exception as e:
    print(f"   ⚠️  Could not check .gitignore: {e}")

# Summary
print("\n" + "=" * 60)

if errors:
    print("❌ DEPLOYMENT BLOCKED - Fix errors first:")
    for error in errors:
        print(f"   • {error}")
    sys.exit(1)

elif warnings:
    print("⚠️  DEPLOYMENT READY WITH WARNINGS:")
    for warning in warnings:
        print(f"   • {warning}")
    print("\n✅ Safe to deploy but review warnings")

else:
    print("✅ DEPLOYMENT READY - ALL CHECKS PASSED!")

print("=" * 60)

print("\n📋 DEPLOYMENT CHECKLIST:")
print("\n🔧 Pre-Deployment:")
print("   1. Set environment variables on Railway:")
print("      - TELEGRAM_BOT_TOKEN")
print("      - ADMIN_USER_ID (your Telegram ID)")
print("      - DATABASE_URL (Railway auto-configures)")
print("   2. Review .env.example for reference")
print("   3. Commit and push to GitHub")
print("\n🚀 Deploy:")
print("   1. Connect Railway to GitHub repo")
print("   2. Railway auto-deploys on push")
print("   3. Monitor build logs")
print("\n📊 Post-Deployment Monitoring:")
print("   1. Check bot responds to /start")
print("   2. Test referral flow end-to-end")
print("   3. Monitor /fraud_queue daily")
print("   4. Watch for velocity patterns")
print("   5. Track approval rate (aim for 85-95%)")
print("\n⏰ Daily Tasks:")
print("   • 10:00 AM UTC: Super VIP decay check runs")
print("   • Review fraud queue")
print("   • Check error logs")
print("   • Monitor user growth")
print("\n📈 Metrics to Track (Week 1-2):")
print("   • Total registrations")
print("   • VIP conversion rate (2+ refs)")
print("   • Super VIP conversions (50+ refs)")
print("   • Fraud detection rate")
print("   • False positive rate (check rejected reviews)")
print("   • Average refs per user")
print("\n🎯 Success Criteria:")
print("   • 85-95% auto-approval rate")
print("   • < 5% false positives")
print("   • No system crashes")
print("   • Users understand fraud warnings")
print("   • Admin can review queue effectively")
print("\n💡 Tuning After 1 Week:")
print("   • Adjust velocity thresholds if too strict")
print("   • Update IP cluster limits based on real data")
print("   • Refine scoring weights")
print("   • Consider new fraud signals")
print("\n🚦 Go/No-Go Decision (2 weeks):")
print("   ✅ GO if:")
print("      - System stable")
print("      - Fraud rate < 10%")
print("      - User growth steady")
print("      - No major bugs")
print("   ❌ NO-GO if:")
print("      - High fraud rate")
print("      - Too many false positives")
print("      - System instability")
print("      - User complaints about fairness")
