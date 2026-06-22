# app/api/endpoints/chemistry.py
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.chemical import (
    CompoundCreate, CompoundResponse, SearchResult, 
    DescriptorResponse, FingerprintResponse, SARRequest, SARResponse
)
from app.repositories import chemical_repository
from app.utils import rdkit_utils

router = APIRouter()

@router.post("/compounds", response_model=CompoundResponse, status_code=201)
def create_compound(compound: CompoundCreate, db: Session = Depends(get_db)):
    """
    Registers a new chemical compound in the discovery database.
    Molecular descriptors and fingerprints are updated automatically by the database.
    """
    db_comp = chemical_repository.get_compound_by_key(db, compound.entity_key)
    if db_comp:
        raise HTTPException(status_code=400, detail="Compound with this entity key already exists")
    return chemical_repository.create_compound(db, compound)

@router.get("/compounds", response_model=List[CompoundResponse])
def get_compounds(limit: int = Query(100, description="Max compounds to return"), db: Session = Depends(get_db)):
    """
    Lists all registered chemical compounds.
    """
    return chemical_repository.get_all_compounds(db, limit=limit)

@router.get("/compounds/{entity_key}", response_model=CompoundResponse)
def get_compound(entity_key: str, db: Session = Depends(get_db)):
    """
    Retrieves a compound by its unique entity key.
    """
    db_comp = chemical_repository.get_compound_by_key(db, entity_key)
    if not db_comp:
        raise HTTPException(status_code=404, detail="Compound not found")
    return db_comp

@router.get("/search", response_model=List[SearchResult])
def search_structures(
    smiles: str = Query(..., description="Query molecule structure in SMILES format"),
    type: str = Query("exact", description="Type of search: exact, substructure, similarity"),
    threshold: float = Query(0.7, description="Similarity threshold (0.0 to 1.0) for similarity search"),
    limit: int = Query(100, description="Max results to return"),
    db: Session = Depends(get_db)
):
    """
    Performs exact structure, substructure, or similarity search.
    Utilizes PostgreSQL RDKit cartridge indices where available.
    """
    # Validate structure format first
    canonical = rdkit_utils.validate_and_canonicalize_smiles(smiles)
    if not canonical:
        raise HTTPException(status_code=400, detail="Invalid query SMILES structure")

    if type == "exact":
        results = chemical_repository.exact_search(db, canonical)
        return [SearchResult(id=r.id, entity_key=r.entity_key, name=r.name, smiles=r.smiles) for r in results]
        
    elif type == "substructure":
        results = chemical_repository.substructure_search(db, canonical, limit)
        return [SearchResult(id=r.id, entity_key=r.entity_key, name=r.name, smiles=r.smiles) for r in results]
        
    elif type == "similarity":
        if not (0.0 <= threshold <= 1.0):
            raise HTTPException(status_code=400, detail="Similarity threshold must be between 0.0 and 1.0")
        results = chemical_repository.similarity_search(db, canonical, threshold, limit)
        return [
            SearchResult(id=r[0].id, entity_key=r[0].entity_key, name=r[0].name, smiles=r[0].smiles, similarity=r[1])
            for r in results
        ]
        
    else:
        raise HTTPException(status_code=400, detail="Invalid search type. Select 'exact', 'substructure', or 'similarity'")

@router.get("/descriptors", response_model=DescriptorResponse)
def get_descriptors(smiles: str = Query(..., description="SMILES representation of the molecule")):
    """
    Calculates 1D/2D chemical descriptors for a given SMILES structure.
    """
    canonical = rdkit_utils.validate_and_canonicalize_smiles(smiles)
    if not canonical:
        raise HTTPException(status_code=400, detail="Invalid SMILES structure")
        
    props = rdkit_utils.calculate_descriptors(canonical)
    if props is None:
        raise HTTPException(status_code=500, detail="Failed to calculate molecular properties")
        
    return DescriptorResponse(smiles=canonical, **props)

@router.get("/fingerprints", response_model=FingerprintResponse)
def get_fingerprint(
    smiles: str = Query(..., description="SMILES representation of the molecule"),
    radius: int = Query(2, description="Morgan fingerprint radius"),
    n_bits: int = Query(2048, description="Fingerprint bit vector length")
):
    """
    Generates Morgan fingerprint bit vector represented as a hexadecimal string.
    """
    canonical = rdkit_utils.validate_and_canonicalize_smiles(smiles)
    if not canonical:
        raise HTTPException(status_code=400, detail="Invalid SMILES structure")
        
    fp_hex = rdkit_utils.generate_fingerprint_hex(canonical, radius, n_bits)
    if fp_hex is None:
        raise HTTPException(status_code=500, detail="Failed to generate molecular fingerprint")
        
    return FingerprintResponse(smiles=canonical, fingerprint_hex=fp_hex)

@router.get("/draw")
def draw_molecule(
    smiles: str = Query(..., description="SMILES representation of the molecule"),
    size: int = Query(300, description="Image width and height in pixels")
):
    """
    Renders the molecule structure and returns it as a vector SVG image.
    """
    canonical = rdkit_utils.validate_and_canonicalize_smiles(smiles)
    if not canonical:
        raise HTTPException(status_code=400, detail="Invalid SMILES structure")
        
    svg_text = rdkit_utils.draw_molecule_svg(canonical, size)
    if not svg_text:
        raise HTTPException(status_code=500, detail="Failed to draw chemical structure")
        
    return Response(content=svg_text, media_type="image/svg+xml")

@router.post("/sar", response_model=SARResponse)
def get_sar_analysis(request: SARRequest):
    """
    Executes Structure-Activity Relationship (SAR) analysis.
    Performs R-group decomposition of analogues against a core scaffold
    and detects significant activity cliffs.
    """
    sar_results = rdkit_utils.perform_sar_analysis(
        compounds=[{"smiles": c.smiles, "activity": c.activity, "name": c.name} for c in request.compounds],
        scaffold_smiles=request.scaffold_smiles
    )
    if "error" in sar_results:
        raise HTTPException(status_code=422, detail=sar_results["error"])
        
    return sar_results
