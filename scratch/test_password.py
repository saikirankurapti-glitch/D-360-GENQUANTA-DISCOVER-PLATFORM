import bcrypt

hashed_pwd = b"$2b$12$6K/z5T.U7i2Fmgp.mB199O1X/qVzE.W4G8oex1XQy3ZtN3t32UreS"

passwords = ["AnalytiXDiscover2026!", "Saikiran@123", "postgres", "admin", "password"]
for pwd in passwords:
    match = bcrypt.checkpw(pwd.encode('utf-8'), hashed_pwd)
    print(f"Verify '{pwd}': {match}")
