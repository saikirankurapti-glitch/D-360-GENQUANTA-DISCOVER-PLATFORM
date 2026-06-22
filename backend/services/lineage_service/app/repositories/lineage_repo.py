import json
from sqlalchemy.orm import Session
from app.models.lineage import LineageNode, LineageEdge
from app.schemas.lineage_schema import LineageNodeCreate, LineageTraceRequest
from typing import List, Tuple

def create_or_update_node(db: Session, node_in: LineageNodeCreate) -> LineageNode:
    db_node = db.query(LineageNode).filter(LineageNode.id == node_in.id).first()
    details_str = json.dumps(node_in.details) if node_in.details else None
    
    if db_node:
        db_node.type = node_in.type
        db_node.name = node_in.name
        if details_str:
            db_node.details_json = details_str
    else:
        db_node = LineageNode(
            id=node_in.id,
            type=node_in.type,
            name=node_in.name,
            details_json=details_str
        )
        db.add(db_node)
        
    db.commit()
    db.refresh(db_node)
    return db_node

def record_trace(db: Session, trace_in: LineageTraceRequest) -> Tuple[LineageNode, LineageNode, LineageEdge]:
    # 1. Create source and target nodes if not exists
    src_node = create_or_update_node(db, trace_in.source_node)
    tgt_node = create_or_update_node(db, trace_in.target_node)
    
    # 2. Check if edge exists
    edge_id = f"{src_node.id}->{tgt_node.id}"
    db_edge = db.query(LineageEdge).filter(LineageEdge.id == edge_id).first()
    
    if not db_edge:
        db_edge = LineageEdge(
            id=edge_id,
            source=src_node.id,
            target=tgt_node.id,
            type=trace_in.edge_type or "flow"
        )
        db.add(db_edge)
        db.commit()
        db.refresh(db_edge)
        
    return src_node, tgt_node, db_edge

def get_graph(db: Session) -> Tuple[List[LineageNode], List[LineageEdge]]:
    nodes = db.query(LineageNode).all()
    edges = db.query(LineageEdge).all()
    return nodes, edges
