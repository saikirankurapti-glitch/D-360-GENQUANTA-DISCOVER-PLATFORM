import psycopg2
import urllib.parse
import os
import httpx
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Saikiran%40123@localhost:5432/genquantaa_ai")

def get_db_connection(db_name: str):
    base_url = DATABASE_URL.rsplit("/", 1)[0]
    target_url = f"{base_url}/{db_name}"
    parsed = urllib.parse.urlparse(target_url)
    username = parsed.username
    password = urllib.parse.unquote(parsed.password or '')
    host = parsed.hostname
    port = parsed.port or 5432
    return psycopg2.connect(host=host, port=port, user=username, password=password, database=db_name)

def run_query(db_name, sql, params=None):
    conn = get_db_connection(db_name)
    cur = conn.cursor()
    cur.execute(sql, params)
    colnames = [desc[0] for desc in cur.description] if cur.description else []
    rows = cur.fetchall() if cur.description else []
    conn.close()
    return colnames, rows

print("Executing all validation queries...\n")

# Q1: Top 10 EGFR compounds
print("--- Q1: Show top 10 EGFR compounds ---")
q1_sql = """
WITH compound_attrs AS (
    SELECT 
        e.entity_key AS compound_id,
        e.name AS compound_name,
        MAX(CASE WHEN v.field_id = 7 THEN v.value END) AS smiles,
        MAX(CASE WHEN v.field_id = 3 THEN v.value END) AS mw,
        MAX(CASE WHEN v.field_id = 4 THEN v.value END) AS clogp
    FROM metadata.metadata_entities e
    JOIN metadata.metadata_values v ON e.id = v.entity_id
    WHERE e.entity_type = 'Compound'
    GROUP BY e.id, e.entity_key, e.name
),
assay_attrs AS (
    SELECT 
        e.entity_key AS assay_id,
        MAX(CASE WHEN v.field_id = 96 THEN v.value END) AS compound_id,
        MAX(CASE WHEN v.field_id = 1 THEN v.value END) AS target_protein,
        MAX(CASE WHEN v.field_id = 2 THEN v.value END)::numeric AS ic50_nm,
        MAX(CASE WHEN v.field_id = 95 THEN v.value END) AS result_date
    FROM metadata.metadata_entities e
    JOIN metadata.metadata_values v ON e.id = v.entity_id
    WHERE e.entity_type = 'Assay'
    GROUP BY e.id, e.entity_key
)
SELECT 
    c.compound_id,
    c.compound_name,
    c.smiles,
    c.mw,
    c.clogp,
    a.assay_id,
    a.target_protein,
    a.ic50_nm,
    a.result_date
FROM assay_attrs a
JOIN compound_attrs c ON a.compound_id = c.compound_id
WHERE a.target_protein = 'EGFR'
ORDER BY a.ic50_nm ASC
LIMIT 10;
"""
cols, rows = run_query("genquantaa_metadata", q1_sql)
print("Columns:", cols)
for r in rows[:3]:
    print(r)
print(f"Total returned: {len(rows)}\n")

# Q2: Compounds with IC50 < 100 nM
print("--- Q2: List compounds with IC50 < 100 nM ---")
q2_sql = """
WITH compound_attrs AS (
    SELECT 
        e.entity_key AS compound_id,
        e.name AS compound_name,
        MAX(CASE WHEN v.field_id = 7 THEN v.value END) AS smiles,
        MAX(CASE WHEN v.field_id = 3 THEN v.value END) AS mw,
        MAX(CASE WHEN v.field_id = 4 THEN v.value END) AS clogp
    FROM metadata.metadata_entities e
    JOIN metadata.metadata_values v ON e.id = v.entity_id
    WHERE e.entity_type = 'Compound'
    GROUP BY e.id, e.entity_key, e.name
),
assay_attrs AS (
    SELECT 
        e.entity_key AS assay_id,
        MAX(CASE WHEN v.field_id = 96 THEN v.value END) AS compound_id,
        MAX(CASE WHEN v.field_id = 1 THEN v.value END) AS target_protein,
        MAX(CASE WHEN v.field_id = 2 THEN v.value END)::numeric AS ic50_nm,
        MAX(CASE WHEN v.field_id = 95 THEN v.value END) AS result_date
    FROM metadata.metadata_entities e
    JOIN metadata.metadata_values v ON e.id = v.entity_id
    WHERE e.entity_type = 'Assay'
    GROUP BY e.id, e.entity_key
)
SELECT 
    c.compound_id,
    c.compound_name,
    c.smiles,
    c.mw,
    a.assay_id,
    a.target_protein,
    a.ic50_nm,
    a.result_date
FROM assay_attrs a
JOIN compound_attrs c ON a.compound_id = c.compound_id
WHERE a.ic50_nm < 100
ORDER BY a.ic50_nm ASC
LIMIT 10;
"""
cols, rows = run_query("genquantaa_metadata", q2_sql)
print("Columns:", cols)
for r in rows[:3]:
    print(r)
