import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.schemas.audit_schema import AuditLogCreate
from typing import List, Optional

def compute_log_hash(
    timestamp_str: str,
    action: str,
    service_name: str,
    user_id: Optional[str],
    previous_hash: Optional[str]
) -> str:
    # Build payload string
    payload = f"{timestamp_str}|{action}|{service_name}|{user_id or ''}|{previous_hash or ''}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def create_audit_log(db: Session, log_in: AuditLogCreate) -> AuditLog:
    # 1. Fetch the last log entry in the database to get its hash
    last_log = db.query(AuditLog).order_by(AuditLog.id.desc()).first()
    previous_hash = last_log.hash if last_log else None
    
    timestamp = datetime.utcnow()
    timestamp_str = timestamp.isoformat()
    
    # 2. Compute SHA-256 hash
    log_hash = compute_log_hash(
        timestamp_str=timestamp_str,
        action=log_in.action,
        service_name=log_in.service_name,
        user_id=log_in.user_id,
        previous_hash=previous_hash
    )
    
    details_str = json.dumps(log_in.details) if log_in.details else None
    
    # 3. Save log
    db_log = AuditLog(
        timestamp=timestamp,
        user_id=log_in.user_id,
        username=log_in.username,
        action=log_in.action,
        service_name=log_in.service_name,
        endpoint=log_in.endpoint,
        status=log_in.status,
        ip_address=log_in.ip_address,
        details_json=details_str,
        previous_hash=previous_hash,
        hash=log_hash
    )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    service_name: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None
) -> List[AuditLog]:
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if service_name:
        query = query.filter(AuditLog.service_name == service_name)
    if action:
        query = query.filter(AuditLog.action == action)
    if status:
        query = query.filter(AuditLog.status == status)
        
    return query.order_by(AuditLog.id.desc()).offset(skip).limit(limit).all()

def get_audit_log(db: Session, log_id: int) -> Optional[AuditLog]:
    return db.query(AuditLog).filter(AuditLog.id == log_id).first()

def verify_chain_integrity(db: Session, target_id: int) -> dict:
    """
    Verifies that all logs up to target_id have intact hashes (chain is not broken).
    """
    # Fetch all logs from the start up to target_id ordered by id asc
    logs = db.query(AuditLog).filter(AuditLog.id <= target_id).order_by(AuditLog.id.asc()).all()
    if not logs:
        return {
            "log_id": target_id,
            "is_valid": False,
            "calculated_hash": "",
            "database_hash": "",
            "message": "Log entry not found.",
            "chain_intact": False
        }
        
    prev_hash = None
    for idx, log in enumerate(logs):
        # Verify previous hash matches what was computed
        if log.previous_hash != prev_hash:
            return {
                "log_id": log.id,
                "is_valid": False,
                "calculated_hash": "",
                "database_hash": log.hash,
                "message": f"Broken chain link: log previous_hash does not match actual previous hash at log id {log.id}",
                "chain_intact": False
            }
            
        # Compute hash
        calc_hash = compute_log_hash(
            timestamp_str=log.timestamp.isoformat(),
            action=log.action,
            service_name=log.service_name,
            user_id=log.user_id,
            previous_hash=prev_hash
        )
        
        if calc_hash != log.hash:
            return {
                "log_id": log.id,
                "is_valid": False,
                "calculated_hash": calc_hash,
                "database_hash": log.hash,
                "message": f"Data integrity failure: log data has been modified at log id {log.id}",
                "chain_intact": False
            }
            
        prev_hash = log.hash
        
    # If we made it to the target log successfully:
    target_log = logs[-1]
    return {
        "log_id": target_id,
        "is_valid": True,
        "calculated_hash": target_log.hash,
        "database_hash": target_log.hash,
        "message": f"Cryptographic validation successful. Chain intact up to log id {target_id}",
        "chain_intact": True
    }
