-- ================================================================
-- STEP 2B (FIXED): Create ALL tables with INTEGER PKs
-- Uses IF NOT EXISTS everywhere — safe to re-run multiple times.
-- ================================================================

-- ── gen_auth ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gen_auth.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    role VARCHAR NOT NULL DEFAULT 'Scientist',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_gen_auth_users_email ON gen_auth.users(email);

CREATE TABLE IF NOT EXISTS gen_auth.roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_gen_auth_roles_name ON gen_auth.roles(name);

CREATE TABLE IF NOT EXISTS gen_auth.permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_gen_auth_permissions_name ON gen_auth.permissions(name);

CREATE TABLE IF NOT EXISTS gen_auth.role_permissions (
    role_id INTEGER NOT NULL REFERENCES gen_auth.roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES gen_auth.permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS gen_auth.user_roles (
    user_id INTEGER NOT NULL REFERENCES gen_auth.users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES gen_auth.roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- ── metadata ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS metadata.metadata_fields (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    display_name VARCHAR NOT NULL,
    data_type VARCHAR NOT NULL,
    description VARCHAR,
    category VARCHAR NOT NULL DEFAULT 'General',
    is_required BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS idx_metadata_fields_name ON metadata.metadata_fields(name);

CREATE TABLE IF NOT EXISTS metadata.metadata_entities (
    id SERIAL PRIMARY KEY,
    entity_key VARCHAR UNIQUE NOT NULL,
    entity_type VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR
);
CREATE INDEX IF NOT EXISTS idx_metadata_entities_key  ON metadata.metadata_entities(entity_key);
CREATE INDEX IF NOT EXISTS idx_metadata_entities_type ON metadata.metadata_entities(entity_type);

CREATE TABLE IF NOT EXISTS metadata.metadata_values (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES metadata.metadata_entities(id) ON DELETE CASCADE,
    field_id  INTEGER NOT NULL REFERENCES metadata.metadata_fields(id)   ON DELETE CASCADE,
    value VARCHAR NOT NULL,
    CONSTRAINT uix_entity_field UNIQUE (entity_id, field_id)
);

CREATE TABLE IF NOT EXISTS metadata.metadata_relationships (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    source_entity_key VARCHAR NOT NULL,
    source_field_name VARCHAR NOT NULL,
    target_entity_key VARCHAR NOT NULL,
    target_field_name VARCHAR NOT NULL,
    cardinality VARCHAR NOT NULL DEFAULT '1:N'
);

CREATE TABLE IF NOT EXISTS metadata.metadata_versions (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    snapshot_data TEXT NOT NULL,
    changes_detected TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS metadata.metadata_sync_history (
    id SERIAL PRIMARY KEY,
    datasource_id INTEGER NOT NULL,
    datasource_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    records_synced INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    changes_detected TEXT
);

-- ── query ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS query.query_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    layout_json TEXT NOT NULL,
    sql_preview TEXT,
    created_by VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS query.query_history (
    id SERIAL PRIMARY KEY,
    sql TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    execution_time_ms DOUBLE PRECISION NOT NULL,
    row_count INTEGER NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS query.analysis_workspaces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    query_history_id INTEGER,
    dataset_json TEXT,
    configs_json TEXT NOT NULL,
    created_at VARCHAR(50) NOT NULL
);

-- ── connector ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS connector.data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    connector_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS connector.connection_configs (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER UNIQUE NOT NULL REFERENCES connector.data_sources(id) ON DELETE CASCADE,
    encrypted_credentials TEXT NOT NULL,
    additional_params TEXT
);

CREATE TABLE IF NOT EXISTS connector.entities (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL REFERENCES connector.data_sources(id) ON DELETE CASCADE,
    physical_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    is_queryable BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS connector.fields (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES connector.entities(id) ON DELETE CASCADE,
    physical_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    is_nullable BOOLEAN NOT NULL DEFAULT TRUE,
    is_primary_key BOOLEAN NOT NULL DEFAULT FALSE,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS connector.relationships (
    id SERIAL PRIMARY KEY,
    data_source_id   INTEGER NOT NULL REFERENCES connector.data_sources(id) ON DELETE CASCADE,
    source_entity_id INTEGER NOT NULL REFERENCES connector.entities(id)      ON DELETE CASCADE,
    source_field_id  INTEGER NOT NULL REFERENCES connector.fields(id)        ON DELETE CASCADE,
    target_entity_id INTEGER NOT NULL REFERENCES connector.entities(id)      ON DELETE CASCADE,
    target_field_id  INTEGER NOT NULL REFERENCES connector.fields(id)        ON DELETE CASCADE,
    cardinality VARCHAR(20) NOT NULL DEFAULT '1:N'
);

CREATE TABLE IF NOT EXISTS connector.connector_sync_history (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL REFERENCES connector.data_sources(id) ON DELETE CASCADE,
    sync_status VARCHAR(20) NOT NULL,
    started_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    records_synced INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS connector.connector_sync_checkpoints (
    id SERIAL PRIMARY KEY,
    data_source_id INTEGER NOT NULL REFERENCES connector.data_sources(id) ON DELETE CASCADE,
    entity_name VARCHAR(100) NOT NULL,
    last_sync_timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    cursor_value VARCHAR(255),
    sync_status VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS connector.compounds (
    id SERIAL PRIMARY KEY,
    entity_key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    smiles VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_connector_compounds_key ON connector.compounds(entity_key);

-- ── audit ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit.audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT now(),
    user_id VARCHAR,
    username VARCHAR,
    action VARCHAR NOT NULL,
    service_name VARCHAR NOT NULL,
    endpoint VARCHAR,
    status VARCHAR NOT NULL,
    ip_address VARCHAR,
    details_json TEXT,
    previous_hash VARCHAR,
    hash VARCHAR NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action  ON audit.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_service ON audit.audit_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_status  ON audit.audit_logs(status);

CREATE TABLE IF NOT EXISTS audit.electronic_signatures (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    username VARCHAR NOT NULL,
    signature_hash VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_audit_esig_user ON audit.electronic_signatures(user_id);

CREATE TABLE IF NOT EXISTS audit.signature_events (
    id SERIAL PRIMARY KEY,
    signature_id INTEGER NOT NULL REFERENCES audit.electronic_signatures(id) ON DELETE CASCADE,
    action_type VARCHAR NOT NULL,
    entity_id VARCHAR NOT NULL,
    reason VARCHAR NOT NULL,
    meaning VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT now(),
    details_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_sigevt_action ON audit.signature_events(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_sigevt_entity ON audit.signature_events(entity_id);

CREATE TABLE IF NOT EXISTS audit.entity_versions (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR NOT NULL,
    entity_id VARCHAR NOT NULL,
    version INTEGER NOT NULL,
    data_json TEXT NOT NULL,
    modified_by VARCHAR NOT NULL,
    modified_at TIMESTAMP NOT NULL DEFAULT now(),
    change_summary VARCHAR,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    hash VARCHAR NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_ev_type ON audit.entity_versions(entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_ev_eid  ON audit.entity_versions(entity_id);

CREATE TABLE IF NOT EXISTS audit.audit_versions (
    id SERIAL PRIMARY KEY,
    audit_log_id      INTEGER NOT NULL REFERENCES audit.audit_logs(id)      ON DELETE CASCADE,
    entity_version_id INTEGER NOT NULL REFERENCES audit.entity_versions(id) ON DELETE CASCADE
);

-- ── lineage ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lineage.lineage_nodes (
    id VARCHAR PRIMARY KEY,
    type VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    details_json TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS lineage.lineage_edges (
    id VARCHAR PRIMARY KEY,
    source VARCHAR NOT NULL REFERENCES lineage.lineage_nodes(id) ON DELETE CASCADE,
    target VARCHAR NOT NULL REFERENCES lineage.lineage_nodes(id) ON DELETE CASCADE,
    type VARCHAR NOT NULL DEFAULT 'flow',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- ── bio ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bio.sequences (
    id SERIAL PRIMARY KEY,
    sequence_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR,
    sequence_type VARCHAR NOT NULL,
    sequence_string TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_bio_sequences_sid ON bio.sequences(sequence_id);

CREATE TABLE IF NOT EXISTS bio.sequence_versions (
    id SERIAL PRIMARY KEY,
    sequence_db_id INTEGER NOT NULL REFERENCES bio.sequences(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    sequence_string TEXT NOT NULL,
    modified_by VARCHAR NOT NULL,
    modified_at TIMESTAMP NOT NULL DEFAULT now(),
    change_summary VARCHAR
);

CREATE TABLE IF NOT EXISTS bio.sequence_annotations (
    id SERIAL PRIMARY KEY,
    sequence_id INTEGER NOT NULL REFERENCES bio.sequences(id) ON DELETE CASCADE,
    feature_type VARCHAR NOT NULL,
    start INTEGER NOT NULL,
    "end" INTEGER NOT NULL,
    strand INTEGER NOT NULL DEFAULT 1,
    name VARCHAR NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS bio.alignments (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    alignment_type VARCHAR NOT NULL,
    sequences_metadata TEXT,
    alignment_data TEXT NOT NULL,
    score DOUBLE PRECISION,
    consensus TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bio.sequence_clusters (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    method VARCHAR NOT NULL,
    distance_metric VARCHAR NOT NULL,
    matrix_json TEXT NOT NULL,
    linkage_json TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- ── workflow ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS workflow.workflow_definitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    nodes_json TEXT NOT NULL,
    edges_json TEXT NOT NULL,
    trigger_type VARCHAR(50) DEFAULT 'MANUAL',
    cron_schedule VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow.workflow_runs (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflow.workflow_definitions(id),
    status VARCHAR(50) DEFAULT 'PENDING',
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    current_step_idx INTEGER DEFAULT 0,
    logs TEXT
);

CREATE TABLE IF NOT EXISTS workflow.workflow_steps (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES workflow.workflow_runs(id),
    step_id VARCHAR(50) NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    node_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    inputs_json TEXT,
    outputs_json TEXT,
    logs TEXT,
    execution_time_ms DOUBLE PRECISION DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS workflow.workflow_schedules (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP,
    next_run TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow.workflow_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    payload_json TEXT NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflow.workflow_approvals (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES workflow.workflow_runs(id),
    step_id VARCHAR(50) NOT NULL,
    role_required VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    requested_at TIMESTAMP,
    completed_at TIMESTAMP,
    approved_by VARCHAR(100),
    signature_hash VARCHAR(256),
    comment TEXT
);

-- ── ai ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ai.chat_sessions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai.chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES ai.chat_sessions(id),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    citations_json TEXT,
    created_at TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_ai_messages_session ON ai.chat_messages(session_id);

-- ================================================================
-- FINAL CONFIRMATION
-- Expected: ai=2, audit=5, bio=5, connector=8,
--           gen_auth=5, lineage=2, metadata=6, query=3, workflow=6
-- ================================================================
SELECT schemaname, COUNT(*) AS tables_created
FROM pg_tables
WHERE schemaname IN ('gen_auth','metadata','query','connector','audit','lineage','bio','workflow','ai')
GROUP BY schemaname
ORDER BY schemaname;
