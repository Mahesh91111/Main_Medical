
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    delete_document,
    process_document,
    upload_document,
)
from app.services.patient_service import ensure_patient_access

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    patient_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Save the file and answer right away with status "processing".
    document = await upload_document(
        db=db,
        file=file,
        user=user,
        patient_id=patient_id,
    )

    # Text extraction, embeddings and Pinecone indexing run after the response.
    background_tasks.add_task(process_document, document.id)

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document_endpoint(
    document_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_document(db=db, document_id=document_id, user=user)


@router.get("", response_model=list[DocumentResponse])
def list_documents_endpoint(
    patient_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    statement = select(Document)

    if user.role == "admin":
        if patient_id is not None:
            statement = statement.where(
                Document.patient_id == patient_id
            )

    elif user.role == "clinician":
        if patient_id is not None:
            ensure_patient_access(db, patient_id, user)
            statement = statement.where(
                Document.patient_id == patient_id
            )
        else:
            statement = statement.where(
                Document.uploaded_by_id == user.id
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to list clinical documents",
        )

    statement = statement.order_by(Document.created_at.desc()).limit(100)
    return list(db.scalars(statement).all())
