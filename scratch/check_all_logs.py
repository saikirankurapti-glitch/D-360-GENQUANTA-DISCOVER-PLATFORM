import os

logs_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER\logs"
for filename in os.listdir(logs_dir):
    if filename.endswith(".log"):
        path = os.path.join(logs_dir, filename)
        print(f"\n=================== {filename} ===================")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(line.strip())
        except Exception as e:
            print(f"Error reading {filename}: {e}")
