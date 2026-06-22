import httpx
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from app.repositories.connector_repository import repo
from sqlalchemy.orm import Session

logger = logging.getLogger("connector_service.base_adapter")

class BaseEnterpriseAdapter:
    """
    Unified abstract base class for enterprise integrations (Benchling, LabWare, etc.)
    Handles API Keys, OAuth2 Token Refresh, Metadata Discovery, and CDC delta tracking.
    """
    def __init__(self, credentials: Dict[str, Any], additional_params: Dict[str, Any] = None):
        self.credentials = credentials
        self.additional_params = additional_params or {}
        self.api_url = credentials.get("api_url", "").rstrip("/")
        self.use_simulator = credentials.get("use_simulator", True)
        self.access_token = credentials.get("auth_token") or credentials.get("api_key")
        self.refresh_token = credentials.get("refresh_token")
        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret")

    async def get_headers(self) -> Dict[str, str]:
        """Prepares request headers with valid authentication tokens."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        # Handshake OAuth2 client credentials or active token
        await self.authenticate()
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
            headers["X-API-Key"] = self.access_token
        return headers

    async def authenticate(self) -> None:
        """Exchanges API Keys or client credentials for access tokens if expired or needed."""
        if self.use_simulator:
            return

        if self.client_id and self.client_secret and not self.access_token:
            # Execute OAuth2 grant flow
            token_url = self.credentials.get("token_url", f"{self.api_url}/oauth/token")
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(token_url, data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }, timeout=10.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        self.access_token = data.get("access_token")
                        self.refresh_token = data.get("refresh_token")
                        logger.info("Successfully authenticated via OAuth2 Client Credentials.")
                    else:
                        logger.error(f"OAuth2 authentication failed with status: {resp.status_code}")
            except Exception as e:
                logger.error(f"Auth error occurred during HTTP handshake: {str(e)}")

    async def test_connection(self) -> Tuple[bool, str]:
        """Pings vendor status endpoint to verify network availability and auth configuration."""
        if self.use_simulator:
            return True, "Simulator: connection test passed."

        try:
            headers = await self.get_headers()
            async with httpx.AsyncClient() as client:
                ping_endpoint = self.additional_params.get("ping_endpoint", f"{self.api_url}/health")
                resp = await client.get(ping_endpoint, headers=headers, timeout=5.0)
                if resp.status_code in [200, 201]:
                    return True, "Connection established successfully."
                return False, f"Server responded with status code: {resp.status_code}"
        except Exception as e:
            return False, f"HTTP Connection failed: {str(e)}"

    async def discover_metadata(self) -> List[Dict[str, Any]]:
        """Auto-discovers schemas, fields, types, and primary keys from vendor."""
        raise NotImplementedError("Subclasses must implement discover_metadata")

    async def sync_entities(self, db: Session, source_id: int) -> int:
        """Pushes auto-discovered metadata configurations directly into EAV Metadata Catalog."""
        discovered_schema = await self.discover_metadata()
        
        # Save to connector database
        synced_count = repo.refresh_entities_metadata(db, source_id, discovered_schema)
        
        # Federate schemas to Metadata Service
        try:
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
            except Exception:
                pass

            payload = {
                "datasource_id": source_id,
                "datasource_name": f"Enterprise-{source_id}",
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
            logger.warning(f"Failed to federate metadata schema: {str(sync_err)}")

        return synced_count

    async def incremental_sync(self, db: Session, source_id: int, entity_name: str) -> Dict[str, Any]:
        """
        Executes Change Data Capture (CDC) based on SyncCheckpoint cursor value.
        Identifies created, updated, and deleted rows relative to last sync run.
        """
        checkpoint = repo.get_sync_checkpoint(db, source_id, entity_name)
        since_timestamp = "1970-01-01T00:00:00Z"
        if checkpoint and checkpoint.sync_status == "SUCCESS":
            since_timestamp = checkpoint.last_sync_timestamp.isoformat() + "Z"

        try:
            changes = await self.get_changes(entity_name, since_timestamp)
            
            # Save new sync timestamp checkpoint
            repo.save_sync_checkpoint(
                db, 
                source_id=source_id, 
                entity_name=entity_name, 
                cursor_value=datetime.utcnow().isoformat(), 
                status="SUCCESS"
            )
            return {
                "entity": entity_name,
                "synced_at": datetime.utcnow().isoformat(),
                "created": len(changes.get("created", [])),
                "updated": len(changes.get("updated", [])),
                "deleted": len(changes.get("deleted", [])),
                "records": changes
            }
        except Exception as e:
            repo.save_sync_checkpoint(
                db, 
                source_id=source_id, 
                entity_name=entity_name, 
                cursor_value=since_timestamp, 
                status="FAILED"
            )
            raise e

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        """Queries vendor endpoint for entity delta changes (created/updated/deleted)."""
        raise NotImplementedError("Subclasses must implement get_changes")

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Queries vendor REST endpoint to read objects using standard limit/offset paging."""
        raise NotImplementedError("Subclasses must implement fetch_records")
