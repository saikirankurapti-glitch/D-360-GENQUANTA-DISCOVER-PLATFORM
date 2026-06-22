import json
import time
import hashlib
import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from ...core.database import get_db
from ...repositories.template_repo import TemplateRepository
from ...schemas.template import QueryTemplateCreate, QueryTemplateResponse

from ...core.cache import cache
from ...core.engine import engine
from ...repositories.history_repo import HistoryRepository
from ...schemas.history import QueryHistoryResponse, QueryHistoryCreate

router = APIRouter(prefix="/query", tags=["query"])

# Compilation engine helper
def compile_graph_to_sql(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> str:
    select_fields = []
    from_table = None
    joins = []
    where_clauses = []
    
    node_map = {}
    for n in nodes:
        node_id = n.get("id")
        data = n.get("data", {})
        entity_type = data.get("entityType", "Compound")
        physical_table = data.get("physicalTableName")
        
        # Normalize name for table
        if entity_type.lower() in ["compound", "assay"]:
            table_name = f"{entity_type.lower()}s"
        else:
            table_name = physical_table if physical_table else entity_type
            if "." in table_name:
                table_name = table_name.split(".")[-1]
                
        alias_raw = entity_type.lower().replace(".", "_").replace("-", "_")
        node_map[node_id] = {
            "id": node_id,
            "entity_type": entity_type,
            "table_name": table_name,
            "alias": f"{alias_raw}_{node_id.replace('-', '_')[:8]}",
            "selected_fields": data.get("selectedFields", []),
            "filters": data.get("filters", [])
        }
        
    if not node_map:
        return "SELECT * FROM compounds"
        
    # First node in nodes list is the anchor/FROM table
    first_node_id = list(node_map.keys())[0]
    first_node = node_map[first_node_id]
    from_table = f"{first_node['table_name']} AS {first_node['alias']}"
    
    # Projection columns
    if first_node["selected_fields"]:
        for f in first_node["selected_fields"]:
            select_fields.append(f"{first_node['alias']}.{f}")
    else:
        select_fields.append(f"{first_node['alias']}.*")
        
    # Filters
    for flt in first_node["filters"]:
        field = flt.get("field")
        op = flt.get("operator", "=")
        val = flt.get("value")
        if not field or val is None:
            continue
        if op.lower() == "between":
            where_clauses.append(f"{first_node['alias']}.{field} BETWEEN {val}")
        else:
            if str(val).replace('.','',1).isdigit():
                where_clauses.append(f"{first_node['alias']}.{field} {op} {val}")
            else:
                where_clauses.append(f"{first_node['alias']}.{field} {op} '{val}'")

    joined_nodes = {first_node_id}
    
    # Walk edges to formulate Joins
    for edge in edges:
        source_id = edge.get("source")
        target_id = edge.get("target")
        
        if source_id not in node_map or target_id not in node_map:
            continue
            
        source_node = node_map[source_id]
        target_node = node_map[target_id]
        
        # Determine join target vs anchor
        node_to_join = None
        anchor_node = None
        
        if target_id not in joined_nodes:
            node_to_join = target_node
            anchor_node = source_node
            joined_nodes.add(target_id)
        elif source_id not in joined_nodes:
            node_to_join = source_node
            anchor_node = target_node
            joined_nodes.add(source_id)
            
        if node_to_join and anchor_node:
            # Infer join column key names dynamically
            join_col_anchor = "id"
            join_col_join = "id"
            rel_found = False
            
            try:
                import httpx
                resp = httpx.get("http://localhost:8002/api/v1/metadata/federation/relationships", timeout=1.0)
                if resp.status_code == 200:
                    relationships = resp.json()
                    rel = next((r for r in relationships if 
                        (r["source_entity_key"].lower() == anchor_node["entity_type"].lower() and 
                         r["target_entity_key"].lower() == node_to_join["entity_type"].lower()) or
                        (r["source_entity_key"].lower() == node_to_join["entity_type"].lower() and 
                         r["target_entity_key"].lower() == anchor_node["entity_type"].lower())
                    ), None)
                    if rel:
                        if rel["source_entity_key"].lower() == anchor_node["entity_type"].lower():
                            join_col_anchor = rel["source_field_name"]
                            join_col_join = rel["target_field_name"]
                        else:
                            join_col_anchor = rel["target_field_name"]
                            join_col_join = rel["source_field_name"]
                        rel_found = True
            except Exception:
                pass
                
            if not rel_found:
                # Fallback heuristics
                join_col_anchor = "id" if anchor_node["entity_type"].lower() == "compound" else "compound_id"
                join_col_join = "id" if node_to_join["entity_type"].lower() == "compound" else "compound_id"
            
            joins.append(
                f"INNER JOIN {node_to_join['table_name']} AS {node_to_join['alias']} "
                f"ON {anchor_node['alias']}.{join_col_anchor} = {node_to_join['alias']}.{join_col_join}"
            )
            
            # Projection columns for join node
            if node_to_join["selected_fields"]:
                for f in node_to_join["selected_fields"]:
                    select_fields.append(f"{node_to_join['alias']}.{f}")
            else:
                select_fields.append(f"{node_to_join['alias']}.*")
                
            # Filters for join node
            for flt in node_to_join["filters"]:
                field = flt.get("field")
                op = flt.get("operator", "=")
                val = flt.get("value")
                if not field or val is None:
                    continue
                if op.lower() == "between":
                    where_clauses.append(f"{node_to_join['alias']}.{field} BETWEEN {val}")
                else:
                    if str(val).replace('.','',1).isdigit():
                        where_clauses.append(f"{node_to_join['alias']}.{field} {op} {val}")
                    else:
                        where_clauses.append(f"{node_to_join['alias']}.{field} {op} '{val}'")

    # Build SQL text
    select_clause = ", ".join(select_fields)
    sql = f"SELECT {select_clause}\nFROM {from_table}"
    for j in joins:
        sql += f"\n{j}"
    if where_clauses:
        sql += f"\nWHERE {' AND '.join(where_clauses)}"
        
    return sql


@router.post("/compile")
def compile_query(payload: Dict[str, Any]):
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])
    try:
        sql = compile_graph_to_sql(nodes, edges)
        return {"sql": sql}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Compiler failure: {str(e)}"
        )


