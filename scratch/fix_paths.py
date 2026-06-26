import os

def fix_paths():
    root_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER"
    
    # Files to process
    valid_exts = {".py", ".json", ".md", ".txt", ".html", ".css", ".ts", ".tsx", ".ps1"}
    exclude_dirs = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
    
    modified_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if filename == "fix_paths.py":
                continue
                
            _, ext = os.path.splitext(filename)
            if ext not in valid_exts:
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Replace incorrect path with the actual workspace folder
                target = r"c:\Users\saiki\AnalytiX"
                replacement = r"c:\Users\saiki\GENQUANTAA DISCOVER"
                
                if target in content or target.replace("\\", "\\\\") in content:
                    content = content.replace(target, replacement)
                    content = content.replace(target.replace("\\", "\\\\"), replacement.replace("\\", "\\\\"))
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    modified_count += 1
                    print(f"[FIX PATH] Fixed: {os.path.relpath(file_path, root_dir)}")
            except Exception as e:
                print(f"[ERROR] Failed {file_path}: {e}")
                
    print(f"Path correction complete. Fixed {modified_count} files.")

if __name__ == "__main__":
    fix_paths()
