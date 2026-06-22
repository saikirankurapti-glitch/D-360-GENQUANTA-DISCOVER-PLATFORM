from sqlalchemy import Column, Integer, String, Text, Float, DateTime, func
from ..core.database import Base

class QueryHistory(Base):
    __tablename__ = "query_history"
    __table_args__ = {"schema": "query"}

    id = Column(Integer, primary_key=True, index=True)
    sql = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)  # SUCCESS, FAILED
    execution_time_ms = Column(Float, nullable=False)
    row_count = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
