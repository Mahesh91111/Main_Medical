
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.schemas.medication import MedicationCreate, MedicationResponse
from app.services.clinical_service import (
    create_patient_medication,
    get_patient_timeline,
    list_medications,
)
from app.services.patient_service import (
    create_patient,
    get_patient,
    list_patients,
    update_patient,
)

router = APIRouter()


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_endpoint(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_patient(db, payload, user)


@router.get("", response_model=list[PatientResponse])
def list_patients_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None, max_length=150),
    gender: str | None = Query(default=None, max_length=30),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_patients(db, user, skip, limit, search, gender)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient_endpoint(
    patient_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_patient(db, patient_id, user)


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient_endpoint(
    patient_id: UUID,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return update_patient(db, patient_id, payload, user)


@router.get("/{patient_id}/medications", response_model=list[MedicationResponse])
def list_patient_medications_endpoint(
    patient_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_medications(db, patient_id, user)


@router.post(
    "/{patient_id}/medications",
    response_model=MedicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_medication_endpoint(
    patient_id: UUID,
    payload: MedicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_patient_medication(db, patient_id, payload, user)


@router.get("/{patient_id}/timeline", response_model=list[dict])
def get_patient_timeline_endpoint(
    patient_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_patient_timeline(db, patient_id, user)
