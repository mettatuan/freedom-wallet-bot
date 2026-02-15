"""
Fix encoding issues in Python files - UTF-8 text wrongly interpreted as Latin-1
"""
import os
from pathlib import Path

def has_garbled_text(filepath):
    """Check if file contains garbled Vietnamese text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for typical garbled byte sequences
        # These are UTF-8 Vietnamese characters interpreted as Latin-1
        garbled_indicators = [
            '\xc3\xa0',  # à as 2 chars
            '\xe1\xba',  # Vietnamese diacritics 
            '\xc4\x91',  # đ as 2 chars
        ]
        
        # Check if any garbled pattern exists
        for indicator in garbled_indicators:
            if indicator in content:
                return True
        
        return False
    except:
        return False

def fix_file_encoding(filepath):
    """Fix double-encoding issue: UTF-8 text wrongly interpreted as Latin-1"""
    
    try:
        # Read garbled text as UTF-8
        with open(filepath, 'r', encoding='utf-8') as f:
            garbled_content = f.read()
        
        # Encode as Latin-1 to get original UTF-8 bytes
        utf8_bytes = garbled_content.encode('latin-1')
        
        # Decode as UTF-8 to get correct text
        correct_content = utf8_bytes.decode('utf-8')
        
        # Write back as UTF-8
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(correct_content)
        
        return True, "OK"
        
    except Exception as e:
        return False, str(e)

def main():
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}\n")
    print("Scanning for files with garbled encoding...\n")
    
    # Find all Python files in app/ directory
    app_dir = project_root / 'app'
    if not app_dir.exists():
        print("ERROR: app/ directory not found!")
        return
    
    python_files = list(app_dir.rglob('*.py'))
    print(f"Found {len(python_files)} Python files in app/\n")
    
    # Filter files with garbled text
    files_to_fix = []
    for filepath in python_files:
        if has_garbled_text(filepath):
            files_to_fix.append(filepath)
            print(f"  [GARBLED] {filepath.relative_to(project_root)}")
    
    print(f"\nFound {len(files_to_fix)} files with garbled encoding\n")
    
    if not files_to_fix:
        print("No files need fixing!")
        return
    
    # Confirm before fixing
    print("=" * 60)
    print(f"About to fix {len(files_to_fix)} files")
    print("=" * 60)
    
    # Fix each file
    fixed_count = 0
    error_count = 0
    errors = []
    
    for filepath in files_to_fix:
        relative_path = filepath.relative_to(project_root)
        success, message = fix_file_encoding(str(filepath))
        
        if success:
            print(f"  [OK] {relative_path}")
            fixed_count += 1
        else:
            print(f"  [ERROR] {relative_path}: {message}")
            error_count += 1
            errors.append((relative_path, message))
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Fixed:  {fixed_count} files")
    print(f"Errors: {error_count} files")
    print(f"Total:  {len(files_to_fix)} files")
    
    if errors:
        print(f"\nERROR DETAILS:")
        for path, msg in errors:
            print(f"  {path}: {msg}")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
