-- ================================================================
-- AnalytiX Discover – Phase 8.1 Data Verification SQL
-- Run each section separately in Supabase SQL Editor.
-- ================================================================

-- ================================================================
-- SECTION 1: ROW COUNTS – All tables across all schemas
-- ================================================================
SELECT 'gen_auth.users'                        AS table_ref, COUNT(*) AS rows FROM gen_auth.users              UNION ALL
SELECT 'gen_auth.roles',                                      COUNT(*) FROM gen_auth.roles                     UNION ALL
SELECT 'gen_auth.permissions',                                COUNT(*) FROM gen_auth.permissions               UNION ALL
SELECT 'gen_auth.role_permissions',                           COUNT(*) FROM gen_auth.role_permissions          UNION ALL
SELECT 'gen_auth.user_roles',                                 COUNT(*) FROM gen_auth.user_roles                UNION ALL
SELECT 'metadata.metadata_fields',                            COUNT(*) FROM metadata.metadata_fields           UNION ALL
SELECT 'metadata.metadata_entities',                          COUNT(*) FROM metadata.metadata_entities         UNION ALL
SELECT 'metadata.metadata_values',                            COUNT(*) FROM metadata.metadata_values           UNION ALL
SELECT 'metadata.metadata_relationships',                     COUNT(*) FROM metadata.metadata_relationships    UNION ALL
SELECT 'metadata.metadata_versions',                          COUNT(*) FROM metadata.metadata_versions         UNION ALL
SELECT 'metadata.metadata_sync_history',                      COUNT(*) FROM metadata.metadata_sync_history     UNION ALL
SELECT 'query.query_templates',                               COUNT(*) FROM query.query_templates              UNION ALL
SELECT 'query.query_history',                                 COUNT(*) FROM query.query_history                UNION ALL
SELECT 'query.analysis_workspaces',                           COUNT(*) FROM query.analysis_workspaces          UNION ALL
SELECT 'connector.data_sources',                              COUNT(*) FROM connector.data_sources             UNION ALL
SELECT 'connector.connection_configs',                        COUNT(*) FROM connector.connection_configs       UNION ALL
SELECT 'connector.entities',                                  COUNT(*) FROM connector.entities                 UNION ALL
SELECT 'connector.fields',                                    COUNT(*) FROM connector.fields                   UNION ALL
SELECT 'connector.relationships',                             COUNT(*) FROM connector.relationships            UNION ALL
SELECT 'connector.connector_sync_history',                    COUNT(*) FROM connector.connector_sync_history   UNION ALL
SELECT 'connector.connector_sync_checkpoints',                COUNT(*) FROM connector.connector_sync_checkpoints UNION ALL
SELECT 'connector.compounds',                                 COUNT(*) FROM connector.compounds                UNION ALL
SELECT 'audit.audit_logs',                                    COUNT(*) FROM audit.audit_logs                   UNION ALL
SELECT 'audit.electronic_signatures',                         COUNT(*) FROM audit.electronic_signatures        UNION ALL
SELECT 'audit.signature_events',                              COUNT(*) FROM audit.signature_events             UNION ALL
SELECT 'audit.entity_versions',                               COUNT(*) FROM audit.entity_versions              UNION ALL
SELECT 'audit.audit_versions',                                COUNT(*) FROM audit.audit_versions               UNION ALL
SELECT 'lineage.lineage_nodes',                               COUNT(*) FROM lineage.lineage_nodes              UNION ALL
SELECT 'lineage.lineage_edges',                               COUNT(*) FROM lineage.lineage_edges              UNION ALL
SELECT 'bio.sequences',                                       COUNT(*) FROM bio.sequences                      UNION ALL
SELECT 'bio.sequence_versions',                               COUNT(*) FROM bio.sequence_versions              UNION ALL
SELECT 'bio.sequence_annotations',                            COUNT(*) FROM bio.sequence_annotations           UNION ALL
SELECT 'bio.alignments',                                      COUNT(*) FROM bio.alignments                     UNION ALL
SELECT 'bio.sequence_clusters',                               COUNT(*) FROM bio.sequence_clusters              UNION ALL
SELECT 'workflow.workflow_definitions',                        COUNT(*) FROM workflow.workflow_definitions      UNION ALL
SELECT 'workflow.workflow_runs',                               COUNT(*) FROM workflow.workflow_runs             UNION ALL
SELECT 'workflow.workflow_steps',                              COUNT(*) FROM workflow.workflow_steps            UNION ALL
SELECT 'workflow.workflow_schedules',                          COUNT(*) FROM workflow.workflow_schedules        UNION ALL
SELECT 'workflow.workflow_events',                             COUNT(*) FROM workflow.workflow_events           UNION ALL
SELECT 'workflow.workflow_approvals',                          COUNT(*) FROM workflow.workflow_approvals        UNION ALL
SELECT 'ai.chat_sessions',                                    COUNT(*) FROM ai.chat_sessions                   UNION ALL
SELECT 'ai.chat_messages',                                    COUNT(*) FROM ai.chat_messages
ORDER BY table_ref;

