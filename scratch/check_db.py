import os
import psycopg2
from dotenv import load_dotenv

# Load backend/.env
dotenv_path = r"c:\Users\saiki\GENQUANTAA DISCOVER\backend\.env"
load_dotenv(dotenv_path)

db_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL is set: {bool(db_url)}")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Query table row counts
    schemas = ['gen_auth', 'metadata', 'query', 'connector', 'audit', 'lineage', 'bio', 'workflow', 'ai']
    for schema in schemas:
        cur.execute(f"""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
        """, (schema,))
        tables = [r[0] for r in cur.fetchall()]
        print(f"\nSchema: {schema}")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
            cnt = cur.fetchone()[0]
            print(f"  - {table}: {cnt} rows")
            
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
