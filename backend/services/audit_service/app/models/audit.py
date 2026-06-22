from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "audit"}

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String, nullable=True)
    username = Column(String, nullable=True)
    action = Column(String, index=True, nullable=False)
    service_name = Column(String, index=True, nullable=False)
    endpoint = Column(String, nullable=True)
    status = Column(String, index=True, nullable=False) # e.g. "SUCCESS", "FAILURE"
    ip_address = Column(String, nullable=True)
    details_json = Column(Text, nullable=True) # Dynamic metadata/context details
    
    # Cryptographic validation fields
    previous_hash = Column(String, nullable=True)
    hash = Column(String, nullable=False, unique=True)

class ElectronicSignature(Base):
    __tablename__ = "electronic_signatures"
    __table_args__ = {"schema": "audit"}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    username = Column(String, nullable=False)
    signature_hash = Column(String, nullable=False, unique=True) # SHA-256 of user + password validation token + timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    events = relationship("SignatureEvent", back_populates="signature", cascade="all, delete-orphan")

class SignatureEvent(Base):
    __tablename__ = "signature_events"
    __table_args__ = {"schema": "audit"}

    id = Column(Integer, primary_key=True, index=True)
    signature_id = Column(Integer, ForeignKey("audit.electronic_signatures.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String, nullable=False, index=True) # e.g., "QUERY_APPROVAL", "DATASET_APPROVAL", "METADATA_APPROVAL", "WORKFLOW_APPROVAL", "EXPORT_APPROVAL"
    entity_id = Column(String, nullable=False, index=True) # e.g. query name, metadata key, dataset name
    reason = Column(String, nullable=False) # reason for signature
    meaning = Column(String, nullable=False) # e.g., "Author", "Reviewer", "Approved"
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    details_json = Column(Text, nullable=True)

    signature = relationship("ElectronicSignature", back_populates="events")

class EntityVersion(Base):
    __tablename__ = "entity_versions"
    __table_args__ = {"schema": "audit"}

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, index=True) # e.g., "MetadataField", "DataSource", "QueryTemplate"
    entity_id = Column(String, nullable=False, index=True) # unique key or string ID of target entity
    version = Column(Integer, nullable=False)
    data_json = Column(Text, nullable=False) # full serialized JSON string of the entity
    modified_by = Column(String, nullable=False)
    modified_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    change_summary = Column(String, nullable=True)
    is_deleted = Column(Integer, default=0, nullable=False) # Soft delete flag (0 = active, 1 = deleted)
    hash = Column(String, nullable=False) # content SHA-256 hash

class AuditVersion(Base):
    __tablename__ = "audit_versions"
    __table_args__ = {"schema": "audit"}

    id = Column(Integer, primary_key=True, index=True)
    audit_log_id = Column(Integer, ForeignKey("audit.audit_logs.id", ondelete="CASCADE"), nullable=False)
    entity_version_id = Column(Integer, ForeignKey("audit.entity_versions.id", ondelete="CASCADE"), nullable=False)
