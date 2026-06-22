from typing import Dict, Any, List, Tuple
from app.connectors.enterprise.base_enterprise import BaseEnterpriseConnector
from app.connectors.enterprise.clients.assay_clients import BioAssayClient, ScreeningClient, HtsClient

class AssayConnector(BaseEnterpriseConnector):
    """
    Assay Database connector framework.
    Maps bioactivity and assay results databases into a standard platform-agnostic schema.
    """

    def _get_client(self):
        vendor = self.additional_params.get("vendor", "bioassay").lower()
        if vendor == "screening":
            return ScreeningClient(self.credentials, self.additional_params)
        elif vendor == "hts":
            return HtsClient(self.credentials, self.additional_params)
        else:
            return BioAssayClient(self.credentials, self.additional_params)

    async def test_connection(self) -> Tuple[bool, str]:
        client = self._get_client()
        success, msg = await client.test_connection()
        vendor_name = self.additional_params.get("vendor", "BioAssay").upper()
        return success, f"ASSAY {vendor_name}: {msg}"

    async def discover_schema(self) -> List[Dict[str, Any]]:
        client = self._get_client()
        return await client.discover_metadata()

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        entity = query["entity"]
        fields = query["fields"]
        limit = query.get("limit", 10)
        
        client = self._get_client()
        raw_items = []
        if entity == "assays":
            raw_items = await client.fetch_assays()
        elif entity == "results":
            raw_items = await client.fetch_results()
        elif entity == "plates" and hasattr(client, "fetch_plates"):
            raw_items = await client.fetch_plates()
            
        # Map objects to dynamic matrix rows based on schema
        schema = await self.discover_schema()
        entity_fields = next((ent["fields"] for ent in schema if ent["physical_name"] == entity), [])
        
        rows = []
        for item in raw_items[:limit]:
            row = []
            for f in fields:
                row.append(item.get(f))
            rows.append(row)
            
        return fields, rows

    async def preview_data(self, entity_name: str, limit: int = 10) -> Tuple[List[str], List[List[Any]]]:
        schema = await self.discover_schema()
        fields = [f["physical_name"] for f in next(ent["fields"] for ent in schema if ent["physical_name"] == entity_name)]
        return await self.execute_query({
            "entity": entity_name,
            "fields": fields,
            "limit": limit
        })

    async def sync_entities(self, db, source_id: int) -> int:
        client = self._get_client()
        return await client.sync_entities(db, source_id)

    async def incremental_sync(self, db, source_id: int, entity_name: str) -> Dict[str, Any]:
        client = self._get_client()
        return await client.incremental_sync(db, source_id, entity_name)

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "assay",
            "name": "Assay Database",
            "description": "Unified virtual connector mapping bioactivity screening systems (e.g. CDD Vault, ActivityBase, HTS)",
            "required_credentials": ["api_url", "auth_token"],
            "supported_operations": ["filter", "limit"]
        }
