import psycopg2

PG_HOST = "localhost"
PG_PORT = "5432"
PG_USER = "postgres"
PG_PASS = "Saikiran@123"

def check_users():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASS,
            database="genquantaa_auth"
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, email, full_name, role, hashed_password FROM gen_auth.users")
        rows = cursor.fetchall()
        print("Users in database:")
        for row in rows:
            print(f"ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Role: {row[3]}, Hash: {row[4]}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error checking users: {e}")

if __name__ == "__main__":
    check_users()
