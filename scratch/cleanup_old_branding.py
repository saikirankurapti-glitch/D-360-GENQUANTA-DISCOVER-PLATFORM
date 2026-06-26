import os

WORKSPACE_DIR = r"c:\Users\saiki\GENQUANTAA DISCOVER"

def cleanup():
    print("Starting cleanup of old branding files...")
    
    # 1. Delete *GENQUANTAA* files in docs/ and frontend/public/docs/
    targets = [
        os.path.join(WORKSPACE_DIR, "docs"),
        os.path.join(WORKSPACE_DIR, "frontend", "public", "docs")
    ]
    
    for target in targets:
        if os.path.exists(target):
            for file in os.listdir(target):
                if "GENQUANTAA" in file:
                    filepath = os.path.join(target, file)
                    os.remove(filepath)
                    print(f"Deleted old branding file: {os.path.relpath(filepath, WORKSPACE_DIR)}")
                    
    # 2. Rename frontend/public/helix_platform.pdf to frontend/public/analytix_platform.pdf
    old_platform_pdf = os.path.join(WORKSPACE_DIR, "frontend", "public", "helix_platform.pdf")
    new_platform_pdf = os.path.join(WORKSPACE_DIR, "frontend", "public", "analytix_platform.pdf")
    
    if os.path.exists(old_platform_pdf):
        if os.path.exists(new_platform_pdf):
            os.remove(new_platform_pdf)
        os.rename(old_platform_pdf, new_platform_pdf)
        print(f"Renamed: public/helix_platform.pdf -> public/analytix_platform.pdf")
        
    print("Cleanup complete.")

if __name__ == "__main__":
    cleanup()
