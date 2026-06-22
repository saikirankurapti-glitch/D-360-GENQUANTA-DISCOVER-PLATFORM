from typing import Optional
from pydantic import BaseModel, ConfigDict

class QueryTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    layout_json: str
    sql_preview: Optional[str] = None
    created_by: Optional[str] = None

class QueryTemplateCreate(QueryTemplateBase):
    pass

class QueryTemplateResponse(QueryTemplateBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
