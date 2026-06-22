from sqlalchemy import Column, Integer, String, Text
from ..core.database import Base

class QueryTemplate(Base):
    __tablename__ = "query_templates"
    __table_args__ = {"schema": "query"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    layout_json = Column(Text, nullable=False)  # Serialized React Flow nodes and edges JSON
    sql_preview = Column(Text, nullable=True)   # Cached generated Trino SQL string
    created_by = Column(String(100), nullable=True)
