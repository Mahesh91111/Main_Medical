
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import exists, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.encounter import Encounter
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientUpdate


def ensure_clinical_role(user: User) -> None:
    """Allow only administrators and clinicians to perform clinical writes."""
    if user.role not in {"admin", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to perform this operation",
        )


def patient_access_condition(user: User):
    """Build the patient-access rule for a clinician."""
    return or_(
        Patient.created_by_id == user.id,
        exists(
            select(Encounter.id).where(
                Encounter.patient_id == Patient.id,
                Encounter.clinician_id == user.id,
            )
        ),
    )


def ensure_patient_access(
    db: Session,
    patient_id: UUID,
    user: User,
) -> Patient:
    """Load a patient only if the current user is authorized to access it."""

    statement = select(Patient).where(Patient.id == patient_id)

    if user.role == "admin":
        patient = db.scalar(statement)
    elif user.role == "clinician":
        patient = db.scalar(
            statement.where(patient_access_condition(user))
        )
    else:
        patient = None

    if patient is None:
        # Return the same response for missing and inaccessible patients.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


def create_patient(
    db: Session,
    patient_data: PatientCreate,
    user: User,
) -> Patient:
    """Create a patient and associate it with the authenticated user."""
    ensure_clinical_role(user)

    patient = Patient(
        patient_code=patient_data.patient_code,
        full_name=patient_data.full_name,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        email=patient_data.email,
        phone=patient_data.phone,
        medical_history=patient_data.medical_history,
        allergies=patient_data.allergies,
        created_by_id=user.id,
    )

    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient code already exists",
        ) from exc


def get_patient(
    db: Session,
    patient_id: UUID,
    user: User,
) -> Patient:
    """Retrieve a single authorized patient."""
    return ensure_patient_access(db, patient_id, user)


def list_patients(
    db: Session,
    user: User,
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    gender: str | None = None,
) -> list[Patient]:
    """Return only patients the user is allowed to access."""
    if user.role == "admin":
        statement = select(Patient)
    elif user.role == "clinician":
        statement = select(Patient).where(
            patient_access_condition(user)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to list patient records",
        )

    if search:
        search_pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Patient.full_name.ilike(search_pattern),
                Patient.patient_code.ilike(search_pattern),
                Patient.email.ilike(search_pattern),
                Patient.phone.ilike(search_pattern),
            )
        )

    if gender and gender.lower() in {"unknown", "unspecified"}:
        statement = statement.where(
            or_(
                Patient.gender.is_(None),
                Patient.gender.in_(["unknown", "unspecified"]),
            )
        )
    elif gender:
        statement = statement.where(Patient.gender == gender)

    statement = (
        statement.order_by(Patient.created_at.desc())
        .offset(max(skip, 0))
        .limit(min(max(limit, 1), 100))
    )

    return list(db.scalars(statement).all())


def update_patient(
    db: Session,
    patient_id: UUID,
    patient_data: PatientUpdate,
    user: User,
) -> Patient:
    """Update an authorized patient's editable demographic fields."""
    ensure_clinical_role(user)

    patient = ensure_patient_access(db, patient_id, user)
    updates = patient_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(patient, field, value)

    try:
        db.commit()
        db.refresh(patient)
        return patient
    except Exception:
        db.rollback()
        raise
