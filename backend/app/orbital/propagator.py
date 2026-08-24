import numpy as np
from datetime import datetime, timezone
from sgp4.api import Satrec, jday
from typing import Tuple, Dict, Any, List
from app.models.satellite import SatelliteStateVector

def propagate_sgp4(
    line1: str,
    line2: str,
    dt: datetime
) -> Tuple[np.ndarray, np.ndarray, bool]:
    """
    Propagates orbit to specified UTC datetime using SGP4.
    Returns: (position_eci_km, velocity_eci_kms, error_flag)
    """
    sat = Satrec.twoline2rv(line1, line2)
    # Convert datetime to Julian date and fraction
    jd, fr = jday(
        dt.year, dt.month, dt.day,
        dt.hour, dt.minute, dt.second + dt.microsecond * 1e-6
    )
    e, r, v = sat.sgp4(jd, fr)
    if e != 0:
        # SGP4 propagation error
        return np.zeros(3), np.zeros(3), False
    return np.array(r, dtype=float), np.array(v, dtype=float), True

def get_satellite_state(
    line1: str,
    line2: str,
    dt: datetime
) -> SatelliteStateVector:
    """Returns structured state vector at target timestamp."""
    r, v, success = propagate_sgp4(line1, line2, dt)
    alt = float(np.linalg.norm(r) - 6378.137)
    speed = float(np.linalg.norm(v))
    return SatelliteStateVector(
        timestamp=dt,
        position_eci=r.tolist(),
        velocity_eci=v.tolist(),
        altitude_km=round(alt, 2),
        speed_kms=round(speed, 3)
    )

def propagate_trajectory(
    line1: str,
    line2: str,
    start_dt: datetime,
    duration_hours: float = 24.0,
    step_minutes: float = 10.0
) -> List[Dict[str, Any]]:
    """Generates trajectory points over time window for 3D visualization and analysis."""
    steps = int((duration_hours * 60.0) / step_minutes)
    points = []
    for i in range(steps + 1):
        t_offset_sec = i * step_minutes * 60.0
        dt = datetime.fromtimestamp(start_dt.timestamp() + t_offset_sec, tz=timezone.utc)
        r, v, ok = propagate_sgp4(line1, line2, dt)
        if ok:
            points.append({
                "time": dt.isoformat(),
                "t_offset_sec": t_offset_sec,
                "position": r.tolist(),
                "velocity": v.tolist(),
                "altitude_km": float(np.linalg.norm(r) - 6378.137)
            })
    return points
