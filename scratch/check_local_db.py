import os
import psycopg2

try:
    # Try connecting to default postgres database first
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="Saikiran@123",
        database="postgres"
    )
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database;")
    dbs = [r[0] for r in cur.fetchall()]
    print("Databases in local PostgreSQL:", dbs)
    cur.close()
    conn.close()
except Exception as e:
    print(f"Failed to connect to local PG: {e}")
