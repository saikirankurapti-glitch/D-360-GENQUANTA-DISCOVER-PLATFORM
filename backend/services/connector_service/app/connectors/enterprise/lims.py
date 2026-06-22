from typing import Dict, Any, List, Tuple
from app.connectors.enterprise.base_enterprise import BaseEnterpriseConnector
from app.connectors.enterprise.clients.lims_clients import LabVantageClient, LabWareClient, StarlimsClient

class LIMSConnector(BaseEnterpriseConnector):
    """
    Laboratory Information Management System (LIMS) connector framework.
    Exposes unified virtual schemas for LabWare, LabVantage, and STARLIMS.
    """

    def _get_client(self):
        vendor = self.additional_params.get("vendor", "labvantage").lower()
        if vendor == "labware":
            return LabWareClient(self.credentials, self.additional_params)
        elif vendor == "starlims":
            return StarlimsClient(self.credentials, self.additional_params)
        else:
            return LabVantageClient(self.credentials, self.additional_params)

    async def test_connection(self) -> Tuple[bool, str]:
        client = self._get_client()
        success, msg = await client.test_connection()
        vendor_name = self.additional_params.get("vendor", "LabVantage").capitalize()
        return success, f"LIMS {vendor_name}: {msg}"

    async def discover_schema(self) -> List[Dict[str, Any]]:
        client = self._get_client()
        return await client.discover_metadata()

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        entity = query["entity"]
        fields = query["fields"]
        limit = query.get("limit", 10)
        
        client = self._get_client()
        raw_items = []
        if entity == "samples":
            raw_items = await client.fetch_samples()
        elif entity == "tests":
            raw_items = await client.fetch_tests()
            
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
            "connector_type": "lims",
            "name": "LIMS (Lab Information Management System)",
            "description": "Federated connector for LabWare, LabVantage, and STARLIMS",
            "required_credentials": ["api_url", "auth_token"],
            "supported_operations": ["filter", "limit"]
        }
