import os

WORKSPACE_DIR = r"c:\Users\saiki\GENQUANTAA DISCOVER"

EXCLUDE_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".svg", ".webp"}

def fix_paths():
    print("Fixing workspace paths...")
    count = 0
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXCLUDE_EXTS:
                continue
            filepath = os.path.join(root, file)
            if "fix_workspace_paths.py" in filepath:
                continue
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original = content
                updated = False
                
                # Check both backslash and forward slash formats
                if r"c:\Users\saiki\AnalytiX DISCOVER" in content:
                    content = content.replace(r"c:\Users\saiki\AnalytiX DISCOVER", r"c:\Users\saiki\GENQUANTAA DISCOVER")
                    updated = True
                if r"c:/Users/saiki/AnalytiX DISCOVER" in content:
                    content = content.replace(r"c:/Users/saiki/AnalytiX DISCOVER", r"c:/Users/saiki/GENQUANTAA DISCOVER")
                    updated = True
                if r"c:\\Users\\saiki\\AnalytiX DISCOVER" in content:
                    content = content.replace(r"c:\\Users\\saiki\\AnalytiX DISCOVER", r"c:\\Users\\saiki\\GENQUANTAA DISCOVER")
                    updated = True
                
                if updated:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Fixed path in: {os.path.relpath(filepath, WORKSPACE_DIR)}")
                    count += 1
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    print(f"Fixed paths in {count} files.")

if __name__ == "__main__":
    fix_paths()
