
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LabResult(Base):
    __tablename__ = "lab_results"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    encounter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    value: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4), nullable=True
    )
    unit: Mapped[str | None] = mapped_column(
        String(40), nullable=True
    )
    reference_range: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    collected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    interpretation: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    encounter: Mapped[Encounter] = relationship(
        back_populates="lab_results"
    )
