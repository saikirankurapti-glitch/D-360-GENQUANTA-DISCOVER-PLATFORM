-- db/init_rdkit.sql
-- Database initialization script for Cheminformatics Service with PostgreSQL RDKit Cartridge

-- Enable the RDKit extension
CREATE EXTENSION IF NOT EXISTS rdkit;

-- Create compounds table supporting RDKit cartridge data types
CREATE TABLE IF NOT EXISTS compounds (
    id SERIAL PRIMARY KEY,
    entity_key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    smiles TEXT NOT NULL,
    mol mol,                       -- RDKit molecule representation
    morgan_bfp bfp,                -- Binary Fingerprint (Morgan/circular)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to automatically populate RDKit molecular fields from SMILES
CREATE OR REPLACE FUNCTION compute_compound_rdkit_fields() 
RETURNS TRIGGER AS $$
BEGIN
    BEGIN
        -- Cast SMILES string directly to mol type
        NEW.mol := NEW.smiles::mol;
        -- Generate Morgan fingerprint (radius 2, 2048 bits)
        NEW.morgan_bfp := morganbv_fp(NEW.mol);
    EXCEPTION WHEN OTHERS THEN
        -- If SMILES is invalid or RDKit fails, set fields to NULL
        NEW.mol := NULL;
        NEW.morgan_bfp := NULL;
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Bind trigger to table for INSERT and UPDATE operations
DROP TRIGGER IF EXISTS trg_compounds_rdkit_fields ON compounds;
CREATE TRIGGER trg_compounds_rdkit_fields
BEFORE INSERT OR UPDATE OF smiles ON compounds
FOR EACH ROW
EXECUTE FUNCTION compute_compound_rdkit_fields();

-- Create GiST indexes for accelerated chemical structure searching
-- GiST index on mol type speeds up substructure search (@>) and exact matching (=)
CREATE INDEX IF NOT EXISTS idx_compounds_mol ON compounds USING gist(mol);

-- GiST index on bfp type speeds up Tanimoto similarity searches (%)
CREATE INDEX IF NOT EXISTS idx_compounds_bfp ON compounds USING gist(morgan_bfp);
