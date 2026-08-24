import urllib.request
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sgp4.api import Satrec, WGS72
from app.models.satellite import TLEData, SatelliteSummary

# Bundled fallback demo dataset
DEMO_TLE_DATA = [
    {
        "norad_id": 25544,
        "name": "ISS (ZARYA)",
        "object_type": "PAYLOAD",
        "line1": "1 25544U 98067A   26236.54166667  .00016717  00000+0  30000-3 0  9993",
        "line2": "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.49815771441234"
    },
    {
        "norad_id": 44713,
        "name": "STARLINK-1007",
        "object_type": "PAYLOAD",
        "line1": "1 44713U 19074A   26236.41666667  .00001234  00000+0  10000-3 0  9991",
        "line2": "2 44713  53.0540 180.2310 0001420  90.2130 270.0120 15.06400000350012"
    },
    {
        "norad_id": 33442,
        "name": "COSMOS 2251 DEBRIS",
        "object_type": "DEBRIS",
        "line1": "1 33442U 93036B   26236.50000000  .00005432  00000+0  25000-3 0  9995",
        "line2": "2 33442  74.0210 120.4500 0021500  45.1200 315.0500 14.85000000210045"
    },
    {
        "norad_id": 29810,
        "name": "FENGYUN 1C DEBRIS",
        "object_type": "DEBRIS",
        "line1": "1 29810U 99025A   26236.48000000  .00008910  00000+0  40000-3 0  9997",
        "line2": "2 29810  98.6500 310.1200 0045000 180.5000 180.0000 14.21000000185023"
    },
    {
        "norad_id": 40059,
        "name": "SENTINEL-1A",
        "object_type": "PAYLOAD",
        "line1": "1 40059U 14016A   26236.52000000  .00000150  00000+0  20000-4 0  9992",
        "line2": "2 40059  98.1800 205.3000 0001200  95.4000 264.8000 14.57100000650089"
    }
]

def parse_tle_epoch(sat: Satrec) -> datetime:
    """Parses SGP4 satrec epoch into UTC datetime."""
    year = sat.epochyr
    if year < 57:
        year += 2000
    else:
        year += 1900
    days = sat.epochdays
    start_of_year = datetime(year, 1, 1, tzinfo=timezone.utc)
    epoch_dt = datetime.fromtimestamp(start_of_year.timestamp() + (days - 1) * 86400, tz=timezone.utc)
    return epoch_dt

def get_tle_summary(item: Dict[str, Any]) -> SatelliteSummary:
    """Calculates orbital elements and metadata from TLE lines."""
    sat = Satrec.twoline2rv(item["line1"], item["line2"])
    epoch_dt = parse_tle_epoch(sat)
    now = datetime.now(timezone.utc)
    age_hours = round(max(0.0, (now - epoch_dt).total_seconds() / 3600.0), 2)
    
    # Orbital parameters using sat.no_kozai (rad/min)
    mean_motion_rdpm = sat.no_kozai
    mean_motion_revday = mean_motion_rdpm * (1440.0 / (2.0 * 3.141592653589793))
    
    mu = 398600.4418
    period_sec = 86400.0 / max(mean_motion_revday, 0.0001)
    a = ((period_sec / (2.0 * 3.141592653589793)) ** 2 * mu) ** (1.0 / 3.0)
    
    e = sat.ecco
    inc_deg = sat.inclo * 57.29577951308232
    
    r_earth = 6378.137
    perigee = round(a * (1 - e) - r_earth, 1)
    apogee = round(a * (1 + e) - r_earth, 1)
    
    confidence = "HIGH"
    if age_hours > 48:
        confidence = "LOW"
    elif age_hours > 24:
        confidence = "MODERATE"
        
    return SatelliteSummary(
        id=str(item["norad_id"]),
        norad_id=item["norad_id"],
        name=item["name"],
        object_type=item.get("object_type", "PAYLOAD"),
        tle_line1=item["line1"],
        tle_line2=item["line2"],
        epoch_datetime=epoch_dt,
        age_hours=age_hours,
        confidence_level=confidence,
        semi_major_axis_km=round(a, 2),
        eccentricity=round(e, 6),
        inclination_deg=round(inc_deg, 2),
        period_min=round(period_sec / 60.0, 2),
        apogee_km=max(0.0, apogee),
        perigee_km=max(0.0, perigee)
    )

def fetch_or_load_tles(live: bool = False) -> List[Dict[str, Any]]:
    """Fetches TLEs from CelesTrak if live=True, else returns fallback dataset."""
    if live:
        try:
            url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"
            req = urllib.request.Request(url, headers={'User-Agent': 'SkyShield-Pro/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('utf-8')
                lines = [l.strip() for l in content.splitlines() if l.strip()]
                parsed = []
                for i in range(0, len(lines) - 2, 3):
                    if lines[i+1].startswith("1 ") and lines[i+2].startswith("2 "):
                        name = lines[i]
                        norad_id = int(lines[i+1][2:7].strip())
                        obj_type = "DEBRIS" if "DEB" in name or "R/B" in name else "PAYLOAD"
                        parsed.append({
                            "norad_id": norad_id,
                            "name": name,
                            "object_type": obj_type,
                            "line1": lines[i+1],
                            "line2": lines[i+2]
                        })
                if len(parsed) > 5:
                    return parsed[:50]
        except Exception:
            pass
            
    return DEMO_TLE_DATA
