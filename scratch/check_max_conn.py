import psycopg2

conn = psycopg2.connect(host="localhost", port="5432", user="postgres", password="Saikiran@123", database="genquantaa_auth")
cur = conn.cursor()
cur.execute("show max_connections;")
print("Max Connections:", cur.fetchone()[0])
cur.execute("select count(*) from pg_stat_activity;")
print("Current Connections:", cur.fetchone()[0])
cur.close()
conn.close()
