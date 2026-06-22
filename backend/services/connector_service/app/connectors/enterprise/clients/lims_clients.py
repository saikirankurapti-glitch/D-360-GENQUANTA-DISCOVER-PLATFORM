import httpx
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
from app.connectors.enterprise.base_adapter import BaseEnterpriseAdapter
from app.connectors.enterprise.unified_model import Sample

logger = logging.getLogger("connector_service.lims_clients")

class BaseLIMSClient(BaseEnterpriseAdapter):
    """Base client for Laboratory Information Management System interfaces."""
    async def discover_metadata(self) -> List[Dict[str, Any]]:
        return [
            {
                "physical_name": "samples",
                "display_name": "Samples",
                "description": "Biological and chemical samples registered in LIMS",
                "fields": [
                    {"physical_name": "sample_id", "display_name": "Sample ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "batch_id", "display_name": "Batch ID", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "sample_type", "display_name": "Sample Type", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "status", "display_name": "Status", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "amount_value", "display_name": "Amount", "data_type": "float", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "amount_unit", "display_name": "Unit", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "location", "display_name": "Storage Location", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                ]
            },
            {
                "physical_name": "tests",
                "display_name": "Tests",
                "description": "Analytical tests assigned or completed on samples",
                "fields": [
                    {"physical_name": "test_id", "display_name": "Test ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "sample_id", "display_name": "Sample ID", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "test_type", "display_name": "Test Type", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "assigned_operator", "display_name": "Operator", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "completion_date", "display_name": "Completion Date", "data_type": "date", "is_nullable": True, "is_primary_key": False}
                ]
            }
        ]

class LabVantageClient(BaseLIMSClient):
    """
    Production LabVantage REST API integration.
    Queries the LabVantage Web Services API.
    """
    async def fetch_samples(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"sample_id": "SMP-LV-001", "batch_id": "BAT-90123", "sample_type": "Blood Serum", "status": "Logged", "amount_value": 5.0, "amount_unit": "mL", "location": "Freezer-A, Shelf-1", "created_at": "2026-05-01T00:00:00Z"},
                {"sample_id": "SMP-LV-002", "batch_id": "BAT-90123", "sample_type": "Blood Serum", "status": "Approved", "amount_value": 4.2, "amount_unit": "mL", "location": "Freezer-A, Shelf-1", "created_at": "2026-05-02T00:00:00Z"},
                {"sample_id": "SMP-LV-003", "batch_id": "BAT-90124", "sample_type": "Tissue Lysate", "status": "Completed", "amount_value": 10.0, "amount_unit": "mg", "location": "Freezer-B, Shelf-4", "created_at": "2026-05-10T00:00:00Z"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/samples", headers=headers, timeout=10.0)
            resp.raise_for_status()
            samples = resp.json().get("samples", [])
            return [
                Sample(
                    sample_id=str(s.get("sampleId") or s.get("id")),
                    batch_id=s.get("batchId"),
                    sample_type=s.get("type") or s.get("sampleType") or "Unknown",
                    status=s.get("status") or "Logged",
                    amount_value=s.get("amount"),
                    amount_unit=s.get("unit"),
                    location=s.get("location"),
                    created_at=s.get("createdDate") or s.get("createdAt")
                ).model_dump()
                for s in samples
            ]

    async def fetch_tests(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"test_id": "TST-LV-101", "sample_id": "SMP-LV-001", "test_type": "HPLC Purity", "assigned_operator": "Dr. Sarah Conner", "completion_date": "2026-05-10T00:00:00Z"},
                {"test_id": "TST-LV-102", "sample_id": "SMP-LV-002", "test_type": "Mass Spectrometry", "assigned_operator": "Dr. John Connor", "completion_date": "2026-05-11T00:00:00Z"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/tests", headers=headers, timeout=10.0)
            resp.raise_for_status()
            return resp.json().get("tests", [])

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            return {
                "created": [{"sample_id": "SMP-LV-004", "batch_id": "BAT-90124", "sample_type": "Plasma", "status": "Logged", "amount_value": 2.0, "amount_unit": "mL", "location": "Freezer-B, Shelf-4", "created_at": datetime.utcnow().isoformat()}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "samples":
                resp = await client.get(f"{self.api_url}/samples?since={since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                samples = resp.json().get("samples", [])
                mapped = [
                    Sample(
                        sample_id=str(s.get("sampleId") or s.get("id")),
                        batch_id=s.get("batchId"),
                        sample_type=s.get("type") or s.get("sampleType") or "Unknown",
                        status=s.get("status") or "Logged",
                        amount_value=s.get("amount"),
                        amount_unit=s.get("unit"),
                        location=s.get("location"),
                        created_at=s.get("createdDate") or s.get("createdAt")
                    ).model_dump()
                    for s in samples
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "samples":
            return await self.fetch_samples()
        elif entity_name == "tests":
            return await self.fetch_tests()
        return []


class LabWareClient(BaseLIMSClient):
    """
    Production LabWare Web LIMS API integration.
    Connects to LabWare Web Services or LabWare API.
    """
    async def fetch_samples(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"sample_id": "SMP-LW-801", "batch_id": "BAT-11002", "sample_type": "HEK293 Lysate", "status": "In Progress", "amount_value": 2.5, "amount_unit": "mL", "location": "Liquid Nitrogen Tank 1", "created_at": "2026-04-12T00:00:00Z"},
                {"sample_id": "SMP-LW-802", "batch_id": "BAT-11003", "sample_type": "CHO Cell Pellet", "status": "Logged", "amount_value": 1.0, "amount_unit": "g", "location": "Freezer-C, Shelf-2", "created_at": "2026-04-15T00:00:00Z"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/api/samples", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            return [
                Sample(
                    sample_id=str(s.get("sampleNumber") or s.get("id")),
                    batch_id=s.get("batch"),
                    sample_type=s.get("sampleTemplate") or s.get("type") or "HEK293",
                    status=s.get("status") or "Logged",
                    amount_value=s.get("amount"),
                    amount_unit=s.get("unit"),
                    location=s.get("location"),
                    created_at=s.get("created")
                ).model_dump()
                for s in data
            ]

    async def fetch_tests(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"test_id": "TST-LW-501", "sample_id": "SMP-LW-801", "test_type": "Western Blot", "assigned_operator": "Alice Vance", "completion_date": "2026-04-20T00:00:00Z"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/api/tests", headers=headers, timeout=10.0)
            resp.raise_for_status()
            return resp.json().get("data", [])

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            return {
                "created": [{"sample_id": "SMP-LW-803", "batch_id": "BAT-11003", "sample_type": "CHO Cell Pellet", "status": "Logged", "amount_value": 0.5, "amount_unit": "g", "location": "Freezer-C, Shelf-2", "created_at": datetime.utcnow().isoformat()}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "samples":
                resp = await client.get(f"{self.api_url}/api/samples?modifiedSince={since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                data = resp.json().get("data", [])
                mapped = [
                    Sample(
                        sample_id=str(s.get("sampleNumber") or s.get("id")),
                        batch_id=s.get("batch"),
                        sample_type=s.get("sampleTemplate") or s.get("type") or "HEK293",
                        status=s.get("status") or "Logged",
                        amount_value=s.get("amount"),
                        amount_unit=s.get("unit"),
                        location=s.get("location"),
                        created_at=s.get("created")
                    ).model_dump()
                    for s in data
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "samples":
            return await self.fetch_samples()
        elif entity_name == "tests":
            return await self.fetch_tests()
        return []


class StarlimsClient(BaseLIMSClient):
    """
    Production STARLIMS REST API integration.
    Interfaces with STARLIMS REST Service endpoints.
    """
    async def fetch_samples(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"sample_id": "SMP-SL-301", "batch_id": "BAT-5509", "sample_type": "Plasma", "status": "Approved", "amount_value": 3.0, "amount_unit": "mL", "location": "STAR-Rack-4", "created_at": "2026-05-18T00:00:00Z"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/starlims/samples", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("samples", [])
            return [
                Sample(
                    sample_id=str(s.get("sampleKey") or s.get("id")),
                    batch_id=s.get("batchNo"),
                    sample_type=s.get("template") or s.get("type") or "Plasma",
                    status=s.get("status") or "Approved",
                    amount_value=s.get("qty"),
                    amount_unit=s.get("unit"),
                    location=s.get("storageLoc"),
                    created_at=s.get("loggedTime")
                ).model_dump()
                for s in data
            ]

    async def fetch_tests(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"test_id": "TST-SL-301", "sample_id": "SMP-SL-301", "test_type": "Enzymatic Influx", "assigned_operator": "Bob Marley", "completion_date": "2026-05-19T00:00:00Z"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/starlims/tests", headers=headers, timeout=10.0)
            resp.raise_for_status()
            return resp.json().get("tests", [])

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            return {
                "created": [{"sample_id": "SMP-SL-302", "batch_id": "BAT-5509", "sample_type": "Plasma", "status": "Approved", "amount_value": 1.0, "amount_unit": "mL", "location": "STAR-Rack-4", "created_at": datetime.utcnow().isoformat()}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "samples":
                resp = await client.get(f"{self.api_url}/starlims/samples?changedSince={since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                data = resp.json().get("samples", [])
                mapped = [
                    Sample(
                        sample_id=str(s.get("sampleKey") or s.get("id")),
                        batch_id=s.get("batchNo"),
                        sample_type=s.get("template") or s.get("type") or "Plasma",
                        status=s.get("status") or "Approved",
                        amount_value=s.get("qty"),
                        amount_unit=s.get("unit"),
                        location=s.get("storageLoc"),
                        created_at=s.get("loggedTime")
                    ).model_dump()
                    for s in data
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "samples":
            return await self.fetch_samples()
        elif entity_name == "tests":
            return await self.fetch_tests()
        return []
