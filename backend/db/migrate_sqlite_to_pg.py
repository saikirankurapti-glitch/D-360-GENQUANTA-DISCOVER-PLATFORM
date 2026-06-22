#!/usr/bin/env python3
"""
GENQUANTAA Discover - SQLite to PostgreSQL Data Migration Script
=================================================================
Phase 8: Exports data from each service's SQLite database and imports
it into the corresponding PostgreSQL database.

Usage:
    python migrate_sqlite_to_pg.py [--pg-host HOST] [--pg-port PORT]
                                   [--pg-user USER] [--pg-password PASS]
                                   [--dry-run]

Prerequisites:
    - PostgreSQL databases must already exist (run init_databases.sql)
    - SQLAlchemy models must define the schema (tables auto-created)
    - psycopg2-binary installed in venv
"""

import argparse
import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path for shared imports
BACKEND_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker


# ---------------------------------------------------------------------------
# Service -> SQLite path -> PostgreSQL database name and schema mapping
# ---------------------------------------------------------------------------
SERVICES = [
    {
        "name": "auth-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "auth_service" / "auth.db",
        ],
        "pg_db": "genquantaa_auth",
        "schema": "gen_auth",
        "tables": ["users", "roles", "permissions", "user_roles", "role_permissions"],
    },
    {
        "name": "metadata-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "metadata_service" / "metadata.db",
        ],
        "pg_db": "genquantaa_metadata",
        "schema": "metadata",
        "tables": [
            "metadata_fields", "metadata_entities", "metadata_values",
            "metadata_relationships", "metadata_versions", "metadata_sync_history",
        ],
    },
    {
        "name": "query-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "query_service" / "query.db",
        ],
        "pg_db": "genquantaa_query",
        "schema": "query",
        "tables": ["query_history", "query_templates", "analysis_workspaces"],
    },
    {
        "name": "connector-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "connector_service" / "connector.db",
            BACKEND_DIR / "connector.db",
        ],
        "pg_db": "genquantaa_connector",
        "schema": "connector",
        "tables": [
            "data_sources", "connection_configs", "entities", "fields",
            "relationships", "connector_sync_history", "connector_sync_checkpoints",
        ],
    },
    {
        "name": "cheminformatics-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "cheminformatics_service" / "cheminformatics.db",
        ],
        "pg_db": "cheminformatics",
        "schema": "connector",
        "tables": ["compounds"],
    },
    {
        "name": "audit-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "audit_service" / "audit.db",
        ],
        "pg_db": "genquantaa_audit",
        "schema": "audit",
        "tables": [
            "audit_logs", "electronic_signatures", "signature_events",
            "entity_versions", "audit_versions",
        ],
    },
    {
        "name": "lineage-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "lineage_service" / "lineage.db",
        ],
        "pg_db": "genquantaa_lineage",
        "schema": "lineage",
        "tables": ["lineage_nodes", "lineage_edges"],
    },
    {
        "name": "bioinformatics-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "bioinformatics_service" / "bioinformatics.db",
        ],
        "pg_db": "genquantaa_bioinfo",
        "schema": "bio",
        "tables": [
            "sequences", "sequence_versions", "sequence_annotations",
            "alignments", "sequence_clusters",
        ],
    },
    {
        "name": "workflow-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "workflow_service" / "workflow.db",
        ],
        "pg_db": "genquantaa_workflow",
        "schema": "workflow",
        "tables": [
            "workflow_definitions", "workflow_runs", "workflow_steps",
            "workflow_schedules", "workflow_events", "workflow_approvals",
        ],
    },
    {
        "name": "ai-service",
        "sqlite_paths": [
            BACKEND_DIR / "services" / "ai_service" / "ai.db",
        ],
        "pg_db": "genquantaa_ai",
        "schema": "ai",
        "tables": ["chat_sessions", "chat_messages"],
    },
]


def find_sqlite_db(paths: list[Path]) -> Path | None:
    """Find the first existing SQLite file from a list of candidate paths."""
    for p in paths:
        if p.exists():
            return p
    return None


