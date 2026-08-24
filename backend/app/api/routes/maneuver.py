import numpy as np
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from app.models.maneuver import (
    ManeuverConstraint, ManeuverCandidate, MultiThreatEvaluationResult
)
from app.maneuver.maneuver_optimizer import evaluate_multi_threat_maneuvers
from app.maneuver import state as maneuver_state
from app.api.routes.conjunctions import get_conjunctions
from app.orbital.tle_loader import fetch_or_load_tles
from app.orbital.propagator import propagate_sgp4
from app.core.logging import log_audit_event

router = APIRouter(prefix="/maneuvers", tags=["Maneuver Advisor"])

@router.post("/evaluate", response_model=MultiThreatEvaluationResult)
def evaluate_maneuver_options(
    satellite_id: str = Query(default="25544"),
    force_no_safe: bool = Query(default=False),
    constraints: Optional[ManeuverConstraint] = Body(default=None)
):
    if constraints is None or not isinstance(constraints, ManeuverConstraint):
        constraints = ManeuverConstraint()
        
    conjs = get_conjunctions()
    target_conjs = [c for c in conjs if str(c.primary_norad_id) == satellite_id or satellite_id == "25544"]
    
    tles = fetch_or_load_tles(live=False)
    primary = next((t for t in tles if str(t["norad_id"]) == satellite_id or t["norad_id"] == 25544), tles[0])
    
    now = datetime.now(timezone.utc)
    r_p, v_p, _ = propagate_sgp4(primary["line1"], primary["line2"], now)
    
    # Prepare threat dict list
    threat_dicts = []
    for c in target_conjs:
        if c.is_approximate or c.risk_level in ["HIGH RISK", "CRITICAL", "WARNING"]:
            # Use geometry relative position directly for scenario high-risk threats
            r_s = r_p + np.array(c.geometry.relative_position_eci)
            v_s = v_p + np.array(c.geometry.relative_velocity_eci)
        else:
            sec = next((t for t in tles if t["norad_id"] == c.secondary_norad_id), None)
            if sec:
                r_s, v_s, _ = propagate_sgp4(sec["line1"], sec["line2"], c.tca)
            else:
                r_s = r_p + np.array(c.geometry.relative_position_eci)
                v_s = v_p + np.array(c.geometry.relative_velocity_eci)
            
        threat_dicts.append({
            "id": c.id,
            "estimated_pc": c.estimated_pc,
            "r_secondary": r_s,
            "v_secondary": v_s,
            "primary_tle_age_hours": c.primary_tle_age_hours,
            "secondary_tle_age_hours": c.secondary_tle_age_hours
        })
        
    burn_epoch = now + timedelta(hours=2.0)
    result = evaluate_multi_threat_maneuvers(
        satellite_id=str(primary["norad_id"]),
        r_primary=r_p,
        v_primary=v_p,
        threats=threat_dicts,
        constraints=constraints,
        burn_epoch=burn_epoch,
        force_no_safe_scenario=force_no_safe
    )
    
    maneuver_state.LATEST_MANEUVER_EVALUATION = result
    
    log_audit_event(
        event_type="MANEUVER_GENERATED",
        object_id=str(primary["norad_id"]),
        status="SUCCESS",
        details={
            "candidates_evaluated": result.evaluated_candidates_count,
            "has_safe": result.has_safe_maneuver,
            "best_burn": result.best_candidate.direction if result.best_candidate else None
        }
    )
    
    return result

@router.get("/recommend", response_model=MultiThreatEvaluationResult)
def get_recommended_maneuver(satellite_id: str = Query(default="25544")):
    if maneuver_state.LATEST_MANEUVER_EVALUATION and maneuver_state.LATEST_MANEUVER_EVALUATION.satellite_id == satellite_id:
        return maneuver_state.LATEST_MANEUVER_EVALUATION
    return evaluate_maneuver_options(satellite_id=satellite_id)
