-- ================================================================
-- STEP 2 FIX: Drop old UUID tables, recreate with INTEGER PKs
-- The old database_setup.sql used UUID PKs — our models use INTEGER.
-- This script drops old gen_auth/metadata/query tables and rebuilds.
-- ================================================================

-- ── Drop old gen_auth tables (reverse FK order) ────────────────
DROP TABLE IF EXISTS gen_auth.user_roles        CASCADE;
DROP TABLE IF EXISTS gen_auth.role_permissions  CASCADE;
DROP TABLE IF EXISTS gen_auth.permissions       CASCADE;
DROP TABLE IF EXISTS gen_auth.roles             CASCADE;
DROP TABLE IF EXISTS gen_auth.users             CASCADE;

-- ── Drop old metadata tables (reverse FK order) ────────────────
DROP TABLE IF EXISTS metadata.metadata_values        CASCADE;
DROP TABLE IF EXISTS metadata.metadata_sync_history  CASCADE;
DROP TABLE IF EXISTS metadata.metadata_versions      CASCADE;
DROP TABLE IF EXISTS metadata.metadata_relationships CASCADE;
DROP TABLE IF EXISTS metadata.metadata_entities      CASCADE;
DROP TABLE IF EXISTS metadata.metadata_fields        CASCADE;

-- ── Drop old query tables ──────────────────────────────────────
DROP TABLE IF EXISTS query.analysis_workspaces CASCADE;
DROP TABLE IF EXISTS query.query_history       CASCADE;
DROP TABLE IF EXISTS query.query_templates     CASCADE;

-- ── Drop old connector tables (reverse FK order) ───────────────
DROP TABLE IF EXISTS connector.connector_sync_checkpoints CASCADE;
DROP TABLE IF EXISTS connector.connector_sync_history     CASCADE;
DROP TABLE IF EXISTS connector.relationships              CASCADE;
DROP TABLE IF EXISTS connector.fields                     CASCADE;
DROP TABLE IF EXISTS connector.entities                   CASCADE;
DROP TABLE IF EXISTS connector.connection_configs         CASCADE;
DROP TABLE IF EXISTS connector.compounds                  CASCADE;
DROP TABLE IF EXISTS connector.data_sources               CASCADE;

-- ── Drop old audit tables (reverse FK order) ───────────────────
DROP TABLE IF EXISTS audit.audit_versions        CASCADE;
DROP TABLE IF EXISTS audit.signature_events      CASCADE;
DROP TABLE IF EXISTS audit.entity_versions       CASCADE;
DROP TABLE IF EXISTS audit.electronic_signatures CASCADE;
DROP TABLE IF EXISTS audit.audit_logs            CASCADE;

-- ── Drop old lineage tables ────────────────────────────────────
DROP TABLE IF EXISTS lineage.lineage_edges CASCADE;
DROP TABLE IF EXISTS lineage.lineage_nodes CASCADE;

-- ── Drop old bio tables ────────────────────────────────────────
DROP TABLE IF EXISTS bio.sequence_clusters     CASCADE;
DROP TABLE IF EXISTS bio.alignments            CASCADE;
DROP TABLE IF EXISTS bio.sequence_annotations  CASCADE;
DROP TABLE IF EXISTS bio.sequence_versions     CASCADE;
DROP TABLE IF EXISTS bio.sequences             CASCADE;

-- ── Drop old workflow tables (reverse FK order) ────────────────
DROP TABLE IF EXISTS workflow.workflow_approvals   CASCADE;
DROP TABLE IF EXISTS workflow.workflow_steps       CASCADE;
DROP TABLE IF EXISTS workflow.workflow_events      CASCADE;
DROP TABLE IF EXISTS workflow.workflow_schedules   CASCADE;
DROP TABLE IF EXISTS workflow.workflow_runs        CASCADE;
DROP TABLE IF EXISTS workflow.workflow_definitions CASCADE;

-- ── Drop old ai tables ─────────────────────────────────────────
DROP TABLE IF EXISTS ai.chat_messages CASCADE;
DROP TABLE IF EXISTS ai.chat_sessions CASCADE;

-- ================================================================
-- Confirm all old tables gone before proceeding
-- Expected: 0 rows (no leftover tables)
-- ================================================================
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname IN ('gen_auth','metadata','query','connector','audit','lineage','bio','workflow','ai')
ORDER BY schemaname, tablename;