-- ================================================================
-- SECTION 2: TOP 10 RECORDS PER TABLE
-- ================================================================

-- gen_auth schema
SELECT 'gen_auth.users' AS source, id, email, role, is_active FROM gen_auth.users LIMIT 10;
SELECT 'gen_auth.roles' AS source, id, name, description FROM gen_auth.roles LIMIT 10;
SELECT 'gen_auth.permissions' AS source, id, name FROM gen_auth.permissions LIMIT 10;
SELECT 'gen_auth.role_permissions' AS source, role_id, permission_id FROM gen_auth.role_permissions LIMIT 10;
SELECT 'gen_auth.user_roles' AS source, user_id, role_id FROM gen_auth.user_roles LIMIT 10;

-- metadata schema
SELECT 'metadata.metadata_fields' AS source, id, name, display_name, data_type, category FROM metadata.metadata_fields LIMIT 10;
SELECT 'metadata.metadata_entities' AS source, id, entity_key, entity_type, name FROM metadata.metadata_entities LIMIT 10;
SELECT 'metadata.metadata_values' AS source, id, entity_id, field_id, value FROM metadata.metadata_values LIMIT 10;
SELECT 'metadata.metadata_relationships' AS source, id, datasource_id, source_entity_key, target_entity_key FROM metadata.metadata_relationships LIMIT 10;
SELECT 'metadata.metadata_sync_history' AS source, id, datasource_name, status, records_synced FROM metadata.metadata_sync_history LIMIT 10;

-- query schema
SELECT 'query.query_templates' AS source, id, name, created_by FROM query.query_templates LIMIT 10;
SELECT 'query.query_history' AS source, id, status, execution_time_ms, row_count, created_at FROM query.query_history LIMIT 10;
SELECT 'query.analysis_workspaces' AS source, id, name, created_at FROM query.analysis_workspaces LIMIT 10;

-- connector schema
SELECT 'connector.data_sources' AS source, id, name, connector_type, is_active FROM connector.data_sources LIMIT 10;
SELECT 'connector.entities' AS source, id, data_source_id, physical_name, display_name FROM connector.entities LIMIT 10;
SELECT 'connector.fields' AS source, id, entity_id, physical_name, data_type FROM connector.fields LIMIT 10;
SELECT 'connector.compounds' AS source, id, entity_key, name, smiles FROM connector.compounds LIMIT 10;
SELECT 'connector.connector_sync_history' AS source, id, data_source_id, sync_status, records_synced FROM connector.connector_sync_history LIMIT 10;

-- audit schema
SELECT 'audit.audit_logs' AS source, id, timestamp, username, action, service_name, status FROM audit.audit_logs LIMIT 10;
SELECT 'audit.electronic_signatures' AS source, id, user_id, username, created_at FROM audit.electronic_signatures LIMIT 10;
SELECT 'audit.entity_versions' AS source, id, entity_type, entity_id, version, modified_by FROM audit.entity_versions LIMIT 10;

-- lineage schema
SELECT 'lineage.lineage_nodes' AS source, id, type, name FROM lineage.lineage_nodes LIMIT 10;
SELECT 'lineage.lineage_edges' AS source, id, source, target, type FROM lineage.lineage_edges LIMIT 10;

-- bio schema
SELECT 'bio.sequences' AS source, id, sequence_id, name, sequence_type, created_at FROM bio.sequences LIMIT 10;
SELECT 'bio.sequence_annotations' AS source, id, sequence_id, feature_type, name FROM bio.sequence_annotations LIMIT 10;
SELECT 'bio.alignments' AS source, id, name, alignment_type, score FROM bio.alignments LIMIT 10;
SELECT 'bio.sequence_clusters' AS source, id, name, method, distance_metric FROM bio.sequence_clusters LIMIT 10;

-- workflow schema
SELECT 'workflow.workflow_definitions' AS source, id, name, trigger_type, is_active, created_at FROM workflow.workflow_definitions LIMIT 10;
SELECT 'workflow.workflow_runs' AS source, id, workflow_id, status, started_at FROM workflow.workflow_runs LIMIT 10;
SELECT 'workflow.workflow_events' AS source, id, event_type, processed, created_at FROM workflow.workflow_events LIMIT 10;

