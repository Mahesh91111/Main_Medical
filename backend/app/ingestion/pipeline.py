
from uuid import UUID

from app.ingestion.chunker import chunk_pages
from app.ingestion.embedder import embed_texts
from app.ingestion.pdf_extractor import extract_pdf_pages
from app.ingestion.pinecone_index import upsert_chunks


def ingest_pdf(
    pdf_bytes: bytes,
    document_id: UUID,
    filename: str,
    patient_id: UUID | None,
    uploaded_by_id: UUID,
) -> int:
    """Run the complete PDF-to-Pinecone ingestion pipeline."""

    # Step 1: Extract text and page numbers.
    pages = extract_pdf_pages(pdf_bytes)

    # Step 2: Split extracted text into chunks.
    chunks = chunk_pages(
        pages=pages,
        document_id=document_id,
        chunk_size=1200,
        overlap=200,
    )

    # Step 3: Generate an embedding for every chunk.
    embeddings = embed_texts([chunk.text for chunk in chunks])

    # Step 4: Store vectors and source metadata.
    indexed_count = upsert_chunks(
        chunks=chunks,
        embeddings=embeddings,
        filename=filename,
        patient_id=str(patient_id) if patient_id else None,
        uploaded_by_id=str(uploaded_by_id),
    )

    return indexed_count
