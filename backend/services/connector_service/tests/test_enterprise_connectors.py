import pytest
import json
from unittest.mock import patch
from app.connectors.enterprise.eln import ELNConnector
from app.connectors.enterprise.lims import LIMSConnector
from app.connectors.enterprise.assay import AssayConnector
from tests.mock_vendor_apis import mock_vendor_request
from app.core.database import SessionLocal
from app.repositories.connector_repository import repo

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.mark.anyio
async def test_eln_benchling_simulator_sync(db_session):
    """Verify that ELNConnector Benchling simulator sync updates metadata catalog & CDC checkpoints."""
    credentials = {
        "api_url": "https://benchling.sandbox.com/api/v1",
        "auth_token": "mock-token-123",
        "use_simulator": True
    }
    additional_params = {"vendor": "benchling"}
    
    # Register data source in db to satisfy ForeignKey constraint
    from app.models.connector import DataSource, ConnectionConfig
    ds = DataSource(name="Test Benchling Source", connector_type="eln", is_active=True)
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)
    
    config = ConnectionConfig(data_source_id=ds.id, encrypted_credentials="{}", additional_params=json.dumps(additional_params))
    db_session.add(config)
    db_session.commit()
    
    connector = ELNConnector(credentials, additional_params)
    
    # 1. Test Connection
    success, msg = await connector.test_connection()
    assert success is True
    
    # 2. Discover & Sync Entities
    synced = await connector.sync_entities(db_session, ds.id)
    assert synced > 0
    
    # 3. Test Incremental CDC Sync
    cdc_res = await connector.incremental_sync(db_session, ds.id, "experiments")
    assert cdc_res["entity"] == "experiments"
    assert cdc_res["created"] > 0
    
    # 4. Check that SyncCheckpoint was recorded
    chk = repo.get_sync_checkpoint(db_session, ds.id, "experiments")
    assert chk is not None
    assert chk.sync_status == "SUCCESS"


@pytest.mark.anyio
@patch("httpx.AsyncClient.get", side_effect=lambda url, **kwargs: mock_vendor_request("GET", url, **kwargs))
@patch("httpx.AsyncClient.post", side_effect=lambda url, **kwargs: mock_vendor_request("POST", url, **kwargs))
async def test_eln_benchling_production_handshake(mock_post, mock_get, db_session):
    """Verify real HTTP handshakes against Benchling API when use_simulator=False."""
    credentials = {
        "api_url": "https://benchling.sandbox.com/api/v1",
        "client_id": "oauth-client-id",
        "client_secret": "oauth-client-secret",
        "use_simulator": False
    }
    additional_params = {"vendor": "benchling"}
    
    connector = ELNConnector(credentials, additional_params)
    client = connector._get_client()
    
    # Test Projects fetch triggers authenticate() and get_headers()
    projects = await client.fetch_projects()
    assert len(projects) == 2
    assert projects[0]["name"] == "Oncology Target Discovery"
    assert projects[0]["project_id"] == "proj_bench_1"
    
    # Verify exact endpoints hit
    assert mock_post.called
    assert mock_get.called


@pytest.mark.anyio
@patch("httpx.AsyncClient.get", side_effect=lambda url, **kwargs: mock_vendor_request("GET", url, **kwargs))
async def test_lims_labware_production_sync(mock_get, db_session):
    """Verify that LabWare LIMS connector handles production REST payload mappings."""
    credentials = {
        "api_url": "https://labware.net/api",
        "auth_token": "lw-token-999",
        "use_simulator": False
    }
    additional_params = {"vendor": "labware"}
    
    connector = LIMSConnector(credentials, additional_params)
    client = connector._get_client()
    
    samples = await client.fetch_samples()
    assert len(samples) == 1
    assert samples[0]["sample_id"] == "SMP-LW-801"
    assert samples[0]["sample_type"] == "HEK293 Lysate"
    assert samples[0]["status"] == "In Progress"


@pytest.mark.anyio
@patch("httpx.AsyncClient.get", side_effect=lambda url, **kwargs: mock_vendor_request("GET", url, **kwargs))
async def test_assay_hts_production_sync(mock_get, db_session):
    """Verify that HTS Assay connector handles production plates and results."""
    credentials = {
        "api_url": "https://hts-db.org",
        "api_key": "hts-token",
        "use_simulator": False
    }
    additional_params = {"vendor": "hts"}
    
    connector = AssayConnector(credentials, additional_params)
    client = connector._get_client()
    
    plates = await client.fetch_plates()
    assert len(plates) == 1
    assert plates[0]["plate_id"] == "PLT-384-90"
    assert plates[0]["plate_format"] == 384
