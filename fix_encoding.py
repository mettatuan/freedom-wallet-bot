"""
Fix encoding issues in Python files - UTF-8 text wrongly interpreted as Latin-1
"""
import os
from pathlib import Path
import re

def has_garbled_text(filepath):
    """Check if file contains garbled Vietnamese text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for typical garbled patterns
        garbled_patterns = [
            'ChÃ', 'báº', 'Ä'', 'â€', 'ðŸ',  # Common garbled Vietnamese
            'Ã¡', 'Ã£', 'Ã¢', 'Ã©', 'Ãª',  # More patterns
            'á»', 'áº', 'Äƒ', 'Äá»"'  # Even more
        ]
        
        return any(pattern in content for pattern in garbled_patterns)
    except:
        return False

def fix_file_encoding(filepath):
    """Fix double-encoding issue: UTF-8 text wrongly interpreted as Latin-1"""
    print(f"Processing: {filepath}")
    
    try:
        # Step 1: Read garbled text as UTF-8 (e.g., "ChÃ o")
        with open(filepath, 'r', encoding='utf-8') as f:
            garbled_content = f.read()
        
        # Step 2: Encode as Latin-1 to get original UTF-8 bytes
        # "ChÃ o" (Latin-1 bytes) -> C3 A0 6F
        utf8_bytes = garbled_content.encode('latin-1')
        
        # Step 3: Decode as UTF-8 to get correct text
        # C3 A0 6F -> "Chào"
        correct_content = utf8_bytes.decode('utf-8')
        
        # Step 4: Write back as UTF-8
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(correct_content)
        
        print(f"  ✅ Fixed: {filepath}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}\n")
    print("🔍 Scanning for files with garbled encoding...\n")
    
    # Find all Python files in app/ directory
    app_dir = project_root / 'app'
    if not app_dir.exists():
        print("❌ app/ directory not found!")
        return
    
    python_files = list(app_dir.rglob('*.py'))
    print(f"📁 Found {len(python_files)} Python files in app/\n")
    
    # Filter files with garbled text
    files_to_fix = []
    for filepath in python_files:
        if has_garbled_text(filepath):
            files_to_fix.append(filepath)
    
    print(f"🎯 Found {len(files_to_fix)} files with garbled encoding\n")
    
    if not files_to_fix:
        print("✅ No files need fixing!")
        return
    
    # Fix each file
    fixed_count = 0
    error_count = 0
    for filepath in files_to_fix:
        relative_path = filepath.relative_to(project_root)
        if fix_file_encoding(str(filepath)):
            fixed_count += 1
        else:
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Fixed:  {fixed_count} files")
    print(f"❌ Errors: {error_count} files")
    print(f"📁 Total:  {len(files_to_fix)} files")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
