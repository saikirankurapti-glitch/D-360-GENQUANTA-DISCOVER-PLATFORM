import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

PG_HOST = "localhost"
PG_PORT = "5432"
PG_USER = "postgres"
PG_PASS = "Saikiran@123"

databases = [
    "genquantaa_auth",
    "genquantaa_metadata",
    "genquantaa_query",
    "cheminformatics",
    "genquantaa_connector",
    "genquantaa_audit",
    "genquantaa_lineage",
    "genquantaa_bioinfo",
    "genquantaa_workflow",
    "genquantaa_ai"
]

def inspect_db():
    for db_name in databases:
        print(f"\n=========================================")
        print(f"DATABASE: {db_name}")
        print(f"=========================================")
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=PG_PASS,
                database=db_name
            )
            cursor = conn.cursor()
            
            # Get list of schemas
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            """)
            schemas = [row[0] for row in cursor.fetchall()]
            print(f"Schemas: {schemas}")
            
            # Get list of tables and their row counts
            for schema in schemas:
                cursor.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = '{schema}' AND table_type = 'BASE TABLE'
                """)
                tables = [row[0] for row in cursor.fetchall()]
                print(f"  Schema '{schema}' Tables:")
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {schema}.\"{table}\"")
                        count = cursor.fetchone()[0]
                        print(f"    - {table}: {count} rows")
                    except Exception as te:
                        print(f"    - {table}: error counting rows ({te})")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error connecting/inspecting {db_name}: {e}")

if __name__ == "__main__":
    inspect_db()
