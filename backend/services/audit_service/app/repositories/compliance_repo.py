import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.audit import ElectronicSignature, SignatureEvent, EntityVersion, AuditVersion
from app.schemas.compliance_schema import ElectronicSignatureCreate, EntityVersionCreate
from typing import List, Optional

def create_electronic_signature(db: Session, signature_in: ElectronicSignatureCreate) -> ElectronicSignature:
    timestamp = datetime.utcnow()
    # Compute signature hash: SHA-256 of user metadata and validation proof
    payload = f"{signature_in.user_id}|{signature_in.username}|{signature_in.password_hash}|{timestamp.isoformat()}"
    signature_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    db_signature = ElectronicSignature(
        user_id=signature_in.user_id,
        username=signature_in.username,
        signature_hash=signature_hash,
        created_at=timestamp
    )
    db.add(db_signature)
    db.flush()

    for event_in in signature_in.events:
        details_str = json.dumps(event_in.details) if event_in.details else None
        db_event = SignatureEvent(
            signature_id=db_signature.id,
            action_type=event_in.action_type,
            entity_id=event_in.entity_id,
            reason=event_in.reason,
            meaning=event_in.meaning,
            timestamp=timestamp,
            details_json=details_str
        )
        db.add(db_event)

    db.commit()
    db.refresh(db_signature)
    return db_signature

def get_signatures(db: Session, skip: int = 0, limit: int = 100) -> List[ElectronicSignature]:
    return db.query(ElectronicSignature).order_by(ElectronicSignature.id.desc()).offset(skip).limit(limit).all()

def create_entity_version(db: Session, version_in: EntityVersionCreate) -> EntityVersion:
    # 1. Check for the previous version of this entity
    last_version = (
        db.query(EntityVersion)
        .filter(EntityVersion.entity_type == version_in.entity_type)
        .filter(EntityVersion.entity_id == version_in.entity_id)
        .order_by(EntityVersion.version.desc())
        .first()
    )
    new_version_num = (last_version.version + 1) if last_version else 1

    # 2. Compute checksum hash of version data
    timestamp = datetime.utcnow()
    payload = f"{version_in.entity_type}|{version_in.entity_id}|{new_version_num}|{version_in.data_json}|{timestamp.isoformat()}"
    version_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    db_version = EntityVersion(
        entity_type=version_in.entity_type,
        entity_id=version_in.entity_id,
        version=new_version_num,
        data_json=version_in.data_json,
        modified_by=version_in.modified_by,
        modified_at=timestamp,
        change_summary=version_in.change_summary,
        is_deleted=version_in.is_deleted,
        hash=version_hash
    )
    db.add(db_version)
    db.flush()

    # 3. Create mapping link if audit_log_id is provided
    if version_in.audit_log_id:
        db_link = AuditVersion(
            audit_log_id=version_in.audit_log_id,
            entity_version_id=db_version.id
        )
        db.add(db_link)

    db.commit()
    db.refresh(db_version)
    return db_version

def get_entity_versions(db: Session, skip: int = 0, limit: int = 100) -> List[EntityVersion]:
    return db.query(EntityVersion).order_by(EntityVersion.id.desc()).offset(skip).limit(limit).all()

def get_entity_version(db: Session, version_id: int) -> Optional[EntityVersion]:
    return db.query(EntityVersion).filter(EntityVersion.id == version_id).first()

def get_entity_history(db: Session, entity_type: str, entity_id: str) -> List[EntityVersion]:
    return (
        db.query(EntityVersion)
        .filter(EntityVersion.entity_type == entity_type)
        .filter(EntityVersion.entity_id == entity_id)
        .order_by(EntityVersion.version.desc())
        .all()
    )
