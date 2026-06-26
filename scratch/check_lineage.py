import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="Saikiran@123",
    database="genquantaa_lineage"
)
cur = conn.cursor()

# List tables in genquantaa_lineage database
cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog');")
tables = cur.fetchall()
print("Tables in genquantaa_lineage:", tables)

for schema, name in tables:
    cur.execute(f"SELECT COUNT(*) FROM {schema}.{name};")
    count = cur.fetchone()[0]
    print(f"Row count in {schema}.{name}: {count}")

conn.close()
