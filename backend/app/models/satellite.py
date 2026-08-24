from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TLEData(BaseModel):
    norad_id: int
    name: str
    line1: str
    line2: str
    epoch_datetime: Optional[datetime] = None
    age_hours: Optional[float] = None

class SatelliteSummary(BaseModel):
    id: str
    norad_id: int
    name: str
    object_type: str  # "PAYLOAD", "DEBRIS", "ROCKET BODY"
    tle_line1: str
    tle_line2: str
    epoch_datetime: datetime
    age_hours: float
    confidence_level: str  # "HIGH", "MODERATE", "LOW", "STALE"
    semi_major_axis_km: float
    eccentricity: float
    inclination_deg: float
    period_min: float
    apogee_km: float
    perigee_km: float

class SatelliteStateVector(BaseModel):
    timestamp: datetime
    position_eci: List[float]  # [x, y, z] km
    velocity_eci: List[float]  # [vx, vy, vz] km/s
    altitude_km: float
    speed_kms: float
