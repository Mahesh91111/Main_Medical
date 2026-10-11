import hashlib
import logging
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.ingestion.pipeline import ingest_pdf
from app.ingestion.pinecone_index import delete_document_vectors
from app.models.document import Document
from app.models.user import User
from app.services.patient_service import ensure_patient_access

logger = logging.getLogger(__name__)

# Private storage directory; do not mount this as public static content.
STORAGE_DIR = Path(__file__).resolve().parents[2] / "private_uploads"


async def upload_document(
    db: Session,
    file: UploadFile,
    user: User,
    patient_id: UUID | None = None,
) -> Document:
    """Validate a PDF, store it privately and record it as 'processing'.

    The slow part (text extraction, embeddings, Pinecone) is not done here.
    It runs afterwards in process_document(), so the upload can answer quickly.
    """

    if user.role not in {"admin", "clinician"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to upload clinical documents",
        )

    if patient_id is not None:
        ensure_patient_access(db, patient_id, user)

    original_name = Path(file.filename or "").name

    if not original_name or Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    pdf_bytes = await file.read(max_bytes + 1)

    if len(pdf_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    if not pdf_bytes.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid PDF",
        )

    document_id = uuid4()
    checksum = hashlib.sha256(pdf_bytes).hexdigest()
    storage_key = f"{document_id}.pdf"
    file_path = STORAGE_DIR / storage_key

    document = Document(
        id=document_id,
        patient_id=patient_id,
        uploaded_by_id=user.id,
        filename=original_name,
        storage_key=storage_key,
        checksum=checksum,
        status="processing",
    )

    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(pdf_bytes)

        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        file_path.unlink(missing_ok=True)
        logger.exception("Failed to create the document record")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the document",
        ) from None

    return document


def delete_document(db: Session, document_id: UUID, user: User) -> None:
    """Delete a document, its stored PDF and its searchable data."""

    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Admins can delete any document; other users only the ones they uploaded.
    if user.role != "admin" and document.uploaded_by_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this document",
        )

    # Deleting now could leave search data behind once processing finishes.
    if document.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This document is still being processed. "
                "Try again when it has finished."
            ),
        )

    storage_key = document.storage_key
    was_processed = document.status == "processed"

    # Remove the search data first, so deleted text can never be retrieved.
    try:
        delete_document_vectors(str(document_id))
    except Exception:
        logger.exception(
            "Could not remove vectors for document %s",
            document_id,
        )

        # A document that was never indexed has nothing to remove, so only
        # stop when search data may really still exist.
        if was_processed:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Could not remove the document's search data. "
                    "Nothing was deleted. Please try again."
                ),
            ) from None

    try:
        db.delete(document)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Could not delete document record %s", document_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the document",
        ) from None

    (STORAGE_DIR / storage_key).unlink(missing_ok=True)
    logger.info("Document %s deleted by user %s", document_id, user.id)


def process_document(document_id: UUID) -> None:
    """Index a stored PDF in the background and update its status.

    This runs after the upload response has been sent, so it opens its own
    database session instead of reusing the request's session.
    """

    db = SessionLocal()

    try:
        document = db.get(Document, document_id)

        if document is None:
            logger.error("Document %s disappeared before processing", document_id)
            return

        try:
            pdf_bytes = (STORAGE_DIR / document.storage_key).read_bytes()

            ingest_pdf(
                pdf_bytes=pdf_bytes,
                document_id=document.id,
                filename=document.filename,
                patient_id=document.patient_id,
                uploaded_by_id=document.uploaded_by_id,
            )

            document.status = "processed"
            db.commit()
            logger.info("Document %s processed", document_id)

        except Exception:
            db.rollback()
            logger.exception("Document ingestion failed for %s", document_id)

            try:
                delete_document_vectors(str(document_id))
            except Exception:
                logger.exception(
                    "Could not clean up vectors for document %s",
                    document_id,
                )

            try:
                failed_document = db.get(Document, document_id)

                if failed_document is not None:
                    failed_document.status = "failed"
                    db.commit()
            except Exception:
                db.rollback()
                logger.exception(
                    "Could not update document status for %s",
                    document_id,
                )
    finally:
        db.close()
