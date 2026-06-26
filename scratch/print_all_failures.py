import os
import re

results_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER\frontend\test-results"
if os.path.exists(results_dir):
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file == "error-context.md":
                path = os.path.join(root, file)
                print(f"\n=================== {os.path.basename(os.path.dirname(path))} ===================")
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        
                        # Extract Test info and Error details
                        test_info = re.search(r"# Test info\s*(.*?)\s*(?=#|$)", content, re.DOTALL)
                        error_details = re.search(r"# Error details\s*(.*?)\s*(?=#|$)", content, re.DOTALL)
                        
                        if test_info:
                            print("TEST INFO:\n", test_info.group(1).strip())
                        if error_details:
                            print("ERROR DETAILS:\n", error_details.group(1).strip()[:1000])
                except Exception as e:
                    print("Error reading:", e)
else:
    print("test-results dir not found")
