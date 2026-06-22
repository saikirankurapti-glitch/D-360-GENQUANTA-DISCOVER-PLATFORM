import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="Saikiran@123",
        database="genquantaa_connector"
    )
    cur = conn.cursor()
    
    print("\nconnection_configs rows:")
    cur.execute("SELECT id, data_source_id, encrypted_credentials, additional_params FROM connector.connection_configs;")
    for r in cur.fetchall():
        print(f"  ID: {r[0]}, Source ID: {r[1]}")
        print(f"    Encrypted Credentials: {r[2]}")
        print(f"    Params: {r[3]}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
