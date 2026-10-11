
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Encounter(Base):
    __tablename__ = "encounters"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clinician_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    encounter_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    clinical_notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="completed", nullable=False
    )

    patient: Mapped[Patient] = relationship(
        back_populates="encounters"
    )
    clinician: Mapped[User] = relationship(
        back_populates="encounters"
    )
    lab_results: Mapped[list[LabResult]] = relationship(
        back_populates="encounter",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
