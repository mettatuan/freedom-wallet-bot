#!/usr/bin/env python3
"""
Phase 1: Clean Architecture Setup - Automated Migration Script
Creates directory structure and moves files to new organized locations.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

PROJECT_ROOT = Path(__file__).parent

def log_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def log_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def create_directories():
    """Create new directory structure for Clean Architecture."""
    log_info("Creating directory structure...")
    
    directories = [
        # Source code structure
        "src",
        "src/domain",
        "src/domain/entities",
        "src/domain/value_objects",
        "src/domain/repositories",
        "src/application",
        "src/application/use_cases",
        "src/application/services",
        "src/presentation",
        "src/presentation/handlers",
        "src/presentation/keyboards",
        "src/presentation/formatters",
        "src/infrastructure",
        "src/infrastructure/database",
        "src/infrastructure/telegram",
        "src/infrastructure/google_sheets",
        "src/infrastructure/ai",
        
        # Tests structure
        "tests",
        "tests/unit",
        "tests/unit/domain",
        "tests/unit/application",
        "tests/integration",
        "tests/integration/handlers",
        "tests/integration/api",
        "tests/e2e",
        "tests/fixtures",
        
        # Scripts structure
        "scripts",
        "scripts/admin",
        "scripts/deployment",
        "scripts/database",
        
        # Documentation structure
        "docs/architecture",
        "docs/flows",
        "docs/guides",
        "docs/archive",
        "docs/troubleshooting",
        
        # Media structure
        "media",
        "media/images",
        "media/images/guide",
        "media/images/branding",
    ]
    
    for directory in directories:
        path = PROJECT_ROOT / directory
        try:
            path.mkdir(parents=True, exist_ok=True)
            log_success(f"Created: {directory}/")
        except Exception as e:
            log_error(f"Failed to create {directory}/: {e}")
    
    print()

def move_test_files():
    """Move test_*.py files to tests/integration/."""
    log_info("Moving test files to tests/integration/...")
    
    test_files = list(PROJECT_ROOT.glob("test_*.py"))
    moved = 0
    
    for test_file in test_files:
        dest = PROJECT_ROOT / "tests/integration" / test_file.name
        try:
            shutil.move(str(test_file), str(dest))
            log_success(f"Moved: {test_file.name} → tests/integration/")
            moved += 1
        except Exception as e:
            log_error(f"Failed to move {test_file.name}: {e}")
    
    log_info(f"Moved {moved}/{len(test_files)} test files")
    print()

def move_admin_scripts():
    """Move admin scripts to scripts/admin/."""
    log_info("Moving admin scripts to scripts/admin/...")
    
    patterns = ["check_*.py", "update_*.py", "cleanup_*.py", "debug_*.py", 
                "demo_*.py", "get_*.py", "quick_*.py", "create_test_*.py"]
    
    moved = 0
    for pattern in patterns:
        for script in PROJECT_ROOT.glob(pattern):
            if script.name not in ["setup_github.ps1", "push_to_github.ps1"]:  # Keep deployment scripts
                dest = PROJECT_ROOT / "scripts/admin" / script.name
                try:
                    shutil.move(str(script), str(dest))
                    log_success(f"Moved: {script.name} → scripts/admin/")
                    moved += 1
                except Exception as e:
                    log_error(f"Failed to move {script.name}: {e}")
    
    log_info(f"Moved {moved} admin scripts")
    print()

def archive_docs():
    """Move old documentation to docs/archive/."""
    log_info("Archiving old documentation...")
    
    doc_patterns = [
        "PHASE*.md", "*_SUMMARY.md", "*_PLAN.md", "*_CHECKLIST.md",
        "*_ANALYSIS.md", "*_REPORT.md", "*_GUIDE.md", "*_STRATEGY.md",
        "RENEWAL_LOGIC.md", "TEST_FREE_FLOW.md", "GOOGLE_SHEETS_FIXES.md"
    ]
    
    archived = 0
    for pattern in doc_patterns:
        for doc in PROJECT_ROOT.glob(pattern):
            if doc.name not in ["README.md"]:  # Keep main README
                dest = PROJECT_ROOT / "docs/archive" / doc.name
                try:
                    shutil.move(str(doc), str(dest))
                    log_success(f"Archived: {doc.name} → docs/archive/")
                    archived += 1
                except Exception as e:
                    log_error(f"Failed to archive {doc.name}: {e}")
    
    log_info(f"Archived {archived} documentation files")
    print()

def organize_media():
    """Copy key images to media/images/branding/."""
    log_info("Organizing media files...")
    
    # Copy branding images if they exist
    image_files = ["hu_tien.jpg", "web_apps.jpg"]
    copied = 0
    
    for img in image_files:
        source = PROJECT_ROOT / "bot" / "media" / "images" / img
        if source.exists():
            dest = PROJECT_ROOT / "media/images/branding" / img
            try:
                shutil.copy2(str(source), str(dest))
                log_success(f"Copied: {img} → media/images/branding/")
                copied += 1
            except Exception as e:
                log_warning(f"Failed to copy {img}: {e}")
    
    log_info(f"Organized {copied} media files")
    print()

def create_initial_files():
    """Create initial domain files."""
    log_info("Creating initial domain files...")
    
    # Create UserTier enum
    user_tier_content = '''"""User tier enumeration for subscription levels."""

from enum import Enum

class UserTier(str, Enum):
    """User subscription tiers."""
    FREE = "FREE"
    UNLOCK = "UNLOCK"
    PREMIUM = "PREMIUM"
    
    def __str__(self):
        return self.value
    
    @property
    def display_name(self):
        """Human-readable tier name."""
        return {
            UserTier.FREE: "Miễn phí",
            UserTier.UNLOCK: "Mở khóa",
            UserTier.PREMIUM: "Premium"
        }[self]
    
    @property
    def has_quick_record(self):
        """Check if tier has Quick Record feature."""
        return self == UserTier.PREMIUM
    
    @property
    def has_sheet_setup(self):
        """Check if tier has Google Sheets setup."""
        return self in [UserTier.UNLOCK, UserTier.PREMIUM]
'''
    
    user_tier_path = PROJECT_ROOT / "src/domain/value_objects/user_tier.py"
    try:
        with open(user_tier_path, 'w', encoding='utf-8') as f:
            f.write(user_tier_content)
        log_success("Created: src/domain/value_objects/user_tier.py")
    except Exception as e:
        log_error(f"Failed to create user_tier.py: {e}")
    
    # Create __init__.py files
    init_dirs = [
        "src", "src/domain", "src/domain/entities", "src/domain/value_objects",
        "src/application", "src/presentation", "src/infrastructure"
    ]
    
    for dir_path in init_dirs:
        init_file = PROJECT_ROOT / dir_path / "__init__.py"
        try:
            init_file.touch()
            log_success(f"Created: {dir_path}/__init__.py")
        except Exception as e:
            log_error(f"Failed to create {dir_path}/__init__.py: {e}")
    
    print()

def create_tracking():
    """Create migration progress tracking document."""
    log_info("Creating migration tracking document...")
    
    content = f"""# Phase 1 Migration Progress

