
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medication_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    dose: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    frequency: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="recorded", nullable=False
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    patient: Mapped[Patient] = relationship(
        back_populates="medications"
    )
