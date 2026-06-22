from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class MetadataFieldBase(BaseModel):
    name: str
    display_name: str
    data_type: str
    description: Optional[str] = None
    category: Optional[str] = "General"
    is_required: Optional[bool] = False

class MetadataFieldCreate(MetadataFieldBase):
    pass

class MetadataFieldResponse(MetadataFieldBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MetadataValueBase(BaseModel):
    field_id: int
    value: str

class MetadataValueCreate(MetadataValueBase):
    pass

class MetadataValueResponse(MetadataValueBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MetadataEntityBase(BaseModel):
    entity_key: str
    entity_type: str
    name: str
    description: Optional[str] = None

class MetadataEntityCreate(MetadataEntityBase):
    values: List[MetadataValueCreate] = []

class MetadataEntityResponse(MetadataEntityBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Helper schemas for consolidated views
class FieldValueDetail(BaseModel):
    field_name: str
    display_name: str
    category: str
    data_type: str
    value: str

class EntityDetailResponse(BaseModel):
    id: int
    entity_key: str
    entity_type: str
    name: str
    description: Optional[str] = None
    attributes: Dict[str, Any] = {}
    details: List[FieldValueDetail] = []

    model_config = ConfigDict(from_attributes=True)


# --- Federation Schemas ---

class MetadataRelationshipBase(BaseModel):
    datasource_id: int
    source_entity_key: str
    source_field_name: str
    target_entity_key: str
    target_field_name: str
    cardinality: str

class MetadataRelationshipCreate(MetadataRelationshipBase):
    pass

class MetadataRelationshipResponse(MetadataRelationshipBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MetadataVersionBase(BaseModel):
    datasource_id: int
    version: int
    snapshot_data: str
    changes_detected: Optional[str] = None

class MetadataVersionResponse(MetadataVersionBase):
    id: int
    created_at: Any
    model_config = ConfigDict(from_attributes=True)


class MetadataSyncHistoryBase(BaseModel):
    datasource_id: int
    datasource_name: str
    status: str
    started_at: Any
    completed_at: Any
    records_synced: int
    error_message: Optional[str] = None
    changes_detected: Optional[str] = None

class MetadataSyncHistoryResponse(MetadataSyncHistoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Input payload for /federation/sync
class FederatedFieldSchema(BaseModel):
    field_name: str
    data_type: str
    is_nullable: bool = True
    is_primary_key: bool = False
    description: Optional[str] = None

class FederatedEntitySchema(BaseModel):
    entity_name: str
    description: Optional[str] = None
    fields: List[FederatedFieldSchema]

class FederatedRelationshipSchema(BaseModel):
    source_entity_name: str
    source_field_name: str
    target_entity_name: str
    target_field_name: str
    cardinality: str = "1:N"

class MetadataFederationSyncPayload(BaseModel):
    datasource_id: int
    datasource_name: str
    entities: List[FederatedEntitySchema]
    relationships: List[FederatedRelationshipSchema]

