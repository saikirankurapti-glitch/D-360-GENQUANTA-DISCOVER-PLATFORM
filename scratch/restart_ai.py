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

# Kill 8003 (just in case)
kill_port(8003)

# Restart AI service
base_dir = r"c:\Users\saiki\GENQUANTAA DISCOVER"
venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
svc_dir = os.path.join(base_dir, r"backend\services\ai_service")
log_file = os.path.join(base_dir, "logs", "ai_service_restart.log")

env = os.environ.copy()
env["DATABASE_URL"] = "postgresql://postgres:Saikiran%40123@localhost:5432/genquantaa_ai"
env["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# Start service in background
cmd = f'"{venv_python}" -m uvicorn app.main:app --port 8003 --host 0.0.0.0'
print("Running command:", cmd)
with open(log_file, "w") as f:
    subprocess.Popen(cmd, shell=True, cwd=svc_dir, env=env, stdout=f, stderr=subprocess.STDOUT)

print("AI Copilot service restarted successfully!")
