from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.compliance_schema import (
    ElectronicSignatureCreate, 
    ElectronicSignatureResponse, 
    EntityVersionCreate, 
    EntityVersionResponse
)
from app.repositories import compliance_repo

router = APIRouter(prefix="/compliance", tags=["compliance"])

@router.post("/signatures", response_model=ElectronicSignatureResponse, status_code=201)
def record_signature(
    signature_in: ElectronicSignatureCreate,
    db: Session = Depends(get_db)
):
    """
    Submits an electronic signature event.
    """
    try:
        return compliance_repo.create_electronic_signature(db, signature_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to record electronic signature: {str(e)}"
        )

@router.get("/signatures", response_model=List[ElectronicSignatureResponse])
def fetch_signatures(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieves filterable paginated list of electronic signatures.
    """
    return compliance_repo.get_signatures(db, skip=skip, limit=limit)

@router.post("/versions", response_model=EntityVersionResponse, status_code=201)
def record_version(
    version_in: EntityVersionCreate,
    db: Session = Depends(get_db)
):
    """
    Logs an immutable snapshot version for an entity.
    """
    try:
        return compliance_repo.create_entity_version(db, version_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to record entity version: {str(e)}"
        )

@router.get("/versions", response_model=List[EntityVersionResponse])
def fetch_versions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Lists logged version snapshots.
    """
    return compliance_repo.get_entity_versions(db, skip=skip, limit=limit)

@router.get("/versions/{version_id}", response_model=EntityVersionResponse)
def get_version_by_id(version_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single version record.
    """
    version = compliance_repo.get_entity_version(db, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Entity version entry not found")
    return version

@router.get("/history/{entity_type}/{entity_id}", response_model=List[EntityVersionResponse])
def get_entity_version_history(
    entity_type: str,
    entity_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns full version history list for a specific entity.
    """
    return compliance_repo.get_entity_history(db, entity_type=entity_type, entity_id=entity_id)
