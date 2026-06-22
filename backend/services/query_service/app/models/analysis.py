from sqlalchemy import Column, Integer, String, Text
from ..core.database import Base

class AnalysisWorkspace(Base):
    __tablename__ = "analysis_workspaces"
    __table_args__ = {"schema": "query"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    query_history_id = Column(Integer, nullable=True)
    dataset_json = Column(Text, nullable=True)     # Serialized representation of columns and rows
    configs_json = Column(Text, nullable=False)     # Chart type selection, features, parameters, IC50 configuration
    created_at = Column(String(50), nullable=False)
