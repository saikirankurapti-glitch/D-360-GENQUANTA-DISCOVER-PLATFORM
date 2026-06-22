from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, DateTime, Text, func
from sqlalchemy.orm import relationship
from ..core.database import Base

class MetadataField(Base):
    __tablename__ = "metadata_fields"
    __table_args__ = {"schema": "metadata"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # string, numeric, boolean, date
    description = Column(String, nullable=True)
    category = Column(String, default="General", nullable=False)  # Assay, Chemistry, In Vivo, Clinical
    is_required = Column(Boolean, default=False, nullable=False)

    values = relationship("MetadataValue", back_populates="field", cascade="all, delete-orphan")


class MetadataEntity(Base):
    __tablename__ = "metadata_entities"
    __table_args__ = {"schema": "metadata"}

    id = Column(Integer, primary_key=True, index=True)
    entity_key = Column(String, unique=True, index=True, nullable=False)  # E.g. CMP-00123, ASSAY-402
    entity_type = Column(String, index=True, nullable=False)  # Compound, Assay, Study, Dataset, Table
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    values = relationship("MetadataValue", back_populates="entity", cascade="all, delete-orphan")


class MetadataValue(Base):
    __tablename__ = "metadata_values"
    __table_args__ = (
        UniqueConstraint("entity_id", "field_id", name="uix_entity_field"),
        {"schema": "metadata"},
    )

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("metadata.metadata_entities.id", ondelete="CASCADE"), nullable=False)
    field_id = Column(Integer, ForeignKey("metadata.metadata_fields.id", ondelete="CASCADE"), nullable=False)
    value = Column(String, nullable=False)

    entity = relationship("MetadataEntity", back_populates="values")
    field = relationship("MetadataField", back_populates="values")


class MetadataRelationship(Base):
    __tablename__ = "metadata_relationships"
    __table_args__ = {"schema": "metadata"}

    id = Column(Integer, primary_key=True, index=True)
    datasource_id = Column(Integer, nullable=False, index=True)
    source_entity_key = Column(String, nullable=False)
    source_field_name = Column(String, nullable=False)
    target_entity_key = Column(String, nullable=False)
    target_field_name = Column(String, nullable=False)
    cardinality = Column(String, default="1:N", nullable=False)  # 1:1, 1:N, N:1


class MetadataVersion(Base):
    __tablename__ = "metadata_versions"
    __table_args__ = {"schema": "metadata"}

    id = Column(Integer, primary_key=True, index=True)
    datasource_id = Column(Integer, nullable=False, index=True)
    version = Column(Integer, nullable=False)
    snapshot_data = Column(Text, nullable=False)  # JSON representation of entities and fields
    changes_detected = Column(Text, nullable=True)  # JSON detailing schema edits
    created_at = Column(DateTime, server_default=func.now())


class MetadataSyncHistory(Base):
    __tablename__ = "metadata_sync_history"
    __table_args__ = {"schema": "metadata"}

    id = Column(Integer, primary_key=True, index=True)
    datasource_id = Column(Integer, nullable=False, index=True)
    datasource_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # SUCCESS, FAILED
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=False)
    records_synced = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    changes_detected = Column(Text, nullable=True)
