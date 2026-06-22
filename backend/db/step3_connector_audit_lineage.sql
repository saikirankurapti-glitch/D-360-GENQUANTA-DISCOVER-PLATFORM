-- ================================================================
-- STEP 3: Create connector + audit + lineage tables
-- Run AFTER step2 succeeds.
-- ================================================================

-- connector tables
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
    data_source_id INTEGER NOT NULL REFERENCES connector.data_sources(id) ON DELETE CASCADE,
    source_entity_id INTEGER NOT NULL REFERENCES connector.entities(id) ON DELETE CASCADE,
    source_field_id INTEGER NOT NULL REFERENCES connector.fields(id) ON DELETE CASCADE,
    target_entity_id INTEGER NOT NULL REFERENCES connector.entities(id) ON DELETE CASCADE,
    target_field_id INTEGER NOT NULL REFERENCES connector.fields(id) ON DELETE CASCADE,
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

-- audit tables
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
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_service ON audit.audit_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_status ON audit.audit_logs(status);

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
CREATE INDEX IF NOT EXISTS idx_audit_ev_eid ON audit.entity_versions(entity_id);

CREATE TABLE IF NOT EXISTS audit.audit_versions (
    id SERIAL PRIMARY KEY,
    audit_log_id INTEGER NOT NULL REFERENCES audit.audit_logs(id) ON DELETE CASCADE,
    entity_version_id INTEGER NOT NULL REFERENCES audit.entity_versions(id) ON DELETE CASCADE
);

-- lineage tables
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

-- Confirm: should return 3 schemas with their table counts
SELECT schemaname, COUNT(*) AS tables_created
FROM pg_tables
WHERE schemaname IN ('connector','audit','lineage')
GROUP BY schemaname ORDER BY schemaname;
