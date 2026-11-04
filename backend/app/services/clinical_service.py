
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.encounter import Encounter
from app.models.document import Document
from app.models.lab_result import LabResult
from app.models.medication import Medication
from app.models.user import User
from app.schemas.encounter import EncounterCreate
from app.schemas.lab_result import LabResultCreate
from app.schemas.medication import MedicationCreate
from app.services.patient_service import (
    ensure_clinical_role,
    ensure_patient_access,
    get_patient,
)


def ensure_encounter_access(
    db: Session,
    encounter_id: UUID,
    user: User,
) -> Encounter:
    """Return an encounter only to its assigned clinician or an admin."""
    statement = select(Encounter).where(
        Encounter.id == encounter_id
    )

    if user.role == "admin":
        encounter = db.scalar(statement)
    elif user.role == "clinician":
        encounter = db.scalar(
            statement.where(Encounter.clinician_id == user.id)
        )
    else:
        encounter = None

    if encounter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found",
        )

    return encounter


def create_encounter(
    db: Session,
    encounter_data: EncounterCreate,
    user: User,
) -> Encounter:
    """Create a clinical encounter for an authorized patient."""
    ensure_clinical_role(user)

    ensure_patient_access(
        db,
        encounter_data.patient_id,
        user,
    )

    values = encounter_data.model_dump(exclude_unset=True)
    values.pop("patient_id", None)

    # The authenticated clinician is assigned by the backend.
    encounter = Encounter(
        patient_id=encounter_data.patient_id,
        clinician_id=user.id,
        **values,
    )

    try:
        db.add(encounter)
        db.commit()
        db.refresh(encounter)
        return encounter
    except Exception:
        db.rollback()
        raise


def get_encounter(
    db: Session,
    encounter_id: UUID,
    user: User,
) -> Encounter:
    """Retrieve an encounter after checking access."""
    return ensure_encounter_access(db, encounter_id, user)


def list_patient_encounters(
    db: Session,
    patient_id: UUID,
    user: User,
) -> list[Encounter]:
    """List encounters for a patient the user may access."""
    ensure_patient_access(db, patient_id, user)

    statement = select(Encounter).where(
        Encounter.patient_id == patient_id
    )

    if user.role == "clinician":
        statement = statement.where(
            Encounter.clinician_id == user.id
        )
    elif user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view clinical encounters",
        )

    return list(
        db.scalars(
            statement.order_by(Encounter.encounter_date.desc())
        ).all()
    )


def create_lab_result(
    db: Session,
    lab_data: LabResultCreate,
    user: User,
) -> LabResult:
    """Add a laboratory result to an authorized encounter."""
    ensure_clinical_role(user)

    ensure_encounter_access(
        db,
        lab_data.encounter_id,
        user,
    )

    lab_result = LabResult(**lab_data.model_dump())

    try:
        db.add(lab_result)
        db.commit()
        db.refresh(lab_result)
        return lab_result
    except Exception:
        db.rollback()
        raise


def list_lab_results(
    db: Session,
    encounter_id: UUID,
    user: User,
) -> list[LabResult]:
    """List laboratory results for an authorized encounter."""
    ensure_encounter_access(db, encounter_id, user)

    statement = (
        select(LabResult)
        .where(LabResult.encounter_id == encounter_id)
        .order_by(LabResult.collected_at.desc())
    )

    return list(db.scalars(statement).all())


def create_medication(
    db: Session,
    patient_id: UUID,
    user: User,
    medication_name: str,
    dose: str | None = None,
    frequency: str | None = None,
    notes: str | None = None,
    status: str = "active",
) -> Medication:
    """Record a medication for an authorized patient."""
    ensure_clinical_role(user)
    ensure_patient_access(db, patient_id, user)

    medication = Medication(
        patient_id=patient_id,
        medication_name=medication_name,
        dose=dose,
        frequency=frequency,
        notes=notes,
        status=status,
    )

    try:
        db.add(medication)
        db.commit()
        db.refresh(medication)
        return medication
    except Exception:
        db.rollback()
        raise


def list_medications(
    db: Session,
    patient_id: UUID,
    user: User,
) -> list[Medication]:
    """List medication records for an authorized patient."""
    ensure_patient_access(db, patient_id, user)

    if user.role not in {"admin", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view medication records",
        )

    statement = (
        select(Medication)
        .where(Medication.patient_id == patient_id)
        .order_by(Medication.recorded_at.desc())
    )

    return list(db.scalars(statement).all())


