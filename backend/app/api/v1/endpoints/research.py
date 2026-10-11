
from fastapi import APIRouter, Depends

from app.core.permissions import ResearcherUser

router = APIRouter()


@router.get("/status")
def research_status(user: ResearcherUser):
    return {
        "status": "not_implemented",
        "message": "Research workflows will be added in a later phase.",
    }
