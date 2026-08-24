from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import numpy as np

from app.models.conjunction import ConjunctionEvent, EncouterGeometry
from app.api.routes.conjunctions import set_active_conjunctions
from app.api.routes.maneuver import evaluate_maneuver_options
from app.maneuver import state as maneuver_state
from app.api.routes.security import create_command_from_maneuver, sign_command
from app.core.logging import log_audit_event

router = APIRouter(prefix="/scenarios", tags=["Presentation Scenarios"])

SCENARIOS_CATALOG = [
    {
        "id": "scenario-1",
        "name": "Standard Single High-Risk Conjunction",
        "category": "Collision Probability",
        "description": "ISS vs Debris object in LEO with miss distance of 0.25 km and Pc = 4.8e-4."
    },
    {
        "id": "scenario-2",
        "name": "Stale TLE Data Confidence Scaling",
        "category": "Uncertainty Scaling",
        "description": "Secondary object TLE age > 72 hours. Demonstrates data freshness penalty and Pc widening."
    },
    {
        "id": "scenario-3",
        "name": "Multi-Threat Maneuver Avoidance",
        "category": "Grid Search Advisor",
        "description": "Primary conjunction present. Prograde burn avoids primary threat while guaranteeing zero secondary collisions."
    },
    {
        "id": "scenario-4",
        "name": "Secondary Threat Conflict (Worsened Threat)",
        "category": "Multi-Threat Safety",
        "description": "Retrograde candidate burn successfully avoids primary threat but increases collision risk for a secondary nearby object."
    },
    {
        "id": "scenario-5",
        "name": "Honest Failure State (No Safe Maneuver Found)",
        "category": "Honest Advisory",
        "description": "All candidate burns exceed max delta-v (5.0 m/s) or fail safety margin. Triggers NO SAFE MANEUVER FOUND state."
    },
    {
        "id": "scenario-6",
        "name": "Monte Carlo Convergence vs Analytical B-Plane",
        "category": "Monte Carlo Engine",
        "description": "Compares 2D Gaussian analytical Pc against 50,000 Monte Carlo propagated particle samples."
    },
    {
        "id": "scenario-7",
        "name": "Cryptographic Command Signing & Tamper Demo",
        "category": "Cybersecurity",
        "description": "Generates RSA-2048 signed burn payload, then modifies burn magnitude to trigger SIGNATURE INVALID verification."
    }
]

@router.get("", response_model=List[Dict[str, Any]])
def list_presentation_scenarios():
    return SCENARIOS_CATALOG

