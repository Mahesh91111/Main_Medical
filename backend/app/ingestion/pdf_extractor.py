
from dataclasses import dataclass

import pymupdf as fitz
@dataclass(frozen=True)
class ExtractedPage:
    page_number: int
    text: str


def extract_pdf_pages(pdf_bytes: bytes) -> list[ExtractedPage]:
    """Extract text from a PDF held in memory."""

    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF.")

    pages: list[ExtractedPage] = []

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            if document.is_encrypted:
                raise ValueError("Password-protected PDFs are not supported.")

            if len(document) == 0:
                raise ValueError("The PDF contains no pages.")

            for page_index, page in enumerate(document):
                text = page.get_text("text").strip()

                if text:
                    pages.append(
                        ExtractedPage(
                            page_number=page_index + 1,
                            text=text,
                        )
                    )

    except (fitz.FileDataError, RuntimeError) as exc:
        raise ValueError("Unable to read the uploaded PDF.") from exc

    if not pages:
        raise ValueError(
            "No selectable text was found. The PDF may require OCR."
        )

    return pages
