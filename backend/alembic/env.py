
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

from app.core.config import settings
from app.db.base import Base

# Import every model so SQLAlchemy registers all tables in Base.metadata.
from app.models.user import User  # noqa: F401
from app.models.patient import Patient  # noqa: F401
from app.models.encounter import Encounter  # noqa: F401
from app.models.lab_result import LabResult  # noqa: F401
from app.models.medication import Medication  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.audit_event import AuditEvent  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Use the same database configuration as the FastAPI application."""
    url = make_url(settings.DATABASE_URL)

    # Avoid logging or exposing the URL because it may contain credentials.
    if url.drivername not in {
        "postgresql",
        "postgresql+psycopg",
        "postgresql+psycopg2",
    }:
        raise RuntimeError(
            "Alembic expects a PostgreSQL database URL."
        )

    # Use the psycopg 3 driver supported by this project's migration setup.
    if url.drivername in {"postgresql", "postgresql+psycopg2"}:
        url = url.set(drivername="postgresql+psycopg")

    return url.render_as_string(hide_password=False)


def run_migrations_offline() -> None:
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Override sqlalchemy.url with the URL from app/core/config.py.
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
