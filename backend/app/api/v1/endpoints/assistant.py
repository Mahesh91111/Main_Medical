
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.graph import run_medical_assistant
from app.core.dependencies import get_current_user, get_db
from app.schemas.assistant import AssistantRequest, AssistantResponse
from app.services.patient_service import ensure_patient_access


router = APIRouter()


@router.post("/ask", response_model=AssistantResponse)
def ask_assistant(
    payload: AssistantRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.role not in {"admin", "clinician", "researcher"}:
        raise HTTPException(
            status_code=403,
            detail="Your role cannot access the medical assistant.",
        )

    if payload.patient_id is not None:
        if user.role not in {"admin", "clinician"}:
            raise HTTPException(
                status_code=403,
                detail="Patient-specific requests require a clinical role.",
            )

        try:
            patient_id = UUID(str(payload.patient_id))
            ensure_patient_access(db, patient_id, user)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="Invalid patient ID.",
            ) from exc
        except PermissionError as exc:
            raise HTTPException(
                status_code=403,
                detail="You cannot access this patient's records.",
            ) from exc

    else:
        patient_id = None

    try:
        result = run_medical_assistant(
            question=payload.question,
            user=user,
            db=db,
            patient_id=str(patient_id) if patient_id else None,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this information.",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Log the full exception server-side in a production application.
        raise HTTPException(
            status_code=502,
            detail="The assistant workflow failed. Please try again.",
        ) from exc

    return AssistantResponse(
        answer=result["answer"],
        citations=result["citations"],
        disclaimer=(
            "AI-generated information is for informational support only. "
            "A qualified clinician must review clinical decisions."
        ),
    )
