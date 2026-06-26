import os

WORKSPACE_DIR = r"c:\Users\saiki\GENQUANTAA DISCOVER"
EXCLUDE_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".svg", ".webp", ".db", ".log"}

def search_remaining():
    print("Searching for remaining references...")
    results = []
    
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXCLUDE_EXTS:
                continue
                
            filepath = os.path.join(root, file)
            if "search_remaining.py" in filepath or "rebrand_to_analytix.py" in filepath or "rebrand.py" in filepath or "remaining_references.txt" in filepath:
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for idx, line in enumerate(lines):
                    # Check for occurrences
                    if "helix" in line.lower() or "genquantaa" in line.lower():
                        relpath = os.path.relpath(filepath, WORKSPACE_DIR)
                        results.append(f"{relpath}:{idx + 1}: {line.strip()}")
            except Exception as e:
                pass
                
    output_path = os.path.join(WORKSPACE_DIR, "scratch", "remaining_references.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Found {len(results)} remaining references:\n\n")
        for res in results:
            f.write(res + "\n")
            
    print(f"Audit completed. Found {len(results)} remaining references. Saved results to scratch/remaining_references.txt.")

if __name__ == "__main__":
    search_remaining()
