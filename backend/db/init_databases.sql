-- =============================================================================
-- AnalytiX Discover – PostgreSQL Database Initialization
-- Phase 8: Creates all service databases in a single PostgreSQL instance.
-- This script runs on first container startup via docker-entrypoint-initdb.d.
-- =============================================================================

-- Create service-specific databases
CREATE DATABASE genquantaa_auth;
CREATE DATABASE genquantaa_metadata;
CREATE DATABASE genquantaa_query;
CREATE DATABASE genquantaa_connector;
CREATE DATABASE genquantaa_audit;
CREATE DATABASE genquantaa_lineage;
CREATE DATABASE genquantaa_bioinfo;
CREATE DATABASE genquantaa_workflow;
CREATE DATABASE genquantaa_ai;

-- Note: 'cheminformatics' database is managed by the separate postgres-rdkit container
-- with RDKit extension support. It is NOT created here.

-- Grant all privileges to the postgres user on each database
GRANT ALL PRIVILEGES ON DATABASE genquantaa_auth TO postgres;
GRANT ALL PRIVILEGES ON DATABASE genquantaa_metadata TO postgres;
GRANT ALL PRIVILEGES ON DATABASE genquantaa_query TO postgres;
GRANT ALL PRIVILEGES ON DATABASE genquantaa_connector TO postgres;
GRANT ALL PRIVILEGES ON DATABASE genquantaa_audit TO postgres;
GRANT ALL PRIVILEGES ON DATABASE genquantaa_lineage TO postgres;
GRANT ALL PRIVILEGES ON DATABASE genquantaa_bioinfo TO postgres;
GRANT ALL PRIVILEGES ON DATABASE genquantaa_workflow TO postgres;
GRANT ALL PRIVILEGES ON DATABASE genquantaa_ai TO postgres;
