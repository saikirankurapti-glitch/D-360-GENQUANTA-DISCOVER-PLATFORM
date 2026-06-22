import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the auth_service root to sys.path so we can import app modules directly
sys.path.append(str(Path(__file__).parent.parent))

# Set environment variables for testing before imports
os.environ["DATABASE_URL"] = "sqlite:///./test_auth.db"

from app.core.database import Base
# Import all models to populate metadata
from app.models.user import User
from app.models.rbac import Role, Permission, RolePermission, UserRole
for table in Base.metadata.tables.values():
    table.schema = None

from app.main import app
from app.core.database import get_db

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
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
    # Strip schemas for SQLite compatibility
    for table in Base.metadata.tables.values():
        table.schema = None
    # Create the tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)
    # Dispose engine to close all open database connections on Windows
    engine.dispose()
    if os.path.exists("./test_auth.db"):
        try:
            os.remove("./test_auth.db")
        except PermissionError:
            pass

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "securepassword123", "full_name": "Test Scientist", "role": "Scientist"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test Scientist"
    assert data["role"] == "Scientist"
    assert "id" in data

def test_login_user():
    # Login with the user registered in the previous test
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "Scientist"

def test_login_invalid_password():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_get_me():
    # First, login to get access token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "securepassword123"}
    )
    token = login_response.json()["access_token"]
    
    # Access profile
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test Scientist"

def test_token_refresh():
    # Login to get refresh token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "securepassword123"}
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
