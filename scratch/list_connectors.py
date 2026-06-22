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
    
    print("DATA SOURCES:")
    cur.execute("SELECT id, name, description, connector_type, is_active FROM connector.data_sources;")
    for r in cur.fetchall():
        print(f"  Source ID: {r[0]}, Name: {r[1]}, Type: {r[3]}, Active: {r[4]}")
        
    print("\nENTITIES:")
    cur.execute("SELECT id, data_source_id, physical_name, display_name, description FROM connector.entities;")
    for r in cur.fetchall():
        print(f"  Entity ID: {r[0]}, Source ID: {r[1]}, Physical: {r[2]}, Display: {r[3]}")
        
    print("\nFIELDS:")
    cur.execute("SELECT id, entity_id, physical_name, display_name, data_type, is_primary_key FROM connector.fields;")
    fields = cur.fetchall()
    print(f"  Total fields: {len(fields)}")
    for r in fields[:20]: # print first 20
        print(f"    Field ID: {r[0]}, Entity ID: {r[1]}, Physical: {r[2]}, Type: {r[4]}, PK: {r[5]}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
