import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.connector import DataSource, Entity
from app.schemas.connector import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    EntityResponse,
    RelationshipCreate,
    RelationshipResponse,
    ConnectionTestRequest,
    ConnectionTestResponse,
    QueryExecutionRequest,
    QueryExecutionResponse,
    SyncHistoryResponse,
    ConnectorCapability
)
from app.repositories.connector_repository import repo
from app.connectors.registry import ConnectorRegistry

# We import the connectors package to ensure all connectors register themselves
import app.connectors

router = APIRouter()

@router.get("/capabilities", response_model=List[ConnectorCapability])
def get_connector_capabilities():
    """Returns capabilities and required credentials schemas for all registered connector types."""
    return ConnectorRegistry.get_all_capabilities()


@router.get("/sources", response_model=List[DataSourceResponse])
def list_data_sources(active_only: bool = False, db: Session = Depends(get_db)):
    """Lists all configured data sources in the metadata database."""
    return repo.get_all_data_sources(db, active_only=active_only)


import base64

def get_user_from_request(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"id": "system", "email": "system-admin@analytix.com"}
    try:
        token = auth_header.split(" ")[1]
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = base64.b64decode(payload_b64).decode("utf-8")
        payload = json.loads(payload_json)
        return {
            "id": payload.get("sub", "system"),
            "email": payload.get("email") or payload.get("sub") or "system-admin@analytix.com"
        }
    except Exception:
        return {"id": "system", "email": "system-admin@analytix.com"}

