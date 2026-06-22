import pytest
import json
import httpx
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.models.workflow import WorkflowDefinition, WorkflowRun, WorkflowStep, WorkflowApproval
from app.engine.executor import WorkflowExecutor

# Mock helper for all external microservices
def mock_http_request(method: str, url: str, **kwargs):
    mock_resp = MagicMock()
    mock_resp.status_code = 200

    # 1. Sources check
    if "sources" in url:
        if method == "GET":
            if "entities" in url:
                mock_resp.json = lambda: [
                    {
                        "physical_name": "experiments",
                        "fields": [{"physical_name": "id"}, {"physical_name": "title"}]
                    }
                ]
            else:
                mock_resp.json = lambda: [{"id": 1, "name": "Benchling LIMS", "is_active": True}]
        elif method == "POST":
            # Sync / Query execution
            mock_resp.json = lambda: {
                "columns": ["id", "title"],
                "rows": [{"id": "EXP-01", "title": "Test Ingestion"}, {"id": "EXP-02", "title": "Binding Assay"}]
            }
    # 2. Query service execution
    elif "query/execute" in url:
        mock_resp.json = lambda: {
            "columns": ["id", "name", "ic50_nm"],
            "rows": [{"id": "CMP-001", "name": "Kinase Inhibitor", "ic50_nm": 3.2}]
        }
    # 3. Cheminformatics search
    elif "cheminformatics/search" in url:
        mock_resp.json = lambda: {
            "results": [{"compound_key": "CMP-001", "similarity": 0.85}]
        }
    # 4. Bioinformatics pairwise alignment
    elif "bioinformatics/align/pairwise" in url:
        mock_resp.json = lambda: {
            "score": 45.0,
            "aligned_seq_a": "MADEEKLK-ALALGYDAVGD",
            "aligned_seq_b": "MADEEK-IKALALGYDAVGD"
        }
    # 5. Audit logs
    elif "audit/logs" in url:
        mock_resp.json = lambda: {"status": "success"}
    else:
        mock_resp.json = lambda: {"status": "success"}

    return mock_resp

@pytest.fixture(autouse=True)
def mock_httpx_requests():
    with patch("httpx.AsyncClient.get", side_effect=lambda url, **kwargs: mock_http_request("GET", url, **kwargs)) as mock_get, \
         patch("httpx.AsyncClient.post", side_effect=lambda url, **kwargs: mock_http_request("POST", url, **kwargs)) as mock_post:
        yield mock_get, mock_post