-- ai schema
SELECT 'ai.chat_sessions' AS source, id, title, created_at FROM ai.chat_sessions LIMIT 10;
SELECT 'ai.chat_messages' AS source, id, session_id, role, created_at FROM ai.chat_messages LIMIT 10;

-- ================================================================
-- SECTION 3: FOREIGN KEY VALIDATION
-- ================================================================

-- metadata.metadata_values → broken entity references
SELECT 'ORPHAN metadata_values→entity' AS issue, mv.id, mv.entity_id
FROM metadata.metadata_values mv
LEFT JOIN metadata.metadata_entities me ON mv.entity_id = me.id
WHERE me.id IS NULL;

-- metadata.metadata_values → broken field references
SELECT 'ORPHAN metadata_values→field' AS issue, mv.id, mv.field_id
FROM metadata.metadata_values mv
LEFT JOIN metadata.metadata_fields mf ON mv.field_id = mf.id
WHERE mf.id IS NULL;

-- connector.connection_configs → broken data_source references
SELECT 'ORPHAN connection_configs→data_source' AS issue, cc.id, cc.data_source_id
FROM connector.connection_configs cc
LEFT JOIN connector.data_sources ds ON cc.data_source_id = ds.id
WHERE ds.id IS NULL;

-- connector.entities → broken data_source references
SELECT 'ORPHAN connector.entities→data_source' AS issue, e.id, e.data_source_id
FROM connector.entities e
LEFT JOIN connector.data_sources ds ON e.data_source_id = ds.id
WHERE ds.id IS NULL;

-- connector.fields → broken entity references
SELECT 'ORPHAN connector.fields→entity' AS issue, f.id, f.entity_id
FROM connector.fields f
LEFT JOIN connector.entities e ON f.entity_id = e.id
WHERE e.id IS NULL;

-- gen_auth.role_permissions → broken role/permission references
SELECT 'ORPHAN role_permissions→role' AS issue, rp.role_id
FROM gen_auth.role_permissions rp
LEFT JOIN gen_auth.roles r ON rp.role_id = r.id
WHERE r.id IS NULL;

SELECT 'ORPHAN role_permissions→permission' AS issue, rp.permission_id
FROM gen_auth.role_permissions rp
LEFT JOIN gen_auth.permissions p ON rp.permission_id = p.id
WHERE p.id IS NULL;

-- gen_auth.user_roles → broken user references
SELECT 'ORPHAN user_roles→user' AS issue, ur.user_id
FROM gen_auth.user_roles ur
LEFT JOIN gen_auth.users u ON ur.user_id = u.id
WHERE u.id IS NULL;

-- audit.signature_events → broken signature references
SELECT 'ORPHAN signature_events→signature' AS issue, se.id, se.signature_id
FROM audit.signature_events se
LEFT JOIN audit.electronic_signatures es ON se.signature_id = es.id
WHERE es.id IS NULL;

-- workflow.workflow_runs → broken workflow_definition references
SELECT 'ORPHAN workflow_runs→definition' AS issue, wr.id, wr.workflow_id
FROM workflow.workflow_runs wr
LEFT JOIN workflow.workflow_definitions wd ON wr.workflow_id = wd.id
WHERE wd.id IS NULL;

-- bio.sequence_versions → broken sequence references
SELECT 'ORPHAN sequence_versions→sequence' AS issue, sv.id, sv.sequence_db_id
FROM bio.sequence_versions sv
LEFT JOIN bio.sequences s ON sv.sequence_db_id = s.id
WHERE s.id IS NULL;

-- ai.chat_messages → broken session references
SELECT 'ORPHAN chat_messages→session' AS issue, cm.id, cm.session_id
FROM ai.chat_messages cm
LEFT JOIN ai.chat_sessions cs ON cm.session_id = cs.id
WHERE cs.id IS NULL;

-- ================================================================
-- SECTION 4: ORPHAN RECORD VALIDATION
-- ================================================================

-- Entities with no metadata values (may be incomplete records)
SELECT 'entities_without_values' AS check_name, me.id, me.entity_key, me.entity_type, me.name
FROM metadata.metadata_entities me
LEFT JOIN metadata.metadata_values mv ON mv.entity_id = me.id
WHERE mv.id IS NULL;

-- Metadata fields never referenced by any value
SELECT 'fields_never_used' AS check_name, mf.id, mf.name, mf.display_name, mf.category
FROM metadata.metadata_fields mf
LEFT JOIN metadata.metadata_values mv ON mv.field_id = mf.id
WHERE mv.id IS NULL;

-- Data sources with no connection config (unconfigured)
SELECT 'data_source_no_config' AS check_name, ds.id, ds.name, ds.connector_type
FROM connector.data_sources ds
LEFT JOIN connector.connection_configs cc ON cc.data_source_id = ds.id
WHERE cc.id IS NULL;