print(f"Total returned: {len(rows)}\n")

# Q3: Scientist executed the most experiments
print("--- Q3: Which scientist executed the most experiments? ---")
try:
    resp = httpx.get("http://localhost:8005/api/v1/connectors/sources/5/entities")
    query_payload = {
        "entity": "experiments",
        "fields": ["experiment_id", "title", "author", "status"],
        "limit": 1000
    }
    exec_resp = httpx.post("http://localhost:8005/api/v1/connectors/sources/5/query", json=query_payload)
    if exec_resp.status_code == 200:
        rows = exec_resp.json().get("rows", [])
        counts = {}
        for r in rows:
            counts[r[2]] = counts.get(r[2], 0) + 1
        print("Experiment counts by scientist:")
        for k, v in counts.items():
            print(f"  {k}: {v}")
    else:
        print("Error fetching experiments:", exec_resp.text)
except Exception as e:
    print("Error:", e)
print("\n")

# Q4: Workflow success rates
print("--- Q4: Show workflow success rates ---")
q4_sql = """
SELECT 
    d.name AS workflow_name,
    COUNT(r.id) AS total_runs,
    SUM(CASE WHEN r.status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_runs,
    SUM(CASE WHEN r.status = 'FAILED' THEN 1 ELSE 0 END) AS failed_runs,
    ROUND(100.0 * SUM(CASE WHEN r.status = 'COMPLETED' THEN 1 ELSE 0 END) / COUNT(r.id), 2) AS success_rate
FROM workflow.workflow_runs r
JOIN workflow.workflow_definitions d ON r.workflow_id = d.id
GROUP BY d.name
ORDER BY success_rate DESC;
"""
cols, rows = run_query("genquantaa_workflow", q4_sql)
print("Columns:", cols)
for r in rows[:3]:
    print(r)
print(f"Total returned: {len(rows)}\n")

# Q5: Summarize audit activity this month
print("--- Q5: Summarize audit activity this month ---")
q5_sql = """
SELECT 
    action,
    service_name,
    COUNT(*) AS event_count,
    SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) AS failure_count
FROM audit.audit_logs
WHERE timestamp >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY action, service_name
ORDER BY event_count DESC;
"""
cols, rows = run_query("genquantaa_audit", q5_sql)
print("Columns:", cols)
for r in rows[:5]:
    print(r)
print(f"Total returned: {len(rows)}\n")

# Q6: Compounds targeting KRAS
print("--- Q6: Show compounds targeting KRAS ---")
q6_sql = """
WITH compound_attrs AS (
    SELECT 
        e.entity_key AS compound_id,
        e.name AS compound_name,
        MAX(CASE WHEN v.field_id = 7 THEN v.value END) AS smiles,
        MAX(CASE WHEN v.field_id = 3 THEN v.value END) AS mw,
        MAX(CASE WHEN v.field_id = 4 THEN v.value END) AS clogp,
        MAX(CASE WHEN v.field_id = 1 THEN v.value END) AS target_protein
    FROM metadata.metadata_entities e
    JOIN metadata.metadata_values v ON e.id = v.entity_id
    WHERE e.entity_type = 'Compound'
    GROUP BY e.id, e.entity_key, e.name
)
SELECT 
    compound_id,
    compound_name,
    smiles,
    mw,
    clogp,
    target_protein
FROM compound_attrs
WHERE target_protein = 'KRAS'
LIMIT 10;
"""
cols, rows = run_query("genquantaa_metadata", q6_sql)
print("Columns:", cols)
for r in rows[:3]:
    print(r)