def create_patient_medication(
    db: Session,
    patient_id: UUID,
    medication_data: MedicationCreate,
    user: User,
) -> Medication:
    return create_medication(
        db=db,
        patient_id=patient_id,
        user=user,
        **medication_data.model_dump(),
    )


def get_patient_timeline(
    db: Session,
    patient_id: UUID,
    user: User,
) -> list[dict]:
    """Combine authorized clinical events into a newest-first timeline."""
    ensure_patient_access(db, patient_id, user)
    encounters = list_patient_encounters(db, patient_id, user)
    medications = list_medications(db, patient_id, user)
    statement = select(Document).where(Document.patient_id == patient_id)

    if user.role not in {"admin", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view patient documents",
        )

    documents = db.scalars(
        statement.order_by(Document.created_at.desc())
    ).all()
    events: list[dict] = []

    for encounter in encounters:
        vital_signs = [
            f"{label}: {value}{unit}"
            for label, value, unit in (
                ("Blood pressure", encounter.blood_pressure, ""),
                ("Heart rate", encounter.heart_rate, " bpm"),
                ("Temperature", encounter.temperature, " °C"),
                ("Respiratory rate", encounter.respiratory_rate, " /min"),
                ("Oxygen saturation", encounter.oxygen_saturation, "%"),
                ("Weight", encounter.weight, " kg"),
                ("Height", encounter.height, " cm"),
            )
            if value is not None
        ]
        events.append({
            "id": str(encounter.id),
            "kind": "encounter",
            "occurred_at": encounter.encounter_date,
            "title": "Clinical encounter",
            "details": " · ".join(
                value for value in (encounter.clinical_notes, *vital_signs)
                if value
            ),
            "status": encounter.status,
        })
        for result in list_lab_results(db, encounter.id, user):
            events.append({
                "id": str(result.id),
                "kind": "lab",
                "occurred_at": result.collected_at or encounter.encounter_date,
                "title": result.test_name,
                "details": " ".join(
                    part for part in (
                        f"{result.value} {result.unit or ''}".strip()
                        if result.value is not None else "",
                        result.interpretation or "",
                    ) if part
                ),
                "status": None,
            })

    for medication in medications:
        events.append({
            "id": str(medication.id),
            "kind": "medication",
            "occurred_at": medication.recorded_at,
            "title": medication.medication_name,
            "details": " · ".join(
                value for value in (
                    medication.dose,
                    medication.frequency,
                    medication.notes,
                ) if value
            ),
            "status": medication.status,
        })

    for document in documents:
        events.append({
            "id": str(document.id),
            "kind": "document",
            "occurred_at": document.created_at,
            "title": document.filename,
            "details": "Patient report",
            "status": document.status,
        })

    return sorted(
        events,
        key=lambda event: event["occurred_at"],
        reverse=True,
    )


def get_patient_records(
    db: Session,
    user: User,
    patient_id: UUID | str,
) -> dict:
    """Return an authorized patient's demographics and clinical history."""
    patient_uuid = UUID(str(patient_id))
    patient = get_patient(db, patient_uuid, user)
    encounters = list_patient_encounters(db, patient_uuid, user)
    medications = list_medications(db, patient_uuid, user)

    return {
        "patient": {
            "patient_code": patient.patient_code,
            "full_name": patient.full_name,
            "date_of_birth": patient.date_of_birth,
            "gender": patient.gender,
            "medical_history": patient.medical_history,
            "allergies": patient.allergies,
        },
        "encounters": [
            {
                "encounter_date": encounter.encounter_date,
                "clinical_notes": encounter.clinical_notes,
                "status": encounter.status,
                "vital_signs": {
                    "blood_pressure": encounter.blood_pressure,
                    "heart_rate": encounter.heart_rate,
                    "temperature": encounter.temperature,
                    "respiratory_rate": encounter.respiratory_rate,
                    "oxygen_saturation": encounter.oxygen_saturation,
                    "weight": encounter.weight,
                    "height": encounter.height,
                },
                "lab_results": [
                    {
                        "test_name": result.test_name,
                        "value": result.value,
                        "unit": result.unit,
                        "reference_range": result.reference_range,
                        "collected_at": result.collected_at,
                        "interpretation": result.interpretation,
                    }
                    for result in list_lab_results(
                        db,
                        encounter.id,
                        user,
                    )
                ],
            }
            for encounter in encounters
        ],
        "medications": [
            {
                "medication_name": medication.medication_name,
                "dose": medication.dose,
                "frequency": medication.frequency,
                "status": medication.status,
                "notes": medication.notes,
                "recorded_at": medication.recorded_at,
            }
            for medication in medications
        ],
    }
