import subprocess
import re
import os
import time

def kill_port(port):
    try:
        output = subprocess.check_output(['netstat', '-ano'], text=True)
        for line in output.splitlines():
            if 'LISTENING' in line and f':{port}' in line:
                parts = re.split(r'\s+', line.strip())
                pid = int(parts[-1])
                print(f"Killing process {pid} on port {port}")
                os.kill(pid, 9)
                time.sleep(1)
                return True
    except Exception as e:
        print(f"Error killing port {port}: {e}")
    return False

# Kill 8003 and 8010
kill_port(8003)
kill_port(8010)

base_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER"
venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")

# 1. Restart Query Service on Port 8003
query_dir = os.path.join(base_dir, r"backend\services\query_service")
query_log = os.path.join(base_dir, "logs", "query_service_restart.log")
query_env = os.environ.copy()
query_env["DATABASE_URL"] = "postgresql://postgres:Saikiran%40123@localhost:5432/genquantaa_query"

cmd_query = f'"{venv_python}" -m uvicorn app.main:app --port 8003 --host 0.0.0.0'
print("Starting Query Service on 8003...")
with open(query_log, "w") as f:
    subprocess.Popen(cmd_query, shell=True, cwd=query_dir, env=query_env, stdout=f, stderr=subprocess.STDOUT)

# 2. Restart AI Service on Port 8010
ai_dir = os.path.join(base_dir, r"backend\services\ai_service")
ai_log = os.path.join(base_dir, "logs", "ai_service_restart.log")
ai_env = os.environ.copy()
ai_env["DATABASE_URL"] = "postgresql://postgres:Saikiran%40123@localhost:5432/genquantaa_ai"
ai_env["AUDIT_API_SECRET"] = "AnalytiX_AUDIT_INTERNAL_API_SECRET_2026"
ai_env["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

cmd_ai = f'"{venv_python}" -m uvicorn app.main:app --port 8010 --host 0.0.0.0'
print("Starting AI Service on 8010...")
with open(ai_log, "w") as f:
    subprocess.Popen(cmd_ai, shell=True, cwd=ai_dir, env=ai_env, stdout=f, stderr=subprocess.STDOUT)

print("Services successfully realigned and restarted!")
