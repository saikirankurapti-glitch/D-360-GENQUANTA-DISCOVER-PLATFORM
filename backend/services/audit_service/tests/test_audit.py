import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the audit_service root to sys.path so we can import app modules directly
sys.path.append(str(Path(__file__).parent.parent))

# Set environment variables for testing before imports
os.environ["DATABASE_URL"] = "sqlite:///./test_audit.db"
os.environ["AUDIT_API_SECRET"] = "TEST_SECRET"

from app.main import app
from app.core.database import Base, get_db

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_audit.db"
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
    if os.path.exists("./test_audit.db"):
        try:
            os.remove("./test_audit.db")
        except PermissionError:
            pass

def test_record_audit_log_without_secret():
    response = client.post(
        "/api/v1/audit/logs",
        json={
            "user_id": "usr-01",
            "username": "tester",
            "action": "LOGIN",
            "service_name": "auth_service",
            "status": "SUCCESS"
        }
    )
    assert response.status_code == 401

def test_record_audit_log_with_secret():
    response = client.post(
        "/api/v1/audit/logs",
        headers={"x-audit-secret": "TEST_SECRET"},
        json={
            "user_id": "usr-01",
            "username": "tester",
            "action": "LOGIN",
            "service_name": "auth_service",
            "endpoint": "/api/v1/auth/login",
            "status": "SUCCESS",
            "ip_address": "127.0.0.1",
            "details": {"method": "password"}
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["action"] == "LOGIN"
    assert data["username"] == "tester"
    assert data["previous_hash"] is None
    assert "hash" in data

def test_chaining_logs():
    # Record a second log
    response = client.post(
        "/api/v1/audit/logs",
        headers={"x-audit-secret": "TEST_SECRET"},
        json={
            "user_id": "usr-01",
            "username": "tester",
            "action": "EXECUTE_QUERY",
            "service_name": "query_service",
            "status": "SUCCESS"
        }
    )
    assert response.status_code == 201
    data2 = response.json()
    assert data2["previous_hash"] is not None

    # Fetch logs
    get_res = client.get("/api/v1/audit/logs")
    assert get_res.status_code == 200
    logs = get_res.json()
    assert len(logs) >= 2
    
    # Confirm first log hash matches second log's previous_hash
    # Remember: logs are returned ordered by id desc
    assert logs[0]["previous_hash"] == logs[1]["hash"]

def test_integrity_verification():
    # Verify the last log's integrity
    get_res = client.get("/api/v1/audit/logs")
    logs = get_res.json()
    last_log_id = logs[0]["id"]
    
    verify_res = client.get(f"/api/v1/audit/logs/{last_log_id}/verify")
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["is_valid"] is True
    assert verify_data["chain_intact"] is True

def test_tampered_integrity():
    # Retrieve DB session, insert a tampered record, and check validation fail
    db = TestingSessionLocal()
    try:
        from app.models.audit import AuditLog
        log_obj = db.query(AuditLog).filter(AuditLog.id == 1).first()
        log_obj.action = "TAMPERED_ACTION"
        db.commit()
    finally:
        db.close()
        
    # Now verify log 2, it should fail because log 1's action changed (so its hash won't match)
    verify_res = client.get("/api/v1/audit/logs/2/verify")
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["is_valid"] is False
    assert verify_data["chain_intact"] is False
