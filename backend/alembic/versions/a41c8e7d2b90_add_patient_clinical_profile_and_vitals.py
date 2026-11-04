"""add patient clinical profile and encounter vital signs

Revision ID: a41c8e7d2b90
Revises: ec9bf85c9bbb
Create Date: 2026-11-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a41c8e7d2b90"
down_revision: Union[str, Sequence[str], None] = "ec9bf85c9bbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("gender", sa.String(length=30), nullable=True))
    op.add_column("patients", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("patients", sa.Column("phone", sa.String(length=30), nullable=True))
    op.add_column("patients", sa.Column("medical_history", sa.Text(), nullable=True))
    op.add_column("patients", sa.Column("allergies", sa.Text(), nullable=True))

    op.add_column("encounters", sa.Column("blood_pressure", sa.String(length=20), nullable=True))
    op.add_column("encounters", sa.Column("heart_rate", sa.Numeric(6, 2), nullable=True))
    op.add_column("encounters", sa.Column("temperature", sa.Numeric(6, 2), nullable=True))
    op.add_column("encounters", sa.Column("respiratory_rate", sa.Numeric(6, 2), nullable=True))
    op.add_column("encounters", sa.Column("oxygen_saturation", sa.Numeric(6, 2), nullable=True))
    op.add_column("encounters", sa.Column("weight", sa.Numeric(7, 2), nullable=True))
    op.add_column("encounters", sa.Column("height", sa.Numeric(7, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("encounters", "height")
    op.drop_column("encounters", "weight")
    op.drop_column("encounters", "oxygen_saturation")
    op.drop_column("encounters", "respiratory_rate")
    op.drop_column("encounters", "temperature")
    op.drop_column("encounters", "heart_rate")
    op.drop_column("encounters", "blood_pressure")

    op.drop_column("patients", "allergies")
    op.drop_column("patients", "medical_history")
    op.drop_column("patients", "phone")
    op.drop_column("patients", "email")
    op.drop_column("patients", "gender")
