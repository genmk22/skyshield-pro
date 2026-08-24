import json
import base64
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

from app.models.command import CommandPayload, SignedCommandPayload, VerificationResult
from app.security.key_management import generate_or_get_keypair
from app.core.logging import log_audit_event

def canonicalize_command_payload(payload: Dict[str, Any]) -> str:
    """
    Serializes payload into canonical JSON representation (deterministic key sorting, no whitespace).
    """
    return json.dumps(payload, sort_keys=True, separators=(',', ':'))

def sign_command_payload(payload: CommandPayload, operator_id: str = "FLIGHT_DYNAMICS_OPERATOR_01") -> SignedCommandPayload:
    """
    Hashes canonical payload with SHA-256 and signs with RSA-2048 private key.
    """
    priv_pem, pub_pem = generate_or_get_keypair()
    
    private_key = serialization.load_pem_private_key(
        priv_pem.encode('utf-8'),
        password=None
    )
    
    payload_dict = payload.model_dump()
    canonical_str = canonicalize_command_payload(payload_dict)
    
    payload_hash = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
    
    signature_bytes = private_key.sign(
        canonical_str.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    
    sig_b64 = base64.b64encode(signature_bytes).decode('utf-8')
    signed_at = datetime.now(timezone.utc).isoformat()
    
    log_audit_event(
        event_type="COMMAND_SIGNED",
        object_id=payload.command_id,
        status="SUCCESS",
        details={
            "mission_id": payload.mission_id,
            "satellite_id": payload.satellite_id,
            "delta_v_ms": payload.delta_v_ms,
            "hash": payload_hash,
            "signed_by": operator_id
        }
    )
    
    return SignedCommandPayload(
        command=payload,
        canonical_json=canonical_str,
        payload_hash_sha256=payload_hash,
        signature_base64=sig_b64,
        algorithm="RSA-2048-PKCS1v15-SHA256 (PQC Abstraction Ready)",
        signed_by=operator_id,
        signed_at=signed_at
    )

def verify_command_signature(signed_payload: SignedCommandPayload) -> VerificationResult:
    """
    Verifies payload signature against public key. Detects any parameter tampering.
    """
    _, pub_pem = generate_or_get_keypair()
    
    public_key = serialization.load_pem_public_key(pub_pem.encode('utf-8'))
    
    # Re-canonicalize actual command inside payload
    current_dict = signed_payload.command.model_dump()
    current_canonical_str = canonicalize_command_payload(current_dict)
    current_hash = hashlib.sha256(current_canonical_str.encode('utf-8')).hexdigest()
    
    now_str = datetime.now(timezone.utc).isoformat()
    sig_bytes = base64.b64decode(signed_payload.signature_base64)
    
    try:
        public_key.verify(
            sig_bytes,
            current_canonical_str.encode('utf-8'),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        log_audit_event(
            event_type="COMMAND_VERIFIED",
            object_id=signed_payload.command.command_id,
            status="SUCCESS",
            details={"integrity": "CONFIRMED"}
        )
        
        return VerificationResult(
            command_id=signed_payload.command.command_id,
            is_valid=True,
            status_message="✓ SIGNATURE VALID — COMMAND INTEGRITY CONFIRMED",
            verification_time=now_str
        )
    except Exception as e:
        log_audit_event(
            event_type="COMMAND_TAMPER_DETECTED",
            object_id=signed_payload.command.command_id,
            status="FAILURE",
            details={"error": str(e), "hash_mismatch": current_hash != signed_payload.payload_hash_sha256}
        )
        
        return VerificationResult(
            command_id=signed_payload.command.command_id,
            is_valid=False,
            status_message="❌ SIGNATURE INVALID — COMMAND REJECTED (PAYLOAD TAMPERING DETECTED)",
            verification_time=now_str,
            tampered_fields=["Cryptographic hash mismatch or signature verification failure"]
        )
