import httpx
from typing import Dict, Any, List
from unittest.mock import MagicMock

class MockResponse:
    def __init__(self, json_data: Any, status_code: int = 200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self) -> Any:
        return self.json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(f"HTTP Error {self.status_code}", request=MagicMock(), response=MagicMock())


def mock_vendor_request(method: str, url: str, **kwargs) -> MockResponse:
    """Interceptors that mock real Benchling, LabWare, and other vendor REST API endpoints."""
    url_str = str(url)
    
    # 1. Benchling mock endpoints
    if "benchling.sandbox.com" in url_str:
        if "/oauth/token" in url_str:
            return MockResponse({"access_token": "mock-benchling-oauth-token-xyz"}, 200)
        elif "/projects" in url_str:
            return MockResponse({
                "projects": [
                    {"id": "proj_bench_1", "name": "Oncology Target Discovery", "description": "Benchling project exploring kinase pathways", "createdAt": "2026-01-10T00:00:00Z"},
                    {"id": "proj_bench_2", "name": "Immunotherapy Screen", "description": "Antibody screening assays and candidate identification", "createdAt": "2026-02-14T00:00:00Z"}
                ]
            }, 200)
        elif "/entries" in url_str:
            return MockResponse({
                "entries": [
                    {"id": "EXP-BEN-01", "name": "Synthesis of Kinase Inhibitor B102", "folderId": "proj_bench_1", "creator": {"name": "Dr. Sarah Connor"}, "createdAt": "2026-03-12T00:00:00Z", "displayStatus": "Completed"},
                    {"id": "EXP-BEN-02", "name": "Binding Assay for target K-RAS", "folderId": "proj_bench_1", "creator": {"name": "Dr. Sarah Connor"}, "createdAt": "2026-04-01T00:00:00Z", "displayStatus": "In Progress"}
                ]
            }, 200)
        elif "/protocols" in url_str:
            return MockResponse({
                "protocols": [
                    {"id": "PROT-BEN-001", "name": "Kinase Profiling Assay Protocol", "version": "v1.2", "description": "Standard operating procedure for kinase profiling"}
                ]
            }, 200)
        elif "/health" in url_str:
            return MockResponse({"status": "healthy"}, 200)

    # 2. LabWare mock endpoints
    elif "labware.net" in url_str:
        if "/api/samples" in url_str:
            return MockResponse({
                "data": [
                    {"sampleNumber": "SMP-LW-801", "batch": "BAT-11002", "sampleTemplate": "HEK293 Lysate", "status": "In Progress", "amount": 2.5, "unit": "mL", "location": "Liquid Nitrogen Tank 1", "created": "2026-04-12T00:00:00Z"}
                ]
            }, 200)
        elif "/api/tests" in url_str:
            return MockResponse({
                "data": [
                    {"test_id": "TST-LW-501", "sample_id": "SMP-LW-801", "test_type": "Western Blot", "assigned_operator": "Alice Vance", "completion_date": "2026-04-20T00:00:00Z"}
                ]
            }, 200)
        elif "/status" in url_str:
            return MockResponse({"status": "ready"}, 200)

    # 3. Signals Notebook mock endpoints
    elif "signals" in url_str:
        if "/api/v1.0/experiments" in url_str:
            return MockResponse({
                "data": [
                    {"id": "EXP-SIG-501", "attributes": {"eid": "EXP-SIG-501", "name": "IC50 curve fitting for compound A", "createdAt": "2026-05-01T00:00:00Z", "status": "Completed"}}
                ]
            }, 200)
        return MockResponse({"status": "ok"}, 200)

    # 4. STARLIMS mock endpoints
    elif "starlims" in url_str:
        if "/samples" in url_str:
            return MockResponse({
                "samples": [
                    {"sampleKey": "SMP-SL-301", "batchNo": "BAT-5509", "template": "Plasma", "status": "Approved", "qty": 3.0, "unit": "mL", "storageLoc": "STAR-Rack-4", "loggedTime": "2026-05-18T00:00:00Z"}
                ]
            }, 200)
        elif "/tests" in url_str:
            return MockResponse({
                "tests": [
                    {"test_id": "TST-SL-301", "sample_id": "SMP-SL-301", "test_type": "Enzymatic Influx", "assigned_operator": "Bob Marley", "completion_date": "2026-05-19T00:00:00Z"}
                ]
            }, 200)

    # 5. HTS mock endpoints
    elif "hts-db.org" in url_str:
        if "/hts/assays" in url_str:
            return MockResponse({
                "assays": [
                    {"id": "ASY-HTS-300", "name": "Primary GPCR 384-well Screening", "target": "GPCR-D2", "type": "Fluorescence Influx"}
                ]
            }, 200)
        elif "/hts/results" in url_str:
            return MockResponse({
                "results": [
                    {"id": "RES-HTS-1209", "assayId": "ASY-HTS-300", "compoundId": "CHEM-000495", "value": 78.4, "unit": "% Inhibition", "outcome": "Active"}
                ]
            }, 200)
        elif "/hts/plates" in url_str:
            return MockResponse({
                "plates": [
                    {"id": "PLT-384-90", "barcode": "BARCODE90", "format": 384, "status": "Screened"}
                ]
            }, 200)

    return MockResponse({"message": "Not Found"}, 404)