print(f"Total returned: {len(rows)}\n")

# Q7: Compare HER2 vs EGFR assay activity
print("--- Q7: Compare HER2 vs EGFR assay activity ---")
q7_sql = """
WITH assay_attrs AS (
    SELECT 
        e.entity_key AS assay_id,
        MAX(CASE WHEN v.field_id = 1 THEN v.value END) AS target_protein,
        MAX(CASE WHEN v.field_id = 2 THEN v.value END)::numeric AS ic50_nm,
        MAX(CASE WHEN v.field_id = 94 THEN v.value END)::numeric AS ec50_nm
    FROM metadata.metadata_entities e
    JOIN metadata.metadata_values v ON e.id = v.entity_id
    WHERE e.entity_type = 'Assay'
    GROUP BY e.id, e.entity_key
)
SELECT 
    target_protein,
    COUNT(*) AS total_assays,
    ROUND(AVG(ic50_nm), 2) AS avg_ic50_nm,
    ROUND(MIN(ic50_nm), 2) AS min_ic50_nm,
    ROUND(MAX(ic50_nm), 2) AS max_ic50_nm,
    ROUND(AVG(ec50_nm), 2) AS avg_ec50_nm
FROM assay_attrs
WHERE target_protein IN ('HER2', 'EGFR')
GROUP BY target_protein;
"""
cols, rows = run_query("genquantaa_metadata", q7_sql)
print("Columns:", cols)
for r in rows:
    print(r)
print(f"Total returned: {len(rows)}\n")

# Q8: Show sequence mutation statistics
print("--- Q8: Show sequence mutation statistics ---")
q8_sql = """
SELECT 
    feature_type,
    name,
    COUNT(*) AS occurrence_count,
    notes
FROM bio.sequence_annotations
GROUP BY feature_type, name, notes
ORDER BY occurrence_count DESC;
"""
cols, rows = run_query("genquantaa_bioinfo", q8_sql)
print("Columns:", cols)
for r in rows:
    print(r)
print(f"Total returned: {len(rows)}\n")

# Q9: Which workflows require approvals
print("--- Q9: Which workflows require approvals? ---")
q9_sql = """
SELECT 
    id,
    name,
    description,
    trigger_type
FROM workflow.workflow_definitions
WHERE nodes_json LIKE '%approval%'
ORDER BY name;
"""
cols, rows = run_query("genquantaa_workflow", q9_sql)
print("Columns:", cols)
for r in rows[:3]:
    print(r)
print(f"Total returned: {len(rows)}\n")

# Q10: Executive scientific summary
print("--- Q10: Generate an executive scientific summary ---")
summary = {}
# Counts
_, r = run_query("genquantaa_metadata", "SELECT COUNT(*) FROM metadata.metadata_entities WHERE entity_type='Compound';")
summary["compounds"] = r[0][0]
_, r = run_query("genquantaa_metadata", "SELECT COUNT(*) FROM metadata.metadata_entities WHERE entity_type='Assay';")
summary["assays"] = r[0][0]
_, r = run_query("genquantaa_bioinfo", "SELECT COUNT(*) FROM bio.sequences;")
summary["sequences"] = r[0][0]
_, r = run_query("genquantaa_workflow", "SELECT COUNT(*) FROM workflow.workflow_runs;")
summary["workflow_runs"] = r[0][0]
_, r = run_query("genquantaa_audit", "SELECT COUNT(*) FROM audit.audit_logs;")
summary["audit_logs"] = r[0][0]
print("Summary Counts:", summary)
