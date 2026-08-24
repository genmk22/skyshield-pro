import pytest
import numpy as np
from datetime import datetime, timezone, timedelta
from app.orbital.tle_loader import fetch_or_load_tles, get_tle_summary
from app.orbital.propagator import propagate_sgp4
from app.orbital.conjunction_detection import find_tca_and_miss_distance
from app.risk.uncertainty import get_combined_covariance_3d
from app.risk.collision_probability import compute_bplane_pc
from app.risk.risk_classifier import classify_conjunction_risk
from app.risk.monte_carlo import run_monte_carlo_simulation
from app.maneuver.maneuver_generator import generate_candidate_burns
from app.maneuver.maneuver_optimizer import evaluate_multi_threat_maneuvers
from app.models.maneuver import ManeuverConstraint
from app.models.command import CommandPayload
from app.security.command_signing import sign_command_payload, verify_command_signature

def test_tle_parsing_and_sgp4_propagation():
    tles = fetch_or_load_tles(live=False)
    assert len(tles) >= 5
    summary = get_tle_summary(tles[0])
    assert summary.norad_id == 25544
    assert summary.apogee_km > 300.0
    
    now = datetime.now(timezone.utc)
    r, v, ok = propagate_sgp4(tles[0]["line1"], tles[0]["line2"], now)
    assert ok is True
    assert np.linalg.norm(r) > 6000.0  # Earth radius + LEO altitude
    assert np.linalg.norm(v) > 7.0     # ~7.5 km/s orbital speed

def test_conjunction_detection_and_bplane_pc():
    tles = fetch_or_load_tles(live=False)
    now = datetime.now(timezone.utc)
    tca_dt, miss_km, r_a, v_a, r_b, v_b = find_tca_and_miss_distance(
        now, tles[0]["line1"], tles[0]["line2"], tles[1]["line1"], tles[1]["line2"]
    )
    assert miss_km >= 0.0
    
    C_eci = get_combined_covariance_3d(6.0, 6.0, r_a, v_a)
    pc, bplane_miss, debug = compute_bplane_pc(r_a, v_a, r_b, v_b, C_eci, 10.0)
    assert 0.0 <= pc <= 1.0

def test_risk_classification():
    level, reasons = classify_conjunction_risk(
        estimated_pc=5e-5,
        miss_distance_km=0.450,
        time_to_tca_hours=12.0,
        relative_velocity_kms=11.2,
        tle_age_hours=18.0
    )
    assert level in ["HIGH RISK", "CRITICAL"]
    assert len(reasons) > 0

def test_monte_carlo_simulation():
    r_a = np.array([7000.0, 0.0, 0.0])
    v_a = np.array([0.0, 7.5, 0.0])
    r_b = np.array([7000.1, 0.0, 0.0])  # 100m miss distance
    v_b = np.array([0.0, -7.5, 0.0])
    C_eci = np.eye(3) * 0.01
    
    res = run_monte_carlo_simulation(
        conjunction_id="test-01",
        r_a=r_a, v_a=v_a,
        r_b=r_b, v_b=v_b,
        C_eci=C_eci,
        analytical_pc=1e-3,
        num_samples=1000,
        random_seed=42
    )
    assert res.num_samples == 1000
    assert len(res.convergence_series) > 0

def test_maneuver_generation_and_no_safe_maneuver():
    r_p = np.array([7000.0, 0.0, 0.0])
    v_p = np.array([0.0, 7.5, 0.0])
    threats = [{
        "id": "conj-1",
        "estimated_pc": 2e-4,
        "r_secondary": np.array([7000.1, 0.0, 0.0]),
        "v_secondary": np.array([0.0, -7.5, 0.0]),
        "primary_tle_age_hours": 6.0,
        "secondary_tle_age_hours": 6.0
    }]
    now = datetime.now(timezone.utc)
    
    # Test valid burn search
    res = evaluate_multi_threat_maneuvers(
        satellite_id="25544",
        r_primary=r_p, v_primary=v_p,
        threats=threats,
        constraints=ManeuverConstraint(),
        burn_epoch=now + timedelta(hours=2),
        force_no_safe_scenario=False
    )
    assert res.evaluated_candidates_count > 0
    
    # Test NO SAFE MANEUVER FOUND case
    no_safe_res = evaluate_multi_threat_maneuvers(
        satellite_id="25544",
        r_primary=r_p, v_primary=v_p,
        threats=threats,
        constraints=ManeuverConstraint(),
        burn_epoch=now + timedelta(hours=2),
        force_no_safe_scenario=True
    )
    assert no_safe_res.has_safe_maneuver is False
    assert "NO SAFE MANEUVER FOUND" in no_safe_res.no_safe_maneuver_reason

def test_command_signing_and_tamper_verification():
    now = datetime.now(timezone.utc)
    payload = CommandPayload(
        command_id="CMD-12345",
        mission_id="TEST-MISSION",
        satellite_id="25544",
        timestamp=now.isoformat(),
        maneuver_type="IMPULSIVE_BURN_RETROGRADE",
        delta_v_ms=0.18,
        direction="RETROGRADE",
        execution_time=(now + timedelta(hours=2)).isoformat(),
        status="HUMAN_APPROVED"
    )
    
    signed = sign_command_payload(payload)
    verify_valid = verify_command_signature(signed)
    assert verify_valid.is_valid is True
    
    # Tamper payload field
    tampered_dict = payload.model_dump()
    tampered_dict["delta_v_ms"] = 9.99  # Altered delta-v
    signed.command = CommandPayload(**tampered_dict)
    
    verify_invalid = verify_command_signature(signed)
    assert verify_invalid.is_valid is False
    assert "INVALID" in verify_invalid.status_message
