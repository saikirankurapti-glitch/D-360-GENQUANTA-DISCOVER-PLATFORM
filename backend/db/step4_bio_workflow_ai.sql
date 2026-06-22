-- ================================================================
-- STEP 4: Create bio + workflow + ai tables
-- Run AFTER step3 succeeds.
-- ================================================================

-- bio tables
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

-- workflow tables
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

-- ai tables
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
-- FINAL CONFIRMATION — Run after all 4 steps complete
-- Expected: 9 schemas, total 42 tables
-- ================================================================
SELECT schemaname, COUNT(*) AS tables_created
FROM pg_tables
WHERE schemaname IN ('gen_auth','metadata','query','connector','audit','lineage','bio','workflow','ai')
GROUP BY schemaname
ORDER BY schemaname;
