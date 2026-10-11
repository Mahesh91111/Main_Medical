
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(
        String(500), unique=True, nullable=False
    )
    checksum: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default="uploaded", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    patient: Mapped[Patient | None] = relationship(
        back_populates="documents"
    )
    uploaded_by: Mapped[User] = relationship(
        back_populates="uploaded_documents"
    )
