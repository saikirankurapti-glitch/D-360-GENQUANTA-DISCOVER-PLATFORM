from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.config import settings
from app.schemas.audit_schema import AuditLogCreate, AuditLogResponse, AuditVerificationResponse
from app.repositories import audit_repo

router = APIRouter(prefix="/audit", tags=["audit"])

def verify_internal_secret(x_audit_secret: Optional[str] = Header(None)):
    if not x_audit_secret or x_audit_secret != settings.AUDIT_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal audit service secret key."
        )
    return True

@router.post("/logs", response_model=AuditLogResponse, status_code=201)
def record_log(
    log_in: AuditLogCreate,
    db: Session = Depends(get_db),
    _authorized: bool = Depends(verify_internal_secret)
):
    """
    Submits a new audit log record. Secured by internal secret header.
    """
    try:
        return audit_repo.create_audit_log(db, log_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record audit log: {str(e)}")

@router.get("/logs", response_model=List[AuditLogResponse])
def fetch_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[str] = Query(None),
    service_name: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns filterable list of audit logs (used by admin dashboard).
    """
    return audit_repo.get_audit_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        service_name=service_name,
        action=action,
        status=status
    )

@router.get("/logs/{log_id}", response_model=AuditLogResponse)
def get_log_by_id(log_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single audit log entry.
    """
    log = audit_repo.get_audit_log(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log entry not found")
    return log

@router.get("/logs/{log_id}/verify", response_model=AuditVerificationResponse)
def verify_log(log_id: int, db: Session = Depends(get_db)):
    """
    Cryptographically verifies database chain integrity up to this log ID.
    """
    return audit_repo.verify_chain_integrity(db, log_id)
