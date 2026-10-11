from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True, 
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session to a FastAPI request.
    Always close the session after the request finishes.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()