ACTIVE_QUERIES = {}

@router.post("/execute")
async def execute_query(payload: Dict[str, Any], db: Session = Depends(get_db)):
    sql = payload.get("sql", "").strip()
    if not sql:
        raise HTTPException(status_code=400, detail="SQL query is required")
        
    page = int(payload.get("page", 1))
    page_size = int(payload.get("page_size", 100))
    offset = (page - 1) * page_size
    
    use_cache = payload.get("use_cache", True)
    q_id = payload.get("query_id") or str(uuid.uuid4())
    
    # 1. Check Cache
    cache_key = f"query_{hashlib.md5(sql.encode('utf-8')).hexdigest()}_lim{page_size}_off{offset}"
    if use_cache:
        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result["statistics"]["cache_hit"] = True
            HistoryRepository.create_history_record(
                db, 
                QueryHistoryCreate(
                    sql=sql,
                    status="SUCCESS",
                    execution_time_ms=0.0,
                    row_count=len(cached_result.get("rows", [])),
                    error_message=None
                )
            )
            return cached_result
            
    # 2. Execute Federated Query
    start_time = time.time()
    try:
        loop = asyncio.get_event_loop()
        task = loop.create_task(engine.execute_federated_query(sql, limit=page_size, offset=offset))
        ACTIVE_QUERIES[q_id] = task
        
        columns, rows, stats = await task
        
        if q_id in ACTIVE_QUERIES:
            del ACTIVE_QUERIES[q_id]
            
        result = {
            "columns": columns,
            "rows": rows,
            "statistics": stats
        }
        
        cache.set(cache_key, result, ttl=300)
        
        HistoryRepository.create_history_record(
            db,
            QueryHistoryCreate(
                sql=sql,
                status="SUCCESS",
                execution_time_ms=stats["execution_time_ms"],
                row_count=len(rows),
                error_message=None
            )
        )
        return result
        
    except asyncio.CancelledError:
        exec_time = (time.time() - start_time) * 1000
        HistoryRepository.create_history_record(
            db,
            QueryHistoryCreate(
                sql=sql,
                status="FAILED",
                execution_time_ms=exec_time,
                row_count=0,
                error_message="Query execution cancelled by user."
            )
        )
        raise HTTPException(status_code=499, detail="Query cancelled by user.")
        
    except Exception as e:
        if q_id in ACTIVE_QUERIES:
            del ACTIVE_QUERIES[q_id]
        exec_time = (time.time() - start_time) * 1000
        error_msg = str(e)
        
        HistoryRepository.create_history_record(
            db,
            QueryHistoryCreate(
                sql=sql,
                status="FAILED",
                execution_time_ms=exec_time,
                row_count=0,
                error_message=error_msg
            )
        )
        raise HTTPException(status_code=500, detail=f"Query execution failed: {error_msg}")


@router.post("/explain")
async def explain_query(payload: Dict[str, Any]):
    sql = payload.get("sql", "").strip()
    if not sql:
        raise HTTPException(status_code=400, detail="SQL query is required")
    plan = await engine.explain_query_plan(sql)
    return {"plan": plan}


@router.get("/history", response_model=List[QueryHistoryResponse])
def get_query_history(limit: int = 50, db: Session = Depends(get_db)):
    return HistoryRepository.get_history(db, limit=limit)


@router.post("/cancel/{query_id}")
def cancel_query(query_id: str):
    if query_id in ACTIVE_QUERIES:
        task = ACTIVE_QUERIES[query_id]
        task.cancel()
        return {"status": "success", "message": "Query cancellation request sent."}
    raise HTTPException(status_code=404, detail="Active query ID not found")


# Template routes
@router.get("/templates", response_model=List[QueryTemplateResponse])
def get_templates(db: Session = Depends(get_db)):
    return TemplateRepository.get_templates(db)


@router.post("/templates", response_model=QueryTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(obj_in: QueryTemplateCreate, db: Session = Depends(get_db)):
    return TemplateRepository.create_template(db, obj_in=obj_in)


@router.get("/templates/{id}", response_model=QueryTemplateResponse)
def get_template(id: int, db: Session = Depends(get_db)):
    template = TemplateRepository.get_template_by_id(db, template_id=id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found."
        )
    return template


@router.delete("/templates/{id}")
def delete_template(id: int, db: Session = Depends(get_db)):
    success = TemplateRepository.delete_template(db, template_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found."
        )
    return {"message": "Template deleted successfully."}


@router.post("/templates/{id}/duplicate", response_model=QueryTemplateResponse)
def duplicate_template(id: int, db: Session = Depends(get_db)):
    duplicated = TemplateRepository.duplicate_template(db, template_id=id)
    if not duplicated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source template not found."
        )
    return duplicated
