from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MedicationCreate(BaseModel):
    medication_name: str = Field(min_length=1, max_length=200)
    dose: str | None = Field(default=None, max_length=100)
    frequency: str | None = Field(default=None, max_length=100)
    status: str = Field(default="active", pattern="^(active|discontinued|recorded)$")
    notes: str | None = Field(default=None, max_length=5000)


class MedicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_id: UUID
    medication_name: str
    dose: str | None
    frequency: str | None
    status: str
    notes: str | None
    recorded_at: datetime
