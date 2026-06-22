import os
import sys
import json
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

def test_pca():
    payload = {
        "columns": ["mw", "logp", "tpsa"],
        "rows": [
            [300.0, 2.5, 60.0],
            [400.0, 3.5, 70.0],
            [250.0, 1.5, 50.0],
            [350.0, 2.8, 65.0]
        ],
        "features": ["mw", "logp", "tpsa"]
    }
    response = client.post("/api/v1/analytics/pca", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "coords" in data
    assert len(data["coords"]) == 4
    assert "explained_variance" in data
    assert "loadings" in data
    assert len(data["loadings"]) == 3

def test_tsne():
    payload = {
        "columns": ["mw", "logp", "tpsa"],
        "rows": [
            [300.0, 2.5, 60.0],
            [400.0, 3.5, 70.0],
            [250.0, 1.5, 50.0],
            [350.0, 2.8, 65.0],
            [420.0, 4.0, 80.0]
        ],
        "features": ["mw", "logp", "tpsa"],
        "perplexity": 2
    }
    response = client.post("/api/v1/analytics/tsne", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "coords" in data
    assert len(data["coords"]) == 5

def test_clustering():
    payload = {
        "columns": ["mw", "logp"],
        "rows": [
            [300.0, 2.5],
            [400.0, 3.5],
            [250.0, 1.5],
            [350.0, 2.8]
        ],
        "features": ["mw", "logp"],
        "algorithm": "kmeans",
        "n_clusters": 2
    }
    response = client.post("/api/v1/analytics/clustering", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert len(data["labels"]) == 4
    assert set(data["labels"]).issubset({0, 1})

def test_correlation():
    payload = {
        "columns": ["mw", "logp"],
        "rows": [
            [300.0, 2.5],
            [400.0, 3.5],
            [250.0, 1.5],
            [350.0, 2.8]
        ],
        "features": ["mw", "logp"]
    }
    response = client.post("/api/v1/analytics/correlation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "matrix" in data
    assert len(data["matrix"]) == 2
    assert "columns" in data

def test_dose_response_success():
    # Sigmoidal response data points
    concentrations = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    responses = [2.0, 8.0, 25.0, 50.0, 80.0, 98.0]
    
    payload = {
        "concentrations": concentrations,
        "responses": responses
    }
    response = client.post("/api/v1/analytics/dose-response", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["ec50"] > 0
    assert "curve_points" in data
    assert len(data["curve_points"]["concentrations"]) == 100

def test_workspaces_crud():
    # 1. Create Workspace
    payload = {
        "name": "Target Validation Workspace",
        "description": "Exploratory analysis of compound panel",
        "configs_json": json.dumps({"xCol": "mw", "yCol": "logp"}),
        "dataset_json": json.dumps({"columns": ["mw"], "rows": [[250.0]]})
    }
    response = client.post("/api/v1/analytics/workspaces", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Target Validation Workspace"
    workspace_id = data["id"]

    # 2. Get list
    response = client.get("/api/v1/analytics/workspaces")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 3. Get single
    response = client.get(f"/api/v1/analytics/workspaces/{workspace_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Target Validation Workspace"

    # 4. Delete
    response = client.delete(f"/api/v1/analytics/workspaces/{workspace_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Workspace deleted successfully"
