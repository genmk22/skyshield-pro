from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ManeuverConstraint(BaseModel):
    max_delta_v_ms: float = 5.0
    min_miss_distance_km: float = 1.0
    max_fuel_budget_kg: float = 2.0
    allowed_directions: List[str] = [
        "PROGRADE", "RETROGRADE", "RADIAL", "ANTI-RADIAL", "NORMAL", "ANTI-NORMAL"
    ]

class ManeuverCandidate(BaseModel):
    id: str
    direction: str
    delta_v_ms: float
    burn_epoch: datetime
    delta_v_components_kms: List[float]  # [dv_x, dv_y, dv_z] in RTN frame
    estimated_fuel_cost_kg: float
    risk_before: float
    risk_after: float
    risk_reduction_pct: float
    post_maneuver_miss_distance_km: float
    affected_threats_count: int
    score: float
    is_valid: bool
    status: str  # "SAFE CANDIDATE", "VIOLATES CONSTRAINT", "INCREASES RISK"
    failure_reason: Optional[str] = None

class MultiThreatEvaluationResult(BaseModel):
    satellite_id: str
    total_active_threats: int
    evaluated_candidates_count: int
    best_candidate: Optional[ManeuverCandidate] = None
    all_candidates: List[ManeuverCandidate]
    has_safe_maneuver: bool
    no_safe_maneuver_reason: Optional[str] = None