@router.post("/{scenario_id}/run")
def run_scenario(scenario_id: str):
    now = datetime.now(timezone.utc)
    
    log_audit_event(
        event_type="SCENARIO_TRIGGERED",
        object_id=scenario_id,
        status="SUCCESS",
        details={}
    )
    
    if scenario_id == "scenario-1":
        conj = ConjunctionEvent(
            id="conj-scenario-1",
            primary_norad_id=25544,
            primary_name="ISS (ZARYA)",
            secondary_norad_id=33442,
            secondary_name="FENGYUN 1C DEBRIS",
            secondary_type="DEBRIS",
            tca=now + timedelta(hours=14.5),
            time_to_tca_hours=14.5,
            geometry=EncouterGeometry(
                miss_distance_km=0.250,
                radial_sep_km=0.080,
                along_track_sep_km=0.210,
                cross_track_sep_km=0.100,
                relative_velocity_kms=12.45,
                relative_position_eci=[0.08, 0.21, 0.10],
                relative_velocity_eci=[-8.2, 7.1, 4.3]
            ),
            estimated_pc=4.82e-04,
            risk_level="HIGH RISK",
            primary_tle_age_hours=4.2,
            secondary_tle_age_hours=11.5,
            combined_uncertainty_m=340.0,
            confidence="HIGH",
            is_approximate=True
        )
        set_active_conjunctions([conj])
        return {"scenario": scenario_id, "status": "ACTIVE", "conjunctions": [conj]}
        
    elif scenario_id == "scenario-2":
        conj = ConjunctionEvent(
            id="conj-scenario-2",
            primary_norad_id=25544,
            primary_name="ISS (ZARYA)",
            secondary_norad_id=41920,
            secondary_name="COSMOS 2251 DEBRIS",
            secondary_type="DEBRIS",
            tca=now + timedelta(hours=22.0),
            time_to_tca_hours=22.0,
            geometry=EncouterGeometry(
                miss_distance_km=0.820,
                radial_sep_km=0.350,
                along_track_sep_km=0.680,
                cross_track_sep_km=0.310,
                relative_velocity_kms=14.10,
                relative_position_eci=[0.35, 0.68, 0.31],
                relative_velocity_eci=[-9.5, 8.2, 5.1]
            ),
            estimated_pc=1.25e-04,
            risk_level="WARNING",
            primary_tle_age_hours=6.0,
            secondary_tle_age_hours=84.5,
            combined_uncertainty_m=1250.0,
            confidence="STALE DATA",
            is_approximate=True
        )
        set_active_conjunctions([conj])
        return {"scenario": scenario_id, "status": "ACTIVE", "conjunctions": [conj]}

    elif scenario_id == "scenario-3":
        conj = ConjunctionEvent(
            id="conj-scenario-3",
            primary_norad_id=25544,
            primary_name="ISS (ZARYA)",
            secondary_norad_id=33442,
            secondary_name="FENGYUN 1C DEBRIS",
            secondary_type="DEBRIS",
            tca=now + timedelta(hours=18.0),
            time_to_tca_hours=18.0,
            geometry=EncouterGeometry(
                miss_distance_km=0.245,
                radial_sep_km=0.075,
                along_track_sep_km=0.210,
                cross_track_sep_km=0.095,
                relative_velocity_kms=12.8,
                relative_position_eci=[0.075, 0.210, 0.095],
                relative_velocity_eci=[-8.5, 7.4, 4.5]
            ),
            estimated_pc=5.12e-04,
            risk_level="HIGH RISK",
            primary_tle_age_hours=3.5,
            secondary_tle_age_hours=8.0,
            combined_uncertainty_m=320.0,
            confidence="HIGH",
            is_approximate=True
        )
        set_active_conjunctions([conj])
        eval_res = evaluate_maneuver_options("25544", force_no_safe=False)
        return {"scenario": scenario_id, "status": "ACTIVE", "conjunctions": [conj], "maneuver_result": eval_res}

    elif scenario_id == "scenario-5":
        eval_res = evaluate_maneuver_options("25544", force_no_safe=True)
        return {"scenario": scenario_id, "status": "NO_SAFE_MANEUVER", "maneuver_result": eval_res}

    elif scenario_id == "scenario-7":
        conj = ConjunctionEvent(
            id="conj-scenario-7",
            primary_norad_id=25544,
            primary_name="ISS (ZARYA)",
            secondary_norad_id=33442,
            secondary_name="FENGYUN 1C DEBRIS",
            secondary_type="DEBRIS",
            tca=now + timedelta(hours=12.0),
            time_to_tca_hours=12.0,
            geometry=EncouterGeometry(
                miss_distance_km=0.310,
                radial_sep_km=0.090,
                along_track_sep_km=0.270,
                cross_track_sep_km=0.110,
                relative_velocity_kms=13.1,
                relative_position_eci=[0.090, 0.270, 0.110],
                relative_velocity_eci=[-8.8, 7.6, 4.7]
            ),
            estimated_pc=3.40e-04,
            risk_level="HIGH RISK",
            primary_tle_age_hours=2.0,
            secondary_tle_age_hours=6.0,
            combined_uncertainty_m=380.0,
            confidence="HIGH",
            is_approximate=True
        )
        set_active_conjunctions([conj])
        eval_res = evaluate_maneuver_options("25544", force_no_safe=False)
        cmd = create_command_from_maneuver("25544")
        signed = sign_command(cmd, "FLIGHT_DYNAMICS_OPERATOR_01")
        return {
            "scenario": scenario_id,
            "status": "SIGNED_COMMAND_READY",
            "conjunctions": [conj],
            "original_signed_command": signed
        }

    else:
        conjs = set_active_conjunctions()
        return {"scenario": scenario_id, "status": "RESET_DEFAULT", "conjunctions": conjs}
