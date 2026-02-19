"""
🏷️ VERSION MANAGEMENT
======================

Centralized semantic versioning for Freedom Wallet Bot

Author: Freedom Wallet Team
Date: 2026-02-17
"""

# Semantic Version
MAJOR = 2
MINOR = 0
PATCH = 0

# Version String
VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
VERSION_NAME = "Unified Flow Architecture"

# Release Information
RELEASE_DATE = "2026-02-17"
RELEASE_STAGE = "stable"  # alpha | beta | stable | deprecated

# Compatibility
MIN_PYTHON_VERSION = "3.9"
TARGET_PYTHON_VERSION = "3.11"

# Feature Flags
FEATURES = {
    "state_machine": True,
    "roadmap_automation": True,
    "changelog_system": True,
    "unified_flow": True,
    "clean_architecture": False,  # Archived experiment
}

# API Versions
API_VERSION = "v2"
TELEGRAM_BOT_API_MIN = "20.0"

# Database Schema Version
DB_SCHEMA_VERSION = 3  # Migration v3 (56-column schema)

# Build Information
BUILD_NUMBER = 1  # Auto-increment on release
BUILD_HASH = None  # Git commit hash (set by CI/CD)


def get_version_info() -> dict:
    """Get complete version information"""
    return {
        "version": VERSION,
        "name": VERSION_NAME,
        "release_date": RELEASE_DATE,
        "stage": RELEASE_STAGE,
        "python": TARGET_PYTHON_VERSION,
        "api": API_VERSION,
        "db_schema": DB_SCHEMA_VERSION,
        "features": FEATURES,
    }


def print_version():
    """Print version information to console"""
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Freedom Wallet Bot v{VERSION}")
    print(f"  {VERSION_NAME}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Release: {RELEASE_DATE} ({RELEASE_STAGE})")
    print(f"  Python: {TARGET_PYTHON_VERSION}+")
    print(f"  API: {API_VERSION}")
    print(f"  DB Schema: v{DB_SCHEMA_VERSION}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    print_version()
    print("\nActive Features:")
    for feature, enabled in FEATURES.items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {feature}")
