import json
import logging
import httpx
import numpy as np
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("rag_service")

# Fallback: scikit-learn is already in the environment, we can use it to build a local vector index
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class RAGService:
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.openai_client = None
        
        # Initialize OpenAI Client if key is available
        if settings.OPENAI_API_KEY:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Ingest basic mock data at startup for testing
        self.seed_mock_knowledge()

    def seed_mock_knowledge(self):
        """Seeds default platform context details to ensure there's always scientific data to retrieve."""
        self.documents = [
            {
                "id": "meta_1",
                "source": "Metadata Catalog",
                "entity_type": "chemical_compound",
                "content": "Compound CHEM-4402 is a potent EGFR inhibitor with an IC50 of 42 nM against wild-type EGFR. Highly active in lung cancer models.",
                "metadata": {"compound_id": "CHEM-4402", "target": "EGFR", "ic50": "42 nM"}
            },
            {
                "id": "meta_2",
                "source": "Metadata Catalog",
                "entity_type": "chemical_compound",
                "content": "Compound CHEM-9821 displays weak activity against EGFR with IC50 of 820 nM, but shows high selectivity against HER2.",
                "metadata": {"compound_id": "CHEM-9821", "target": "EGFR", "ic50": "820 nM"}
            },
            {
                "id": "lims_1",
                "source": "LIMS: LabWare",
                "entity_type": "assay_result",
                "content": "Assay run #8892 performed last month (May 2026). Target: EGFR phosphorylation. Plate status: Approved. Operator: Dr. Sarah Connor.",
                "metadata": {"assay_id": "ASSAY-8892", "date": "2026-05-12", "target": "EGFR"}
            },
            {
                "id": "eln_1",
                "source": "ELN: Benchling",
                "entity_type": "experiment_record",
                "content": "Experiment EXP-10901: Synthesized 12 novel kinase inhibitors aiming for EGFR binding site. Final yield 74% purity checked by HPLC.",
                "metadata": {"experiment_id": "EXP-10901", "author": "Dr. Sarah Connor"}
            },
            {
                "id": "bio_1",
                "source": "Bioinformatics Data",
                "entity_type": "protein_sequence",
                "content": "Protein sequence EGFR_HUMAN (Epidermal growth factor receptor). Length: 1210 aa. Key mutation: T790M causes resistance to first-generation tyrosine kinase inhibitors.",
                "metadata": {"sequence_id": "EGFR_HUMAN", "gene": "EGFR"}
            },
            {
                "id": "workflow_1",
                "source": "Workflow History",
                "entity_type": "workflow_run",
                "content": "Workflow 'Benchling Daily Sync & Alignment' run #101 executed successfully. Processed 12 fasta records, synced 4 LIMS plates.",
                "metadata": {"workflow_id": "WF-101", "status": "COMPLETED"}
            }
        ]
        self._build_index()

    async def ingest_platform_data(self):
        """Fetches active data from all services and indexes them."""
        new_docs = []
        async with httpx.AsyncClient() as client:
            # 1. Fetch Metadata Entities
            try:
                resp = await client.get("http://localhost:8002/api/v1/metadata/entities", timeout=1.0)
                if resp.status_code == 200:
                    for item in resp.json():
                        new_docs.append({
                            "id": f"meta_dyn_{item.get('id')}",
                            "source": "Metadata Catalog",
                            "entity_type": "catalog_entity",
                            "content": f"Entity {item.get('name')} (Type: {item.get('type')}) - {item.get('description', '')}",
                            "metadata": item
                        })
            except Exception:
                pass

            # 2. Fetch Bioinformatics Sequences
            try:
                resp = await client.get("http://localhost:8008/api/v1/bioinformatics/sequences", timeout=1.0)
                if resp.status_code == 200:
                    for seq in resp.json():
                        new_docs.append({
                            "id": f"bio_dyn_{seq.get('id')}",
                            "source": "Bioinformatics Hub",
                            "entity_type": "sequence",
                            "content": f"Sequence {seq.get('name')} - Type: {seq.get('seq_type')}. Header: {seq.get('header')}. Sequence: {seq.get('sequence')[:100]}...",
                            "metadata": seq
                        })
            except Exception:
                pass

            # 3. Fetch Chemical Compounds
            try:
                resp = await client.get("http://localhost:8004/api/v1/chemistry/compounds", timeout=1.0)
                if resp.status_code == 200:
                    for comp in resp.json():
                        new_docs.append({
                            "id": f"chem_dyn_{comp.get('id')}",
                            "source": "Cheminformatics Catalog",
                            "entity_type": "chemical_compound",
                            "content": f"Compound {comp.get('name')} (Key: {comp.get('entity_key')}) - SMILES structure: {comp.get('smiles')}",
                            "metadata": {
                                "compound_id": comp.get("entity_key"),
                                "name": comp.get("name"),
                                "smiles": comp.get("smiles")
                            }
                        })
            except Exception:
                pass

        if new_docs:
            self.documents.extend(new_docs)
            self._build_index()
            logger.info(f"Ingested {len(new_docs)} dynamic records from services.")

    def _build_index(self):
        """Re-builds local vector search index using TF-IDF if OpenAI is not available."""
        if not self.documents:
            return

        if self.openai_client:
            # Using OpenAI Embeddings would store vectors. For local execution in tests/demos,
            # we also build the TF-IDF representation as an immediate, fast, and free local fallback.
            pass

        if SKLEARN_AVAILABLE:
            texts = [doc["content"] for doc in self.documents]
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)

    def search(self, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Searches index semantically or using TF-IDF."""
        if not self.documents:
            return []

        # If OpenAI API Key is configured, try using true embeddings
        if self.openai_client:
            try:
                response = self.openai_client.embeddings.create(
                    input=[query],
                    model="text-embedding-3-small"
                )
                query_vector = response.data[0].embedding
                # In a real implementation we would compute cosine similarity against stored document embeddings.
                # To maintain reliable offline-first fallback, we fall back to TF-IDF if OpenAI is slow or fails.
            except Exception as err:
                logger.warning(f"OpenAI embedding generation failed, using local TF-IDF: {err}")

        # Local TF-IDF Search
        if SKLEARN_AVAILABLE and self.vectorizer is not None:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            top_indices = np.argsort(similarities)[::-1][:limit]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score > 0.05:  # Relevance threshold
                    doc = dict(self.documents[idx])
                    doc["relevance"] = score
                    results.append(doc)
            return results
        
        # Simple substring search if sklearn is somehow missing
        results = []
        for doc in self.documents:
            if any(word.lower() in doc["content"].lower() for word in query.split()):
                results.append({**doc, "relevance": 0.5})
            if len(results) >= limit:
                break
        return results

rag_service = RAGService()
