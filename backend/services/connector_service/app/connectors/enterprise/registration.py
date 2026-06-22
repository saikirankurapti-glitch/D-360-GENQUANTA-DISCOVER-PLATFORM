from typing import Dict, Any, List, Tuple
from app.connectors.enterprise.base_enterprise import BaseEnterpriseConnector

class CompoundRegistrationConnector(BaseEnterpriseConnector):
    """
    Compound Registration system connector framework.
    Adapts ChemAxon Registry, Dotmatics Register, or custom databases into standard compound/batch objects.
    """

    async def discover_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "physical_name": "compounds",
                "display_name": "Registered Compounds",
                "description": "Unique corporate registry structures",
                "fields": [
                    {"physical_name": "registry_number", "display_name": "Reg No", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "smiles", "display_name": "SMILES", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "iupac_name", "display_name": "IUPAC Name", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "molecular_weight", "display_name": "Mol Weight", "data_type": "float", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "registrant", "display_name": "Registrant", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                ]
            },
            {
                "physical_name": "batches",
                "display_name": "Structure Batches",
                "description": "Sub-lots and batches of registered chemicals",
                "fields": [
                    {"physical_name": "batch_id", "display_name": "Batch ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "registry_number", "display_name": "Reg No", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "purity", "display_name": "Purity (%)", "data_type": "float", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "salt_form", "display_name": "Salt Form", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                ]
            }
        ]

    async def execute_query(self, query: Dict[str, Any]) -> Tuple[List[str], List[List[Any]]]:
        entity = query["entity"]
        fields = query["fields"]
        limit = query.get("limit", 10)
        
        mock_data = {
            "compounds": [
                ["GQ-00481", "CC(=O)Oc1ccccc1C(=O)O", "2-(acetyloxy)benzoic acid", 180.16, "Dr. Alice"],
                ["GQ-00482", "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "1,3,7-Trimethylpurine-2,6-dione", 194.19, "Dr. Alice"]
            ],
            "batches": [
                ["GQ-00481-A", "GQ-00481", 98.5, "Free Acid"],
                ["GQ-00481-B", "GQ-00481", 99.2, "Sodium Salt"],
                ["GQ-00482-A", "GQ-00482", 99.8, "Free Base"]
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
            "connector_type": "registration",
            "name": "Compound Registration System",
            "description": "Enterprise connector integrating chemical registration software",
            "required_credentials": ["api_url", "auth_token"],
            "supported_operations": ["filter", "limit"]
        }
