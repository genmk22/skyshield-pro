import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Setup standard logger
logger = logging.getLogger("skyshield")
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] SkyShield: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# In-memory audit log buffer for API access & UI audit table
AUDIT_LOGS: List[Dict[str, Any]] = []

def log_audit_event(
    event_type: str,
    object_id: Optional[str] = None,
    status: str = "SUCCESS",
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Records an audit event in memory and outputs structured log."""
    event = {
        "id": f"evt-{len(AUDIT_LOGS) + 1:05d}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "object_id": object_id or "SYSTEM",
        "status": status,
        "details": details or {}
    }
    AUDIT_LOGS.insert(0, event)  # newest first
    # Keep last 500 events
    if len(AUDIT_LOGS) > 500:
        AUDIT_LOGS.pop()
    
    logger.info(f"AUDIT_EVENT: {event_type} | Object: {object_id} | Status: {status} | Details: {json.dumps(details or {})}")
    return event

def get_audit_logs(limit: int = 100) -> List[Dict[str, Any]]:
    return AUDIT_LOGS[:limit]
