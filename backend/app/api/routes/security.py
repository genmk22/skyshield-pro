from fastapi import APIRouter, HTTPException, Query, Body
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import uuid

from app.models.command import CommandPayload, SignedCommandPayload, VerificationResult, TamperDemoRequest
from app.security.command_signing import sign_command_payload, verify_command_signature
from app.maneuver import state as maneuver_state
from app.api.routes.maneuver import evaluate_maneuver_options
from app.core.logging import log_audit_event

router = APIRouter(prefix="/commands", tags=["Security Subsystem"])

@router.post("/create", response_model=CommandPayload)
def create_command_from_maneuver(
    satellite_id: str = Query(default="25544"),
    candidate_id: Optional[str] = Query(default=None)
):
    maneuver_res = maneuver_state.LATEST_MANEUVER_EVALUATION
    if not maneuver_res or not maneuver_res.all_candidates:
        maneuver_res = evaluate_maneuver_options(satellite_id=satellite_id)
        
    if not maneuver_res or not maneuver_res.all_candidates:
        raise HTTPException(
            status_code=400,
            detail="Cannot create command: No maneuver candidates available."
        )
        
    cand = maneuver_res.best_candidate
    if candidate_id:
        match = next((c for c in maneuver_res.all_candidates if c.id == candidate_id), None)
        if match:
            cand = match
            
    if not cand:
        cand = maneuver_res.all_candidates[0]
            
    now = datetime.now(timezone.utc)
    cmd_id = f"CMD-{uuid.uuid4().hex[:8].upper()}"
    
    return CommandPayload(
        command_id=cmd_id,
        mission_id="SKYSHIELD-LEO-01",
        satellite_id=satellite_id,
        timestamp=now.isoformat(),
        maneuver_type=f"IMPULSIVE_BURN_{cand.direction}",
        delta_v_ms=cand.delta_v_ms,
        direction=cand.direction,
        execution_time=(now + timedelta(hours=2)).isoformat(),
        status="HUMAN_APPROVED"
    )

@router.post("/sign", response_model=SignedCommandPayload)
def sign_command(payload: CommandPayload, operator_id: str = Query(default="FLIGHT_DYNAMICS_OPERATOR_01")):
    return sign_command_payload(payload, operator_id=operator_id)

@router.post("/verify", response_model=VerificationResult)
def verify_command(signed_payload: SignedCommandPayload):
    return verify_command_signature(signed_payload)

@router.post("/tamper-demo", response_model=VerificationResult)
def tamper_command_demo(req: TamperDemoRequest):
    """
    Simulates malicious command tampering by modifying a target field
    and running signature verification.
    """
    signed_copy = req.original_signed_command.model_copy(deep=True)
    
    # Mutate requested field inside command dictionary
    cmd_dict = signed_copy.command.model_dump()
    field = req.field_to_tamper
    cmd_dict[field] = req.tampered_value
    
    # Re-instantiate tampered command
    signed_copy.command = CommandPayload(**cmd_dict)
    
    # Run signature verification (will fail)
    res = verify_command_signature(signed_copy)
    res.tampered_fields = [f"Field '{field}' was modified from original signed value to {req.tampered_value}"]
    
    log_audit_event(
        event_type="COMMAND_TAMPER_DEMO",
        object_id=signed_copy.command.command_id,
        status="TAMPER_DETECTED",
        details={"tampered_field": field, "tampered_value": str(req.tampered_value)}
    )
    
    return res
