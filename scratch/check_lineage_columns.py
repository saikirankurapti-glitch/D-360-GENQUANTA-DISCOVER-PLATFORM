import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port="5432",
    user="postgres",
    password="Saikiran@123",
    database="genquantaa_lineage"
)
cur = conn.cursor()

for table in ["lineage_nodes", "lineage_edges"]:
    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'lineage' AND table_name = '{table}';")
    print(f"Columns for {table}:", cur.fetchall())

conn.close()
