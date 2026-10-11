
from uuid import UUID

from app.ingestion.embedder import embed_texts
from app.ingestion.pinecone_index import get_pinecone_index
from app.models.user import User


NAMESPACE = "medical-documents"


def retrieve_documents(
    question: str,
    user: User,
    patient_id: UUID | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Retrieve relevant document chunks from Pinecone."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not 1 <= top_k <= 10:
        raise ValueError("top_k must be between 1 and 10.")

    # Patient authorization must be checked by the calling service/API.
    if patient_id is not None:
        metadata_filter = {
            "patient_id": {"$eq": str(patient_id)}
        }
    else:
        metadata_filter = {
            "uploaded_by_id": {"$eq": str(user.id)}
        }

    query_vector = embed_texts([question])[0]
    index = get_pinecone_index()

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        namespace=NAMESPACE,
        filter=metadata_filter,
    )

    documents = []

    for match in results.matches or []:
        metadata = match.metadata or {}
        text = metadata.get("text")

        if not text:
            continue

        documents.append(
            {
                "vector_id": match.id,
                "document_id": metadata.get("document_id"),
                "filename": metadata.get("filename"),
                "page_number": metadata.get("page_number"),
                "chunk_index": metadata.get("chunk_index"),
                "text": text,
                "score": (
                    float(match.score)
                    if match.score is not None
                    else None
                ),
            }
        )

    return documents
