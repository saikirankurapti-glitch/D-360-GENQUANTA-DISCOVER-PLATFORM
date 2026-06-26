"""
AnalytiX – Load Testing Suite
=========================================
Uses Locust to simulate concurrent scientific platform users.

Test Scenarios:
  • AuthenticatedUser  – Full workflow: login → query → analyze
  • ScientistUser      – Heavy chemistry + bioinformatics operations
  • AdminUser          – Audit + lineage queries
  • AIUser             – AI Copilot interactions

Targets: 100 / 500 / 1000 concurrent users

Run:
  locust -f load_tests/locustfile.py --host http://localhost:8001 \\
         --users 100 --spawn-rate 10 --run-time 5m --headless \\
         --csv results/load_100users

Generate capacity report:
  python load_tests/capacity_report.py --csv-prefix results/load_
"""

import json
import random
import string
from locust import HttpUser, task, between, events, tag
from locust.contrib.fasthttp import FastHttpUser


# --------------------------------------------------------------------------- #
# Shared test data
# --------------------------------------------------------------------------- #
TEST_SMILES = [
    "CC(=O)Oc1ccccc1C(=O)O",           # Aspirin
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",    # Caffeine
    "CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C",  # Testosterone
    "c1ccc2c(c1)cc1ccc3cccc4ccc2c1c34", # Pyrene
    "CC(C)Cc1ccc(cc1)C(C)C(=O)O",       # Ibuprofen
]

TEST_SEQUENCES = [
    "ATGCGATCGATCGATCG",
    "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGEDEDtokenizedthis",
]


def random_suffix(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


# --------------------------------------------------------------------------- #
# Base User with Auth
# --------------------------------------------------------------------------- #
class BaseDiscoverUser(HttpUser):
    abstract = True
    wait_time = between(1, 3)
    _token = None

    def on_start(self):
        """Login and store JWT token."""
        suffix = random_suffix()
        resp = self.client.post(
            "http://localhost:8001/api/v1/auth/login",
            data={"username": "scientist@analytix.com", "password": "ScientistPass123!"},
            name="AUTH: Login"
        )
        if resp.status_code == 200:
            self._token = resp.json().get("access_token")
        else:
            # Try demo user
            resp2 = self.client.post(
                "http://localhost:8001/api/v1/auth/login",
                data={"username": "admin@analytix.com", "password": "AdminPass123!"},
                name="AUTH: Login (Admin fallback)"
            )
            if resp2.status_code == 200:
                self._token = resp2.json().get("access_token")

    def auth_headers(self) -> dict:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}


# --------------------------------------------------------------------------- #
# Scenario 1: General Scientist User
# --------------------------------------------------------------------------- #
class ScientistUser(BaseDiscoverUser):
    """Simulates a drug discovery scientist using all major platform features."""
    weight = 60  # 60% of load

    @task(3)
    @tag("metadata")
    def browse_catalog(self):
        self.client.get(
            "http://localhost:8002/api/v1/datasets",
            headers=self.auth_headers(),
            name="METADATA: List datasets"
        )

    @task(4)
    @tag("query")
    def run_query(self):
        template_ids = [1, 2, 3]
        self.client.get(
            f"http://localhost:8003/api/v1/query/templates",
            headers=self.auth_headers(),
            name="QUERY: List templates"
        )

    @task(3)
    @tag("chemistry")
    def similarity_search(self):
        smiles = random.choice(TEST_SMILES)
        self.client.post(
            "http://localhost:8004/api/v1/chemistry/similarity",
            json={"smiles": smiles, "threshold": 0.7, "limit": 20},
            headers=self.auth_headers(),
            name="CHEM: Similarity search"
        )

    @task(2)
    @tag("chemistry")
    def substructure_search(self):
        smiles = random.choice(TEST_SMILES)
        self.client.post(
            "http://localhost:8004/api/v1/chemistry/substructure",
            json={"smarts": smiles, "limit": 50},
            headers=self.auth_headers(),
            name="CHEM: Substructure search"
        )

    @task(1)
    @tag("chemistry")
    def calculate_properties(self):
        smiles = random.choice(TEST_SMILES)
        self.client.post(
            "http://localhost:8004/api/v1/chemistry/properties",
            json={"smiles": smiles},
            headers=self.auth_headers(),
            name="CHEM: Calculate properties"
        )

    @task(2)
    @tag("workflow")
    def list_workflows(self):
        self.client.get(
            "http://localhost:8009/api/v1/workflow/workflows",
            headers=self.auth_headers(),
            name="WORKFLOW: List workflows"
        )

    @task(1)
    @tag("lineage")
    def check_lineage(self):
        self.client.get(
            "http://localhost:8007/api/v1/lineage/graph",
            headers=self.auth_headers(),
            name="LINEAGE: Get graph"
        )