-- Data sources with no entities (never synced)
SELECT 'data_source_no_entities' AS check_name, ds.id, ds.name, ds.connector_type
FROM connector.data_sources ds
LEFT JOIN connector.entities e ON e.data_source_id = ds.id
WHERE e.id IS NULL;

-- Workflow definitions that have never been run
SELECT 'workflow_never_run' AS check_name, wd.id, wd.name, wd.trigger_type, wd.created_at
FROM workflow.workflow_definitions wd
LEFT JOIN workflow.workflow_runs wr ON wr.workflow_id = wd.id
WHERE wr.id IS NULL;

-- Sequences with no annotations
SELECT 'sequence_no_annotations' AS check_name, s.id, s.sequence_id, s.name, s.sequence_type
FROM bio.sequences s
LEFT JOIN bio.sequence_annotations sa ON sa.sequence_id = s.id
WHERE sa.id IS NULL;

-- ================================================================
-- SECTION 5: MISSING DATA VALIDATION
-- ================================================================

-- Check users with null required fields
SELECT 'user_missing_email' AS issue, id FROM gen_auth.users WHERE email IS NULL OR email = '';
SELECT 'user_missing_password' AS issue, id FROM gen_auth.users WHERE hashed_password IS NULL OR hashed_password = '';

-- Check metadata fields with missing display name or type
SELECT 'field_missing_display_name' AS issue, id, name FROM metadata.metadata_fields WHERE display_name IS NULL OR display_name = '';
SELECT 'field_missing_data_type' AS issue, id, name FROM metadata.metadata_fields WHERE data_type IS NULL OR data_type = '';

-- Check entities missing required fields
SELECT 'entity_missing_name' AS issue, id, entity_key FROM metadata.metadata_entities WHERE name IS NULL OR name = '';
SELECT 'entity_missing_type' AS issue, id, entity_key FROM metadata.metadata_entities WHERE entity_type IS NULL OR entity_type = '';

-- Check workflow definitions missing node/edge JSON
SELECT 'workflow_missing_nodes' AS issue, id, name FROM workflow.workflow_definitions WHERE nodes_json IS NULL OR nodes_json = '';
SELECT 'workflow_missing_edges' AS issue, id, name FROM workflow.workflow_definitions WHERE edges_json IS NULL OR edges_json = '';

-- Check audit logs missing hash (integrity check)
SELECT 'audit_log_missing_hash' AS issue, id, action FROM audit.audit_logs WHERE hash IS NULL OR hash = '';

-- Check connector compounds missing SMILES
SELECT 'compound_missing_smiles' AS issue, id, entity_key, name FROM connector.compounds WHERE smiles IS NULL OR smiles = '';

-- Check sequences missing sequence string
SELECT 'sequence_missing_string' AS issue, id, sequence_id FROM bio.sequences WHERE sequence_string IS NULL OR sequence_string = '';

-- ================================================================
-- SECTION 6: PUBLIC SCHEMA ORPHAN CHECK
-- Tables that still exist in public schema (should be empty/removed)
-- ================================================================
SELECT tablename, 
       (xpath('/row/c/text()', query_to_xml('SELECT COUNT(*) AS c FROM public.' || quote_ident(tablename), false, true, '')))[1]::text::int AS public_row_count
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
    'users','roles','permissions','role_permissions','user_roles',
    'metadata_fields','metadata_entities','metadata_values',
    'query_templates','query_history','analysis_workspaces',
    'data_sources','connection_configs','entities','fields',
    'compounds','audit_logs','lineage_nodes','lineage_edges',
    'sequences','workflow_definitions','chat_sessions','chat_messages'
)
ORDER BY tablename;

-- ================================================================
-- SECTION 7: BOOTSTRAP CHECK – Is gen_auth seeded?
-- ================================================================
-- Expected: 4 users, 4 roles, 7 permissions after service starts
SELECT 'users_count'       AS metric, COUNT(*)::text AS value FROM gen_auth.users      UNION ALL
SELECT 'roles_count',                  COUNT(*)::text         FROM gen_auth.roles       UNION ALL
SELECT 'permissions_count',            COUNT(*)::text         FROM gen_auth.permissions;

-- ================================================================
-- SECTION 8: METADATA BOOTSTRAP CHECK
-- ================================================================
-- Expected: fields and entities if /metadata/bootstrap was called
SELECT 'metadata_fields_count'   AS metric, COUNT(*)::text AS value FROM metadata.metadata_fields   UNION ALL
SELECT 'metadata_entities_count',            COUNT(*)::text         FROM metadata.metadata_entities;

-- ================================================================
-- END OF VERIFICATION SCRIPT
-- Share output of Section 1 (row counts) to confirm health status
-- ================================================================
