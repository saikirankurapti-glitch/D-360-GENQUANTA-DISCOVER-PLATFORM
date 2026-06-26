import os

results_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER\frontend\test-results"
if os.path.exists(results_dir):
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file == "error-context.md" or file == "stderr.txt" or file.endswith(".txt"):
                path = os.path.join(root, file)
                print(f"\n=================== {path.replace(results_dir, '')} ===================")
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        print(f.read())
                except Exception as e:
                    print("Error reading:", e)
else:
    print("test-results dir not found")
