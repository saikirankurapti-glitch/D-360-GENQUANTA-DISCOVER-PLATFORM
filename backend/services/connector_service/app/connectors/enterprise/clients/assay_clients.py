import httpx
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
from app.connectors.enterprise.base_adapter import BaseEnterpriseAdapter
from app.connectors.enterprise.unified_model import Assay, Result, Plate

logger = logging.getLogger("connector_service.assay_clients")

class BaseAssayClient(BaseEnterpriseAdapter):
    """Base client for Assay database interfaces."""
    async def discover_metadata(self) -> List[Dict[str, Any]]:
        entities = [
            {
                "physical_name": "assays",
                "display_name": "Assays",
                "description": "Biological and chemical screening assays definition",
                "fields": [
                    {"physical_name": "assay_id", "display_name": "Assay ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "name", "display_name": "Assay Name", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "target", "display_name": "Target biological entity", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "assay_type", "display_name": "Assay Type", "data_type": "string", "is_nullable": False, "is_primary_key": False}
                ]
            },
            {
                "physical_name": "results",
                "display_name": "Assay Results",
                "description": "Individual dose-response or single point screening results",
                "fields": [
                    {"physical_name": "result_id", "display_name": "Result ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "assay_id", "display_name": "Assay ID", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "compound_key", "display_name": "Compound Key", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "activity_value", "display_name": "Activity Value", "data_type": "float", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "activity_unit", "display_name": "Unit", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "outcome", "display_name": "Outcome", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                ]
            }
        ]
        if isinstance(self, HtsClient):
            entities.append({
                "physical_name": "plates",
                "display_name": "Plates",
                "description": "Assay microplate layout tracking",
                "fields": [
                    {"physical_name": "plate_id", "display_name": "Plate ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "barcode", "display_name": "Barcode", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "plate_format", "display_name": "Plate Format", "data_type": "integer", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "status", "display_name": "Status", "data_type": "string", "is_nullable": False, "is_primary_key": False}
                ]
            })
        return entities

class BioAssayClient(BaseAssayClient):
    """
    Production BioAssay integration client.
    Interfaces with standardized bioactivity and cell assay databases (e.g. CDD Vault, ActivityBase).
    """
    async def fetch_assays(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"assay_id": "ASY-BA-01", "name": "SARS-CoV-2 Main Protease Inhibitors", "target": "Mpro", "assay_type": "Enzymatic Activity"},
                {"assay_id": "ASY-BA-02", "name": "HERG Potassium Channel Cardiotoxicity", "target": "hERG Channel", "assay_type": "Electrophysiology Patch-Clamp"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/assays", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("assays", [])
            return [
                Assay(
                    assay_id=str(a.get("id")),
                    name=a.get("name"),
                    target=a.get("targetName") or a.get("target"),
                    assay_type=a.get("type") or a.get("assay_type") or "In Vitro"
                ).model_dump()
                for a in data
            ]

    async def fetch_results(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"result_id": "RES-BA-501", "assay_id": "ASY-BA-01", "compound_key": "CHEM-000492", "activity_value": 1.25, "activity_unit": "uM", "outcome": "Active"},
                {"result_id": "RES-BA-502", "assay_id": "ASY-BA-01", "compound_key": "CHEM-000493", "activity_value": 25.4, "activity_unit": "uM", "outcome": "Inactive"},
                {"result_id": "RES-BA-503", "assay_id": "ASY-BA-02", "compound_key": "CHEM-000492", "activity_value": 82.1, "activity_unit": "uM", "outcome": "Safe"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/results", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("results", [])
            return [
                Result(
                    result_id=str(r.get("id")),
                    assay_id=str(r.get("assayId")),
                    compound_key=r.get("compoundId") or r.get("compound_key"),
                    activity_value=r.get("value") or r.get("activity_value"),
                    activity_unit=r.get("unit") or r.get("activity_unit"),
                    outcome=r.get("outcome")
                ).model_dump()
                for r in data
            ]

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            return {
                "created": [{"result_id": "RES-BA-504", "assay_id": "ASY-BA-01", "compound_key": "CHEM-000494", "activity_value": 0.45, "activity_unit": "uM", "outcome": "Active"}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "results":
                resp = await client.get(f"{self.api_url}/results?since={since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                data = resp.json().get("results", [])
                mapped = [
                    Result(
                        result_id=str(r.get("id")),
                        assay_id=str(r.get("assayId")),
                        compound_key=r.get("compoundId") or r.get("compound_key"),
                        activity_value=r.get("value") or r.get("activity_value"),
                        activity_unit=r.get("unit") or r.get("activity_unit"),
                        outcome=r.get("outcome")
                    ).model_dump()
                    for r in data
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "assays":
            return await self.fetch_assays()
        elif entity_name == "results":
            return await self.fetch_results()
        return []


class ScreeningClient(BaseAssayClient):
    """
    Production Screening Database integration client.
    """
    async def fetch_assays(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"assay_id": "ASY-SCR-10", "name": "EGFR Kinase Cascade Assay", "target": "EGFR", "assay_type": "Luminescence"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/screening/assays", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            return [
                Assay(
                    assay_id=str(a.get("id")),
                    name=a.get("name"),
                    target=a.get("target"),
                    assay_type=a.get("type") or "Screening"
                ).model_dump()
                for a in data
            ]

    async def fetch_results(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"result_id": "RES-SCR-101", "assay_id": "ASY-SCR-10", "compound_key": "CHEM-000493", "activity_value": 0.08, "activity_unit": "uM", "outcome": "Active"},
                {"result_id": "RES-SCR-102", "assay_id": "ASY-SCR-10", "compound_key": "CHEM-000494", "activity_value": 4.10, "activity_unit": "uM", "outcome": "Inactive"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/screening/results", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            return [
                Result(
                    result_id=str(r.get("id")),
                    assay_id=str(r.get("assayId")),
                    compound_key=r.get("compoundId"),
                    activity_value=r.get("value"),
                    activity_unit=r.get("unit"),
                    outcome=r.get("outcome")
                ).model_dump()
                for r in data
            ]

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            return {
                "created": [{"result_id": "RES-SCR-103", "assay_id": "ASY-SCR-10", "compound_key": "CHEM-000495", "activity_value": 10.5, "activity_unit": "uM", "outcome": "Inactive"}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "results":
                resp = await client.get(f"{self.api_url}/screening/results?since={since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                data = resp.json().get("data", [])
                mapped = [
                    Result(
                        result_id=str(r.get("id")),
                        assay_id=str(r.get("assayId")),
                        compound_key=r.get("compoundId"),
                        activity_value=r.get("value"),
                        activity_unit=r.get("unit"),
                        outcome=r.get("outcome")
                    ).model_dump()
                    for r in data
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "assays":
            return await self.fetch_assays()
        elif entity_name == "results":
            return await self.fetch_results()
        return []


class HtsClient(BaseAssayClient):
    """
    Production High-Throughput Screening (HTS) client.
    Includes plate format/layout tracking.
    """
    async def fetch_assays(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"assay_id": "ASY-HTS-300", "name": "Primary GPCR 384-well Screening", "target": "GPCR-D2", "assay_type": "Fluorescence Influx"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/hts/assays", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("assays", [])
            return [
                Assay(
                    assay_id=str(a.get("id")),
                    name=a.get("name"),
                    target=a.get("target"),
                    assay_type=a.get("type") or "HTS"
                ).model_dump()
                for a in data
            ]

    async def fetch_results(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"result_id": "RES-HTS-1209", "assay_id": "ASY-HTS-300", "compound_key": "CHEM-000495", "activity_value": 78.4, "activity_unit": "% Inhibition", "outcome": "Active"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/hts/results", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("results", [])
            return [
                Result(
                    result_id=str(r.get("id")),
                    assay_id=str(r.get("assayId")),
                    compound_key=r.get("compoundId"),
                    activity_value=r.get("value"),
                    activity_unit=r.get("unit"),
                    outcome=r.get("outcome")
                ).model_dump()
                for r in data
            ]

    async def fetch_plates(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"plate_id": "PLT-384-90", "barcode": "BARCODE90", "plate_format": 384, "status": "Screened"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/hts/plates", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("plates", [])
            return [
                Plate(
                    plate_id=str(p.get("id") or p.get("plateId")),
                    barcode=p.get("barcode"),
                    plate_format=p.get("format") or 384,
                    status=p.get("status")
                ).model_dump()
                for p in data
            ]

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            return {
                "created": [{"result_id": "RES-HTS-1210", "assay_id": "ASY-HTS-300", "compound_key": "CHEM-000496", "activity_value": 12.2, "activity_unit": "% Inhibition", "outcome": "Inactive"}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "results":
                resp = await client.get(f"{self.api_url}/hts/results?since={since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                data = resp.json().get("results", [])
                mapped = [
                    Result(
                        result_id=str(r.get("id")),
                        assay_id=str(r.get("assayId")),
                        compound_key=r.get("compoundId"),
                        activity_value=r.get("value"),
                        activity_unit=r.get("unit"),
                        outcome=r.get("outcome")
                    ).model_dump()
                    for r in data
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "assays":
            return await self.fetch_assays()
        elif entity_name == "results":
            return await self.fetch_results()
        elif entity_name == "plates":
            return await self.fetch_plates()
        return []
