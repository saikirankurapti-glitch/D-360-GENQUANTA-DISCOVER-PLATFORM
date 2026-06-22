import base64
import json
import pytest
from app.connectors.registry import ConnectorRegistry
from app.utils.security import encryptor
from app.connectors.file_reader import FileReaderConnector

def test_connector_registry():
    """Verify that registry registers built-in and enterprise connectors."""
    assert "postgresql" in ConnectorRegistry._registry
    assert "file" in ConnectorRegistry._registry
    assert "eln" in ConnectorRegistry._registry
    assert "lims" in ConnectorRegistry._registry
    
    postgres_class = ConnectorRegistry.get_connector("postgresql")
    assert postgres_class.__name__ == "PostgreSQLConnector"
    
    capabilities = ConnectorRegistry.get_all_capabilities()
    assert len(capabilities) > 0
    connector_types = [c["connector_type"] for c in capabilities]
    assert "postgresql" in connector_types
    assert "file" in connector_types


def test_encryption_decryption():
    """Verify credential encryption/decryption works correctly and safely."""
    creds = {"host": "localhost", "username": "admin", "password": "super-secret-password-123"}
    encrypted = encryptor.encrypt(creds)
    assert isinstance(encrypted, str)
    assert encrypted != json.dumps(creds)
    
    decrypted = encryptor.decrypt(encrypted)
    assert decrypted == creds


@pytest.mark.anyio
async def test_csv_file_connector():
    """Verify that FileReaderConnector successfully ingests CSV and executes pandas queries."""
    # Create simple base64 encoded CSV
    csv_content = (
        "id,compound_name,mw,active\n"
        "1,Aspirin,180.16,True\n"
        "2,Caffeine,194.19,True\n"
        "3,Ibuprofen,206.29,False\n"
    )
    b64_content = base64.b64encode(csv_content.encode()).decode()
    
    credentials = {
        "file_name": "compounds_test.csv",
        "file_content": b64_content
    }
    
    connector = FileReaderConnector(credentials)
    
    # Test connection
    success, msg = await connector.test_connection()
    assert success is True
    
    # Test schema discovery
    schema = await connector.discover_schema()
    assert len(schema) == 1
    entity = schema[0]
    assert entity["physical_name"] == "compounds_test"
    assert len(entity["fields"]) == 4
    
    field_names = [f["physical_name"] for f in entity["fields"]]
    assert "compound_name" in field_names
    assert "mw" in field_names
    
    # Test execute query with filters (mw > 190)
    query = {
        "entity": "compounds_test",
        "fields": ["compound_name", "mw"],
        "filters": [
            {"field": "mw", "operator": ">", "value": 190.0}
        ],
        "limit": 10
    }
    
    columns, rows = await connector.execute_query(query)
    assert columns == ["compound_name", "mw"]
    assert len(rows) == 2  # Caffeine (194.19) and Ibuprofen (206.29)
    assert rows[0][0] == "Caffeine"
    assert rows[1][0] == "Ibuprofen"


def test_api_endpoints(client):
    """Verify core API endpoints for datasource CRUD and querying."""
    # 1. Get capabilities
    response = client.get("/api/v1/connectors/capabilities")
    assert response.status_code == 200
    assert len(response.json()) > 0

    # 2. Register a mock/file source
    csv_content = "id,name\n1,Compound A\n2,Compound B\n"
    b64_content = base64.b64encode(csv_content.encode()).decode()
    
    source_payload = {
        "name": "Test File Source",
        "description": "Local test dataset",
        "connector_type": "file",
        "credentials": {
            "file_name": "test_compounds.csv",
            "file_content": b64_content
        },
        "additional_params": {}
    }
    
    response = client.post("/api/v1/connectors/sources", json=source_payload)
    assert response.status_code == 201
    source_data = response.json()
    assert source_data["name"] == "Test File Source"
    source_id = source_data["id"]
    
    # 3. List data sources
    response = client.get("/api/v1/connectors/sources")
    assert response.status_code == 200
    assert len(response.json()) == 1
    
    # 4. Trigger Schema Sync
    response = client.post(f"/api/v1/connectors/sources/{source_id}/sync")
    assert response.status_code == 200
    sync_data = response.json()
    assert sync_data["sync_status"] == "SUCCESS"
    
    # 5. Get discovered entities
    response = client.get(f"/api/v1/connectors/sources/{source_id}/entities")
    assert response.status_code == 200
    entities = response.json()
    assert len(entities) == 1
    assert entities[0]["physical_name"] == "test_compounds"
    assert len(entities[0]["fields"]) == 2
    
    # 6. Execute data query
    query_payload = {
        "entity": "test_compounds",
        "fields": ["id", "name"],
        "filters": [
            {"field": "id", "operator": "=", "value": 2}
        ],
        "limit": 10
    }
    response = client.post(f"/api/v1/connectors/sources/{source_id}/query", json=query_payload)
    assert response.status_code == 200
    query_result = response.json()
    assert query_result["row_count"] == 1
    assert query_result["rows"][0][1] == "Compound B"


