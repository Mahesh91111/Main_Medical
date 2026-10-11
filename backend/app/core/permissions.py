
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status

from app.core.dependencies import CurrentUser
from app.models.user import User


def require_roles(
    *allowed_roles: str,
) -> Callable[..., User]:
    """Create a FastAPI dependency that enforces allowed roles."""

    def role_checker(user: CurrentUser) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return user

    return role_checker


AdminUser = Annotated[
    User,
    Depends(require_roles("admin")),
]

ClinicianUser = Annotated[
    User,
    Depends(require_roles("clinician", "admin")),
]

ResearcherUser = Annotated[
    User,
    Depends(require_roles("researcher", "admin")),
]
