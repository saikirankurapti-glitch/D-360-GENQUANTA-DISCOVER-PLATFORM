-- ==============================================================
-- GENQUANTAA Discover – Full Schema Alignment Verification
-- ==============================================================
-- Run ALL statements in order in Supabase SQL Editor.
-- Every block is labelled with what it checks and what to expect.
-- ==============================================================

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 1 – Schemas exist                                     │
-- │ Expected: 9 rows                                            │
-- └─────────────────────────────────────────────────────────────┘
SELECT schema_name
FROM   information_schema.schemata
WHERE  schema_name IN (
           'gen_auth','metadata','query','connector',
           'audit','lineage','bio','workflow','ai'
       )
ORDER  BY schema_name;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 2 – All 34 tables exist                               │
-- │ Expected: 34 rows across all custom schemas                 │
-- └─────────────────────────────────────────────────────────────┘
SELECT schemaname AS schema, tablename AS table_name
FROM   pg_tables
WHERE  schemaname IN (
           'gen_auth','metadata','query','connector',
           'audit','lineage','bio','workflow','ai'
       )
ORDER  BY schemaname, tablename;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 3 – Table count per schema                            │
-- └─────────────────────────────────────────────────────────────┘
-- Expected:
--   ai         → 2  (chat_sessions, chat_messages)
--   audit      → 5  (audit_logs, audit_versions, electronic_signatures, entity_versions, signature_events)
--   bio        → 5  (alignments, sequence_annotations, sequence_clusters, sequence_versions, sequences)
--   connector  → 8  (compounds, connection_configs, connector_sync_checkpoints, connector_sync_history, data_sources, entities, fields, relationships)
--   gen_auth   → 5  (permissions, role_permissions, roles, user_roles, users)
--   lineage    → 2  (lineage_edges, lineage_nodes)
--   metadata   → 6  (metadata_entities, metadata_fields, metadata_relationships, metadata_sync_history, metadata_values, metadata_versions)
--   query      → 3  (analysis_workspaces, query_history, query_templates)
--   workflow   → 6  (workflow_approvals, workflow_definitions, workflow_events, workflow_runs, workflow_schedules, workflow_steps)
SELECT schemaname AS schema, COUNT(*) AS table_count
FROM   pg_tables
WHERE  schemaname IN (
           'gen_auth','metadata','query','connector',
           'audit','lineage','bio','workflow','ai'
       )
GROUP  BY schemaname
ORDER  BY schemaname;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 4 – All indexes present                               │
-- └─────────────────────────────────────────────────────────────┘
SELECT schemaname, tablename, indexname
FROM   pg_indexes
WHERE  schemaname IN (
           'gen_auth','metadata','query','connector',
           'audit','lineage','bio','workflow','ai'
       )
AND    indexname LIKE 'idx_%'
ORDER  BY schemaname, tablename, indexname;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 5 – Extensions                                        │
-- │ Expected: uuid-ossp and pgcrypto rows                       │
-- └─────────────────────────────────────────────────────────────┘
SELECT extname, extversion
FROM   pg_extension
WHERE  extname IN ('uuid-ossp','pgcrypto');

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 6 – No orphan tables left in public schema            │
-- │ Expected: 0 rows (all old public.* tables should be gone    │
-- │ or empty after migration)                                    │
-- └─────────────────────────────────────────────────────────────┘
SELECT tablename,
       pg_total_relation_size(quote_ident('public') || '.' || quote_ident(tablename)) AS size_bytes
