import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="Saikiran@123",
        database="genquantaa_metadata"
    )
    cur = conn.cursor()
    cur.execute("SELECT id, name, display_name, data_type, category FROM metadata.metadata_fields;")
    fields = cur.fetchall()
    print("Metadata fields:")
    for f in fields:
         print(f"  ID: {f[0]}, Name: {f[1]}, Display: {f[2]}, Type: {f[3]}, Category: {f[4]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
