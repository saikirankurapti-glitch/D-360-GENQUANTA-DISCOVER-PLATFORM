from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class SignatureEventCreate(BaseModel):
    action_type: str # QUERY_APPROVAL, DATASET_APPROVAL, etc.
    entity_id: str
    reason: str
    meaning: str
    details: Optional[Dict[str, Any]] = None

class ElectronicSignatureCreate(BaseModel):
    user_id: str
    username: str
    password_hash: str # The password proof hash
    events: List[SignatureEventCreate]

class SignatureEventResponse(BaseModel):
    id: int
    signature_id: int
    action_type: str
    entity_id: str
    reason: str
    meaning: str
    timestamp: datetime
    details_json: Optional[str]

    class Config:
        from_attributes = True

class ElectronicSignatureResponse(BaseModel):
    id: int
    user_id: str
    username: str
    signature_hash: str
    created_at: datetime
    events: List[SignatureEventResponse]

    class Config:
        from_attributes = True

class EntityVersionCreate(BaseModel):
    entity_type: str
    entity_id: str
    data_json: str
    modified_by: str
    change_summary: Optional[str] = None
    is_deleted: Optional[int] = 0
    audit_log_id: Optional[int] = None

class EntityVersionResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    version: int
    data_json: str
    modified_by: str
    modified_at: datetime
    change_summary: Optional[str]
    is_deleted: int
    hash: str

    class Config:
        from_attributes = True
