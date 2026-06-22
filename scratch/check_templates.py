import os
import json
from sqlalchemy import create_engine, text

# Get database URL from env or fallback
db_url = "postgresql://postgres:Saikiran@123@localhost:5432/genquantaa_query"
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, layout_json FROM query_templates"))
    for row in result:
        print(f"Template ID: {row[0]}")
        print(f"Name: {row[1]}")
        try:
            layout = json.loads(row[2])
            print("Nodes:")
            for node in layout.get("nodes", []):
                print(f"  Node ID: {node.get('id')}, Data: {node.get('data')}")
            print("Edges:")
            for edge in layout.get("edges", []):
                print(f"  Edge: {edge.get('source')} -> {edge.get('target')}")
        except Exception as e:
            print(f"  Error parsing layout_json: {e}")
        print("-" * 50)
