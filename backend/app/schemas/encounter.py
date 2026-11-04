   
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EncounterCreate(BaseModel):
    patient_id: UUID
    encounter_date: datetime | None = None
    clinical_notes: str | None = Field(default=None, max_length=20000)
    status: str = Field(default="completed", pattern="^(scheduled|in_progress|completed|cancelled)$")
    blood_pressure: str | None = Field(default=None, max_length=20)
    heart_rate: float | None = Field(default=None, gt=0, le=350)
    temperature: float | None = Field(default=None, gt=25, le=45)
    respiratory_rate: float | None = Field(default=None, gt=0, le=100)
    oxygen_saturation: float | None = Field(default=None, gt=0, le=100)
    weight: float | None = Field(default=None, gt=0, le=1000)
    height: float | None = Field(default=None, gt=0, le=300)


class EncounterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID        
    patient_id: UUID
    clinician_id: UUID
    encounter_date: datetime
    clinical_notes: str | None
    status: str
    blood_pressure: str | None
    heart_rate: float | None
    temperature: float | None
    respiratory_rate: float | None
    oxygen_saturation: float | None
    weight: float | None
    height: float | None
 