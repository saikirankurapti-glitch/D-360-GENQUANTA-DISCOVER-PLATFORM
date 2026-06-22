import psycopg2

DB_USER = "postgres"
DB_PASS = "Saikiran@123"
DB_HOST = "localhost"
DB_PORT = "5432"

databases = {
    "auth": "genquantaa_auth",
    "metadata": "genquantaa_metadata",
    "query": "genquantaa_query",
    "chem": "cheminformatics",
    "connector": "genquantaa_connector",
    "audit": "genquantaa_audit",
    "lineage": "genquantaa_lineage",
    "bio": "genquantaa_bioinfo",
    "workflow": "genquantaa_workflow",
    "ai": "genquantaa_ai"
}

def get_row_counts():
    counts = {}
    
    # Table mapping to database key and table name
    tables = [
        ("auth", "gen_auth.users"),
        ("auth", "gen_auth.roles"),
        ("auth", "gen_auth.permissions"),
        ("auth", "gen_auth.role_permissions"),
        ("auth", "gen_auth.user_roles"),
        ("metadata", "metadata.metadata_fields"),
        ("metadata", "metadata.metadata_entities"),
        ("metadata", "metadata.metadata_values"),
        ("query", "query.query_templates"),
        ("query", "query.query_history"),
        ("query", "query.analysis_workspaces"),
        ("chem", "connector.compounds"),
        ("audit", "audit.audit_logs"),
        ("audit", "audit.electronic_signatures"),
        ("audit", "audit.signature_events"),
        ("audit", "audit.entity_versions"),
        ("audit", "audit.audit_versions"),
        ("bio", "bio.sequences"),
        ("bio", "bio.sequence_versions"),
        ("bio", "bio.sequence_annotations"),
        ("bio", "bio.alignments"),
        ("bio", "bio.sequence_clusters"),
        ("workflow", "workflow.workflow_definitions"),
        ("workflow", "workflow.workflow_runs"),
        ("workflow", "workflow.workflow_steps"),
        ("workflow", "workflow.workflow_approvals"),
        ("ai", "ai.chat_sessions"),
        ("ai", "ai.chat_messages")
    ]
    
    for db_key, table in tables:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                database=databases[db_key]
            )
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cur.fetchone()[0]
            counts[table] = row_count
            cur.close()
            conn.close()
        except Exception as e:
            counts[table] = f"ERROR: {str(e)}"
            
    print("\n" + "="*50)
    print(f"{'Table Name':<35} | {'Row Count':<10}")
    print("="*50)
    for table, count in sorted(counts.items()):
        print(f"{table:<35} | {count:<10}")
    print("="*50 + "\n")

if __name__ == "__main__":
    get_row_counts()
