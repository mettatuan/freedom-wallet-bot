# 🧪 TESTING GUIDE - Freedom Wallet Bot
**Comprehensive Testing Framework**

Version: 2.0  
Date: 2026-02-17

---

## 📋 OVERVIEW

This guide covers the complete testing strategy for Freedom Wallet Bot, including unit tests, integration tests, end-to-end tests, and manual testing procedures.

**Coverage Goal:** 90%+

---

## 🎯 TESTING PHILOSOPHY

### **Pyramid Strategy**

```
         ┌─────────────┐
         │    E2E      │  ← 10% (Critical paths)
         │   Tests     │
         ├─────────────┤
         │ Integration │  ← 30% (System interaction)
         │   Tests     │
         ├─────────────┤
         │    Unit     │  ← 60% (Business logic)
         │   Tests     │
         └─────────────┘
```

**Principles:**
- ✅ Fast feedback (unit tests run in <1 second)
- ✅ Isolated tests (no external dependencies in unit)
- ✅ Realistic scenarios (integration tests use real APIs)
- ✅ Complete coverage (all state transitions tested)

---

## 🏗️ TEST STRUCTURE

```
tests/
├── conftest.py                    # Pytest fixtures
├── pytest.ini                     # Pytest configuration
│
├── unit/                          # Fast, isolated tests
│   ├── test_state_machine.py     # State transition logic
│   ├── test_tier_system.py       # Subscription tier logic
│   ├── test_referral_logic.py    # Referral counting
│   └── test_user_profile.py      # User model validation
│
├── integration/                   # System interaction tests
│   ├── test_registration.py      # Full registration flow
│   ├── test_sheets_setup.py      # Google Sheets integration
│   ├── test_referral_flow.py     # Referral link → reward
│   ├── test_premium_upgrade.py   # Payment → upgrade
│   └── test_ai_service.py        # GPT-4 integration
│
├── e2e/                           # End-to-end user journeys
│   ├── test_new_user_journey.py  # VISITOR → ACTIVE
│   ├── test_vip_journey.py       # Referral path
│   └── test_premium_journey.py   # FREE → PREMIUM
│
└── fixtures/                      # Test data
    ├── sample_users.json
    ├── mock_telegram_updates.json
    └── sample_sheets_data.json
```

---

## 🧪 UNIT TESTS

### **1. State Machine Tests**

**File:** `tests/unit/test_state_machine.py`

```python
import pytest
from app.core.state_machine import StateManager, UserState

class TestStateTransitions:
    """Test all valid and invalid state transitions"""
    
    def test_visitor_to_registered(self, db_session):
        """Test: VISITOR can transition to REGISTERED"""
        mgr = StateManager()
        success, msg = mgr.transition_user(
            user_id=123,
            new_state=UserState.REGISTERED,
            reason="Registration completed"
        )
        assert success is True
        assert "REGISTERED" in msg
    
    def test_invalid_transition_blocked(self, db_session):
        """Test: Cannot transition from VISITOR to VIP directly"""
        mgr = StateManager()
        success, msg = mgr.transition_user(
            user_id=123,
            new_state=UserState.VIP
        )
        assert success is False
        assert "Invalid transition" in msg
    
    def test_legacy_user_migration(self, legacy_user):
        """Test: LEGACY users auto-migrate on first transition"""
        mgr = StateManager()
        state, is_legacy = mgr.get_user_state(legacy_user.id)
        assert is_legacy is True
        
        # Trigger migration
        mgr.transition_user(legacy_user.id, UserState.VIP)
        
        state, is_legacy = mgr.get_user_state(legacy_user.id)
        assert is_legacy is False
        assert state == UserState.VIP
```

**Run:**
```bash
pytest tests/unit/test_state_machine.py -v
```

---

### **2. Tier System Tests**

**File:** `tests/unit/test_tier_system.py`

