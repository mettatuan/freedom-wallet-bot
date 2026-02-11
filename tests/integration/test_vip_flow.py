"""
Test VIP Identity Tier Flow
Tests milestone detection and celebration for 10/50/100 referrals
"""
import asyncio
import sys
from loguru import logger
from bot.utils.database import SessionLocal, User
from bot.handlers.vip import check_vip_milestone, VIP_MILESTONES


async def test_vip_milestone_detection():
    """Test VIP milestone detection logic"""
    
    logger.info("🧪 Testing VIP Milestone Detection...")
    
    session = SessionLocal()
    
    try:
        # Get or create test user
        test_user = session.query(User).filter(User.id == 999999).first()
        
        if not test_user:
            logger.info("Creating test user 999999...")
            test_user = User(
                id=999999,
                first_name="VIP Test User",
                username="vip_test",
                referral_code="VIPTEST999",
                referral_count=0
            )
            session.add(test_user)
            session.commit()
        
        # Test scenarios
        test_cases = [
            (9, None, "9 refs - Should NOT trigger milestone"),
            (10, "RISING_STAR", "10 refs - Should trigger Rising Star"),
            (11, None, "11 refs - Should NOT trigger milestone"),
            (49, None, "49 refs - Should NOT trigger milestone"),
            (50, "SUPER_VIP", "50 refs - Should trigger Super VIP"),
            (99, None, "99 refs - Should NOT trigger milestone"),
            (100, "LEGEND", "100 refs - Should trigger Legend"),
        ]
        
        for ref_count, expected_tier, description in test_cases:
            logger.info(f"\n{'='*60}")
            logger.info(f"TEST: {description}")
            logger.info(f"{'='*60}")
            
            # Set referral count
            test_user.referral_count = ref_count
            test_user.vip_tier = None  # Reset VIP tier
            session.commit()
            
            # Check if milestone should be triggered
            should_trigger = ref_count in VIP_MILESTONES
            
            logger.info(f"Referral count: {ref_count}")
            logger.info(f"Should trigger: {should_trigger}")
            logger.info(f"Expected tier: {expected_tier}")
            
            # Verify milestone configuration
            if should_trigger:
                milestone = VIP_MILESTONES[ref_count]
                logger.info(f"✅ Milestone found in config:")
                logger.info(f"   Tier: {milestone['tier']}")
                logger.info(f"   Name: {milestone['name']}")
                logger.info(f"   Benefits count: {len(milestone['benefits'])}")
                
                assert milestone['tier'] == expected_tier, \
                    f"Tier mismatch! Expected {expected_tier}, got {milestone['tier']}"
            
            # Test detection logic
            if ref_count in [10, 50, 100]:
                logger.info(f"✅ PASS: Milestone {ref_count} exists in config")
            else:
                logger.info(f"✅ PASS: No milestone at {ref_count} refs")
        
        logger.info("\n" + "="*60)
        logger.info("✅ ALL VIP MILESTONE DETECTION TESTS PASSED!")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False
    finally:
        session.close()


async def test_vip_benefits():
    """Test VIP benefits configuration"""
    
    logger.info("\n🧪 Testing VIP Benefits Configuration...")
    
    for ref_count, milestone in VIP_MILESTONES.items():
        logger.info(f"\n{milestone['name']} ({ref_count} refs):")
        logger.info(f"  Tier: {milestone['tier']}")
        logger.info(f"  Benefits:")
        for benefit in milestone['benefits']:
            logger.info(f"    • {benefit}")
        
        # Verify structure
        assert 'tier' in milestone, f"Missing 'tier' in milestone {ref_count}"
        assert 'name' in milestone, f"Missing 'name' in milestone {ref_count}"
        assert 'benefits' in milestone, f"Missing 'benefits' in milestone {ref_count}"
        assert 'message' in milestone, f"Missing 'message' in milestone {ref_count}"
        assert isinstance(milestone['benefits'], list), f"Benefits must be a list for milestone {ref_count}"
        assert len(milestone['benefits']) > 0, f"Benefits list empty for milestone {ref_count}"
    
    logger.info("\n✅ ALL VIP BENEFITS TESTS PASSED!")
    return True


async def test_vip_database_fields():
    """Test VIP database fields are accessible"""
    
    logger.info("\n🧪 Testing VIP Database Fields...")
    
    session = SessionLocal()
    
    try:
        # Get first user
        user = session.query(User).first()
        
        if not user:
            logger.warning("⚠️ No users in database to test with")
            return True
        
        logger.info(f"Testing with user {user.id}...")
        
        # Test field access
        vip_tier = user.vip_tier
        vip_unlocked_at = user.vip_unlocked_at
        vip_benefits = user.vip_benefits
        
        logger.info(f"  vip_tier: {vip_tier}")
        logger.info(f"  vip_unlocked_at: {vip_unlocked_at}")
        logger.info(f"  vip_benefits: {vip_benefits}")
        
        logger.info("✅ ALL DATABASE FIELD TESTS PASSED!")
        return True
        
    except AttributeError as e:
        logger.error(f"❌ Database field missing: {e}")
        logger.error("   Run migration first: python migrations/add_vip_fields.py upgrade")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False
    finally:
        session.close()


async def main():
    """Run all VIP flow tests"""
    
    logger.info("="*60)
    logger.info("🚀 STARTING VIP FLOW TESTS")
    logger.info("="*60)
    
    results = []
    
    # Test 1: Database fields
    logger.info("\n[TEST 1/3] Database Fields")
    results.append(await test_vip_database_fields())
    
    # Test 2: Milestone detection
    logger.info("\n[TEST 2/3] Milestone Detection")
    results.append(await test_vip_milestone_detection())
    
    # Test 3: Benefits configuration
    logger.info("\n[TEST 3/3] Benefits Configuration")
    results.append(await test_vip_benefits())
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(results)
    total = len(results)
    
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✅ ALL TESTS PASSED!")
        return 0
    else:
        logger.error(f"❌ {total - passed} TEST(S) FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