# --------------------------------------------------------------------------- #
# Scenario 2: Bioinformatics User
# --------------------------------------------------------------------------- #
class BioinformaticsUser(BaseDiscoverUser):
    """Simulates a bioinformatics researcher."""
    weight = 25  # 25% of load

    @task(3)
    @tag("bioinformatics")
    def sequence_search(self):
        seq = random.choice(TEST_SEQUENCES)
        self.client.post(
            "http://localhost:8008/api/v1/bioinformatics/blast",
            json={"sequence": seq[:100], "program": "blastn", "database": "nt"},
            headers=self.auth_headers(),
            name="BIO: BLAST search"
        )

    @task(2)
    @tag("bioinformatics")
    def list_sequences(self):
        self.client.get(
            "http://localhost:8008/api/v1/bioinformatics/sequences",
            headers=self.auth_headers(),
            name="BIO: List sequences"
        )

    @task(2)
    @tag("bioinformatics")
    def protein_analysis(self):
        self.client.post(
            "http://localhost:8008/api/v1/bioinformatics/analyze",
            json={"sequence": TEST_SEQUENCES[1][:50], "sequence_type": "protein"},
            headers=self.auth_headers(),
            name="BIO: Protein analysis"
        )

    @task(1)
    @tag("ai")
    def ai_question(self):
        questions = [
            "What are the key physicochemical properties of aspirin?",
            "Explain the mechanism of action of caffeine.",
            "What is the significance of Lipinski's Rule of Five?",
        ]
        self.client.post(
            "http://localhost:8010/api/v1/copilot/chat",
            json={
                "session_id": f"load-test-{random_suffix()}",
                "message": random.choice(questions)
            },
            headers=self.auth_headers(),
            name="AI: Copilot question",
            timeout=30
        )


# --------------------------------------------------------------------------- #
# Scenario 3: Admin / Audit User
# --------------------------------------------------------------------------- #
class AdminUser(BaseDiscoverUser):
    """Simulates platform admin checking audit logs and system health."""
    weight = 15  # 15% of load

    def on_start(self):
        resp = self.client.post(
            "http://localhost:8001/api/v1/auth/login",
            data={"username": "admin@analytix.com", "password": "AdminPass123!"},
            name="AUTH: Admin login"
        )
        if resp.status_code == 200:
            self._token = resp.json().get("access_token")

    @task(3)
    @tag("audit")
    def audit_logs(self):
        self.client.get(
            "http://localhost:8006/api/v1/audit/logs?limit=50",
            headers=self.auth_headers(),
            name="AUDIT: Get logs"
        )

    @task(2)
    @tag("connector")
    def list_connectors(self):
        self.client.get(
            "http://localhost:8005/api/v1/connector/connectors",
            headers=self.auth_headers(),
            name="CONNECTOR: List connectors"
        )

    @task(1)
    @tag("metadata")
    def check_datasets(self):
        self.client.get(
            "http://localhost:8002/api/v1/datasets",
            headers=self.auth_headers(),
            name="METADATA: List datasets (admin)"
        )

    @task(1)
    @tag("health")
    def check_service_health(self):
        services = [8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010]
        port = random.choice(services)
        self.client.get(
            f"http://localhost:{port}/health",
            name="HEALTH: Service health check"
        )


# --------------------------------------------------------------------------- #
# Event hooks for custom reporting
# --------------------------------------------------------------------------- #
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "="*60)
    print("AnalytiX – Load Test Starting")
    print(f"Target: {environment.host}")
    print("="*60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    stats = environment.stats
    print("\n" + "="*60)
    print("AnalytiX – Load Test Complete")
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Failures:       {stats.total.num_failures}")
    print(f"Failure rate:   {stats.total.fail_ratio:.2%}")
    print(f"Avg latency:    {stats.total.avg_response_time:.0f}ms")
    print(f"p50 latency:    {stats.total.get_response_time_percentile(0.5):.0f}ms")
    print(f"p95 latency:    {stats.total.get_response_time_percentile(0.95):.0f}ms")
    print(f"p99 latency:    {stats.total.get_response_time_percentile(0.99):.0f}ms")
    print(f"Max latency:    {stats.total.max_response_time:.0f}ms")
    print(f"RPS:            {stats.total.current_rps:.1f}")
    print("="*60 + "\n")
