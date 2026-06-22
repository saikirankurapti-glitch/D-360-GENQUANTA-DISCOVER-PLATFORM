import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app

# Database setup for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_bioinfo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def override_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides.clear()

client = TestClient(app)

# Sample FASTA files data
SAMPLE_SINGLE_FASTA = """>SEQ1 DNA sequence test
ATGCTAGCTAGCTAGCTAGCTAGC"""

SAMPLE_MULTI_FASTA = """>SEQ1 DNA seq
ATGCTAGCTAGCTAGCTAGC
>SEQ2 RNA seq
AUGCUAGCUAGCUAGCUAGC
>SEQ3 Protein seq
MTEITAAMVKELRESTGAGMMD"""

def test_import_fasta():
    # 1. Single FASTA
    response = client.post("/api/v1/sequences/import", json={"fasta_data": SAMPLE_SINGLE_FASTA})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sequence_id"] == "SEQ1"
    assert data[0]["sequence_type"] == "DNA"

    # 2. Multi FASTA
    response = client.post("/api/v1/sequences/import", json={"fasta_data": SAMPLE_MULTI_FASTA})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Assert correct type detection
    assert data[0]["sequence_type"] == "DNA"
    assert data[1]["sequence_type"] == "RNA"
    assert data[2]["sequence_type"] == "Protein"

def test_get_sequence_metrics():
    # Setup sequences
    client.post("/api/v1/sequences/import", json={"fasta_data": SAMPLE_MULTI_FASTA})
    
    # 1. DNA metrics
    res_dna = client.get("/api/v1/sequences/SEQ1/metrics")
    assert res_dna.status_code == 200
    dna_data = res_dna.json()
    assert dna_data["type"] == "DNA"
    assert dna_data["length"] == 20
    assert "gc_content" in dna_data
    
    # 2. Protein metrics
    res_prot = client.get("/api/v1/sequences/SEQ3/metrics")
    assert res_prot.status_code == 200
    prot_data = res_prot.json()
    assert prot_data["type"] == "Protein"
    assert prot_data["length"] == 22
    assert prot_data["molecular_weight"] > 0.0
    assert prot_data["isoelectric_point"] > 0.0

def test_pairwise_alignment():
    client.post("/api/v1/sequences/import", json={"fasta_data": SAMPLE_MULTI_FASTA})
    
    payload = {
        "seq_a_id": "SEQ1",
        "seq_b_id": "SEQ1",
        "alignment_type": "global"
    }
    response = client.post("/api/v1/alignments/pairwise", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert data["score"] == 20.0 # identical matches for length 20

def test_multiple_alignment():
    client.post("/api/v1/sequences/import", json={"fasta_data": SAMPLE_MULTI_FASTA})
    
    payload = {
        "seq_ids": ["SEQ1", "SEQ2"]
    }
    response = client.post("/api/v1/alignments/multiple", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "clustal" in data
    assert "consensus" in data

def test_sequence_search():
    client.post("/api/v1/sequences/import", json={"fasta_data": SAMPLE_MULTI_FASTA})
    
    # Exact search
    payload = {
        "query_string": "ATGCT",
        "search_type": "exact"
    }
    response = client.post("/api/v1/search/sequence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["sequence_id"] == "SEQ1"

    # Motif search
    payload = {
        "query_string": "MTE",
        "search_type": "motif"
    }
    response = client.post("/api/v1/search/sequence", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sequence_id"] == "SEQ3"

def test_clustering():
    # Setup some test sequences
    fasta_seqs = """>S1
ATGCTAGCTAGC
>S2
ATGCTAGCTAGG
>S3
ATGCAAGCTAGC"""
    client.post("/api/v1/sequences/import", json={"fasta_data": fasta_seqs})
    
    payload = {
        "name": "Clustering Test Run",
        "seq_ids": ["S1", "S2", "S3"],
        "method": "hierarchical",
        "distance_metric": "identity"
    }
    response = client.post("/api/v1/clusters", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Clustering Test Run"
    assert "matrix_json" in data
    assert "linkage_json" in data
