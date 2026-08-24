from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class CommandPayload(BaseModel):
    command_id: str
    mission_id: str
    satellite_id: str
    timestamp: str
    maneuver_type: str
    delta_v_ms: float
    direction: str
    execution_time: str
    status: str = "PENDING_APPROVAL"

class SignedCommandPayload(BaseModel):
    command: CommandPayload
    canonical_json: str
    payload_hash_sha256: str
    signature_base64: str
    algorithm: str
    signed_by: str
    signed_at: str

class VerificationResult(BaseModel):
    command_id: str
    is_valid: bool
    status_message: str
    verification_time: str
    tampered_fields: Optional[List[str]] = None

class TamperDemoRequest(BaseModel):
    original_signed_command: SignedCommandPayload
    field_to_tamper: str = "delta_v_ms"
    tampered_value: Any = 99.9
