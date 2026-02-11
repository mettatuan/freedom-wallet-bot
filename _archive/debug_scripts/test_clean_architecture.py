"""Test Clean Architecture integration."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.di_container import initialize_container
from src.infrastructure.database import init_db, drop_db
from src.application.dtos import RegisterUserInput, SetupSheetInput, RecordTransactionInput
from decimal import Decimal
from datetime import datetime


async def test_clean_architecture():
    """Test Clean Architecture end-to-end."""
    
    print("=" * 60)
    print("Testing Clean Architecture Integration")
    print("=" * 60)
    
    # 1. Initialize database (in-memory SQLite for testing)
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    print("\n1️⃣  Initializing database...")
    
    # Drop and recreate database to ensure clean state
    try:
        drop_db()
    except:
        pass
    init_db()
    print("   ✅ Database initialized")
    
    # 2. Initialize DI Container
    print("\n2️⃣  Initializing DI Container...")
    container = initialize_container(
        bot=None,  # No bot needed for testing
        google_credentials_file=None,
        openai_api_key=None
    )
    print("   ✅ DI Container initialized")
    
    # 3. Test RegisterUserUseCase
    print("\n3️⃣  Testing RegisterUserUseCase...")
    session = container.get_db_session()
    
    try:
        register_use_case = container.get_register_user_use_case(session)
        
        result = await register_use_case.execute(RegisterUserInput(
            telegram_user_id=123456,
            telegram_username="testuser",
            email=None,
            phone=None
        ))
        
        if result.is_success():
            user = result.data.user
            sub = result.data.subscription
            print(f"   ✅ User registered: {user.user_id} ({user.tier})")
            print(f"   ✅ Subscription: {sub.tier} (expires: {sub.expires_at})")
        else:
            print(f"   ❌ Failed: {result.error_message}")
            return
        
        # 4. Test SetupSheetUseCase
        print("\n4️⃣  Testing SetupSheetUseCase...")
        setup_use_case = container.get_setup_sheet_use_case(session)
        
        result = await setup_use_case.execute(SetupSheetInput(
            user_id=123456,
            email="test@gmail.com",
            phone="+84901234567",
            sheet_url="https://docs.google.com/spreadsheets/d/test123",
            webapp_url="https://webapp.example.com/123"
        ))
        
        if result.is_success():
            user = result.data.user
            sub = result.data.subscription
            print(f"   ✅ Sheet setup completed: {user.tier}")
            print(f"   ✅ Email: {user.email}, Phone: {user.phone}")
            print(f"   ✅ Subscription upgraded to: {sub.tier}")
        else:
            print(f"   ❌ Failed: {result.error_message}")
            return
        
        # 5. Test RecordTransactionUseCase
        print("\n5️⃣  Testing RecordTransactionUseCase...")
        record_use_case = container.get_record_transaction_use_case(session)
        
        # Record expense
        result = await record_use_case.execute(RecordTransactionInput(
            user_id=123456,
            amount=Decimal("-50000"),
            category="Ăn uống",
            note="Ăn sáng",
            date=datetime.utcnow()
        ))
        
        if result.is_success():
            txn = result.data.transaction
            balance = result.data.balance
            print(f"   ✅ Expense recorded: {txn.amount}đ ({txn.category})")
            print(f"   ✅ Balance: {balance}đ")
        else:
            print(f"   ❌ Failed: {result.error_message}")
            return
        
        # Record income
        result = await record_use_case.execute(RecordTransactionInput(
            user_id=123456,
            amount=Decimal("5000000"),
            category="Thu nhập",
            note="Lương tháng 1",
            date=datetime.utcnow()
        ))
        
        if result.is_success():
            txn = result.data.transaction
            balance = result.data.balance
            print(f"   ✅ Income recorded: {txn.amount}đ ({txn.category})")
            print(f"   ✅ New balance: {balance}đ")
        else:
            print(f"   ❌ Failed: {result.error_message}")
            return
        
        # 6. Test CalculateBalanceUseCase
        print("\n6️⃣  Testing CalculateBalanceUseCase...")
        calculate_use_case = container.get_calculate_balance_use_case(session)
        
        result = await calculate_use_case.execute(123456)
        
        if result.is_success():
            data = result.data
            print(f"   ✅ Total income: {data.total_income}đ")
            print(f"   ✅ Total expense: {data.total_expense}đ")
            print(f"   ✅ Balance: {data.balance}đ")
            print(f"   ✅ Transaction count: {data.transaction_count}")
        else:
            print(f"   ❌ Failed: {result.error_message}")
            return
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nClean Architecture is working correctly! 🎉")
        print("\nYou can now:")
        print("  1. Wire these handlers in main.py")
        print("  2. Test with real Telegram bot")
        print("  3. Deploy to production")
        
    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(test_clean_architecture())
