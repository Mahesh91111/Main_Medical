
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID | None
    uploaded_by_id: UUID
    filename: str = Field(max_length=255)
    status: str
    created_at: datetime
