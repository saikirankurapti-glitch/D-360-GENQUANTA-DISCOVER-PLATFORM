import socket

ports = {
    8001: "Auth Service",
    8002: "Metadata Service",
    8003: "Query Service",
    8004: "Cheminformatics Service",
    8005: "Connector Service",
    8006: "Audit Service",
    8007: "Lineage Service",
    8008: "Bioinformatics Service",
    8009: "Workflow Service",
    8010: "AI Service",
    5173: "Frontend App"
}

for port, name in ports.items():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    result = s.connect_ex(('127.0.0.1', port))
    if result == 0:
        print(f"Port {port} ({name}) is OPEN")
    else:
        print(f"Port {port} ({name}) is CLOSED (code: {result})")
    s.close()
