from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any, List

class LineageNodeCreate(BaseModel):
    id: str
    type: str
    name: str
    details: Optional[Dict[str, Any]] = None

class LineageEdgeCreate(BaseModel):
    source: str
    target: str
    type: Optional[str] = "flow"

class LineageTraceRequest(BaseModel):
    source_node: LineageNodeCreate
    target_node: LineageNodeCreate
    edge_type: Optional[str] = "flow"

class LineageNodeResponse(BaseModel):
    id: str
    type: str
    name: str
    details_json: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LineageEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LineageGraphResponse(BaseModel):
    nodes: List[LineageNodeResponse]
    edges: List[LineageEdgeResponse]
