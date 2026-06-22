import json
import pytest
from fastapi.testclient import TestClient

def test_health(client: TestClient):
    """Test the base health check endpoint."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    assert "AI Copilot" in resp.json()["service"]

def test_chat_flow(client: TestClient):
    """Test creating a chat session and carrying out a grounded conversation with citations."""
    # 1. Create a session
    resp = client.post("/api/v1/copilot/chat/sessions", json={"title": "EGFR Inhibitor Investigation"})
    assert resp.status_code == 200
    session_data = resp.json()
    session_id = session_data["id"]
    assert session_data["title"] == "EGFR Inhibitor Investigation"

    # 2. Retrieve history (should be empty)
    resp = client.get(f"/api/v1/copilot/chat/sessions/{session_id}/messages")
    assert resp.status_code == 200
    assert len(resp.json()) == 0

    # 3. Post a message
    message_payload = {"message": "Tell me about compound CHEM-4402 and its target."}
    resp = client.post(f"/api/v1/copilot/chat/sessions/{session_id}/respond", json=message_payload)
    assert resp.status_code == 200
    msg = resp.json()
    assert msg["role"] == "assistant"
    assert "CHEM-4402" in msg["content"]
    
    # 4. Check citations
    citations = json.loads(msg["citations_json"])
    assert len(citations) > 0
    assert citations[0]["source"] is not None
    assert "[1]" in msg["content"] or "Findings" in msg["content"]

    # 5. Check history size
    resp = client.get(f"/api/v1/copilot/chat/sessions/{session_id}/messages")
    assert len(resp.json()) == 2  # 1 User message + 1 Assistant response

def test_query_plan(client: TestClient):
    """Test natural language to federated query plan compilation."""
    payload = {"query": "Show compounds active against EGFR with IC50 < 100 nM"}
    resp = client.post("/api/v1/copilot/query-plan", json=payload)
    assert resp.status_code == 200
    plan = resp.json()
    assert plan["original_query"] == payload["query"]
    assert "generated_sql" in plan
    assert "EGFR" in plan["generated_sql"]
    assert len(plan["plan_steps"]) > 0

def test_analytics(client: TestClient):
    """Test generating scientific insights for specific alignment datasets."""
    payload = {
        "data_type": "alignment",
        "payload": {
            "matches": 92,
            "mismatches": 8,
            "gaps": 1,
            "score": 485.0
        }
    }
    resp = client.post("/api/v1/copilot/analytics", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    assert res["data_type"] == "alignment"
    assert "Sequence Alignment Analysis" in res["analysis"]
    assert "92%" in res["analysis"]

def test_excel_report_generation(client: TestClient):
    """Test exporting scientific results as an Excel sheet."""
    payload = {
        "title": "Kinase Screening Report",
        "format": "excel",
        "data": [
            {"compound_id": "CHEM-4402", "target": "EGFR", "ic50": 42.0},
            {"compound_id": "CHEM-9821", "target": "EGFR", "ic50": 820.0}
        ]
    }
    resp = client.post("/api/v1/copilot/report", json=payload)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(resp.content) > 100  # Verify non-empty workbook binary

def test_dashboard_layout_generation(client: TestClient):
    """Test compiling natural language requests into dashboard widgets."""
    payload = {"prompt": "Create a dashboard showing active compounds by target."}
    resp = client.post("/api/v1/copilot/dashboard", json=payload)
    assert resp.status_code == 200
    layout = resp.json()
    assert "title" in layout
    assert "widgets" in layout
    assert len(layout["widgets"]) > 0
    assert layout["widgets"][0]["plotly_data"] is not None

def test_workflow_generation(client: TestClient):
    """Test compiling user requests into React Flow graph definitions."""
    payload = {"prompt": "Create a workflow that syncs Benchling daily, runs sequence alignment, and emails results."}
    resp = client.post("/api/v1/copilot/workflow", json=payload)
    assert resp.status_code == 200
    graph = resp.json()
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) > 2
    assert graph["trigger_type"] == "SCHEDULED"
