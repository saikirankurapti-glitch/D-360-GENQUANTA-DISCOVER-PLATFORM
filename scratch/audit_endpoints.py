import os
import sys
import json
import sqlite3
import urllib.parse
import requests
from pathlib import Path
from sqlalchemy import create_engine, text

# Setup project directories
SCRATCH_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRATCH_DIR.parent
VENV_PYTHON = WORKSPACE_DIR / ".venv" / "Scripts" / "python.exe"

PG_HOST = "localhost"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASS = "Saikiran@123"

# Services to DB name mappings
SERVICES_DBS = {
    "auth": "genquantaa_auth",
    "metadata": "genquantaa_metadata",
    "query": "genquantaa_query",
    "chemistry": "cheminformatics",
    "connectors": "genquantaa_connector",
    "audit": "genquantaa_audit",
    "lineage": "genquantaa_lineage",
    "bioinformatics": "genquantaa_bioinfo",
    "workflow": "genquantaa_workflow",
    "ai": "genquantaa_ai"
}

SERVICES_SCHEMAS = {
    "auth": ("gen_auth", ["users", "roles", "permissions"]),
    "metadata": ("metadata", ["metadata_entities", "metadata_fields", "metadata_relationships", "metadata_versions", "metadata_sync_history"]),
    "query": ("query", ["query_templates", "query_history"]),
    "chemistry": ("connector", ["compounds"]),
    "connectors": ("connector", ["data_sources", "connection_configs"]),
    "audit": ("audit", ["audit_logs", "electronic_signatures"]),
    "lineage": ("lineage", ["lineage_nodes", "lineage_edges"]),
    "bioinformatics": ("bio", ["sequences", "alignments"]),
    "workflow": ("workflow", ["workflow_definitions", "workflow_runs", "workflow_steps", "workflow_approvals"]),
    "ai": ("ai", ["chat_sessions", "chat_messages"])
}

API_PORTS = {
    "auth": 8001,
    "metadata": 8002,
    "query": 8003,
    "chemistry": 8004,
    "connectors": 8005,
    "audit": 8006,
    "lineage": 8007,
    "bioinformatics": 8008,
    "workflow": 8009,
    "ai": 8010
}

def get_pg_engine(db_name):
    # URL escape password
    escaped_pass = urllib.parse.quote_plus(PG_PASS)
    url = f"postgresql://{PG_USER}:{escaped_pass}@{PG_HOST}:{PG_PORT}/{db_name}"
    return create_engine(url, connect_args={"connect_timeout": 3})

def get_db_counts():
    db_counts = {}
    for service, db_name in SERVICES_DBS.items():
        print(f"Connecting to database '{db_name}' for service '{service}'...")
        db_counts[service] = {}
        schema, tables = SERVICES_SCHEMAS[service]
        try:
            engine = get_pg_engine(db_name)
            with engine.connect() as conn:
                for table in tables:
                    try:
                        res = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}"))
                        count = res.scalar()
                        print(f"  Table '{schema}.{table}': {count} rows")
                        db_counts[service][table] = count
                    except Exception as e:
                        print(f"  Failed to query table '{schema}.{table}': {e}")
                        db_counts[service][table] = f"Error: {str(e)}"
            engine.dispose()
        except Exception as e:
            print(f"  Failed to connect to database '{db_name}': {e}")
            db_counts[service]["connection_error"] = str(e)
    return db_counts

def get_auth_token():
    try:
        url = f"http://localhost:{API_PORTS['auth']}/api/v1/auth/login"
        print(f"Authenticating against {url}...")
        resp = requests.post(url, json={
            "email": "admin@genquantaa.com",
            "password": "GenQuantaaDiscover2026!"
        })
        if resp.status_code == 200:
            return resp.json().get("access_token")
        else:
            print(f"Failed to authenticate: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
    return None

def test_api_endpoints(token):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    results = {}

    # Define endpoints to check
    endpoints = {
        "metadata": [
            ("/metadata/entities", "metadata_entities"),
            ("/metadata/fields", "metadata_fields"),
            ("/metadata/federation/relationships", "metadata_relationships")
        ],
        "query": [
            ("/query/templates", "query_templates"),
            ("/query/history", "query_history")
        ],
        "chemistry": [
            ("/compounds", "compounds")
        ],
        "connectors": [
            ("/connectors/sources", "data_sources")
        ],
        "audit": [
            ("/audit/logs?limit=200", "audit_logs"),
            ("/compliance/signatures", "electronic_signatures")
        ],
        "lineage": [
            ("/lineage/graph", "lineage_elements") # returns {nodes: [], edges: []}
        ],
        "bioinformatics": [
            ("/sequences", "sequences")
        ],
        "workflow": [
            ("/workflows", "workflow_definitions"),
            ("/workflows/runs", "workflow_runs"),
            ("/workflows/approvals", "workflow_approvals")
        ],
        "ai": [
            ("/copilot/chat/sessions", "chat_sessions")
        ]
    }

    for svc, list_eps in endpoints.items():
        results[svc] = {}
        port = API_PORTS[svc]
        for path, key in list_eps:
            url = f"http://localhost:{port}/api/v1{path}"
            print(f"Calling endpoint {url}...")
            try:
                resp = requests.get(url, headers=headers, timeout=4)
                if resp.status_code == 200:
                    data = resp.json()
                    # Handle different response formats
                    if isinstance(data, list):
                        count = len(data)
                    elif isinstance(data, dict):
                        if "nodes" in data and "edges" in data:
                            count = len(data["nodes"]) + len(data["edges"])
                        else:
                            count = len(data.keys())
                    else:
                        count = "Unknown Format"
                    print(f"  Response: SUCCESS ({count} items)")
                    results[svc][key] = {"status": "SUCCESS", "count": count, "url": url}
                else:
                    print(f"  Response: FAILED ({resp.status_code}) - {resp.text[:100]}")
                    results[svc][key] = {"status": f"FAILED ({resp.status_code})", "count": 0, "url": url, "error": resp.text}
            except Exception as e:
                print(f"  Response: ERROR - {str(e)}")
                results[svc][key] = {"status": "ERROR", "count": 0, "url": url, "error": str(e)}
    return results

def main():
    print("Gathering database row counts from PostgreSQL...")
    db_counts = get_db_counts()
    print("Database counts gathered:")
    print(json.dumps(db_counts, indent=2))

    token = get_auth_token()
    if not token:
        print("Warning: proceeding without auth token.")
    
    print("\nCalling microservice API endpoints...")
    api_results = test_api_endpoints(token)
    print("API verification completed:")
    print(json.dumps(api_results, indent=2))

    # Save outputs to JSON for report generation
    with open(SCRATCH_DIR / "verification_data.json", "w") as f:
        json.dump({"db": db_counts, "api": api_results}, f, indent=2)

if __name__ == "__main__":
    main()
