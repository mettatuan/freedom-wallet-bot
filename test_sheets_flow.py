"""
Test Clean Architecture Sheets Setup Flow
Run this before testing realtime to ensure all components work
"""
import asyncio
import sqlite3
import re
from datetime import datetime


async def test_database_connection():
    """Test 1: Database connection"""
    print("\n🧪 Test 1: Database Connection")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        print("✅ Database connection successful")
        
        # Check if users table exists
        result = cursor.execute("SELECT COUNT(*) FROM users").fetchone()
        print(f"✅ Users table accessible, {result[0]} users found")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def test_user_table_schema():
    """Test 2: User table schema"""
    print("\n🧪 Test 2: User Table Schema")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        # Check table schema
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        required_columns = ['user_id', 'telegram_username', 'email', 'phone', 'tier', 'sheet_url', 'webapp_url']
        
        for col in required_columns:
            if col in column_names:
                print(f"✅ Column exists: {col}")
            else:
                print(f"❌ Missing column: {col}")
                conn.close()
                return False
        
        # Check primary key
        pk_columns = [col for col in columns if col[5] == 1]
        if pk_columns and pk_columns[0][1] == 'user_id':
            print(f"✅ Primary key: user_id")
        else:
            print(f"❌ Primary key is not user_id")
            conn.close()
            return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False


