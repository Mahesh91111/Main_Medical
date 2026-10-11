
from functools import lru_cache

from pinecone import Pinecone

from app.core.config import settings
from app.ingestion.chunker import DocumentChunk


@lru_cache(maxsize=1)
def get_pinecone_index():
    """Create and cache the Pinecone index client."""

    if not settings.PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY is not configured.")

    if not settings.PINECONE_INDEX_NAME:
        raise RuntimeError("PINECONE_INDEX_NAME is not configured.")

    client = Pinecone(api_key=settings.PINECONE_API_KEY)

    # The index must already exist.
    return client.Index(settings.PINECONE_INDEX_NAME)


def upsert_chunks(
    chunks: list[DocumentChunk],
    embeddings: list[list[float]],
    filename: str,
    patient_id: str | None,
    uploaded_by_id: str,
) -> int:
    """Store embeddings and searchable source metadata in Pinecone."""

    if len(chunks) != len(embeddings):
        raise ValueError("Each chunk must have exactly one embedding.")

    if not chunks:
        return 0

    index = get_pinecone_index()
    batch_size = 100

    for start in range(0, len(chunks), batch_size):
        batch_chunks = chunks[start:start + batch_size]
        batch_embeddings = embeddings[start:start + batch_size]

        vectors = []

        for chunk, embedding in zip(batch_chunks, batch_embeddings):
            metadata = {
                "document_id": chunk.document_id,
                "filename": filename,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "uploaded_by_id": uploaded_by_id,
            }

            if patient_id is not None:
                metadata["patient_id"] = patient_id

            vectors.append({
                "id": chunk.chunk_id,
                "values": embedding,
                "metadata": metadata,
            })

        index.upsert(
            vectors=vectors,
            namespace="medical-documents",
        )

    return len(chunks)


def delete_document_vectors(document_id: str) -> None:
    """Remove vectors associated with a document after a failed ingestion."""
    index = get_pinecone_index()

    index.delete(
        filter={"document_id": {"$eq": document_id}},
        namespace="medical-documents",
    )
