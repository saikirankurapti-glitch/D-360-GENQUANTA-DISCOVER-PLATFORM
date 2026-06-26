/**
 * AnalytiX Discover – k6 Load Test Suite
 * ==========================================
 * Supplemental load test using k6 for precise scenario control.
 * 
 * Tests:
 *   Stage 1: Ramp to 100 users (2 min)
 *   Stage 2: Hold 100 users (5 min)
 *   Stage 3: Ramp to 500 users (3 min)
 *   Stage 4: Hold 500 users (5 min)
 *   Stage 5: Ramp to 1000 users (5 min)
 *   Stage 6: Hold 1000 users (5 min)
 *   Stage 7: Ramp down (2 min)
 *
 * Run:
 *   k6 run --out json=results/k6_results.json k6_load_test.js
 *
 * Thresholds (SLOs):
 *   - p95 response time < 2000ms
 *   - p99 response time < 5000ms
 *   - Error rate < 1%
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomItem, randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

// --------------------------------------------------------------------------
// Custom Metrics
// --------------------------------------------------------------------------
const authLatency = new Trend('auth_latency', true);
const queryLatency = new Trend('query_latency', true);
const chemLatency = new Trend('chem_latency', true);
const aiLatency = new Trend('ai_latency', true);
const workflowLatency = new Trend('workflow_latency', true);
const errorRate = new Rate('error_rate');

// --------------------------------------------------------------------------
// Test Configuration
// --------------------------------------------------------------------------
export const options = {
  stages: [
    { duration: '2m',  target: 100 },   // Ramp to 100
    { duration: '5m',  target: 100 },   // Hold 100
    { duration: '3m',  target: 500 },   // Ramp to 500
    { duration: '5m',  target: 500 },   // Hold 500
    { duration: '5m',  target: 1000 },  // Ramp to 1000
    { duration: '5m',  target: 1000 },  // Hold 1000
    { duration: '2m',  target: 0 },     // Ramp down
  ],
  thresholds: {
    // SLO: p95 < 2s, p99 < 5s
    'http_req_duration': ['p(95)<2000', 'p(99)<5000'],
    // Per-service latency thresholds
    'auth_latency': ['p(95)<1000'],
    'query_latency': ['p(95)<2000'],
    'chem_latency': ['p(95)<3000'],
    'ai_latency': ['p(95)<10000'],
    'workflow_latency': ['p(95)<3000'],
    // Error rate < 1%
    'error_rate': ['rate<0.01'],
    // Request failure rate
    'http_req_failed': ['rate<0.01'],
  },
  ext: {
    loadimpact: {
      projectID: 0,
      name: 'AnalytiX Discover Load Test',
    },
  },
};

// --------------------------------------------------------------------------
// Test Data
// --------------------------------------------------------------------------
const SMILES_LIST = [
  'CC(=O)Oc1ccccc1C(=O)O',         // Aspirin
  'CN1C=NC2=C1C(=O)N(C(=O)N2C)C', // Caffeine
  'CC(C)Cc1ccc(cc1)C(C)C(=O)O',   // Ibuprofen
  'c1ccc2c(c1)ccc3cccc4ccc2c34',   // Pyrene
];

const AUTH_URL        = 'http://localhost:8001';
const METADATA_URL    = 'http://localhost:8002';
const QUERY_URL       = 'http://localhost:8003';
const CHEM_URL        = 'http://localhost:8004';
const CONNECTOR_URL   = 'http://localhost:8005';
const AUDIT_URL       = 'http://localhost:8006';
const LINEAGE_URL     = 'http://localhost:8007';
const BIO_URL         = 'http://localhost:8008';
const WORKFLOW_URL    = 'http://localhost:8009';
const AI_URL          = 'http://localhost:8010';

// --------------------------------------------------------------------------
// Authentication
// --------------------------------------------------------------------------
function login() {
  const params = new URLSearchParams();
  params.append('username', 'scientist@analytix.com');
  params.append('password', 'ScientistPass123!');

  const start = Date.now();
  const resp = http.post(
    `${AUTH_URL}/api/v1/auth/login`,
    params.toString(),
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  authLatency.add(Date.now() - start);

  const success = check(resp, {
    'login status 200': (r) => r.status === 200,
    'has access_token': (r) => r.json('access_token') !== undefined,
  });
  errorRate.add(!success);

  if (resp.status === 200) {
    return resp.json('access_token');
  }
  return null;
}

// --------------------------------------------------------------------------
// Main Virtual User Scenario
// --------------------------------------------------------------------------
export default function () {
  // Login
  const token = login();
  if (!token) {
    sleep(1);
    return;
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  sleep(randomIntBetween(1, 2));

  // --- Metadata Catalog ---
  group('Metadata Catalog', () => {
    const resp = http.get(`${METADATA_URL}/api/v1/datasets`, { headers });
    const ok = check(resp, { 'metadata 200': (r) => r.status === 200 });
    errorRate.add(!ok);
  });

  sleep(randomIntBetween(1, 2));

  // --- Chemistry Operations ---
  group('Chemistry', () => {
    const smiles = randomItem(SMILES_LIST);
    const start = Date.now();

    // Similarity search
    const simResp = http.post(
      `${CHEM_URL}/api/v1/chemistry/similarity`,
      JSON.stringify({ smiles, threshold: 0.7, limit: 20 }),
      { headers }
    );
    chemLatency.add(Date.now() - start);
    const simOk = check(simResp, { 'similarity 200': (r) => r.status === 200 });
    errorRate.add(!simOk);

    sleep(1);

    // Properties
    const propResp = http.post(
      `${CHEM_URL}/api/v1/chemistry/properties`,
      JSON.stringify({ smiles }),
      { headers }
    );
    const propOk = check(propResp, { 'properties 200': (r) => r.status === 200 });
    errorRate.add(!propOk);
  });

  sleep(randomIntBetween(1, 3));

  // --- Query Service ---
  group('Query Federation', () => {
    const start = Date.now();
    const resp = http.get(`${QUERY_URL}/api/v1/query/templates`, { headers });
    queryLatency.add(Date.now() - start);
    const ok = check(resp, { 'query templates 200': (r) => r.status === 200 });
    errorRate.add(!ok);
  });

  sleep(randomIntBetween(1, 2));

  // --- Workflow ---
  group('Workflows', () => {
    const start = Date.now();
    const resp = http.get(`${WORKFLOW_URL}/api/v1/workflow/workflows`, { headers });
    workflowLatency.add(Date.now() - start);
    const ok = check(resp, { 'workflow list 200': (r) => r.status === 200 });
    errorRate.add(!ok);
  });

  // --- AI Copilot (1 in 5 users) ---
  if (randomIntBetween(1, 5) === 1) {
    group('AI Copilot', () => {
      const questions = [
        'What are the key ADMET properties to consider for drug candidates?',
        'Explain Lipinski Rule of Five.',
        'What is the role of cytochrome P450 in drug metabolism?',
      ];
      const start = Date.now();
      const resp = http.post(
        `${AI_URL}/api/v1/copilot/chat`,
        JSON.stringify({
          session_id: `k6-${__VU}-${__ITER}`,
          message: randomItem(questions),
        }),
        { headers, timeout: '30s' }
      );
      aiLatency.add(Date.now() - start);
      const ok = check(resp, { 'ai copilot 200': (r) => r.status === 200 });
      errorRate.add(!ok);
    });
  }

  sleep(randomIntBetween(2, 5));
}

// --------------------------------------------------------------------------
// Setup (runs once before test)
// --------------------------------------------------------------------------
export function setup() {
  console.log('AnalytiX Discover Load Test – Setup');
  // Verify services are reachable
  const services = [
    { name: 'auth',     url: `${AUTH_URL}/health` },
    { name: 'metadata', url: `${METADATA_URL}/health` },
    { name: 'query',    url: `${QUERY_URL}/health` },
    { name: 'chem',     url: `${CHEM_URL}/health` },
    { name: 'workflow', url: `${WORKFLOW_URL}/health` },
    { name: 'ai',       url: `${AI_URL}/health` },
  ];

  for (const svc of services) {
    const resp = http.get(svc.url);
    if (resp.status !== 200) {
      console.warn(`⚠ ${svc.name} not healthy (${resp.status})`);
    } else {
      console.log(`✓ ${svc.name} healthy`);
    }
  }
}

// --------------------------------------------------------------------------
// Teardown (runs once after test)
// --------------------------------------------------------------------------
export function teardown(data) {
  console.log('AnalytiX Discover Load Test – Complete');
}
