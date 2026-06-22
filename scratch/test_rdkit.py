import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="Saikiran@123",
        database="cheminformatics"
    )
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'rdkit';")
    rdkit_exists = cur.fetchone() is not None
    print(f"RDKit extension exists in cheminformatics DB: {rdkit_exists}")
    
    # Let's check table columns of connector.compounds
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema='connector' AND table_name='compounds';
    """)
    print("connector.compounds columns:")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")
        
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
