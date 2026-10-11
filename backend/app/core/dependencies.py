
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


# Swagger's Authorize button accepts a pasted Bearer token with this scheme
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Return the active user associated with the access token."""

    token = credentials.credentials


    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError, TypeError):
        raise unauthorized from None

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        raise unauthorized

    # The user's current role is read from PostgreSQL rather than
    # trusting a potentially outdated role claim in the JWT.
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]
