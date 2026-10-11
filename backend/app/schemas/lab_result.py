
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LabResultCreate(BaseModel):
    encounter_id: UUID
    test_name: str = Field(min_length=1, max_length=150)
    value: Decimal | None = Field(default=None, max_digits=12, decimal_places=4)
    unit: str | None = Field(default=None, max_length=40)
    reference_range: str | None = Field(default=None, max_length=100)
    collected_at: datetime | None = None
    interpretation: str | None = Field(default=None, max_length=5000)


class LabResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    encounter_id: UUID
    test_name: str
    value: Decimal | None
    unit: str | None
    reference_range: str | None
    collected_at: datetime | None
    interpretation: str | None
