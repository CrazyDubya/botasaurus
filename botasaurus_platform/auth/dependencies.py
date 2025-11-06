"""
Authentication Dependencies
==========================

FastAPI dependencies for authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID

from ..core.database import get_db
from ..core.database.models import User
from .service import AuthService


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Usage:
        @router.get("/me")
        def get_me(user: User = Depends(get_current_user)):
            return user
    """
    token = credentials.credentials
    auth_service = AuthService(db)

    try:
        payload = auth_service.verify_token(token)
        user_id = UUID(payload.get("sub"))
        user = auth_service.get_user_by_id(user_id)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_auth(user: User = Depends(get_current_user)) -> User:
    """
    Require authentication (same as get_current_user, for clarity).

    Usage:
        @router.get("/protected")
        def protected_route(user: User = Depends(require_auth)):
            return {"message": "This is protected"}
    """
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    Require admin privileges.

    Usage:
        @router.delete("/users/{user_id}")
        def delete_user(user_id: str, admin: User = Depends(require_admin)):
            # Only admins can delete users
            pass
    """
    if user.plan != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user