```python
from app.core.unified_states import (
    SubscriptionTier, 
    TierTransitions,
    UserProfile
)

class TestTierUpgrades:
    """Test subscription tier upgrades"""
    
    def test_free_to_unlock_upgrade(self):
        """Test: FREE can upgrade to UNLOCK"""
        can_upgrade = TierTransitions.can_upgrade(
            SubscriptionTier.FREE,
            SubscriptionTier.UNLOCK
        )
        assert can_upgrade is True
    
    def test_premium_cannot_upgrade(self):
        """Test: PREMIUM is max tier"""
        can_upgrade = TierTransitions.can_upgrade(
            SubscriptionTier.PREMIUM,
            SubscriptionTier.PREMIUM
        )
        assert can_upgrade is False
    
    def test_ai_message_limits(self):
        """Test: Each tier has correct AI limits"""
        assert SubscriptionTier.FREE.ai_message_limit == 5
        assert SubscriptionTier.UNLOCK.ai_message_limit == 20
        assert SubscriptionTier.PREMIUM.ai_message_limit is None
```

---

### **3. Referral Logic Tests**

**File:** `tests/unit/test_referral_logic.py`

```python
class TestReferralLogic:
    """Test referral counting and VIP unlocks"""
    
    def test_vip_unlock_at_2_refs(self, user_with_1_ref):
        """Test: User becomes VIP at 2 referrals"""
        mgr = StateManager()
        
        # Add 1 more referral (total = 2)
        user_with_1_ref.referral_count = 2
        db.session.commit()
        
        # Check state update
        new_state = mgr.check_and_update_state_by_referrals(
            user_with_1_ref.id
        )
        
        assert new_state == UserState.VIP
    
    def test_super_vip_at_50_refs(self, user_with_49_refs):
        """Test: User becomes SUPER_VIP at 50 referrals"""
        mgr = StateManager()
        
        user_with_49_refs.referral_count = 50
        db.session.commit()
        
        new_state = mgr.check_and_update_state_by_referrals(
            user_with_49_refs.id
        )
        
        assert new_state == UserState.SUPER_VIP
```

---

## 🔗 INTEGRATION TESTS

### **1. Registration Flow Test**

**File:** `tests/integration/test_registration.py`

```python
import pytest
from telegram import Update
from tests.fixtures.mock_bot import MockTelegramBot

@pytest.mark.asyncio
class TestRegistrationFlow:
    """Test complete registration flow"""
    
    async def test_full_registration_flow(self, mock_bot, mock_update):
        """
        Simulate: /start → email → phone → name → confirm
        """
        # Step 1: /start command
        await start(mock_update, mock_bot.context)
        assert "Welcome" in mock_bot.last_message
        
        # Step 2: User clicks "Register"
        callback_update = mock_update.callback_query("register_start")
        await handle_callback(callback_update, mock_bot.context)
        assert "email" in mock_bot.last_message.lower()
        
        # Step 3: User sends email
        email_update = mock_update.message("user@example.com")
        await receive_email(email_update, mock_bot.context)
        assert "phone" in mock_bot.last_message.lower()
        
        # Step 4: User sends phone
        phone_update = mock_update.message("0901234567")
        await receive_phone(phone_update, mock_bot.context)
        assert "name" in mock_bot.last_message.lower()
        
        # Step 5: User sends name
        name_update = mock_update.message("Nguyễn Văn A")
        await receive_name(name_update, mock_bot.context)
        assert "confirm" in mock_bot.last_message.lower()
        
        # Step 6: Confirm registration
        confirm_update = mock_update.callback_query("confirm_yes")
        await confirm_registration(confirm_update, mock_bot.context)
        
        # Verify user created in DB
        user = db.query(User).filter_by(
            email="user@example.com"
        ).first()
        
        assert user is not None
        assert user.phone == "0901234567"
        assert user.full_name == "Nguyễn Văn A"
        assert user.subscription_tier == "FREE"
        assert user.user_state == "REGISTERED"
```

---

### **2. Referral Flow Test**

**File:** `tests/integration/test_referral_flow.py`

