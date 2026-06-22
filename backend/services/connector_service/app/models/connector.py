from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class DataSource(Base):
    __tablename__ = "data_sources"
    __table_args__ = {"schema": "connector"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    connector_type = Column(String(50), nullable=False)  # postgresql, oracle, sqlserver, snowflake, file, rest_api
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    config = relationship("ConnectionConfig", back_populates="data_source", uselist=False, cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="data_source", cascade="all, delete-orphan")
    sync_history = relationship("SyncHistory", back_populates="data_source", cascade="all, delete-orphan")
    relationships = relationship("Relationship", back_populates="data_source", cascade="all, delete-orphan")
    sync_checkpoints = relationship("SyncCheckpoint", back_populates="data_source", cascade="all, delete-orphan")



class ConnectionConfig(Base):
    __tablename__ = "connection_configs"
    __table_args__ = {"schema": "connector"}

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("connector.data_sources.id", ondelete="CASCADE"), unique=True, nullable=False)
    encrypted_credentials = Column(Text, nullable=False)  # Encrypted host, username, password, token, etc.
    additional_params = Column(Text, nullable=True)      # Any extra non-sensitive params as a JSON string

    # Relationships
    data_source = relationship("DataSource", back_populates="config")


class Entity(Base):
    __tablename__ = "entities"
    __table_args__ = {"schema": "connector"}

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("connector.data_sources.id", ondelete="CASCADE"), nullable=False)
    physical_name = Column(String(100), nullable=False)  # Real table/view name, or API path
    display_name = Column(String(100), nullable=False)   # Scientist-friendly name
    description = Column(String(255), nullable=True)
    is_queryable = Column(Boolean, default=True, nullable=False)

    # Relationships
    data_source = relationship("DataSource", back_populates="entities")
    fields = relationship("Field", back_populates="entity", cascade="all, delete-orphan")


class Field(Base):
    __tablename__ = "fields"
    __table_args__ = {"schema": "connector"}

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("connector.entities.id", ondelete="CASCADE"), nullable=False)
    physical_name = Column(String(100), nullable=False)  # Real column name
    display_name = Column(String(100), nullable=False)   # Scientist-friendly name
    data_type = Column(String(50), nullable=False)       # integer, float, string, date, boolean
    is_nullable = Column(Boolean, default=True, nullable=False)
    is_primary_key = Column(Boolean, default=False, nullable=False)
    description = Column(String(255), nullable=True)

    # Relationships
    entity = relationship("Entity", back_populates="fields")


class Relationship(Base):
    __tablename__ = "relationships"
    __table_args__ = {"schema": "connector"}

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("connector.data_sources.id", ondelete="CASCADE"), nullable=False)
    source_entity_id = Column(Integer, ForeignKey("connector.entities.id", ondelete="CASCADE"), nullable=False)
    source_field_id = Column(Integer, ForeignKey("connector.fields.id", ondelete="CASCADE"), nullable=False)
    target_entity_id = Column(Integer, ForeignKey("connector.entities.id", ondelete="CASCADE"), nullable=False)
    target_field_id = Column(Integer, ForeignKey("connector.fields.id", ondelete="CASCADE"), nullable=False)
    cardinality = Column(String(20), default="1:N", nullable=False)  # 1:1, 1:N, N:1

    # Relationships mapping
    data_source = relationship("DataSource", back_populates="relationships")
    source_entity = relationship("Entity", foreign_keys=[source_entity_id])
    target_entity = relationship("Entity", foreign_keys=[target_entity_id])
    source_field = relationship("Field", foreign_keys=[source_field_id])
    target_field = relationship("Field", foreign_keys=[target_field_id])


class SyncHistory(Base):
    __tablename__ = "connector_sync_history"
    __table_args__ = {"schema": "connector"}

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("connector.data_sources.id", ondelete="CASCADE"), nullable=False)
    sync_status = Column(String(20), nullable=False)  # RUNNING, SUCCESS, FAILED
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    records_synced = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    data_source = relationship("DataSource", back_populates="sync_history")


class SyncCheckpoint(Base):
    __tablename__ = "connector_sync_checkpoints"
    __table_args__ = {"schema": "connector"}

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, ForeignKey("connector.data_sources.id", ondelete="CASCADE"), nullable=False)
    entity_name = Column(String(100), nullable=False)
    last_sync_timestamp = Column(DateTime, nullable=False, server_default=func.now())
    cursor_value = Column(String(255), nullable=True)
    sync_status = Column(String(20), nullable=False)  # SUCCESS, FAILED

    # Relationships
    data_source = relationship("DataSource", back_populates="sync_checkpoints")
