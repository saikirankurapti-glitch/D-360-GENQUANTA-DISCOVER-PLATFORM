-- ================================================================
-- STEP 1: Create Extensions + All 9 Schemas
-- Run this first. Expected: "Success. No rows returned."
-- ================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE SCHEMA IF NOT EXISTS gen_auth;
CREATE SCHEMA IF NOT EXISTS metadata;
CREATE SCHEMA IF NOT EXISTS query;
CREATE SCHEMA IF NOT EXISTS connector;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS lineage;
CREATE SCHEMA IF NOT EXISTS bio;
CREATE SCHEMA IF NOT EXISTS workflow;
CREATE SCHEMA IF NOT EXISTS ai;

-- Confirm: should return 9 rows
SELECT schema_name FROM information_schema.schemata
WHERE schema_name IN ('gen_auth','metadata','query','connector','audit','lineage','bio','workflow','ai')
ORDER BY schema_name;
