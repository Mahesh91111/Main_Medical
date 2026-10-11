
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.auth import UserRegister


def register_user(
    db: Session,
    user_data: UserRegister,
) -> User:
    """Register a new user with a securely hashed password."""

    existing_user = db.scalar(
        select(User).where(User.email == str(user_data.email))
    )

    if existing_user is not None:
        raise ValueError("An account with this email already exists")

    user = User(
        email=str(user_data.email),
        full_name=user_data.full_name,
        password_hash=hash_password(user_data.password),
        # Role is assigned by the backend, never by the request.
        role="clinician",
        is_active=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "Unable to register user; the email may already exist"
        ) from exc
    except Exception:
        db.rollback()
        raise

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    """Return the user when the email and password are valid."""

    user = db.scalar(
        select(User).where(User.email == email)
    )

    # Verify a password only when a matching account exists.
    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user
