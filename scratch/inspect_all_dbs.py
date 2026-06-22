import psycopg2

dbs = [
    'genquantaa_auth', 'genquantaa_metadata', 'genquantaa_query', 
    'cheminformatics', 'genquantaa_connector', 'genquantaa_audit', 
    'genquantaa_lineage', 'genquantaa_bioinfo', 'genquantaa_workflow', 'genquantaa_ai'
]

for db in dbs:
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="Saikiran@123",
            database=db
        )
        cur = conn.cursor()
        
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """)
        tables = cur.fetchall()
        print(f"\nDatabase: {db}")
        if not tables:
            print("  (no tables)")
        else:
            for schema, table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
                cnt = cur.fetchone()[0]
                print(f"  - {schema}.{table}: {cnt} rows")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to connect to database {db}: {e}")
