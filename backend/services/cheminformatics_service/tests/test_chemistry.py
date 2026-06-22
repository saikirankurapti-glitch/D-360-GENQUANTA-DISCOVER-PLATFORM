# tests/test_chemistry.py
import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_and_get_compound(client: TestClient):
    # Test valid compound creation (Aspirin)
    payload = {
        "entity_key": "COMP-001",
        "name": "Aspirin",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O"
    }
    response = client.post("/api/v1/compounds", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["entity_key"] == "COMP-001"
    assert data["name"] == "Aspirin"
    assert "smiles" in data
    
    # Check duplicate prevention
    response = client.post("/api/v1/compounds", json=payload)
    assert response.status_code == 400
    
    # Retrieve compound
    response = client.get("/api/v1/compounds/COMP-001")
    assert response.status_code == 200
    assert response.json()["name"] == "Aspirin"

def test_create_compound_invalid_smiles(client: TestClient):
    # Test invalid SMILES
    payload = {
        "entity_key": "COMP-999",
        "name": "Invalid Molecule",
        "smiles": "CC(=O)Oc1ccccc1C(=O)OXXXX"
    }
    response = client.post("/api/v1/compounds", json=payload)
    assert response.status_code == 422 # Pydantic validation error

def test_get_descriptors(client: TestClient):
    # Benzene
    response = client.get("/api/v1/descriptors", params={"smiles": "c1ccccc1"})
    assert response.status_code == 200
    data = response.json()
    assert data["formula"] == "C6H6"
    assert data["heavy_atoms"] == 6
    assert abs(data["mw"] - 78.0) < 1.0
    assert data["rotatable_bonds"] == 0

def test_get_fingerprints(client: TestClient):
    response = client.get("/api/v1/fingerprints", params={"smiles": "c1ccccc1"})
    assert response.status_code == 200
    data = response.json()
    assert "fingerprint_hex" in data
    assert len(data["fingerprint_hex"]) > 0

def test_draw_molecule(client: TestClient):
    response = client.get("/api/v1/draw", params={"smiles": "c1ccccc1"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    assert "<svg" in response.text
    assert "</svg>" in response.text

def test_chemical_searches(client: TestClient):
    # Insert test dataset (Benzene and Phenol)
    client.post("/api/v1/compounds", json={
        "entity_key": "COMP-B", "name": "Benzene", "smiles": "c1ccccc1"
    })
    client.post("/api/v1/compounds", json={
        "entity_key": "COMP-P", "name": "Phenol", "smiles": "Oc1ccccc1"
    })

    # 1. Exact Search
    response = client.get("/api/v1/search", params={"smiles": "C1=CC=CC=C1", "type": "exact"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["entity_key"] == "COMP-B"

    # 2. Substructure Search (query Benzene inside Phenol and Benzene)
    response = client.get("/api/v1/search", params={"smiles": "c1ccccc1", "type": "substructure"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2 # both contain benzene ring

    # 3. Similarity Search (Phenol query compared to Benzene/Phenol)
    response = client.get("/api/v1/search", params={"smiles": "Oc1ccccc1", "type": "similarity", "threshold": 0.4})
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert results[0]["entity_key"] == "COMP-P"
    assert results[0]["similarity"] == 1.0  # Perfect self similarity

def test_sar_analysis(client: TestClient):
    # Scaffold: Benzene ring
    scaffold = "c1ccccc1"
    
    # Analogues: Toluene, Phenol, Chlorobenzene, Aniline
    compounds = [
        {"smiles": "Cc1ccccc1", "activity": 50.0, "name": "Toluene"},      # R1 = Me
        {"smiles": "Oc1ccccc1", "activity": 1.0, "name": "Phenol"},        # R1 = OH (High activity)
        {"smiles": "Clc1ccccc1", "activity": 55.0, "name": "Chlorobenzene"},# R1 = Cl
        {"smiles": "Nc1ccccc1", "activity": 100.0, "name": "Aniline"}      # R1 = NH2
    ]
    
    payload = {
        "scaffold_smiles": scaffold,
        "compounds": compounds
    }
    
    response = client.post("/api/v1/sar", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["scaffold"] == scaffold
    assert len(data["compounds"]) == 4
    
    # Confirm R-groups are decomposed (Toluene should have R1 = [H] or -CH3 depending on query core)
    # The output should show chemical variations
    assert "r_groups" in data["compounds"][0]
    
    # Confirm activity cliffs are detected
    # Phenol (1.0) compared to Aniline (100.0) represents a 100x shift, which exceeds 10-fold cliff threshold
    assert len(data["activity_cliffs"]) > 0
    cliffs = data["activity_cliffs"]
    assert any(c["compound_a"] == "Phenol" or c["compound_b"] == "Phenol" for c in cliffs)
