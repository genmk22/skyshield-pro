import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkyShield Pro"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Data & Persistence
    DATABASE_URL: str = Field(default="sqlite:///./data/cache/skyshield.db", env="DATABASE_URL")
    CELESTRAK_URL: str = Field(default="https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle", env="CELESTRAK_URL")
    
    # Physics & Simulation Defaults
    DEFAULT_HARD_BODY_RADIUS_M: float = 10.0  # 10 meters default combined HBR
    DEFAULT_LOOKAHEAD_HOURS: float = 72.0      # 3 days prediction window
    DEFAULT_STEP_SECONDS: float = 60.0         # 60s step size for propagation
    MONTE_CARLO_DEFAULT_SAMPLES: int = 10000
    
    # Risk Classification Thresholds
    RISK_SAFE_PC: float = 1e-7
    RISK_MONITOR_PC: float = 1e-6
    RISK_WARNING_PC: float = 1e-5
    RISK_HIGH_PC: float = 1e-4
    
    # Maneuver Optimization Limits
    MAX_DELTA_V_MS: float = 5.0                # Max 5 m/s delta-v per burn
    MIN_SAFETY_MARGIN_KM: float = 1.0          # Required 1 km miss distance after maneuver
    
    # Security
    SECRET_KEY: str = Field(default="skyshield-pro-secret-key-change-in-prod-2026", env="SECRET_KEY")
    SIGNING_ALGORITHM: str = "RSA-2048"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
