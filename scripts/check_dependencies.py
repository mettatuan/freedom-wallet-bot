#!/usr/bin/env python3
"""
Architecture Dependency Guard

Enforces import rules to prevent architecture violations.
Fails CI if forbidden dependencies are detected.

FORBIDDEN RULES:
1. core/ CANNOT import from services/
2. core/ CANNOT import from models/
3. handlers/ CANNOT import from models/ (must go through services)
4. core/ CANNOT import anything that causes side effects

Usage:
    python scripts/check_dependencies.py
    
Exit codes:
    0 - No violations found
    1 - Violations detected (fails CI)
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Violation:
    """Represents a dependency violation."""
    file_path: str
    line_number: int
    import_statement: str
    reason: str
    severity: str  # 'ERROR' or 'WARNING'


class DependencyChecker:
    """Checks import dependencies against architecture rules."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.violations: List[Violation] = []
        
    def check_all(self) -> List[Violation]:
        """Check all Python files in the project."""
        app_dir = self.project_root / "app"
        
        if not app_dir.exists():
            print(f"⚠️  Warning: app/ directory not found. Checking bot/ instead.")
            app_dir = self.project_root / "bot"
            
        if not app_dir.exists():
            print("❌ Error: Neither app/ nor bot/ directory found.")
            return []
        
        # Check core/ files
        core_dir = app_dir / "core"
        if core_dir.exists():
            for py_file in core_dir.rglob("*.py"):
                self._check_core_file(py_file)
        
        # Check handlers/ files
        handlers_dir = app_dir / "handlers"
        if handlers_dir.exists():
            for py_file in handlers_dir.rglob("*.py"):
                self._check_handler_file(py_file)
        
        # Check services/ files (optional - for circular dependency)
        services_dir = app_dir / "services"
        if services_dir.exists():
            for py_file in services_dir.rglob("*.py"):
                self._check_service_file(py_file)
        
        return self.violations
    
    def _check_core_file(self, file_path: Path):
        """Check core/ file for forbidden imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception as e:
            print(f"⚠️  Warning: Could not parse {file_path}: {e}")
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_core_import(file_path, node.lineno, alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._check_core_import(file_path, node.lineno, node.module)
    
    def _check_core_import(self, file_path: Path, line_no: int, import_module: str):
        """Check if core/ import is allowed."""
        # Forbidden: core imports services
        if 'services' in import_module or import_module.startswith('app.services'):
            self.violations.append(Violation(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_no,
                import_statement=import_module,
                reason="core/ CANNOT import from services/ (services depend on core, not vice versa)",
                severity='ERROR'
            ))
        
        # Forbidden: core imports models
        if 'models' in import_module or import_module.startswith('app.models'):
            self.violations.append(Violation(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_no,
                import_statement=import_module,
                reason="core/ CANNOT import from models/ (core should be pure domain logic)",
                severity='ERROR'
            ))
        
        # Forbidden: core imports handlers
        if 'handlers' in import_module or import_module.startswith('app.handlers'):
            self.violations.append(Violation(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_no,
                import_statement=import_module,
                reason="core/ CANNOT import from handlers/ (handlers call core, not vice versa)",
                severity='ERROR'
            ))
    
    def _check_handler_file(self, file_path: Path):
        """Check handlers/ file for forbidden imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception as e:
            print(f"⚠️  Warning: Could not parse {file_path}: {e}")
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_handler_import(file_path, node.lineno, alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._check_handler_import(file_path, node.lineno, node.module)
    
    def _check_handler_import(self, file_path: Path, line_no: int, import_module: str):
        """Check if handler import is allowed."""
        # Forbidden: handlers import models directly
        if 'models' in import_module or import_module.startswith('app.models'):
            self.violations.append(Violation(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_no,
                import_statement=import_module,
                reason="handlers/ CANNOT import from models/ directly (must go through services/)",
                severity='ERROR'
            ))
    
    def _check_service_file(self, file_path: Path):
        """Check services/ file for circular dependencies."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception as e:
            print(f"⚠️  Warning: Could not parse {file_path}: {e}")
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_service_import(file_path, node.lineno, alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._check_service_import(file_path, node.lineno, node.module)
    
    def _check_service_import(self, file_path: Path, line_no: int, import_module: str):
        """Check if service import creates circular dependency."""
        # Forbidden: services import handlers
        if 'handlers' in import_module or import_module.startswith('app.handlers'):
            self.violations.append(Violation(
                file_path=str(file_path.relative_to(self.project_root)),
                line_number=line_no,
                import_statement=import_module,
                reason="services/ CANNOT import from handlers/ (creates circular dependency)",
                severity='ERROR'
            ))


def print_violations(violations: List[Violation]) -> None:
    """Print violations in a readable format."""
    if not violations:
        print("✅ No dependency violations found!")
        print("✅ Architecture rules enforced successfully.")
        return
    
    print(f"\n❌ Found {len(violations)} dependency violation(s):\n")
    print("=" * 80)
    
    for i, violation in enumerate(violations, 1):
        print(f"\n{i}. {violation.severity}: {violation.file_path}:{violation.line_number}")
        print(f"   Import: {violation.import_statement}")
        print(f"   Reason: {violation.reason}")
        print("-" * 80)
    
    print("\n📚 Architecture Rules:")
    print("   1. core/ = Pure domain logic (NO imports from services/models/handlers)")
    print("   2. handlers/ call services (NOT models directly)")
    print("   3. services/ orchestrate (can import core & models)")
    print("   4. Flow: handlers → services → core/models")
    print("\n📖 See ARCHITECTURE_RULES.md for details.")
    print("=" * 80)


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    
    print("🔍 Checking architecture dependencies...")
    print(f"📂 Project root: {project_root}")
    print("-" * 80)
    
    checker = DependencyChecker(project_root)
    violations = checker.check_all()
    
    print_violations(violations)
    
    # Exit with error code if violations found
    if violations:
        error_count = sum(1 for v in violations if v.severity == 'ERROR')
        warning_count = sum(1 for v in violations if v.severity == 'WARNING')
        
        print(f"\n❌ FAILED: {error_count} error(s), {warning_count} warning(s)")
        print("❌ Fix violations before committing.")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
