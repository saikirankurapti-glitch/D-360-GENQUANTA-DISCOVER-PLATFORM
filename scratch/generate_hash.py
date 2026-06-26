import bcrypt

passwd = "AnalytiXDiscover2026!"
hashed = bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt(12))
print("Hashed:", hashed.decode('utf-8'))
