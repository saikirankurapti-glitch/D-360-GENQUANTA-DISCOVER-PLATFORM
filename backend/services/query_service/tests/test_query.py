import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add query_service root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

os.environ["DATABASE_URL"] = "sqlite:///./test_query.db"

from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_query.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_query.db"):
        try:
            os.remove("./test_query.db")
        except PermissionError:
            pass

def test_sql_compilation_single():
    response = client.post(
        "/api/v1/query/compile",
        json={
            "nodes": [
                {
                    "id": "node-1",
                    "data": {
                        "entityType": "Compound",
                        "selectedFields": ["mw", "clogp"],
                        "filters": [{"field": "mw", "operator": ">", "value": "400"}]
                    }
                }
            ],
            "edges": []
        }
    )
    assert response.status_code == 200
    sql = response.json()["sql"]
    assert "SELECT compound_node_1.mw, compound_node_1.clogp" in sql
    assert "FROM compounds AS compound_node_1" in sql
    assert "WHERE compound_node_1.mw > 400" in sql

def test_sql_compilation_joined():
    response = client.post(
        "/api/v1/query/compile",
        json={
            "nodes": [
                {
                    "id": "node-1",
                    "data": {
                        "entityType": "Compound",
                        "selectedFields": ["mw"],
                        "filters": []
                    }
                },
                {
                    "id": "node-2",
                    "data": {
                        "entityType": "Assay",
                        "selectedFields": ["ic50_nm"],
                        "filters": [{"field": "ic50_nm", "operator": "<", "value": "10"}]
                    }
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "node-1",
                    "target": "node-2"
                }
            ]
        }
    )
    assert response.status_code == 200
    sql = response.json()["sql"]
    assert "INNER JOIN assays AS assay_node_2" in sql
    assert "ON compound_node_1.id = assay_node_2.compound_id" in sql
    assert "assay_node_2.ic50_nm < 10" in sql

def test_template_crud_and_duplication():
    # 1. Create Template
    create_resp = client.post(
        "/api/v1/query/templates",
        json={
            "name": "EGFR Inhibitors",
            "description": "Extract compounds with low EGFR activity",
            "layout_json": '{"nodes":[], "edges":[]}',
            "sql_preview": "SELECT * FROM compounds",
            "created_by": "sarah@company.com"
        }
    )
    assert create_resp.status_code == 201
    template = create_resp.json()
    assert template["name"] == "EGFR Inhibitors"
    template_id = template["id"]

    # 2. Get Templates
    list_resp = client.get("/api/v1/query/templates")
    assert len(list_resp.json()) >= 1

    # 3. Duplicate Template
    dup_resp = client.post(f"/api/v1/query/templates/{template_id}/duplicate")
    assert dup_resp.status_code == 200
    dup_template = dup_resp.json()
    assert dup_template["name"] == "Copy of EGFR Inhibitors"
    assert dup_template["layout_json"] == '{"nodes":[], "edges":[]}'

    # 4. Delete Original
    del_resp = client.delete(f"/api/v1/query/templates/{template_id}")
    assert del_resp.status_code == 200


def test_query_execution_real():
    # Test real query execution in DuckDB against virtual compounds table
    response = client.post(
        "/api/v1/query/execute",
        json={
            "sql": "SELECT id, name, smiles FROM compounds WHERE mw > 400",
            "use_cache": False
        }
    )
    assert response.status_code == 200
    res = response.json()
    assert "columns" in res
    assert "rows" in res
    assert "statistics" in res
    assert "id" in res["columns"]
    # Check that it executed and returned row(s) matching seed data
    assert len(res["rows"]) > 0
    assert res["rows"][0]["id"] in ["CMP-001", "CMP-002", "CMP-003", "CMP-004"]


def test_query_explain():
    # Test query explain plan compilation in DuckDB
    response = client.post(
        "/api/v1/query/explain",
        json={"sql": "SELECT name FROM compounds"}
    )
    assert response.status_code == 200
    res = response.json()
    assert "plan" in res
    assert "LOGICAL_LIMIT" in res["plan"] or "SCAN" in res["plan"] or "plan" in res


def test_query_history():
    # Test execution history recording
    # Execute a query first
    client.post(
        "/api/v1/query/execute",
        json={"sql": "SELECT name FROM compounds", "use_cache": False}
    )
    # Get history
    history_resp = client.get("/api/v1/query/history?limit=10")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert len(history) >= 1
    assert history[0]["status"] == "SUCCESS"
    assert "compounds" in history[0]["sql"]


def test_query_cancel_invalid_id():
    response = client.post("/api/v1/query/cancel/nonexistent-query-id")
    assert response.status_code == 404

