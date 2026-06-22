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
    for r in cur.fetchall():
        if not (r[1].startswith("Benchling") or r[1].startswith("Enterprise")):
            print(f"ID: {r[0]}, Name: {r[1]}, Display: {r[2]}, Type: {r[3]}, Category: {r[4]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
