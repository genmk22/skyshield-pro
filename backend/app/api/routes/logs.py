from fastapi import APIRouter, Query
from typing import List, Dict, Any
from app.core.logging import get_audit_logs

router = APIRouter(prefix="/logs", tags=["Audit Logs"])

@router.get("", response_model=List[Dict[str, Any]])
def read_audit_logs(limit: int = Query(default=100, ge=1, le=500)):
    return get_audit_logs(limit=limit)
