import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("compliance_client")

AUDIT_SERVICE_URL = "http://localhost:8006/api/v1/audit/logs"
VERSION_SERVICE_URL = "http://localhost:8006/api/v1/compliance/versions"
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

def log_entity_version(
    entity_type: str,
    entity_id: str,
    data_json: str,
    modified_by: str,
    change_summary: Optional[str] = None,
    is_deleted: int = 0,
    audit_log_id: Optional[int] = None
):
    payload = {
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "data_json": data_json,
        "modified_by": modified_by,
        "change_summary": change_summary,
        "is_deleted": is_deleted,
        "audit_log_id": audit_log_id
    }
    headers = {
        "x-audit-secret": AUDIT_API_SECRET,
        "Content-Type": "application/json"
    }
    try:
        response = httpx.post(VERSION_SERVICE_URL, json=payload, headers=headers, timeout=2.0)
        if response.status_code != 201:
            logger.error(f"Version log failed with status {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send version snapshot: {str(e)}")
