
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Import models so every model is registered in Base.metadata.
from app.models.user import User  # noqa: F401
from app.models.patient import Patient  # noqa: F401
from app.models.encounter import Encounter  # noqa: F401
from app.models.lab_result import LabResult  # noqa: F401
from app.models.medication import Medication  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.audit_event import AuditEvent  # noqa: F401


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def create_user(db_session):
    """Create a user directly for tests that need authenticated accounts."""
    from app.core.security import hash_password
    from app.models.user import User

    def _create_user(
        email="clinician@example.com",
        role="clinician",
        password="TestPassword123!",
    ):
        user = User(
            email=email,
            full_name="Test User",
            password_hash=hash_password(password),
            role=role,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture()
def auth_headers(client, create_user):
    """Return bearer headers for an authenticated clinician."""
    create_user()
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "clinician@example.com",
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200, response.text
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
