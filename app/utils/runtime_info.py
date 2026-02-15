"""
Runtime Info Module
Prints diagnostic information on bot startup
Prevents schema drift issues by making runtime state visible
"""
import sys
import os
from pathlib import Path
from datetime import datetime

def print_runtime_info():
    """Print comprehensive runtime information on bot startup"""
    
    # Set UTF-8 encoding for Windows console
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    
    try:
        print("\n" + "=" * 80)
        print("🚀 FREEDOM WALLET BOT - RUNTIME INFORMATION")
        print("=" * 80)
    except UnicodeEncodeError:
        print("\n" + "=" * 80)
        print("FREEDOM WALLET BOT - RUNTIME INFORMATION")
        print("=" * 80)
    
    print(f"📅 Startup Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version:   {sys.version.split()[0]}")
    print(f"📁 Python Path:      {sys.executable}")
    print(f"📂 Working Dir:      {os.getcwd()}")
    print(f"🏠 Project Root:     {Path(__file__).parent.parent}")
    print()
    
    # Database configuration
    try:
        from config.settings import settings
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        db_full_path = Path(db_path).resolve()
        
        print("=" * 80)
        print("💾 DATABASE CONFIGURATION")
        print("=" * 80)
        print(f"📋 DATABASE_URL:     {settings.DATABASE_URL}")
        print(f"📄 Database File:    {db_path}")
        print(f"🔗 Resolved Path:    {db_full_path}")
        print(f"✅ File Exists:      {db_full_path.exists()}")
        if db_full_path.exists():
            size_kb = db_full_path.stat().st_size / 1024
            print(f"📦 File Size:        {size_kb:.2f} KB")
        print()
        
        # Schema verification
        import sqlite3
        conn = sqlite3.connect(str(db_full_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("=" * 80)
        print("📊 DATABASE SCHEMA STATUS")
        print("=" * 80)
        print(f"📋 Tables:           {len(tables)} total")
        print(f"👥 Users Count:      {users_count} rows")
        print(f"🏗️  User Columns:     {len(columns)} columns")
        
        # Verify model matches DB
        from app.utils.database import User
        model_table = User.__tablename__
        print(f"🔗 Model Points To:  '{model_table}' table")
        
        # Check for legacy table
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='users_legacy'")
        has_legacy = cursor.fetchone()[0] > 0
        if has_legacy:
            cursor.execute("SELECT COUNT(*) FROM users_legacy")
            legacy_count = cursor.fetchone()[0]
            print(f"⚠️  Legacy Table:     EXISTS ({legacy_count} rows)")
        else:
            print(f"✅ Legacy Table:     Cleaned up")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database config: {e}")
    
    # Check for multiple bot instances
    print()
    print("=" * 80)
    print("🔒 PROCESS CHECK")
    print("=" * 80)
    
    try:
        import psutil
        python_processes = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) 
                           if p.info['name'] and 'python' in p.info['name'].lower()]
        
        bot_processes = [p for p in python_processes 
                        if p.info['cmdline'] and any('main.py' in str(cmd) for cmd in p.info['cmdline'])]
        
        if len(bot_processes) > 1:
            print(f"⚠️  Multiple bot instances detected: {len(bot_processes)}")
            for p in bot_processes:
                print(f"   PID {p.info['pid']}: {' '.join(p.info['cmdline'])}")
        else:
            print(f"✅ Single bot instance running (PID: {os.getpid()})")
            
    except ImportError:
        print("ℹ️  Install 'psutil' for process monitoring")
    except Exception as e:
        print(f"⚠️  Could not check processes: {e}")
    
    print("=" * 80)
    print()


def verify_single_database():
    """Ensure only one database file is being used"""
    from config.settings import settings
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    # Check for common duplicate DB files
    project_root = Path(__file__).parent.parent
    potential_dbs = [
        "bot.db",
        "data/bot.db",
        "db/bot.db",
        "database/bot.db",
        "freedomwallet.db",
        "data/freedomwallet.db",
    ]
    
    found_dbs = []
    for db in potential_dbs:
        db_file = project_root / db
        if db_file.exists():
            found_dbs.append(str(db_file.resolve()))
    
    if len(found_dbs) > 1:
        print("\n⚠️  WARNING: Multiple database files detected!")
        print("   This may cause data inconsistency.")
        print(f"\n   Configured: {Path(db_path).resolve()}")
        print(f"\n   Found {len(found_dbs)} database files:")
        for db in found_dbs:
            print(f"   - {db}")
        print("\n   Action: Remove unused database files\n")
        return False
    
    return True


if __name__ == "__main__":
    print_runtime_info()
    verify_single_database()
