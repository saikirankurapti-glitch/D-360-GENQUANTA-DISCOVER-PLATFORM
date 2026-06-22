import psycopg2
from psycopg2 import sql

conn_str = "postgresql://postgres:Saikiran%40123@localhost:5432/postgres"
try:
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database WHERE datname LIKE 'genquantaa_%' OR datname = 'cheminformatics' OR datname = 'postgres';")
    dbs = [r[0] for r in cur.fetchall()]
    print("Databases found:", dbs)
    
    for db in dbs:
        print(f"\nChecking DB: {db}")
        db_conn_str = f"postgresql://postgres:Saikiran%40123@localhost:5432/{db}"
        try:
            db_conn = psycopg2.connect(db_conn_str)
            db_cur = db_conn.cursor()
            
            # List schemas
            db_cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('pg_catalog', 'information_schema') AND schema_name NOT LIKE 'pg_toast%';")
            schemas = [r[0] for r in db_cur.fetchall()]
            print(f"  Schemas: {schemas}")
            
            # List tables across schemas
            db_cur.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema') 
                  AND table_schema NOT LIKE 'pg_toast%';
            """)
            tables = db_cur.fetchall()
            if not tables:
                print("  No tables found.")
            for table_schema, table_name in tables:
                try:
                    db_cur.execute(sql.SQL("SELECT COUNT(*) FROM {}.{}").format(sql.Identifier(table_schema), sql.Identifier(table_name)))
                    count = db_cur.fetchone()[0]
                    print(f"  Table: {table_schema}.{table_name} - Rows: {count}")
                except Exception as tbl_err:
                    print(f"  Table: {table_schema}.{table_name} - Error: {tbl_err}")
                    db_conn.rollback()
            db_cur.close()
            db_conn.close()
        except Exception as e:
            print(f"  Error connecting or querying {db}: {e}")
            
    cur.close()
    conn.close()
except Exception as e:
    print("Error connecting to postgres default db:", e)
