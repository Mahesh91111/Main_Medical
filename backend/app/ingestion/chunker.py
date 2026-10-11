
from dataclasses import dataclass
from uuid import UUID

from app.ingestion.pdf_extractor import ExtractedPage


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    page_number: int
    chunk_index: int
    text: str


def chunk_pages(
    pages: list[ExtractedPage],
    document_id: UUID,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[DocumentChunk]:
    """Split page text into overlapping character-based chunks."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size.")

    chunks: list[DocumentChunk] = []
    step = chunk_size - overlap

    for page in pages:
        text = page.text.strip()
        chunk_index = 0
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunk_id = (
                    f"{document_id}:p{page.page_number}:c{chunk_index}"
                )

                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=str(document_id),
                        page_number=page.page_number,
                        chunk_index=chunk_index,
                        text=chunk_text,
                    )
                )

            if end == len(text):
                break

            start += step
            chunk_index += 1

    if not chunks:
        raise ValueError("No text chunks could be generated.")

    return chunks
