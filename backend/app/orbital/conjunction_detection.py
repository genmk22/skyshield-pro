import numpy as np
from datetime import datetime, timezone
from scipy.optimize import minimize_scalar
from typing import Tuple, Dict, Any, Optional, List
from app.orbital.propagator import propagate_sgp4
from app.orbital.coordinate_utils import compute_relative_geometry

def separation_at_time(
    t_sec: float,
    start_dt: datetime,
    line1_a: str, line2_a: str,
    line1_b: str, line2_b: str
) -> float:
    """Distance function at offset t_sec from start_dt."""
    dt = datetime.fromtimestamp(start_dt.timestamp() + t_sec, tz=timezone.utc)
    r_a, _, ok_a = propagate_sgp4(line1_a, line2_a, dt)
    r_b, _, ok_b = propagate_sgp4(line1_b, line2_b, dt)
    if not (ok_a and ok_b):
        return 1e9
    return float(np.linalg.norm(r_b - r_a))

def find_tca_and_miss_distance(
    start_dt: datetime,
    line1_a: str, line2_a: str,
    line1_b: str, line2_b: str,
    lookahead_hours: float = 72.0,
    coarse_step_sec: float = 300.0  # 5 min coarse grid
) -> Tuple[datetime, float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Finds exact TCA (Time of Closest Approach) and encounter state vectors.
    Returns: (tca_dt, miss_distance_km, r_a, v_a, r_b, v_b)
    """
    total_sec = lookahead_hours * 3600.0
    num_steps = int(total_sec / coarse_step_sec)
    
    best_t_sec = 0.0
    min_dist = 1e9
    
    # Coarse scan
    for i in range(num_steps + 1):
        t = i * coarse_step_sec
        dist = separation_at_time(t, start_dt, line1_a, line2_a, line1_b, line2_b)
        if dist < min_dist:
            min_dist = dist
            best_t_sec = t
            
    # Fine numerical optimization around best_t_sec window [best_t - step, best_t + step]
    t_min = max(0.0, best_t_sec - coarse_step_sec)
    t_max = min(total_sec, best_t_sec + coarse_step_sec)
    
    res = minimize_scalar(
        separation_at_time,
        bracket=(t_min, best_t_sec, t_max),
        bounds=(t_min, t_max),
        method='bounded',
        args=(start_dt, line1_a, line2_a, line1_b, line2_b),
        options={'xatol': 1e-4}  # 0.1 ms precision
    )
    
    exact_t_sec = float(res.x)
    exact_tca_dt = datetime.fromtimestamp(start_dt.timestamp() + exact_t_sec, tz=timezone.utc)
    
    r_a, v_a, _ = propagate_sgp4(line1_a, line2_a, exact_tca_dt)
    r_b, v_b, _ = propagate_sgp4(line1_b, line2_b, exact_tca_dt)
    exact_miss_dist = float(np.linalg.norm(r_b - r_a))
    
    return exact_tca_dt, exact_miss_dist, r_a, v_a, r_b, v_b
