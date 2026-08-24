from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ConjunctionAnalysisRequest(BaseModel):
    primary_norad_id: int
    secondary_norad_ids: Optional[List[int]] = None
    lookahead_hours: float = 72.0
    hard_body_radius_m: float = 10.0

class EncouterGeometry(BaseModel):
    miss_distance_km: float
    radial_sep_km: float
    along_track_sep_km: float
    cross_track_sep_km: float
    relative_velocity_kms: float
    relative_position_eci: List[float]
    relative_velocity_eci: List[float]

class ConjunctionEvent(BaseModel):
    id: str
    primary_norad_id: int
    primary_name: str
    secondary_norad_id: int
    secondary_name: str
    secondary_type: str
    tca: datetime
    time_to_tca_hours: float
    geometry: EncouterGeometry
    estimated_pc: float
    monte_carlo_pc: Optional[float] = None
    risk_level: str  # SAFE, MONITOR, WARNING, HIGH RISK, CRITICAL
    primary_tle_age_hours: float
    secondary_tle_age_hours: float
    combined_uncertainty_m: float
    confidence: str  # HIGH, MODERATE, LOW
    is_approximate: bool = True
