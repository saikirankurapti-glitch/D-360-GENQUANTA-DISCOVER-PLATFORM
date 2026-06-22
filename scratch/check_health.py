import urllib.request
import json
import socket

ports = {
    8001: "Auth",
    8002: "Metadata",
    8003: "Query",
    8004: "Cheminformatics",
    8005: "Connector",
    8006: "Audit",
    8007: "Lineage",
    8008: "Bioinformatics",
    8009: "Workflow",
    8010: "AI",
    5173: "Frontend"
}

for port, name in ports.items():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    result = s.connect_ex(('127.0.0.1', port))
    if result == 0:
        print(f"Port {port} ({name}) is OPEN.")
        if port != 5173:
            try:
                # read health or root
                url = f"http://localhost:{port}/"
                with urllib.request.urlopen(url, timeout=1.0) as response:
                    data = response.read().decode('utf-8')
                    print(f"  Response: {data}")
            except Exception as e:
                print(f"  Failed health check: {e}")
    else:
        print(f"Port {port} ({name}) is CLOSED.")
    s.close()
