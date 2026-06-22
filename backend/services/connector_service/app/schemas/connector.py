from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime

# Connection config schemas
class ConnectionConfigBase(BaseModel):
    encrypted_credentials: str = Field(..., description="Encrypted credentials JSON string")
    additional_params: Optional[str] = Field(None, description="Non-sensitive metadata params JSON string")

class ConnectionConfigCreate(ConnectionConfigBase):
    pass

class ConnectionConfigResponse(BaseModel):
    id: int
    data_source_id: int
    additional_params: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Data source schemas
class DataSourceBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    connector_type: str = Field(..., description="Connector identifier (postgresql, oracle, etc.)")
    is_active: bool = True

class DataSourceCreate(DataSourceBase):
    credentials: Dict[str, Any] = Field(..., description="Plaintext credentials to be encrypted")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Extra connector specific parameters")

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    credentials: Optional[Dict[str, Any]] = None
    additional_params: Optional[Dict[str, Any]] = None

class DataSourceResponse(DataSourceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    config: Optional[ConnectionConfigResponse] = None

    model_config = ConfigDict(from_attributes=True)

# Schema Discovery / Field / Entity schemas
class FieldResponse(BaseModel):
    id: int
    entity_id: int
    physical_name: str
    display_name: str
    data_type: str
    is_nullable: bool
    is_primary_key: bool
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EntityResponse(BaseModel):
    id: int
    data_source_id: int
    physical_name: str
    display_name: str
    description: Optional[str] = None
    is_queryable: bool
    fields: List[FieldResponse] = []

    model_config = ConfigDict(from_attributes=True)

class RelationshipCreate(BaseModel):
    source_entity_id: int
    source_field_id: int
    target_entity_id: int
    target_field_id: int
    cardinality: str = "1:N"

class RelationshipResponse(BaseModel):
    id: int
    data_source_id: int
    source_entity_id: int
    source_field_id: int
    target_entity_id: int
    target_field_id: int
    cardinality: str

    model_config = ConfigDict(from_attributes=True)

# Connection Test schemas
class ConnectionTestRequest(BaseModel):
    connector_type: str
    credentials: Dict[str, Any]
    additional_params: Optional[Dict[str, Any]] = None

class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    details: Optional[str] = None

# Query schemas
class FilterItem(BaseModel):
    field: str
    operator: str  # '=', '!=', '>', '<', 'LIKE', 'IN', etc.
    value: Any

class QueryExecutionRequest(BaseModel):
    entity: str
    fields: List[str]
    filters: Optional[List[FilterItem]] = None
    limit: int = 100

class QueryExecutionResponse(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float

# Sync history
class SyncHistoryResponse(BaseModel):
    id: int
    data_source_id: int
    sync_status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_synced: int
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Capabilities
class ConnectorCapability(BaseModel):
    connector_type: str
    name: str
    description: str
    required_credentials: List[str]
    supported_operations: List[str]