```python
@pytest.mark.asyncio
class TestReferralFlow:
    """Test complete referral flow"""
    
    async def test_referral_link_to_vip(self, referrer_user, mock_bot):
        """
        Test: User A refers User B & C → becomes VIP
        """
        # User A generates referral link
        ref_link = f"t.me/FreedomWalletBot?start=ref_{referrer_user.referral_code}"
        
        # User B clicks link
        update_b = mock_update.with_start_param(
            f"ref_{referrer_user.referral_code}"
        )
        await start(update_b, mock_bot.context)
        
        # User B registers
        user_b = await complete_registration(
            update_b, 
            email="userb@example.com"
        )
        
        # Check: User B linked to User A
        assert user_b.referred_by == referrer_user.id
        assert referrer_user.referral_count == 1
        
        # User C clicks link & registers
        update_c = mock_update.with_start_param(
            f"ref_{referrer_user.referral_code}"
        )
        user_c = await complete_registration(
            update_c,
            email="userc@example.com"
        )
        
        # Check: User A becomes VIP
        db.session.refresh(referrer_user)
        assert referrer_user.referral_count == 2
        assert referrer_user.user_state == "VIP"
        assert referrer_user.is_free_unlocked is True
```

---

### **3. Google Sheets Setup Test**

**File:** `tests/integration/test_sheets_setup.py`

```python
@pytest.mark.asyncio
class TestSheetsSetup:
    """Test Google Sheets integration"""
    
    async def test_sheets_setup_flow(self, registered_user, mock_bot):
        """
        Test: User sets up Google Sheets → UNLOCK tier
        """
        # User clicks "Setup Sheets"
        update = mock_update.callback_query("setup_sheets")
        await start_sheet_setup(update, mock_bot.context)
        
        # User provides sheet URL
        sheet_url = "https://docs.google.com/spreadsheets/d/ABC123"
        sheet_update = mock_update.message(sheet_url)
        await receive_sheet_url(sheet_update, mock_bot.context)
        
        # Verify backend processes
        assert mock_bot.context.user_data["sheet_url"] == sheet_url
        
        # User provides webapp URL
        webapp_url = "https://script.google.com/macros/s/XYZ"
        webapp_update = mock_update.message(webapp_url)
        await receive_webapp_url(webapp_update, mock_bot.context)
        
        # Check: User upgraded to UNLOCK
        db.session.refresh(registered_user)
        assert registered_user.subscription_tier == "UNLOCK"
        assert registered_user.sheet_url == sheet_url
        assert registered_user.web_app_url == webapp_url
```

---

## 🎭 END-TO-END TESTS

### **Complete User Journey**

**File:** `tests/e2e/test_new_user_journey.py`

```python
@pytest.mark.asyncio
@pytest.mark.e2e
class TestCompleteUserJourney:
    """Test full user journey from visitor to active user"""
    
    async def test_visitor_to_active_premium(self, mock_bot):
        """
        Complete flow:
        VISITOR → REGISTERED → ONBOARDING → ACTIVE (UNLOCK)
        → VIP (2 refs) → PREMIUM (payment)
        """
        # === PHASE 1: REGISTRATION ===
        user_id = 999888777
        update = mock_update.from_user(user_id)
        
        # /start
        await start(update, mock_bot.context)
        
        # Complete registration
        user = await complete_registration_flow(
            update,
            email="testuser@example.com",
            phone="0909123456",
            name="Test User"
        )
        
        assert user.user_state == "REGISTERED"
        assert user.subscription_tier == "FREE"
        
        # === PHASE 2: ONBOARDING ===
        # Setup Google Sheets
        await complete_sheets_setup(
            update,
            sheet_url="https://docs.google.com/spreadsheets/d/TEST",
            webapp_url="https://script.google.com/macros/s/TEST"
        )
        
        db.session.refresh(user)
        assert user.user_state == "ACTIVE"
        assert user.subscription_tier == "UNLOCK"
        
        # === PHASE 3: REFERRALS → VIP ===
        # Refer 2 users
        ref1 = await register_via_referral(user.referral_code, "ref1@test.com")
        ref2 = await register_via_referral(user.referral_code, "ref2@test.com")
        
        db.session.refresh(user)
        assert user.referral_count == 2
        assert user.user_state == "VIP"
        
        # === PHASE 4: PREMIUM UPGRADE ===
        # Simulate payment
        await process_premium_payment(user.id, amount=999000)
        
        db.session.refresh(user)
        assert user.subscription_tier == "PREMIUM"
        assert user.premium_expires_at is not None
        
        # === VERIFICATION ===
        # Check all features unlocked
        assert user.can_use_ai_unlimited() is True
        assert user.can_access_premium_features() is True
```

