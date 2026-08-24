import numpy as np
from typing import Tuple

def get_combined_covariance_3d(
    tle_age_hours_a: float,
    tle_age_hours_b: float,
    r_primary: np.ndarray,
    v_primary: np.ndarray
) -> np.ndarray:
    """
    Computes time-dependent combined 3D positional covariance matrix C in ECI frame.
    Base 1-sigma uncertainties in RTN frame:
    Radial: 50m, Along-track: 250m, Cross-track: 80m.
    Scales with TLE age t_age via exponential growth factor.
    """
    # Base standard deviations in km
    sigma_r_0 = 0.050   # 50 meters
    sigma_t_0 = 0.250   # 250 meters
    sigma_n_0 = 0.080   # 80 meters
    
    # Growth factor as function of TLE age in hours
    growth_a = 1.0 + 0.15 * (tle_age_hours_a / 24.0) ** 1.5
    growth_b = 1.0 + 0.15 * (tle_age_hours_b / 24.0) ** 1.5
    
    sigma_r_a = sigma_r_0 * growth_a
    sigma_t_a = sigma_t_0 * growth_a
    sigma_n_a = sigma_n_0 * growth_a
    
    sigma_r_b = sigma_r_0 * growth_b
    sigma_t_b = sigma_t_0 * growth_b
    sigma_n_b = sigma_n_0 * growth_b
    
    # Combined variance in RTN frame
    var_r = sigma_r_a**2 + sigma_r_b**2
    var_t = sigma_t_a**2 + sigma_t_b**2
    var_n = sigma_n_a**2 + sigma_n_b**2
    
    C_rtn = np.diag([var_r, var_t, var_n])
    
    # Rotate RTN covariance into ECI frame
    r_norm = np.linalg.norm(r_primary)
    if r_norm == 0:
        return C_rtn
    unit_r = r_primary / r_norm
    h = np.cross(r_primary, v_primary)
    h_norm = np.linalg.norm(h)
    unit_n = h / h_norm if h_norm > 0 else np.array([0., 0., 1.])
    unit_t = np.cross(unit_n, unit_r)
    
    # Rotation matrix RTN -> ECI (columns are unit vectors)
    R_mat = np.column_stack([unit_r, unit_t, unit_n])
    
    C_eci = R_mat @ C_rtn @ R_mat.T
    return C_eci