def test_create_workflow_definition(client: TestClient):
    """Test creating a workflow definition via REST API."""
    payload = {
        "name": "Metadata Ingestion Flow",
        "description": "Syncs LIMS records and flags low similarity compounds",
        "nodes_json": json.dumps([
            {"id": "node_1", "type": "datasource", "data": {"label": "LIMS Ingestion", "source_id": 1, "entity_name": "samples"}},
            {"id": "node_2", "type": "notification", "data": {"label": "Email Alert", "recipient": "lab@org.com"}}
        ]),
        "edges_json": json.dumps([
            {"id": "edge_1", "source": "node_1", "target": "node_2"}
        ]),
        "trigger_type": "MANUAL",
        "cron_schedule": None,
        "is_active": True
    }

    resp = client.post("/api/v1/workflows", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Metadata Ingestion Flow"
    assert data["trigger_type"] == "MANUAL"
    assert data["id"] is not None

@pytest.mark.anyio
async def test_manual_run_execution(client: TestClient, db_session):
    """Test launching and executing a workflow run to completion."""
    # Seed a definition
    nodes = [
        {"id": "node_1", "type": "datasource", "data": {"label": "Benchling LIMS", "source_id": 1, "entity_name": "experiments"}},
        {"id": "node_2", "type": "notification", "data": {"label": "Teams Alert", "recipient": "test@org.com"}}
    ]
    edges = [{"id": "edge_1", "source": "node_1", "target": "node_2"}]
    
    definition = WorkflowDefinition(
        name="LIMS Ingest Flow",
        nodes_json=json.dumps(nodes),
        edges_json=json.dumps(edges),
        trigger_type="MANUAL"
    )
    db_session.add(definition)
    db_session.commit()
    db_session.refresh(definition)

    # Trigger run
    resp = client.post(f"/api/v1/workflows/{definition.id}/run")
    assert resp.status_code == 200
    run_data = resp.json()
    run_id = run_data["id"]

    # Manually execute to guarantee determinism in testing
    executor = WorkflowExecutor()
    await executor.execute_run(run_id, db=db_session)

    # Check execution status of run
    resp = client.get(f"/api/v1/workflows/runs/{run_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "COMPLETED"

    # Verify execution steps were generated
    resp = client.get(f"/api/v1/workflows/runs/{run_id}/steps")
    assert resp.status_code == 200
    steps = resp.json()
    assert len(steps) == 2
    assert steps[0]["step_id"] == "node_1"
    assert steps[1]["step_id"] == "node_2"

@pytest.mark.anyio
async def test_approval_halt_and_resume(client: TestClient, db_session, mock_httpx_requests):
    """Test that approval node halts the run and actioning resumes execution."""
    mock_get, mock_post = mock_httpx_requests
    nodes = [
        {"id": "node_1", "type": "datasource", "data": {"label": "Benchling LIMS", "source_id": 1}},
        {"id": "node_2", "type": "approval", "data": {"label": "Review Signature", "role_required": "REVIEWER"}},
        {"id": "node_3", "type": "notification", "data": {"label": "Notify Completed"}}
    ]
    edges = [
        {"id": "edge_1", "source": "node_1", "target": "node_2"},
        {"id": "edge_2", "source": "node_2", "target": "node_3"}
    ]

    definition = WorkflowDefinition(
        name="Compliance Sign Flow",
        nodes_json=json.dumps(nodes),
        edges_json=json.dumps(edges),
        trigger_type="MANUAL"
    )
    db_session.add(definition)
    db_session.commit()
    db_session.refresh(definition)

    # Trigger run
    resp = client.post(f"/api/v1/workflows/{definition.id}/run")
    assert resp.status_code == 200
    run_id = resp.json()["id"]

    # Manually execute to halt on approval
    executor = WorkflowExecutor()
    await executor.execute_run(run_id, db=db_session)

    # Verify that run is waiting for approval
    resp = client.get(f"/api/v1/workflows/runs/{run_id}")
    assert resp.json()["status"] == "WAITING_APPROVAL"

    # Verify approval request was generated
    resp = client.get("/api/v1/workflows/approvals")
    assert resp.status_code == 200
    approvals = resp.json()
    assert len(approvals) >= 1
    pending_app = next(a for a in approvals if a["run_id"] == run_id)
    assert pending_app["status"] == "PENDING"
    assert pending_app["role_required"] == "REVIEWER"

    # Action Approval (APPROVE)
    action_payload = {
        "status": "APPROVED",
        "approved_by": "Dr. Sarah Connor",
        "comment": "Data looks verified and matches compliance catalog.",
        "signature_payload": {"user_id": 101, "signed_fullname": "Sarah Connor"}
    }
    
    # Call the API action (which updates database status to APPROVED)
    resp = client.post(f"/api/v1/workflows/approvals/{pending_app['id']}/action", json=action_payload)
    assert resp.status_code == 200

    # Call the resume_run directly with the db session to execute synchronously and deterministically
    await executor.resume_run(run_id, pending_app["id"], action_payload["signature_payload"], db=db_session)

    # Verify that the run has resumed and completed successfully
    resp = client.get(f"/api/v1/workflows/runs/{run_id}")
    assert resp.json()["status"] == "COMPLETED"

    # Assert compliance signature and audit log posts occurred
    posted_urls = [args[0][0] for args in mock_post.call_args_list]
    assert any("audit/logs" in url for url in posted_urls)
    assert any("compliance/signatures" in url for url in posted_urls)

@pytest.mark.anyio
async def test_event_driven_triggering(client: TestClient, db_session):
    """Test that a matching event type triggers active event workflows."""
    # Seed an event-driven definition
    nodes = [{"id": "node_1", "type": "notification", "data": {"label": "Notify Event"}}]
    
    definition = WorkflowDefinition(
        name="Auto Event Flow",
        nodes_json=json.dumps(nodes),
        edges_json=json.dumps([]),
        trigger_type="EVENT",
        is_active=True
    )
    db_session.add(definition)
    db_session.commit()

    # Trigger event
    event_payload = {
        "event_type": "new_file",
        "payload": {"filename": "sequence_A.fasta", "size_bytes": 1024}
    }
    resp = client.post("/api/v1/workflows/events/trigger", json=event_payload)
    assert resp.status_code == 200
    assert resp.json()["triggered_runs"] == 1

def test_sync_scheduler_jobs(db_session, monkeypatch):
    """Test that active scheduled workflows are registered in APScheduler on startup."""
    from app.main import sync_scheduler_jobs, scheduler
    import app.main
    
    # Override SessionLocal to use test database
    monkeypatch.setattr(app.main, "SessionLocal", lambda: db_session)
    
    definition = WorkflowDefinition(
        name="Scheduled Data Sync",
        nodes_json="[]",
        edges_json="[]",
        trigger_type="SCHEDULED",
        cron_schedule="0 12 * * *",
        is_active=True
    )
    db_session.add(definition)
    db_session.commit()
    db_session.refresh(definition)
    
    sync_scheduler_jobs()
    
    job_id = f"workflow_{definition.id}"
    job = scheduler.get_job(job_id)
    assert job is not None
    assert job.id == job_id
    
    scheduler.remove_job(job_id)
