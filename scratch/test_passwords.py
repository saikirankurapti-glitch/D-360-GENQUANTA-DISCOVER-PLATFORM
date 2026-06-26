import bcrypt

hash_val = "$2b$12$6K/z5T.U7i2Fmgp.mB199O1X/qVzE.W4G8oex1XQy3ZtN3t32UreS"
passwords = [
    "AnalytiXDiscover2026!",
    "Saikiran@123",
    "admin",
    "admin123",
    "password",
    "password123",
    "DiscoverySafetyPIN2026!",
    "admin@analytix.com",
    "scientist@analytix.com",
    "Dr. Sarah Connor",
    "Dr. John Connor"
]

for p in passwords:
    try:
        if bcrypt.checkpw(p.encode('utf-8'), hash_val.encode('utf-8')):
            print(f"MATCH FOUND: {p}")
            break
    except Exception as e:
        print(f"Error checking {p}: {e}")
else:
    print("No match found in local test list.")
