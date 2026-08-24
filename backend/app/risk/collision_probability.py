import numpy as np
from scipy.integrate import dblquad
from typing import Tuple, Dict, Any

def compute_bplane_pc(
    r_a: np.ndarray,
    v_a: np.ndarray,
    r_b: np.ndarray,
    v_b: np.ndarray,
    C_eci: np.ndarray,
    hard_body_radius_m: float = 10.0
) -> Tuple[float, float, Dict[str, Any]]:
    """
    Computes analytical collision probability Pc on 2D encounter plane (B-plane).
    
    Returns: (Pc, bplane_miss_distance_km, debug_info)
    """
    dr = r_b - r_a  # relative position vector at TCA (km)
    dv = v_b - v_a  # relative velocity vector at TCA (km/s)
    
    v_rel_norm = np.linalg.norm(dv)
    if v_rel_norm < 1e-6:
        # Stationary encounter - fallback
        return 0.0, float(np.linalg.norm(dr)), {}
        
    # Build encounter plane orthonormal basis (unit_i, unit_j, unit_k)
    unit_k = dv / v_rel_norm  # along relative velocity
    
    # Pick arbitrary non-parallel vector to define unit_i
    ref = np.array([1.0, 0.0, 0.0]) if abs(unit_k[0]) < 0.8 else np.array([0.0, 1.0, 0.0])
    unit_i = np.cross(unit_k, ref)
    unit_i = unit_i / np.linalg.norm(unit_i)
    
    unit_j = np.cross(unit_k, unit_i)
    unit_j = unit_j / np.linalg.norm(unit_j)
    
    # Project relative position onto 2D encounter plane (unit_i, unit_j)
    x_enc = float(np.dot(dr, unit_i))
    y_enc = float(np.dot(dr, unit_j))
    bplane_miss_km = float(np.sqrt(x_enc**2 + y_enc**2))
    
    # Transformation matrix ECI (3D) -> Encounter Plane (2D)
    M_enc = np.vstack([unit_i, unit_j])  # 2x3
    
    # 2D Covariance Matrix on encounter plane
    C_2d = M_enc @ C_eci @ M_enc.T  # 2x2 matrix (in km^2)
    
    det_C = np.linalg.det(C_2d)
    if det_C <= 0:
        return 0.0, bplane_miss_km, {}
        
    C_inv = np.linalg.inv(C_2d)
    
    # Hard-body radius in kilometers
    hbr_km = hard_body_radius_m / 1000.0
    
    # Chan / Akella-Alfriend analytical approximation for small HBR over covariance:
    # Pc = (HBR^2 / (2 * sqrt(det_C))) * exp(-0.5 * x_mean^T * C_inv * x_mean)
    mean_vec = np.array([x_enc, y_enc])
    mahalanobis_sq = float(mean_vec.T @ C_inv @ mean_vec)
    
    # 2D Gaussian density at encounter center
    coeff = 1.0 / (2.0 * np.pi * np.sqrt(det_C))
    pc_chan = (np.pi * hbr_km**2) * coeff * np.exp(-0.5 * mahalanobis_sq)
    
    # Cap probability between 0 and 1
    pc_final = float(np.clip(pc_chan, 1e-12, 1.0))
    
    debug_info = {
        "x_enc_km": round(x_enc, 4),
        "y_enc_km": round(y_enc, 4),
        "bplane_miss_km": round(bplane_miss_km, 4),
        "mahalanobis_dist": round(float(np.sqrt(mahalanobis_sq)), 3),
        "hbr_m": hard_body_radius_m
    }
    
    return pc_final, bplane_miss_km, debug_info
