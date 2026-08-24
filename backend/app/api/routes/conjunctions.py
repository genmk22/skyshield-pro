import numpy as np
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from app.models.conjunction import ConjunctionEvent, ConjunctionAnalysisRequest, EncouterGeometry
from app.orbital.tle_loader import fetch_or_load_tles, get_tle_summary
from app.orbital.conjunction_detection import find_tca_and_miss_distance
from app.orbital.coordinate_utils import compute_relative_geometry
from app.risk.uncertainty import get_combined_covariance_3d
from app.risk.collision_probability import compute_bplane_pc
from app.risk.risk_classifier import classify_conjunction_risk
from app.core.logging import log_audit_event

router = APIRouter(prefix="/conjunctions", tags=["Conjunctions"])

# Cache in-memory active conjunctions for demo
ACTIVE_CONJUNCTIONS: List[ConjunctionEvent] = []

def set_active_conjunctions(events: Optional[List[ConjunctionEvent]] = None):
    global ACTIVE_CONJUNCTIONS
    if events is not None:
        ACTIVE_CONJUNCTIONS = events
    else:
        ACTIVE_CONJUNCTIONS = []
    return get_conjunctions()

def analyze_single_conjunction(
    sat_a: dict,
    sat_b: dict,
    lookahead_hours: float = 72.0,
    hbr_m: float = 10.0
) -> ConjunctionEvent:
    now = datetime.now(timezone.utc)
    tca_dt, miss_km, r_a, v_a, r_b, v_b = find_tca_and_miss_distance(
        now, sat_a["line1"], sat_a["line2"], sat_b["line1"], sat_b["line2"],
        lookahead_hours=lookahead_hours
    )
    
    geom_dict = compute_relative_geometry(r_a, v_a, r_b, v_b)
    sum_a = get_tle_summary(sat_a)
    sum_b = get_tle_summary(sat_b)
    
    time_to_tca_hrs = round(max(0.0, (tca_dt - now).total_seconds() / 3600.0), 2)
    
    C_eci = get_combined_covariance_3d(sum_a.age_hours, sum_b.age_hours, r_a, v_a)
    pc, bplane_miss, _ = compute_bplane_pc(r_a, v_a, r_b, v_b, C_eci, hbr_m)
    
    risk_lvl, reasons = classify_conjunction_risk(
        estimated_pc=pc,
        miss_distance_km=miss_km,
        time_to_tca_hours=time_to_tca_hrs,
        relative_velocity_kms=geom_dict["relative_velocity_kms"],
        tle_age_hours=max(sum_a.age_hours, sum_b.age_hours)
    )
    
    event_id = f"conj-{sat_a['norad_id']}-{sat_b['norad_id']}"
    
    # Combined positional uncertainty in meters
    comb_unc_m = round(float(np.sqrt(np.trace(C_eci))) * 1000.0, 1)
    
    confidence = "HIGH"
    if max(sum_a.age_hours, sum_b.age_hours) > 48:
        confidence = "LOW"
    elif max(sum_a.age_hours, sum_b.age_hours) > 24:
        confidence = "MODERATE"
        
    return ConjunctionEvent(
        id=event_id,
        primary_norad_id=sat_a["norad_id"],
        primary_name=sat_a["name"],
        secondary_norad_id=sat_b["norad_id"],
        secondary_name=sat_b["name"],
        secondary_type=sat_b.get("object_type", "DEBRIS"),
        tca=tca_dt,
        time_to_tca_hours=time_to_tca_hrs,
        geometry=EncouterGeometry(
            miss_distance_km=miss_km,
            radial_sep_km=geom_dict["radial_sep_km"],
            along_track_sep_km=geom_dict["along_track_sep_km"],
            cross_track_sep_km=geom_dict["cross_track_sep_km"],
            relative_velocity_kms=geom_dict["relative_velocity_kms"],
            relative_position_eci=(r_b - r_a).tolist(),
            relative_velocity_eci=(v_b - v_a).tolist()
        ),
        estimated_pc=pc,
        risk_level=risk_lvl,
        primary_tle_age_hours=sum_a.age_hours,
        secondary_tle_age_hours=sum_b.age_hours,
        combined_uncertainty_m=comb_unc_m,
        confidence=confidence,
        is_approximate=True
    )

@router.get("", response_model=List[ConjunctionEvent])
def get_conjunctions():
    if not ACTIVE_CONJUNCTIONS:
        # Generate default analysis using demo dataset
        tles = fetch_or_load_tles(live=False)
        if len(tles) >= 2:
            primary = tles[0]  # ISS
            for sec in tles[1:]:
                event = analyze_single_conjunction(primary, sec)
                ACTIVE_CONJUNCTIONS.append(event)
    return ACTIVE_CONJUNCTIONS

@router.get("/{id}", response_model=ConjunctionEvent)
def get_conjunction_by_id(id: str):
    conjs = get_conjunctions()
    for c in conjs:
        if c.id == id:
            return c
    raise HTTPException(status_code=404, detail="Conjunction event not found")

@router.post("/analyze", response_model=List[ConjunctionEvent])
def analyze_conjunctions(req: ConjunctionAnalysisRequest):
    global ACTIVE_CONJUNCTIONS
    tles = fetch_or_load_tles(live=False)
    primary = None
    for t in tles:
        if t["norad_id"] == req.primary_norad_id:
            primary = t
            break
    if not primary:
        raise HTTPException(status_code=404, detail=f"Primary satellite NORAD ID {req.primary_norad_id} not found")
        
    secondaries = []
    if req.secondary_norad_ids:
        secondaries = [t for t in tles if t["norad_id"] in req.secondary_norad_ids]
    else:
        secondaries = [t for t in tles if t["norad_id"] != req.primary_norad_id]
        
    results = []
    for sec in secondaries:
        event = analyze_single_conjunction(primary, sec, req.lookahead_hours, req.hard_body_radius_m)
        results.append(event)
        
    ACTIVE_CONJUNCTIONS = results
    log_audit_event(
        event_type="CONJUNCTION_ANALYZED",
        object_id=str(req.primary_norad_id),
        status="SUCCESS",
        details={"threats_detected": len(results)}
    )
    return results
