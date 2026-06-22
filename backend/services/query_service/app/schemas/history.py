from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class QueryHistoryBase(BaseModel):
    sql: str
    status: str
    execution_time_ms: float
    row_count: int
    error_message: Optional[str] = None

class QueryHistoryCreate(QueryHistoryBase):
    pass

class QueryHistoryResponse(QueryHistoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