def migrate_table(sqlite_conn, pg_engine, table_name: str, schema: str, dry_run: bool = False):
    """
    Migrate all rows from a SQLite table into the same-named PostgreSQL table.
    Uses batch INSERT for performance.
    """
    cursor = sqlite_conn.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    if not rows:
        print(f"    [Skipped] {table_name}: 0 rows")
        return 0

    if dry_run:
        print(f"    [Dry-run] {table_name}: {len(rows)} rows (not inserted)")
        return len(rows)

    # Inspect the target PostgreSQL table to find boolean columns
    inspector = inspect(pg_engine)
    bool_cols = set()
    try:
        columns_info = inspector.get_columns(table_name, schema=schema)
        for col in columns_info:
            if "bool" in str(col["type"]).lower():
                bool_cols.add(col["name"])
    except Exception as e:
        print(f"    [Warning] Could not inspect column types for {schema}.{table_name}: {e}")

    # Build parameterized INSERT
    col_list = ", ".join(columns)
    param_list = ", ".join([f":{c}" for c in columns])
    insert_sql = text(f"INSERT INTO {schema}.{table_name} ({col_list}) VALUES ({param_list})")

    with pg_engine.begin() as conn:
        # Disable constraints temporarily for FK ordering
        conn.execute(text("SET session_replication_role = 'replica'"))
        # Truncate target table to avoid unique constraint / duplicate key violations
        conn.execute(text(f"TRUNCATE TABLE {schema}.{table_name} CASCADE"))
        for row in rows:
            params = {}
            for col_name, val in zip(columns, row):
                if col_name in bool_cols and val is not None:
                    # Convert SQLite integer booleans to python True/False
                    if val in (1, "1", True, "true", "True"):
                        params[col_name] = True
                    elif val in (0, "0", False, "false", "False"):
                        params[col_name] = False
                    else:
                        params[col_name] = bool(val)
                else:
                    params[col_name] = val
            conn.execute(insert_sql, params)
        conn.execute(text("SET session_replication_role = 'origin'"))

    print(f"    [Migrated] {table_name}: {len(rows)} rows")
    return len(rows)


def reset_sequences(pg_engine, tables: list[str], schema: str):
    """Reset PostgreSQL auto-increment sequences after data import."""
    with pg_engine.begin() as conn:
        inspector = inspect(pg_engine)
        for table_name in tables:
            try:
                pk_cols = inspector.get_pk_constraint(table_name, schema=schema).get("constrained_columns", [])
                if pk_cols and pk_cols[0] == "id":
                    seq_name = f"{schema}.{table_name}_id_seq"
                    conn.execute(text(
                        f"SELECT setval('{seq_name}', COALESCE((SELECT MAX(id) FROM {schema}.{table_name}), 0) + 1, false)"
                    ))
            except Exception:
                pass  # Table might not have an auto-increment 'id'


def migrate_service(svc: dict, pg_host: str, pg_port: int, pg_user: str, pg_password: str, dry_run: bool):
    """Migrate one service's SQLite data to PostgreSQL."""
    sqlite_path = find_sqlite_db(svc["sqlite_paths"])
    if not sqlite_path:
        print(f"\n[Warning] {svc['name']}: No SQLite database found, skipping")
        return

    pg_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{svc['pg_db']}"
    
    print(f"\n{'='*60}")
    print(f"Migrating: {svc['name']}")
    print(f"   SQLite: {sqlite_path}")
    print(f"   PostgreSQL DB: {svc['pg_db']}, Schema: {svc['schema']}")
    print(f"{'='*60}")

    sqlite_conn = sqlite3.connect(str(sqlite_path))
    pg_engine = create_engine(pg_url)

    total_rows = 0
    for table in svc["tables"]:
        try:
            # Check if table exists in SQLite
            check = sqlite_conn.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            ).fetchone()
            if not check:
                print(f"    [Skipped] {table}: not found in SQLite")
                continue
            total_rows += migrate_table(sqlite_conn, pg_engine, table, svc["schema"], dry_run)
        except Exception as e:
            print(f"    [Error] {table}: {e}")

    if not dry_run and total_rows > 0:
        reset_sequences(pg_engine, svc["tables"], svc["schema"])

    sqlite_conn.close()
    pg_engine.dispose()
    print(f"   Total: {total_rows} rows {'(dry-run)' if dry_run else 'migrated'}")


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL")
    parser.add_argument("--pg-host", default="localhost", help="PostgreSQL host")
    parser.add_argument("--pg-port", type=int, default=5432, help="PostgreSQL port")
    parser.add_argument("--pg-user", default="postgres", help="PostgreSQL user")
    parser.add_argument("--pg-password", default=os.getenv("POSTGRES_PASSWORD", "postgres"), help="PostgreSQL password")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without writing")
    parser.add_argument("--service", default=None, help="Migrate only this service (e.g. 'auth-service')")
    args = parser.parse_args()

    print("=" * 60)
    print("GENQUANTAA Discover - SQLite -> PostgreSQL Migration")
    print(f"Target: {args.pg_user}@{args.pg_host}:{args.pg_port}")
    if args.dry_run:
        print("MODE: DRY RUN (no data will be written)")
    print("=" * 60)

    services = SERVICES
    if args.service:
        services = [s for s in SERVICES if s["name"] == args.service]
        if not services:
            print(f"ERROR: Service '{args.service}' not found")
            sys.exit(1)

    for svc in services:
        migrate_service(svc, args.pg_host, args.pg_port, args.pg_user, args.pg_password, args.dry_run)

    print(f"\n{'='*60}")
    print("Migration complete!" if not args.dry_run else "Dry run complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
