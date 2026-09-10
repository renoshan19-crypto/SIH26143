from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config import APP_NAME, APP_VERSION
from database.connection import engine

from api.incidents import router as incidents_router
from api.detection import router as detection_router
from api.spill import router as spill_router
from api.drift import get_drift
from api.vessels import router as vessels_router
from api.candidates import router as candidates_router
from api.casc import router as casc_router
from api.certificate import router as certificates_router
from api.audit import router as audit_router


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)


# =========================================================
# CORS
# Allows frontend (port 5500) to communicate
# with backend (port 8000)
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(incidents_router)
app.include_router(detection_router)
app.include_router(spill_router)

app.add_api_route(
    "/drift/{incident_id}",
    get_drift,
    methods=["GET"],
    tags=["Drift / Backtrack"]
)

app.include_router(vessels_router)
app.include_router(candidates_router)
app.include_router(casc_router)
app.include_router(certificates_router)
app.include_router(audit_router)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "service": APP_NAME,
        "version": APP_VERSION
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    try:

        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as error:

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error)
        }