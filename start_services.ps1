# start_services.ps1
# GENQUANTAA Discover - All services use local PostgreSQL (port 5432)
# Each service gets its own dedicated database.

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $baseDir ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment Python executable not found at: $venvPython"
    exit 1
}

# == Local PostgreSQL connection strings ======================================
$PG_HOST = "localhost"
$PG_PORT = "5432"
$PG_USER = "postgres"
$PG_PASS = "Saikiran%40123"   # URL-encoded: @ → %40 (required in connection strings)

$DB_AUTH        = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_auth"
$DB_METADATA    = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_metadata"
$DB_QUERY       = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_query"
$DB_CHEM        = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/cheminformatics"
$DB_CONNECTOR   = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_connector"
$DB_AUDIT       = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_audit"
$DB_LINEAGE     = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_lineage"
$DB_BIOINFO     = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_bioinfo"
$DB_WORKFLOW    = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_workflow"
$DB_AI          = "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/genquantaa_ai"

# == Helper: start a service in the background and redirect output to a log ============
function Start-Service-Window($serviceName, $port, $dirName, $envVars) {
    Write-Host "Starting $serviceName on port $port..." -ForegroundColor Cyan

    # Ensure logs directory exists
    $logDir = Join-Path $baseDir "logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    $logFile = Join-Path $logDir "$($serviceName.Replace(' ', '_').ToLower()).log"

    # Build environment variable SET commands for cmd.exe without trailing spaces
    $envCmds = ""
    foreach ($kv in $envVars.GetEnumerator()) {
        $envCmds += "SET $($kv.Key)=$($kv.Value)&&"
    }

    $svcDir = Join-Path $baseDir "backend\services\$dirName"
    Start-Process "cmd.exe" -ArgumentList "/c cd /d `"$svcDir`" && ${envCmds}`"$venvPython`" -m uvicorn app.main:app --port $port --host 0.0.0.0 > `"$logFile`" 2>&1" -NoNewWindow
}

Write-Host "Cleaning up ports 8001-8010, 5173, 5174 using Python..." -ForegroundColor Yellow
& "$venvPython" -c "def k(p):
    try:
        import os; os.kill(p, 15)
    except:
        pass
import subprocess, re
output = subprocess.check_output(['netstat', '-ano'], text=True)
pids = {int(parts[4]) for line in output.splitlines() if 'LISTENING' in line for parts in [re.split(r'\s+', line.strip())] if len(parts) >= 5 and re.search(r':(800[1-9]|8010|5173|5174)$', parts[1])}
[k(pid) for pid in pids if pid > 0]"
Start-Sleep -Seconds 1

# == 1. Auth Service (8001) ====================================================
Start-Service-Window "Auth Service" 8001 "auth_service" @{
    "DATABASE_URL" = $DB_AUTH
    "SECRET_KEY"   = "SUPER_SECRET_SCIENTIFIC_PLATFORM_KEY_2026"
    "ALLOWED_ORIGINS" = "http://localhost:5173,http://localhost:5174,http://localhost:3000"
}

# == 2. Metadata Service (8002) ================================================
Start-Service-Window "Metadata Service" 8002 "metadata_service" @{
    "DATABASE_URL" = $DB_METADATA
}

# == 3. Query Service (8003) ==================================================-
Start-Service-Window "Query Service" 8003 "query_service" @{
    "DATABASE_URL" = $DB_QUERY
}

# == 4. Cheminformatics Service (8004) ========================================-
Start-Service-Window "Cheminformatics Service" 8004 "cheminformatics_service" @{
    "DATABASE_URL" = $DB_CHEM
}

# == 5. Connector Service (8005) ==============================================-
Start-Service-Window "Connector Service" 8005 "connector_service" @{
    "DATABASE_URL"   = $DB_CONNECTOR
    "ENCRYPTION_KEY" = "351F6FEE44C2BD56A11D36982DB5F11F351F6FEE44C2BD56A11D36982DB5F11F"
}

# == 6. Audit Service (8006) ==================================================-
Start-Service-Window "Audit Service" 8006 "audit_service" @{
    "DATABASE_URL"     = $DB_AUDIT
    "AUDIT_API_SECRET" = "GENQUANTAA_AUDIT_INTERNAL_API_SECRET_2026"
}

# == 7. Lineage Service (8007) ================================================-
Start-Service-Window "Lineage Service" 8007 "lineage_service" @{
    "DATABASE_URL" = $DB_LINEAGE
}

# == 8. Bioinformatics Service (8008) ========================================-
Start-Service-Window "Bioinformatics Service" 8008 "bioinformatics_service" @{
    "DATABASE_URL" = $DB_BIOINFO
}

# == 9. Workflow Service (8009) ================================================
Start-Service-Window "Workflow Service" 8009 "workflow_service" @{
    "DATABASE_URL" = $DB_WORKFLOW
}

# == 10. AI Service (8010) ====================================================-
Start-Service-Window "AI Service" 8010 "ai_service" @{
    "DATABASE_URL"     = $DB_AI
    "AUDIT_API_SECRET" = "GENQUANTAA_AUDIT_INTERNAL_API_SECRET_2026"
}

# == 11. Frontend Dev Server (5173) ============================================
Write-Host "Starting Frontend Dev Server..." -ForegroundColor Green
$frontDir = Join-Path $baseDir "frontend"
$frontLog = Join-Path $baseDir "logs\frontend.log"
Start-Process "cmd.exe" -ArgumentList "/c cd /d `"$frontDir`" && npm run dev > `"$frontLog`" 2>&1" -NoNewWindow

# == Summary ==================================================================-
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host " GENQUANTAA DISCOVER - All Services Launching" -ForegroundColor White
Write-Host "  Database: Local PostgreSQL @ localhost:5432" -ForegroundColor Magenta
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  Auth API:            http://localhost:8001/docs" -ForegroundColor Gray
Write-Host "  Metadata API:        http://localhost:8002/docs" -ForegroundColor Gray
Write-Host "  Query API:           http://localhost:8003/docs" -ForegroundColor Gray
Write-Host "  Cheminformatics API: http://localhost:8004/docs" -ForegroundColor Gray
Write-Host "  Connector API:       http://localhost:8005/docs" -ForegroundColor Gray
Write-Host "  Audit API:           http://localhost:8006/docs" -ForegroundColor Gray
Write-Host "  Lineage API:         http://localhost:8007/docs" -ForegroundColor Gray
Write-Host "  Bioinformatics API:  http://localhost:8008/docs" -ForegroundColor Gray
Write-Host "  Workflow API:        http://localhost:8009/docs" -ForegroundColor Gray
Write-Host "  AI API:              http://localhost:8010/docs" -ForegroundColor Gray
Write-Host "  Frontend App:        http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "  Default Login: admin@genquantaa.com / GenQuantaaDiscover2026!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Each service runs in its own console window." -ForegroundColor DarkGray
Write-Host "Wait 10s for all services to fully start." -ForegroundColor DarkGray
