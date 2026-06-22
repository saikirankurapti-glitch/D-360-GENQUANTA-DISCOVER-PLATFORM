from typing import Dict, Any, List, Tuple
from app.connectors.enterprise.base_enterprise import BaseEnterpriseConnector

class InventoryConnector(BaseEnterpriseConnector):
    """
    Inventory System connector framework.
    Exposes unified virtual models for tracking scientific items, vials, plates, and physical storage.
    """

    async def discover_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "physical_name": "containers",
                "display_name": "Containers",
                "description": "Vials, tubes, and bottles in laboratory inventory",
                "fields": [
                    {"physical_name": "barcode", "display_name": "Barcode", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "compound_key", "display_name": "Compound Key", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "container_type", "display_name": "Type", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "room", "display_name": "Room", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "shelf", "display_name": "Shelf", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "current_mass_mg", "display_name": "Mass (mg)", "data_type": "float", "is_nullable": True, "is_primary_key": False}
                ]
            },
            {
                "physical_name": "plates",
                "display_name": "Plates",
                "description": "96 or 384-well plates used for compound screening assays",
                "fields": [
                    {"physical_name": "plate_id", "display_name": "Plate ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "name", "display_name": "Plate Name", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "format", "display_name": "Format", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "fridge_location", "display_name": "Fridge Location", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                ]
            }
        ]

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        entity = query["entity"]
        fields = query["fields"]
        limit = query.get("limit", 10)
        
        mock_data = {
            "containers": [
                ["BAR-202611", "GQ-00481", "1D Vial", "Room 402", "Shelf A", 12.5],
                ["BAR-202612", "GQ-00481", "1D Vial", "Room 402", "Shelf A", 8.4],
                ["BAR-202613", "GQ-00482", "2D Tube", "Room 101", "Freezer B", 50.0]
            ],
            "plates": [
                ["PLT-9920", "Screening Plate 1 - Oncology", "96-well", "Freezer A, Shelf 1"],
                ["PLT-9921", "Screening Plate 2 - GPCR", "384-well", "Freezer A, Shelf 2"]
            ]
        }
        
        raw_rows = mock_data.get(entity, [])
        schema = await self.discover_schema()
        entity_fields = next(ent["fields"] for ent in schema if ent["physical_name"] == entity)
        field_indices = {f["physical_name"]: idx for idx, f in enumerate(entity_fields)}
        
        rows = []
        for r in raw_rows[:limit]:
            row = []
            for f in fields:
                idx = field_indices.get(f)
                row.append(r[idx] if idx is not None else None)
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

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "connector_type": "inventory",
            "name": "Inventory System",
            "description": "Enterprise connector integrating warehouse and laboratory sample inventories (e.g. Mosaic, LabCup)",
            "required_credentials": ["api_url", "auth_token"],
            "supported_operations": ["filter", "limit"]
        }
