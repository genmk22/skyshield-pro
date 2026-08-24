import numpy as np
from fastapi import APIRouter, HTTPException
from app.models.risk import RiskExplanation, MonteCarloRequest, MonteCarloResult
from app.api.routes.conjunctions import ACTIVE_CONJUNCTIONS, get_conjunctions
from app.risk.explainability import generate_risk_explanation
from app.risk.risk_classifier import classify_conjunction_risk
from app.risk.monte_carlo import run_monte_carlo_simulation
from app.risk.uncertainty import get_combined_covariance_3d
from app.orbital.tle_loader import fetch_or_load_tles
from app.orbital.propagator import propagate_sgp4
from app.core.logging import log_audit_event

router = APIRouter(prefix="/risk", tags=["Risk & Monte Carlo"])

@router.get("/explain/{conjunction_id}", response_model=RiskExplanation)
def explain_conjunction_risk(conjunction_id: str):
    conjs = get_conjunctions()
    target = None
    for c in conjs:
        if c.id == conjunction_id:
            target = c
            break
    if not target:
        raise HTTPException(status_code=404, detail="Conjunction ID not found")
        
    _, reasons = classify_conjunction_risk(
        target.estimated_pc,
        target.geometry.miss_distance_km,
        target.time_to_tca_hours,
        target.geometry.relative_velocity_kms,
        max(target.primary_tle_age_hours, target.secondary_tle_age_hours)
    )
    
    return generate_risk_explanation(
        conjunction_id=target.id,
        risk_level=target.risk_level,
        estimated_pc=target.estimated_pc,
        miss_distance_km=target.geometry.miss_distance_km,
        time_to_tca_hours=target.time_to_tca_hours,
        relative_velocity_kms=target.geometry.relative_velocity_kms,
        primary_tle_age_hours=target.primary_tle_age_hours,
        secondary_tle_age_hours=target.secondary_tle_age_hours,
        reasons=reasons
    )

@router.post("/monte-carlo", response_model=MonteCarloResult)
def run_monte_carlo_api(req: MonteCarloRequest):
    conjs = get_conjunctions()
    target = None
    for c in conjs:
        if c.id == req.conjunction_id:
            target = c
            break
    if not target:
        raise HTTPException(status_code=404, detail="Conjunction ID not found")
        
    tles = fetch_or_load_tles(live=False)
    sat_a = next((t for t in tles if t["norad_id"] == target.primary_norad_id), None)
    sat_b = next((t for t in tles if t["norad_id"] == target.secondary_norad_id), None)
    
    if not (sat_a and sat_b):
        # Generate synthetic state vectors if TLE mismatch
        r_a, v_a = np.array([7000.0, 0.0, 0.0]), np.array([0.0, 7.5, 0.0])
        r_b = r_a + np.array(target.geometry.relative_position_eci)
        v_b = v_a + np.array(target.geometry.relative_velocity_eci)
    else:
        r_a, v_a, _ = propagate_sgp4(sat_a["line1"], sat_a["line2"], target.tca)
        r_b, v_b, _ = propagate_sgp4(sat_b["line1"], sat_b["line2"], target.tca)
        
    C_eci = get_combined_covariance_3d(
        target.primary_tle_age_hours,
        target.secondary_tle_age_hours,
        r_a, v_a
    )
    
    result = run_monte_carlo_simulation(
        conjunction_id=target.id,
        r_a=r_a, v_a=v_a,
        r_b=r_b, v_b=v_b,
        C_eci=C_eci,
        analytical_pc=target.estimated_pc,
        num_samples=req.num_samples,
        random_seed=req.random_seed or 42
    )
    
    # Cache result back onto active conjunction
    target.monte_carlo_pc = result.monte_carlo_pc
    
    log_audit_event(
        event_type="MONTE_CARLO_COMPLETED",
        object_id=req.conjunction_id,
        status="SUCCESS",
        details={
            "samples": req.num_samples,
            "analytical_pc": target.estimated_pc,
            "mc_pc": result.monte_carlo_pc,
            "diff_pct": result.percentage_difference
        }
    )
    
    return result
