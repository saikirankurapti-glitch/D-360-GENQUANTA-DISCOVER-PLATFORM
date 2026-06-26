import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(host="localhost", port="5432", user="postgres", password="Saikiran@123", database="genquantaa_auth")
conn.autocommit = True
cur = conn.cursor(cursor_factory=RealDictCursor)

print("--- All Database Connections ---")
cur.execute("""
    SELECT pid, state, query, age(clock_timestamp(), query_start) as duration, wait_event_type, wait_event
    FROM pg_stat_activity
    WHERE pid <> pg_backend_pid();
""")
for row in cur.fetchall():
    print(f"PID: {row['pid']}, State: {row['state']}, Duration: {row['duration']}")
    print(f"  Query: {row['query'][:200]}")
    print(f"  Wait Event: {row['wait_event_type']} - {row['wait_event']}")

cur.close()
conn.close()