---

## 🤖 AUTOMATED TEST SUITE

### **Pytest Configuration**

**File:** `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (external dependencies)
    e2e: End-to-end tests (complete flows)
    slow: Tests that take >5 seconds

addopts =
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
```

---

### **Run Commands**

```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run E2E tests
pytest tests/e2e/ -v -m e2e

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_state_machine.py -v

# Run specific test
pytest tests/unit/test_state_machine.py::TestStateTransitions::test_visitor_to_registered -v

# Run in parallel (faster)
pytest -n auto

# Run and stop on first failure
pytest -x
```

---

## 🎯 COVERAGE TARGETS

| Component | Target | Current |
|-----------|--------|---------|
| State Machine | 100% | TBD |
| Tier System | 100% | TBD |
| Referral Logic | 95% | TBD |
| Handlers | 85% | TBD |
| Services | 90% | TBD |
| **Overall** | **90%** | **TBD** |

**Track with:**
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 🔍 MANUAL TESTING

### **Critical User Flows to Test Manually**

#### **1. Registration Flow**
- [ ] Click /start → See welcome message
- [ ] Click "Register" → Email prompt appears
- [ ] Enter email → Phone prompt appears
- [ ] Enter phone → Name prompt appears
- [ ] Enter name → Confirmation appears
- [ ] Confirm → Success message + referral code

#### **2. Referral Flow**
- [ ] User A generates referral link
- [ ] User B clicks link → Sees referral attribution
- [ ] User B registers → User A notified
- [ ] User A refers 2+ users → VIP unlocked
- [ ] User A gets VIP notification

#### **3. Google Sheets Setup**
- [ ] Click "Setup Sheets" → Instructions appear
- [ ] Paste sheet URL → Validation success
- [ ] Paste webapp URL → Connection test
- [ ] Setup complete → UNLOCK tier activated

#### **4. Premium Upgrade**
- [ ] User sees premium offer
- [ ] Clicks "Upgrade" → Payment QR appears
- [ ] Transfers money → Clicks "I paid"
- [ ] Admin confirms → Premium activated
- [ ] User gets confirmation + features unlocked

---

## 🐛 DEBUGGING TESTS

### **Common Issues**

**Test fails due to DB state:**
```bash
# Reset test database
pytest --create-db

# Or use fixtures properly
@pytest.fixture
def clean_db(db_session):
    db_session.query(User).delete()
    db_session.commit()
    yield
    db_session.rollback()
```

**Async test not running:**
```python
# Install pytest-asyncio
pip install pytest-asyncio

# Mark test as async
@pytest.mark.asyncio
async def test_async_handler():
    ...
```

**Mock not working:**
```python
# Use proper mocking
from unittest.mock import AsyncMock, patch

@patch('app.services.ai_service.openai_client')
async def test_ai_call(mock_openai):
    mock_openai.chat.completions.create = AsyncMock(
        return_value={"response": "test"}
    )
    ...
```

---

## 📊 CI/CD INTEGRATION

**GitHub Actions Workflow:**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: pytest --cov=app --cov-fail-under=90
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 📝 BEST PRACTICES

1. **Write tests first** (TDD) for new features
2. **Use fixtures** for common setup
3. **Mock external APIs** (Telegram, OpenAI, Google Sheets)
4. **Test edge cases** (empty input, invalid data, network errors)
5. **Keep tests fast** (<0.1s for unit, <1s for integration)
6. **Use descriptive names** (`test_user_becomes_vip_after_2_referrals`)
7. **One assertion per test** (when possible)
8. **Clean up after tests** (fixtures with cleanup)

---

**Last Updated:** 2026-02-17  
**Version:** 2.0  
**Maintainer:** Freedom Wallet Team
