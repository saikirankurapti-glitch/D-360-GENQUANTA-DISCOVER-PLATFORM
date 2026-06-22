from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from datetime import datetime
from app.core.database import Base

class LineageNode(Base):
    __tablename__ = "lineage_nodes"
    __table_args__ = {"schema": "lineage"}

    id = Column(String, primary_key=True, index=True) # e.g. "ds-postgres", "q-438", "export-1"
    type = Column(String, nullable=False) # e.g., "datasource", "query", "dataset", "analytics", "visualization", "export"
    name = Column(String, nullable=False)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LineageEdge(Base):
    __tablename__ = "lineage_edges"
    __table_args__ = {"schema": "lineage"}

    id = Column(String, primary_key=True, index=True) # e.g. "ds-postgres->q-438"
    source = Column(String, ForeignKey("lineage.lineage_nodes.id", ondelete="CASCADE"), nullable=False)
    target = Column(String, ForeignKey("lineage.lineage_nodes.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, default="flow", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