@router.post("/sources", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_data_source(request: Request, obj_in: DataSourceCreate, db: Session = Depends(get_db)):
    """Creates a new data source and encrypts credentials."""
    db_source = repo.create_data_source(db, obj_in)
    user = get_user_from_request(request)
    
    from app.core.compliance_client import log_audit_event, log_entity_version
    audit_id = log_audit_event(
        action="CREATE_CONNECTOR",
        service_name="connector_service",
        user_id=user["id"],
        username=user["email"],
        endpoint="/api/v1/sources",
        status="SUCCESS",
        details={"connector_id": db_source.id, "connector_name": db_source.name}
    )
    
    source_dict = {
        "id": db_source.id,
        "name": db_source.name,
        "description": db_source.description,
        "connector_type": db_source.connector_type,
        "is_active": db_source.is_active
    }
    log_entity_version(
        entity_type="DataSource",
        entity_id=str(db_source.id),
        data_json=json.dumps(source_dict),
        modified_by=user["email"],
        change_summary="Created data source connector",
        is_deleted=0,
        audit_log_id=audit_id
    )
    return db_source


@router.get("/sources/{source_id}", response_model=DataSourceResponse)
def get_data_source(source_id: int, db: Session = Depends(get_db)):
    """Gets details for a specific data source."""
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return db_source


@router.put("/sources/{source_id}", response_model=DataSourceResponse)
def update_data_source(request: Request, source_id: int, obj_in: DataSourceUpdate, db: Session = Depends(get_db)):
    """Updates an existing data source's configuration."""
    db_source = repo.update_data_source(db, source_id, obj_in)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    user = get_user_from_request(request)
    from app.core.compliance_client import log_audit_event, log_entity_version
    audit_id = log_audit_event(
        action="UPDATE_CONNECTOR",
        service_name="connector_service",
        user_id=user["id"],
        username=user["email"],
        endpoint=f"/api/v1/sources/{source_id}",
        status="SUCCESS",
        details={"connector_id": db_source.id, "connector_name": db_source.name}
    )
    
    source_dict = {
        "id": db_source.id,
        "name": db_source.name,
        "description": db_source.description,
        "connector_type": db_source.connector_type,
        "is_active": db_source.is_active
    }
    log_entity_version(
        entity_type="DataSource",
        entity_id=str(db_source.id),
        data_json=json.dumps(source_dict),
        modified_by=user["email"],
        change_summary="Updated data source connector config",
        is_deleted=0,
        audit_log_id=audit_id
    )
    return db_source


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data_source(request: Request, source_id: int, db: Session = Depends(get_db)):
    """Soft deletes a data source by setting is_active = False (No hard delete allowed)."""
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    # Soft delete instead of hard delete
    repo.update_data_source(db, source_id, DataSourceUpdate(is_active=False))
    
    user = get_user_from_request(request)
    from app.core.compliance_client import log_audit_event, log_entity_version
    audit_id = log_audit_event(
        action="DELETE_CONNECTOR",
        service_name="connector_service",
        user_id=user["id"],
        username=user["email"],
        endpoint=f"/api/v1/sources/{source_id}",
        status="SUCCESS",
        details={"connector_id": db_source.id, "connector_name": db_source.name, "deleted": "soft"}
    )
    
    source_dict = {
        "id": db_source.id,
        "name": db_source.name,
        "description": db_source.description,
        "connector_type": db_source.connector_type,
        "is_active": False
    }
    log_entity_version(
        entity_type="DataSource",
        entity_id=str(db_source.id),
        data_json=json.dumps(source_dict),
        modified_by=user["email"],
        change_summary="Soft deleted data source connector",
        is_deleted=1,
        audit_log_id=audit_id
    )
    return None


@router.post("/test-raw", response_model=ConnectionTestResponse)
async def test_raw_connection(request: ConnectionTestRequest):
    """
    Tests connection credentials in real-time.
    Used in wizards prior to registering the data source.
    """
    try:
        connector_class = ConnectorRegistry.get_connector(request.connector_type)
        connector = connector_class(request.credentials, request.additional_params)
        success, message = await connector.test_connection()
        return ConnectionTestResponse(success=success, message=message)
    except Exception as e:
        return ConnectionTestResponse(success=False, message="Connection test failed.", details=str(e))


@router.post("/sources/{source_id}/test", response_model=ConnectionTestResponse)
async def test_saved_connection(source_id: int, db: Session = Depends(get_db)):
    """Tests connection to a stored data source using its encrypted credentials."""
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    try:
        credentials = repo.get_decrypted_credentials(db, source_id)
        add_params = json.loads(db_source.config.additional_params) if db_source.config.additional_params else {}
        
        connector_class = ConnectorRegistry.get_connector(db_source.connector_type)
        connector = connector_class(credentials, add_params)
        
        success, message = await connector.test_connection()
        return ConnectionTestResponse(success=success, message=message)
    except Exception as e:
        return ConnectionTestResponse(success=False, message="Saved connection test failed.", details=str(e))


@router.post("/sources/{source_id}/sync", response_model=SyncHistoryResponse)
async def sync_data_source_schema(source_id: int, db: Session = Depends(get_db)):
    """
    Triggers dynamic schema discovery on the data source.
    Refreshes entities and columns in metadata tables and registers a sync log.
    """
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    start_time = datetime.utcnow()
    try:
        credentials = repo.get_decrypted_credentials(db, source_id)
        add_params = json.loads(db_source.config.additional_params) if db_source.config.additional_params else {}
        
        connector_class = ConnectorRegistry.get_connector(db_source.connector_type)
        connector = connector_class(credentials, add_params)
        
        if hasattr(connector, "sync_entities"):
            synced_count = await connector.sync_entities(db, source_id)
            # Log success and return directly since sync_entities handles propagation
            sync_log = repo.log_sync_history(
                db, source_id, status="SUCCESS", records=synced_count, started_at=start_time
            )
            return sync_log
        else:
            # Trigger schema discovery on the remote database/API/file
            discovered_schema = await connector.discover_schema()
            # Synchronize metadata catalogs
            synced_count = repo.refresh_entities_metadata(db, source_id, discovered_schema)
        
        # Query relationships to sync
        relationships = []
        try:
            db_rels = repo.get_relationships(db, source_id)
            relationships = [
                {
                    "source_entity_name": r.source_entity.physical_name,
                    "source_field_name": r.source_field.physical_name,
                    "target_entity_name": r.target_entity.physical_name,
                    "target_field_name": r.target_field.physical_name,
                    "cardinality": r.cardinality
                }
                for r in db_rels if r.source_entity and r.source_field and r.target_entity and r.target_field
            ]
        except Exception as rel_err:
            print(f"Failed to fetch relationships for propagation: {rel_err}")

        # Propagate metadata schema discovery to metadata service EAV
        try:
            import httpx
            payload = {
                "datasource_id": source_id,
                "datasource_name": db_source.name,
                "entities": [
                    {
                        "entity_name": ent["physical_name"],
                        "description": ent.get("description"),
                        "fields": [
                            {
                                "field_name": fld["physical_name"],
                                "data_type": fld.get("data_type", "string"),
                                "is_nullable": fld.get("is_nullable", True),
                                "is_primary_key": fld.get("is_primary_key", False),
                                "description": fld.get("description")
                            }
                            for fld in ent.get("fields", [])
                        ]
                    }
                    for ent in discovered_schema
                ],
                "relationships": relationships
            }
            async with httpx.AsyncClient() as client:
                await client.post("http://localhost:8002/api/v1/metadata/federation/sync", json=payload, timeout=10.0)
        except Exception as sync_err:
            print(f"Failed to propagate metadata: {sync_err}")

        # Log success
        sync_log = repo.log_sync_history(
            db, source_id, status="SUCCESS", records=synced_count, started_at=start_time
        )
        return sync_log
        
    except Exception as e:
        # Log failure
        sync_log = repo.log_sync_history(
            db, source_id, status="FAILED", error=str(e), started_at=start_time
        )
        return sync_log


@router.get("/sources/{source_id}/entities", response_model=List[EntityResponse])
def get_discovered_entities(source_id: int, db: Session = Depends(get_db)):
    """Returns all discovered entities (tables/endpoints) and fields for a data source."""
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return db_source.entities


@router.get("/sources/{source_id}/preview/{entity_name:path}")
async def preview_entity_data(source_id: int, entity_name: str, limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """Retrieves preview data rows for a discovered entity."""
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    try:
        credentials = repo.get_decrypted_credentials(db, source_id)
        add_params = json.loads(db_source.config.additional_params) if db_source.config.additional_params else {}
        
        connector_class = ConnectorRegistry.get_connector(db_source.connector_type)
        connector = connector_class(credentials, add_params)
        
        columns, rows = await connector.preview_data(entity_name, limit)
        return {"columns": columns, "rows": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview data: {str(e)}")


@router.post("/sources/{source_id}/query", response_model=QueryExecutionResponse)
async def query_entity_data(source_id: int, request: QueryExecutionRequest, db: Session = Depends(get_db)):
    """Executes a structured query containing filters, projections, and limits."""
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
        
    t_start = datetime.now()
    try:
        credentials = repo.get_decrypted_credentials(db, source_id)
        add_params = json.loads(db_source.config.additional_params) if db_source.config.additional_params else {}
        
        connector_class = ConnectorRegistry.get_connector(db_source.connector_type)
        connector = connector_class(credentials, add_params)
        
        # Translate and execute the relational query dictionary
        columns, rows = await connector.execute_query(request.model_dump())
        execution_time_ms = (datetime.now() - t_start).total_seconds() * 1000
        
        return QueryExecutionResponse(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time_ms=execution_time_ms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute query: {str(e)}")


@router.get("/sources/{source_id}/sync/history", response_model=List[SyncHistoryResponse])
def get_sync_audit_logs(source_id: int, db: Session = Depends(get_db)):
    """Returns schema synchronization history logs for a source."""
    return repo.get_sync_history(db, source_id)


# Relationships endpoints
@router.post("/sources/{source_id}/relationships", response_model=RelationshipResponse)
def create_source_relationship(source_id: int, obj_in: RelationshipCreate, db: Session = Depends(get_db)):
    """Registers a new logical relationship link between two discovered entities."""
    return repo.create_relationship(db, source_id, obj_in)


@router.get("/sources/{source_id}/relationships", response_model=List[RelationshipResponse])
def list_source_relationships(source_id: int, db: Session = Depends(get_db)):
    """Lists all registered relationships for a data source."""
    return repo.get_relationships(db, source_id)


@router.delete("/sources/{source_id}/relationships/{rel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source_relationship(source_id: int, rel_id: int, db: Session = Depends(get_db)):
    """Deletes a relationship link."""
    success = repo.delete_relationship(db, rel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return None


@router.get("/internal/sources/{source_id}/connection-info")
def get_internal_source_connection_info(source_id: int, db: Session = Depends(get_db)):
    """Internal endpoint for other microservices (like Query Service) to fetch connection config & credentials."""
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    try:
        credentials = repo.get_decrypted_credentials(db, source_id)
        add_params = json.loads(db_source.config.additional_params) if (db_source.config and db_source.config.additional_params) else {}
        return {
            "id": db_source.id,
            "name": db_source.name,
            "connector_type": db_source.connector_type,
            "credentials": credentials,
            "additional_params": add_params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/{source_id}/sync-incremental/{entity_name}")
async def sync_incremental_data(source_id: int, entity_name: str, db: Session = Depends(get_db)):
    """Triggers an incremental Change Data Capture (CDC) sync for a specific entity."""
    db_source = repo.get_data_source(db, source_id)
    if not db_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    try:
        credentials = repo.get_decrypted_credentials(db, source_id)
        add_params = json.loads(db_source.config.additional_params) if (db_source.config and db_source.config.additional_params) else {}
        
        connector_class = ConnectorRegistry.get_connector(db_source.connector_type)
        connector = connector_class(credentials, add_params)
        
        if not hasattr(connector, "incremental_sync"):
            raise HTTPException(status_code=400, detail="Incremental sync is only supported on enterprise connectors")
            
        res = await connector.incremental_sync(db, source_id, entity_name)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Incremental sync failed: {str(e)}")


@router.get("/sources/{source_id}/sync-checkpoints")
def get_sync_checkpoints(source_id: int, db: Session = Depends(get_db)):
    """Retrieves all stored Change Data Capture (CDC) checkpoints for a source."""
    from app.models.connector import SyncCheckpoint
    checkpoints = db.query(SyncCheckpoint).filter(SyncCheckpoint.data_source_id == source_id).all()
    return [
        {
            "id": c.id,
            "entity_name": c.entity_name,
            "last_sync_timestamp": c.last_sync_timestamp.isoformat(),
            "cursor_value": c.cursor_value,
            "sync_status": c.sync_status
        }
        for c in checkpoints
    ]


