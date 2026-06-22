# =============================================================================
# GENQUANTAA Discover – PostgreSQL Schema Definitions (single DB: genquantaa)
# =============================================================================
-- Create schemas for each microservice
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS metadata;
CREATE SCHEMA IF NOT EXISTS query;
CREATE SCHEMA IF NOT EXISTS connector;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS lineage;
CREATE SCHEMA IF NOT EXISTS bio;
CREATE SCHEMA IF NOT EXISTS workflow;
CREATE SCHEMA IF NOT EXISTS ai;

-- You may add any extension requirements here (e.g., pgcrypto)
-- Example: CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
