"""
Script to get Admin User ID and configure .env
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from bot.utils.database import get_db, User
from sqlalchemy import or_


def get_admin_users():
    """Get all admin users from database"""
    db = next(get_db())
    
    # Get all users and show them
    all_users = db.query(User).all()
    
    print("=" * 60)
    print("  ALL USERS IN DATABASE")
    print("=" * 60)
    
    if not all_users:
        print("❌ No users found in database!")
        print("\n💡 Start the bot and send /start to create your user")
        return
    
    print(f"\n✅ Found {len(all_users)} user(s):\n")
    for user in all_users:
        print(f"  • ID: {user.id}")
        print(f"    Username: @{user.username or 'N/A'}")
        print(f"    Name: {user.full_name or (user.first_name or 'N/A')}")
        print(f"    Tier: {user.subscription_tier}")
        print(f"    Created: {user.created_at.strftime('%d/%m/%Y')}")
        print()
    
    # Show .env configuration for first user (usually the admin/owner)
    first_user_id = all_users[0].id
    print("\n" + "=" * 60)
    print("  CONFIGURATION")
    print("=" * 60)
    print(f"\n💡 Recommended: Set your Telegram ID as admin")
    print(f"\nAdd this to your .env file:")
    print(f"ADMIN_USER_ID={first_user_id}")
    
    # Check if .env exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"\n✅ .env file exists at: {env_file}")
        
        # Check if ADMIN_USER_ID already set
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'ADMIN_USER_ID' in content:
                print("⚠️  ADMIN_USER_ID already set in .env")
                # Show current value
                for line in content.split('\n'):
                    if 'ADMIN_USER_ID' in line and not line.strip().startswith('#'):
                        print(f"    Current value: {line.strip()}")
            else:
                # Offer to add automatically
                print("\n❓ Do you want to add ADMIN_USER_ID to .env now? (y/n): ", end="")
                choice = input().lower()
                if choice == 'y':
                    with open(env_file, 'a', encoding='utf-8') as f:
                        f.write(f"\n# Admin User ID for payment notifications\nADMIN_USER_ID={first_user_id}\n")
                    print(f"✅ Added ADMIN_USER_ID={first_user_id} to .env")
                    print("🔄 Please restart the bot for changes to take effect")
    else:
        print(f"\n❌ .env file not found!")
        print(f"\n📝 Create .env file with:")
        print(f"ADMIN_USER_ID={first_user_id}")
    
    db.close()


def get_your_telegram_id():
    """Show how to get your Telegram ID"""
    print("\n" + "=" * 60)
    print("  HOW TO GET YOUR TELEGRAM ID")
    print("=" * 60)
    print("""
1. Open Telegram and search for: @userinfobot
2. Start the bot and it will show your User ID
3. Copy that ID and use it to set ADMIN_USER_ID

OR

1. Start Freedom Wallet bot: /start
2. Check the logs for your user ID
3. Look for: "User 1299465308 (username)"
""")


if __name__ == "__main__":
    print("\n🔍 Checking for admin users...\n")
    try:
        get_admin_users()
        get_your_telegram_id()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the database is initialized:")
        print("python main.py  # Run bot once to create database")
