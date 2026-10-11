
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EncounterCreate(BaseModel):
    patient_id: UUID
    encounter_date: datetime | None = None
    clinical_notes: str | None = Field(default=None, max_length=20000)
    status: str = Field(default="completed", pattern="^(scheduled|in_progress|completed|cancelled)$")


class EncounterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    clinician_id: UUID
    encounter_date: datetime
    clinical_notes: str | None
    status: str
 