import httpx
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
from app.connectors.enterprise.base_adapter import BaseEnterpriseAdapter
from app.connectors.enterprise.unified_model import Project, Experiment, Protocol, Notebook

logger = logging.getLogger("connector_service.eln_clients")

class BaseELNClient(BaseEnterpriseAdapter):
    """Base client for Electronic Lab Notebook interfaces."""
    async def discover_metadata(self) -> List[Dict[str, Any]]:
        entities = [
            {
                "physical_name": "experiments",
                "display_name": "Experiments",
                "description": "Notebook experiment records",
                "fields": [
                    {"physical_name": "experiment_id", "display_name": "Experiment ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "title", "display_name": "Title", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "project_id", "display_name": "Project ID", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "author", "display_name": "Author", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "created_at", "display_name": "Created Date", "data_type": "date", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "status", "display_name": "Status", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                ]
            },
            {
                "physical_name": "protocols",
                "display_name": "Protocols",
                "description": "Experimental Standard Operating Procedures",
                "fields": [
                    {"physical_name": "protocol_id", "display_name": "Protocol ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "name", "display_name": "Protocol Name", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "version", "display_name": "Version", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "description", "display_name": "Description", "data_type": "string", "is_nullable": True, "is_primary_key": False}
                ]
            }
        ]
        if isinstance(self, BenchlingClient):
            entities.insert(0, {
                "physical_name": "projects",
                "display_name": "Projects",
                "description": "Benchling research projects list",
                "fields": [
                    {"physical_name": "project_id", "display_name": "Project ID", "data_type": "string", "is_nullable": False, "is_primary_key": True},
                    {"physical_name": "name", "display_name": "Project Name", "data_type": "string", "is_nullable": False, "is_primary_key": False},
                    {"physical_name": "description", "display_name": "Description", "data_type": "string", "is_nullable": True, "is_primary_key": False},
                    {"physical_name": "created_at", "display_name": "Created At", "data_type": "date", "is_nullable": True, "is_primary_key": False}
                ]
            })
        return entities

class BenchlingClient(BaseELNClient):
    """
    Production Benchling REST API integration.
    Aligns with Benchling v2 / v3 endpoints for Projects, Entries, and Protocols.
    """
    async def fetch_projects(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            from datetime import timedelta
            projects = []
            project_names = [
                "Oncology Target Discovery", "Immunotherapy Screen", "ALK Resistant Mutation Study",
                "Cardiovascular Safety Screen", "GPCR Binding Profiling", "Neurodegenerative Pathway Study",
                "Antibody-Drug Conjugates development", "CRISPR-Cas9 Validation Screen", "Kinase Inhibitor Optimization",
                "Epigenetics Regulation Target Scan"
            ]
            for i in range(55):
                name = f"{project_names[i % len(project_names)]} Phase {i // len(project_names) + 1}"
                projects.append({
                    "project_id": f"proj_bench_{i+1}",
                    "name": name,
                    "description": f"Simulated Benchling project: {name}. Investigating key biological targets and therapeutic efficacy.",
                    "created_at": (datetime.now() - timedelta(days=200+i*5)).isoformat()
                })
            return projects

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/projects", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("projects", [])
            # Map to unified model
            return [
                Project(
                    project_id=p.get("id"),
                    name=p.get("name"),
                    description=p.get("description"),
                    created_at=p.get("createdAt")
                ).model_dump()
                for p in data
            ]

    async def fetch_experiments(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            from datetime import timedelta
            experiments = []
            authors = ["Dr. Sarah Connor", "Dr. John Connor", "Dr. Kyle Reese", "Dr. Miles Dyson", "Dr. Marcus Wright"]
            statuses = ["Completed", "In Progress", "Signed Off", "Draft", "Under Review"]
            experiment_types = [
                "Synthesis of Kinase Inhibitor", "Binding Assay for target", "In vitro ELISA Screen",
                "Cell Viability Assay of cancer line", "Flow Cytometry Sorting of T-cells", "Western Blot verification of protein expression",
                "Real-Time PCR target amplification", "Chromatography purification run"
            ]
            for i in range(550):
                proj_idx = (i % 55) + 1
                author = authors[i % len(authors)]
                status = statuses[i % len(statuses)]
                exp_type = experiment_types[i % len(experiment_types)]
                title = f"{exp_type} B{100+i} - Variant {i+1}"
                experiments.append({
                    "experiment_id": f"EXP-BEN-{i+1:04d}",
                    "title": title,
                    "project_id": f"proj_bench_{proj_idx}",
                    "author": author,
                    "created_at": (datetime.now() - timedelta(days=100+i//5)).isoformat(),
                    "status": status
                })
            return experiments

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/entries", headers=headers, timeout=10.0)
            resp.raise_for_status()
            entries = resp.json().get("entries", [])
            return [
                Experiment(
                    experiment_id=e.get("id"),
                    title=e.get("name"),
                    project_id=e.get("projectId") or e.get("folderId"),
                    author=e.get("creator", {}).get("name") if isinstance(e.get("creator"), dict) else str(e.get("creator")),
                    created_at=e.get("createdAt"),
                    status=e.get("displayStatus") or "Completed"
                ).model_dump()
                for e in entries
            ]

    async def fetch_protocols(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            protocols = []
            protocol_types = [
                "Kinase Profiling Assay Protocol", "High-Throughput ELISA protocol", "CRISPR transfection protocol",
                "Flow Cytometry validation procedure", "Sanger sequencing sample preparation", "MTS cell proliferation protocol",
                "Standard Operating Procedure for structural docking preparation"
            ]
            for i in range(120):
                name = f"{protocol_types[i % len(protocol_types)]} (Rev {i+1})"
                protocols.append({
                    "protocol_id": f"PROT-BEN-{i+1:03d}",
                    "name": name,
                    "version": f"v{1+i//10}.{i%10}",
                    "description": f"Standardized operating procedure for {name} to ensure batch reproducibility across screens."
                })
            return protocols

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/protocols", headers=headers, timeout=10.0)
            resp.raise_for_status()
            protocols = resp.json().get("protocols", [])
            return [
                Protocol(
                    protocol_id=p.get("id"),
                    name=p.get("name"),
                    version=p.get("version", "1.0"),
                    description=p.get("description")
                ).model_dump()
                for p in protocols
            ]

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            # Simulate a delta update
            return {
                "created": [{"experiment_id": "EXP-BEN-04", "title": "Delta Synthesis Screen", "project_id": "proj_bench_1", "author": "Dr. Sarah Connor", "created_at": datetime.utcnow().isoformat(), "status": "Draft"}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "experiments":
                # Benchling modifiedAt filter
                resp = await client.get(f"{self.api_url}/entries?modifiedAt=gte:{since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                entries = resp.json().get("entries", [])
                mapped = [
                    Experiment(
                        experiment_id=e.get("id"),
                        title=e.get("name"),
                        project_id=e.get("projectId") or e.get("folderId"),
                        author=e.get("creator", {}).get("name") if isinstance(e.get("creator"), dict) else str(e.get("creator")),
                        created_at=e.get("createdAt"),
                        status=e.get("displayStatus") or "Completed"
                    ).model_dump()
                    for e in entries
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "projects":
            return await self.fetch_projects()
        elif entity_name == "experiments":
            return await self.fetch_experiments()
        elif entity_name == "protocols":
            return await self.fetch_protocols()
        return []


class DotmaticsClient(BaseELNClient):
    """
    Production Dotmatics ELN integration.
    Interfaces with Dotmatics Gateway and Studies REST endpoints.
    """
    async def fetch_experiments(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"experiment_id": "EXP-DOT-101", "title": "Reflux Synthesis of Imidazoles", "project_id": "proj_dot_1", "author": "Alice Vance", "created_at": "2026-03-20T00:00:00Z", "status": "Signed Off"},
                {"experiment_id": "EXP-DOT-102", "title": "Hydrogenation under high pressure", "project_id": "proj_dot_1", "author": "Alice Vance", "created_at": "2026-04-22T00:00:00Z", "status": "In Progress"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/eln/experiments", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("experiments", [])
            return [
                Experiment(
                    experiment_id=str(e.get("experimentId") or e.get("id")),
                    title=e.get("title") or e.get("name"),
                    project_id=e.get("projectId"),
                    author=e.get("scientist") or e.get("author"),
                    created_at=e.get("createdDate") or e.get("createdAt"),
                    status=e.get("status")
                ).model_dump()
                for e in data
            ]

    async def fetch_protocols(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"protocol_id": "PROT-DOT-88", "name": "High-Pressure Reflux Protocol", "version": "v1.0", "description": "Reflux conditions at 5 bar pressure"},
                {"protocol_id": "PROT-DOT-89", "name": "Flash Column Chromatography", "version": "v2.4", "description": "Purification using Biotage automated column system"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/eln/protocols", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("protocols", [])
            return [
                Protocol(
                    protocol_id=str(p.get("protocolId") or p.get("id")),
                    name=p.get("name"),
                    version=p.get("version", "1.0"),
                    description=p.get("description")
                ).model_dump()
                for p in data
            ]

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            return {
                "created": [{"experiment_id": "EXP-DOT-103", "title": "Delta Dotmatics Run", "project_id": "proj_dot_1", "author": "Alice Vance", "created_at": datetime.utcnow().isoformat(), "status": "Draft"}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "experiments":
                resp = await client.get(f"{self.api_url}/eln/experiments?since={since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                data = resp.json().get("experiments", [])
                mapped = [
                    Experiment(
                        experiment_id=str(e.get("experimentId") or e.get("id")),
                        title=e.get("title") or e.get("name"),
                        project_id=e.get("projectId"),
                        author=e.get("scientist") or e.get("author"),
                        created_at=e.get("createdDate") or e.get("createdAt"),
                        status=e.get("status")
                    ).model_dump()
                    for e in data
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "experiments":
            return await self.fetch_experiments()
        elif entity_name == "protocols":
            return await self.fetch_protocols()
        return []


class SignalsNotebookClient(BaseELNClient):
    """
    Production Signals Notebook REST API integration.
    Interfaces with Revvity Signals Notebook endpoints.
    """
    async def fetch_experiments(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"experiment_id": "EXP-SIG-501", "title": "IC50 curve fitting for compound A", "project_id": "proj_sig_1", "author": "Dr. Sarah Conner", "created_at": "2026-05-01T00:00:00Z", "status": "Completed"},
                {"experiment_id": "EXP-SIG-502", "title": "Single-dose screen of GPCR analogs", "project_id": "proj_sig_1", "author": "Dr. John Connor", "created_at": "2026-05-10T00:00:00Z", "status": "Draft"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/api/v1.0/experiments", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            return [
                Experiment(
                    experiment_id=e.get("attributes", {}).get("eid") or e.get("id"),
                    title=e.get("attributes", {}).get("name"),
                    project_id=e.get("relationships", {}).get("project", {}).get("data", {}).get("id"),
                    author=e.get("attributes", {}).get("author", {}).get("name"),
                    created_at=e.get("attributes", {}).get("createdAt"),
                    status=e.get("attributes", {}).get("status") or "Draft"
                ).model_dump()
                for e in data
            ]

    async def fetch_protocols(self) -> List[Dict[str, Any]]:
        if self.use_simulator:
            return [
                {"protocol_id": "PROT-SIG-09", "name": "GPCR Calcium Influx Assay Protocol", "version": "v2.0", "description": "FLIPR based calcium influx screening assay method"}
            ]

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.api_url}/api/v1.0/protocols", headers=headers, timeout=10.0)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            return [
                Protocol(
                    protocol_id=p.get("id"),
                    name=p.get("attributes", {}).get("name"),
                    version=p.get("attributes", {}).get("version", "1.0"),
                    description=p.get("attributes", {}).get("description")
                ).model_dump()
                for p in data
            ]

    async def get_changes(self, entity_name: str, since_timestamp: str) -> Dict[str, List[Dict[str, Any]]]:
        if self.use_simulator:
            return {
                "created": [{"experiment_id": "EXP-SIG-503", "title": "Delta Signals Experiment", "project_id": "proj_sig_1", "author": "Dr. Sarah Conner", "created_at": datetime.utcnow().isoformat(), "status": "Draft"}],
                "updated": [],
                "deleted": []
            }

        headers = await self.get_headers()
        async with httpx.AsyncClient() as client:
            if entity_name == "experiments":
                resp = await client.get(f"{self.api_url}/api/v1.0/experiments?lastModified={since_timestamp}", headers=headers, timeout=10.0)
                resp.raise_for_status()
                data = resp.json().get("data", [])
                mapped = [
                    Experiment(
                        experiment_id=e.get("attributes", {}).get("eid") or e.get("id"),
                        title=e.get("attributes", {}).get("name"),
                        project_id=e.get("relationships", {}).get("project", {}).get("data", {}).get("id"),
                        author=e.get("attributes", {}).get("author", {}).get("name"),
                        created_at=e.get("attributes", {}).get("createdAt"),
                        status=e.get("attributes", {}).get("status") or "Draft"
                    ).model_dump()
                    for e in data
                ]
                return {"created": mapped, "updated": [], "deleted": []}
            return {"created": [], "updated": [], "deleted": []}

    async def fetch_records(self, entity_name: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if entity_name == "experiments":
            return await self.fetch_experiments()
        elif entity_name == "protocols":
            return await self.fetch_protocols()
        return []
