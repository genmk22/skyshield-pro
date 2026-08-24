from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import (
    satellites, conjunctions, risk, maneuver, security, scenarios, logs
)
from app.core.logging import log_audit_event

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SkyShield Pro: Physics-Based Satellite Collision Risk Assessment & Secure Maneuver Advisory Platform"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(satellites.router, prefix=settings.API_V1_STR)
app.include_router(conjunctions.router, prefix=settings.API_V1_STR)
app.include_router(risk.router, prefix=settings.API_V1_STR)
app.include_router(maneuver.router, prefix=settings.API_V1_STR)
app.include_router(security.router, prefix=settings.API_V1_STR)
app.include_router(scenarios.router, prefix=settings.API_V1_STR)
app.include_router(logs.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    log_audit_event("SYSTEM_STARTUP", object_id="SKYSHIELD_BACKEND", status="SUCCESS")

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": "PHYSICS_BASED_ADVISORY"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
