# app/repositories/chemical_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Tuple, Optional
from app.models.chemical import Compound, MolType, HAS_RDKIT
from app.schemas.chemical import CompoundCreate
from app.utils.rdkit_utils import validate_and_canonicalize_smiles
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import DataStructs

def create_compound(db: Session, compound: CompoundCreate) -> Compound:
    """
    Inserts a compound into the database.
    Note: Database triggers handle the creation of RDKit cartridge fields (mol and morgan_bfp).
    """
    db_compound = Compound(
        entity_key=compound.entity_key,
        name=compound.name,
        smiles=compound.smiles
    )
    db.add(db_compound)
    db.commit()
    db.refresh(db_compound)
    return db_compound

def get_compound_by_key(db: Session, entity_key: str) -> Optional[Compound]:
    return db.query(Compound).filter(Compound.entity_key == entity_key).first()

def get_all_compounds(db: Session, limit: int = 100) -> List[Compound]:
    return db.query(Compound).limit(limit).all()

def exact_search(db: Session, query_smiles: str) -> List[Compound]:
    """
    Finds compounds matching the query structure exactly.
    Uses RDKit database cartridge operators if running on PostgreSQL,
    otherwise falls back to in-memory matching.
    """
    # Canonicalize the query structure first
    canonical = validate_and_canonicalize_smiles(query_smiles)
    if not canonical:
        return []

    is_postgres = db.bind.dialect.name == "postgresql" and HAS_RDKIT
    
    if is_postgres:
        # PostgreSQL exact match: '=' operator on 'mol' type
        query = text("SELECT id, entity_key, name, smiles FROM compounds WHERE mol = :query_smiles::mol")
        result = db.execute(query, {"query_smiles": canonical}).fetchall()
        return [
            Compound(id=r[0], entity_key=r[1], name=r[2], smiles=r[3])
            for r in result
        ]
    else:
        # Fallback for SQLite/Testing
        all_compounds = db.query(Compound).all()
        matches = []
        for c in all_compounds:
            c_canonical = validate_and_canonicalize_smiles(c.smiles)
            if c_canonical == canonical:
                matches.append(c)
        return matches

def substructure_search(db: Session, query_smiles: str, limit: int = 100) -> List[Compound]:
    """
    Finds compounds containing the query structure as a substructure.
    Uses PostgreSQL RDKit substructure operator (@>) for indexing, 
    otherwise falls back to RDKit's in-memory substructure matching.
    """
    is_postgres = db.bind.dialect.name == "postgresql" and HAS_RDKIT
    
    if is_postgres:
        query = text("""
            SELECT id, entity_key, name, smiles 
            FROM compounds 
            WHERE mol @> :query_smiles::mol 
            LIMIT :limit
        """)
        result = db.execute(query, {"query_smiles": query_smiles, "limit": limit}).fetchall()
        return [
            Compound(id=r[0], entity_key=r[1], name=r[2], smiles=r[3])
            for r in result
        ]
    else:
        # Fallback for SQLite/Testing using RDKit Python wrapper
        query_mol = Chem.MolFromSmiles(query_smiles)
        if not query_mol:
            return []
            
        all_compounds = db.query(Compound).all()
        matches = []
        for c in all_compounds:
            mol = Chem.MolFromSmiles(c.smiles)
            if mol and mol.HasSubstructMatch(query_mol):
                matches.append(c)
                if len(matches) >= limit:
                    break
        return matches

def similarity_search(
    db: Session, 
    query_smiles: str, 
    threshold: float = 0.7, 
    limit: int = 100
) -> List[Tuple[Compound, float]]:
    """
    Performs Tanimoto similarity search on circular fingerprints.
    Uses PostgreSQL RDKit cartridge similarity operators (%) with GiST indexes.
    Falls back to RDKit Python fingerprint calculations for local testing.
    """
    is_postgres = db.bind.dialect.name == "postgresql" and HAS_RDKIT
    
    if is_postgres:
        # Set database cartridge threshold for similarity operator
        db.execute(text("SET rdkit.tanimoto_threshold = :threshold").bindparams(threshold=threshold))
        
        # Query utilizing index-backed % operator and tanimoto_sml calculation
        query = text("""
            SELECT id, entity_key, name, smiles, 
                   tanimoto_sml(morgan_bfp, morganbv_fp(:query_smiles::mol)) as similarity
            FROM compounds
            WHERE morgan_bfp % morganbv_fp(:query_smiles::mol)
            ORDER BY similarity DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"query_smiles": query_smiles, "limit": limit}).fetchall()
        return [
            (Compound(id=r[0], entity_key=r[1], name=r[2], smiles=r[3]), float(r[4]))
            for r in result
        ]
    else:
        # Fallback for SQLite/Testing using RDKit python fingerprinting
        query_mol = Chem.MolFromSmiles(query_smiles)
        if not query_mol:
            return []
            
        query_fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(query_mol, 2, nBits=2048)
        
        all_compounds = db.query(Compound).all()
        results = []
        for c in all_compounds:
            mol = Chem.MolFromSmiles(c.smiles)
            if mol:
                fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
                similarity = DataStructs.TanimotoSimilarity(query_fp, fp)
                if similarity >= threshold:
                    results.append((c, similarity))
                    
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]
