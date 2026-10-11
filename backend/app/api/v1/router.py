
from fastapi import APIRouter

from app.api.v1.endpoints import (
    assistant,
    auth,
    documents,
    encounters,
    labs,
    patients,
    research,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(patients.router, prefix="/patients", tags=["Patients"])
api_router.include_router(encounters.router, prefix="/encounters", tags=["Encounters"])
api_router.include_router(labs.router, prefix="/labs", tags=["Laboratory Results"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant"])
api_router.include_router(research.router, prefix="/research", tags=["Research"])
