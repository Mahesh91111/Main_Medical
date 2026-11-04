
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PatientCreate(BaseModel):
    patient_code: str = Field(min_length=1, max_length=50)
    full_name: str = Field(min_length=2, max_length=150)
    gender: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    date_of_birth: date | None = None
    medical_history: str | None = Field(default=None, max_length=20000)
    allergies: str | None = Field(default=None, max_length=10000)

    @model_validator(mode="after")
    def validate_birth_date(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return self


class PatientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    gender: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    date_of_birth: date | None = None
    medical_history: str | None = Field(default=None, max_length=20000)
    allergies: str | None = Field(default=None, max_length=10000)

    @model_validator(mode="after")
    def validate_birth_date(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return self


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    patient_code: str
    full_name: str
    gender: str | None
    email: str | None
    phone: str | None
    date_of_birth: date | None
    medical_history: str | None
    allergies: str | None
    created_by_id: UUID
    created_at: datetime
