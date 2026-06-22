from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.bioinfo_schema import (
    SequenceResponse, 
    SequenceCreate, 
    PairwiseAlignmentRequest, 
    MultipleAlignmentRequest,
    SearchSequenceRequest, 
    SequenceClusterCreate, 
    SequenceClusterResponse,
    FastaImportRequest
)
from app.repositories import bioinfo_repo
from typing import List, Dict, Any, Optional

router = APIRouter()

@router.post("/sequences/import", response_model=List[SequenceResponse])
def import_sequences_fasta(
    req: FastaImportRequest,
    db: Session = Depends(get_db)
):
    content = req.fasta_data
    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty FASTA payload.")

    try:
        imported_seqs = bioinfo_repo.import_fasta(db, content)
        return imported_seqs
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"FASTA parsing failed: {str(e)}")

@router.get("/sequences", response_model=List[SequenceResponse])
def list_sequences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return bioinfo_repo.get_sequences(db, skip=skip, limit=limit)

@router.get("/sequences/{sequence_id}", response_model=SequenceResponse)
def get_sequence(sequence_id: str, db: Session = Depends(get_db)):
    seq = bioinfo_repo.get_sequence_by_id(db, sequence_id)
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found.")
    return seq

@router.get("/sequences/{sequence_id}/metrics")
def get_sequence_metrics(sequence_id: str, db: Session = Depends(get_db)):
    seq = bioinfo_repo.get_sequence_by_id(db, sequence_id)
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found.")
    
    # Calculate GC content for nucleotide sequences, or protein properties for proteins
    seq_str = seq.sequence_string
    if seq.sequence_type in ["DNA", "RNA"]:
        # GC Content
        gc_count = sum(1 for c in seq_str.upper() if c in "GC")
        gc_content = gc_count / len(seq_str) if len(seq_str) > 0 else 0.0
        return {
            "type": seq.sequence_type,
            "length": len(seq_str),
            "gc_content": round(gc_content, 4)
        }
    else:
        # Protein Params
        metrics = bioinfo_repo.calculate_protein_metrics(seq_str)
        return {
            "type": seq.sequence_type,
            "length": len(seq_str),
            **metrics
        }

@router.post("/alignments/pairwise")
def run_pairwise_alignment(req: PairwiseAlignmentRequest, db: Session = Depends(get_db)):
    seq_a = bioinfo_repo.get_sequence_by_id(db, req.seq_a_id)
    seq_b = bioinfo_repo.get_sequence_by_id(db, req.seq_b_id)
    if not seq_a or not seq_b:
        raise HTTPException(status_code=404, detail="One or both sequences not found.")
    
    try:
        res = bioinfo_repo.run_pairwise_alignment(req, seq_a.sequence_string, seq_b.sequence_string)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Alignment calculation failed: {str(e)}")

@router.post("/alignments/multiple")
def run_multiple_alignment(req: MultipleAlignmentRequest, db: Session = Depends(get_db)):
    db_seqs = db.query(bioinfo_repo.Sequence).filter(bioinfo_repo.Sequence.sequence_id.in_(req.seq_ids)).all()
    if len(db_seqs) < 2:
        raise HTTPException(status_code=400, detail="At least two sequences are required.")
    
    seq_tuples = [(s.sequence_id, s.sequence_string) for s in db_seqs]
    try:
        res = bioinfo_repo.run_multiple_alignment(seq_tuples)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Multiple alignment failed: {str(e)}")

@router.post("/search/sequence")
def search_sequences(req: SearchSequenceRequest, db: Session = Depends(get_db)):
    try:
        return bioinfo_repo.search_sequence(db, req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Search execution error: {str(e)}")

@router.post("/clusters", response_model=SequenceClusterResponse)
def run_clustering(req: SequenceClusterCreate, db: Session = Depends(get_db)):
    try:
        cluster = bioinfo_repo.perform_clustering(db, req)
        return cluster
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Clustering calculation failed: {str(e)}")

@router.get("/clusters", response_model=List[SequenceClusterResponse])
def list_clusters(db: Session = Depends(get_db)):
    return db.query(bioinfo_repo.SequenceCluster).all()

@router.get("/clusters/{cluster_id}", response_model=SequenceClusterResponse)
def get_cluster(cluster_id: int, db: Session = Depends(get_db)):
    cluster = db.query(bioinfo_repo.SequenceCluster).filter(bioinfo_repo.SequenceCluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster run not found.")
    return cluster