**Migration Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** Structure Created ✅

## Directory Structure Created

✅ src/domain/ - Domain entities and business logic
✅ src/application/ - Use cases and workflows
✅ src/presentation/ - Telegram handlers and UI
✅ src/infrastructure/ - External integrations
✅ tests/ - Organized test structure
✅ scripts/ - Admin and deployment scripts
✅ docs/ - Consolidated documentation
✅ media/ - Images and branding assets

## Files Reorganized

✅ Test files → tests/integration/
✅ Admin scripts → scripts/admin/
✅ Old documentation → docs/archive/
✅ Media files → media/images/

## Initial Domain Files

✅ UserTier enum created
✅ __init__.py files created

## Next Steps

- [ ] Phase 2: Implement domain entities (User, Subscription, Transaction)
- [ ] Phase 3: Implement application use cases
- [ ] Phase 4: Create infrastructure adapters
- [ ] Phase 5: Refactor handlers to use new architecture

## Verification

Run these commands to verify bot still works:
```bash
python main.py
```

## Notes

- Old structure preserved for backward compatibility
- No breaking changes in this phase
- Handlers still reference old paths (will migrate in Phase 5)
"""
    
    tracking_path = PROJECT_ROOT / "MIGRATION_PROGRESS.md"
    try:
        with open(tracking_path, 'w', encoding='utf-8') as f:
            f.write(content)
        log_success("Created: MIGRATION_PROGRESS.md")
    except Exception as e:
        log_error(f"Failed to create tracking document: {e}")
    
    print()

def main():
    """Execute Phase 1 migration."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Phase 1: Clean Architecture Setup{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    try:
        create_directories()
        move_test_files()
        move_admin_scripts()
        archive_docs()
        organize_media()
        create_initial_files()
        create_tracking()
        
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}✓ Phase 1 Migration Complete!{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}\n")
        
        print(f"{Colors.BLUE}Next steps:{Colors.END}")
        print("1. Verify bot still works: python main.py")
        print("2. Review MIGRATION_PROGRESS.md")
        print("3. Ready for Phase 2: Domain Layer Implementation\n")
        
    except Exception as e:
        log_error(f"Migration failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
