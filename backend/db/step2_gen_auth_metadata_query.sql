-- ================================================================
-- STEP 2: Create gen_auth + metadata + query tables
-- Run AFTER step1_schemas.sql succeeds.
-- ================================================================

-- gen_auth tables
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

-- metadata tables
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
CREATE INDEX IF NOT EXISTS idx_metadata_entities_key ON metadata.metadata_entities(entity_key);
CREATE INDEX IF NOT EXISTS idx_metadata_entities_type ON metadata.metadata_entities(entity_type);

CREATE TABLE IF NOT EXISTS metadata.metadata_values (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES metadata.metadata_entities(id) ON DELETE CASCADE,
    field_id INTEGER NOT NULL REFERENCES metadata.metadata_fields(id) ON DELETE CASCADE,
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

-- query tables
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

-- Confirm: should return 3 schemas with their table counts
SELECT schemaname, COUNT(*) AS tables_created
FROM pg_tables
WHERE schemaname IN ('gen_auth','metadata','query')
GROUP BY schemaname ORDER BY schemaname;
