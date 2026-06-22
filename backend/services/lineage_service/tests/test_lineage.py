import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine

@pytest.fixture(scope="module")
def client():
    # Bind to standard sqlite db for tests
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Discover Lineage Service"

def test_record_trace(client):
    payload = {
        "source_node": {
            "id": "ds-postgres",
            "type": "datasource",
            "name": "Production PostgreSQL DB",
            "details": {"url": "postgresql://localhost:5432"}
        },
        "target_node": {
            "id": "q-438",
            "type": "query",
            "name": "Select Active Compounds Query",
            "details": {"sql": "SELECT * FROM compounds WHERE active = true"}
        },
        "edge_type": "flow"
    }
    response = client.post("/api/v1/lineage/trace", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == "recorded"
    assert response.json()["source_node_id"] == "ds-postgres"
    assert response.json()["target_node_id"] == "q-438"

def test_fetch_graph(client):
    payload = {
        "source_node": {
            "id": "q-438",
            "type": "query",
            "name": "Select Active Compounds Query"
        },
        "target_node": {
            "id": "export-1",
            "type": "export",
            "name": "Active_Compounds_Export.csv"
        }
    }
    client.post("/api/v1/lineage/trace", json=payload)
    
    response = client.get("/api/v1/lineage/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 3
    assert len(data["edges"]) >= 2
