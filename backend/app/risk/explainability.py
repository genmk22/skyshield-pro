from typing import Dict, Any, List
from app.models.risk import RiskExplanation, RiskFactor

def generate_risk_explanation(
    conjunction_id: str,
    risk_level: str,
    estimated_pc: float,
    miss_distance_km: float,
    time_to_tca_hours: float,
    relative_velocity_kms: float,
    primary_tle_age_hours: float,
    secondary_tle_age_hours: float,
    reasons: List[str]
) -> RiskExplanation:
    """Generates structured human-readable explainability report."""
    
    max_age = max(primary_tle_age_hours, secondary_tle_age_hours)
    uncertainty_scale = round(1.0 + 0.15 * (max_age / 24.0) ** 1.5, 2)
    
    data_freshness_impact = (
        f"Tracking data age is {max_age:.1f} hours. "
        f"Position variance expanded by {uncertainty_scale}x."
    ) if max_age > 24 else f"Fresh tracking data ({max_age:.1f} hours old). Uncertainty bounds standard."
    
    factors = [
        RiskFactor(
            name="Collision Probability (Pc)",
            value=f"{estimated_pc:.2e}",
            weight="CRITICAL" if estimated_pc > 1e-4 else "HIGH" if estimated_pc > 1e-5 else "MEDIUM",
            description="2D B-plane integrated probability over combined hard-body radius.",
            threshold_crossed=estimated_pc >= 1e-6
        ),
        RiskFactor(
            name="Miss Distance at TCA",
            value=f"{miss_distance_km:.3f} km ({miss_distance_km*1000:.0f} m)",
            weight="CRITICAL" if miss_distance_km < 0.3 else "HIGH" if miss_distance_km < 1.0 else "LOW",
            description="Closest distance separation at Time of Closest Approach.",
            threshold_crossed=miss_distance_km < 2.0
        ),
        RiskFactor(
            name="Time to TCA",
            value=f"{time_to_tca_hours:.1f} hours",
            weight="HIGH" if time_to_tca_hours < 18 else "LOW",
            description="Time remaining until encounter peak.",
            threshold_crossed=time_to_tca_hours < 24
        ),
        RiskFactor(
            name="Relative Velocity",
            value=f"{relative_velocity_kms:.2f} km/s",
            weight="MEDIUM",
            description="Kinetic energy scale of collision encounter.",
            threshold_crossed=relative_velocity_kms > 8.0
        ),
        RiskFactor(
            name="TLE Data Freshness",
            value=f"{max_age:.1f} hrs (Confidence: {'LOW' if max_age > 48 else 'MODERATE' if max_age > 24 else 'HIGH'})",
            weight="HIGH" if max_age > 36 else "LOW",
            description="Age of two-line element set affecting covariance spread.",
            threshold_crossed=max_age > 24
        )
    ]
    
    rec_note = (
        "IMMEDIATE ACTION RECOMMENDED: Perform candidate maneuver grid search and human review."
        if risk_level in ["CRITICAL", "HIGH RISK"] else
        "MONITOR ENCOUNTER: Re-evaluating next TLE update cycle."
    )
    
    return RiskExplanation(
        conjunction_id=conjunction_id,
        risk_level=risk_level,
        summary=f"Conjunction assessed as {risk_level}. " + " ".join(reasons[:2]),
        key_factors=factors,
        data_freshness_impact=data_freshness_impact,
        uncertainty_scaling_factor=uncertainty_scale,
        recommendation_note=rec_note
    )
