
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.lab_result import LabResultCreate, LabResultResponse
from app.services.clinical_service import (
    create_lab_result,
    list_lab_results,
)

router = APIRouter()


@router.post(
    "",
    response_model=LabResultResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lab_result_endpoint(
    payload: LabResultCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_lab_result(db, payload, user)


@router.get(
    "/encounter/{encounter_id}",
    response_model=list[LabResultResponse],
)
def list_lab_results_endpoint(
    encounter_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_lab_results(db, encounter_id, user)