@pytest.mark.anyio
async def test_mongodb_connector(monkeypatch):
    """Verify that MongoDBConnector handles connection, schema discovery, and query translation correctly."""
    from unittest.mock import MagicMock
    from app.connectors.mongodb import MongoDBConnector
    
    # Mock MongoClient
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    
    # Mock list_collection_names
    mock_db.list_collection_names.return_value = ["compounds", "system.views"]
    
    # Mock sample documents for schema discovery
    mock_db["compounds"].find.return_value.limit.return_value = [
        {"_id": "obj123", "name": "Compound X", "density": 1.25, "active": True}
    ]
    
    # Monkeypatch pymongo MongoClient to return our mock
    monkeypatch.setattr("app.connectors.mongodb.MongoClient", lambda *args, **kwargs: mock_client)
    
    credentials = {
        "host": "localhost",
        "port": 27017,
        "database": "test_db",
        "username": "user",
        "password": "pwd"
    }
    
    connector = MongoDBConnector(credentials)
    
    # 1. Test Connection
    success, msg = await connector.test_connection()
    assert success is True
    assert "Successfully" in msg
    mock_client.admin.command.assert_called_with("ping")
    
    # 2. Schema Discovery
    schema = await connector.discover_schema()
    assert len(schema) == 1
    entity = schema[0]
    assert entity["physical_name"] == "compounds"
    assert len(entity["fields"]) == 4
    
    field_names = [f["physical_name"] for f in entity["fields"]]
    assert "_id" in field_names
    assert "density" in field_names
    
    # Find density type
    density_field = next(f for f in entity["fields"] if f["physical_name"] == "density")
    assert density_field["data_type"] == "float"
    
    # 3. Preview Data
    mock_db["compounds"].find.return_value.limit.return_value = [
        {"_id": "obj123", "name": "Compound X", "density": 1.25, "active": True}
    ]
    columns, rows = await connector.preview_data("compounds", limit=5)
    assert columns == ["_id", "name", "density", "active"]
    assert len(rows) == 1
    assert rows[0][1] == "Compound X"
    
    # 4. Execute Query
    query = {
        "entity": "compounds",
        "fields": ["name", "density"],
        "filters": [
            {"field": "name", "operator": "=", "value": "Compound X"},
            {"field": "density", "operator": ">", "value": 1.0}
        ],
        "limit": 10
    }
    
    mock_db["compounds"].find.return_value.limit.return_value = [
        {"name": "Compound X", "density": 1.25}
    ]
    
    cols, q_rows = await connector.execute_query(query)
    assert cols == ["name", "density"]
    assert len(q_rows) == 1
    assert q_rows[0][0] == "Compound X"
    
    # Verify mock find was called with query structure
    mock_db["compounds"].find.assert_called()
    called_args, called_kwargs = mock_db["compounds"].find.call_args
    # First arg is filter
    assert called_args[0]["name"] == "Compound X"
    assert called_args[0]["density"] == {"$gt": 1.0}
    # Second arg is projection
    assert called_args[1]["_id"] == 0
    assert called_args[1]["name"] == 1

