from typing import Tuple, Dict, Any, List
from app.core.config import settings

def classify_conjunction_risk(
    estimated_pc: float,
    miss_distance_km: float,
    time_to_tca_hours: float,
    relative_velocity_kms: float,
    tle_age_hours: float
) -> Tuple[str, List[str]]:
    """
    Classifies risk into: SAFE, MONITOR, WARNING, HIGH RISK, CRITICAL.
    Returns: (risk_level, crossed_reasons)
    """
    reasons = []
    
    if estimated_pc >= settings.RISK_HIGH_PC:
        reasons.append(f"Estimated Pc ({estimated_pc:.2e}) exceeds Critical threshold ({settings.RISK_HIGH_PC:.2e})")
    elif estimated_pc >= settings.RISK_WARNING_PC:
        reasons.append(f"Estimated Pc ({estimated_pc:.2e}) exceeds High Risk threshold ({settings.RISK_WARNING_PC:.2e})")
    elif estimated_pc >= settings.RISK_MONITOR_PC:
        reasons.append(f"Estimated Pc ({estimated_pc:.2e}) exceeds Warning threshold ({settings.RISK_MONITOR_PC:.2e})")
    elif estimated_pc >= settings.RISK_SAFE_PC:
        reasons.append(f"Estimated Pc ({estimated_pc:.2e}) exceeds Monitor threshold ({settings.RISK_SAFE_PC:.2e})")
        
    if miss_distance_km < 0.2:
        reasons.append(f"Extremely close miss distance ({miss_distance_km*1000:.0f} m)")
    elif miss_distance_km < 1.0:
        reasons.append(f"Miss distance below 1.0 km safety buffer ({miss_distance_km:.2f} km)")
        
    if time_to_tca_hours < 12.0:
        reasons.append(f"Imminent encounter within {time_to_tca_hours:.1f} hours")
    elif time_to_tca_hours < 24.0:
        reasons.append(f"Time to TCA is within 24 hours ({time_to_tca_hours:.1f} hrs)")
        
    if tle_age_hours > 36.0:
        reasons.append(f"Tracking data is aged ({tle_age_hours:.1f} hrs old), expanding uncertainty volume")
        
    if relative_velocity_kms > 10.0:
        reasons.append(f"Hyper-velocity encounter ({relative_velocity_kms:.1f} km/s relative speed)")
        
    # Determine final level
    if estimated_pc >= 1e-4 or miss_distance_km < 0.2:
        return "CRITICAL", reasons
    elif estimated_pc >= 1e-5 or (miss_distance_km < 1.0 and time_to_tca_hours < 24.0):
        return "HIGH RISK", reasons
    elif estimated_pc >= 1e-6 or miss_distance_km < 2.5:
        return "WARNING", reasons
    elif estimated_pc >= 1e-7 or miss_distance_km < 5.0:
        return "MONITOR", reasons
    else:
        return "SAFE", ["Encounters outside high-risk geometric and probability bounds"]
