import bcrypt
import psycopg2

PG_HOST = "localhost"
PG_PORT = "5432"
PG_USER = "postgres"
PG_PASS = "Saikiran@123"

def update_passwords():
    # Hash "AnalytiXDiscover2026!"
    password = "AnalytiXDiscover2026!"
    salt = bcrypt.gensalt()
    new_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    print(f"Generated new hash: {new_hash}")
    
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASS,
            database="genquantaa_auth"
        )
        cursor = conn.cursor()
        
        # Update admin@analytix.com
        cursor.execute(
            "UPDATE gen_auth.users SET hashed_password = %s WHERE email = %s",
            (new_hash, "admin@analytix.com")
        )
        print(f"Updated admin@analytix.com rows: {cursor.rowcount}")
        
        # Update scientist@analytix.com
        cursor.execute(
            "UPDATE gen_auth.users SET hashed_password = %s WHERE email = %s",
            (new_hash, "scientist@analytix.com")
        )
        print(f"Updated scientist@analytix.com rows: {cursor.rowcount}")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Successfully updated database passwords.")
    except Exception as e:
        print(f"Error updating passwords: {e}")

if __name__ == "__main__":
    update_passwords()
