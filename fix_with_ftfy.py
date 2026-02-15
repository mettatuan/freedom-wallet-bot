"""
Fix encoding issues using ftfy library
"""
import ftfy
from pathlib import Path

def fix_file_with_ftfy(filepath):
    """Fix encoding issues using ftfy"""
    
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Fix encoding with ftfy
        fixed_content = ftfy.fix_text(content)
        
        # Only write if changed
        if fixed_content != content:
            with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(fixed_content)
            return True, "Fixed"
        else:
            return True, "No changes needed"
        
    except Exception as e:
        return False, str(e)

def main():
    project_root = Path(__file__).parent
    print(f"Project root: {project_root}\n")
    
    # Find all Python files in app/
    app_dir = project_root / 'app'
    python_files = list(app_dir.rglob('*.py'))
    
    print(f"Found {len(python_files)} Python files\n")
    print("=" * 60)
    
    fixed_count = 0
    unchanged_count = 0
    error_count = 0
    
    for filepath in python_files:
        relative_path = filepath.relative_to(project_root)
        success, message = fix_file_with_ftfy(str(filepath))
        
        if success:
            if "Fixed" in message:
                print(f"  [FIXED] {relative_path}")
                fixed_count += 1
            else:
                unchanged_count += 1
        else:
            print(f"  [ERROR] {relative_path}: {message}")
            error_count += 1
    
    print("=" * 60)
    print(f"\nSUMMARY:")
    print(f"  Fixed:     {fixed_count} files")
    print(f"  Unchanged: {unchanged_count} files")
    print(f"  Errors:    {error_count} files")
    print(f"  Total:     {len(python_files)} files\n")

if __name__ == "__main__":
    main()
