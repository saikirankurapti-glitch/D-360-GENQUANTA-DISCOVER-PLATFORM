from typing import Optional
from pydantic import BaseModel, ConfigDict

class AnalysisWorkspaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    query_history_id: Optional[int] = None
    dataset_json: Optional[str] = None
    configs_json: str

class AnalysisWorkspaceCreate(AnalysisWorkspaceBase):
    pass

class AnalysisWorkspaceResponse(AnalysisWorkspaceBase):
    id: int
    created_at: str
    model_config = ConfigDict(from_attributes=True)
