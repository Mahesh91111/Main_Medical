
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once per application process."""
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Convert text strings into normalized embedding vectors."""

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()
