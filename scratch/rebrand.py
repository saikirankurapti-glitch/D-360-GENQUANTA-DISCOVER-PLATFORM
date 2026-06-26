import os
import re

def rebrand():
    root_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER"
    
    # 1. Define exact string replacements
    replacements = [
        # Product/Platform names
        ("GENQUANTAA Discover Platform", "GENQUANTAA Helix Platform"),
        ("GENQUANTAA Discover", "GENQUANTAA Helix"),
        ("GENQUANTAA DISCOVER", "GENQUANTAA HELIX"),
        ("Discover Platform", "GENQUANTAA Helix"),
        ("discovery_platform.pdf", "helix_platform.pdf"),
        
        # Service Names in configs
        ("Discover Metadata Catalog Service", "Helix Metadata Catalog Service"),
        ("Discover Lineage Service", "Helix Lineage Service"),
        ("Discover Data Connector Service", "Helix Data Connector Service"),
        ("Discover Bioinformatics Service", "Helix Bioinformatics Service"),
        ("Discover Cheminformatics Service", "Helix Cheminformatics Service"),
        ("Discover Audit Service", "Helix Audit Service"),
        ("Discover Auth Service", "Helix Auth Service"),
        
        # Other references
        ("genquantaa-discover", "genquantaa-helix"),
    ]
    
    # We should be careful with "Discover" by itself to avoid replacing "discovery" or "discover_schema".
    # Therefore, let's also do a word boundary replace for "Discover" when it is not part of code variables.
    # The list above covers most brand occurrences.
    
    # Files to process (extensions to search)
    valid_exts = {".py", ".json", ".md", ".txt", ".html", ".css", ".ts", ".tsx", ".ps1"}
    exclude_dirs = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
    
    modified_files = []
    
    # Walk directory
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # Skip the rebrand script itself
            if filename == "rebrand.py":
                continue
                
            _, ext = os.path.splitext(filename)
            if ext not in valid_exts:
                continue
                
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                original_content = content
                
                # Apply replacements
                for old, new in replacements:
                    content = content.replace(old, new)
                
                # Special replacement for login page tagline
                if filename == "LoginPage.tsx":
                    # Update tagline to "The AI Operating System for Drug Discovery"
                    content = content.replace(
                        '<p className="text-xs text-slate-400 mt-1 uppercase tracking-widest">Scientific Informatics Platform</p>',
                        '<p className="text-xs text-slate-400 mt-1 uppercase tracking-widest">AI-Powered Scientific Informatics Platform</p>'
                    )
                
                # Save if modified
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    modified_files.append(file_path)
                    print(f"[REBRAND] Updated: {os.path.relpath(file_path, root_dir)}")
                    
            except Exception as e:
                print(f"[ERROR] Failed to process {file_path}: {e}")
                
    # 2. File Renaming
    renames = [
        (
            os.path.join(root_dir, "frontend", "tests", "discover.spec.ts"),
            os.path.join(root_dir, "frontend", "tests", "helix.spec.ts")
        ),
        (
            os.path.join(root_dir, "frontend", "public", "discovery_platform.pdf"),
            os.path.join(root_dir, "frontend", "public", "helix_platform.pdf")
        )
    ]
    
    for old_path, new_path in renames:
        if os.path.exists(old_path):
            try:
                if os.path.exists(new_path):
                    os.remove(new_path)
                os.rename(old_path, new_path)
                print(f"[RENAME] Renamed {os.path.relpath(old_path, root_dir)} to {os.path.relpath(new_path, root_dir)}")
                modified_files.append(new_path)
            except Exception as e:
                print(f"[ERROR] Failed to rename {old_path}: {e}")
        else:
            print(f"[WARNING] Rename source not found: {os.path.relpath(old_path, root_dir)}")
            
    print(f"\nRebranding completed. Modified/Created {len(modified_files)} files.")

if __name__ == "__main__":
    rebrand()
