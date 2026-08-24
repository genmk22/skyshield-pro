import numpy as np
from typing import Tuple, Dict

def eci_to_rtn(
    r_primary: np.ndarray,
    v_primary: np.ndarray,
    r_relative: np.ndarray
) -> np.ndarray:
    """
    Transforms relative ECI position vector into RTN (Radial, Transverse/Along-track, Normal/Cross-track) frame.
    
    Radial (R): Unit vector along primary radius vector r_primary.
    Normal (N): Unit vector along orbital angular momentum h = r x v.
    Transverse (T): Unit vector completing right-hand triad (N x R).
    """
    r_norm = np.linalg.norm(r_primary)
    if r_norm == 0:
        return r_relative
    
    unit_r = r_primary / r_norm
    h = np.cross(r_primary, v_primary)
    h_norm = np.linalg.norm(h)
    if h_norm == 0:
        unit_n = np.array([0.0, 0.0, 1.0])
    else:
        unit_n = h / h_norm
        
    unit_t = np.cross(unit_n, unit_r)
    unit_t = unit_t / np.linalg.norm(unit_t)
    
    # Transformation matrix ECI -> RTN
    R_mat = np.vstack([unit_r, unit_t, unit_n])
    return R_mat @ r_relative

def compute_relative_geometry(
    r1: np.ndarray,
    v1: np.ndarray,
    r2: np.ndarray,
    v2: np.ndarray
) -> Dict[str, float]:
    """Computes miss distance, relative velocity, and RTN separation breakdown."""
    dr = r2 - r1
    dv = v2 - v1
    miss_distance = float(np.linalg.norm(dr))
    rel_speed = float(np.linalg.norm(dv))
    
    rtn_sep = eci_to_rtn(r1, v1, dr)
    
    return {
        "miss_distance_km": round(miss_distance, 4),
        "radial_sep_km": round(float(rtn_sep[0]), 4),
        "along_track_sep_km": round(float(rtn_sep[1]), 4),
        "cross_track_sep_km": round(float(rtn_sep[2]), 4),
        "relative_velocity_kms": round(rel_speed, 4)
    }
