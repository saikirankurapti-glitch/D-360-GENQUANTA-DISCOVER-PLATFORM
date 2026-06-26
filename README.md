# AnalytiX

AnalytiX is an enterprise-grade AI-Powered Scientific Intelligence Platform modeled after Certara D360 capabilities. It provides researchers with unified metadata federation, query building, cheminformatics analysis, bioinformatics sequence explorer, lineage tracking, workflow orchestration, audit trails, and an integrated AI Scientist Copilot.

---

## Architecture Overview

The platform uses a microservices-based architecture running a React frontend and 10 Python (FastAPI) backend services, communicating with a PostgreSQL database.

### Core Services
1. **Auth Service (Port 8001):** Manages user registration, JWT token generation, and role-based access control.
2. **Metadata Service (Port 8002):** Orchestrates EAV (Entity-Attribute-Value) scientific schemas and federation catalogs.
3. **Query Service (Port 8003):** Translates visual query builder trees into executable SQL templates.
4. **Cheminformatics Service (Port 8004):** Performs molecular structure searches (substructure, similarity) using RDKit.
5. **Connector Service (Port 8005):** Synchronizes database and API endpoints (LIMS, ELN, SQL, REST APIs).
6. **Audit Service (Port 8006):** Tracks all access and configuration modifications for FDA 21 CFR Part 11 compliance.
7. **Lineage Service (Port 8007):** visualizes data flow mapping from source system to final dataset representation.
8. **Bioinformatics Service (Port 8008):** Processes FASTA/FASTQ genomic sequences and renders modern Plotly alignments.
9. **Workflow Service (Port 8009):** Designs and runs multi-step scientific workflows.
10. **AI Service (Port 8010):** Powering the AI Scientist Copilot with integrated LLM and scientific context.

---

## Environment Variables (`.env`)

For local execution, the platform configuration is managed via environment variables. To configure the backend:

1. Locate the `backend/.env.example` file.
2. Copy it to a new file named `backend/.env` (which is excluded from Git tracking for security):
   ```bash
   cp backend/.env.example backend/.env
   ```
3. Set your Supabase or local PostgreSQL parameters inside `backend/.env`:

```env
# Supabase project parameters (Optional if using local PostgreSQL)
SUPABASE_PROJECT_REF=zsbcktaeasdegnihupyb
SUPABASE_URL=https://zsbcktaeasdegnihupyb.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# PostgreSQL Connection Strings
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<dbname>
DATABASE_URL_ASYNC=postgresql+asyncpg://<username>:<password>@<host>:<port>/<dbname>

# FastAPI settings
ENVIRONMENT=development
PORT=8000

# JWT secret for auth service
AUTH_SECRET_KEY=CHANGE_ME_TO_RANDOM_64_CHAR_STRING

# OpenAI API key (for AI Scientist Copilot Service)
OPENAI_API_KEY=your_openai_api_key
```

---

## How to Run the Platform

### Option A: Automatically Run Everything (Windows PowerShell)

A startup PowerShell script is provided to automate port cleanup, environment injection, microservice launch, and Vite dev server initialization.

Run the following command from the project root:
```powershell
.\start_services.ps1
```

*Note: This script boots all 10 microservices, maps their logs to `./logs/*.log`, and serves the React App on [http://localhost:5173](http://localhost:5173).*

---

### Option B: Manually Run Services

If you prefer to start services individually:

#### 1. Setup Backend Environment
- Ensure PostgreSQL is running (default port `5432`).
- Setup your Python virtual environment inside the project root:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  pip install -r backend/requirements.txt  # If requirements.txt exists
  ```
- To run any microservice (e.g., Auth Service):
  ```bash
  cd backend/services/auth_service
  uvicorn app.main:app --port 8001 --reload
  ```
  *(Repeat for other services on ports 8002 - 8010)*

#### 2. Setup Frontend Environment
- Navigate to the frontend directory:
  ```bash
  cd frontend
  npm install
  npm run dev
  ```
- The React App will launch on [http://localhost:5173](http://localhost:5173).

---

## Default Login Credentials

Use the following default administrator credentials to log into the platform locally:

- **Username:** `admin@analytix.com`
- **Password:** `AnalytiXDiscover2026!`
