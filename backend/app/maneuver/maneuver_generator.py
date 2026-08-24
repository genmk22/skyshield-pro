import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.models.maneuver import ManeuverCandidate

def generate_candidate_burns(
    satellite_id: str,
    r_primary: np.ndarray,
    v_primary: np.ndarray,
    burn_epoch: datetime,
    allowed_directions: List[str] = None,
    delta_v_magnitudes_ms: List[float] = None
) -> List[Dict[str, Any]]:
    """
    Generates transparent grid-search candidate maneuvers in RTN frame.
    """
    if allowed_directions is None:
        allowed_directions = [
            "PROGRADE", "RETROGRADE", "RADIAL", "ANTI-RADIAL", "NORMAL", "ANTI-NORMAL"
        ]
    if delta_v_magnitudes_ms is None:
        delta_v_magnitudes_ms = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
        
    r_norm = np.linalg.norm(r_primary)
    unit_r = r_primary / r_norm if r_norm > 0 else np.array([1., 0., 0.])
    h = np.cross(r_primary, v_primary)
    h_norm = np.linalg.norm(h)
    unit_n = h / h_norm if h_norm > 0 else np.array([0., 0., 1.])
    unit_t = np.cross(unit_n, unit_r)
    
    # Transformation matrix RTN -> ECI
    R_mat = np.column_stack([unit_r, unit_t, unit_n])
    
    direction_vectors = {
        "PROGRADE": np.array([0.0, 1.0, 0.0]),
        "RETROGRADE": np.array([0.0, -1.0, 0.0]),
        "RADIAL": np.array([1.0, 0.0, 0.0]),
        "ANTI-RADIAL": np.array([-1.0, 0.0, 0.0]),
        "NORMAL": np.array([0.0, 0.0, 1.0]),
        "ANTI-NORMAL": np.array([0.0, 0.0, -1.0])
    }
    
    candidates = []
    idx = 1
    
    for direction in allowed_directions:
        if direction not in direction_vectors:
            continue
        unit_dir_rtn = direction_vectors[direction]
        
        for dv_ms in delta_v_magnitudes_ms:
            dv_kms = dv_ms / 1000.0  # m/s to km/s
            dv_rtn = unit_dir_rtn * dv_kms
            dv_eci = R_mat @ dv_rtn
            
            # Estimated fuel cost (0.4 kg per m/s for 500kg satellite)
            fuel_cost_kg = round(dv_ms * 0.4, 2)
            
            candidates.append({
                "id": f"M-{idx:03d}",
                "direction": direction,
                "delta_v_ms": dv_ms,
                "burn_epoch": burn_epoch,
                "dv_rtn_kms": dv_rtn.tolist(),
                "dv_eci_kms": dv_eci.tolist(),
                "fuel_cost_kg": fuel_cost_kg
            })
            idx += 1
            
    return candidates
