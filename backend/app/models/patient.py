
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    patient_code: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    date_of_birth: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    created_by: Mapped[User] = relationship(
        back_populates="created_patients"
    )
    encounters: Mapped[list[Encounter]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    medications: Mapped[list[Medication]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    documents: Mapped[list[Document]] = relationship(
        back_populates="patient",
        passive_deletes=True,
    )
