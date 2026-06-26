with open(r"c:\Users\saiki\GENQUANTAA DISCOVER\logs\auth_service.log", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
print(f"Total log lines: {len(lines)}")
print("Last 100 lines:")
for line in lines[-100:]:
    print(line.strip())
