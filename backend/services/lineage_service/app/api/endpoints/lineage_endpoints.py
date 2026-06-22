from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.lineage_schema import LineageTraceRequest, LineageGraphResponse
from app.repositories import lineage_repo

router = APIRouter(prefix="/lineage", tags=["lineage"])

@router.post("/trace", status_code=201)
def record_lineage_trace(
    trace_in: LineageTraceRequest,
    db: Session = Depends(get_db)
):
    """
    Submits a connection step in data lineage trace (e.g. query running on datasource).
    """
    try:
        src, tgt, edge = lineage_repo.record_trace(db, trace_in)
        return {
            "status": "recorded",
            "source_node_id": src.id,
            "target_node_id": tgt.id,
            "edge_id": edge.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record lineage trace: {str(e)}"
        )

@router.get("/graph", response_model=LineageGraphResponse)
def fetch_graph(db: Session = Depends(get_db)):
    """
    Retrieves complete nodes and edges mapping of the data lineage tree.
    """
    nodes, edges = lineage_repo.get_graph(db)
    return {
        "nodes": nodes,
        "edges": edges
    }
