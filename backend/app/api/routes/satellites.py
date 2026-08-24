from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.satellite import SatelliteSummary, SatelliteStateVector
from app.orbital.tle_loader import fetch_or_load_tles, get_tle_summary
from app.orbital.propagator import get_satellite_state, propagate_trajectory
from datetime import datetime, timezone

router = APIRouter(prefix="/satellites", tags=["Satellites"])

@router.get("", response_model=List[SatelliteSummary])
def list_satellites(live: bool = Query(default=False)):
    tles = fetch_or_load_tles(live=live)
    return [get_tle_summary(item) for item in tles]

@router.get("/{id}", response_model=SatelliteSummary)
def get_satellite_by_id(id: str, live: bool = Query(default=False)):
    tles = fetch_or_load_tles(live=live)
    for item in tles:
        if str(item["norad_id"]) == id or item["name"].lower() == id.lower():
            return get_tle_summary(item)
    raise HTTPException(status_code=404, detail="Satellite object not found")

@router.get("/{id}/state", response_model=SatelliteStateVector)
def get_satellite_state_vector(id: str):
    tles = fetch_or_load_tles(live=False)
    for item in tles:
        if str(item["norad_id"]) == id:
            now = datetime.now(timezone.utc)
            return get_satellite_state(item["line1"], item["line2"], now)
    raise HTTPException(status_code=404, detail="Satellite object not found")

@router.get("/{id}/trajectory")
def get_satellite_trajectory(id: str, duration_hours: float = 24.0):
    tles = fetch_or_load_tles(live=False)
    for item in tles:
        if str(item["norad_id"]) == id:
            now = datetime.now(timezone.utc)
            return propagate_trajectory(item["line1"], item["line2"], now, duration_hours=duration_hours)
    raise HTTPException(status_code=404, detail="Satellite object not found")
