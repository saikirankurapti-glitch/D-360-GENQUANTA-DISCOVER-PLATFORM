with open(r"c:\Users\saiki\GENQUANTAA DISCOVER\backend\db\seed_data.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "lineage" in line.lower():
            print(f"Line {i}: {line.strip()}")
