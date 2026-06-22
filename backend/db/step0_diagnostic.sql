-- ================================================================
-- STEP 0: DIAGNOSTIC — Run this FIRST to see current DB state
-- ================================================================
-- What schemas currently exist?
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name NOT IN ('pg_catalog','information_schema','pg_toast','pg_temp_1','pg_toast_temp_1','extensions','graphql','graphql_public','realtime','pgbouncer','vault','pgsodium','supabase_functions','storage','_realtime')
ORDER BY schema_name;
