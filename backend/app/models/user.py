
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    full_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(30), default="clinician", nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    created_patients: Mapped[list[Patient]] = relationship(
        back_populates="created_by"
    )
    encounters: Mapped[list[Encounter]] = relationship(
        back_populates="clinician"
    )
    uploaded_documents: Mapped[list[Document]] = relationship(
        back_populates="uploaded_by"
    )
    audit_events: Mapped[list[AuditEvent]] = relationship(
        back_populates="actor"
    )
