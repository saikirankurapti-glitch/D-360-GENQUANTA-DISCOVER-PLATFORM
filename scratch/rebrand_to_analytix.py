import os
import re
import shutil

WORKSPACE_DIR = r"c:\Users\saiki\GENQUANTAA DISCOVER"

# Excluded directories and file patterns
EXCLUDE_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__", ".pytest_cache"}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico", ".svg", ".webp", ".woff", ".woff2", ".eot", ".ttf"}

REPLACEMENTS = [
    # Taglines and full product names first to avoid partial replacement issues
    ("AI-Powered Scientific Informatics Platform", "AI-Powered Scientific Intelligence Platform"),
    ("Scientific Informatics Platform", "AI-Powered Scientific Intelligence Platform"),
    ("GENQUANTAA Helix Analytics Suite", "AnalytiX Analytics Suite"),
    ("GENQUANTAA Helix Platform", "AnalytiX Platform"),
    ("GENQUANTAA HELIX Platform", "AnalytiX Platform"),
    ("GenQuantaa Helix Platform", "AnalytiX Platform"),
    ("GENQUANTAA Helix", "AnalytiX"),
    ("GENQUANTAA HELIX", "AnalytiX"),
    ("GenQuantaa Helix", "AnalytiX"),
    ("Helix Platform", "AnalytiX Platform"),
    ("Helix Analytics", "AnalytiX Analytics"),
    
    # Service titles in FastAPI config
    ("Helix Metadata Catalog Service", "AnalytiX Metadata Catalog Service"),
    ("Helix Lineage Service", "AnalytiX Lineage Service"),
    ("Helix Data Connector Service", "AnalytiX Data Connector Service"),
    ("Helix Bioinformatics Service", "AnalytiX Bioinformatics Service"),
    ("Helix Cheminformatics Service", "AnalytiX Cheminformatics Service"),
    ("Helix Audit Service", "AnalytiX Audit Service"),
    ("Helix Auth Service", "AnalytiX Auth Service"),
    
    # Generic brand names (case sensitive check)
    ("GENQUANTAA", "AnalytiX"),
    ("GenQuantaa", "AnalytiX"),
    
    # PDF manuals and documentation filenames
    ("GENQUANTAA_USER_MANUAL.pdf", "ANALYTIX_USER_MANUAL.pdf"),
    ("GENQUANTAA_QUICK_START_GUIDE.pdf", "ANALYTIX_QUICK_START_GUIDE.pdf"),
    ("GENQUANTAA_ADMIN_GUIDE.pdf", "ANALYTIX_ADMIN_GUIDE.pdf"),
    ("GENQUANTAA_AI_COPILOT_GUIDE.pdf", "ANALYTIX_AI_COPILOT_GUIDE.pdf"),
    ("GENQUANTAA_E2E_TEST_REPORT.pdf", "ANALYTIX_E2E_TEST_REPORT.pdf"),
    ("GENQUANTAA_USER_MANUAL.md", "ANALYTIX_USER_MANUAL.md"),
    
    # Other filenames/links
    ("helix_platform.pdf", "analytix_platform.pdf"),
    ("discovery_platform.pdf", "analytix_platform.pdf"),
    
    # Email and server domains
    ("@genquantaa.com", "@analytix.com"),
    ("smtp.genquantaa.com", "smtp.analytix.com"),
    ("lab-alert@genquantaa.com", "lab-alert@analytix.com"),
]

modified_files = []

def run_rebranding():
    print("Starting rebranding migration...")
    
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        # Filter out excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXCLUDE_EXTS:
                continue
                
            filepath = os.path.join(root, file)
            
            # Skip current script and existing rebrand.py
            if "rebrand_to_analytix.py" in filepath or "rebrand.py" in filepath:
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                original_content = content
                updated = False
                
                # Perform replacements
                for old_str, new_str in REPLACEMENTS:
                    if old_str in content:
                        content = content.replace(old_str, new_str)
                        updated = True
                
                if updated:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated file: {os.path.relpath(filepath, WORKSPACE_DIR)}")
                    modified_files.append(os.path.relpath(filepath, WORKSPACE_DIR))
                    
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

    # Explicitly rename the Playwright test file
    old_test_file = os.path.join(WORKSPACE_DIR, "frontend", "tests", "helix.spec.ts")
    new_test_file = os.path.join(WORKSPACE_DIR, "frontend", "tests", "analytix.spec.ts")
    if os.path.exists(old_test_file):
        shutil.move(old_test_file, new_test_file)
        print(f"Renamed test file: frontend/tests/helix.spec.ts -> frontend/tests/analytix.spec.ts")
        modified_files.append("frontend/tests/analytix.spec.ts")

    print("\nRebranding complete.")
    print(f"Total files modified/renamed: {len(modified_files)}")

if __name__ == "__main__":
    run_rebranding()
