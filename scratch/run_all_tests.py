import subprocess
import os

services = [
    "auth_service",
    "metadata_service",
    "query_service",
    "cheminformatics_service",
    "connector_service",
    "audit_service",
    "lineage_service",
    "bioinformatics_service",
    "workflow_service",
    "ai_service"
]

base_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER"
venv_pytest = os.path.join(base_dir, ".venv", "Scripts", "pytest")

for svc in services:
    svc_test_path = os.path.join(base_dir, "backend", "services", svc, "tests")
    if not os.path.exists(svc_test_path):
        print(f"[{svc}] No tests directory found.")
        continue
        
    print(f"\n================ Running tests for {svc} ================")
    try:
        # Set environment variables if needed
        env = os.environ.copy()
        # Run pytest
        res = subprocess.run([venv_pytest, svc_test_path], capture_output=True, text=True, env=env)
        print(f"Status: {'PASSED' if res.returncode == 0 else 'FAILED'}")
        if res.returncode != 0:
            # print first 20 lines of stderr or stdout
            lines = res.stdout.splitlines()
            for l in lines[:30]:
                print("  ", l)
            if len(lines) > 30:
                print("   ...")
    except Exception as e:
        print(f"[{svc}] Execution error: {e}")
