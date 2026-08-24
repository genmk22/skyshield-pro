import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.models.maneuver import ManeuverCandidate, ManeuverConstraint, MultiThreatEvaluationResult
from app.maneuver.maneuver_generator import generate_candidate_burns
from app.maneuver.maneuver_simulator import simulate_post_maneuver_conjunction

def evaluate_multi_threat_maneuvers(
    satellite_id: str,
    r_primary: np.ndarray,
    v_primary: np.ndarray,
    threats: List[Dict[str, Any]],  # List of active conjunction threat dicts
    constraints: ManeuverConstraint,
    burn_epoch: datetime,
    force_no_safe_scenario: bool = False
) -> MultiThreatEvaluationResult:
    """
    Evaluates candidate maneuvers against ALL active threat conjunctions simultaneously.
    
    Formula for candidate score:
    Score = (Risk Reduction %) * 10 - (Delta-V m/s) * 2 - (Fuel kg) * 1.5 - New Threat Penalty
    """
    if force_no_safe_scenario:
        # Predefined scenario 5: Force all candidates to violate constraints
        candidates_raw = generate_candidate_burns(
            satellite_id, r_primary, v_primary, burn_epoch,
            allowed_directions=["PROGRADE", "RETROGRADE"],
            delta_v_magnitudes_ms=[0.01, 0.02]  # Intentionally inadequate delta-v
        )
    else:
        candidates_raw = generate_candidate_burns(
            satellite_id, r_primary, v_primary, burn_epoch,
            allowed_directions=constraints.allowed_directions,
            delta_v_magnitudes_ms=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
        )
        
    evaluated_candidates: List[ManeuverCandidate] = []
    
    # Calculate baseline combined risk before burn
    max_risk_before = max([t.get("estimated_pc", 1e-5) for t in threats]) if threats else 1e-5
    
    for item in candidates_raw:
        dv_eci = np.array(item["dv_eci_kms"])
        dv_ms = item["delta_v_ms"]
        
        # Evaluate burn against every threat
        post_pcs = []
        post_misses = []
        threat_worsened = False
        
        for t in threats:
            r_sec = np.array(t.get("r_secondary", [0, 0, 0]))
            v_sec = np.array(t.get("v_secondary", [0, 0, 0]))
            pc_before = t.get("estimated_pc", 1e-5)
            age_p = t.get("primary_tle_age_hours", 6.0)
            age_s = t.get("secondary_tle_age_hours", 6.0)
            
            pc_after, miss_after, _ = simulate_post_maneuver_conjunction(
                r_primary, v_primary, dv_eci,
                r_sec, v_sec, age_p, age_s
            )
            post_pcs.append(pc_after)
            post_misses.append(miss_after)
            
            if pc_after > pc_before * 1.2 and pc_after > 1e-7:
                threat_worsened = True
                
        max_post_pc = max(post_pcs) if post_pcs else 1e-7
        min_post_miss = min(post_misses) if post_misses else 5.0
        
        risk_reduction_pct = max(0.0, round((1.0 - (max_post_pc / max_risk_before)) * 100.0, 2))
        
        # Check constraints
        is_valid = True
        status = "SAFE CANDIDATE"
        failure_reason = None
        
        if force_no_safe_scenario:
            is_valid = False
            status = "VIOLATES CONSTRAINT"
            failure_reason = "Insufficient delta-v: Post-maneuver miss distance remains below required 1.0 km safety threshold."
        elif dv_ms > constraints.max_delta_v_ms:
            is_valid = False
            status = "VIOLATES CONSTRAINT"
            failure_reason = f"Delta-V ({dv_ms} m/s) exceeds maximum allowed limit ({constraints.max_delta_v_ms} m/s)."
        elif item["fuel_cost_kg"] > constraints.max_fuel_budget_kg:
            is_valid = False
            status = "VIOLATES CONSTRAINT"
            failure_reason = f"Fuel cost ({item['fuel_cost_kg']} kg) exceeds budget limit ({constraints.max_fuel_budget_kg} kg)."
        elif min_post_miss < constraints.min_miss_distance_km:
            is_valid = False
            status = "VIOLATES CONSTRAINT"
            failure_reason = f"Post-maneuver miss distance ({min_post_miss:.2f} km) is below required safety margin ({constraints.min_miss_distance_km} km)."
        elif threat_worsened:
            is_valid = False
            status = "INCREASES RISK"
            failure_reason = "Maneuver exacerbates risk for at least one secondary threat conjunction."
            
        # Scoring function:
        # Score = (Risk Reduction %) * 10 - (Delta-V m/s) * 5 - (Fuel kg) * 2 - (Penalty if invalid)
        score = (risk_reduction_pct * 10.0) - (dv_ms * 5.0) - (item["fuel_cost_kg"] * 2.0)
        if not is_valid:
            score -= 1000.0
            
        candidate_obj = ManeuverCandidate(
            id=item["id"],
            direction=item["direction"],
            delta_v_ms=dv_ms,
            burn_epoch=item["burn_epoch"],
            delta_v_components_kms=item["dv_eci_kms"],
            estimated_fuel_cost_kg=item["fuel_cost_kg"],
            risk_before=max_risk_before,
            risk_after=max_post_pc,
            risk_reduction_pct=risk_reduction_pct,
            post_maneuver_miss_distance_km=round(min_post_miss, 3),
            affected_threats_count=len(threats),
            score=round(score, 2),
            is_valid=is_valid,
            status=status,
            failure_reason=failure_reason
        )
        evaluated_candidates.append(candidate_obj)
        
    # Sort candidates by score descending
    evaluated_candidates.sort(key=lambda c: c.score, reverse=True)
    
    valid_candidates = [c for c in evaluated_candidates if c.is_valid]
    has_safe = len(valid_candidates) > 0
    best_candidate = valid_candidates[0] if has_safe else None
    
    no_safe_reason = None
    if not has_safe:
        no_safe_reason = (
            "NO SAFE MANEUVER FOUND: Every evaluated candidate burn violates either "
            "delta-v limits, fuel budget, or creates secondary threat collisions."
        )
        
    return MultiThreatEvaluationResult(
        satellite_id=satellite_id,
        total_active_threats=len(threats),
        evaluated_candidates_count=len(evaluated_candidates),
        best_candidate=best_candidate,
        all_candidates=evaluated_candidates,
        has_safe_maneuver=has_safe,
        no_safe_maneuver_reason=no_safe_reason
    )
