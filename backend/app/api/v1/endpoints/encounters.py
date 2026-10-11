
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.encounter import EncounterCreate, EncounterResponse
from app.services.clinical_service import (
    create_encounter,
    get_encounter,
    list_patient_encounters,
)

router = APIRouter()


@router.post(
    "",
    response_model=EncounterResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_encounter_endpoint(
    payload: EncounterCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_encounter(db, payload, user)


@router.get("/{encounter_id}", response_model=EncounterResponse)
def get_encounter_endpoint(
    encounter_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_encounter(db, encounter_id, user)


@router.get(
    "/patient/{patient_id}",
    response_model=list[EncounterResponse],
)
def list_encounters_endpoint(
    patient_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_patient_encounters(db, patient_id, user)
