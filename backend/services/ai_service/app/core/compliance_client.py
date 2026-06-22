import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("compliance_client")

AUDIT_SERVICE_URL = "http://localhost:8006/api/v1/audit/logs"
AUDIT_API_SECRET = "GENQUANTAA_AUDIT_INTERNAL_API_SECRET_2026"

def log_audit_event(
    action: str,
    service_name: str,
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    endpoint: Optional[str] = None,
    status: str = "SUCCESS",
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Optional[int]:
    payload = {
        "user_id": str(user_id) if user_id is not None else None,
        "username": username,
        "action": action,
        "service_name": service_name,
        "endpoint": endpoint,
        "status": status,
        "ip_address": ip_address,
        "details": details
    }
    headers = {
        "x-audit-secret": AUDIT_API_SECRET,
        "Content-Type": "application/json"
    }
    try:
        response = httpx.post(AUDIT_SERVICE_URL, json=payload, headers=headers, timeout=2.0)
        if response.status_code == 201:
            return response.json().get("id")
        else:
            logger.error(f"Audit log failed with status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send audit log: {str(e)}")
    return None
