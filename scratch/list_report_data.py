import os
import json

data_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER\frontend\playwright-report\data"
if os.path.exists(data_dir):
    print("Files in data:", os.listdir(data_dir))
    # Search for json files
    for f in os.listdir(data_dir):
        if f.endswith(".json") or f.endswith(".zip"):
            print(f"File: {f}, Size: {os.path.getsize(os.path.join(data_dir, f))} bytes")
else:
    print("Data dir does not exist")
