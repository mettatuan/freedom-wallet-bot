"""
Phase 3 Testing Script
Test all Phase 2 functionality end-to-end
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.utils.database import Base, engine, SessionLocal, Transaction, User
from bot.core.nlp import parse_natural_language_transaction, format_vnd
from bot.core.categories import detect_category
from bot.core.awareness import get_awareness_snapshot, format_awareness_message
from bot.core.behavioral import get_behavioral_snapshot, format_behavioral_message
from bot.core.reflection import generate_weekly_insight, format_weekly_insight_message
from datetime import datetime
import traceback


def test_database_schema():
    """Test 1: Verify Transaction table exists"""
    print("\n" + "="*60)
    print("TEST 1: Database Schema")
    print("="*60)
    
    try:
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
        
        # Check Transaction table specifically
        if 'transactions' in tables:
            print("\n✅ Transaction table exists!")
            
            # Check columns
            columns = inspector.get_columns('transactions')
            print(f"   Columns ({len(columns)}):")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
        else:
            print("\n❌ Transaction table NOT found!")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        traceback.print_exc()
        return False


def test_nlp_parser():
    """Test 2: NLP Parser"""
    print("\n" + "="*60)
    print("TEST 2: NLP Parser")
    print("="*60)
    
    test_cases = [
        "Cà phê 35k",
        "Ăn trưa 50000",
        "Grab 45k",
        "Lương 15tr",
        "Bán hàng 2.5tr",
        "Mua quần áo 350k",
    ]
    
    all_passed = True
    
    for text in test_cases:
        try:
            result = parse_natural_language_transaction(text)
            
            if "error" in result:
                print(f"❌ '{text}' → ERROR: {result['error']}")
                all_passed = False
            else:
                print(f"✅ '{text}' →")
                print(f"   Amount: {format_vnd(result['amount'])}")
                print(f"   Category: {result['category']}")
                print(f"   Type: {result['type']}")
                print(f"   Description: {result['description']}")
        except Exception as e:
            print(f"❌ '{text}' → EXCEPTION: {e}")
            all_passed = False
    
    return all_passed


def test_transaction_save():
    """Test 3: Save Transaction to Database"""
    print("\n" + "="*60)
    print("TEST 3: Transaction Save & Retrieve")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Create test user if not exists
        test_user_id = 999999
        user = db.query(User).filter(User.id == test_user_id).first()
        
        if not user:
            print(f"Creating test user {test_user_id}...")
            user = User(
                id=test_user_id,
                username="test_user",
                first_name="Test",
                last_name="User",
                referral_code="TEST0001",
                subscription_tier="FREE"
            )
            db.add(user)
            db.commit()
            print("✅ Test user created")
        else:
            print(f"✅ Test user {test_user_id} exists")
        
        # Parse and save transaction
        text = "Cà phê 35k"
        parsed = parse_natural_language_transaction(text)
        
        if "error" in parsed:
            print(f"❌ Failed to parse '{text}'")
            return False
        
        # Save transaction
        tx = Transaction(
            user_id=test_user_id,
            amount=parsed['amount'],
            category=parsed['category'],
            description=parsed['description'],
            transaction_type=parsed['type'],
            created_at=datetime.utcnow()
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        
        print(f"✅ Transaction saved:")
        print(f"   ID: {tx.id}")
        print(f"   Amount: {format_vnd(tx.amount)}")
        print(f"   Category: {tx.category}")
        print(f"   Description: {tx.description}")
        
        # Retrieve transaction
        retrieved = db.query(Transaction).filter(Transaction.id == tx.id).first()
        
        if retrieved:
            print(f"✅ Transaction retrieved successfully")
            return True
        else:
            print(f"❌ Failed to retrieve transaction")
            return False
            
    except Exception as e:
        print(f"❌ Transaction save test failed: {e}")
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def test_awareness_engine():
    """Test 4: Awareness Engine"""
    print("\n" + "="*60)
    print("TEST 4: Awareness Engine")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        test_user_id = 999999
        
        # Get awareness snapshot
        snapshot = get_awareness_snapshot(test_user_id, db)
        
        print(f"✅ Awareness snapshot generated:")
        print(f"   Balance: {format_vnd(snapshot['balance'])}")
        print(f"   Today: {snapshot['today']}")
        print(f"   Week: {snapshot['week']}")
        print(f"   Streak: {snapshot['streak']}")
        print(f"   Anomalies: {len(snapshot['anomalies'])}")
        
        # Format message
        message = format_awareness_message(snapshot)
        print(f"\n✅ Formatted message ({len(message)} chars):")
        print("   " + message.replace("\n", "\n   "))
        
        return True
        
    except Exception as e:
        print(f"❌ Awareness engine test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_behavioral_engine():
    """Test 5: Behavioral Engine"""
    print("\n" + "="*60)
    print("TEST 5: Behavioral Engine")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        test_user_id = 999999
        
        # Get behavioral snapshot
        snapshot = get_behavioral_snapshot(test_user_id, db)
        
        print(f"✅ Behavioral snapshot generated:")
        print(f"   Categories: {len(snapshot['categories'])}")
        print(f"   Personas: {snapshot['personas']}")
        print(f"   Velocity: {snapshot['velocity']}")
        
        # Format message
        message = format_behavioral_message(snapshot)
        print(f"\n✅ Formatted message ({len(message)} chars):")
        print("   " + message.replace("\n", "\n   "))
        
        return True
        
    except Exception as e:
        print(f"❌ Behavioral engine test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_reflection_engine():
    """Test 6: Reflection Engine"""
    print("\n" + "="*60)
    print("TEST 6: Reflection Engine")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        test_user_id = 999999
        
        # Generate weekly insight
        insight = generate_weekly_insight(test_user_id, db)
        
        print(f"✅ Weekly insight generated:")
        print(f"   User: {insight['user_name']}")
        print(f"   Tone: {insight['tone']}")
        print(f"   Celebrations: {len(insight['celebrations'])}")
        print(f"   Nudges: {len(insight['nudges'])}")
        print(f"   Tips: {len(insight['tips'])}")
        
        # Format message
        message = format_weekly_insight_message(insight)
        print(f"\n✅ Formatted message ({len(message)} chars):")
        print("   " + message.replace("\n", "\n   "))
        
        return True
        
    except Exception as e:
        print(f"❌ Reflection engine test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        db.close()


def cleanup_test_data():
    """Cleanup: Remove test data"""
    print("\n" + "="*60)
    print("CLEANUP: Removing test data")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        test_user_id = 999999
        
        # Delete test transactions
        deleted_tx = db.query(Transaction).filter(Transaction.user_id == test_user_id).delete()
        print(f"✅ Deleted {deleted_tx} test transactions")
        
        # Delete test user
        deleted_user = db.query(User).filter(User.id == test_user_id).delete()
        print(f"✅ Deleted {deleted_user} test user")
        
        db.commit()
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Run all Phase 3 tests"""
    print("\n" + "="*60)
    print("🧪 PHASE 3 TESTING SUITE")
    print("="*60)
    print(f"Testing Financial Assistant Core functionality...")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run tests
    results['database_schema'] = test_database_schema()
    results['nlp_parser'] = test_nlp_parser()
    results['transaction_save'] = test_transaction_save()
    results['awareness_engine'] = test_awareness_engine()
    results['behavioral_engine'] = test_behavioral_engine()
    results['reflection_engine'] = test_reflection_engine()
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    failed_tests = total_tests - passed_tests
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Total: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}")
    
    if failed_tests == 0:
        print(f"\n🎉 ALL TESTS PASSED! Phase 2 is production-ready!")
    else:
        print(f"\n⚠️ {failed_tests} test(s) failed. Please review.")
    
    print(f"{'='*60}\n")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
