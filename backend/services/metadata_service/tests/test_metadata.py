import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the metadata_service root to sys.path so we can import app modules directly
sys.path.append(str(Path(__file__).parent.parent))

# Set environment variables for testing before imports
os.environ["DATABASE_URL"] = "sqlite:///./test_metadata.db"

from app.main import app
from app.core.database import Base, get_db

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_metadata.db"
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
    # Create the tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_metadata.db"):
        try:
            os.remove("./test_metadata.db")
        except PermissionError:
            pass

def test_create_field():
    response = client.post(
        "/api/v1/metadata/fields",
        json={
            "name": "clogp",
            "display_name": "cLogP",
            "data_type": "numeric",
            "description": "Calculated logP",
            "category": "Chemistry",
            "is_required": False
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "clogp"
    assert data["display_name"] == "cLogP"
    assert data["data_type"] == "numeric"
    assert "id" in data

def test_create_entity():
    # We need to get the field ID of clogp first or make sure it exists
    # Wait, the field clogp was created in test_create_field, let's fetch fields
    fields_response = client.get("/api/v1/metadata/fields")
    clogp_field = [f for f in fields_response.json() if f["name"] == "clogp"][0]
    clogp_id = clogp_field["id"]

    response = client.post(
        "/api/v1/metadata/entities",
        json={
            "entity_key": "CMP-101",
            "entity_type": "Compound",
            "name": "Test Compound",
            "description": "A compound for testing",
            "values": [
                {"field_id": clogp_id, "value": "3.5"}
            ]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["entity_key"] == "CMP-101"
    assert data["attributes"]["clogp"] == "3.5"
    assert data["details"][0]["display_name"] == "cLogP"

def test_bootstrap():
    response = client.post("/api/v1/metadata/bootstrap")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    
    # Confirm mock data is fetched
    entities_response = client.get("/api/v1/metadata/entities")
    assert len(entities_response.json()) > 0
