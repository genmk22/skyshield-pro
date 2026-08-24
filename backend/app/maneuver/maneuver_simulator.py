import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from app.orbital.coordinate_utils import compute_relative_geometry
from app.risk.uncertainty import get_combined_covariance_3d
from app.risk.collision_probability import compute_bplane_pc

def simulate_post_maneuver_conjunction(
    r_primary: np.ndarray,
    v_primary: np.ndarray,
    dv_eci_kms: np.ndarray,
    r_secondary: np.ndarray,
    v_secondary: np.ndarray,
    dt_a_hours: float,
    dt_b_hours: float,
    hard_body_radius_m: float = 10.0,
    time_to_tca_hours: float = 2.0
) -> Tuple[float, float, Dict[str, Any]]:
    """
    Applies impulsive delta-v to primary satellite velocity v_primary,
    propagates position shift forward to TCA, and recomputes B-plane Pc and miss distance.
    
    Returns: (pc_after, post_miss_distance_km, geometry_info)
    """
    v_mag = np.linalg.norm(v_primary)
    if v_mag == 0:
        v_mag = 7.66
        
    v_unit = v_primary / v_mag
    
    # Linearized orbital shift at TCA (2 hours burn advance notice)
    dt_sec = max(time_to_tca_hours, 1.0) * 3600.0
    dv_tangential_kms = float(np.dot(dv_eci_kms, v_unit))
    
    # Clohessy-Wiltshire along-track drift: dr_along = 3 * dt * dv_tangential
    dr_along_km = 3.0 * dt_sec * dv_tangential_kms
    
    # ECI shift vector
    dr_shift_eci = dr_along_km * v_unit
    
    # Post maneuver position at TCA
    r_primary_post = r_primary + dr_shift_eci
    v_primary_post = v_primary + dv_eci_kms
    
    dr_post = r_secondary - r_primary_post
    post_miss_km = float(np.linalg.norm(dr_post))
    
    C_eci = get_combined_covariance_3d(dt_a_hours, dt_b_hours, r_primary_post, v_primary_post)
    pc_after, bplane_miss, debug_info = compute_bplane_pc(
        r_primary_post, v_primary_post,
        r_secondary, v_secondary,
        C_eci, hard_body_radius_m
    )
    
    geom = compute_relative_geometry(r_primary_post, v_primary_post, r_secondary, v_secondary)
    return pc_after, post_miss_km, geom
