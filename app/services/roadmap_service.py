"""
🤖 ROADMAP INTEGRATION SERVICE
================================

Automatically sync roadmap updates when AI proposes ideas,
tasks are planned/started/completed, or releases are created.

Integrates with Google Apps Script RoadmapAutoInsert_v2.gs

Author: Freedom Wallet Team
Version: 2.0
Date: 2026-02-17
"""

import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# ROADMAP STATUS TYPES
# ============================================================================

class RoadmapStatus(str, Enum):
    """Roadmap item status types"""
    IDEA = "IDEA"
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REFACTORED = "REFACTORED"
    RELEASED = "RELEASED"
    ARCHITECTURE_UPDATE = "ARCHITECTURE_UPDATE"


class RoadmapType(str, Enum):
    """Roadmap item types"""
    FEATURE = "Tính năng"
    BUG_FIX = "Bug Fix"
    UI_UX = "UI/UX"
    RELEASE = "Release"
    ARCHITECTURE = "Architecture"
    REFACTOR = "Refactor"


# ============================================================================
# ROADMAP SERVICE
# ============================================================================

class RoadmapService:
    """
    Service to interact with Google Apps Script roadmap automation
    
    Usage:
        roadmap = RoadmapService()
        roadmap.insert_item({
            "title": "New Feature",
            "description": "Description",
            "status": RoadmapStatus.IDEA
        })
    """
    
    def __init__(self, apps_script_url: Optional[str] = None):
        """
        Initialize roadmap service
        
        Args:
            apps_script_url: Google Apps Script Web App URL
                           If None, reads from environment variable
        """
        self.apps_script_url = apps_script_url or self._get_url_from_env()
    
    def _get_url_from_env(self) -> str:
        """Get Apps Script URL from environment variable"""
        import os
        url = os.getenv('ROADMAP_APPS_SCRIPT_URL')
        if not url:
            logger.warning("ROADMAP_APPS_SCRIPT_URL not set, roadmap sync disabled")
        return url
    
    def insert_item(
        self,
        title: str,
        description: str,
        status: RoadmapStatus = RoadmapStatus.IDEA,
        item_type: RoadmapType = RoadmapType.FEATURE,
        email: str = "system@freedomwallet.com",
        item_id: Optional[str] = None
    ) -> Dict:
        """
        Insert new roadmap item
        
        Args:
            title: Item title
            description: Item description
            status: Initial status (default: IDEA)
            item_type: Item type (default: FEATURE)
            email: Reporter email
            item_id: Custom ID (auto-generated if None)
        
        Returns:
            Result dict with success status
        """
        if not self.apps_script_url:
            logger.info(f"Roadmap sync disabled: {title}")
            return {"success": False, "message": "Apps Script URL not configured"}
        
        payload = {
            "action": "insertItem",
            "data": {
                "id": item_id,
                "title": title,
                "description": description,
                "type": item_type.value,
                "status": status.value,
                "email": email
            }
        }
        
        try:
            response = requests.post(
                self.apps_script_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Roadmap insert: {title} → {status.value}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Roadmap insert failed: {e}")
            return {"success": False, "message": str(e)}
    
    def update_status(
        self,
        item_id: str,
        new_status: RoadmapStatus,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Update roadmap item status by ID
        
        Args:
            item_id: Item ID (e.g., "FW#123")
            new_status: New status
            notes: Optional notes to append to description
        
        Returns:
            Result dict
        """
        if not self.apps_script_url:
            return {"success": False, "message": "Apps Script URL not configured"}
        
        payload = {
            "action": "updateStatus",
            "data": {
                "id": item_id,
                "newStatus": new_status.value,
                "notes": notes
            }
        }
        
        try:
            response = requests.post(
                self.apps_script_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Roadmap update: {item_id} → {new_status.value}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Roadmap update failed: {e}")
            return {"success": False, "message": str(e)}
    
    def update_by_title(
        self,
        title: str,
        new_status: RoadmapStatus
    ) -> Dict:
        """
        Update roadmap item status by title
        
        Args:
            title: Item title (exact match)
            new_status: New status
        
        Returns:
            Result dict
        """
        if not self.apps_script_url:
            return {"success": False, "message": "Apps Script URL not configured"}
        
        payload = {
            "action": "updateByTitle",
            "data": {
                "title": title,
                "newStatus": new_status.value
            }
        }
        
        try:
            response = requests.post(
                self.apps_script_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Roadmap update: {title} → {new_status.value}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Roadmap update failed: {e}")
            return {"success": False, "message": str(e)}
    
    def log_release(
        self,
        version: str,
        description: str,
        features: List[str]
    ) -> Dict:
        """
        Log a new release version
        
        Args:
            version: Version number (e.g., "v2.0.0")
            description: Release description
            features: List of feature titles included
        
        Returns:
            Result dict
        """
        if not self.apps_script_url:
            return {"success": False, "message": "Apps Script URL not configured"}
        
        payload = {
            "action": "logRelease",
            "data": {
                "version": version,
                "description": description,
                "features": features
            }
        }
        
        try:
            response = requests.post(
                self.apps_script_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Release logged: {version}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Release log failed: {e}")
            return {"success": False, "message": str(e)}


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def sync_ai_idea(title: str, description: str) -> Dict:
    """
    Sync AI-proposed idea to roadmap
    
    Usage:
        sync_ai_idea(
            "AI Budget Recommendations",
            "Auto-suggest budget based on spending patterns"
        )
    """
    service = RoadmapService()
    return service.insert_item(
        title=title,
        description=description,
        status=RoadmapStatus.IDEA,
        item_type=RoadmapType.FEATURE,
        email="ai@freedomwallet.com"
    )


def mark_task_planned(title: str) -> Dict:
    """Mark task as planned (after approval)"""
    service = RoadmapService()
    return service.update_by_title(title, RoadmapStatus.PLANNED)


def mark_task_in_progress(title: str) -> Dict:
    """Mark task as in progress (coding started)"""
    service = RoadmapService()
    return service.update_by_title(title, RoadmapStatus.IN_PROGRESS)


def mark_task_completed(title: str) -> Dict:
    """Mark task as completed (coding finished)"""
    service = RoadmapService()
    return service.update_by_title(title, RoadmapStatus.COMPLETED)


def mark_task_refactored(title: str) -> Dict:
    """Mark task as refactored (code cleanup)"""
    service = RoadmapService()
    return service.update_by_title(title, RoadmapStatus.REFACTORED)


def log_release_version(version: str, description: str, features: List[str]) -> Dict:
    """
    Log release and mark all completed items as released
    
    Usage:
        log_release_version(
            "v2.1.0",
            "Budget AI Release",
            ["AI Budget Recommendations", "Spending Analysis"]
        )
    """
    service = RoadmapService()
    return service.log_release(version, description, features)


# ============================================================================
# CHANGELOG UPDATER
# ============================================================================

def update_changelog(
    version: str,
    description: str,
    added: List[str],
    changed: List[str],
    removed: List[str],
    fixed: List[str]
):
    """
    Update CHANGELOG.md with new release
    
    Args:
        version: Version number (e.g., "v2.1.0")
        description: Release description
        added: List of new features
        changed: List of changes
        removed: List of removed items
        fixed: List of bug fixes
    """
    from pathlib import Path
    
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        logger.error("CHANGELOG.md not found")
        return
    
    # Read current changelog
    current = changelog_path.read_text(encoding='utf-8')
    
    # Prepare new entry
    new_entry = f"""
## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### 📝 {description}

"""
    
    if added:
        new_entry += "### ✨ Added\n\n"
        for item in added:
            new_entry += f"- {item}\n"
        new_entry += "\n"
    
    if changed:
        new_entry += "### 🔄 Changed\n\n"
        for item in changed:
            new_entry += f"- {item}\n"
        new_entry += "\n"
    
    if removed:
        new_entry += "### 🗑️ Removed\n\n"
        for item in removed:
            new_entry += f"- {item}\n"
        new_entry += "\n"
    
    if fixed:
        new_entry += "### 🐛 Fixed\n\n"
        for item in fixed:
            new_entry += f"- {item}\n"
        new_entry += "\n"
    
    new_entry += "---\n"
    
    # Insert after header (find first ## and insert before it)
    lines = current.split('\n')
    insert_index = 0
    
    for i, line in enumerate(lines):
        if line.startswith('## [v'):
            insert_index = i
            break
    
    # Insert new entry
    lines.insert(insert_index, new_entry)
    updated = '\n'.join(lines)
    
    # Write back
    changelog_path.write_text(updated, encoding='utf-8')
    logger.info(f"✅ CHANGELOG.md updated with {version}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example 1: AI proposes an idea
    print("=== Example 1: AI Idea ===")
    result = sync_ai_idea(
        "AI Budget Recommendations",
        "Automatically suggest budget allocation based on spending patterns"
    )
    print(result)
    
    # Example 2: Task approved and planned
    print("\n=== Example 2: Task Planned ===")
    result = mark_task_planned("AI Budget Recommendations")
    print(result)
    
    # Example 3: Development started
    print("\n=== Example 3: In Progress ===")
    result = mark_task_in_progress("AI Budget Recommendations")
    print(result)
    
    # Example 4: Task completed
    print("\n=== Example 4: Completed ===")
    result = mark_task_completed("AI Budget Recommendations")
    print(result)
    
    # Example 5: Log release
    print("\n=== Example 5: Release ===")
    result = log_release_version(
        "v2.1.0",
        "Budget AI Release",
        [
            "AI Budget Recommendations",
            "Spending pattern analysis",
            "Smart budget alerts"
        ]
    )
    print(result)
    
    # Example 6: Update CHANGELOG
    print("\n=== Example 6: Update CHANGELOG ===")
    update_changelog(
        "v2.1.0",
        "Budget AI Release",
        added=[
            "AI-powered budget recommendations",
            "Spending pattern analysis",
            "Smart budget alerts"
        ],
        changed=[
            "Improved AI response time",
            "Enhanced budget tracking UI"
        ],
        removed=[],
        fixed=[
            "Fixed budget calculation rounding errors"
        ]
    )
    print("CHANGELOG updated!")