FROM   pg_tables
WHERE  schemaname = 'public'
AND    tablename IN (
    'users','roles','permissions','role_permissions','user_roles',
    'metadata_fields','metadata_entities','metadata_values',
    'metadata_relationships','metadata_versions','metadata_sync_history',
    'query_templates','query_history','analysis_workspaces',
    'data_sources','connection_configs','entities','fields','relationships',
    'connector_sync_history','connector_sync_checkpoints','compounds',
    'audit_logs','electronic_signatures','signature_events',
    'entity_versions','audit_versions',
    'lineage_nodes','lineage_edges',
    'sequences','sequence_versions','sequence_annotations',
    'alignments','sequence_clusters',
    'workflow_definitions','workflow_runs','workflow_steps',
    'workflow_schedules','workflow_events','workflow_approvals',
    'chat_sessions','chat_messages'
)
ORDER  BY tablename;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 7 – gen_auth schema functional smoke test             │
-- └─────────────────────────────────────────────────────────────┘
INSERT INTO gen_auth.roles (name, description)
VALUES ('__verify_role__','Temporary – auto deleted');

SELECT id, name FROM gen_auth.roles WHERE name = '__verify_role__';

DELETE FROM gen_auth.roles WHERE name = '__verify_role__';

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 8 – metadata schema functional smoke test             │
-- └─────────────────────────────────────────────────────────────┘
INSERT INTO metadata.metadata_fields (name, display_name, data_type, category)
VALUES ('__verify_field__','Verify Field','string','Test');

SELECT id, name FROM metadata.metadata_fields WHERE name = '__verify_field__';

DELETE FROM metadata.metadata_fields WHERE name = '__verify_field__';

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 9 – workflow schema functional smoke test             │
-- └─────────────────────────────────────────────────────────────┘
INSERT INTO workflow.workflow_definitions (name, nodes_json, edges_json)
VALUES ('__verify_wf__','[]','[]');

SELECT id, name FROM workflow.workflow_definitions WHERE name = '__verify_wf__';

DELETE FROM workflow.workflow_definitions WHERE name = '__verify_wf__';

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 10 – ForeignKey integrity (gen_auth)                  │
-- └─────────────────────────────────────────────────────────────┘
SELECT
    tc.table_schema, tc.table_name, kcu.column_name,
    ccu.table_schema AS foreign_schema, ccu.table_name AS foreign_table
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND   tc.table_schema IN (
          'gen_auth','metadata','query','connector',
          'audit','lineage','bio','workflow','ai'
      )
ORDER  BY tc.table_schema, tc.table_name;

-- ┌─────────────────────────────────────────────────────────────┐
-- │ CHECK 11 – Data row counts across all schema tables         │
-- │ Run this after migration to confirm data was moved          │
-- └─────────────────────────────────────────────────────────────┘
SELECT 'gen_auth.users'               AS table_ref, COUNT(*) AS rows FROM gen_auth.users           UNION ALL
SELECT 'gen_auth.roles',                             COUNT(*) FROM gen_auth.roles                   UNION ALL
SELECT 'gen_auth.permissions',                       COUNT(*) FROM gen_auth.permissions             UNION ALL
SELECT 'metadata.metadata_fields',                   COUNT(*) FROM metadata.metadata_fields         UNION ALL
SELECT 'metadata.metadata_entities',                 COUNT(*) FROM metadata.metadata_entities       UNION ALL
SELECT 'metadata.metadata_values',                   COUNT(*) FROM metadata.metadata_values         UNION ALL
SELECT 'query.query_templates',                      COUNT(*) FROM query.query_templates            UNION ALL
SELECT 'query.query_history',                        COUNT(*) FROM query.query_history              UNION ALL
SELECT 'connector.data_sources',                     COUNT(*) FROM connector.data_sources           UNION ALL
SELECT 'connector.entities',                         COUNT(*) FROM connector.entities               UNION ALL
SELECT 'audit.audit_logs',                           COUNT(*) FROM audit.audit_logs                 UNION ALL
SELECT 'lineage.lineage_nodes',                      COUNT(*) FROM lineage.lineage_nodes             UNION ALL
SELECT 'bio.sequences',                              COUNT(*) FROM bio.sequences                    UNION ALL
SELECT 'workflow.workflow_definitions',               COUNT(*) FROM workflow.workflow_definitions    UNION ALL
SELECT 'ai.chat_sessions',                           COUNT(*) FROM ai.chat_sessions
ORDER  BY table_ref;

-- ==============================================================
-- All checks passed = schema alignment is complete.
-- ==============================================================
