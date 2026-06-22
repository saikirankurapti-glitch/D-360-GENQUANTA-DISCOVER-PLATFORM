from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class AuditLogCreate(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    action: str
    service_name: str
    endpoint: Optional[str] = None
    status: str
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    user_id: Optional[str]
    username: Optional[str]
    action: str
    service_name: str
    endpoint: Optional[str]
    status: str
    ip_address: Optional[str]
    details_json: Optional[str]
    previous_hash: Optional[str]
    hash: str

    class Config:
        from_attributes = True

class AuditVerificationResponse(BaseModel):
    log_id: int
    is_valid: bool
    calculated_hash: str
    database_hash: str
    message: str
    chain_intact: bool
