
from uuid import UUID

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    question: str = Field(min_length=3, max_length=5000)
    patient_id: UUID | None = None


class SourceCitation(BaseModel):
    document_id: UUID | None = None
    filename: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    excerpt: str | None = Field(default=None, max_length=2000)
    score: float | None = None


class AssistantResponse(BaseModel):
    answer: str
    citations: list[SourceCitation] = Field(default_factory=list)
    disclaimer: str = (
        "AI-generated information is for clinical support and informational "
        "purposes only. It must be reviewed by a qualified healthcare professional."
    )
