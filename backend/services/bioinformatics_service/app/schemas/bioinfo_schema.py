from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any

class SequenceAnnotationCreate(BaseModel):
    feature_type: str
    start: int
    end: int
    strand: Optional[int] = 1
    name: str
    notes: Optional[str] = None

class SequenceAnnotationResponse(BaseModel):
    id: int
    sequence_id: int
    feature_type: str
    start: int
    end: int
    strand: int
    name: str
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class SequenceCreate(BaseModel):
    sequence_id: str
    name: str
    description: Optional[str] = None
    sequence_type: str # DNA, RNA, Protein
    sequence_string: str
    annotations: Optional[List[SequenceAnnotationCreate]] = None

class SequenceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sequence_string: Optional[str] = None
    change_summary: Optional[str] = None
    modified_by: Optional[str] = "system"

class SequenceVersionResponse(BaseModel):
    id: int
    sequence_db_id: int
    version: int
    sequence_string: str
    modified_by: str
    modified_at: datetime
    change_summary: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class SequenceResponse(BaseModel):
    id: int
    sequence_id: str
    name: str
    description: Optional[str]
    sequence_type: str
    sequence_string: str
    created_at: datetime
    annotations: List[SequenceAnnotationResponse]
    versions: List[SequenceVersionResponse]

    model_config = ConfigDict(from_attributes=True)

class PairwiseAlignmentRequest(BaseModel):
    seq_a_id: str
    seq_b_id: str
    alignment_type: str = "global" # global or local
    match_score: float = 1.0
    mismatch_score: float = -1.0
    open_gap_score: float = -0.5
    extend_gap_score: float = -0.1

class MultipleAlignmentRequest(BaseModel):
    seq_ids: List[str]

class SearchSequenceRequest(BaseModel):
    query_string: str
    search_type: str = "exact" # exact, motif, or similarity
    threshold: Optional[float] = 0.7 # For similarity search

class SequenceClusterCreate(BaseModel):
    name: str
    seq_ids: List[str]
    method: str = "hierarchical"
    distance_metric: str = "identity"

class SequenceClusterResponse(BaseModel):
    id: int
    name: str
    method: str
    distance_metric: str
    matrix_json: str
    linkage_json: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FastaImportRequest(BaseModel):
    fasta_data: str