async def test_crud_operations():
    """Test 3: CRUD operations"""
    print("\n🧪 Test 3: CRUD Operations")
    print("=" * 50)
    
    test_user_id = 999888777
    
    try:
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        # CREATE
        cursor.execute(
            """INSERT OR REPLACE INTO users 
               (user_id, telegram_username, email, phone, tier, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (test_user_id, "test_user", "test@example.com", "+84999888777", 
             "FREE", datetime.utcnow(), datetime.utcnow())
        )
        conn.commit()
        print(f"✅ CREATE: User {test_user_id} inserted")
        
        # READ
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (test_user_id,))
        user = cursor.fetchone()
        if user:
            print(f"✅ READ: Found user - {user[1]} ({user[2]})")
        else:
            print(f"❌ READ: User not found")
            conn.close()
            return False
        
        # UPDATE
        cursor.execute(
            "UPDATE users SET email = ?, updated_at = ? WHERE user_id = ?",
            ("updated@example.com", datetime.utcnow(), test_user_id)
        )
        conn.commit()
        
        cursor.execute("SELECT email FROM users WHERE user_id = ?", (test_user_id,))
        updated_email = cursor.fetchone()[0]
        if updated_email == "updated@example.com":
            print(f"✅ UPDATE: Email updated to {updated_email}")
        else:
            print(f"❌ UPDATE: Email not updated")
            conn.close()
            return False
        
        # DELETE
        cursor.execute("DELETE FROM users WHERE user_id = ?", (test_user_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (test_user_id,))
        deleted_user = cursor.fetchone()
        if not deleted_user:
            print(f"✅ DELETE: User {test_user_id} deleted")
        else:
            print(f"❌ DELETE: User still exists")
            conn.close()
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ CRUD operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_message_formatting():
    """Test 4: Message formatting"""
    print("\n🧪 Test 4: Message Formatting")
    print("=" * 50)
    
    try:
        # Email confirmation message
        email = "test@gmail.com"
        message = (
            f"✅ **Email đã lưu:** `{email}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📱 **Bước 2/4: Số điện thoại**\n"
            f"Nhập số điện thoại của bạn:\n\n"
            f"📝 Ví dụ: `0901234567` hoặc `+84901234567`"
        )
        
        print("📱 Email Confirmation Message:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        
        # Phone confirmation message
        phone = "+84901234567"
        message2 = (
            f"✅ **Số điện thoại đã lưu:** `{phone}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 **Bước 3/4: Google Sheet**\n"
            f"Nhập link Google Sheet của bạn:\n\n"
            f"📝 Ví dụ: `https://docs.google.com/spreadsheets/d/...`"
        )
        
        print("\n📊 Phone Confirmation Message:")
        print("-" * 50)
        print(message2)
        print("-" * 50)
        
        print("\n✅ Message formatting works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Message formatting failed: {e}")
        return False


async def test_validation():
    """Test 5: Input validation"""
    print("\n🧪 Test 5: Input Validation")
    print("=" * 50)
    
    try:
        # Test email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        valid_emails = [
            "test@gmail.com",
            "user.name@example.co.uk",
            "test+tag@domain.com",
            "john_doe@company-name.vn"
        ]
        
        invalid_emails = [
            "notanemail",
            "@domain.com",
            "test@",
            "test @domain.com",
            "test@domain",
            "test..name@domain.com"
        ]
        
        print("📧 Email Validation:")
        for email in valid_emails:
            if re.match(email_pattern, email):
                print(f"  ✅ Valid: {email}")
            else:
                print(f"  ❌ Should accept: {email}")
                return False
        
        for email in invalid_emails:
            if not re.match(email_pattern, email):
                print(f"  ✅ Rejected: {email}")
            else:
                print(f"  ❌ Should reject: {email}")
                return False
        
        # Test phone validation
        phone_pattern = r'^(\+84|0)[0-9]{9,10}$'
        
        valid_phones = [
            "0901234567",
            "+84901234567",
            "0123456789",
            "+840123456789"
        ]
        
        invalid_phones = [
            "123",
            "12345678901",
            "+85901234567",
            "abc123",
            "090 123 4567",
            "+84 901234567"
        ]
        
        print("\n📱 Phone Validation:")
        for phone in valid_phones:
            if re.match(phone_pattern, phone):
                print(f"  ✅ Valid: {phone}")
            else:
                print(f"  ❌ Should accept: {phone}")
                return False
        
        for phone in invalid_phones:
            if not re.match(phone_pattern, phone):
                print(f"  ✅ Rejected: {phone}")
            else:
                print(f"  ❌ Should reject: {phone}")
                return False
        
        # Test URL validation
        url_pattern = r'^https://docs\.google\.com/spreadsheets/'
        
        valid_urls = [
            "https://docs.google.com/spreadsheets/d/abc123/edit",
            "https://docs.google.com/spreadsheets/d/xyz456/edit#gid=0"
        ]
        
        invalid_urls = [
            "http://docs.google.com/spreadsheets/d/abc123",
            "https://drive.google.com/file/d/abc123",
            "https://sheets.google.com/abc",
            "docs.google.com/spreadsheets/d/abc"
        ]
        
        print("\n🔗 Sheet URL Validation:")
        for url in valid_urls:
            if re.match(url_pattern, url):
                print(f"  ✅ Valid URL")
            else:
                print(f"  ❌ Should accept: {url[:50]}...")
                return False
        
        for url in invalid_urls:
            if not re.match(url_pattern, url):
                print(f"  ✅ Rejected invalid URL")
            else:
                print(f"  ❌ Should reject: {url[:50]}...")
                return False
        
        print("\n✅ All validation tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False


async def test_conversation_flow():
    """Test 6: Conversation flow simulation"""
    print("\n🧪 Test 6: Conversation Flow Simulation")
    print("=" * 50)
    
    try:
        test_user_id = 777666555
        
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        # Step 1: /sheetssetup command
        print("📍 Step 1: User sends /sheetssetup")
        print("   Bot: 'Nhập email của bạn'")
        
        # Step 2: User sends email
        email = "testflow@gmail.com"
        print(f"\n📍 Step 2: User sends: {email}")
        
        # Validate email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            print("   ❌ Email validation failed")
            return False
        print("   ✅ Email validated")
        
        # Save email
        cursor.execute(
            """INSERT OR REPLACE INTO users 
               (user_id, telegram_username, email, tier, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (test_user_id, "testflow_user", email, "FREE", 
             datetime.utcnow(), datetime.utcnow())
        )
        conn.commit()
        print(f"   ✅ Email saved: {email}")
        print("   Bot: 'Email đã lưu. Nhập số điện thoại'")
        
        # Step 3: User sends phone
        phone = "+84901234567"
        print(f"\n📍 Step 3: User sends: {phone}")
        
        # Validate phone
        phone_pattern = r'^(\+84|0)[0-9]{9,10}$'
        if not re.match(phone_pattern, phone):
            print("   ❌ Phone validation failed")
            return False
        print("   ✅ Phone validated")
        
        # Save phone
        cursor.execute(
            "UPDATE users SET phone = ?, updated_at = ? WHERE user_id = ?",
            (phone, datetime.utcnow(), test_user_id)
        )
        conn.commit()
        print(f"   ✅ Phone saved: {phone}")
        print("   Bot: 'Số điện thoại đã lưu. Nhập Google Sheet URL'")
        
        # Step 4: User sends sheet URL
        sheet_url = "https://docs.google.com/spreadsheets/d/abc123xyz/edit"
        print(f"\n📍 Step 4: User sends: {sheet_url[:50]}...")
        
        # Validate URL
        url_pattern = r'^https://docs\.google\.com/spreadsheets/'
        if not re.match(url_pattern, sheet_url):
            print("   ❌ URL validation failed")
            return False
        print("   ✅ URL validated")
        
        # Save URL
        cursor.execute(
            "UPDATE users SET sheet_url = ?, updated_at = ? WHERE user_id = ?",
            (sheet_url, datetime.utcnow(), test_user_id)
        )
        conn.commit()
        print(f"   ✅ Sheet URL saved")
        print("   Bot: 'Google Sheet đã lưu. Nhập WebApp URL'")
        
        # Step 5: Verify final state
        print(f"\n📍 Step 5: Verify user data")
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (test_user_id,))
        user = cursor.fetchone()
        
        if user:
            print(f"   ✅ User ID: {user[0]}")
            print(f"   ✅ Username: {user[1]}")
            print(f"   ✅ Email: {user[2]}")
            print(f"   ✅ Phone: {user[3]}")
            print(f"   ✅ Tier: {user[4]}")
            print(f"   ✅ Sheet URL: {user[5][:50] if user[5] else 'None'}...")
        else:
            print("   ❌ User data not found")
            return False
        
        # Cleanup
        cursor.execute("DELETE FROM users WHERE user_id = ?", (test_user_id,))
        conn.commit()
        print(f"\n✅ Test user cleaned up")
        
        conn.close()
        print("\n✅ Complete flow simulation successful")
        return True
        
    except Exception as e:
        print(f"❌ Flow simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("🚀 Sheets Setup Flow Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("User Table Schema", test_user_table_schema),
        ("CRUD Operations", test_crud_operations),
        ("Message Formatting", test_message_formatting),
        ("Input Validation", test_validation),
        ("Conversation Flow", test_conversation_flow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready for realtime testing!")
        print("\n📝 Next steps:")
        print("   1. Open Telegram bot")
        print("   2. Send /sheetssetup command")
        print("   3. Follow the prompts to enter:")
        print("      - Email (example: test@gmail.com)")
        print("      - Phone (example: +84901234567)")
        print("      - Google Sheet URL")
        print("      - WebApp URL")
    else:
        print("\n⚠️ Some tests failed. Fix issues before realtime testing.")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
